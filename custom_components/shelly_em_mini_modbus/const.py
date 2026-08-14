from __future__ import annotations

DOMAIN = "shelly_em_mini_modbus"
DEFAULT_NAME = "Shelly EM"
DEFAULT_PORT = 502
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_MODBUS_TIMEOUT = 5.0
MODBUS_RETRIES = 1

CONF_HOST = "host"
CONF_NAME = "name"
CONF_PORT = "port"
CONF_MODEL = "model"

MODEL_EM_MINI_GEN4 = "em_mini_gen4"
MODEL_3EM_63_GEN3 = "3em_63_gen3"
DEFAULT_MODEL = MODEL_EM_MINI_GEN4

MODEL_NAMES = {
    MODEL_EM_MINI_GEN4: "EM Mini Gen4",
    MODEL_3EM_63_GEN3: "3EM-63 Gen3",
}

# label, key, Modbus address, unit, device_class, state_class, scale
# Shelly documents Modbus addresses as 3xxxx input registers.
# The client below uses the address without the 30000 prefix.
# Use address None for sensors calculated from other sensor values.
EM_MINI_GEN4_SENSOR_DEFINITIONS = [
    ("Effekt", "power", 2007, "W", "power", "measurement", 1.0),
    ("Spænding", "voltage", 2003, "V", "voltage", "measurement", 1.0),
    ("Strøm", "current", 2005, "A", "current", "measurement", 1.0),
    ("Frekvens", "frequency", 2016, "Hz", "frequency", "measurement", 1.0),
    ("Energi", "energy", 2310, "Wh", "energy", "total_increasing", 1.0),
    ("Energi kWh", "energy_kwh", 2310, "kWh", "energy", "total_increasing", 0.001),
    ("Returneret energi", "returned_energy", 2312, "Wh", "energy", "total_increasing", 1.0),
    ("Returneret energi kWh", "returned_energy_kwh", 2312, "kWh", "energy", "total_increasing", 0.001),
]

THREE_EM_63_GEN3_SENSOR_DEFINITIONS = [
    ("Total strøm", "total_current", None, "A", "current", "measurement", 1.0),
    ("Total effekt", "total_power", None, "W", "power", "measurement", 1.0),
    ("Total apparent power", "total_apparent_power", None, "VA", "apparent_power", "measurement", 1.0),
    ("Total energi", "total_energy", 1162, "Wh", "energy", "total_increasing", 1.0),
    ("Total energi kWh", "total_energy_kwh", 1162, "kWh", "energy", "total_increasing", 0.001),
    ("Total returneret energi", "total_returned_energy", 1164, "Wh", "energy", "total_increasing", 1.0),
    ("Total returneret energi kWh", "total_returned_energy_kwh", 1164, "kWh", "energy", "total_increasing", 0.001),
    ("Fase A spænding", "phase_a_voltage", 1020, "V", "voltage", "measurement", 1.0),
    ("Fase A strøm", "phase_a_current", 1022, "A", "current", "measurement", 1.0),
    ("Fase A effekt", "phase_a_power", 1024, "W", "power", "measurement", 1.0),
    ("Fase A apparent power", "phase_a_apparent_power", 1026, "VA", "apparent_power", "measurement", 1.0),
    ("Fase A power factor", "phase_a_power_factor", 1028, None, "power_factor", "measurement", 1.0),
    ("Fase B spænding", "phase_b_voltage", 1040, "V", "voltage", "measurement", 1.0),
    ("Fase B strøm", "phase_b_current", 1042, "A", "current", "measurement", 1.0),
    ("Fase B effekt", "phase_b_power", 1044, "W", "power", "measurement", 1.0),
    ("Fase B apparent power", "phase_b_apparent_power", 1046, "VA", "apparent_power", "measurement", 1.0),
    ("Fase B power factor", "phase_b_power_factor", 1048, None, "power_factor", "measurement", 1.0),
    ("Fase C spænding", "phase_c_voltage", 1060, "V", "voltage", "measurement", 1.0),
    ("Fase C strøm", "phase_c_current", 1062, "A", "current", "measurement", 1.0),
    ("Fase C effekt", "phase_c_power", 1064, "W", "power", "measurement", 1.0),
    ("Fase C apparent power", "phase_c_apparent_power", 1066, "VA", "apparent_power", "measurement", 1.0),
    ("Fase C power factor", "phase_c_power_factor", 1068, None, "power_factor", "measurement", 1.0),
]

COMPUTED_SUMS_BY_MODEL = {
    MODEL_3EM_63_GEN3: {
        "total_current": ("phase_a_current", "phase_b_current", "phase_c_current"),
        "total_power": ("phase_a_power", "phase_b_power", "phase_c_power"),
        "total_apparent_power": (
            "phase_a_apparent_power",
            "phase_b_apparent_power",
            "phase_c_apparent_power",
        ),
    }
}

SENSOR_DEFINITIONS_BY_MODEL = {
    MODEL_EM_MINI_GEN4: EM_MINI_GEN4_SENSOR_DEFINITIONS,
    MODEL_3EM_63_GEN3: THREE_EM_63_GEN3_SENSOR_DEFINITIONS,
}

# Backwards-compatible alias used by the CLI/YAML helpers and older code.
SENSOR_DEFINITIONS = EM_MINI_GEN4_SENSOR_DEFINITIONS
