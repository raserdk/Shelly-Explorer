from __future__ import annotations

DOMAIN = "shelly_em_mini_modbus"
DEFAULT_NAME = "Shelly EM Mini"
DEFAULT_PORT = 502
DEFAULT_SCAN_INTERVAL = 10

CONF_HOST = "host"
CONF_NAME = "name"
CONF_PORT = "port"

# label, key, Modbus address, unit, device_class, state_class, scale
SENSOR_DEFINITIONS = [
    ("Effekt", "power", 2007, "W", "power", "measurement", 1.0),
    ("Spænding", "voltage", 2003, "V", "voltage", "measurement", 1.0),
    ("Strøm", "current", 2005, "A", "current", "measurement", 1.0),
    ("Frekvens", "frequency", 2016, "Hz", "frequency", "measurement", 1.0),
    ("Energi", "energy", 2310, "Wh", "energy", "total_increasing", 1.0),
    ("Energi kWh", "energy_kwh", 2310, "kWh", "energy", "total_increasing", 0.001),
    ("Returneret energi", "returned_energy", 2312, "Wh", "energy", "total_increasing", 1.0),
    ("Returneret energi kWh", "returned_energy_kwh", 2312, "kWh", "energy", "total_increasing", 0.001),
]
