from __future__ import annotations

import socket
import struct
from itertools import count
from typing import Final

MODBUS_UNIT_ID: Final = 1
MODBUS_FUNCTION_READ_INPUT_REGISTERS: Final = 4

_transaction_ids = count(1)


class ModbusError(Exception):
    """Raised when a Modbus request fails."""


class ShellyEmMiniModbusClient:
    """Small Modbus TCP client for Shelly EM Mini Gen4.

    The device responds to input registers and appears to ignore unit id,
    but unit id 1 is used consistently.
    """

    def __init__(self, host: str, port: int = 502, timeout: float = 3.0) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout

    def read_input_registers(self, address: int, count_: int) -> list[int]:
        transaction_id = next(_transaction_ids) & 0xFFFF
        request = struct.pack(
            ">HHHBBHH",
            transaction_id,
            0,
            6,
            MODBUS_UNIT_ID,
            MODBUS_FUNCTION_READ_INPUT_REGISTERS,
            address,
            count_,
        )

        with socket.create_connection((self.host, self.port), timeout=self.timeout) as sock:
            sock.settimeout(self.timeout)
            sock.sendall(request)
            header = self._recv_exact(sock, 7)
            response_transaction_id, protocol_id, length, _unit_id = struct.unpack(">HHHB", header)
            if response_transaction_id != transaction_id:
                raise ModbusError("Unexpected Modbus transaction id")
            if protocol_id != 0:
                raise ModbusError("Unexpected Modbus protocol id")

            pdu = self._recv_exact(sock, length - 1)

        function_code = pdu[0]
        if function_code & 0x80:
            exception_code = pdu[1] if len(pdu) > 1 else None
            raise ModbusError(f"Modbus exception {exception_code}")
        if function_code != MODBUS_FUNCTION_READ_INPUT_REGISTERS:
            raise ModbusError("Unexpected Modbus function code")

        byte_count = pdu[1]
        payload = pdu[2 : 2 + byte_count]
        if len(payload) != count_ * 2:
            raise ModbusError("Unexpected Modbus payload length")

        return list(struct.unpack(f">{count_}H", payload))

    def read_float32_cdab(self, address: int) -> float:
        registers = self.read_input_registers(address, 2)
        raw = struct.pack(">HH", registers[1], registers[0])
        return struct.unpack(">f", raw)[0]

    @staticmethod
    def _recv_exact(sock: socket.socket, size: int) -> bytes:
        chunks = bytearray()
        while len(chunks) < size:
            chunk = sock.recv(size - len(chunks))
            if not chunk:
                raise ModbusError("Connection closed while reading Modbus response")
            chunks.extend(chunk)
        return bytes(chunks)
