import { useEffect, useRef, useState } from 'react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts'
import type { SensorReading } from '../types'

/** Tracks an element's pixel size so the chart never renders at size 0
 *  (which makes Recharts emit "<line>/<circle> attribute … undefined"). */
function useMeasuredSize() {
  const ref = useRef<HTMLDivElement>(null)
  const [size, setSize] = useState({ w: 0, h: 0 })
  useEffect(() => {
    const el = ref.current
    if (!el) return
    let raf = 0
    const ro = new ResizeObserver((entries) => {
      const r = entries[0]?.contentRect
      if (!r) return
      // Collapse rapid resize/animation callbacks to one post-layout value.
      cancelAnimationFrame(raf)
      raf = requestAnimationFrame(() => {
        const w = Math.floor(r.width)
        const h = Math.floor(r.height)
        // Below this Recharts emits undefined axis coords mid-layout.
        setSize(w >= 60 && h >= 60 ? { w, h } : { w: 0, h: 0 })
      })
    })
    ro.observe(el)
    return () => {
      cancelAnimationFrame(raf)
      ro.disconnect()
    }
  }, [])
  return { ref, size }
}

interface Props {
  title: string
  dataKey: keyof SensorReading
  data: Map<string, SensorReading[]>
  unit: string
}

const EQUIPMENT_COLORS = [
  { stroke: '#3b82f6', fill: 'url(#gradient-blue)' },
  { stroke: '#f97316', fill: 'url(#gradient-orange)' },
  { stroke: '#10b981', fill: 'url(#gradient-green)' },
  { stroke: '#a855f7', fill: 'url(#gradient-purple)' },
  { stroke: '#ec4899', fill: 'url(#gradient-pink)' },
]

interface ChartDataPoint {
  time: string
  [key: string]: string | number | undefined
}

export default function SensorChart({ title, dataKey, data, unit }: Props) {
  const { ref: boxRef, size } = useMeasuredSize()
  const equipmentIds = Array.from(data.keys()).sort()

  // Build unified timeline data
  const chartData: ChartDataPoint[] = []
  const maxLen = Math.max(0, ...Array.from(data.values()).map((v) => v.length))

  for (let i = 0; i < maxLen; i++) {
    const point: ChartDataPoint = { time: '' }
    for (const eqId of equipmentIds) {
      const readings = data.get(eqId)
      if (readings && readings[i]) {
        const val = readings[i][dataKey]
        if (typeof val === 'number') {
          point[eqId] = val
        }
        if (!point.time && readings[i].timestamp) {
          const ts = new Date(readings[i].timestamp)
          point.time = ts.toLocaleTimeString('de-DE', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
          })
        }
      }
    }
    if (point.time) {
      chartData.push(point)
    }
  }

  return (
    <div className="bg-plant-card border border-plant-border rounded-lg p-4 h-full flex flex-col">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold text-gray-300">{title}</h3>
        <span className="text-[10px] text-gray-600 font-mono">{unit}</span>
      </div>
      {equipmentIds.length > 0 && (
        <div className="flex flex-wrap gap-x-3 gap-y-1 mb-2">
          {equipmentIds.map((eqId, idx) => (
            <span key={eqId} className="flex items-center gap-1.5 text-[10px] text-gray-400">
              <span
                className="inline-block w-3 h-[3px] rounded-full"
                style={{ backgroundColor: EQUIPMENT_COLORS[idx % EQUIPMENT_COLORS.length].stroke }}
              />
              {eqId}
            </span>
          ))}
        </div>
      )}
      <div ref={boxRef} className="flex-1 min-h-0">
        {chartData.length < 2 || size.w === 0 || size.h === 0 ? (
          <div className="flex items-center justify-center h-full text-sm text-gray-600">
            Warte auf Daten …
          </div>
        ) : (
          <AreaChart
            width={size.w}
            height={size.h}
            data={chartData}
            margin={{ top: 5, right: 5, left: -10, bottom: 0 }}
          >
            <defs>
              <linearGradient id="gradient-blue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gradient-orange" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#f97316" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#f97316" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gradient-green" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#10b981" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#10b981" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gradient-purple" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#a855f7" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#a855f7" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gradient-pink" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#ec4899" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#ec4899" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis
              dataKey="time"
              tick={{ fill: '#6b7280', fontSize: 10 }}
              axisLine={{ stroke: '#1e293b' }}
              tickLine={{ stroke: '#1e293b' }}
              interval="preserveStartEnd"
            />
            <YAxis
              tick={{ fill: '#6b7280', fontSize: 10 }}
              axisLine={{ stroke: '#1e293b' }}
              tickLine={{ stroke: '#1e293b' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#111827',
                border: '1px solid #1e293b',
                borderRadius: '8px',
                fontSize: '12px',
                color: '#e5e7eb',
              }}
              labelStyle={{ color: '#9ca3af' }}
            />
            {equipmentIds.map((eqId, idx) => {
              const colorSet = EQUIPMENT_COLORS[idx % EQUIPMENT_COLORS.length]
              return (
                <Area
                  key={eqId}
                  type="monotone"
                  dataKey={eqId}
                  stroke={colorSet.stroke}
                  fill={colorSet.fill}
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 3, stroke: colorSet.stroke }}
                  name={eqId}
                  isAnimationActive={false}
                />
              )
            })}
          </AreaChart>
        )}
      </div>
    </div>
  )
}
