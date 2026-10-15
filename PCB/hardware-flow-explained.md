# AuraPump Hardware Flow --- Plain-Language Explanation

## One-line summary

Sensors measure pump and farm conditions → ESP32 checks the readings →
the relay can interrupt pump power if a validated fault is detected →
OLED shows local status → telemetry and events are sent to the software
layer.

## 1. What each component does

### ESP32 Dev Kit --- the brain

Reads sensors, runs deterministic fault rules, controls the relay,
updates the OLED and sends data over Wi-Fi.

### ACS712 5A current sensor

Measures pump current. Abnormal current can indicate overload or other
abnormal operation. Confirm that its rating and module output suit the
actual pump.

### Voltage sensor

Measures supply voltage so configured voltage limits can be checked.
Confirm input range and safe isolation/interface before connecting it to
a circuit.

### DS18B20 temperature sensor

Measures temperature at a suitable location. A high reading can trigger
a warning or protection according to validated limits.

### Water Flow Sensor

Measures water moving through a pipe. Low or absent flow while the pump
is running may indicate a dry-run condition, blockage or another
water-delivery issue. Flow alone does not identify the exact cause.

### TDS sensor

Estimates dissolved-solids-related properties of water. It does not
identify every contaminant or prove water is safe.

### Turbidity sensor

Estimates water cloudiness due to suspended particles. It does not by
itself prove water is safe.

### Capacitive soil-moisture sensor

Measures a signal correlated with soil moisture. It can support
irrigation decisions but requires calibration and suitable placement.

### 5 V relay module

An electrically controlled switch. Its contacts can interrupt the pump's
power circuit if the module is correctly rated and wired.

### 0.96-inch I2C OLED

Shows simple local messages such as `PUMP NORMAL`, `LOW FLOW`,
`PUMP STOPPED`, or `SENSOR ERROR`.

## 2. Relay open versus closed

-   **Contacts closed:** the path through the selected relay contacts is
    electrically complete.
-   **Contacts open:** the path through those contacts is interrupted.
-   **COM:** common terminal.
-   **NO:** normally open; disconnected from COM when the relay coil is
    not energised.
-   **NC:** normally closed; connected to COM when the relay coil is not
    energised.

The ESP32's HIGH/LOW signal does not universally map to relay ON/OFF.
Some modules are active-low. Verify the exact module and test its
behaviour without the pump connected.

A relay command is not proof the pump physically stopped. Feedback would
be needed to verify actual stopping.

For a mains-powered agricultural pump, do not assume a hobby relay is
suitable. Verify motor-load ratings, inrush current, isolation,
enclosure, wiring and protective devices. A properly rated
contactor/motor-protection arrangement may be required.

## 3. Normal operating example

1.  Farmer starts the pump.
2.  ESP32 reads current, voltage, temperature and flow.
3.  It checks values against calibrated limits and distinguishes startup
    from normal running.
4.  If readings are normal, it continues monitoring and updates the
    OLED.
5.  Water-quality and soil-moisture measurements are processed as
    additional agricultural information.
6.  Telemetry is sent to the software layer when connectivity is
    available.

## 4. Fault example

1.  Pump is running.
2.  Flow becomes unusually low or absent.
3.  ESP32 checks flow and other available evidence against validated
    rules.
4.  If an actionable fault is detected, ESP32 commands the relay to
    interrupt pump power.
5.  OLED displays the fault; local alarm may activate if implemented.
6.  Fault is latched until defined safe recovery conditions are met.
7.  Event data is transmitted to the software layer when connectivity is
    available.
8.  The software layer may arrange a farmer-friendly voice call if the
    backend and calling service are configured.

## 5. Data sent to software

Where available, include: - device ID and timestamp; - pump state; -
current, voltage, temperature and flow; - TDS, turbidity and
soil-moisture measurements; - fault category and severity; -
sensor-health flags; - relay command and verified shutdown status, if
available; - communication status.

## 6. Safety and accuracy

-   Keep protective decisions local to the ESP32.
-   Configure thresholds only after calibration and testing.
-   Do not claim current variance alone proves cavitation or dry
    running.
-   Do not invent detection time or accuracy.
-   Treat stale/missing readings as unavailable, not healthy.
-   Do not run a pump dry for extended periods or deliberately lock its
    rotor for a demonstration.
-   Verify all electrical ratings and safety arrangements before
    connecting any pump.
