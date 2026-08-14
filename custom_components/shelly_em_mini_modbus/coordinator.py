from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_HOST, CONF_PORT, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, DOMAIN, SENSOR_DEFINITIONS
from .modbus import ModbusError, ShellyEmMiniModbusClient


class ShellyEmMiniModbusCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate Modbus polling for one Shelly EM Mini device."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.host: str = entry.data[CONF_HOST]
        self.port: int = entry.data.get(CONF_PORT, DEFAULT_PORT)
        self.client = ShellyEmMiniModbusClient(self.host, self.port)

        super().__init__(
            hass,
            hass.loop,
            name=f"{DOMAIN}_{self.host}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.hass.async_add_executor_job(self._read_values)
        except (OSError, ModbusError) as exc:
            raise UpdateFailed(f"Failed to read Shelly EM Mini Modbus data from {self.host}: {exc}") from exc

    def _read_values(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        for _label, key, address, _unit, _device_class, _state_class in SENSOR_DEFINITIONS:
            data[key] = self.client.read_float32_cdab(address)
        return data
