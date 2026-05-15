import { useEffect, useRef, useState } from 'react'
import EquipmentModal from './EquipmentModal'

const API = '/api'

interface ScenarioMeta {
  label: string
  desc: string
}

// Fleet-themed (Fuhrpark) scenarios. Keys are the backend scenario ids.
const SCENARIO_META: Record<string, ScenarioMeta> = {
  thermal_runaway: {
    label: 'Motorüberhitzung',
    desc: 'LKW TR-501: Kühlmittelausfall/Überlast — die Motortemperatur '
      + 'steigt kontinuierlich bis in den kritischen Bereich. Der KI-Agent '
      + 'muss kühlen bzw. notabschalten und danach wieder anfahren.',
  },
  bearing_degradation: {
    label: 'Lagerschaden',
    desc: 'Gabelstapler FL-401: fortschreitender Radlagerverschleiß — '
      + 'Vibration und Temperatur steigen langsam an.',
  },
  compressor_surge: {
    label: 'Antriebsinstabilität',
    desc: 'Transportroboter AGV-601: instabiler Fahrantrieb — der '
      + 'Systemdruck pendelt stark und die Vibration nimmt zu.',
  },
  pressure_spike: {
    label: 'Hydraulikdruckspitze',
    desc: 'Gabelstapler FL-402: plötzliche Druckspitze im Hydrauliksystem '
      + '(Ventil-/Pumpenfehler).',
  },
}

function scenarioLabel(id: string): string {
  return SCENARIO_META[id]?.label ?? id
}

export default function ControlBar() {
  const [scenarios, setScenarios] = useState<string[]>([])
  const [busy, setBusy] = useState<string | null>(null)
  const [msg, setMsg] = useState('')
  // Transient confirmation: { id, ok } — flashes the clicked button and a
  // toast for a few seconds after a scenario / reset action.
  const [flash, setFlash] = useState<{ id: string; ok: boolean } | null>(null)
  const flashTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  function showFlash(id: string, ok: boolean) {
    if (flashTimer.current) clearTimeout(flashTimer.current)
    setFlash({ id, ok })
    flashTimer.current = setTimeout(() => setFlash(null), 3000)
  }

  useEffect(() => () => {
    if (flashTimer.current) clearTimeout(flashTimer.current)
  }, [])

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
      .catch(() => setScenarios(Object.keys(SCENARIO_META)))
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
      const m = (await r.json()).message
      setMsg(m ?? `Szenario „${scenarioLabel(name)}" ausgelöst`)
      showFlash(name, r.ok)
    } catch {
      setMsg(`Fehler beim Auslösen von „${scenarioLabel(name)}"`)
      showFlash(name, false)
    } finally {
      setBusy(null)
    }
  }

  async function resetPlant() {
    setBusy('reset')
    setMsg('')
    try {
      const r = await fetch(`${API}/control/reset`, { method: 'POST' })
      setMsg((await r.json()).message ?? 'Normalzustand wiederhergestellt')
      showFlash('reset', r.ok)
    } catch {
      setMsg('Fehler beim Zurücksetzen')
      showFlash('reset', false)
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

  const list = scenarios.length ? scenarios : Object.keys(SCENARIO_META)

  return (
    <div className="flex items-center gap-2 flex-wrap">
      <span className="text-[10px] uppercase tracking-wider text-gray-500 mr-1">
        Szenario
      </span>
      {list.map((s) => {
        const desc = SCENARIO_META[s]?.desc
        const flashed = flash?.id === s
        const flashOk = flashed && flash?.ok
        const flashErr = flashed && !flash?.ok
        return (
          <div
            key={s}
            className={`flex items-center rounded-md border transition-colors overflow-hidden ${
              flashOk
                ? 'bg-plant-success/20 border-plant-success'
                : flashErr
                  ? 'bg-plant-danger/20 border-plant-danger'
                  : 'bg-plant-card border-plant-border hover:border-plant-warning'
            }`}
          >
            <button
              onClick={() => trigger(s)}
              disabled={busy !== null}
              title={desc}
              className={`px-2.5 py-1 text-xs disabled:opacity-50 transition-colors ${
                flashOk
                  ? 'text-plant-success font-semibold'
                  : flashErr
                    ? 'text-plant-danger font-semibold'
                    : 'hover:text-plant-warning'
              }`}
            >
              {busy === s
                ? '…'
                : flashOk
                  ? `✓ ${scenarioLabel(s)}`
                  : flashErr
                    ? `✕ ${scenarioLabel(s)}`
                    : scenarioLabel(s)}
            </button>
            {desc && (
              <span
                title={desc}
                aria-label={`Erklärung: ${scenarioLabel(s)}`}
                className="flex items-center justify-center w-5 h-6 text-[10px]
                           font-bold text-gray-500 border-l border-plant-border
                           cursor-help hover:text-plant-warning hover:bg-plant-warning/10"
              >
                ?
              </span>
            )}
          </div>
        )
      })}

      <button
        onClick={resetPlant}
        disabled={busy !== null}
        className={`px-2.5 py-1 text-xs rounded-md border transition-colors
                   disabled:opacity-50 ${
          flash?.id === 'reset' && flash?.ok
            ? 'bg-plant-success/30 border-plant-success text-plant-success font-semibold'
            : 'bg-plant-success/15 border-plant-success/40 text-plant-success hover:bg-plant-success/25'
        }`}
      >
        {busy === 'reset'
          ? '…'
          : flash?.id === 'reset' && flash?.ok
            ? '✓ Normalzustand wiederhergestellt'
            : '↺ Normalzustand wiederherstellen'}
      </button>

      <div className="h-5 w-px bg-plant-border mx-1" />

      <button
        onClick={() => setEquipOpen(true)}
        className="px-2.5 py-1 text-xs rounded-md bg-plant-card border border-plant-border
                   hover:border-plant-accent hover:text-plant-accent transition-colors"
      >
        Anlagen
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
          {isDefault ? 'Standard' : 'Angepasst'}
        </span>
      </button>

      {msg && (
        <span
          className={`ml-1 px-2 py-1 rounded-md text-[11px] max-w-[320px] truncate
                     border transition-colors ${
            flash && !flash.ok
              ? 'bg-plant-danger/15 border-plant-danger/40 text-plant-danger'
              : flash
                ? 'bg-plant-success/15 border-plant-success/40 text-plant-success'
                : 'bg-plant-card border-plant-border text-gray-400'
          }`}
          title={msg}
        >
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
                System-Prompt des KI-Agenten
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
                Standard
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
