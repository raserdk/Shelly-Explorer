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

Scan Modbus registers:

```bash
python cli.py 192.168.1.160 modbus-scan --start 30000 --end 32400
```

## Status

Very early development. Tested first against Shelly EM Mini Gen4 firmware `2.0.0`.
