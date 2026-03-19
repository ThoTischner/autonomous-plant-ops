export type EquipmentStatus = 'normal' | 'warning' | 'critical' | 'shutdown'

export interface SensorReading {
  equipment_id: string
  equipment_name: string
  timestamp: string
  temperature: number
  pressure: number
  vibration: number
  flow_rate?: number
  status: EquipmentStatus
}

export interface Anomaly {
  equipment_id: string
  sensor: string
  value: number
  normal_range: string
  severity: string
}

export interface RecommendedAction {
  equipment_id: string
  action: string
  reason: string
  urgency: string
  parameters?: Record<string, unknown>
}

export interface AgentAnalysis {
  anomalies: Anomaly[]
  reasoning: string
  actions: RecommendedAction[]
  timestamp: string
}

export interface PlantEvent {
  id: string
  event_type: string
  timestamp: string
  data: unknown
  equipment_id?: string
  severity?: string
}
