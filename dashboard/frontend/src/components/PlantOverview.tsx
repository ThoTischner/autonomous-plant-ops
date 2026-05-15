import { useState, useEffect } from 'react'
import type { EquipmentStatus } from '../types'

// The plant-wide rollup has its own states: a shut-down (but otherwise
// healthy) fleet is "degraded", NOT critical. Warning/critical only when
// equipment is actually in warning/critical.
type OverallStatus = 'normal' | 'degraded' | 'warning' | 'critical'

const OVERALL_DE: Record<OverallStatus, string> = {
  normal: 'Alles normal',
  degraded: 'Eingeschränkt',
  warning: 'Warnung',
  critical: 'Kritisch',
}

interface Props {
  equipmentStatus: Map<string, EquipmentStatus>
  connected: boolean
}

function getOverallStatus(equipmentStatus: Map<string, EquipmentStatus>): OverallStatus {
  let hasWarning = false
  let hasShutdown = false
  for (const status of equipmentStatus.values()) {
    if (status === 'critical') return 'critical'
    if (status === 'warning') hasWarning = true
    if (status === 'shutdown') hasShutdown = true
  }
  if (hasWarning) return 'warning'
  if (hasShutdown) return 'degraded'
  return 'normal'
}

function statusColor(status: OverallStatus): string {
  switch (status) {
    case 'normal': return 'bg-plant-success'
    case 'degraded': return 'bg-orange-500'
    case 'warning': return 'bg-plant-warning'
    case 'critical': return 'bg-plant-danger'
  }
}

function statusPulse(status: OverallStatus): string {
  switch (status) {
    case 'normal': return 'pulse-normal'
    case 'degraded': return ''
    case 'warning': return 'pulse-warning'
    case 'critical': return 'pulse-critical'
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
            KI-Überwachung
          </div>
        </div>

        <div className="h-8 w-px bg-plant-border mx-2" />

        {/* Overall status indicator */}
        <div className="flex items-center gap-2">
          <div
            className={`w-3 h-3 rounded-full ${statusColor(overall)} ${statusPulse(overall)}`}
          />
          <span className="text-sm text-gray-300">{OVERALL_DE[overall]}</span>
          {equipmentCount > 0 && (
            <span className="text-xs text-gray-500">
              ({equipmentCount} Anlagen)
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
            {connected ? 'LIVE' : 'GETRENNT'}
          </span>
        </div>
      </div>
    </header>
  )
}
