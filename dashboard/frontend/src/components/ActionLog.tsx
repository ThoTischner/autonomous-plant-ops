import { motion, AnimatePresence } from 'framer-motion'
import type { RecommendedAction } from '../types'

interface Props {
  actions: RecommendedAction[]
}

function urgencyColor(urgency: string): string {
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
  // Assign colors based on hash of equipment ID
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

export default function ActionLog({ actions }: Props) {
  return (
    <div className="h-full flex flex-col py-2 px-4">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-sm font-bold text-gray-300 uppercase tracking-wider">
          Action Log
        </h2>
        <span className="text-[10px] text-gray-600">
          {actions.length} actions
        </span>
      </div>

      <div className="flex-1 overflow-x-auto overflow-y-hidden">
        <div className="flex gap-2 h-full items-start pb-2">
          {actions.length === 0 ? (
            <div className="flex items-center justify-center w-full h-full text-sm text-gray-600">
              No actions yet...
            </div>
          ) : (
            <AnimatePresence initial={false}>
              {actions.map((action, idx) => (
                <motion.div
                  key={`${action.equipment_id}-${action.action}-${idx}`}
                  initial={{ opacity: 0, scale: 0.8, y: 20 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  transition={{ duration: 0.3 }}
                  className="flex-shrink-0 w-[260px] bg-plant-card border border-plant-border rounded-lg p-3"
                >
                  <div className="flex items-center gap-2 mb-1.5">
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${equipmentTagColor(action.equipment_id)}`}
                    >
                      {action.equipment_id}
                    </span>
                    {action.urgency && (
                      <span
                        className={`text-[9px] font-bold px-1.5 py-0.5 rounded border ${urgencyColor(action.urgency)}`}
                      >
                        {action.urgency.toUpperCase()}
                      </span>
                    )}
                  </div>
                  <div className="text-xs font-semibold text-gray-200 mb-1 truncate">
                    {action.action}
                  </div>
                  <div className="text-[10px] text-gray-500 line-clamp-2">
                    {action.reason}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          )}
        </div>
      </div>
    </div>
  )
}
