# Changelog

All notable changes to the Shelly EM Mini Modbus Home Assistant integration are documented here.

## 0.1.2 - 2026-08-14

- Added kWh energy sensors beside the existing Wh sensors.
- Added scaling support for sensor definitions.
- Kept existing Wh sensors for compatibility.

## 0.1.1 - 2026-08-14

- Added Danish discovery status labels.
- Added HACS/custom integration install notes.
- Added integration logo and brand assets.
- Updated README with Home Assistant integration information.

## 0.1.0 - 2026-08-14

- Added first Home Assistant custom integration skeleton.
- Added config flow with manual IP setup.
- Added Modbus TCP polling without external Python dependencies.
- Added network discovery via Modbus probing.
- Added configured/new status in discovery results.
- Added sensors for power, voltage, current, frequency, energy, and returned energy.
