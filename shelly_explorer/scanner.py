from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from ipaddress import ip_network
from typing import Any

import requests

from shelly_explorer.modbus import is_port_open


@dataclass(slots=True)
class DiscoveredShelly:
    ip: str
    model: str = ''
    app: str = ''
    version: str = ''
    firmware_id: str = ''
    mac: str = ''
    modbus: bool = False
    voltage: float | None = None
    current: float | None = None
    power: float | None = None
    frequency: float | None = None


def _rpc_call(host: str, method: str, params: dict[str, Any] | None = None, timeout: float = 1.5) -> dict[str, Any] | None:
    try:
        response = requests.get(
            f'http://{host}/rpc/{method}',
            params=params or {},
            timeout=timeout,
        )
        if response.status_code != 200:
            return None
        payload = response.json()
        return payload if isinstance(payload, dict) else None
    except (requests.RequestException, ValueError):
        return None


def scan_one_host(host: str, timeout: float = 1.5) -> DiscoveredShelly | None:
    info = _rpc_call(host, 'Shelly.GetDeviceInfo', timeout=timeout)
    if not info:
        return None

    device = DiscoveredShelly(
        ip=host,
        model=str(info.get('model') or ''),
        app=str(info.get('app') or ''),
        version=str(info.get('ver') or ''),
        firmware_id=str(info.get('fw_id') or ''),
        mac=str(info.get('mac') or info.get('id') or ''),
    )

    device.modbus = is_port_open(host, 502, timeout=timeout)

    em1 = _rpc_call(host, 'EM1.GetStatus', {'id': 0}, timeout=timeout)
    if em1:
        for attr, key in [
            ('voltage', 'voltage'),
            ('current', 'current'),
            ('power', 'act_power'),
            ('frequency', 'freq'),
        ]:
            value = em1.get(key)
            if isinstance(value, (int, float)):
                setattr(device, attr, value)

    return device


def is_em_device(device: DiscoveredShelly) -> bool:
    return (
        device.voltage is not None
        or device.current is not None
        or device.power is not None
        or device.frequency is not None
        or 'em' in device.model.lower()
        or 'em' in device.app.lower()
    )


def scan_subnet(
    subnet: str,
    timeout: float = 1.5,
    workers: int = 64,
    em_only: bool = False,
) -> list[DiscoveredShelly]:
    network = ip_network(subnet, strict=False)
    found: list[DiscoveredShelly] = []

    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        futures = {
            executor.submit(scan_one_host, str(ip), timeout): str(ip)
            for ip in network.hosts()
        }
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                found.append(result)

    if em_only:
        found = [device for device in found if is_em_device(device)]

    return sorted(found, key=lambda item: tuple(int(part) for part in item.ip.split('.')))
