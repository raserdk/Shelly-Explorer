from __future__ import annotations

import socket
import struct
from dataclasses import dataclass
from typing import Any

from pymodbus.client import ModbusTcpClient


@dataclass(slots=True)
class RegisterValue:
    address: int
    registers: list[int]

    @property
    def uint16(self) -> int | None:
        return self.registers[0] if self.registers else None

    @property
    def int16(self) -> int | None:
        if not self.registers:
            return None
        value = self.registers[0]
        return value - 65536 if value > 32767 else value

    def uint32(self) -> int | None:
        if len(self.registers) < 2:
            return None
        return (self.registers[0] << 16) + self.registers[1]

    def int32(self) -> int | None:
        value = self.uint32()
        if value is None:
            return None
        return value - 4294967296 if value > 2147483647 else value

    def float32_abcd(self) -> float | None:
        if len(self.registers) < 2:
            return None
        raw = struct.pack('>HH', self.registers[0], self.registers[1])
        return struct.unpack('>f', raw)[0]

    def float32_cdab(self) -> float | None:
        if len(self.registers) < 2:
            return None
        raw = struct.pack('>HH', self.registers[1], self.registers[0])
        return struct.unpack('>f', raw)[0]


def is_port_open(host: str, port: int = 502, timeout: float = 2.0) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        return sock.connect_ex((host, port)) == 0


class ShellyModbusScanner:
    def __init__(self, host: str, port: int = 502, timeout: float = 3.0) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout

    def _client(self) -> ModbusTcpClient:
        return ModbusTcpClient(self.host, port=self.port, timeout=self.timeout)

    def read_input(self, address: int, count: int = 2, slave: int = 1) -> list[int] | None:
        client = self._client()
        try:
            client.connect()
            try:
                result = client.read_input_registers(address=address, count=count, slave=slave)
            except TypeError:
                result = client.read_input_registers(address=address, count=count, unit=slave)
            if result.isError():
                return None
            return list(result.registers)
        finally:
            client.close()

    def read_holding(self, address: int, count: int = 2, slave: int = 1) -> list[int] | None:
        client = self._client()
        try:
            client.connect()
            try:
                result = client.read_holding_registers(address=address, count=count, slave=slave)
            except TypeError:
                result = client.read_holding_registers(address=address, count=count, unit=slave)
            if result.isError():
                return None
            return list(result.registers)
        finally:
            client.close()

    def scan_slave_ids(self, start: int = 1, end: int = 10) -> list[int]:
        found: list[int] = []
        for slave in range(start, end + 1):
            if self.read_input(0, count=1, slave=slave) is not None or self.read_holding(0, count=1, slave=slave) is not None:
                found.append(slave)
        return found

    def scan_input_range(self, start: int, end: int, slave: int = 1) -> list[RegisterValue]:
        found: list[RegisterValue] = []
        for address in range(start, end + 1):
            registers = self.read_input(address, count=2, slave=slave)
            if registers is not None:
                found.append(RegisterValue(address=address, registers=registers))
        return found

    def scan_holding_range(self, start: int, end: int, slave: int = 1) -> list[RegisterValue]:
        found: list[RegisterValue] = []
        for address in range(start, end + 1):
            registers = self.read_holding(address, count=2, slave=slave)
            if registers is not None:
                found.append(RegisterValue(address=address, registers=registers))
        return found


def describe_register(value: RegisterValue) -> dict[str, Any]:
    return {
        'address': value.address,
        'registers': value.registers,
        'uint16': value.uint16,
        'int16': value.int16,
        'uint32': value.uint32(),
        'int32': value.int32(),
        'float32_abcd': value.float32_abcd(),
        'float32_cdab': value.float32_cdab(),
    }
