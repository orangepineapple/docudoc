import { Activity, useEffect, useState } from 'react'
import { api, type FormSchema } from './api'
import { EvalPage } from './eval/EvalPage'
import { cx } from './styles'
import { Workspace } from './workspace/Workspace'

type Tab = 'workspace' | 'eval'

export default function App() {
  const [tab, setTab] = useState<Tab>(() => (location.hash === '#eval' ? 'eval' : 'workspace'))
  const [form, setForm] = useState<FormSchema | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.form().then(setForm, (e) => setError(String(e)))
  }, [])

  useEffect(() => {
    history.replaceState(null, '', tab === 'eval' ? '#eval' : '#')
  }, [tab])

  return (
    <div className="flex h-full flex-col">
      <header className="flex flex-wrap items-center gap-x-6 gap-y-2 border-b border-line bg-panel px-4 py-2.5">
        <div className="flex items-baseline gap-2">
          <span className="text-[15px] font-semibold tracking-tight">FormFiller</span>
          <span className="hidden text-xs text-muted sm:inline">{form?.title ?? 'T2201 Disability Tax Credit'}</span>
        </div>
        <nav className="flex gap-1">
          {(['workspace', 'eval'] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={cx('rounded-md px-3 py-1 text-sm', tab === t ? 'bg-accent-soft font-medium text-accent' : 'text-muted hover:text-ink')}
            >
              {t === 'workspace' ? 'Workspace' : 'Evaluation'}
            </button>
          ))}
        </nav>
        <span className="ml-auto flex items-center gap-1.5 text-xs text-muted" title="Extraction runs on a local Ollama model">
          <span className="size-1.5 rounded-full bg-ok" /> Runs locally: notes never leave this machine
        </span>
      </header>
      <div className="border-b border-line bg-warn-soft px-4 py-1.5 text-xs text-warn">
        AI-assisted draft. The practitioner must review every answer before signing. Use de-identified notes in this demo.
      </div>

      <main className="min-h-0 flex-1 p-3">
        {error && <p className="p-6 text-sm text-error">Can't reach the API ({error}). Is the backend running on :8000?</p>}
        {form && (
          <>
            <Activity mode={tab === 'workspace' ? 'visible' : 'hidden'}>
              <Workspace form={form} />
            </Activity>
            <Activity mode={tab === 'eval' ? 'visible' : 'hidden'}>
              <EvalPage />
            </Activity>
          </>
        )}
      </main>
    </div>
  )
}
