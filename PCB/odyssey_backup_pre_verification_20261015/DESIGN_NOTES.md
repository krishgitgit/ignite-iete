# AuraPump electrical interface schematic

`odyssey.kicad_sch` is a first-pass, module-level electrical circuit for the AuraPump controller carrier. It replaces the earlier boxes-only architecture page. The schematic includes connector, resistor, transistor and power symbols with named electrical nets. A KiCad-rendered preview is `preview/odyssey.svg`; the exported connectivity list is `odyssey.net`.

## Circuit summary

- J1/J2 are the carrier headers for a common 30-pin ESP32 DevKit V1 arrangement. ADC1 channels GPIO34/35/32/33/36 read ACS712, low-voltage DC, soil moisture, TDS and turbidity. GPIO21/22 connect an I2C OLED; GPIO4 connects DS18B20 data; GPIO26 commands the relay module; GPIO27 reads conditioned flow pulses.
- J12 accepts regulated external 5 V for ESP32 VIN and 5 V modules. ESP32 3V3 powers the soil sensor, DS18B20 pull-up and OLED interface.
- R1–R8 form four 15 kΩ / 20 kΩ dividers using 1% resistors. A confirmed 0–5 V module output maps to 0–2.86 V nominal and below 2.9 V worst-case tolerance. Do not connect an output above 5 V without recalculating. The attenuation also reduces sensor resolution, especially for ACS712.
- R9 is the 4.7 kΩ DS18B20 pull-up.
- R10–R13 and Q1 form an NPN flow-pulse conditioner with 5 V sensor-side and 3.3 V MCU-side pull-ups. The output pulse is inverted in firmware.
- J11 is only the low-voltage relay-module interface. Pump switching must use an appropriately rated external contactor and motor protection. No mains path is routed on this controller PCB.

## Assumptions to verify before board layout

- The component list says “ESP32 Dev Kit” without a model. J1/J2 use a common 30-pin DevKit V1 signal mapping as a draft only. ADC channels connect to J1 pins 3/5/6/7/8; flow/relay to J1 pins 11/10; and I2C/temperature to J2 pins 4/7/14. Verify every pin, supply, ground, connector order and orientation against the exact board. J1/J2 footprints are deliberately blank until then.
- Verify each module's output range and supply requirements. Divider channels assume outputs never exceed 5 V. TDS divider loading may reduce ADC resolution; recalibrate with the actual modules.
- Verify the soil-moisture and OLED modules work at 3.3 V. Check whether the OLED already has I2C pull-ups.
- Flow conditioner: R10 4.7 kΩ base resistor; R11 100 kΩ base pull-down; Q1 emitter to GND; collector to FLOW_GPIO with R13 10 kΩ pull-up to 3V3; R12 10 kΩ pulls the flow input to 5 V. This inverts the pulse. Verify sensor output type/current and firmware polarity. Q1 footprint is blank pending exact package pinout.
- The voltage module is for isolated low-voltage DC measurement only. Never connect mains to this circuit.
- ACS712-05B datasheet nominal: 2.5 V zero-current output and 185 mV/A. Nominal ±5 A gives 1.575–3.425 V, mapped to ~0.90–1.96 V by this divider. That is within range but uses only ~1.06 V ADC span; calibrate and verify the module variant plus pump RMS/startup current before relying on it.
- Relay active-high/active-low behavior is unknown, so RELAY_IN has no default bias. Its state during ESP32 reset is not guaranteed. Verify the exact module and add the correct inactive-state bias/interface before operating it. Confirm contact rating, pump startup current and protection.
- Q1's PCB footprint is intentionally unassigned: choose the exact transistor and verify its package pinout before layout.
- Added parts beyond the supplied modules: eight 0805 1% divider resistors (four 15 kΩ and four 20 kΩ), one 4.7 kΩ DS18B20 pull-up, flow-conditioning resistors (4.7 kΩ, 100 kΩ, two 10 kΩ), and one NPN transistor. Total: R1–R13 plus Q1.

## Source documents reviewed

- `../project-brief.md`
- `../hardware-flow-explained.md`
- `../hardware-flowchart-prompt.md`
- `../software-flowchart-prompt.md`
- `../Hackathon Component List.docx`
- `../README.md`
