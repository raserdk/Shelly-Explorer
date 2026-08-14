from __future__ import annotations

import logging
import time
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_HOST,
    CONF_PORT,
    DEFAULT_MODBUS_TIMEOUT,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MODBUS_RETRIES,
    SENSOR_DEFINITIONS,
)
from .modbus import ModbusError, ShellyEmMiniModbusClient

_LOGGER = logging.getLogger(__name__)


class ShellyEmMiniModbusCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate Modbus polling for one Shelly EM Mini device."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.host: str = entry.data[CONF_HOST]
        self.port: int = entry.data.get(CONF_PORT, DEFAULT_PORT)
        self.client = ShellyEmMiniModbusClient(self.host, self.port, timeout=DEFAULT_MODBUS_TIMEOUT)

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.host}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.hass.async_add_executor_job(self._read_values_with_retry)
        except (OSError, ModbusError) as exc:
            raise UpdateFailed(f"Failed to read Shelly EM Mini Modbus data from {self.host}: {exc}") from exc

    def _read_values_with_retry(self) -> dict[str, Any]:
        last_error: OSError | ModbusError | None = None
        for attempt in range(MODBUS_RETRIES + 1):
            try:
                return self._read_values()
            except (OSError, ModbusError) as exc:
                last_error = exc
                if attempt < MODBUS_RETRIES:
                    time.sleep(0.4)
        if last_error is not None:
            raise last_error
        raise ModbusError("Modbus polling failed without an error")

    def _read_values(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        raw_values: dict[int, float] = {}
        for _label, key, address, _unit, _device_class, _state_class, scale in SENSOR_DEFINITIONS:
            if address not in raw_values:
                raw_values[address] = self.client.read_float32_cdab(address)
            data[key] = raw_values[address] * scale
        return data
