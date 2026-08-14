# Shelly Explorer

Shelly Explorer is a local diagnostic and exploration toolkit for Shelly Gen2/Gen3/Gen4 energy meters.

It currently targets:

- **Shelly EM Mini Gen4** / `S4EM-001PXCEU16`
- **Shelly 3EM-63 Gen3** / `S3EM-003CXCEU63`

![Shelly EM Modbus logo](docs/assets/shelly-em-mini-modbus-logo.svg)

## Home Assistant custom integration

This repository includes a HACS-compatible Home Assistant custom integration for Shelly energy meters over local Modbus TCP, with optional RPC reads for values that are not exposed through Modbus.

Integration path:

```text
custom_components/shelly_em_mini_modbus
```

HACS custom repository:

```text
https://github.com/raserdk/Shelly-Explorer
```

HACS category:

```text
Integration
```

Manual install path:

```text
/config/custom_components/shelly_em_mini_modbus
```

After installation, restart Home Assistant and add:

```text
Settings -> Devices & services -> Add integration -> Shelly EM Modbus
```

The integration supports:

- manual IP setup
- network scan/discovery
- marking already configured meters in discovery results
- local Modbus TCP polling without YAML
- model-specific sensor profiles
- EM Mini Gen4 support
- 3EM-63 Gen3 support
- kWh sensors beside Wh sensors
- unsupported Modbus registers handled per sensor instead of failing the whole device
- internal 3EM temperature via RPC `Temperature.GetStatus?id=0`

Full integration notes:

```text
docs/hacs-integration.md
```

Changelog:

```text
CHANGELOG.md
```

## Supported Home Assistant sensors

### Shelly EM Mini Gen4

Verified on real devices with firmware `2.0.0`, including Wi-Fi/Zigbee/Matter firmware variants.

Sensors:

- Effekt
- Spænding
- Strøm
- Frekvens
- Energi
- Energi kWh
- Returneret energi
- Returneret energi kWh

Verified Modbus addresses used by the integration:

| Shelly address | Integration address | Value |
| ---: | ---: | --- |
| 32003 | 2003 | Voltage |
| 32005 | 2005 | Current |
| 32007 | 2007 | Active power |
| 32016 | 2016 | Frequency |
| 32310 | 2310 | Perpetual active energy |
| 32312 | 2312 | Perpetual returned energy |

### Shelly 3EM-63 Gen3

Verified on real device model `S3EM-003CXCEU63`, app `3EMG3`, firmware `2.0.0`.

Sensors:

- Total strøm
- Total effekt
- Total apparent power
- Total energi
- Total energi kWh
- Total returneret energi
- Total returneret energi kWh
- Fase A/B/C spænding
- Fase A/B/C strøm
- Fase A/B/C effekt
- Fase A/B/C apparent power
- Fase A/B/C power factor
- Intern temperatur

Verified Modbus addresses used by the integration:

| Shelly address | Integration address | Value |
| ---: | ---: | --- |
| 31011 | 1011 | Total current |
| 31013 | 1013 | Total active power |
| 31015 | 1015 | Total apparent power |
| 31020 | 1020 | Phase A voltage |
| 31022 | 1022 | Phase A current |
| 31024 | 1024 | Phase A active power |
| 31026 | 1026 | Phase A apparent power |
| 31028 | 1028 | Phase A power factor |
| 31040 | 1040 | Phase B voltage |
| 31042 | 1042 | Phase B current |
| 31044 | 1044 | Phase B active power |
| 31046 | 1046 | Phase B apparent power |
| 31048 | 1048 | Phase B power factor |
| 31060 | 1060 | Phase C voltage |
| 31062 | 1062 | Phase C current |
| 31064 | 1064 | Phase C active power |
| 31066 | 1066 | Phase C apparent power |
| 31068 | 1068 | Phase C power factor |
| 31162 | 1162 | Total active energy |
| 31164 | 1164 | Total returned active energy |

Important 3EM note:

- `31080`, `31082`, and `31084` returned `Modbus exception 2` on the tested 3EM-63 Gen3 firmware `2.0.0`.
- The working total registers are `31011`, `31013`, and `31015`.
- Internal temperature is not read through Modbus. It is read through RPC:

```text
/rpc/Temperature.GetStatus?id=0
```

Expected RPC response:

```json
{"id": 0, "tC": 56.5, "tF": 133.8}
```

## Modbus addressing note

Shelly documents Modbus addresses as `3xxxx` input registers.

The integration and the Python tools use:

```text
integration address = Shelly documented address - 30000
```

Examples:

```text
32007 -> 2007
31020 -> 1020
31162 -> 1162
```

The devices use input registers and float32 word-swapped decoding.

## CLI toolkit

The repository also contains command-line tools for exploring Shelly devices locally.

Install:

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

Download local history to CSV:

```bash
python cli.py 192.168.1.160 history --out history.csv
```

Test Modbus TCP:

```bash
python cli.py 192.168.1.160 modbus-test
```

Show known EM Mini Modbus registers:

```bash
python cli.py 192.168.1.160 modbus-known
```

Compare RPC live values against Modbus register values:

```bash
python cli.py 192.168.1.160 compare
```

Scan Modbus registers:

```bash
python cli.py 192.168.1.160 modbus-scan --start 2000 --end 2320
```

Scan the local network for Shelly devices:

```bash
python cli.py 192.168.1.1 scan-devices --subnet 192.168.1.0/24
```

Show only EM-capable devices during network scan:

```bash
python cli.py 192.168.1.1 scan-devices --subnet 192.168.1.0/24 --em-only
```

The `host` argument is still required by the shared CLI parser. For `scan-devices`, it is currently unused, so any placeholder IP can be passed, for example `192.168.1.1`.

## Home Assistant YAML helper tooling

The custom integration is now the preferred Home Assistant setup, but the repo still includes YAML helper tools.

Generate Home Assistant Modbus YAML for one EM Mini device:

```bash
python cli.py 192.168.1.160 ha-yaml --name "Gruppe 1" --out gruppe1.yaml
```

Generate Home Assistant Modbus YAML for all EM-capable devices on a subnet:

```bash
python cli.py 192.168.1.1 ha-yaml-scan --subnet 192.168.1.0/24 --out shelly_modbus.yaml
```

Use a name mapping file if you want real group names instead of IP-based names:

```yaml
192.168.1.160: Gruppe 1
192.168.1.161: Gruppe 2
192.168.1.162: Gruppe 3
```

Then pass it with `--names`:

```bash
python cli.py 192.168.1.1 ha-yaml-scan --subnet 192.168.1.0/24 --names shelly_names.yaml --out shelly_modbus.yaml
```

You can also let Shelly Explorer create the first names file from a scan:

```bash
python cli.py 192.168.1.1 ha-yaml-scan --subnet 192.168.1.0/24 --timeout 4 --write-names shelly_names.yaml --out shelly_modbus.yaml
```

## Goals

- RPC Explorer
- Modbus Explorer
- Network device scanner
- RPC vs Modbus comparison
- Local history downloader
- CSV export
- Device diagnostics
- Home Assistant YAML helper tooling
- Home Assistant custom/HACS integration
- Zigbee / Matter / Wi-Fi comparison

## Current status

Current integration version: `0.2.5`.

Verified:

- Shelly EM Mini Gen4 Modbus live values
- Shelly EM Mini Gen4 local history export
- Shelly EM Mini Gen4 RPC vs Modbus comparison
- Shelly 3EM-63 Gen3 Modbus live values
- Shelly 3EM-63 Gen3 internal temperature via RPC
- Subnet scanning for Shelly energy meters
- EM-only filtering for network scans
- Home Assistant Modbus YAML generation
- Home Assistant custom integration with manual setup and Modbus discovery
- HACS custom repository install

## License

This project is licensed under the MIT License.

You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software, as long as the copyright and license notice are kept with the software.

See [LICENSE](LICENSE) for the full license text.
