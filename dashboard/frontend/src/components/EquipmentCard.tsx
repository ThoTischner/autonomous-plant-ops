import { motion } from 'framer-motion'
import type { SensorReading, EquipmentStatus } from '../types'

interface Props {
  equipmentId: string
  name: string
  status: EquipmentStatus
  reading?: SensorReading
}

function statusColor(status: EquipmentStatus): string {
  switch (status) {
    case 'normal': return 'border-plant-success'
    case 'warning': return 'border-plant-warning'
    case 'critical': return 'border-plant-danger'
    case 'shutdown': return 'border-gray-600'
  }
}

function statusBg(status: EquipmentStatus): string {
  switch (status) {
    case 'normal': return 'bg-emerald-500/10'
    case 'warning': return 'bg-amber-500/10'
    case 'critical': return 'bg-red-500/10'
    case 'shutdown': return 'bg-gray-500/10'
  }
}

function statusBadgeColor(status: EquipmentStatus): string {
  switch (status) {
    case 'normal': return 'bg-plant-success/20 text-plant-success'
    case 'warning': return 'bg-plant-warning/20 text-plant-warning'
    case 'critical': return 'bg-plant-danger/20 text-plant-danger'
    case 'shutdown': return 'bg-gray-500/20 text-gray-400'
  }
}

function glowShadow(status: EquipmentStatus): string {
  switch (status) {
    case 'normal': return '0 0 12px rgba(16, 185, 129, 0.15)'
    case 'warning': return '0 0 12px rgba(245, 158, 11, 0.2)'
    case 'critical': return '0 0 16px rgba(239, 68, 68, 0.25)'
    case 'shutdown': return 'none'
  }
}

function getEquipmentType(id: string): 'pump' | 'reactor' | 'compressor' {
  if (id.startsWith('P-')) return 'pump'
  if (id.startsWith('R-')) return 'reactor'
  return 'compressor'
}

function EquipmentIcon({ type, status }: { type: string; status: EquipmentStatus }) {
  const color =
    status === 'normal' ? '#10b981' :
    status === 'warning' ? '#f59e0b' :
    status === 'critical' ? '#ef4444' : '#6b7280'

  if (type === 'pump') {
    return (
      <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
        <motion.circle
          cx="18" cy="18" r="12"
          stroke={color} strokeWidth="2" fill="none"
          animate={{ rotate: 360 }}
          transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
          style={{ transformOrigin: '18px 18px' }}
        />
        <motion.path
          d="M18 6 L18 12 M18 24 L18 30 M6 18 L12 18 M24 18 L30 18"
          stroke={color} strokeWidth="1.5" strokeLinecap="round"
          animate={{ rotate: 360 }}
          transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
          style={{ transformOrigin: '18px 18px' }}
        />
        <circle cx="18" cy="18" r="3" fill={color} opacity={0.6} />
      </svg>
    )
  }

  if (type === 'reactor') {
    return (
      <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
        <circle cx="18" cy="18" r="13" stroke={color} strokeWidth="2" fill="none" />
        <circle cx="18" cy="18" r="8" stroke={color} strokeWidth="1" fill="none" opacity={0.4} />
        <motion.circle
          cx="14" cy="14" r="2" fill={color} opacity={0.5}
          animate={{ cy: [14, 10, 14], opacity: [0.5, 0.8, 0.5] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.circle
          cx="22" cy="16" r="1.5" fill={color} opacity={0.4}
          animate={{ cy: [16, 11, 16], opacity: [0.4, 0.7, 0.4] }}
          transition={{ duration: 2.5, repeat: Infinity, ease: 'easeInOut', delay: 0.5 }}
        />
        <motion.circle
          cx="18" cy="20" r="1.8" fill={color} opacity={0.3}
          animate={{ cy: [20, 13, 20], opacity: [0.3, 0.6, 0.3] }}
          transition={{ duration: 1.8, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
        />
      </svg>
    )
  }

  // Compressor
  return (
    <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
      <motion.rect
        x="8" y="10" width="20" height="16" rx="3"
        stroke={color} strokeWidth="2" fill="none"
        animate={{ scale: [1, 1.04, 1] }}
        transition={{ duration: 1.2, repeat: Infinity, ease: 'easeInOut' }}
        style={{ transformOrigin: '18px 18px' }}
      />
      <motion.line
        x1="13" y1="14" x2="13" y2="22"
        stroke={color} strokeWidth="1.5" strokeLinecap="round"
        animate={{ x1: [13, 14, 13], x2: [13, 14, 13] }}
        transition={{ duration: 1.2, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.line
        x1="18" y1="14" x2="18" y2="22"
        stroke={color} strokeWidth="1.5" strokeLinecap="round"
        animate={{ x1: [18, 19, 18], x2: [18, 19, 18] }}
        transition={{ duration: 1.2, repeat: Infinity, ease: 'easeInOut', delay: 0.2 }}
      />
      <motion.line
        x1="23" y1="14" x2="23" y2="22"
        stroke={color} strokeWidth="1.5" strokeLinecap="round"
        animate={{ x1: [23, 24, 23], x2: [23, 24, 23] }}
        transition={{ duration: 1.2, repeat: Infinity, ease: 'easeInOut', delay: 0.4 }}
      />
    </svg>
  )
}

export default function EquipmentCard({ equipmentId, name, status, reading }: Props) {
  const type = getEquipmentType(equipmentId)

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className={`mx-3 mb-2 p-3 rounded-lg border ${statusColor(status)} ${statusBg(status)} bg-plant-card`}
      style={{ boxShadow: glowShadow(status) }}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <EquipmentIcon type={type} status={status} />
          <div>
            <div className="text-sm font-semibold text-white truncate max-w-[140px]">
              {name || equipmentId}
            </div>
            <div className="text-[10px] text-gray-500 font-mono">{equipmentId}</div>
          </div>
        </div>
        <span
          className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${statusBadgeColor(status)}`}
        >
          {status}
        </span>
      </div>

      {reading && (
        <div className="grid grid-cols-3 gap-1 mt-1">
          <SensorValue label="TEMP" value={reading.temperature} unit="C" />
          <SensorValue label="PRESS" value={reading.pressure} unit="bar" />
          <SensorValue label="VIB" value={reading.vibration} unit="mm/s" />
        </div>
      )}
    </motion.div>
  )
}

function SensorValue({ label, value, unit }: { label: string; value?: number; unit: string }) {
  return (
    <div className="text-center">
      <div className="text-[9px] text-gray-500 uppercase">{label}</div>
      <div className="text-xs font-mono text-gray-300">
        {value != null ? value.toFixed(1) : '--'}
        <span className="text-[9px] text-gray-600 ml-0.5">{unit}</span>
      </div>
    </div>
  )
}
