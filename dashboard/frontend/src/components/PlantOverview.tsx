import { useState, useEffect } from 'react'
import type { EquipmentStatus } from '../types'

interface Props {
  equipmentStatus: Map<string, EquipmentStatus>
  connected: boolean
}

function getOverallStatus(equipmentStatus: Map<string, EquipmentStatus>): EquipmentStatus {
  let worst: EquipmentStatus = 'normal'
  for (const status of equipmentStatus.values()) {
    if (status === 'critical' || status === 'shutdown') return 'critical'
    if (status === 'warning') worst = 'warning'
  }
  return worst
}

function statusColor(status: EquipmentStatus): string {
  switch (status) {
    case 'normal': return 'bg-plant-success'
    case 'warning': return 'bg-plant-warning'
    case 'critical': return 'bg-plant-danger'
    case 'shutdown': return 'bg-gray-500'
  }
}

function statusPulse(status: EquipmentStatus): string {
  switch (status) {
    case 'normal': return 'pulse-normal'
    case 'warning': return 'pulse-warning'
    case 'critical': return 'pulse-critical'
    case 'shutdown': return ''
  }
}

export default function PlantOverview({ equipmentStatus, connected }: Props) {
  const [time, setTime] = useState(new Date())

  useEffect(() => {
    const interval = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(interval)
  }, [])

  const overall = getOverallStatus(equipmentStatus)
  const equipmentCount = equipmentStatus.size

  return (
    <header className="bg-plant-card border-b border-plant-border px-6 py-3 flex items-center justify-between">
      {/* Left: Title + status */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-3">
          <div className="text-2xl font-bold tracking-tight">
            <span className="text-plant-accent">Autonomous</span>{' '}
            <span className="text-white">Plant Ops</span>
          </div>
          <div className="text-xs text-gray-500 uppercase tracking-widest mt-1">
            AI Monitoring
          </div>
        </div>

        <div className="h-8 w-px bg-plant-border mx-2" />

        {/* Overall status indicator */}
        <div className="flex items-center gap-2">
          <div
            className={`w-3 h-3 rounded-full ${statusColor(overall)} ${statusPulse(overall)}`}
          />
          <span className="text-sm text-gray-300 capitalize">{overall}</span>
          {equipmentCount > 0 && (
            <span className="text-xs text-gray-500">
              ({equipmentCount} units)
            </span>
          )}
        </div>
      </div>

      {/* Right: Time + connection */}
      <div className="flex items-center gap-4">
        <div className="text-sm text-gray-400 font-mono">
          {time.toLocaleTimeString('de-DE', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
          })}
        </div>
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              connected ? 'bg-plant-success' : 'bg-plant-danger'
            }`}
          />
          <span className="text-xs text-gray-500">
            {connected ? 'LIVE' : 'DISCONNECTED'}
          </span>
        </div>
      </div>
    </header>
  )
}
