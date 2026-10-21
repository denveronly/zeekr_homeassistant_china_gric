"""Binary sensor platform — charging, openings and tyre warnings."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import ZeekrCoordinator
from .entity import VehicleEntityManager, ZeekrEntity

_POSITIONS = ("fl", "fr", "rl", "rr")
_POS_LABEL = {"fl": "front left", "fr": "front right", "rl": "rear left", "rr": "rear right"}


@dataclass(frozen=True)
class BinarySpec:
    key: str
    name: str
    path: tuple[str, ...]
    device_class: BinarySensorDeviceClass | None = None
    invert: bool = False


def _build_specs() -> list[BinarySpec]:
    specs: list[BinarySpec] = [
        BinarySpec("charging", "Charging", ("battery", "charging"),
                   BinarySensorDeviceClass.BATTERY_CHARGING),
        BinarySpec("plugged_in", "Charger plugged in", ("battery", "plugged"),
                   BinarySensorDeviceClass.PLUG),
        BinarySpec("door_open_fl", "Door front left", ("doors", "fl"),
                   BinarySensorDeviceClass.DOOR),
        BinarySpec("door_open_fr", "Door front right", ("doors", "fr"),
                   BinarySensorDeviceClass.DOOR),
        BinarySpec("door_open_rl", "Door rear left", ("doors", "rl"),
                   BinarySensorDeviceClass.DOOR),
        BinarySpec("door_open_rr", "Door rear right", ("doors", "rr"),
                   BinarySensorDeviceClass.DOOR),
        BinarySpec("trunk_open", "Trunk", ("doors", "trunk"),
                   BinarySensorDeviceClass.DOOR),
        BinarySpec("hood_open", "Hood", ("doors", "hood"),
                   BinarySensorDeviceClass.DOOR),
        BinarySpec("window_open_fl", "Window front left", ("windows", "fl"),
                   BinarySensorDeviceClass.WINDOW),
        BinarySpec("window_open_fr", "Window front right", ("windows", "fr"),
                   BinarySensorDeviceClass.WINDOW),
        BinarySpec("window_open_rl", "Window rear left", ("windows", "rl"),
                   BinarySensorDeviceClass.WINDOW),
        BinarySpec("window_open_rr", "Window rear right", ("windows", "rr"),
                   BinarySensorDeviceClass.WINDOW),
    ]
    for pos in _POSITIONS:
        specs.append(
            BinarySpec(
                f"tyre_warning_{pos}", f"Tire pressure warning {_POS_LABEL[pos]}",
                ("tyres", "pressure_warning", pos),
                BinarySensorDeviceClass.PROBLEM,
            )
        )
    return specs


BINARY_SPECS = _build_specs()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensor platform."""
    coordinator: ZeekrCoordinator = hass.data[DOMAIN][entry.entry_id]
    VehicleEntityManager(
        hass,
        entry,
        coordinator,
        async_add_entities,
        lambda vin: [ZeekrBinarySensor(coordinator, vin, spec)
                     for spec in BINARY_SPECS],
    ).start()


class ZeekrBinarySensor(ZeekrEntity, BinarySensorEntity):
    """A boolean read from the canonical state."""

    def __init__(self, coordinator: ZeekrCoordinator, vin: str,
                 spec: BinarySpec) -> None:
        super().__init__(coordinator, vin, spec.key)
        self._spec = spec
        self._attr_name = spec.name
        self._attr_device_class = spec.device_class

    @property
    def is_on(self) -> bool | None:
        value = self.get(*self._spec.path)
        if value is None:
            return None
        return (not value) if self._spec.invert else bool(value)
