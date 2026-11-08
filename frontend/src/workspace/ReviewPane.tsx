import { useState } from 'react'
import { isEmpty, NOT_MENTIONED, type FieldDef, type FieldMeta, type FormSchema, type Issue, type Value } from '../api'
import { Badge, Panel, Spinner } from '../ui'
import { cx, input } from '../styles'
import type { RunState } from './Workspace'

interface Props {
  form: FormSchema
  values: Record<string, Value>
  meta: Record<string, FieldMeta>
  issues: Issue[]
  run: RunState
  active: string | null
  setActive: (k: string | null) => void
  edited: Set<string>
  onEdit: (key: string, v: Value) => void
}

export function ReviewPane(props: Props) {
  const { form, run, values, issues } = props
  const filled = form.fields.filter((f) => !isEmpty(values[f.key])).length
  const errors = issues.filter((i) => i.severity === 'error').length
  const warnings = issues.filter((i) => i.severity === 'warning').length

  if (run.phase === 'idle' && filled === 0) {
    return (
      <Panel title="Review">
        <div className="flex h-full flex-col items-center justify-center gap-2 p-8 text-center text-sm text-muted">
          <p className="max-w-sm">
            Draft the form from the notes. Each answer comes with the quote it was based on. Click an answer to see that quote
            in the notes, and correct anything before generating the PDF.
          </p>
        </div>
      </Panel>
    )
  }

  const order = (id: string) => (run.sections[id] === 'skipped' ? 1 : 0)
  const sections = [...form.sections].sort((a, b) => order(a.id) - order(b.id))

  return (
    <Panel
      title="Review"
      actions={
        <div className="flex items-center gap-1.5">
          <Badge tone="accent">{filled} answers</Badge>
          {errors > 0 && <Badge tone="error">{errors} required</Badge>}
          {warnings > 0 && <Badge tone="warn">{warnings} to check</Badge>}
        </div>
      }
    >
      <div className="divide-y divide-line">
        {sections.map((s) => (
          <SectionBlock key={s.id} {...props} sectionId={s.id} label={s.label} />
        ))}
      </div>
    </Panel>
  )
}

function SectionBlock({ form, values, meta, issues, run, active, setActive, edited, onEdit, sectionId, label }: Props & { sectionId: string; label: string }) {
  const [showAll, setShowAll] = useState(false)
  const status = run.sections[sectionId]
  const fields = form.fields.filter((f) => f.section === sectionId)
  const issueKeys = new Set(issues.map((i) => i.field))
  const relevant = fields.filter((f) => !isEmpty(values[f.key]) || issueKeys.has(f.key) || edited.has(f.key))
  const shown = showAll ? fields : relevant
  const [open, setOpen] = useState(true)

  if (status === 'skipped' && relevant.length === 0 && !showAll) {
    return (
      <div className="flex items-center justify-between px-4 py-2 text-sm text-faint">
        <span>{label}</span>
        <button className="text-xs hover:text-accent" onClick={() => setShowAll(true)}>not in notes · add manually</button>
      </div>
    )
  }

  return (
    <div>
      <button className="flex w-full items-center justify-between px-4 py-2.5 text-left hover:bg-sunken" onClick={() => setOpen(!open)}>
        <span className="flex items-center gap-2 text-sm font-semibold">
          <span className={cx('text-faint transition-transform', open && 'rotate-90')}>›</span>
          {label}
        </span>
        <span className="flex items-center gap-2 text-xs text-muted">
          {status === 'pending' && <><Spinner className="text-accent" /> extracting</>}
          {status === 'error' && <Badge tone="error">model error</Badge>}
          {status === 'empty' && 'nothing found'}
          {status !== 'pending' && `${relevant.length}/${fields.length}`}
        </span>
      </button>
      {open && status !== 'pending' && (
        <div className="pb-2">
          {shown.map((f) => (
            <FieldRow
              key={f.key}
              field={f}
              value={values[f.key]}
              meta={meta[f.key]}
              issues={issues.filter((i) => i.field === f.key)}
              active={active === f.key}
              edited={edited.has(f.key)}
              onFocus={() => setActive(f.key)}
              onChange={(v) => onEdit(f.key, v)}
            />
          ))}
          <button className="px-4 py-1 text-xs text-accent hover:underline" onClick={() => setShowAll(!showAll)}>
            {showAll ? 'Show answered fields only' : `Show all ${fields.length} fields`}
          </button>
        </div>
      )}
    </div>
  )
}

function shortLabel(f: FieldDef) {
  const first = f.description.split('. ')[0]
  const m = first.match(/^(Q\d+[^:]*):\s*(.*)$/)
  return m ? { q: m[1], text: m[2] } : { q: '', text: first }
}

function FieldRow({ field, value, meta, issues, active, edited, onFocus, onChange }: {
  field: FieldDef; value: Value | undefined; meta?: FieldMeta; issues: Issue[]; active: boolean; edited: boolean
  onFocus: () => void; onChange: (v: Value) => void
}) {
  const { q, text } = shortLabel(field)
  const filled = !isEmpty(value)
  const worst = issues.find((i) => i.severity === 'error') ?? issues.find((i) => i.severity === 'warning') ?? issues[0]

  return (
    <div
      className={cx('mx-2 grid grid-cols-[minmax(0,1fr)_minmax(0,1.1fr)] items-start gap-3 rounded-md px-2 py-1.5', active ? 'bg-accent-soft' : 'hover:bg-sunken')}
      onClick={onFocus}
    >
      <div className="min-w-0 pt-1 text-[13px] leading-snug">
        {q && <span className="mr-1 font-mono text-[11px] text-faint">{q}</span>}
        <span className={filled ? 'text-ink' : 'text-muted'}>{text}</span>
        {field.mandatory && <span className="ml-1 text-error" title="Mandatory">*</span>}
        <div className="mt-0.5 flex flex-wrap gap-1">
          {edited && <Badge>edited</Badge>}
          {!edited && filled && meta?.grounded && <Badge tone="accent" title={meta.evidence}>quoted</Badge>}
          {worst && <Badge tone={worst.severity === 'error' ? 'error' : worst.severity === 'warning' ? 'warn' : 'neutral'} title={worst.message}>{worst.rule === 'ungrounded' ? 'no quote found' : worst.message}</Badge>}
        </div>
        {active && meta?.evidence && !meta.grounded && (
          <p className="mt-1 text-[11px] text-warn italic">Model's quote (not found in notes): “{meta.evidence}”</p>
        )}
      </div>
      <Editor field={field} value={value} onChange={onChange} onFocus={onFocus} />
    </div>
  )
}

function Editor({ field, value, onChange, onFocus }: { field: FieldDef; value: Value | undefined; onChange: (v: Value) => void; onFocus: () => void }) {
  if (field.kind === 'enum') {
    return (
      <select
        className={cx(input, 'py-1', isEmpty(value) && 'text-faint')}
        value={(value as string) || NOT_MENTIONED}
        onChange={(e) => onChange(e.target.value)}
        onFocus={onFocus}
      >
        <option value={NOT_MENTIONED}>— not mentioned —</option>
        {field.options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    )
  }
  if (field.kind === 'bool') {
    return (
      <label className="flex items-center gap-2 pt-1 text-sm">
        <input type="checkbox" className="size-4 accent-[var(--accent)]" checked={value === true} onChange={(e) => onChange(e.target.checked)} onFocus={onFocus} />
        <span className="text-muted">{value ? 'Yes' : 'No'}</span>
      </label>
    )
  }
  if (field.kind === 'text') {
    return (
      <textarea
        className={cx(input, 'min-h-[2.1rem] resize-y py-1 leading-snug')}
        rows={String(value ?? '').length > 60 ? 3 : 1}
        value={(value as string) ?? ''}
        onChange={(e) => onChange(e.target.value)}
        onFocus={onFocus}
        placeholder="—"
      />
    )
  }
  return (
    <input
      className={cx(input, 'w-28 py-1 font-mono')}
      inputMode="numeric"
      value={(value as string) ?? ''}
      onChange={(e) => onChange(e.target.value)}
      onFocus={onFocus}
      placeholder={field.kind === 'year' ? 'YYYY' : '—'}
    />
  )
}
