from __future__ import annotations

import argparse
import json
from typing import Any

from rich.console import Console
from rich.table import Table

from shelly_explorer.device import ShellyDevice
from shelly_explorer.history import download_rows, export_csv, get_records
from shelly_explorer.modbus import ShellyModbusScanner, describe_register, is_port_open
from shelly_explorer.rpc import ShellyRPCClient

console = Console()


def print_dict(title: str, data: dict[str, Any]) -> None:
    table = Table(title=title)
    table.add_column('Key')
    table.add_column('Value')
    for key, value in data.items():
        table.add_row(str(key), str(value))
    console.print(table)


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
    console.print(f'Slave IDs found: {slaves}')


def cmd_modbus_scan(args: argparse.Namespace) -> None:
    scanner = ShellyModbusScanner(args.host, port=args.port)
    if args.kind == 'input':
        found = scanner.scan_input_range(args.start, args.end, slave=args.slave)
    else:
        found = scanner.scan_holding_range(args.start, args.end, slave=args.slave)

    table = Table(title=f'Modbus {args.kind} registers {args.start}-{args.end}')
    table.add_column('Address')
    table.add_column('Registers')
    table.add_column('uint16')
    table.add_column('float32 ABCD')
    table.add_column('float32 CDAB')
    for item in found:
        decoded = describe_register(item)
        table.add_row(
            str(decoded['address']),
            str(decoded['registers']),
            str(decoded['uint16']),
            f'{decoded["float32_abcd"]:.6g}' if decoded['float32_abcd'] is not None else '',
            f'{decoded["float32_cdab"]:.6g}' if decoded['float32_cdab'] is not None else '',
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
    modbus_scan.add_argument('--kind', choices=['input', 'holding'], default='input')
    modbus_scan.add_argument('--start', type=int, default=30000)
    modbus_scan.add_argument('--end', type=int, default=32400)

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
    else:
        parser.error(f'Unknown command: {command}')


if __name__ == '__main__':
    main()
