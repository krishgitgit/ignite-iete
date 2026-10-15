# AuraPump KiCad verification report

## Scope and backup

- Corrected source: `odyssey.kicad_sch`.
- Baseline copy taken before these verification edits: `../odyssey_backup_pre_verification_20261015/`.
- The prior architecture-only concept remains separately stored as `odyssey_architecture.kicad_sch`.
- `odyssey.kicad_pcb` was inspected and contains only an empty KiCad board shell. It was left untouched because the carrier/connector geometry, relay module, and pump supply are not finalized.

## GPIO map implemented

All analog assignments use classic ESP32 ADC1 pins. The table reflects the requested signal allocation on the common 30-pin ESP32-WROOM-32 DevKit V1 style header. The generic 30-pin clone's exact pin order/orientation and spacing still need to be checked against its silkscreen/physical board before footprints or layout. GPIO34–GPIO39 are input-only; this design uses them only for analog input. The selected signal GPIOs avoid the usual boot-strapping and flash pins.

| Schematic connector pin | Signal | ESP32 pin |
|---|---|---|
| J1-7 | Turbidity ADC | GPIO32 / ADC1_CH4 |
| J1-8 | ACS712 ADC | GPIO33 / ADC1_CH5 |
| J1-5 | Voltage module ADC | GPIO34 / ADC1_CH6, input-only |
| J1-6 | Soil ADC | GPIO35 / ADC1_CH7, input-only |
| J1-3 | TDS ADC | GPIO36 / VP / ADC1_CH0, input-only |
| J1-10 | Relay command | GPIO26 |
| J1-11 | Conditioned flow pulse | GPIO27 |
| J2-14 | DS18B20 data | GPIO4 |
| J2-7 | OLED SDA | GPIO21 |
| J2-4 | OLED SCL | GPIO22 |
| J1-1 / J1-14 | 3V3 / GND | supply |
| J2-1 / J2-2 / J2-8 | VIN(5V) / GND / GND | supply |

Reference documentation: [Espressif ESP32-DevKitC guide](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html). Espressif's documented DevKitC V4 layout is a 38-pin board, so it verifies ESP32 signal names/functions, not the mechanical numbering of an unspecified 30-pin clone. J1/J2 stay footprintless until the user's actual board is checked. The controller is intended to plug into two removable female sockets.

## Corrections and circuit checks

- Corrected the previous header signal allocation to the requested GPIO map above. Explicit GPIO identifiers are now part of the signal names; the current netlist was regenerated from the schematic.
- R1–R8 are 15 kΩ / 20 kΩ, 1% interface dividers for the four 5 V module outputs (ACS712, DC voltage module, TDS, turbidity). With 5.00 V input, the nominal output is 2.86 V; worst-case 1% resistor ratio gives about 2.89 V. This is below the ESP32 ADC's roughly 3.1 V measurement range at 11 dB attenuation; firmware must configure attenuation and calibrate ADC readings (see [Espressif Arduino ADC documentation](https://docs.espressif.com/projects/arduino-esp32/en/latest/api/adc.html)). The divider is not proof that any unspecified module stays at or below 5 V.
- The soil module is powered from the 3V3 rail and its output now goes through R14=15 kΩ / R15=75 kΩ, both 1%. This keeps a rail-level output below about 3.02 V even if 3V3 reaches 3.6 V, leaving margin below the ADC measurement range. Its actual supply/output specification remains unverified.
- The [Allegro ACS712 datasheet](https://www.allegromicro.com/-/media/Files/Datasheets/ACS712-Datasheet.ashx) specifies a zero-current output near VCC/2 and typical 185 mV/A sensitivity for the -05B variant. On a 5 V module, nominal ±5 A produces approximately 1.575–3.425 V before the external divider and 0.90–1.96 V after it. This is electrically bounded but uses only about 1.06 V of ADC span. Confirm actual module variant and pump RMS/startup current; the 5 A variant may saturate at startup.
- The voltage-sensor module may already contain a measurement divider. R3/R4 are a second, intentional ADC-interface scale-down. Determine the module's actual output-versus-measured-voltage transfer function and calibrate the combined scaling; do not apply the 15k/20k formula twice in software without accounting for the onboard module divider.
- The DS18B20 data line is connected to R9=4.7 kΩ from 3V3. If the chosen sensor assembly already contains a pull-up, verify whether it should remain.
- Flow stage netlist: J9 pulse -> R12 10 kΩ pull-up to 5V and R10 4.7 kΩ base resistor; R11 100 kΩ pulls Q1 base down; Q1 emitter goes to GND; Q1 collector connects to GPIO27 and R13 10 kΩ pull-up to 3V3. The GPIO output is a valid 3.3 V pulled-up, transistor-inverted signal in the stated open-collector/5 V pulse use case. Firmware polarity must be inverted. Sensor output type/current and Q1's exact package pinout/part are still to be confirmed; Q1 footprint is blank.
- Relay J11 is a 5V module interface on GPIO26. R16 10 kΩ pull-up and R17 10 kΩ pull-down are both DNP options; populate exactly one only after checking the module's input circuit and active level. The 3.3 V logic compatibility and safe inactive level during reset are not yet verified, so this interface is not cleared for relay or pump operation.
- J12 is a provisional 5V logic-source interface, not a selected supply design. The 5V source/current capacity and sensor-module current draw need selection. Do not power the exact DevKit through USB and VIN simultaneously unless that board's documentation permits it. Pump supply voltage is undecided and its power path, switching, fuse and protection are intentionally absent from this PCB schematic. For a mains pump, use appropriately rated isolated switching and protection designed by a qualified person.
- No external sensor connector footprints, ESP32 socket footprints, resistor footprints, or transistor footprint are assigned. All symbol footprint fields are blank. The complete connector/board mechanical geometry must be verified before layout.

## KiCad checks and readiness

- KiCad CLI 10.0.6 ERC: **0 errors, 0 warnings** (`erc-report.txt`). The project ERC exclusions list is empty; no warnings were suppressed. The report's “ignored checks” list is KiCad's informational list of non-reported check classes, not project exclusions.
- KiCad CLI netlist export: **succeeded** (`odyssey.net`). Explicit assertions passed for all ten requested signal-to-header pin connections. Soil and DS18B20 dividers/pull-up, flow conditioner and both DNP relay bias options are present on their intended nets. Generic header symbols carry numbered pins; GPIO-to-header-pin mapping is stated in the table above and remains conditional on the physical clone match.
- KiCad CLI SVG render: **succeeded** (`preview/odyssey.svg`).
- PCB DRC: **run; 1 violation** (`drc-report.txt`) — `[invalid_outline]` because the existing `.kicad_pcb` has no Edge.Cuts outline. The report finds 0 unconnected pads and 0 footprint errors because this is an empty board shell with no footprints/tracks/zones. This is not a meaningful layout DRC.
- Status: **ready for schematic review only**. Not ready for PCB layout or fabrication until the exact 30-pin board/header geometry, sensor-module output/supply specs, transistor part/pinout, relay input behavior, and logic power source are confirmed. Pump voltage and switching path remain intentionally undecided.

## Component-list and project files reviewed

- `../Hackathon Component List.docx`
- `../README.md`
- `../project-brief.md`
- `../hardware-flow-explained.md`
- `../hardware-flowchart-prompt.md`
- `../software-flowchart-prompt.md`
- `odyssey.kicad_sch`, `odyssey.kicad_pcb`, `odyssey.kicad_pro`, prior architecture schematic, exported netlist, and prior ERC report.

The component list names generic modules and does not identify exact sensor boards, flow-sensor output circuit, relay module, or clone manufacturer/footprint. Those specifications remain unresolved.
