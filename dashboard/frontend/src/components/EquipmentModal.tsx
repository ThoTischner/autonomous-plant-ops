import { useEffect, useState } from 'react'
import type { EquipmentDef } from '../types'

const API = '/api'

interface Props {
  open: boolean
  onClose: () => void
}

interface RangeForm {
  min: string
  max: string
  unit: string
}
interface Form {
  equipment_id: string
  name: string
  etype: string
  temperature: RangeForm
  pressure: RangeForm
  vibration: RangeForm
  hasFlow: boolean
  flow_rate: RangeForm
}

const EMPTY: Form = {
  equipment_id: '',
  name: '',
  etype: 'pump',
  temperature: { min: '0', max: '100', unit: '°C' },
  pressure: { min: '0', max: '10', unit: 'bar' },
  vibration: { min: '0', max: '5', unit: 'mm/s' },
  hasFlow: false,
  flow_rate: { min: '0', max: '100', unit: 'L/min' },
}

const TYPES = ['pump', 'reactor', 'compressor', 'generic']

function toForm(e: EquipmentDef): Form {
  const r = (x: { min: number; max: number; unit: string } | null, d: RangeForm) =>
    x ? { min: String(x.min), max: String(x.max), unit: x.unit } : d
  return {
    equipment_id: e.equipment_id,
    name: e.name,
    etype: e.etype || 'generic',
    temperature: r(e.temperature, EMPTY.temperature),
    pressure: r(e.pressure, EMPTY.pressure),
    vibration: r(e.vibration, EMPTY.vibration),
    hasFlow: e.flow_rate != null,
    flow_rate: r(e.flow_rate, EMPTY.flow_rate),
  }
}

export default function EquipmentModal({ open, onClose }: Props) {
  const [list, setList] = useState<EquipmentDef[]>([])
  const [form, setForm] = useState<Form>(EMPTY)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')

  useEffect(() => {
    if (open) load()
  }, [open])

  function load() {
    fetch(`${API}/control/equipment`)
      .then((r) => r.json())
      .then((d) => Array.isArray(d) && setList(d))
      .catch(() => setErr('Liste konnte nicht geladen werden'))
  }

  function rng(f: RangeForm) {
    return { min: parseFloat(f.min), max: parseFloat(f.max), unit: f.unit }
  }

  async function save() {
    setBusy(true)
    setErr('')
    const body = {
      equipment_id: form.equipment_id.trim(),
      name: form.name.trim() || form.equipment_id.trim(),
      etype: form.etype,
      temperature: rng(form.temperature),
      pressure: rng(form.pressure),
      vibration: rng(form.vibration),
      flow_rate: form.hasFlow ? rng(form.flow_rate) : null,
    }
    const isEdit = editingId && list.some((e) => e.equipment_id === editingId)
    try {
      const r = await fetch(
        isEdit
          ? `${API}/control/equipment/${editingId}`
          : `${API}/control/equipment`,
        {
          method: isEdit ? 'PUT' : 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        },
      )
      if (!r.ok) {
        const d = await r.json().catch(() => ({}))
        setErr(d.detail || `Fehler (${r.status})`)
      } else {
        setForm(EMPTY)
        setEditingId(null)
        load()
      }
    } catch {
      setErr('Speichern fehlgeschlagen')
    } finally {
      setBusy(false)
    }
  }

  async function del(id: string) {
    setBusy(true)
    setErr('')
    try {
      const r = await fetch(`${API}/control/equipment/${id}`, { method: 'DELETE' })
      if (!r.ok) {
        const d = await r.json().catch(() => ({}))
        setErr(d.detail || `Fehler (${r.status})`)
      } else {
        if (editingId === id) {
          setEditingId(null)
          setForm(EMPTY)
        }
        load()
      }
    } finally {
      setBusy(false)
    }
  }

  async function resetAll() {
    setBusy(true)
    setErr('')
    try {
      await fetch(`${API}/control/equipment/reset`, { method: 'POST' })
      setEditingId(null)
      setForm(EMPTY)
      load()
    } finally {
      setBusy(false)
    }
  }

  if (!open) return null

  const rangeRow = (
    label: string,
    key: 'temperature' | 'pressure' | 'vibration' | 'flow_rate',
  ) => (
    <div className="flex items-center gap-2 mb-1.5">
      <span className="w-20 text-[11px] text-gray-400">{label}</span>
      {(['min', 'max', 'unit'] as const).map((fld) => (
        <input
          key={fld}
          value={form[key][fld]}
          placeholder={fld}
          onChange={(e) =>
            setForm((p) => ({ ...p, [key]: { ...p[key], [fld]: e.target.value } }))
          }
          className="w-20 text-xs px-2 py-1 rounded bg-plant-bg border border-plant-border
                     text-gray-200 focus:outline-none focus:border-plant-accent"
        />
      ))}
    </div>
  )

  return (
    <div
      className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-6"
      onClick={onClose}
    >
      <div
        className="bg-plant-card border border-plant-border rounded-xl w-full max-w-4xl p-5"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-bold text-gray-200 uppercase tracking-wider">
            Equipment verwalten
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-white text-lg leading-none"
            aria-label="Schließen"
          >
            ×
          </button>
        </div>

        <div className="grid grid-cols-[260px_1fr] gap-5">
          {/* List */}
          <div className="border-r border-plant-border pr-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] uppercase tracking-wider text-gray-500">
                Vorhanden ({list.length})
              </span>
              <button
                onClick={() => {
                  setEditingId(null)
                  setForm(EMPTY)
                }}
                className="text-[11px] text-plant-accent hover:underline"
              >
                + Neu
              </button>
            </div>
            <div className="space-y-1 max-h-72 overflow-y-auto">
              {list.map((e) => (
                <div
                  key={e.equipment_id}
                  className={`flex items-center justify-between px-2 py-1.5 rounded text-xs
                    cursor-pointer border ${
                      editingId === e.equipment_id
                        ? 'border-plant-accent bg-plant-accent/10'
                        : 'border-transparent hover:bg-plant-bg'
                    }`}
                  onClick={() => {
                    setEditingId(e.equipment_id)
                    setForm(toForm(e))
                  }}
                >
                  <span className="text-gray-300">
                    {e.equipment_id}
                    <span className="text-gray-600"> · {e.etype}</span>
                  </span>
                  <button
                    onClick={(ev) => {
                      ev.stopPropagation()
                      del(e.equipment_id)
                    }}
                    disabled={busy}
                    className="text-plant-danger/70 hover:text-plant-danger text-[11px]"
                  >
                    löschen
                  </button>
                </div>
              ))}
            </div>
            <button
              onClick={resetAll}
              disabled={busy}
              className="mt-3 w-full text-[11px] px-2 py-1.5 rounded-lg bg-plant-card
                         border border-plant-border text-gray-400 hover:text-white
                         disabled:opacity-40"
            >
              Auf Standard zurücksetzen
            </button>
          </div>

          {/* Form */}
          <div>
            <div className="flex gap-2 mb-2">
              <input
                value={form.equipment_id}
                placeholder="ID (z.B. P-102)"
                disabled={!!editingId}
                onChange={(e) =>
                  setForm((p) => ({ ...p, equipment_id: e.target.value }))
                }
                className="flex-1 text-xs px-2 py-1.5 rounded bg-plant-bg border
                           border-plant-border text-gray-200 disabled:opacity-60
                           focus:outline-none focus:border-plant-accent"
              />
              <input
                value={form.name}
                placeholder="Name"
                onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
                className="flex-1 text-xs px-2 py-1.5 rounded bg-plant-bg border
                           border-plant-border text-gray-200
                           focus:outline-none focus:border-plant-accent"
              />
              <select
                value={form.etype}
                onChange={(e) => setForm((p) => ({ ...p, etype: e.target.value }))}
                className="text-xs px-2 py-1.5 rounded bg-plant-bg border
                           border-plant-border text-gray-200"
              >
                {TYPES.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>

            {rangeRow('Temperatur', 'temperature')}
            {rangeRow('Druck', 'pressure')}
            {rangeRow('Vibration', 'vibration')}

            <label className="flex items-center gap-2 text-[11px] text-gray-400 my-1.5">
              <input
                type="checkbox"
                checked={form.hasFlow}
                onChange={(e) =>
                  setForm((p) => ({ ...p, hasFlow: e.target.checked }))
                }
              />
              Durchfluss (flow_rate)
            </label>
            {form.hasFlow && rangeRow('Flow', 'flow_rate')}

            {err && <p className="text-[11px] text-plant-danger mt-2">{err}</p>}

            <div className="flex gap-2 mt-3">
              <button
                onClick={save}
                disabled={busy || !form.equipment_id.trim()}
                className="px-3 py-1.5 text-xs rounded-lg bg-plant-accent/20
                           border border-plant-accent/40 text-plant-accent
                           hover:bg-plant-accent/30 disabled:opacity-40"
              >
                {editingId ? 'Speichern' : 'Hinzufügen'}
              </button>
              {editingId && (
                <button
                  onClick={() => {
                    setEditingId(null)
                    setForm(EMPTY)
                  }}
                  className="px-3 py-1.5 text-xs rounded-lg bg-plant-card
                             border border-plant-border text-gray-400 hover:text-white"
                >
                  Abbrechen
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
