"""Button platform — one-shot remote actions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import ZeekrCoordinator
from .entity import VehicleEntityManager, ZeekrEntity
from .parser import PRESET_QUICK_COOL, PRESET_QUICK_HEAT


@dataclass(frozen=True)
class ButtonSpec:
    key: str
    name: str
    icon: str
    command: str = ""
    service_id: str = ""
    setting: dict[str, Any] | None = None
    # Either a raw remote command (above), or one of the App's climate presets.
    preset: str | None = None


BUTTON_SPECS: tuple[ButtonSpec, ...] = (
    ButtonSpec(
        "flash_blinkers", "Flash lights", "mdi:car-light-alert",
        "start", "RHL",
        {"serviceParameters": [{"key": "rhl", "value": "light-flash"}]},
    ),
    ButtonSpec(
        "honk_flash", "Horn and flash", "mdi:bullhorn",
        "start", "RHL",
        {"serviceParameters": [{"key": "rhl", "value": "horn-light-flash"}]},
    ),
    # Captured from the Chinese app on 2026-10-21: opening AND closing the
    # power tailgate both send RDU start with target=trunk; the car toggles.
    # The app asks for the vehicle PIN before closing, but that check happens
    # app-side only: the command itself carries no PIN proof.
    ButtonSpec(
        "open_trunk", "Trunk open / close", "mdi:car-back",
        "start", "RDU",
        {"serviceParameters": [{"key": "target", "value": "trunk"}]},
    ),
    ButtonSpec(
        "parking_comfort_off", "Turn off parking comfort", "mdi:car-seat-cooler",
        "stop", "PCM",
        {"serviceParameters": [{"key": "parking_comfortable", "value": "false"}]},
    ),
    # The App's 极速制冷 / 极速制热.  Their own command was never captured, so
    # these push the setpoint to the end of the scale — see
    # ``parser.preset_setpoint``.
    ButtonSpec("quick_cool", "Rapid cooling", "mdi:snowflake",
               preset=PRESET_QUICK_COOL),
    ButtonSpec("quick_heat", "Rapid heating", "mdi:heat-wave",
               preset=PRESET_QUICK_HEAT),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    coordinator: ZeekrCoordinator = hass.data[DOMAIN][entry.entry_id]

    def factory(vin: str) -> list[ButtonEntity]:
        entities: list[ButtonEntity] = [
            ZeekrCommandButton(coordinator, vin, spec) for spec in BUTTON_SPECS
        ]
        entities.append(ZeekrRefreshButton(coordinator, vin))
        return entities

    VehicleEntityManager(hass, entry, coordinator, async_add_entities, factory).start()


class ZeekrCommandButton(ZeekrEntity, ButtonEntity):
    """A button that fires a fixed remote-control command."""

    def __init__(self, coordinator: ZeekrCoordinator, vin: str,
                 spec: ButtonSpec) -> None:
        super().__init__(coordinator, vin, spec.key)
        self._attr_name = spec.name
        self._attr_icon = spec.icon
        self._spec = spec

    async def async_press(self) -> None:
        if self._spec.preset is not None:
            await self.coordinator.async_set_climate_preset(
                self.vin, self._spec.preset
            )
            return
        await self.send_command(
            self._spec.command, self._spec.service_id, self._spec.setting or {}
        )


class ZeekrRefreshButton(ZeekrEntity, ButtonEntity):
    """Force an immediate poll (and vehicle rediscovery)."""

    _attr_name = "Refresh now"
    _attr_icon = "mdi:refresh"

    def __init__(self, coordinator: ZeekrCoordinator, vin: str) -> None:
        super().__init__(coordinator, vin, "refresh")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        # The interval is adaptive: a sleeping car backs it off, so "why has my
        # change not shown up yet" is answered by looking here.
        polling = self.coordinator.polling_info
        return {
            "last_poll": self.coordinator.latest_poll_time,
            "poll_interval_minutes": polling.get("current_minutes"),
            "poll_interval_max_minutes": polling.get("max_minutes"),
            "unchanged_polls": polling.get("idle_polls"),
        }

    async def async_press(self) -> None:
        await self.coordinator.async_force_discovery()
