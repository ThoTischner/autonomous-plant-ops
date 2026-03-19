import type { SensorReading } from '../types'
import SensorChart from './SensorChart'

interface Props {
  sensorData: Map<string, SensorReading[]>
}

export default function SensorCharts({ sensorData }: Props) {
  return (
    <div className="grid grid-cols-2 grid-rows-2 gap-4 h-full">
      <SensorChart
        title="Temperature"
        dataKey="temperature"
        data={sensorData}
        unit="\u00B0C"
        normalRange={{ min: 60, max: 85 }}
      />
      <SensorChart
        title="Pressure"
        dataKey="pressure"
        data={sensorData}
        unit="bar"
        normalRange={{ min: 2.0, max: 6.0 }}
      />
      <SensorChart
        title="Vibration"
        dataKey="vibration"
        data={sensorData}
        unit="mm/s"
        normalRange={{ min: 0.5, max: 4.0 }}
      />
      <SensorChart
        title="Flow Rate"
        dataKey="flow_rate"
        data={sensorData}
        unit="L/min"
        normalRange={{ min: 80, max: 150 }}
      />
    </div>
  )
}
