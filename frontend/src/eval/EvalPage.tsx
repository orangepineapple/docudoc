import { useEffect, useState } from 'react'
import { api, type EvalConfig, type Rates } from '../api'
import { Panel } from '../ui'
import { cx } from '../styles'

const pct = (v: number | null | undefined, d = 0) => (v == null ? '–' : `${(v * 100).toFixed(d)}%`)
const secs = (ms: number) => `${(ms / 1000).toFixed(0)}s`
const VARIANT: Record<string, string> = { v0_baseline: 'Prototype baseline', v1_schema: 'Schema + enums', v2_evidence: 'Schema + evidence', v3_select: 'Select, then fill' }

export function EvalPage() {
  const [runs, setRuns] = useState<Record<string, Record<string, EvalConfig>> | null>(null)
  const [run, setRun] = useState<string>('')

  useEffect(() => {
    api.evalRuns().then((r) => {
      setRuns(r)
      const names = Object.keys(r)
      setRun(names.includes('dev') ? 'dev' : names[0] ?? '')
    })
  }, [])

  if (!runs) return <p className="p-6 text-sm text-muted">Loading results…</p>
  const configs = Object.entries(runs[run] ?? {})
  if (!configs.length) {
    return <p className="p-6 text-sm text-muted">No eval results yet. Run <code className="font-mono">python eval/run.py</code>.</p>
  }

  const baseline = configs.find(([, c]) => c.config.variant === 'v0_baseline')
  const best = [...configs].filter(([, c]) => c.config.variant !== 'v0_baseline')
    .sort(([, a], [, b]) => b.aggregate.overall.f1 - a.aggregate.overall.f1)[0]
  const n = configs[0][1].aggregate.n_cases

  return (
    <div className="mx-auto flex h-full max-w-6xl flex-col gap-4 overflow-auto pb-8">
      <div className="flex flex-wrap items-end justify-between gap-2">
        <div>
          <h1 className="text-lg font-semibold">How accurate is the draft?</h1>
          <p className="max-w-2xl text-sm text-muted">
            Each configuration filled the form for {n} labelled case{n === 1 ? '' : 's'}. Every answer is compared with the gold label.
            <b className="text-ink"> Hallucinations</b> are answers filled in when the notes don't say anything about that question.
            This is the error that matters most on a medical form.
          </p>
        </div>
        {Object.keys(runs).length > 1 && (
          <select className="rounded-md border border-line bg-panel px-2 py-1.5 text-sm" value={run} onChange={(e) => setRun(e.target.value)}>
            {Object.keys(runs).map((r) => <option key={r}>{r}</option>)}
          </select>
        )}
      </div>

      {best && <Headline best={best} baseline={baseline} />}
      <ConfigTable configs={configs} bestName={best?.[0]} />
      {best && <Breakdown name={best[0]} cfg={best[1]} />}
    </div>
  )
}

function Headline({ best, baseline }: { best: [string, EvalConfig]; baseline?: [string, EvalConfig] }) {
  const b = best[1].aggregate
  const o = baseline?.[1].aggregate
  const tiles = [
    { label: 'Facts filled correctly', value: pct(b.overall.accuracy), was: o && pct(o.overall.accuracy) },
    { label: 'Filled answers that are right', value: pct(b.overall.precision), was: o && pct(o.overall.precision) },
    { label: 'Hallucinated answers per form', value: (b.overall.hallucinations_per_case ?? 0).toFixed(1), was: o && (o.overall.hallucinations_per_case ?? 0).toFixed(1) },
    { label: 'Time per form (median)', value: secs(b.latency_ms.p50), was: o && secs(o.latency_ms.p50) },
  ]
  return (
    <section>
      <p className="mb-2 text-xs text-muted">
        Best: <b className="text-ink">{best[1].config.model} · {VARIANT[best[1].config.variant]}</b>
        {baseline && <> vs the original prototype ({baseline[1].config.model})</>}
      </p>
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        {tiles.map((t) => (
          <div key={t.label} className="rounded-lg border border-line bg-panel p-4">
            <div className="text-xs text-muted">{t.label}</div>
            <div className="mt-1 text-3xl font-semibold tracking-tight tabular-nums">{t.value}</div>
            {t.was && <div className="mt-1 text-xs text-faint tabular-nums">prototype: {t.was}</div>}
          </div>
        ))}
      </div>
    </section>
  )
}

/** Thin single-hue meter; the number beside it carries the value. */
function Meter({ value, max = 1, invert = false, label }: { value: number | null; max?: number; invert?: boolean; label: string }) {
  const w = value == null ? 0 : Math.max(2, Math.min(100, (value / max) * 100))
  return (
    <div className="flex items-center gap-2" title={label}>
      <span className="w-12 text-right text-xs tabular-nums">{label}</span>
      <span className="relative h-1.5 w-20 rounded-full bg-sunken">
        <span className={cx('absolute inset-y-0 left-0 rounded-full', invert ? 'bg-faint' : 'bg-accent')} style={{ width: `${w}%` }} />
      </span>
    </div>
  )
}

function ConfigTable({ configs, bestName }: { configs: [string, EvalConfig][]; bestName?: string }) {
  const maxHall = Math.max(...configs.map(([, c]) => c.aggregate.overall.hallucinations_per_case ?? 0), 1)
  const maxLat = Math.max(...configs.map(([, c]) => c.aggregate.latency_ms.p50), 1)
  const rows = [...configs].sort(([, a], [, b]) => b.aggregate.overall.f1 - a.aggregate.overall.f1)
  return (
    <Panel title="All configurations">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-left text-xs text-muted">
            <tr className="border-b border-line">
              <th className="px-4 py-2 font-medium">Model</th>
              <th className="px-2 py-2 font-medium">Pipeline</th>
              <th className="px-2 py-2 font-medium">Accuracy</th>
              <th className="px-2 py-2 font-medium">Precision</th>
              <th className="px-2 py-2 font-medium">Hallucinations / form</th>
              <th className="px-2 py-2 font-medium">Median time</th>
              <th className="px-2 py-2 font-medium">Sections found</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(([name, c]) => {
              const a = c.aggregate
              return (
                <tr key={name} className={cx('border-b border-line last:border-0', name === bestName && 'bg-accent-soft/50')}>
                  <td className="px-4 py-2 font-mono text-xs">{c.config.model}{c.config.think ? ' (think)' : ''}</td>
                  <td className="px-2 py-2 text-xs">{VARIANT[c.config.variant] ?? c.config.variant}{c.config.drop_ungrounded ? ' + drop unquoted' : ''}</td>
                  <td className="px-2 py-2"><Meter value={a.overall.accuracy} label={pct(a.overall.accuracy)} /></td>
                  <td className="px-2 py-2"><Meter value={a.overall.precision} label={pct(a.overall.precision)} /></td>
                  <td className="px-2 py-2"><Meter value={a.overall.hallucinations_per_case} max={maxHall} invert label={(a.overall.hallucinations_per_case ?? 0).toFixed(1)} /></td>
                  <td className="px-2 py-2"><Meter value={a.latency_ms.p50} max={maxLat} invert label={secs(a.latency_ms.p50)} /></td>
                  <td className="px-2 py-2 text-xs tabular-nums">
                    {pct(a.section_detection.recall)} recall · {pct(a.section_detection.precision)} precision
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </Panel>
  )
}

const KIND_LABEL: Record<string, string> = { enum: 'Multiple choice', bool: 'Checkboxes', text: 'Free text', year: 'Years', number: 'Numbers' }

function RateTable({ title, rows }: { title: string; rows: [string, Rates][] }) {
  return (
    <Panel title={title}>
      <table className="w-full text-sm">
        <thead className="text-left text-xs text-muted">
          <tr className="border-b border-line">
            <th className="px-4 py-1.5 font-medium" />
            <th className="px-2 py-1.5 font-medium">Facts</th>
            <th className="px-2 py-1.5 font-medium">Accuracy</th>
            <th className="px-2 py-1.5 font-medium">Halluc. rate</th>
          </tr>
        </thead>
        <tbody>
          {rows.filter(([, r]) => r.n_gold > 0).map(([k, r]) => (
            <tr key={k} className="border-b border-line last:border-0">
              <td className="px-4 py-1.5 text-xs">{k}</td>
              <td className="px-2 py-1.5 text-xs text-muted tabular-nums">{r.n_gold}</td>
              <td className="px-2 py-1.5"><Meter value={r.accuracy} label={pct(r.accuracy)} /></td>
              <td className="px-2 py-1.5 text-xs tabular-nums">{pct(r.hallucination_rate, 1)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Panel>
  )
}

function Breakdown({ name, cfg }: { name: string; cfg: EvalConfig }) {
  const a = cfg.aggregate
  const g = a.grounding
  const kinds = Object.entries(a.by_kind).map(([k, r]) => [KIND_LABEL[k] ?? k, r] as [string, Rates])
  const sections = Object.entries(a.by_section).sort(([, x], [, y]) => y.n_gold - x.n_gold)
  return (
    <section className="flex flex-col gap-3">
      <h2 className="text-sm font-semibold">Where the best configuration goes wrong <span className="font-normal text-muted">({name.replace('|', ' · ')})</span></h2>
      <div className="grid gap-3 md:grid-cols-2">
        <RateTable title="By answer type" rows={kinds} />
        <RateTable title="By form section" rows={sections} />
      </div>
      {g.flag_precision != null && (
        <Panel title="Does the “no quote found” flag catch errors?">
          <div className="grid gap-4 p-4 text-sm md:grid-cols-[auto_1fr]">
            <table className="text-xs tabular-nums">
              <thead className="text-muted">
                <tr><th /><th className="px-3 py-1 font-medium">Correct</th><th className="px-3 py-1 font-medium">Wrong</th></tr>
              </thead>
              <tbody>
                <tr><td className="pr-3 text-muted">Quote found</td><td className="px-3 py-1 text-center">{g.grounded_correct ?? 0}</td><td className="px-3 py-1 text-center">{g.grounded_incorrect ?? 0}</td></tr>
                <tr><td className="pr-3 text-muted">Flagged</td><td className="px-3 py-1 text-center">{g.ungrounded_correct ?? 0}</td><td className="px-3 py-1 text-center font-semibold">{g.ungrounded_incorrect ?? 0}</td></tr>
              </tbody>
            </table>
            <p className="text-muted">
              Of the answers the UI flags for review, <b className="text-ink">{pct(g.flag_precision)}</b> really are wrong, and the flag
              catches <b className="text-ink">{pct(g.flag_recall)}</b> of all wrong answers. The flag points the reviewer at likely errors.
              It doesn't replace reviewing the whole form.
            </p>
          </div>
        </Panel>
      )}
    </section>
  )
}
