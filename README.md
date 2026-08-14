# Shelly Explorer

Shelly Explorer is a local diagnostic and exploration toolkit for Shelly Gen2/Gen3/Gen4 devices.

The first target device is **Shelly EM Mini Gen4**, including Wi-Fi, Zigbee firmware and Matter firmware variants.

![Shelly EM Mini Modbus logo](docs/assets/shelly-em-mini-modbus-logo.svg)

## Home Assistant custom integration

This repository includes an early HACS-compatible Home Assistant custom integration for Shelly EM Mini Gen4 over local Modbus TCP.

Integration path:

```text
custom_components/shelly_em_mini_modbus
```

Manual install:

```text
/config/custom_components/shelly_em_mini_modbus
```

After copying the integration folder, restart Home Assistant and add:

```text
Settings -> Devices & services -> Add integration -> Shelly EM Mini Modbus
```

The integration supports:

- manual IP setup
- network scan/discovery
- marking already configured meters in discovery results
- local Modbus TCP polling without YAML
- sensors for power, voltage, current, frequency, energy and returned energy

Full integration notes are here:

```text
docs/hacs-integration.md
```

## Goals

- RPC Explorer
- Modbus Explorer
- Network device scanner
- RPC vs Modbus comparison
- Local history downloader
- CSV export
- Device diagnostics
- Home Assistant helper tooling
- Home Assistant custom integration
- Zigbee / Matter / Wi-Fi comparison

## What we already verified on Shelly EM Mini Gen4

Shelly EM Mini Gen4 exposes a local RPC API with:

- `Shelly.GetDeviceInfo`
- `Shelly.GetStatus`
- `Shelly.GetComponents`
- `Shelly.ListMethods`
- `EM1.GetStatus`
- `EM1Data.GetStatus`
- `EM1Data.GetRecords`
- `EM1Data.GetData`
- `EM1Data.GetNetEnergies`
- `Modbus.GetConfig`
- `Modbus.GetStatus`

The device stores local 1-minute history blocks through `EM1Data.GetData`.

Known history fields:

- `total_act_energy`
- `total_act_ret_energy`
- `lag_react_energy`
- `lead_react_energy`
- `max_act_power`
- `min_act_power`
- `max_aprt_power`
- `min_aprt_power`
- `max_voltage`
- `min_voltage`
- `avg_voltage`
- `max_current`
- `min_current`
- `avg_current`

## Verified Modbus support

Shelly EM Mini Gen4 exposes documented EM1 and EM1Data values over Modbus TCP.

Verified on real devices:

- Shelly EM Mini Gen4 with Zigbee firmware, firmware `2.0.0`
- Shelly EM Mini Gen4 with Matter firmware, firmware `2.0.0`

Important addressing note:

```text
pymodbus address = Shelly documented Modbus address - 30000
```

Examples:

| Shelly address | pymodbus address | Value |
| ---: | ---: | --- |
| 32000 | 2000 | EM1 timestamp |
| 32003 | 2003 | EM1 voltage |
| 32005 | 2005 | EM1 current |
| 32007 | 2007 | EM1 active power |
| 32016 | 2016 | EM1 frequency |
| 32302 | 2302 | EM1Data total active energy |
| 32310 | 2310 | EM1Data perpetual active energy |

Energy note:

- `32310` is the total/perpetual active energy counter and matches `EM1Data.GetStatus total_act_energy`.
- `32302` is a shorter period/session-style active energy value and does not match the perpetual total.

The command below prints the known EM1 and EM1Data registers with decoded values:

```bash
python cli.py 192.168.1.160 modbus-known
```

## Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Show device summary:

```bash
python cli.py 192.168.1.160
```

Show RPC methods:

```bash
python cli.py 192.168.1.160 methods
```

Show EM live data:

```bash
python cli.py 192.168.1.160 live
```

Show local history blocks:

```bash
python cli.py 192.168.1.160 records
```

Download all local history to CSV:

```bash
python cli.py 192.168.1.160 history --out history.csv
```

Test Modbus TCP:

```bash
python cli.py 192.168.1.160 modbus-test
```

Show known EM1 and EM1Data Modbus registers:

```bash
python cli.py 192.168.1.160 modbus-known
```

Compare RPC live values against Modbus register values:

```bash
python cli.py 192.168.1.160 compare
```

Example output:

```text
                               RPC vs Modbus
+--------------------------------------------------------------------------+
| Name            | RPC        | Modbus     | Diff         | Unit | Status |
|-----------------+------------+------------+--------------+------+--------|
| Voltage         | 236.2 V    | 236.244 V  | 0.0442017    | V    | OK     |
| Current         | 1.065 A    | 1.06515 A  | 0.000147877  | A    | OK     |
| Active power    | 215.5 W    | 215.512 W  | 0.0118256    | W    | OK     |
| Frequency       | 50 Hz      | 50.025 Hz  | 0.025013     | Hz   | OK     |
| Energy total    | 7781.17 Wh | 7781.17 Wh | -0.000566406 | Wh   | OK     |
| Energy returned | 0 Wh       | 0 Wh       | 0            | Wh   | OK     |
+--------------------------------------------------------------------------+
```

Scan Modbus registers:

```bash
python cli.py 192.168.1.160 modbus-scan --start 2000 --end 2320
```

Scan the local network for Shelly devices:

```bash
python cli.py 192.168.1.1 scan-devices --subnet 192.168.1.0/24
```

The `host` argument is still required by the shared CLI parser. For `scan-devices`, it is currently unused, so any placeholder IP can be passed, for example `192.168.1.1`.

Show only EM-capable devices during network scan:

```bash
python cli.py 192.168.1.1 scan-devices --subnet 192.168.1.0/24 --em-only
```

Example output:

```text
                       Shelly devices on 192.168.1.0/24
+-----------------------------------------------------------------------------+
| IP           | Model             | App      | Version | Modbus | Power     |
|--------------+-------------------+----------+---------+--------+-----------|
| 192.168.1.6  | S4EM-001PXCEU16    | MiniEMG4 | 2.0.0   | OK     | 0.0 W     |
| 192.168.1.20 | S4EM-001PXCEU16    | MiniEMG4 | 2.0.0   | OK     | 349.0 W   |
| 192.168.1.85 | S4EM-001PXCEU16    | MiniEMG4 | 2.0.0   | OK     | 109.0 W   |
+-----------------------------------------------------------------------------+
```

Generate Home Assistant Modbus YAML for one device:

```bash
python cli.py 192.168.1.160 ha-yaml --name "Gruppe 1" --out gruppe1.yaml
```

Generate Home Assistant Modbus YAML for all EM-capable devices on a subnet:

```bash
python cli.py 192.168.1.1 ha-yaml-scan --subnet 192.168.1.0/24 --out shelly_modbus.yaml
```

Use a name mapping file if you want real group names instead of IP-based names. Create a UTF-8 text file, for example `shelly_names.yaml`:

```yaml
192.168.1.160: Gruppe 1
192.168.1.161: Gruppe 2
192.168.1.162: Gruppe 3
```

Then pass it with `--names`:

```bash
python cli.py 192.168.1.1 ha-yaml-scan --subnet 192.168.1.0/24 --names shelly_names.yaml --out shelly_modbus.yaml
```

Devices that are not listed in the name mapping file still get IP-based names.

You can also let Shelly Explorer create the first names file from a scan:

```bash
python cli.py 192.168.1.1 ha-yaml-scan --subnet 192.168.1.0/24 --timeout 4 --write-names shelly_names.yaml --out shelly_modbus.yaml
```

This writes `shelly_names.yaml` with generated names:

```yaml
192.168.1.6: Gruppe 1
192.168.1.19: Gruppe 2
192.168.1.48: Gruppe 3
```

If the names file already exists, it is not overwritten unless you add `--force`.

Example generated Home Assistant YAML for one group:

```yaml
modbus:
  - name: shelly_em_gruppe_1
    type: tcp
    host: 192.168.1.160
    port: 502
    sensors:
      - name: "Gruppe 1 Effekt"
        unique_id: gruppe_1_power
        input_type: input
        address: 2007
        data_type: float32
        swap: word
        unit_of_measurement: "W"
        device_class: power
        state_class: measurement
      - name: "Gruppe 1 Spænding"
        unique_id: gruppe_1_voltage
        input_type: input
        address: 2003
        data_type: float32
        swap: word
        unit_of_measurement: "V"
        device_class: voltage
        state_class: measurement
      - name: "Gruppe 1 Strøm"
        unique_id: gruppe_1_current
        input_type: input
        address: 2005
        data_type: float32
        swap: word
        unit_of_measurement: "A"
        device_class: current
        state_class: measurement
      - name: "Gruppe 1 Frekvens"
        unique_id: gruppe_1_frequency
        input_type: input
        address: 2016
        data_type: float32
        swap: word
        unit_of_measurement: "Hz"
        device_class: frequency
        state_class: measurement
      - name: "Gruppe 1 Energi"
        unique_id: gruppe_1_energy
        input_type: input
        address: 2310
        data_type: float32
        swap: word
        unit_of_measurement: "Wh"
        device_class: energy
        state_class: total_increasing
      - name: "Gruppe 1 Returneret energi"
        unique_id: gruppe_1_returned_energy
        input_type: input
        address: 2312
        data_type: float32
        swap: word
        unit_of_measurement: "Wh"
        device_class: energy
        state_class: total_increasing
```

If `ha-yaml-scan` does not find any EM-capable Shelly devices, it does not write an empty `modbus:` file. Instead it prints:

```text
No EM-capable Shelly devices found
```

## Status

Very early development. Tested first against Shelly EM Mini Gen4 firmware `2.0.0`.

Currently verified:

- RPC live reads
- Local history export
- Known EM1 and EM1Data Modbus register decoding
- RPC vs Modbus comparison
- Subnet scanning for Shelly devices
- EM-only filtering for network scans
- Home Assistant Modbus YAML generation
- Home Assistant custom integration with manual setup and Modbus discovery
