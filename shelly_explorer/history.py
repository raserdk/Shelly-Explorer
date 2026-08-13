from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from .rpc import ShellyRPCClient

HISTORY_KEYS = [
    'total_act_energy', 'total_act_ret_energy', 'lag_react_energy', 'lead_react_energy',
    'max_act_power', 'min_act_power', 'max_aprt_power', 'min_aprt_power',
    'max_voltage', 'min_voltage', 'avg_voltage',
    'max_current', 'min_current', 'avg_current',
]


def get_records(client: ShellyRPCClient, em_id: int = 0) -> list[dict[str, Any]]:
    return list(client.call('EM1Data.GetRecords', id=em_id).get('data_blocks', []))


def get_data(client: ShellyRPCClient, em_id: int = 0, ts: int | None = None) -> dict[str, Any]:
    params: dict[str, Any] = {'id': em_id}
    if ts is not None:
        params['ts'] = ts
    return client.call('EM1Data.GetData', **params)


def download_rows(client: ShellyRPCClient, em_id: int = 0, max_pages: int = 200) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    record_blocks = get_records(client, em_id)
    start_times = [int(item['ts']) for item in record_blocks if int(item.get('ts', 0)) < 4000000000]

    for start_ts in start_times:
        ts = start_ts
        for _ in range(max_pages):
            payload = get_data(client, em_id, ts)
            keys = payload.get('keys', HISTORY_KEYS)
            for block in payload.get('data', []):
                block_ts = int(block.get('ts', ts))
                period = int(block.get('period', 60))
                for index, values in enumerate(block.get('values', [])):
                    row = {'ts': block_ts + index * period, 'period': period}
                    for value_index, key in enumerate(keys):
                        if value_index < len(values):
                            row[key] = values[value_index]
                    rows.append(row)

            next_ts = payload.get('next_record_ts')
            if not next_ts or int(next_ts) <= ts:
                break
            ts = int(next_ts)
    return rows


def export_csv(rows: list[dict[str, Any]], output_path: str) -> int:
    path = Path(output_path)
    fieldnames = ['ts', 'period', *HISTORY_KEYS]
    with path.open('w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)
