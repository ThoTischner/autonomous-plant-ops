from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SensorRange:
    min_val: float
    max_val: float
    unit: str


@dataclass
class EquipmentConfig:
    equipment_id: str
    name: str
    temperature: SensorRange
    pressure: SensorRange
    vibration: SensorRange
    flow_rate: SensorRange | None = None
    # Mutable runtime state
    speed_factor: float = field(default=1.0, repr=False)
    cooling_factor: float = field(default=1.0, repr=False)
    is_shutdown: bool = field(default=False, repr=False)

    def reset(self) -> None:
        self.speed_factor = 1.0
        self.cooling_factor = 1.0
        self.is_shutdown = False


EQUIPMENT: dict[str, EquipmentConfig] = {
    "P-101": EquipmentConfig(
        equipment_id="P-101",
        name="Pump P-101",
        temperature=SensorRange(60, 80, "°C"),
        pressure=SensorRange(2, 4, "bar"),
        vibration=SensorRange(0, 5, "mm/s"),
        flow_rate=SensorRange(100, 150, "L/min"),
    ),
    "R-201": EquipmentConfig(
        equipment_id="R-201",
        name="Reactor R-201",
        temperature=SensorRange(150, 200, "°C"),
        pressure=SensorRange(5, 10, "bar"),
        vibration=SensorRange(0, 3, "mm/s"),
    ),
    "C-301": EquipmentConfig(
        equipment_id="C-301",
        name="Compressor C-301",
        temperature=SensorRange(40, 70, "°C"),
        pressure=SensorRange(6, 12, "bar"),
        vibration=SensorRange(0, 8, "mm/s"),
        flow_rate=SensorRange(200, 300, "m³/h"),
    ),
}
