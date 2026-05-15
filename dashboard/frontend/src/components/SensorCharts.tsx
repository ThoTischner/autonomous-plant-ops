import type { SensorReading } from '../types'
import SensorChart from './SensorChart'

interface Props {
  sensorData: Map<string, SensorReading[]>
}

export default function SensorCharts({ sensorData }: Props) {
  return (
    <div className="grid grid-cols-2 grid-rows-2 gap-4 h-full">
      <SensorChart
        title="Temperatur"
        dataKey="temperature"
        data={sensorData}
        unit="°C"
      />
      <SensorChart title="Druck" dataKey="pressure" data={sensorData} unit="bar" />
      <SensorChart
        title="Vibration"
        dataKey="vibration"
        data={sensorData}
        unit="mm/s"
      />
      <SensorChart
        title="Durchfluss"
        dataKey="flow_rate"
        data={sensorData}
        unit="L/min"
      />
    </div>
  )
}
