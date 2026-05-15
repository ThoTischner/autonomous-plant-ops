import type { RecommendedAction } from '../types'

interface Props {
  actions: RecommendedAction[]
}

function urgencyBadge(urgency: string): string {
  switch (urgency?.toLowerCase()) {
    case 'critical':
    case 'high':
      return 'bg-plant-danger/20 text-plant-danger border-plant-danger/30'
    case 'medium':
    case 'warning':
      return 'bg-plant-warning/20 text-plant-warning border-plant-warning/30'
    default:
      return 'bg-plant-accent/20 text-plant-accent border-plant-accent/30'
  }
}

function equipmentTagColor(equipmentId: string): string {
  const hash = equipmentId.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0)
  const colors = [
    'bg-blue-500/20 text-blue-400',
    'bg-orange-500/20 text-orange-400',
    'bg-emerald-500/20 text-emerald-400',
    'bg-purple-500/20 text-purple-400',
    'bg-pink-500/20 text-pink-400',
  ]
  return colors[hash % colors.length]
}

function formatTime(ts?: string): string {
  if (!ts) return '—'
  try {
    return new Date(ts).toLocaleTimeString('de-DE', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  } catch {
    return ts
  }
}

export default function ActionLog({ actions }: Props) {
  return (
    <div className="h-full flex flex-col py-2 px-4">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-sm font-bold text-gray-300 uppercase tracking-wider">
          Action Log
        </h2>
        <span className="text-[10px] text-gray-600">{actions.length} actions</span>
      </div>

      <div className="flex-1 overflow-y-auto">
        {actions.length === 0 ? (
          <div className="flex items-center justify-center w-full h-full text-sm text-gray-600">
            No actions yet...
          </div>
        ) : (
          <table className="w-full text-left border-collapse">
            <thead className="sticky top-0 bg-plant-bg z-10">
              <tr className="text-[10px] uppercase tracking-wider text-gray-500">
                <th className="px-3 py-1.5 font-medium w-[90px]">Zeit</th>
                <th className="px-3 py-1.5 font-medium w-[90px]">Equipment</th>
                <th className="px-3 py-1.5 font-medium w-[170px]">Aktion</th>
                <th className="px-3 py-1.5 font-medium w-[100px]">Dringlichkeit</th>
                <th className="px-3 py-1.5 font-medium">Grund</th>
              </tr>
            </thead>
            <tbody>
              {actions.map((action, idx) => (
                <tr
                  key={`${action.equipment_id}-${action.action}-${idx}`}
                  className="border-t border-plant-border/60 hover:bg-plant-card/60"
                >
                  <td className="px-3 py-1.5 text-[11px] font-mono text-gray-500 whitespace-nowrap">
                    {formatTime(action.timestamp)}
                  </td>
                  <td className="px-3 py-1.5">
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${equipmentTagColor(action.equipment_id)}`}
                    >
                      {action.equipment_id}
                    </span>
                  </td>
                  <td className="px-3 py-1.5 text-xs font-semibold text-gray-200">
                    {action.action}
                  </td>
                  <td className="px-3 py-1.5">
                    {action.urgency && (
                      <span
                        className={`text-[9px] font-bold px-1.5 py-0.5 rounded border ${urgencyBadge(action.urgency)}`}
                      >
                        {action.urgency.toUpperCase()}
                      </span>
                    )}
                  </td>
                  <td className="px-3 py-1.5 text-[11px] text-gray-500">
                    {action.reason || action.message || '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
