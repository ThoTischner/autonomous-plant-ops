import { useEffect, useState } from 'react'

const API = '/api'

const SCENARIO_LABELS: Record<string, string> = {
  thermal_runaway: 'Thermal Runaway',
  bearing_degradation: 'Bearing Degradation',
  compressor_surge: 'Compressor Surge',
  pressure_spike: 'Pressure Spike',
}

export default function ControlPanel() {
  const [scenarios, setScenarios] = useState<string[]>([])
  const [busy, setBusy] = useState<string | null>(null)
  const [msg, setMsg] = useState<string>('')

  const [prompt, setPrompt] = useState('')
  const [isDefault, setIsDefault] = useState(true)
  const [promptDirty, setPromptDirty] = useState(false)
  const [savingPrompt, setSavingPrompt] = useState(false)

  useEffect(() => {
    fetch(`${API}/control/scenarios`)
      .then((r) => r.json())
      .then((data) => Array.isArray(data) && setScenarios(data))
      .catch(() => setScenarios(Object.keys(SCENARIO_LABELS)))
    loadPrompt()
  }, [])

  function loadPrompt() {
    fetch(`${API}/control/prompt`)
      .then((r) => r.json())
      .then((d) => {
        setPrompt(d.prompt ?? '')
        setIsDefault(Boolean(d.is_default))
        setPromptDirty(false)
      })
      .catch(() => {})
  }

  async function trigger(name: string) {
    setBusy(name)
    setMsg('')
    try {
      const r = await fetch(`${API}/control/scenario`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario: name }),
      })
      const d = await r.json()
      setMsg(d.message ?? `${name} ausgelöst`)
    } catch {
      setMsg('Fehler beim Auslösen')
    } finally {
      setBusy(null)
    }
  }

  async function resetPlant() {
    setBusy('reset')
    setMsg('')
    try {
      const r = await fetch(`${API}/control/reset`, { method: 'POST' })
      const d = await r.json()
      setMsg(d.message ?? 'Zurückgesetzt')
    } catch {
      setMsg('Fehler beim Zurücksetzen')
    } finally {
      setBusy(null)
    }
  }

  async function savePrompt() {
    setSavingPrompt(true)
    try {
      const r = await fetch(`${API}/control/prompt`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
      })
      const d = await r.json()
      setPrompt(d.prompt ?? prompt)
      setIsDefault(Boolean(d.is_default))
      setPromptDirty(false)
    } finally {
      setSavingPrompt(false)
    }
  }

  async function resetPrompt() {
    setSavingPrompt(true)
    try {
      const r = await fetch(`${API}/control/prompt/reset`, { method: 'POST' })
      const d = await r.json()
      setPrompt(d.prompt ?? '')
      setIsDefault(Boolean(d.is_default))
      setPromptDirty(false)
    } finally {
      setSavingPrompt(false)
    }
  }

  return (
    <div className="p-4 border-b border-plant-border">
      <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">
        Steuerung
      </h2>

      <div className="grid grid-cols-2 gap-2">
        {(scenarios.length ? scenarios : Object.keys(SCENARIO_LABELS)).map((s) => (
          <button
            key={s}
            onClick={() => trigger(s)}
            disabled={busy !== null}
            className="px-2 py-2 text-xs rounded-lg bg-plant-card border border-plant-border
                       hover:border-plant-warning hover:text-plant-warning
                       disabled:opacity-50 transition-colors"
          >
            {busy === s ? '…' : SCENARIO_LABELS[s] ?? s}
          </button>
        ))}
      </div>

      <button
        onClick={resetPlant}
        disabled={busy !== null}
        className="mt-2 w-full px-2 py-2 text-xs rounded-lg bg-plant-success/15
                   border border-plant-success/40 text-plant-success
                   hover:bg-plant-success/25 disabled:opacity-50 transition-colors"
      >
        {busy === 'reset' ? '…' : '↺ Normalzustand wiederherstellen'}
      </button>

      {msg && <p className="mt-2 text-[11px] text-gray-400">{msg}</p>}

      <div className="mt-5">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-400">
            System-Prompt
          </h2>
          <span
            className={`text-[10px] px-1.5 py-0.5 rounded ${
              isDefault
                ? 'bg-plant-border text-gray-400'
                : 'bg-plant-warning/20 text-plant-warning'
            }`}
          >
            {isDefault ? 'Default' : 'Angepasst'}
          </span>
        </div>
        <textarea
          value={prompt}
          onChange={(e) => {
            setPrompt(e.target.value)
            setPromptDirty(true)
          }}
          spellCheck={false}
          className="w-full h-40 text-[11px] font-mono p-2 rounded-lg
                     bg-plant-bg border border-plant-border text-gray-300
                     focus:outline-none focus:border-plant-accent resize-y"
        />
        <div className="flex gap-2 mt-2">
          <button
            onClick={savePrompt}
            disabled={savingPrompt || !promptDirty}
            className="flex-1 px-2 py-1.5 text-xs rounded-lg bg-plant-accent/20
                       border border-plant-accent/40 text-plant-accent
                       hover:bg-plant-accent/30 disabled:opacity-40 transition-colors"
          >
            Speichern
          </button>
          <button
            onClick={resetPrompt}
            disabled={savingPrompt || isDefault}
            className="px-2 py-1.5 text-xs rounded-lg bg-plant-card
                       border border-plant-border text-gray-400
                       hover:text-white disabled:opacity-40 transition-colors"
          >
            Default
          </button>
        </div>
      </div>
    </div>
  )
}
