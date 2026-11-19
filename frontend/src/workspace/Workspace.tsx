import { useEffect, useEffectEvent, useRef, useState } from 'react'
import { api, type ExtractResult, type FieldMeta, type FormSchema, type Issue, type Sample, type SectionStatus, type Value } from '../api'
import { Spinner } from '../ui'
import { btn, cx } from '../styles'
import { NotesPane } from './NotesPane'
import { PdfPane } from './PdfPane'
import { ReviewPane } from './ReviewPane'

export interface RunState {
  phase: 'idle' | 'routing' | 'extracting' | 'done' | 'error'
  sections: Record<string, SectionStatus>
  error?: string
  stats?: ExtractResult['stats']
  startedAt?: number
}

const VARIANT_LABELS: Record<string, string> = {
  v3_select: 'Select, then fill',
  v2_evidence: 'Evidence-grounded',
  v1_schema: 'Schema only',
  v0_baseline: 'Prototype baseline',
}

export function Workspace({ form }: { form: FormSchema }) {
  const [samples, setSamples] = useState<Sample[]>([])
  const [models, setModels] = useState<{ ok: boolean; error?: string; names: string[] }>({ ok: true, names: [] })
  const [model, setModel] = useState('qwen2.5:7b')
  const [variant, setVariant] = useState('v3_select')
  const [notes, setNotes] = useState('')
  const [values, setValues] = useState<Record<string, Value>>({})
  const [meta, setMeta] = useState<Record<string, FieldMeta>>({})
  const [issues, setIssues] = useState<Issue[]>([])
  const [run, setRun] = useState<RunState>({ phase: 'idle', sections: {} })
  const [active, setActive] = useState<string | null>(null)
  const [edited, setEdited] = useState<Set<string>>(new Set())
  const abort = useRef<AbortController | null>(null)

  useEffect(() => {
    api.samples().then((s) => {
      setSamples(s)
      if (s[0]) setNotes((n) => n || s[0].notes)
    })
    api.models().then((m) => {
      setModels({ ok: m.ok, error: m.error, names: m.models.map((x) => x.name) })
      if (m.models.some((x) => x.name === m.default)) setModel(m.default)
      else if (m.models[0]) setModel(m.models[0].name)
    })
  }, [])

  // Re-run the form rules after manual edits (debounced). Extraction results
  // already include issues, so this only fires once the user changes something.
  const revalidate = useEffectEvent(async () => {
    const { issues: base } = await api.validate(values)
    const ungrounded = issues.filter((i) => i.rule === 'ungrounded' && !edited.has(i.field ?? ''))
    setIssues([...base, ...ungrounded])
  })
  useEffect(() => {
    if (edited.size === 0) return
    const t = setTimeout(() => void revalidate(), 400)
    return () => clearTimeout(t)
  }, [values, edited])

  async function extract() {
    abort.current?.abort()
    const ctrl = new AbortController()
    abort.current = ctrl
    setValues({})
    setMeta({})
    setIssues([])
    setEdited(new Set())
    setActive(null)
    setRun({ phase: 'routing', sections: Object.fromEntries(form.sections.map((s) => [s.id, 'pending'])), startedAt: Date.now() })
    try {
      await api.extract({ notes, model, variant }, (ev) => {
        if (ev.type === 'routed') {
          setRun((r) => ({
            ...r,
            phase: 'extracting',
            sections: Object.fromEntries(form.sections.map((s) => [s.id, ev.sections.includes(s.id) ? 'pending' : 'skipped'])),
          }))
        } else if (ev.type === 'section') {
          setValues((v) => ({ ...v, ...ev.values }))
          setMeta((m) => ({ ...m, ...ev.meta }))
          setRun((r) => ({ ...r, sections: { ...r.sections, [ev.section]: ev.status } }))
        } else if (ev.type === 'done') {
          setValues(ev.result.values)
          setMeta(ev.result.fields)
          setIssues(ev.result.issues)
          setRun((r) => ({ ...r, phase: 'done', sections: Object.fromEntries(Object.entries(ev.result.sections).map(([k, s]) => [k, s.status])), stats: ev.result.stats }))
        } else if (ev.type === 'error') {
          setRun((r) => ({ ...r, phase: 'error', error: ev.message }))
        }
      }, ctrl.signal)
    } catch (e) {
      if (!ctrl.signal.aborted) setRun((r) => ({ ...r, phase: 'error', error: String(e) }))
    }
  }

  function cancel() {
    abort.current?.abort()
    setRun((r) => ({ ...r, phase: 'idle' }))
  }

  function edit(key: string, v: Value) {
    setValues((prev) => ({ ...prev, [key]: v }))
    setEdited((prev) => new Set(prev).add(key))
  }

  const busy = run.phase === 'routing' || run.phase === 'extracting'

  return (
    <div className="flex h-full min-h-0 flex-col gap-3">
      <div className="flex flex-wrap items-center gap-2">
        <button className={btn.primary} onClick={busy ? cancel : extract} disabled={!busy && (!notes.trim() || !models.ok)}>
          {busy ? <><Spinner /> Cancel</> : 'Draft form from notes'}
        </button>
        <label className="flex items-center gap-1.5 text-xs text-muted">
          Model
          <select className="rounded-md border border-line bg-panel px-2 py-1.5 text-sm text-ink" value={model} onChange={(e) => setModel(e.target.value)} disabled={busy}>
            {models.names.map((m) => <option key={m}>{m}</option>)}
          </select>
        </label>
        <label className="flex items-center gap-1.5 text-xs text-muted">
          Pipeline
          <select className="rounded-md border border-line bg-panel px-2 py-1.5 text-sm text-ink" value={variant} onChange={(e) => setVariant(e.target.value)} disabled={busy}>
            {form.variants.slice().reverse().map((v) => <option key={v} value={v}>{VARIANT_LABELS[v] ?? v}</option>)}
          </select>
        </label>
        <RunStatus run={run} />
        {!models.ok && (
          <span className="rounded-md bg-error-soft px-2.5 py-1.5 text-xs text-error">
            Ollama isn't reachable. Start it with <code className="font-mono">ollama serve</code>.
          </span>
        )}
      </div>

      <div className="grid min-h-0 flex-1 grid-cols-1 gap-3 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.25fr)_minmax(0,1fr)]">
        <NotesPane
          notes={notes}
          setNotes={setNotes}
          samples={samples}
          meta={meta}
          values={values}
          active={active}
          setActive={setActive}
          locked={busy || run.phase === 'done'}
          onUnlock={() => setRun({ phase: 'idle', sections: {} })}
        />
        <ReviewPane
          form={form}
          values={values}
          meta={meta}
          issues={issues}
          run={run}
          active={active}
          setActive={setActive}
          edited={edited}
          onEdit={edit}
        />
        <PdfPane form={form} values={values} ready={run.phase === 'done'} issues={issues} />
      </div>
    </div>
  )
}

function RunStatus({ run }: { run: RunState }) {
  const [now, setNow] = useState(() => Date.now())
  const busy = run.phase === 'routing' || run.phase === 'extracting'
  useEffect(() => {
    if (!busy) return
    const t = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(t)
  }, [busy])

  if (run.phase === 'idle') return null
  if (run.phase === 'error') return <span className="text-xs text-error">{run.error}</span>
  const all = Object.values(run.sections)
  const todo = all.filter((s) => s !== 'skipped')
  const done = todo.filter((s) => s !== 'pending').length
  const secs = run.phase === 'done' && run.stats ? run.stats.ms / 1000 : (now - (run.startedAt ?? now)) / 1000
  return (
    <span className={cx('text-xs', run.phase === 'done' ? 'text-muted' : 'text-accent')}>
      {run.phase === 'routing' && 'Finding relevant sections…'}
      {run.phase === 'extracting' && `Extracting ${done}/${todo.length} sections…`}
      {run.phase === 'done' && `Done: ${todo.length} of ${all.length} sections relevant`}
      {' · '}
      {secs.toFixed(0)}s{run.phase === 'done' && run.stats ? ` · ${run.stats.output_tokens.toLocaleString()} tokens generated` : ''}
    </span>
  )
}
