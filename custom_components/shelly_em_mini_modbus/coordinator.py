from __future__ import annotations

import logging
import time
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    COMPUTED_SUMS_BY_MODEL,
    CONF_HOST,
    CONF_MODEL,
    CONF_PORT,
    DEFAULT_MODEL,
    DEFAULT_MODBUS_TIMEOUT,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MODBUS_RETRIES,
    SENSOR_DEFINITIONS_BY_MODEL,
)
from .modbus import ModbusError, ShellyEmMiniModbusClient

_LOGGER = logging.getLogger(__name__)


class ShellyEmMiniModbusCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate Modbus polling for one Shelly energy meter device."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.host: str = entry.data[CONF_HOST]
        self.port: int = entry.data.get(CONF_PORT, DEFAULT_PORT)
        self.model: str = entry.data.get(CONF_MODEL, DEFAULT_MODEL)
        self.sensor_definitions = SENSOR_DEFINITIONS_BY_MODEL.get(
            self.model,
            SENSOR_DEFINITIONS_BY_MODEL[DEFAULT_MODEL],
        )
        self.computed_sums = COMPUTED_SUMS_BY_MODEL.get(self.model, {})
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
            raise UpdateFailed(f"Failed to read Shelly energy meter Modbus data from {self.host}: {exc}") from exc

    def _read_values_with_retry(self) -> dict[str, Any]:
        last_error: OSError | ModbusError | None = None
        for attempt in range(MODBUS_RETRIES + 1):
            try:
                return self._read_values()
            except OSError as exc:
                last_error = exc
                if attempt < MODBUS_RETRIES:
                    time.sleep(0.4)
        if last_error is not None:
            raise last_error
        raise ModbusError("Modbus polling failed without an error")

    def _read_values(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        raw_values: dict[int, float | None] = {}
        successful_reads = 0

        for _label, key, address, _unit, _device_class, _state_class, scale in self.sensor_definitions:
            if address is None:
                data[key] = None
                continue

            if address not in raw_values:
                try:
                    raw_values[address] = self.client.read_float32_cdab(address)
                    successful_reads += 1
                except ModbusError as exc:
                    raw_values[address] = None
                    _LOGGER.debug(
                        "Unsupported or unreadable Modbus register %s for %s (%s): %s",
                        address,
                        self.host,
                        self.model,
                        exc,
                    )

            raw_value = raw_values[address]
            data[key] = raw_value * scale if raw_value is not None else None

        for target_key, source_keys in self.computed_sums.items():
            source_values = [data.get(source_key) for source_key in source_keys]
            data[target_key] = (
                sum(source_values)
                if all(isinstance(value, int | float) for value in source_values)
                else None
            )

        if successful_reads == 0:
            raise ModbusError("No Modbus registers could be read")

        return data
