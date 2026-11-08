import { useEffect, useMemo, useRef } from 'react'
import { isEmpty, type FieldMeta, type Sample, type Value } from '../api'
import { Panel } from '../ui'
import { btn, cx } from '../styles'

interface Props {
  notes: string
  setNotes: (s: string) => void
  samples: Sample[]
  meta: Record<string, FieldMeta>
  values: Record<string, Value>
  active: string | null
  setActive: (k: string | null) => void
  locked: boolean
  onUnlock: () => void
}

/** Split the notes at every evidence-span boundary; each piece knows which fields cite it. */
function segment(notes: string, spans: { key: string; start: number; end: number }[]) {
  const cuts = new Set([0, notes.length])
  for (const s of spans) {
    cuts.add(s.start)
    cuts.add(s.end)
  }
  const points = [...cuts].sort((a, b) => a - b)
  const out: { text: string; keys: string[] }[] = []
  for (let i = 0; i < points.length - 1; i++) {
    const [a, b] = [points[i], points[i + 1]]
    out.push({ text: notes.slice(a, b), keys: spans.filter((s) => s.start <= a && s.end >= b).map((s) => s.key) })
  }
  return out
}

export function NotesPane({ notes, setNotes, samples, meta, values, active, setActive, locked, onUnlock }: Props) {
  const activeRef = useRef<HTMLElement | null>(null)

  const spans = useMemo(
    () =>
      Object.entries(meta).flatMap(([key, m]) =>
        m.grounded && !isEmpty(values[key]) ? m.spans.map(([start, end]) => ({ key, start, end })) : [],
      ),
    [meta, values],
  )
  const segments = useMemo(() => segment(notes, spans), [notes, spans])

  useEffect(() => {
    activeRef.current?.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
  }, [active])

  const sampleLabel = (s: Sample) =>
    s.id.startsWith('hand') ? 'Sample: hearing + mental health' : `Sample ${s.id.replace('syn-', '#')} · ${s.style} · ${s.sections.filter((x) => x !== 'cert').join(', ')}`

  return (
    <Panel
      title="Clinical notes"
      actions={
        locked ? (
          <button className={btn.link} onClick={onUnlock}>Edit notes</button>
        ) : (
          <select
            className="max-w-56 rounded-md border border-line bg-panel px-2 py-1 text-xs text-ink"
            value=""
            onChange={(e) => {
              const s = samples.find((x) => x.id === e.target.value)
              if (s) setNotes(s.notes)
            }}
          >
            <option value="" disabled>Load a sample…</option>
            {samples.map((s) => <option key={s.id} value={s.id}>{sampleLabel(s)}</option>)}
          </select>
        )
      }
    >
      {locked ? (
        <div className="px-4 py-3 font-mono text-[12.5px] leading-relaxed whitespace-pre-wrap">
          {segments.map((s, i) => {
            if (!s.keys.length) return <span key={i}>{s.text}</span>
            const on = active !== null && s.keys.includes(active)
            return (
              <mark
                key={i}
                ref={on ? (el) => { activeRef.current = el } : undefined}
                className={cx('cursor-pointer', on ? 'bg-mark' : 'bg-mark-faint hover:bg-mark')}
                onClick={() => setActive(s.keys[0])}
                title={s.keys.join('\n')}
              >
                {s.text}
              </mark>
            )
          })}
        </div>
      ) : (
        <textarea
          className="block h-full min-h-80 w-full resize-none bg-transparent px-4 py-3 font-mono text-[12.5px] leading-relaxed text-ink outline-none placeholder:text-faint"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Paste de-identified clinical notes here…"
          spellCheck={false}
        />
      )}
    </Panel>
  )
}
