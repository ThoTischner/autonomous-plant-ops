import { Component, type ReactNode } from 'react'
import { useEventStream } from './hooks/useEventStream'
import PlantOverview from './components/PlantOverview'
import EquipmentPanel from './components/EquipmentPanel'
import SensorCharts from './components/SensorCharts'
import AgentFeed from './components/AgentFeed'
import ActionLog from './components/ActionLog'

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
    <div className="h-screen w-screen overflow-hidden grid grid-cols-[280px_1fr_320px] grid-rows-[auto_1fr_200px] gap-0">
      {/* Header — full width */}
      <div className="col-span-3">
        <PlantOverview
          equipmentStatus={equipmentStatus}
          connected={connected}
        />
      </div>

      {/* Left sidebar — equipment panel */}
      <div className="overflow-y-auto border-r border-plant-border">
        <EquipmentPanel
          latestReadings={latestReadings}
          equipmentStatus={equipmentStatus}
        />
      </div>

      {/* Center — sensor charts */}
      <div className="overflow-y-auto p-4">
        <SensorCharts sensorData={sensorData} />
      </div>

      {/* Right sidebar — agent feed */}
      <div className="overflow-y-auto border-l border-plant-border">
        <AgentFeed analyses={analyses} />
      </div>

      {/* Bottom bar — action log, full width */}
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
