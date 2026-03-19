import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'
import type { SensorReading } from '../types'

interface Props {
  title: string
  dataKey: keyof SensorReading
  data: Map<string, SensorReading[]>
  unit: string
  normalRange?: { min: number; max: number }
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

export default function SensorChart({ title, dataKey, data, unit, normalRange }: Props) {
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
    <div className="bg-plant-card border border-plant-border rounded-lg p-4 h-full">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold text-gray-300">{title}</h3>
        <span className="text-[10px] text-gray-600 font-mono">{unit}</span>
      </div>
      <div className="h-[calc(100%-28px)]">
        {chartData.length === 0 ? (
          <div className="flex items-center justify-center h-full text-sm text-gray-600">
            Waiting for data...
          </div>
        ) : (
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 5, right: 5, left: -10, bottom: 0 }}>
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
            {normalRange && (
              <>
                <ReferenceLine
                  y={normalRange.min}
                  stroke="#10b981"
                  strokeDasharray="6 4"
                  strokeOpacity={0.5}
                  label={{
                    value: `min ${normalRange.min}`,
                    position: 'left',
                    fill: '#10b981',
                    fontSize: 9,
                  }}
                />
                <ReferenceLine
                  y={normalRange.max}
                  stroke="#10b981"
                  strokeDasharray="6 4"
                  strokeOpacity={0.5}
                  label={{
                    value: `max ${normalRange.max}`,
                    position: 'left',
                    fill: '#10b981',
                    fontSize: 9,
                  }}
                />
              </>
            )}
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
                />
              )
            })}
          </AreaChart>
        </ResponsiveContainer>
        )}
      </div>
    </div>
  )
}
