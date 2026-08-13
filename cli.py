from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from typing import Any

from rich.console import Console
from rich.table import Table

from shelly_explorer.device import ShellyDevice
from shelly_explorer.history import download_rows, export_csv, get_records
from shelly_explorer.modbus import RegisterValue, ShellyModbusScanner, describe_register, is_port_open
from shelly_explorer.registers import COMPARE_REGISTERS, KNOWN_MODBUS_REGISTERS, MODBUS_OFFSET
from shelly_explorer.rpc import ShellyRPCClient

console = Console()


def print_dict(title: str, data: dict[str, Any]) -> None:
    table = Table(title=title)
    table.add_column('Key')
    table.add_column('Value')
    for key, value in data.items():
        table.add_row(str(key), str(value))
    console.print(table)


def print_modbus_table(title: str, found: list[Any]) -> None:
    table = Table(title=title)
    table.add_column('Address')
    table.add_column('Shelly address')
    table.add_column('Registers')
    table.add_column('uint16')
    table.add_column('float32 ABCD')
    table.add_column('float32 CDAB')
    for item in found:
        decoded = describe_register(item)
        table.add_row(
            str(decoded['address']),
            str(decoded['address'] + MODBUS_OFFSET),
            str(decoded['registers']),
            str(decoded['uint16']),
            f'{decoded["float32_abcd"]:.6g}' if decoded['float32_abcd'] is not None else '',
            f'{decoded["float32_cdab"]:.6g}' if decoded['float32_cdab'] is not None else '',
        )
    console.print(table)


def uint32_cdab(registers: list[int]) -> int | None:
    if len(registers) < 2:
        return None
    return (registers[1] << 16) + registers[0]


def known_value(registers: list[int], decoded: dict[str, Any], datatype: str) -> Any:
    if datatype == 'uint32_cdab':
        return uint32_cdab(registers)
    if datatype == 'uint32':
        return decoded['uint32']
    if datatype == 'uint16':
        return decoded['uint16']
    return decoded[datatype]


def format_known_value(value: Any, datatype: str) -> str:
    if value is None:
        return ''
    if datatype == 'uint32_cdab' and isinstance(value, int):
        try:
            iso = datetime.fromtimestamp(value, tz=timezone.utc).isoformat()
            return f'{value} / {iso}'
        except (OverflowError, OSError, ValueError):
            return str(value)
    if isinstance(value, float):
        if math.isnan(value):
            return 'N/A'
        return f'{value:.6g}'
    return str(value)


def format_compare_value(value: Any, unit: str) -> str:
    if value is None:
        return ''
    if isinstance(value, float) and math.isnan(value):
        return 'N/A'
    if isinstance(value, (int, float)):
        return f'{value:.6g} {unit}'.strip()
    return str(value)


def compare_status(rpc_value: Any, modbus_value: Any, tolerance: float) -> tuple[str, str]:
    if rpc_value is None or modbus_value is None:
        return '', '[red]MISSING[/red]'
    if isinstance(rpc_value, float) and math.isnan(rpc_value):
        return '', '[yellow]N/A[/yellow]'
    if isinstance(modbus_value, float) and math.isnan(modbus_value):
        return '', '[yellow]N/A[/yellow]'

    diff = float(modbus_value) - float(rpc_value)
    status = '[green]OK[/green]' if abs(diff) <= tolerance else '[red]DIFF[/red]'
    return f'{diff:.6g}', status


def _rpc_number(payload: dict[str, Any], key: str) -> float | int | None:
    value = payload.get(key)
    return value if isinstance(value, (int, float)) else None


def read_known_modbus_value(
    scanner: ShellyModbusScanner,
    shelly_address: int,
    datatype: str,
    slave: int,
) -> Any:
    address = shelly_address - MODBUS_OFFSET
    registers = scanner.read_input(address, count=2, slave=slave)
    if registers is None:
        return None
    decoded = describe_register(RegisterValue(address=address, registers=registers))
    return known_value(registers, decoded, datatype)


def cmd_summary(args: argparse.Namespace) -> None:
    device = ShellyDevice(args.host)
    print_dict('Shelly Explorer - Summary', device.summary())


def cmd_live(args: argparse.Namespace) -> None:
    device = ShellyDevice(args.host)
    print_dict('EM1 Live', device.em_status(args.id))
    print_dict('EM1Data Live', device.em_data_status(args.id))


def cmd_methods(args: argparse.Namespace) -> None:
    client = ShellyRPCClient(args.host)
    methods = client.list_methods()
    table = Table(title=f'RPC methods ({len(methods)})')
    table.add_column('Method')
    for method in methods:
        table.add_row(method)
    console.print(table)


def cmd_records(args: argparse.Namespace) -> None:
    client = ShellyRPCClient(args.host)
    records = get_records(client, args.id)
    table = Table(title='History record blocks')
    table.add_column('ts')
    table.add_column('period')
    table.add_column('records')
    for item in records:
        table.add_row(str(item.get('ts')), str(item.get('period')), str(item.get('records')))
    console.print(table)


def cmd_history(args: argparse.Namespace) -> None:
    client = ShellyRPCClient(args.host)
    rows = download_rows(client, em_id=args.id, max_pages=args.max_pages)
    count = export_csv(rows, args.out)
    console.print(f'[green]Exported {count} rows to {args.out}[/green]')


def cmd_modbus_test(args: argparse.Namespace) -> None:
    open_ = is_port_open(args.host, args.port)
    console.print(f'Port {args.port}: ' + ('[green]open[/green]' if open_ else '[red]closed[/red]'))
    if not open_:
        return
    scanner = ShellyModbusScanner(args.host, port=args.port)
    slaves = scanner.scan_slave_ids(args.slave_start, args.slave_end)
    if len(slaves) > 1:
        console.print(f'Slave IDs responding: {slaves}')
        console.print('[yellow]Device appears to ignore unit id. Using slave/device id 1 by default.[/yellow]')
    else:
        console.print(f'Slave IDs found: {slaves}')


def cmd_modbus_scan(args: argparse.Namespace) -> None:
    scanner = ShellyModbusScanner(args.host, port=args.port)

    if args.kind in {'input', 'both'}:
        input_found = scanner.scan_input_range(args.start, args.end, slave=args.slave)
        print_modbus_table(f'Modbus input registers {args.start}-{args.end}', input_found)

    if args.kind in {'holding', 'both'}:
        holding_found = scanner.scan_holding_range(args.start, args.end, slave=args.slave)
        print_modbus_table(f'Modbus holding registers {args.start}-{args.end}', holding_found)


def cmd_modbus_known(args: argparse.Namespace) -> None:
    scanner = ShellyModbusScanner(args.host, port=args.port)
    table = Table(title='Known Shelly Modbus input registers')
    table.add_column('Name')
    table.add_column('Shelly address')
    table.add_column('pymodbus address')
    table.add_column('Raw')
    table.add_column('Value')
    table.add_column('Unit')

    for shelly_address, name, datatype, unit in KNOWN_MODBUS_REGISTERS:
        address = shelly_address - MODBUS_OFFSET
        registers = scanner.read_input(address, count=2, slave=args.slave)
        if registers is None:
            table.add_row(name, str(shelly_address), str(address), 'no response', '', unit)
            continue
        decoded = describe_register(RegisterValue(address=address, registers=registers))
        value = known_value(registers, decoded, datatype)
        table.add_row(
            name,
            str(shelly_address),
            str(address),
            str(registers),
            format_known_value(value, datatype),
            unit,
        )

    console.print(table)


def cmd_compare(args: argparse.Namespace) -> None:
    device = ShellyDevice(args.host)
    scanner = ShellyModbusScanner(args.host, port=args.port)
    em = device.em_status(args.id)
    emdata = device.em_data_status(args.id)
    rpc_sources = {'em1': em, 'em1data': emdata}

    table = Table(title='RPC vs Modbus')
    table.add_column('Name')
    table.add_column('RPC')
    table.add_column('Modbus')
    table.add_column('Diff')
    table.add_column('Unit')
    table.add_column('Status')

    for name, shelly_address, rpc_key, source, datatype, unit, tolerance in COMPARE_REGISTERS:
        rpc_value = _rpc_number(rpc_sources[source], rpc_key)
        modbus_value = read_known_modbus_value(scanner, shelly_address, datatype, args.slave)
        diff, status = compare_status(rpc_value, modbus_value, tolerance)
        table.add_row(
            name,
            format_compare_value(rpc_value, unit),
            format_compare_value(modbus_value, unit),
            diff,
            unit,
            status,
        )

    console.print(table)


def cmd_rpc(args: argparse.Namespace) -> None:
    client = ShellyRPCClient(args.host)
    params: dict[str, Any] = {}
    for raw in args.param or []:
        key, _, value = raw.partition('=')
        if value.isdigit():
            params[key] = int(value)
        elif value.lower() in {'true', 'false'}:
            params[key] = value.lower() == 'true'
        else:
            params[key] = value
    payload = client.call(args.method, **params)
    console.print_json(json.dumps(payload, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Shelly Explorer')
    parser.add_argument('host', help='Shelly IP address or hostname')
    sub = parser.add_subparsers(dest='command')

    sub.add_parser('summary')

    live = sub.add_parser('live')
    live.add_argument('--id', type=int, default=0)

    sub.add_parser('methods')

    records = sub.add_parser('records')
    records.add_argument('--id', type=int, default=0)

    history = sub.add_parser('history')
    history.add_argument('--id', type=int, default=0)
    history.add_argument('--out', default='shelly_history.csv')
    history.add_argument('--max-pages', type=int, default=200)

    rpc = sub.add_parser('rpc')
    rpc.add_argument('method')
    rpc.add_argument('--param', action='append', help='RPC parameter as key=value')

    modbus_test = sub.add_parser('modbus-test')
    modbus_test.add_argument('--port', type=int, default=502)
    modbus_test.add_argument('--slave-start', type=int, default=1)
    modbus_test.add_argument('--slave-end', type=int, default=10)

    modbus_scan = sub.add_parser('modbus-scan')
    modbus_scan.add_argument('--port', type=int, default=502)
    modbus_scan.add_argument('--slave', type=int, default=1)
    modbus_scan.add_argument('--kind', choices=['input', 'holding', 'both'], default='both')
    modbus_scan.add_argument('--start', type=int, default=30000)
    modbus_scan.add_argument('--end', type=int, default=32400)

    modbus_known = sub.add_parser('modbus-known')
    modbus_known.add_argument('--port', type=int, default=502)
    modbus_known.add_argument('--slave', type=int, default=1)

    compare = sub.add_parser('compare')
    compare.add_argument('--id', type=int, default=0)
    compare.add_argument('--port', type=int, default=502)
    compare.add_argument('--slave', type=int, default=1)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    command = args.command or 'summary'
    if command == 'summary':
        cmd_summary(args)
    elif command == 'live':
        cmd_live(args)
    elif command == 'methods':
        cmd_methods(args)
    elif command == 'records':
        cmd_records(args)
    elif command == 'history':
        cmd_history(args)
    elif command == 'rpc':
        cmd_rpc(args)
    elif command == 'modbus-test':
        cmd_modbus_test(args)
    elif command == 'modbus-scan':
        cmd_modbus_scan(args)
    elif command == 'modbus-known':
        cmd_modbus_known(args)
    elif command == 'compare':
        cmd_compare(args)
    else:
        parser.error(f'Unknown command: {command}')


if __name__ == '__main__':
    main()
