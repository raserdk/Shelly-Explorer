# Shelly EM Mini Modbus Home Assistant integration

<p align="center">
  <img src="assets/shelly-em-mini-modbus-logo.svg" alt="Shelly EM Mini Modbus" width="520">
</p>

This repository includes an early Home Assistant custom integration for Shelly EM Mini Gen4 over local Modbus TCP.

## Manual install

Copy this folder from the repository:

```text
custom_components/shelly_em_mini_modbus
```

into your Home Assistant config folder:

```text
/config/custom_components/shelly_em_mini_modbus
```

Restart Home Assistant.

Then go to:

```text
Settings -> Devices & services -> Add integration
```

Search for:

```text
Shelly EM Mini Modbus
```

## Setup methods

The integration supports two setup methods:

- Scan network
- Manual IP

### Scan network

Use a subnet such as:

```text
192.168.1.0/24
```

The integration probes Modbus TCP port `502` and looks for values that look like an EM Mini meter:

- voltage around 230 V
- frequency around 50 Hz
- active power in W

Discovered devices are shown with their current values and status:

```text
192.168.1.123 - 107 W, 230 V, 50.0 Hz - ny
192.168.1.160 - 157 W, 230 V, 50.0 Hz - konfigureret
```

### Manual IP

Enter the meter IP address manually, for example:

```text
192.168.1.160
```

Give it a friendly name, for example:

```text
Gruppe 1
```

## Sensors

Each configured meter creates these sensors:

- Effekt
- Spænding
- Strøm
- Frekvens
- Energi
- Returneret energi

## Logo assets

The integration includes a small local SVG icon in:

```text
custom_components/shelly_em_mini_modbus/icon.svg
```

A wider documentation logo is available in:

```text
docs/assets/shelly-em-mini-modbus-logo.svg
```

## Notes

This is an early test version. It has been tested with Shelly EM Mini Gen4 firmware `2.0.0` using local Modbus TCP.
