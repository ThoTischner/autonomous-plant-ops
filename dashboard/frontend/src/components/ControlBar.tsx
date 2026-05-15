import { useEffect, useState } from 'react'
import EquipmentModal from './EquipmentModal'

const API = '/api'

const SCENARIO_LABELS: Record<string, string> = {
  thermal_runaway: 'Thermal Runaway',
  bearing_degradation: 'Bearing Degradation',
  compressor_surge: 'Compressor Surge',
  pressure_spike: 'Pressure Spike',
}

export default function ControlBar() {
  const [scenarios, setScenarios] = useState<string[]>([])
  const [busy, setBusy] = useState<string | null>(null)
  const [msg, setMsg] = useState('')

  const [equipOpen, setEquipOpen] = useState(false)
  const [promptOpen, setPromptOpen] = useState(false)
  const [prompt, setPrompt] = useState('')
  const [isDefault, setIsDefault] = useState(true)
  const [promptDirty, setPromptDirty] = useState(false)
  const [savingPrompt, setSavingPrompt] = useState(false)

  useEffect(() => {
    fetch(`${API}/control/scenarios`)
      .then((r) => r.json())
      .then((d) => Array.isArray(d) && setScenarios(d))
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
      setMsg((await r.json()).message ?? `${name} ausgelöst`)
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
      setMsg((await r.json()).message ?? 'Zurückgesetzt')
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

  const list = scenarios.length ? scenarios : Object.keys(SCENARIO_LABELS)

  return (
    <div className="flex items-center gap-2 flex-wrap">
      <span className="text-[10px] uppercase tracking-wider text-gray-500 mr-1">
        Szenario
      </span>
      {list.map((s) => (
        <button
          key={s}
          onClick={() => trigger(s)}
          disabled={busy !== null}
          className="px-2.5 py-1 text-xs rounded-md bg-plant-card border border-plant-border
                     hover:border-plant-warning hover:text-plant-warning
                     disabled:opacity-50 transition-colors"
        >
          {busy === s ? '…' : SCENARIO_LABELS[s] ?? s}
        </button>
      ))}

      <button
        onClick={resetPlant}
        disabled={busy !== null}
        className="px-2.5 py-1 text-xs rounded-md bg-plant-success/15
                   border border-plant-success/40 text-plant-success
                   hover:bg-plant-success/25 disabled:opacity-50 transition-colors"
      >
        {busy === 'reset' ? '…' : '↺ Normalzustand wiederherstellen'}
      </button>

      <div className="h-5 w-px bg-plant-border mx-1" />

      <button
        onClick={() => setEquipOpen(true)}
        className="px-2.5 py-1 text-xs rounded-md bg-plant-card border border-plant-border
                   hover:border-plant-accent hover:text-plant-accent transition-colors"
      >
        Equipment
      </button>

      <button
        onClick={() => setPromptOpen(true)}
        className="px-2.5 py-1 text-xs rounded-md bg-plant-card border border-plant-border
                   hover:border-plant-accent hover:text-plant-accent transition-colors
                   flex items-center gap-1.5"
      >
        System-Prompt
        <span
          className={`text-[9px] px-1 py-px rounded ${
            isDefault ? 'bg-plant-border text-gray-400'
                      : 'bg-plant-warning/20 text-plant-warning'
          }`}
        >
          {isDefault ? 'Default' : 'Angepasst'}
        </span>
      </button>

      {msg && (
        <span className="text-[11px] text-gray-500 ml-1 max-w-[260px] truncate">
          {msg}
        </span>
      )}

      <EquipmentModal open={equipOpen} onClose={() => setEquipOpen(false)} />

      {promptOpen && (
        <div
          className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-6"
          onClick={() => setPromptOpen(false)}
        >
          <div
            className="bg-plant-card border border-plant-border rounded-xl w-full max-w-3xl p-5"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-bold text-gray-200 uppercase tracking-wider">
                System-Prompt des AI-Agenten
              </h2>
              <button
                onClick={() => setPromptOpen(false)}
                className="text-gray-500 hover:text-white text-lg leading-none"
                aria-label="Schließen"
              >
                ×
              </button>
            </div>
            <textarea
              value={prompt}
              onChange={(e) => {
                setPrompt(e.target.value)
                setPromptDirty(true)
              }}
              spellCheck={false}
              className="w-full h-72 text-xs font-mono p-3 rounded-lg bg-plant-bg
                         border border-plant-border text-gray-300
                         focus:outline-none focus:border-plant-accent resize-y"
            />
            <div className="flex gap-2 mt-3">
              <button
                onClick={savePrompt}
                disabled={savingPrompt || !promptDirty}
                className="px-3 py-1.5 text-xs rounded-lg bg-plant-accent/20
                           border border-plant-accent/40 text-plant-accent
                           hover:bg-plant-accent/30 disabled:opacity-40 transition-colors"
              >
                Speichern
              </button>
              <button
                onClick={resetPrompt}
                disabled={savingPrompt || isDefault}
                className="px-3 py-1.5 text-xs rounded-lg bg-plant-card
                           border border-plant-border text-gray-400
                           hover:text-white disabled:opacity-40 transition-colors"
              >
                Default
              </button>
              <span className="ml-auto self-center text-[11px] text-gray-500">
                {isDefault ? 'Standard-Prompt aktiv' : 'Angepasster Prompt aktiv'}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
