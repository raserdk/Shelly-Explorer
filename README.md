# Shelly Explorer

Shelly Explorer is a local diagnostic and exploration toolkit for Shelly Gen2/Gen3/Gen4 devices.

The first target device is **Shelly EM Mini Gen4**, including Wi-Fi, Zigbee firmware and Matter firmware variants.

## Goals

- RPC Explorer
- Modbus Explorer
- Local history downloader
- CSV export
- Device diagnostics
- Home Assistant helper tooling
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

Scan Modbus registers:

```bash
python cli.py 192.168.1.160 modbus-scan --start 2000 --end 2320
```

## Status

Very early development. Tested first against Shelly EM Mini Gen4 firmware `2.0.0`.
