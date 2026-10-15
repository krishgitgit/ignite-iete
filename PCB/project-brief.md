# AuraPump --- Project Brief

## Project title

**AuraPump: Intelligent Agricultural Pump Protection, Water Quality and
Irrigation Monitoring System**

## Purpose

AuraPump monitors pump operating conditions, detects abnormal conditions
using calibrated deterministic rules, performs local protective shutdown
where appropriate, and sends telemetry/fault events to a farmer-friendly
software layer. The software layer can present simple status messages
and, subject to integration availability, arrange multilingual voice
calls through Gnani AI.

## Farmer-centred design goal

Farmers should not need to interpret engineering graphs or routinely
open an app to learn about important faults. The system should: - show
clear states such as **Working**, **Needs Attention**, **Stopped for
Protection**, and **Status Unavailable**; - explain what happened and
what to check in plain language; - call the farmer in a preferred,
supported language for important events, if the calling integration is
configured; - track whether calls were answered or acknowledged; -
remain protective when internet, backend, app, or voice service is
unavailable.

## Proposed hardware inventory

1.  ESP32 Dev Kit --- controller, local processing and Wi-Fi.
2.  ACS712 5A current sensor --- pump current measurement, subject to
    pump ratings.
3.  Voltage sensor --- supply-voltage measurement, subject to its input
    range and safe interfacing.
4.  DS18B20 temperature sensor --- temperature at a suitable measurement
    point.
5.  Water Flow Sensor --- water-flow measurement.
6.  TDS sensor module and probe --- dissolved-solids-related
    measurement.
7.  Turbidity sensor module and probe --- water-cloudiness/turbidity
    measurement.
8.  Capacitive soil-moisture sensor --- soil-moisture-related
    measurement.
9.  5 V relay module --- switching interface, subject to contact rating
    and safe interfacing.
10. 0.96-inch I2C OLED --- local status and fault messages.

**Important:** This is a proposed complete inventory, not a confirmed
component allocation. The hackathon allows 3--5 major components/sensor
modules including the microcontroller. Ask the organisers how the relay,
display, probes, and additional agricultural sensors count.

## Sensor roles

### Pump-protection measurements

-   **Current:** helps identify overload or abnormal operating
    behaviour.
-   **Voltage:** helps identify configured undervoltage/overvoltage
    conditions.
-   **Temperature:** helps identify excessive measured temperature.
-   **Flow:** helps identify low/absent water delivery; combine with
    other evidence for suspected dry running.

### Additional agricultural monitoring

-   **TDS:** estimates dissolved-solids-related properties; does not
    identify all contaminants or prove water safety.
-   **Turbidity:** estimates cloudiness from suspended particles; does
    not by itself establish water safety.
-   **Soil moisture:** provides a soil-moisture-related measurement;
    requires calibration and suitable placement.

Do not treat TDS, turbidity, or soil moisture as direct substitutes for
pump-protection sensors.

## Core hardware flow

1.  Power on and initialise ESP32, sensors, OLED, relay control and
    communications.
2.  Put relay control into the defined safe default state.
3.  Validate essential protection sensors.
4.  Acquire sensor readings and validate/filter them.
5.  Determine whether the pump is stopped, starting, or running.
6.  Apply a validated startup grace period while retaining necessary
    electrical protection.
7.  Evaluate current, voltage, temperature, and flow against calibrated
    rules.
8.  If a confirmed actionable fault occurs, command protective shutdown,
    activate local alarm if available, update OLED, latch the fault and
    record the event.
9.  Collect optional TDS, turbidity and soil-moisture data separately.
10. Prepare a structured telemetry/event record.
11. Transmit telemetry and fault events to the software layer when
    connectivity is available.
12. If connectivity fails, local protection continues; buffer events
    only if storage is implemented.

## Relay terminology

-   **Contact closed:** the circuit through those contacts is complete.
-   **Contact open:** the circuit through those contacts is interrupted.
-   **COM:** common contact.
-   **NO:** normally open; disconnected from COM when the relay coil is
    not energised.
-   **NC:** normally closed; connected to COM when the relay coil is not
    energised.

The ESP32's HIGH/LOW command depends on the specific relay module; some
modules are active-low. Verify the module. A commanded shutdown is not
proof the physical pump has stopped unless feedback is measured.

For mains-powered pumps, do not assume a hobby relay module is suitable.
Verify motor-load ratings, inrush current, isolation, enclosure, wiring,
and protective devices. A properly rated contactor or motor-protection
arrangement may be required.

## Software-layer handoff

Telemetry may include: - device ID and timestamp; - pump state; -
current, voltage, temperature and flow; - TDS, turbidity and
soil-moisture readings if available; - fault category and severity; -
sensor-health flags; - relay command and any verified shutdown status; -
communication status.

The hardware flowchart must end at:

> **Transmit telemetry and fault events to AuraPump Software Layer**

## Software and Gnani AI

The backend validates telemetry, interprets event records, applies alert
priority, retrieves the farmer's verified phone number and preferred
supported language, and invokes a configured Gnani AI outbound calling
integration when appropriate.

Do not invent API endpoints, supported languages, prices, or
call-delivery capabilities. Verify them. An unanswered call is not an
acknowledgement. Use bounded retries and event deduplication. AI may
explain approved event data but must not invent diagnoses or override
local protection.

## Validation and safety principles

-   Use configured thresholds that are established by calibration and
    testing.
-   Do not claim current variance alone proves cavitation or dry
    running.
-   Do not claim specific detection times or accuracy without
    measurements.
-   Keep shutdown logic local to the ESP32.
-   Treat stale or missing telemetry as **Status Unavailable**, not
    healthy.
-   Require safe fault recovery and a defined reset process.
-   Avoid deliberately damaging a pump during tests.
