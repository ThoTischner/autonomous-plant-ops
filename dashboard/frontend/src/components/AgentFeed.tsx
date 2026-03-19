import { motion, AnimatePresence } from 'framer-motion'
import type { AgentAnalysis } from '../types'

interface Props {
  analyses: AgentAnalysis[]
}

function severityDotColor(analysis: AgentAnalysis): string {
  if (!analysis.anomalies || analysis.anomalies.length === 0) return 'bg-plant-success'
  const hasCritical = analysis.anomalies.some((a) => a.severity === 'critical')
  if (hasCritical) return 'bg-plant-danger'
  return 'bg-plant-warning'
}

function formatTimestamp(ts: string): string {
  try {
    const d = new Date(ts)
    return d.toLocaleTimeString('de-DE', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  } catch {
    return ts
  }
}

export default function AgentFeed({ analyses }: Props) {
  return (
    <div className="py-3 h-full flex flex-col">
      <div className="px-4 mb-3 flex items-center gap-2">
        <div className="w-2 h-2 rounded-full bg-plant-accent animate-pulse" />
        <h2 className="text-sm font-bold text-gray-300 uppercase tracking-wider">
          AI Agent Feed
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto px-3 space-y-2">
        {analyses.length === 0 ? (
          <div className="px-2 py-8 text-center text-sm text-gray-600">
            Waiting for AI analysis...
          </div>
        ) : (
          <AnimatePresence initial={false}>
            {analyses.map((analysis, idx) => (
              <motion.div
                key={`${analysis.timestamp}-${idx}`}
                initial={{ opacity: 0, x: 30 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 30 }}
                transition={{ duration: 0.3 }}
                className="bg-plant-card border border-plant-border rounded-lg p-3"
              >
                <div className="flex items-center gap-2 mb-1.5">
                  <div className={`w-2 h-2 rounded-full flex-shrink-0 ${severityDotColor(analysis)}`} />
                  <span className="text-[10px] text-gray-500 font-mono">
                    {formatTimestamp(analysis.timestamp)}
                  </span>
                </div>

                {analysis.reasoning && (
                  <p className="text-xs text-gray-300 leading-relaxed mb-2">
                    {analysis.reasoning}
                  </p>
                )}

                {analysis.anomalies && analysis.anomalies.length > 0 && (
                  <div className="space-y-1">
                    {analysis.anomalies.map((anomaly, aIdx) => (
                      <div
                        key={aIdx}
                        className="flex items-center gap-2 text-[10px] bg-plant-bg/50 rounded px-2 py-1"
                      >
                        <span
                          className={`font-bold ${
                            anomaly.severity === 'critical'
                              ? 'text-plant-danger'
                              : 'text-plant-warning'
                          }`}
                        >
                          {anomaly.severity?.toUpperCase()}
                        </span>
                        <span className="text-gray-400">{anomaly.equipment_id}</span>
                        <span className="text-gray-500">
                          {anomaly.sensor}: {anomaly.value?.toFixed(1)}
                        </span>
                        {anomaly.normal_range && (
                          <span className="text-gray-600">
                            (norm: {anomaly.normal_range})
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {analysis.actions && analysis.actions.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-plant-border">
                    {analysis.actions.map((action, aIdx) => (
                      <div key={aIdx} className="flex items-start gap-1.5 text-[10px]">
                        <span className="text-plant-accent font-semibold mt-px">ACTION</span>
                        <span className="text-gray-400">
                          {action.action} — {action.reason}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
        )}
      </div>
    </div>
  )
}
