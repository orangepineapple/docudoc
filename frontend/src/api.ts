export type FieldKind = 'enum' | 'bool' | 'text' | 'year' | 'number'
export type Value = string | boolean

export interface FieldDef {
  key: string
  section: string
  kind: FieldKind
  description: string
  mandatory: boolean
  options: { value: string; label: string }[]
}

export interface FormSchema {
  id: string
  title: string
  sections: { id: string; label: string; description: string }[]
  fields: FieldDef[]
  profile_fields: Record<string, string>
  practitioner_types: string[]
  variants: string[]
}

export interface FieldMeta {
  evidence: string
  grounded: boolean
  spans: [number, number][]
  score: number
  dropped?: boolean
}

export interface Issue {
  field: string | null
  severity: 'error' | 'warning' | 'info'
  message: string
  rule: string
}

export type SectionStatus = 'pending' | 'skipped' | 'extracted' | 'empty' | 'error'

export type ExtractEvent =
  | { type: 'routed'; sections: string[] }
  | { type: 'warning'; message: string }
  | { type: 'section'; section: string; status: SectionStatus; errors: string[]; values: Record<string, Value>; meta: Record<string, FieldMeta> }
  | { type: 'done'; result: ExtractResult }
  | { type: 'error'; message: string }

export interface ExtractResult {
  values: Record<string, Value>
  fields: Record<string, FieldMeta>
  sections: Record<string, { status: SectionStatus; errors?: string[]; ms?: number }>
  issues: Issue[]
  routed: string[]
  stats: { ms: number; prompt_tokens: number; output_tokens: number; errors: number }
}

export interface Sample {
  id: string
  style: string | null
  sections: string[]
  notes: string
}

export const NOT_MENTIONED = 'not_mentioned'

export const isEmpty = (v: Value | undefined) => v === undefined || v === '' || v === false || v === NOT_MENTIONED

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`)
  return res.json() as Promise<T>
}

export const api = {
  form: (id = 't2201') => fetch(`/api/forms/${id}`).then(json<FormSchema>),
  models: () => fetch('/api/models').then(json<{ ok: boolean; error?: string; models: { name: string }[]; default: string }>),
  samples: () => fetch('/api/samples').then(json<Sample[]>),
  evalRuns: () => fetch('/api/eval').then(json<Record<string, Record<string, EvalConfig>>>),

  validate: (values: Record<string, Value>, formId = 't2201') =>
    fetch('/api/validate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ form_id: formId, values }),
    }).then(json<{ issues: Issue[] }>),

  fill: async (values: Record<string, Value>, profile: Record<string, string>, formId = 't2201') => {
    const res = await fetch('/api/fill', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ form_id: formId, values, profile }),
    })
    if (!res.ok) throw new Error(`${res.status} ${await res.text()}`)
    return res.blob()
  },

  /** POST + server-sent events. EventSource can't POST, so parse the stream by hand. */
  async extract(body: { notes: string; model: string; variant: string }, onEvent: (e: ExtractEvent) => void, signal: AbortSignal) {
    const res = await fetch('/api/extract', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ form_id: 't2201', ...body }),
      signal,
    })
    if (!res.ok || !res.body) throw new Error(`${res.status} ${await res.text()}`)
    const reader = res.body.pipeThrough(new TextDecoderStream()).getReader()
    let buf = ''
    for (;;) {
      const { value, done } = await reader.read()
      if (done) break
      buf += value
      let i: number
      while ((i = buf.indexOf('\n\n')) >= 0) {
        const block = buf.slice(0, i)
        buf = buf.slice(i + 2)
        const data = block.split('\n').find((l) => l.startsWith('data: '))
        if (data) onEvent(JSON.parse(data.slice(6)) as ExtractEvent)
      }
    }
  },
}

export interface Rates {
  accuracy: number | null
  precision: number | null
  f1: number
  hallucination_rate: number | null
  omission_rate: number | null
  wrong_rate: number | null
  hallucinations_per_case: number | null
  n_gold: number
}

export interface EvalConfig {
  config: { model: string; variant: string; route: boolean; think: boolean; drop_ungrounded: boolean }
  aggregate: {
    n_cases: number
    overall: Rates
    by_kind: Record<string, Rates>
    by_section: Record<string, Rates>
    section_detection: { precision: number | null; recall: number | null }
    grounding: { flag_precision: number | null; flag_recall: number | null } & Record<string, number | null>
    latency_ms: { mean: number; p50: number; max: number }
    tokens_per_case: { prompt: number; output: number }
    schema_errors: number
    counts: Record<string, number>
  }
}
