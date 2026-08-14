from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from .const import CONF_HOST, CONF_NAME, CONF_PORT, DEFAULT_NAME, DEFAULT_PORT, DOMAIN
from .modbus import ModbusError, ShellyEmMiniModbusClient


class CannotConnect(Exception):
    """Raised when the device cannot be reached."""


async def validate_input(hass: HomeAssistant, data: dict[str, object]) -> None:
    host = str(data[CONF_HOST])
    port = int(data.get(CONF_PORT, DEFAULT_PORT))
    client = ShellyEmMiniModbusClient(host, port)

    try:
        await hass.async_add_executor_job(client.read_float32_cdab, 2007)
    except (OSError, ModbusError) as exc:
        raise CannotConnect from exc


class ShellyEmMiniModbusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Shelly EM Mini Modbus."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, object] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            host = str(user_input[CONF_HOST]).strip()
            name = str(user_input[CONF_NAME]).strip()
            port = int(user_input.get(CONF_PORT, DEFAULT_PORT))
            data = {CONF_HOST: host, CONF_NAME: name, CONF_PORT: port}

            await self.async_set_unique_id(host)
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
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                }
            ),
            errors=errors,
        )
