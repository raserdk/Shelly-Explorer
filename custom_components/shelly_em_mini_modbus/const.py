from __future__ import annotations

DOMAIN = "shelly_em_mini_modbus"
DEFAULT_NAME = "Shelly EM Mini"
DEFAULT_PORT = 502
DEFAULT_SCAN_INTERVAL = 10

CONF_HOST = "host"
CONF_NAME = "name"
CONF_PORT = "port"

SENSOR_DEFINITIONS = [
    ("Effekt", "power", 2007, "W", "power", "measurement"),
    ("Spænding", "voltage", 2003, "V", "voltage", "measurement"),
    ("Strøm", "current", 2005, "A", "current", "measurement"),
    ("Frekvens", "frequency", 2016, "Hz", "frequency", "measurement"),
    ("Energi", "energy", 2310, "Wh", "energy", "total_increasing"),
    ("Returneret energi", "returned_energy", 2312, "Wh", "energy", "total_increasing"),
]
