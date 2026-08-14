# Changelog

All notable changes to the Shelly EM Modbus Home Assistant integration are documented here.

## 0.2.5 - 2026-08-14

- Added Shelly 3EM-63 Gen3 internal temperature sensor.
- Reads temperature from local HTTP RPC `Temperature.GetStatus?id=0` using the `tC` value.
- Keeps electrical values on Modbus and only uses RPC for internal temperature.

## 0.2.4 - 2026-08-14

- Use verified Shelly 3EM-63 Gen3 direct total registers from local Modbus testing.
- Set total current to register `31011` / address `1011`.
- Set total active power to register `31013` / address `1013`.
- Set total apparent power to register `31015` / address `1015`.
- Keep `31080`, `31082`, and `31084` unused because they return Modbus exception 2 on tested 3EM-63 Gen3 firmware 2.0.0.

## 0.2.3 - 2026-08-14

- Changed Shelly 3EM-63 Gen3 total current, total active power, and total apparent power to calculated values from phase A+B+C.
- Avoided unsupported total Modbus registers on 3EM firmware where direct total power/current registers return Modbus exception 2.

## 0.2.2 - 2026-08-14

- Do not fail a full device update when one configured Modbus register returns an exception.
- Unsupported or unreadable registers now return unavailable values for their individual sensors.
- Intended to make Shelly 3EM-63 Gen3 testing safer across firmware/register differences.

## 0.2.1 - 2026-08-14

- Corrected Shelly 3EM-63 Gen3 total current and total active power Modbus registers.
- Added Shelly 3EM-63 Gen3 apparent power sensors for total and each phase.
- Updated 3EM discovery to use the corrected total active power register.

## 0.2.0 - 2026-08-14

- Added initial Shelly 3EM-63 Gen3 support.
- Added model profiles so EM Mini Gen4 and 3EM-63 Gen3 can use different Modbus registers.
- Added automatic discovery of supported model type during scan and manual setup.
- Added 3EM-63 Gen3 total power, total current, total energy, returned energy, and per-phase voltage/current/power/power-factor sensors.
- Renamed the integration display name to Shelly EM Modbus.

## 0.1.3 - 2026-08-14

- Increased the default polling interval from 10 seconds to 30 seconds.
- Increased the Modbus timeout for normal polling.
- Added one retry before a polling update is marked as failed.
- Intended to reduce sporadic Wi-Fi Modbus timeout warnings.

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
