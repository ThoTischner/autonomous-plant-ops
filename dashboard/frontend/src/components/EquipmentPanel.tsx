import { useEffect, useState } from 'react'
import type { SensorReading, EquipmentStatus, EquipmentDef } from '../types'
import EquipmentCard from './EquipmentCard'

interface Props {
  latestReadings: Map<string, SensorReading>
  equipmentStatus: Map<string, EquipmentStatus>
}

const API = '/api'

export default function EquipmentPanel({ latestReadings, equipmentStatus }: Props) {
  // Equipment definitions hold the "good" ranges per sensor. They can change
  // at runtime (added/edited via the UI), so poll periodically.
  const [defs, setDefs] = useState<Map<string, EquipmentDef>>(new Map())

  useEffect(() => {
    let active = true
    const load = async () => {
      try {
        const r = await fetch(`${API}/control/equipment`)
        if (!r.ok) return
        const list: EquipmentDef[] = await r.json()
        if (!active) return
        setDefs(new Map(list.map((e) => [e.equipment_id, e])))
      } catch {
        // keep last known defs on transient failure
      }
    }
    load()
    const t = setInterval(load, 15000)
    return () => {
      active = false
      clearInterval(t)
    }
  }, [])

  // Collect all known equipment from both maps
  const allIds = new Set([...latestReadings.keys(), ...equipmentStatus.keys()])
  const equipmentList = Array.from(allIds).sort()

  return (
    <div className="py-3">
      <div className="px-4 mb-3 flex items-center justify-between">
        <h2 className="text-sm font-bold text-gray-300 uppercase tracking-wider">
          Anlagen
        </h2>
        <span className="text-[10px] text-gray-600">
          {equipmentList.length} Anlagen
        </span>
      </div>
      {equipmentList.length === 0 ? (
        <div className="px-4 py-8 text-center text-sm text-gray-600">
          Warte auf Daten …
        </div>
      ) : (
        equipmentList.map((id) => {
          const reading = latestReadings.get(id)
          const status = equipmentStatus.get(id) || 'normal'
          return (
            <EquipmentCard
              key={id}
              equipmentId={id}
              name={reading?.equipment_name || id}
              status={status}
              reading={reading}
              def={defs.get(id)}
            />
          )
        })
      )}
    </div>
  )
}
