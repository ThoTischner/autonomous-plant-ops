import { Component, type ReactNode } from 'react'
import { useEventStream } from './hooks/useEventStream'
import PlantOverview from './components/PlantOverview'
import EquipmentPanel from './components/EquipmentPanel'
import SensorCharts from './components/SensorCharts'
import AgentFeed from './components/AgentFeed'
import ActionLog from './components/ActionLog'
import ControlBar from './components/ControlBar'

class ErrorBoundary extends Component<
  { children: ReactNode },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: { children: ReactNode }) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="h-screen w-screen flex items-center justify-center bg-plant-bg text-white">
          <div className="text-center p-8">
            <h1 className="text-2xl font-bold text-plant-danger mb-4">Dashboard Error</h1>
            <p className="text-gray-400 mb-4">Something went wrong rendering the dashboard.</p>
            <pre className="text-xs text-gray-500 bg-plant-card p-4 rounded-lg max-w-lg overflow-auto">
              {this.state.error?.message}
            </pre>
            <button
              className="mt-4 px-4 py-2 bg-plant-accent text-white rounded-lg text-sm"
              onClick={() => this.setState({ hasError: false, error: null })}
            >
              Try Again
            </button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}

function App() {
  const {
    sensorData,
    latestReadings,
    analyses,
    actions,
    equipmentStatus,
    connected,
  } = useEventStream()

  return (
    <div className="h-screen w-screen overflow-hidden grid grid-cols-[260px_1fr_440px] grid-rows-[auto_auto_1fr_220px] gap-0">
      {/* Row 1 — status header, full width */}
      <div className="col-span-3">
        <PlantOverview
          equipmentStatus={equipmentStatus}
          connected={connected}
        />
      </div>

      {/* Row 2 — control + system prompt toolbar, full width */}
      <div className="col-span-3 bg-plant-card border-b border-plant-border px-6 py-2">
        <ControlBar />
      </div>

      {/* Row 3 — left: equipment */}
      <div className="overflow-y-auto border-r border-plant-border">
        <EquipmentPanel
          latestReadings={latestReadings}
          equipmentStatus={equipmentStatus}
        />
      </div>

      {/* Row 3 — center: sensor charts */}
      <div className="overflow-y-auto p-4">
        <SensorCharts sensorData={sensorData} />
      </div>

      {/* Row 3 — right: AI agent feed (primary focus) */}
      <div className="overflow-y-auto border-l-2 border-plant-accent/40 bg-plant-accent/[0.03]">
        <AgentFeed analyses={analyses} />
      </div>

      {/* Row 4 — action log table, full width */}
      <div className="col-span-3 border-t border-plant-border overflow-hidden">
        <ActionLog actions={actions} />
      </div>
    </div>
  )
}

function AppWithErrorBoundary() {
  return (
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  )
}

export default AppWithErrorBoundary
