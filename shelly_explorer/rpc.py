from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


class ShellyRPCError(RuntimeError):
    pass


@dataclass(slots=True)
class ShellyRPCClient:
    host: str
    timeout: float = 5.0

    def _url(self, method: str) -> str:
        host = self.host.strip().rstrip('/')
        if not host.startswith('http'):
            host = 'http://' + host
        return host + '/rpc/' + method

    def call(self, method: str, **params: Any) -> dict[str, Any]:
        response = requests.get(self._url(method), params=params, timeout=self.timeout)
        payload = response.json()
        if response.status_code >= 400:
            raise ShellyRPCError(f'{method} failed: HTTP {response.status_code}: {payload}')
        if isinstance(payload, dict) and payload.get('code', 0) < 0:
            raise ShellyRPCError(f'{method} failed: {payload}')
        return payload

    def list_methods(self) -> list[str]:
        return list(self.call('Shelly.ListMethods').get('methods', []))

    def get_device_info(self, ident: bool = False) -> dict[str, Any]:
        if ident:
            return self.call('Shelly.GetDeviceInfo', ident=True)
        return self.call('Shelly.GetDeviceInfo')

    def get_status(self) -> dict[str, Any]:
        return self.call('Shelly.GetStatus')

    def get_config(self) -> dict[str, Any]:
        return self.call('Shelly.GetConfig')

    def get_components(self) -> dict[str, Any]:
        return self.call('Shelly.GetComponents')
