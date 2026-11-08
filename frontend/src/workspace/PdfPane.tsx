import { useEffect, useState } from 'react'
import { api, type FormSchema, type Issue, type Value } from '../api'
import { Panel, Spinner } from '../ui'
import { btn, input } from '../styles'

const PROFILE_KEY = 'formfiller.profile'

function loadProfile(): Record<string, string> {
  try {
    return JSON.parse(localStorage.getItem(PROFILE_KEY) ?? '{}')
  } catch {
    return {}
  }
}

const label = (t: string) => t.replace(/_/g, ' ').replace(/^\w/, (c) => c.toUpperCase())

export function PdfPane({ form, values, ready, issues }: { form: FormSchema; values: Record<string, Value>; ready: boolean; issues: Issue[] }) {
  const [profile, setProfile] = useState<Record<string, string>>(() => ({ practitioner_type: 'medical_doctor', ...loadProfile() }))
  const [url, setUrl] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Practitioner details are remembered locally; the patient name is not.
  useEffect(() => {
    const { patient_name: _p, ...keep } = profile
    try {
      localStorage.setItem(PROFILE_KEY, JSON.stringify(keep))
    } catch { /* storage unavailable */ }
  }, [profile])

  useEffect(() => () => { if (url) URL.revokeObjectURL(url) }, [url])

  async function generate() {
    setBusy(true)
    setError(null)
    try {
      const blob = await api.fill(values, profile)
      setUrl(URL.createObjectURL(blob))
    } catch (e) {
      setError(String(e))
    } finally {
      setBusy(false)
    }
  }

  const required = issues.filter((i) => i.severity === 'error').length
  const set = (k: string, v: string) => setProfile((p) => ({ ...p, [k]: v }))

  return (
    <Panel
      title="PDF"
      actions={url && <a className={btn.link} href={url} download={`${form.id}-draft.pdf`}>Download</a>}
    >
      <div className="flex h-full flex-col">
        <details className="border-b border-line px-4 py-2.5" open={!url}>
          <summary className="cursor-pointer text-xs font-medium text-muted">Patient &amp; practitioner (not sent to the model)</summary>
          <div className="mt-2 grid grid-cols-2 gap-2">
            <Field label="Patient name" className="col-span-2">
              <input className={input} value={profile.patient_name ?? ''} onChange={(e) => set('patient_name', e.target.value)} />
            </Field>
            <Field label="Practitioner type">
              <select className={input} value={profile.practitioner_type ?? ''} onChange={(e) => set('practitioner_type', e.target.value)}>
                {form.practitioner_types.map((t) => <option key={t} value={t}>{label(t)}</option>)}
              </select>
            </Field>
            <Field label="Initials">
              <input className={input} value={profile.practitioner_initials ?? ''} onChange={(e) => set('practitioner_initials', e.target.value)} maxLength={4} />
            </Field>
            <Field label="Practitioner name" className="col-span-2">
              <input className={input} value={profile.practitioner_name ?? ''} onChange={(e) => set('practitioner_name', e.target.value)} />
            </Field>
            <Field label="Licence no.">
              <input className={input} value={profile.license_number ?? ''} onChange={(e) => set('license_number', e.target.value)} />
            </Field>
            <Field label="Telephone">
              <input className={input} value={profile.telephone ?? ''} onChange={(e) => set('telephone', e.target.value)} />
            </Field>
          </div>
          <p className="mt-2 text-[11px] text-faint">Practitioner details are remembered in this browser. The patient name is not saved.</p>
        </details>
        <div className="flex items-center gap-2 px-4 py-2.5">
          <button className={btn.primary} onClick={generate} disabled={!ready || busy}>
            {busy && <Spinner />} {url ? 'Regenerate PDF' : 'Generate PDF'}
          </button>
          {required > 0 && <span className="text-xs text-error">{required} required field{required > 1 ? 's' : ''} still empty</span>}
          {error && <span className="text-xs text-error">{error}</span>}
        </div>
        <div className="min-h-[24rem] flex-1 border-t border-line bg-sunken">
          {url ? (
            <iframe title="Filled form preview" src={url} className="h-full min-h-[24rem] w-full" />
          ) : (
            <p className="p-6 text-center text-xs text-faint">{ready ? 'Generate the PDF to preview it here.' : 'The preview appears once the draft is ready.'}</p>
          )}
        </div>
      </div>
    </Panel>
  )
}

function Field({ label, className, children }: { label: string; className?: string; children: React.ReactNode }) {
  return (
    <label className={className}>
      <span className="mb-0.5 block text-[11px] text-muted">{label}</span>
      {children}
    </label>
  )
}
