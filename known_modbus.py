from __future__ import annotations

import argparse
from rich.console import Console
from rich.table import Table

from shelly_explorer.modbus import RegisterValue, ShellyModbusScanner, describe_register

console = Console()
OFFSET = 30000

REGISTERS = [
    (32000, 'EM1 timestamp', 'uint32', ''),
    (32002, 'EM1 error', 'uint16', ''),
    (32003, 'EM1 voltage', 'float32_cdab', 'V'),
    (32005, 'EM1 current', 'float32_cdab', 'A'),
    (32007, 'EM1 active power', 'float32_cdab', 'W'),
    (32009, 'EM1 apparent power', 'float32_cdab', 'VA'),
    (32011, 'EM1 power factor', 'float32_cdab', ''),
    (32013, 'EM1 overpower error', 'uint16', ''),
    (32014, 'EM1 overvoltage error', 'uint16', ''),
    (32015, 'EM1 overcurrent error', 'uint16', ''),
    (32016, 'EM1 frequency', 'float32_cdab', 'Hz'),
    (32300, 'EM1Data timestamp', 'uint32', ''),
    (32302, 'EM1Data total active energy', 'float32_cdab', 'Wh'),
    (32304, 'EM1Data returned energy', 'float32_cdab', 'Wh'),
    (32306, 'EM1Data lag reactive energy', 'float32_cdab', 'VARh'),
    (32308, 'EM1Data lead reactive energy', 'float32_cdab', 'VARh'),
    (32310, 'EM1Data perpetual active energy', 'float32_cdab', 'Wh'),
    (32312, 'EM1Data perpetual returned energy', 'float32_cdab', 'Wh'),
]


def value_from(decoded: dict, datatype: str):
    if datatype == 'uint32':
        return decoded['uint32']
    if datatype == 'uint16':
        return decoded['uint16']
    return decoded[datatype]


def main() -> None:
    parser = argparse.ArgumentParser(description='Read known Shelly Modbus registers')
    parser.add_argument('host')
    parser.add_argument('--port', type=int, default=502)
    parser.add_argument('--slave', type=int, default=1)
    args = parser.parse_args()

    scanner = ShellyModbusScanner(args.host, port=args.port)
    table = Table(title='Known Shelly Modbus input registers')
    table.add_column('Name')
    table.add_column('Shelly address')
    table.add_column('pymodbus address')
    table.add_column('Raw')
    table.add_column('Value')
    table.add_column('Unit')

    for shelly_address, name, datatype, unit in REGISTERS:
        address = shelly_address - OFFSET
        registers = scanner.read_input(address, count=2, slave=args.slave)
        if registers is None:
            table.add_row(name, str(shelly_address), str(address), 'no response', '', unit)
            continue
        decoded = describe_register(RegisterValue(address=address, registers=registers))
        value = value_from(decoded, datatype)
        if isinstance(value, float):
            value_text = f'{value:.6g}'
        else:
            value_text = str(value)
        table.add_row(name, str(shelly_address), str(address), str(registers), value_text, unit)

    console.print(table)


if __name__ == '__main__':
    main()
