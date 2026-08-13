from __future__ import annotations

MODBUS_OFFSET = 30000

KNOWN_MODBUS_REGISTERS = [
    (32000, 'EM1 timestamp', 'uint32_cdab', ''),
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
    (32300, 'EM1Data timestamp', 'uint32_cdab', ''),
    (32302, 'EM1Data total active energy', 'float32_cdab', 'Wh'),
    (32304, 'EM1Data returned energy', 'float32_cdab', 'Wh'),
    (32306, 'EM1Data lag reactive energy', 'float32_cdab', 'VARh'),
    (32308, 'EM1Data lead reactive energy', 'float32_cdab', 'VARh'),
    (32310, 'EM1Data perpetual active energy', 'float32_cdab', 'Wh'),
    (32312, 'EM1Data perpetual returned energy', 'float32_cdab', 'Wh'),
]

COMPARE_REGISTERS = [
    ('Voltage', 32003, 'voltage', 'em1', 'float32_cdab', 'V', 1.0),
    ('Current', 32005, 'current', 'em1', 'float32_cdab', 'A', 0.15),
    ('Active power', 32007, 'act_power', 'em1', 'float32_cdab', 'W', 35.0),
    ('Frequency', 32016, 'freq', 'em1', 'float32_cdab', 'Hz', 0.1),
    ('Energy total', 32310, 'total_act_energy', 'em1data', 'float32_cdab', 'Wh', 1.0),
    ('Energy returned', 32312, 'total_act_ret_energy', 'em1data', 'float32_cdab', 'Wh', 1.0),
]