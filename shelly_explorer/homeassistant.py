from __future__ import annotations

import re
from collections.abc import Iterable


HA_SENSOR_DEFINITIONS = [
    ('Effekt', 'power', 2007, 'W', 'power', 'measurement'),
    ('Spænding', 'voltage', 2003, 'V', 'voltage', 'measurement'),
    ('Strøm', 'current', 2005, 'A', 'current', 'measurement'),
    ('Frekvens', 'frequency', 2016, 'Hz', 'frequency', 'measurement'),
    ('Energi', 'energy', 2310, 'Wh', 'energy', 'total_increasing'),
    ('Returneret energi', 'returned_energy', 2312, 'Wh', 'energy', 'total_increasing'),
]


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = value.replace('æ', 'ae').replace('ø', 'oe').replace('å', 'aa')
    value = re.sub(r'[^a-z0-9]+', '_', value)
    value = re.sub(r'_+', '_', value).strip('_')
    return value or 'shelly_em'


def _sensor_block(
    *,
    indent: str,
    name: str,
    unique_id: str,
    address: int,
    unit: str,
    device_class: str,
    state_class: str,
) -> list[str]:
    return [
        f'{indent}- name: "{name}"',
        f'{indent}  unique_id: {unique_id}',
        f'{indent}  input_type: input',
        f'{indent}  address: {address}',
        f'{indent}  data_type: float32',
        f'{indent}  swap: word',
        f'{indent}  unit_of_measurement: "{unit}"',
        f'{indent}  device_class: {device_class}',
        f'{indent}  state_class: {state_class}',
    ]


def generate_ha_modbus_hub_yaml(
    host: str,
    name: str,
    unique_id_prefix: str | None = None,
    port: int = 502,
) -> str:
    base = slugify(unique_id_prefix or name)
    hub_name = base if base.startswith('shelly_em_') else f'shelly_em_{base}'

    lines = [
        f'  - name: {hub_name}',
        '    type: tcp',
        f'    host: {host}',
        f'    port: {port}',
        '    sensors:',
    ]

    for label, suffix, address, unit, device_class, state_class in HA_SENSOR_DEFINITIONS:
        lines.extend(
            _sensor_block(
                indent='      ',
                name=f'{name} {label}',
                unique_id=f'{base}_{suffix}',
                address=address,
                unit=unit,
                device_class=device_class,
                state_class=state_class,
            )
        )

    return '\n'.join(lines)


def generate_ha_modbus_yaml(host: str, name: str, unique_id_prefix: str | None = None, port: int = 502) -> str:
    return 'modbus:\n' + generate_ha_modbus_hub_yaml(host, name, unique_id_prefix, port) + '\n'


def generate_ha_modbus_multi_yaml(devices: Iterable[tuple[str, str, str | None]], port: int = 502) -> str:
    lines = ['modbus:']
    for host, name, unique_id_prefix in devices:
        lines.append(generate_ha_modbus_hub_yaml(host, name, unique_id_prefix, port))
    return '\n'.join(lines) + '\n'
