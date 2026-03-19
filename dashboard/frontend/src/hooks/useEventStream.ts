import { useState, useEffect, useRef, useCallback } from 'react'
import type {
  SensorReading,
  AgentAnalysis,
  RecommendedAction,
  EquipmentStatus,
} from '../types'

const MAX_READINGS = 60
const MAX_ANALYSES = 50
const MAX_ACTIONS = 100

function getBaseUrl(): string {
  // Allow override via env var (set at build time)
  const envUrl = import.meta.env.VITE_API_URL as string | undefined
  if (envUrl) return envUrl

  // In production (served by nginx), use relative /api path
  if (import.meta.env.PROD) return '/api'

  // In dev mode, the Vite proxy handles /api -> localhost:8003
  return '/api'
}

export function useEventStream() {
  const [sensorData, setSensorData] = useState<Map<string, SensorReading[]>>(new Map())
  const [latestReadings, setLatestReadings] = useState<Map<string, SensorReading>>(new Map())
  const [analyses, setAnalyses] = useState<AgentAnalysis[]>([])
  const [actions, setActions] = useState<RecommendedAction[]>([])
  const [equipmentStatus, setEquipmentStatus] = useState<Map<string, EquipmentStatus>>(new Map())
  const [connected, setConnected] = useState(false)
  const eventSourceRef = useRef<EventSource | null>(null)
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const handleSensorReading = useCallback((reading: SensorReading) => {
    setSensorData((prev) => {
      const next = new Map(prev)
      const existing = next.get(reading.equipment_id) || []
      const updated = [...existing, reading].slice(-MAX_READINGS)
      next.set(reading.equipment_id, updated)
      return next
    })

    setLatestReadings((prev) => {
      const next = new Map(prev)
      next.set(reading.equipment_id, reading)
      return next
    })

    setEquipmentStatus((prev) => {
      const next = new Map(prev)
      next.set(reading.equipment_id, reading.status)
      return next
    })
  }, [])

  const handleAgentAnalysis = useCallback((analysis: AgentAnalysis) => {
    setAnalyses((prev) => [analysis, ...prev].slice(0, MAX_ANALYSES))

    if (analysis.actions && analysis.actions.length > 0) {
      setActions((prev) => [...analysis.actions, ...prev].slice(0, MAX_ACTIONS))
    }

    // Update equipment status from anomalies
    if (analysis.anomalies && analysis.anomalies.length > 0) {
      setEquipmentStatus((prev) => {
        const next = new Map(prev)
        for (const anomaly of analysis.anomalies) {
          const currentStatus = next.get(anomaly.equipment_id)
          const newStatus = anomaly.severity === 'critical' ? 'critical' : 'warning'
          if (currentStatus !== 'critical' || newStatus === 'critical') {
            next.set(anomaly.equipment_id, newStatus)
          }
        }
        return next
      })
    }
  }, [])

  const handleActionExecuted = useCallback((action: RecommendedAction) => {
    setActions((prev) => [action, ...prev].slice(0, MAX_ACTIONS))
  }, [])

  const connect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
    }

    const baseUrl = getBaseUrl()
    const url = `${baseUrl}/events/stream`
    const es = new EventSource(url)
    eventSourceRef.current = es

    es.onopen = () => {
      setConnected(true)
    }

    es.onerror = () => {
      setConnected(false)
      es.close()
      eventSourceRef.current = null
      // Reconnect after delay
      reconnectTimeoutRef.current = setTimeout(() => {
        connect()
      }, 3000)
    }

    // Listen on generic message event
    es.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data)
        const eventType = parsed.event_type || parsed.type

        if (eventType === 'sensor_reading') {
          handleSensorReading(parsed.data || parsed)
        } else if (eventType === 'agent_analysis') {
          handleAgentAnalysis(parsed.data || parsed)
        } else if (eventType === 'action_executed') {
          handleActionExecuted(parsed.data || parsed)
        }
      } catch {
        // Ignore malformed events
      }
    }

    // Also listen on named event types
    es.addEventListener('sensor_reading', (event) => {
      try {
        const envelope = JSON.parse((event as MessageEvent).data)
        handleSensorReading(envelope.data || envelope)
      } catch {
        // Ignore
      }
    })

    es.addEventListener('agent_analysis', (event) => {
      try {
        const envelope = JSON.parse((event as MessageEvent).data)
        handleAgentAnalysis(envelope.data || envelope)
      } catch {
        // Ignore
      }
    })

    es.addEventListener('action_executed', (event) => {
      try {
        const envelope = JSON.parse((event as MessageEvent).data)
        handleActionExecuted(envelope.data || envelope)
      } catch {
        // Ignore
      }
    })
  }, [handleSensorReading, handleAgentAnalysis, handleActionExecuted])

  useEffect(() => {
    connect()

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
    }
  }, [connect])

  return {
    sensorData,
    latestReadings,
    analyses,
    actions,
    equipmentStatus,
    connected,
  }
}
