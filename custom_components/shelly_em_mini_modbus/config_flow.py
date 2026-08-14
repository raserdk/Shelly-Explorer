from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import ipaddress
import math
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from .const import (
    CONF_HOST,
    CONF_MODEL,
    CONF_NAME,
    CONF_PORT,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DOMAIN,
    MODEL_3EM_63_GEN3,
    MODEL_EM_MINI_GEN4,
    MODEL_NAMES,
)
from .modbus import ModbusError, ShellyEmMiniModbusClient

CONF_SETUP_METHOD = "setup_method"
CONF_SUBNET = "subnet"
CONF_DEVICE = "device"
SETUP_METHOD_MANUAL = "manual"
SETUP_METHOD_SCAN = "scan"
DEFAULT_SUBNET = "192.168.1.0/24"
MAX_SCAN_HOSTS = 1024
SCAN_WORKERS = 64
SCAN_TIMEOUT = 0.7


class CannotConnect(Exception):
    """Raised when the device cannot be reached."""


class InvalidSubnet(Exception):
    """Raised when the subnet cannot be scanned."""


@dataclass(frozen=True)
class DiscoveredDevice:
    """A supported Shelly Modbus energy meter discovered on the network."""

    host: str
    model: str
    power: float | None
    voltage: float | None
    frequency: float | None = None

    @property
    def label(self) -> str:
        model_name = MODEL_NAMES.get(self.model, self.model)
        power = f"{self.power:.0f} W" if self.power is not None and math.isfinite(self.power) else "? W"
        voltage = f", {self.voltage:.0f} V" if self.voltage is not None and math.isfinite(self.voltage) else ""
        frequency = f", {self.frequency:.1f} Hz" if self.frequency is not None and math.isfinite(self.frequency) else ""
        return f"{self.host} - {model_name} - {power}{voltage}{frequency}"


async def validate_input(hass: HomeAssistant, data: dict[str, object]) -> str:
    host = str(data[CONF_HOST])
    port = int(data.get(CONF_PORT, DEFAULT_PORT))

    try:
        return await hass.async_add_executor_job(detect_device_model, host, port)
    except (OSError, ModbusError) as exc:
        raise CannotConnect from exc


def _valid_voltage(value: float) -> bool:
    return math.isfinite(value) and 180 <= value <= 260


def _valid_frequency(value: float) -> bool:
    return math.isfinite(value) and 45 <= value <= 55


def _probe_em_mini(client: ShellyEmMiniModbusClient, host: str) -> DiscoveredDevice | None:
    try:
        voltage = client.read_float32_cdab(2003)
        frequency = client.read_float32_cdab(2016)
    except (OSError, ModbusError):
        return None

    if not _valid_voltage(voltage) or not _valid_frequency(frequency):
        return None

    try:
        power = client.read_float32_cdab(2007)
    except (OSError, ModbusError):
        power = None

    return DiscoveredDevice(
        host=host,
        model=MODEL_EM_MINI_GEN4,
        power=power,
        voltage=voltage,
        frequency=frequency,
    )


def _probe_3em_63(client: ShellyEmMiniModbusClient, host: str) -> DiscoveredDevice | None:
    try:
        phase_a_voltage = client.read_float32_cdab(1020)
    except (OSError, ModbusError):
        return None

    if not _valid_voltage(phase_a_voltage):
        return None

    try:
        power = client.read_float32_cdab(1013)
    except (OSError, ModbusError):
        power = None

    return DiscoveredDevice(
        host=host,
        model=MODEL_3EM_63_GEN3,
        power=power,
        voltage=phase_a_voltage,
    )


def probe_host(host: str, port: int, timeout: float = SCAN_TIMEOUT) -> DiscoveredDevice | None:
    client = ShellyEmMiniModbusClient(host, port, timeout=timeout)
    return _probe_3em_63(client, host) or _probe_em_mini(client, host)


def detect_device_model(host: str, port: int) -> str:
    device = probe_host(host, port, timeout=2.5)
    if device is None:
        raise ModbusError("No supported Shelly Modbus energy meter detected")
    return device.model


def _probe_host(host: str, port: int) -> DiscoveredDevice | None:
    return probe_host(host, port)


def discover_devices(subnet: str, port: int) -> list[DiscoveredDevice]:
    try:
        network = ipaddress.ip_network(subnet, strict=False)
    except ValueError as exc:
        raise InvalidSubnet from exc

    hosts = [str(host) for host in network.hosts()]
    if len(hosts) > MAX_SCAN_HOSTS:
        raise InvalidSubnet

    devices: list[DiscoveredDevice] = []
    with ThreadPoolExecutor(max_workers=SCAN_WORKERS) as executor:
        futures = [executor.submit(_probe_host, host, port) for host in hosts]
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                devices.append(result)

    return sorted(devices, key=lambda item: tuple(int(part) for part in item.host.split(".")))


class ShellyEmMiniModbusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Shelly Modbus energy meters."""

    VERSION = 1

    def __init__(self) -> None:
        self._scan_results: dict[str, DiscoveredDevice] = {}
        self._scan_port = DEFAULT_PORT

    def _configured_hosts(self) -> set[str]:
        """Return hosts that are already configured for this integration."""
        configured_hosts: set[str] = set()
        for entry in self._async_current_entries():
            if entry.unique_id:
                configured_hosts.add(entry.unique_id)
            host = entry.data.get(CONF_HOST)
            if isinstance(host, str):
                configured_hosts.add(host)
        return configured_hosts

    def _discovery_label(self, device: DiscoveredDevice, configured_hosts: set[str]) -> str:
        """Return a label for a discovered device, including configuration status."""
        status = "konfigureret" if device.host in configured_hosts else "ny"
        return f"{device.label} - {status}"

    async def async_step_user(self, user_input: dict[str, object] | None = None):
        if user_input is not None:
            setup_method = str(user_input[CONF_SETUP_METHOD])
            if setup_method == SETUP_METHOD_SCAN:
                return await self.async_step_scan()
            return await self.async_step_manual()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SETUP_METHOD, default=SETUP_METHOD_SCAN): vol.In(
                        {
                            SETUP_METHOD_SCAN: "Scan netværk",
                            SETUP_METHOD_MANUAL: "Manuel IP",
                        }
                    ),
                }
            ),
        )

    async def async_step_manual(self, user_input: dict[str, object] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            host = str(user_input[CONF_HOST]).strip()
            name = str(user_input[CONF_NAME]).strip()
            port = int(user_input.get(CONF_PORT, DEFAULT_PORT))
            data = {CONF_HOST: host, CONF_NAME: name, CONF_PORT: port}

            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()

            try:
                model = await validate_input(self.hass, data)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"
            else:
                data[CONF_MODEL] = model
                return self.async_create_entry(title=name, data=data)

        return self.async_show_form(
            step_id="manual",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                }
            ),
            errors=errors,
        )

    async def async_step_scan(self, user_input: dict[str, object] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            subnet = str(user_input[CONF_SUBNET]).strip()
            port = int(user_input.get(CONF_PORT, DEFAULT_PORT))
            self._scan_port = port

            try:
                devices = await self.hass.async_add_executor_job(discover_devices, subnet, port)
            except InvalidSubnet:
                errors["base"] = "invalid_subnet"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"
            else:
                if not devices:
                    errors["base"] = "no_devices_found"
                else:
                    configured_hosts = self._configured_hosts()
                    self._scan_results = {
                        self._discovery_label(device, configured_hosts): device
                        for device in devices
                    }
                    return await self.async_step_pick()

        return self.async_show_form(
            step_id="scan",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SUBNET, default=DEFAULT_SUBNET): str,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                }
            ),
            errors=errors,
        )

    async def async_step_pick(self, user_input: dict[str, object] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            label = str(user_input[CONF_DEVICE])
            name = str(user_input[CONF_NAME]).strip()
            device = self._scan_results[label]
            data = {
                CONF_HOST: device.host,
                CONF_NAME: name,
                CONF_PORT: self._scan_port,
                CONF_MODEL: device.model,
            }

            await self.async_set_unique_id(device.host)
            self._abort_if_unique_id_configured()

            try:
                await validate_input(self.hass, data)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=name, data=data)

        return self.async_show_form(
            step_id="pick",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_DEVICE): vol.In(list(self._scan_results)),
                    vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                }
            ),
            errors=errors,
        )
