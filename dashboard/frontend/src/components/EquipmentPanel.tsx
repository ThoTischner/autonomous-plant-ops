import type { SensorReading, EquipmentStatus } from '../types'
import EquipmentCard from './EquipmentCard'

interface Props {
  latestReadings: Map<string, SensorReading>
  equipmentStatus: Map<string, EquipmentStatus>
}

export default function EquipmentPanel({ latestReadings, equipmentStatus }: Props) {
  // Collect all known equipment from both maps
  const allIds = new Set([...latestReadings.keys(), ...equipmentStatus.keys()])
  const equipmentList = Array.from(allIds).sort()

  return (
    <div className="py-3">
      <div className="px-4 mb-3 flex items-center justify-between">
        <h2 className="text-sm font-bold text-gray-300 uppercase tracking-wider">
          Equipment
        </h2>
        <span className="text-[10px] text-gray-600">
          {equipmentList.length} units
        </span>
      </div>
      {equipmentList.length === 0 ? (
        <div className="px-4 py-8 text-center text-sm text-gray-600">
          Waiting for data...
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
            />
          )
        })
      )}
    </div>
  )
}
