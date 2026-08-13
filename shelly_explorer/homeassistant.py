from __future__ import annotations

import re


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r'[^a-z0-9]+', '_', value)
    value = re.sub(r'_+', '_', value).strip('_')
    return value or 'shelly_em'


def _sensor_block(
    *,
    name: str,
    unique_id: str,
    address: int,
    unit: str,
    device_class: str,
    state_class: str,
) -> list[str]:
    return [
        f'      - name: "{name}"',
        f'        unique_id: {unique_id}',
        '        input_type: input',
        f'        address: {address}',
        '        data_type: float32',
        '        swap: word',
        f'        unit_of_measurement: "{unit}"',
        f'        device_class: {device_class}',
        f'        state_class: {state_class}',
    ]


def generate_ha_modbus_yaml(host: str, name: str, unique_id_prefix: str | None = None, port: int = 502) -> str:
    base = slugify(unique_id_prefix or name)
    hub_name = f'shelly_em_{base}'

    sensors = [
        ('Effekt', 'power', 2007, 'W', 'power', 'measurement'),
        ('Spænding', 'voltage', 2003, 'V', 'voltage', 'measurement'),
        ('Strøm', 'current', 2005, 'A', 'current', 'measurement'),
        ('Frekvens', 'frequency', 2016, 'Hz', 'frequency', 'measurement'),
        ('Energi', 'energy', 2310, 'Wh', 'energy', 'total_increasing'),
        ('Returneret energi', 'returned_energy', 2312, 'Wh', 'energy', 'total_increasing'),
    ]

    lines = [
        'modbus:',
        f'  - name: {hub_name}',
        '    type: tcp',
        f'    host: {host}',
        f'    port: {port}',
        '    sensors:',
    ]

    for label, suffix, address, unit, device_class, state_class in sensors:
        lines.extend(
            _sensor_block(
                name=f'{name} {label}',
                unique_id=f'{base}_{suffix}',
                address=address,
                unit=unit,
                device_class=device_class,
                state_class=state_class,
            )
        )

    return '\n'.join(lines) + '\n'
