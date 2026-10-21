"""Sensor platform — read-only vehicle telemetry."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    EntityCategory,
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfLength,
    UnitOfPower,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import ZeekrCoordinator
from .entity import VehicleEntityManager, ZeekrEntity

_TYRE_POSITIONS = ("fl", "fr", "rl", "rr")
_TYRE_LABEL = {"fl": "front left", "fr": "front right", "rl": "rear left", "rr": "rear right"}

# No standard HA unit for consumption; keep the string the car reports.
_CONSUMPTION_UNIT = "kWh/100km"


@dataclass(frozen=True)
class SensorSpec:
    """Declarative description of one sensor."""

    key: str
    name: str
    path: tuple[str, ...]
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None
    unit: str | None = None
    icon: str | None = None
    divisor: float = 1.0
    category: EntityCategory | None = None


def _build_specs() -> list[SensorSpec]:
    specs: list[SensorSpec] = [
        # -- drive / energy ---------------------------------------------
        SensorSpec(
            "battery_level", "Battery level", ("battery", "soc"),
            SensorDeviceClass.BATTERY, SensorStateClass.MEASUREMENT,
            PERCENTAGE, "mdi:battery",
        ),
        SensorSpec(
            "range", "Range", ("battery", "range"),
            SensorDeviceClass.DISTANCE, SensorStateClass.MEASUREMENT,
            UnitOfLength.KILOMETERS, "mdi:map-marker-distance",
        ),
        SensorSpec(
            "odometer", "Odometer", ("odometer",),
            SensorDeviceClass.DISTANCE, SensorStateClass.TOTAL_INCREASING,
            UnitOfLength.KILOMETERS, "mdi:counter",
        ),
        SensorSpec(
            "speed", "Speed", ("safety", "speed"),
            SensorDeviceClass.SPEED, SensorStateClass.MEASUREMENT,
            UnitOfSpeed.KILOMETERS_PER_HOUR, "mdi:speedometer",
        ),
        SensorSpec(
            "power_consumption", "Average consumption", ("battery", "power_consumption"),
            None, None, _CONSUMPTION_UNIT, "mdi:lightning-bolt-outline",
        ),
        # -- climate ----------------------------------------------------
        SensorSpec(
            "inside_temperature", "Interior temperature", ("climate", "inside_temp"),
            SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT,
            UnitOfTemperature.CELSIUS, "mdi:thermometer",
        ),
        SensorSpec(
            "outside_temperature", "Exterior temperature", ("climate", "outside_temp"),
            SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT,
            UnitOfTemperature.CELSIUS, "mdi:thermometer-lines",
        ),
        SensorSpec(
            "climate_target_temperature", "Climate set temperature", ("climate", "target_temp"),
            SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT,
            UnitOfTemperature.CELSIUS, "mdi:thermostat",
        ),
        # -- charging ---------------------------------------------------
        SensorSpec(
            "charge_power", "Charging power", ("battery", "power"),
            SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT,
            UnitOfPower.KILO_WATT, "mdi:flash",
        ),
        SensorSpec(
            "charge_voltage", "Charging voltage", ("battery", "voltage"),
            SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT,
            UnitOfElectricPotential.VOLT, "mdi:sine-wave",
        ),
        SensorSpec(
            "charge_current", "Charging current", ("battery", "current"),
            SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT,
            UnitOfElectricCurrent.AMPERE, "mdi:current-ac",
        ),
        SensorSpec(
            "remaining_charge_time", "Estimated full charge time", ("battery", "remaining_minutes"),
            SensorDeviceClass.DURATION, SensorStateClass.MEASUREMENT,
            UnitOfTime.MINUTES, "mdi:timer-sand",
        ),
        # Deliberately *not* ``SensorDeviceClass.BATTERY``: that class means
        # "how much charge is left", and the front end uses it to pick the
        # battery badge it draws on the device page.  With two battery-class
        # sensors on one vehicle it picked this one, so the corner of the
        # device page showed the charge target (90 %) instead of the actual
        # state of charge.  The icon still says "charging limit"; only the
        # class — which is what makes a number *the* battery — is dropped.
        SensorSpec(
            "charge_limit", "Charge limit", ("battery", "limit"),
            None, None,
            PERCENTAGE, "mdi:battery-charging-high",
        ),
        # -- 12 V aux battery ------------------------------------------
        SensorSpec(
            "aux_battery_voltage", "12V battery voltage", ("battery12v", "voltage"),
            SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT,
            UnitOfElectricPotential.VOLT, "mdi:car-battery",
        ),
        SensorSpec(
            "aux_battery_level", "12V battery level", ("battery12v", "soc"),
            None, SensorStateClass.MEASUREMENT,
            PERCENTAGE, "mdi:car-battery",
        ),
        # -- cabin air / service ---------------------------------------
        SensorSpec(
            "service_distance", "Service distance remaining", ("service", "distance_to_service"),
            SensorDeviceClass.DISTANCE, None,
            UnitOfLength.KILOMETERS, "mdi:wrench-clock",
        ),
        SensorSpec(
            "service_days", "Service days remaining", ("service", "days_to_service"),
            SensorDeviceClass.DURATION, None,
            UnitOfTime.DAYS, "mdi:calendar-clock",
        ),
        # -- diagnostics -------------------------------------------------
        # Not telemetry about the car, but about the *data*: when the car last
        # uploaded.  This is what tells you whether a lagging value is Home
        # Assistant polling too slowly or the car simply not reporting.
        SensorSpec(
            "report_time", "Last status report", ("report_time",),
            SensorDeviceClass.TIMESTAMP, None,
            None, "mdi:clock-check-outline",
            category=EntityCategory.DIAGNOSTIC,
        ),
    ]

    for pos in _TYRE_POSITIONS:
        specs.append(
            SensorSpec(
                f"tyre_pressure_{pos}", f"Tire pressure {_TYRE_LABEL[pos]}",
                ("tyres", "pressure", pos),
                SensorDeviceClass.PRESSURE, SensorStateClass.MEASUREMENT,
                UnitOfPressure.KPA, "mdi:car-tire-alert",
            )
        )
        specs.append(
            SensorSpec(
                f"tyre_temperature_{pos}", f"Tire temperature {_TYRE_LABEL[pos]}",
                ("tyres", "temp", pos),
                SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT,
                UnitOfTemperature.CELSIUS, "mdi:thermometer",
            )
        )

    return specs


SENSOR_SPECS = _build_specs()


def _as_datetime(value: Any) -> datetime | None:
    """Turn a gateway epoch stamp into an aware datetime.

    GRIC reports milliseconds; a seconds stamp has been seen on the SNC side,
    so anything that would land before 1973 is read as seconds instead.
    """
    try:
        stamp = float(value)
    except (TypeError, ValueError):
        return None
    if stamp <= 0:
        return None
    if stamp > 1e11:  # milliseconds
        stamp /= 1000.0
    try:
        return datetime.fromtimestamp(stamp, tz=dt_util.UTC)
    except (OverflowError, OSError, ValueError):
        return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: ZeekrCoordinator = hass.data[DOMAIN][entry.entry_id]
    VehicleEntityManager(
        hass,
        entry,
        coordinator,
        async_add_entities,
        lambda vin: [ZeekrSensor(coordinator, vin, spec) for spec in SENSOR_SPECS],
    ).start()


class ZeekrSensor(ZeekrEntity, SensorEntity):
    """A single telemetry value read from the canonical state."""

    def __init__(self, coordinator: ZeekrCoordinator, vin: str,
                 spec: SensorSpec) -> None:
        super().__init__(coordinator, vin, spec.key)
        self._spec = spec
        self._attr_name = spec.name
        self._attr_device_class = spec.device_class
        self._attr_state_class = spec.state_class
        if spec.unit:
            self._attr_native_unit_of_measurement = spec.unit
        if spec.icon:
            self._attr_icon = spec.icon
        if spec.category:
            self._attr_entity_category = spec.category

    @property
    def native_value(self):
        value = self.get(*self._spec.path)
        if value is None:
            return None
        if self._spec.device_class == SensorDeviceClass.TIMESTAMP:
            return _as_datetime(value)
        if self._spec.divisor and self._spec.divisor != 1.0:
            try:
                return round(float(value) / self._spec.divisor, 1)
            except (TypeError, ValueError):
                return None
        return value
