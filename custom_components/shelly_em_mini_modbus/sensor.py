from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_HOST, DOMAIN, SENSOR_DEFINITIONS
from .coordinator import ShellyEmMiniModbusCoordinator


@dataclass(frozen=True, kw_only=True)
class ShellyEmMiniSensorEntityDescription(SensorEntityDescription):
    """Description for a Shelly EM Mini sensor."""


SENSOR_DESCRIPTIONS: tuple[ShellyEmMiniSensorEntityDescription, ...] = tuple(
    ShellyEmMiniSensorEntityDescription(
        key=key,
        name=label,
        native_unit_of_measurement=unit,
        device_class=device_class,
        state_class=state_class,
    )
    for label, key, _address, unit, device_class, state_class in SENSOR_DEFINITIONS
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Shelly EM Mini Modbus sensors."""
    coordinator: ShellyEmMiniModbusCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        ShellyEmMiniSensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    )


class ShellyEmMiniSensor(CoordinatorEntity[ShellyEmMiniModbusCoordinator], SensorEntity):
    """Shelly EM Mini Modbus sensor."""

    entity_description: ShellyEmMiniSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ShellyEmMiniModbusCoordinator,
        entry: ConfigEntry,
        description: ShellyEmMiniSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.unique_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.data[CONF_HOST])},
            manufacturer="Shelly",
            model="EM Mini Gen4",
            name=entry.title,
        )

    @property
    def native_value(self) -> Any:
        return self.coordinator.data.get(self.entity_description.key)
