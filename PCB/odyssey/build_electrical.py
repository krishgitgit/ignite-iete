from pathlib import Path
import re
import uuid

ROOT_UUID = "7ba9848b-47ba-4c22-ad57-f2bbacb61101"
PROJECT = "odyssey"
HERE = Path(__file__).parent

def uid():
    return str(uuid.uuid4())

def snap(v):
    return round(round(v / 1.27) * 1.27, 2)

def read_library_snips():
    raw = (HERE / "library_snips.txt").read_text(encoding="utf-8")
    chunks = {}
    for chunk in re.split(r"\n;LIB [^\n]+\n", "\n" + raw):
        m = re.search(r'\(symbol "([^"]+)"', chunk)
        if m:
            chunks[m.group(1)] = chunk.strip()
    return chunks

chunks = read_library_snips()
lib_names = {
    "Conn_01x03": "Connector_Generic:Conn_01x03",
    "Conn_01x04": "Connector_Generic:Conn_01x04",
    "Conn_01x15": "Connector_Generic:Conn_01x15",
    "R": "Device:R",
    "Q_NPN_BCE": "Transistor_BJT:Q_NPN_BCE",
}

def embedded(name):
    s = chunks[name]
    return s.replace(f'(symbol "{name}"', f'(symbol "{lib_names[name]}"', 1)

out = [
    "(kicad_sch",
    "  (version 20250114)",
    '  (generator "eeschema")',
    '  (generator_version "10.0")',
    f'  (uuid "{ROOT_UUID}")',
    '  (paper "A3")',
    "  (lib_symbols",
]
for name in lib_names:
    out.append(embedded(name))
out += [
    "  )",
    '  (text "AURAPUMP - ESP32 PUMP AND FARM SENSOR INTERFACE" (at 25 22 0) (effects (font (size 2.5 2.5) (thickness 0.35)) (justify left bottom)))',
    '  (text "LOW-VOLTAGE CONTROL BOARD | Reference mapping for common 30-pin ESP32-WROOM-32 DevKit V1; clone geometry/pinout must be verified before layout." (at 25 28 0) (effects (font (size 1.4 1.4)) (justify left bottom)))',
    '  (text "5V logic source TBD; pump supply is not designed here. Do not power the exact DevKit simultaneously by USB and VIN unless its documentation allows it." (at 25 35 0) (effects (font (size 1.3 1.3)) (justify left bottom)))',
]

items = []

def add_wire_label(x1, y1, x2, y2, name, angle=0):
    items.append(f'  (wire (pts (xy {x1:g} {y1:g}) (xy {x2:g} {y2:g})) (stroke (width 0) (type default)) (uuid "{uid()}"))')
    items.append(f'  (label "{name}" (at {x2:g} {y2:g} {angle}) (effects (font (size 1.15 1.15)) (justify left bottom)) (uuid "{uid()}"))')

def add_nc(x, y):
    items.append(f'  (no_connect (at {x:g} {y:g}) (uuid "{uid()}"))')

def add_connector(ref, value, count, x, y, nets, footprint, field_side="right"):
    x, y = snap(x), snap(y)
    lib = f"Connector_Generic:Conn_01x{count:02d}"
    # KiCad library coordinates are y-up; schematic coordinates are y-down.
    pinys = {1: 2.54, 2: 0, 3: -2.54, 4: -5.08}
    if count == 15:
        pinys = {i: 17.78 - 2.54 * (i - 1) for i in range(1, 16)}
    prop_x = x + 9.0 if field_side == "right" else x - 10.0
    items.append("  (symbol")
    items.append(f'    (lib_id "{lib}") (at {x:g} {y:g} 0) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid()}")')
    items.append(f'    (property "Reference" "{ref}" (at {prop_x:g} {y-3:g} 0) (effects (font (size 1.27 1.27)) (justify left)))')
    items.append(f'    (property "Value" "{value}" (at {prop_x:g} {y:g} 0) (effects (font (size 1.27 1.27)) (justify left)))')
    items.append(f'    (property "Footprint" "" (at {x:g} {y:g} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    items.append(f'    (property "Datasheet" "" (at {x:g} {y:g} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    for p in range(1, count + 1):
        items.append(f'    (pin "{p}" (uuid "{uid()}"))')
    items.append(f'    (instances (project "{PROJECT}" (path "/" (reference "{ref}") (unit 1))))')
    items.append("  )")
    for p in range(1, count + 1):
        # Standard Conn_01x symbols have endpoints at x=-5.08, with y-up pin offsets.
        px, py = x - 5.08, y - pinys[p]
        net = nets.get(p)
        if net:
            add_wire_label(px, py, px - 7.62, py, net, 180)
        else:
            add_nc(px, py)

def add_resistor(ref, value, x, y, pin1_net, pin2_net, dnp=False):
    x, y = snap(x), snap(y)
    items.append("  (symbol")
    items.append(f'    (lib_id "Device:R") (at {x:g} {y:g} 0) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp {"yes" if dnp else "no"}) (uuid "{uid()}")')
    items.append(f'    (property "Reference" "{ref}" (at {x+2:g} {y-1:g} 0) (effects (font (size 1.15 1.15)) (justify left)))')
    items.append(f'    (property "Value" "{value}" (at {x+2:g} {y+1.5:g} 0) (effects (font (size 1.15 1.15)) (justify left)))')
    items.append(f'    (property "Footprint" "" (at {x:g} {y:g} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    items.append(f'    (property "Datasheet" "" (at {x:g} {y:g} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    items.append(f'    (pin "1" (uuid "{uid()}")) (pin "2" (uuid "{uid()}"))')
    items.append(f'    (instances (project "{PROJECT}" (path "/" (reference "{ref}") (unit 1))))')
    items.append("  )")
    add_wire_label(x, y-3.81, x-6.35, y-3.81, pin1_net, 180)
    add_wire_label(x, y+3.81, x+6.35, y+3.81, pin2_net, 0)

def add_transistor(ref, value, x, y):
    x, y = snap(x), snap(y)
    items.append("  (symbol")
    items.append('    (lib_id "Transistor_BJT:Q_NPN_BCE")')
    items.append(f'    (at {x:g} {y:g} 0) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid()}")')
    items.append(f'    (property "Reference" "{ref}" (at {x+5:g} {y-2:g} 0) (effects (font (size 1.15 1.15)) (justify left)))')
    items.append(f'    (property "Value" "{value}" (at {x+5:g} {y+1:g} 0) (effects (font (size 1.15 1.15)) (justify left)))')
    items.append(f'    (property "Footprint" "" (at {x:g} {y:g} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    items.append(f'    (property "Datasheet" "" (at {x:g} {y:g} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    items.append(f'    (pin "1" (uuid "{uid()}")) (pin "2" (uuid "{uid()}")) (pin "3" (uuid "{uid()}"))')
    items.append(f'    (instances (project "{PROJECT}" (path "/" (reference "{ref}") (unit 1))))')
    items.append("  )")
    # Q_NPN_BCE library pin positions: B=(-5.08,0), C=(2.54,5.08), E=(2.54,-5.08).
    add_wire_label(x-5.08, y, x-12.7, y, "FLOW_BASE", 180)
    add_wire_label(x+2.54, y-5.08, x+10.16, y-5.08, "FLOW_GPIO27", 0)
    add_wire_label(x+2.54, y+5.08, x+10.16, y+5.08, "GND", 0)

# ESP32 DevKit V1 30-pin carrier headers. Verify pinout and connector orientation against the supplied board.
left = {1:"+3V3", 2:None, 3:"TDS_GPIO36_ADC", 4:None, 5:"VOLT_GPIO34_ADC", 6:"SOIL_GPIO35_ADC", 7:"TURB_GPIO32_ADC", 8:"ACS_GPIO33_ADC", 9:None, 10:"RELAY_GPIO26", 11:"FLOW_GPIO27", 12:None, 13:None, 14:"GND", 15:None}
right = {1:"+5V", 2:"GND", 3:None, 4:"I2C_SCL_GPIO22", 5:None, 6:None, 7:"I2C_SDA_GPIO21", 8:"GND", 9:None, 10:None, 11:None, 12:None, 13:None, 14:"TEMP_GPIO4", 15:None}
add_connector("J1", "ESP32 removable female socket, left - reference map; verify", 15, 67, 130, left, "")
add_connector("J2", "ESP32 removable female socket, right - reference map; verify", 15, 137, 130, right, "")

# External module headers. Pin order is defined on this interface PCB.
add_connector("J3", "ACS712 5A module LV: 5V, GND, OUT", 3, 355, 48, {1:"+5V",2:"GND",3:"ACS_RAW"}, "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical")
add_connector("J4", "Voltage module: 5V, GND, OUT", 3, 355, 70, {1:"+5V",2:"GND",3:"VOLT_RAW"}, "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical")
add_connector("J5", "Capacitive soil module: 3V3, GND, OUT", 3, 355, 92, {1:"+3V3",2:"GND",3:"SOIL_RAW"}, "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical")
add_connector("J6", "TDS module: 5V, GND, OUT", 3, 355, 114, {1:"+5V",2:"GND",3:"TDS_RAW"}, "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical")
add_connector("J7", "Turbidity module: 5V, GND, OUT", 3, 355, 136, {1:"+5V",2:"GND",3:"TURB_RAW"}, "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical")
add_connector("J8", "DS18B20: 3V3, GND, DATA", 3, 355, 158, {1:"+3V3",2:"GND",3:"TEMP_GPIO4"}, "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical")
add_connector("J9", "Flow module: 5V, GND, PULSE", 3, 355, 180, {1:"+5V",2:"GND",3:"FLOW_RAW"}, "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical")
add_connector("J10", "OLED I2C: 3V3, GND, SDA, SCL", 4, 355, 205, {1:"+3V3",2:"GND",3:"I2C_SDA_GPIO21",4:"I2C_SCL_GPIO22"}, "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical")
add_connector("J11", "5V relay module: VCC, GND, IN", 3, 355, 231, {1:"+5V",2:"GND",3:"RELAY_GPIO26"}, "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical")
add_connector("J12", "5V logic input - source TBD", 3, 355, 253, {1:"+5V",2:"GND",3:None}, "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical")

# 15k/20k dividers scale confirmed 0-5V outputs below 2.9V using 1% resistors.
channels = [("ACS_RAW","ACS_GPIO33_ADC",55),("VOLT_RAW","VOLT_GPIO34_ADC",82),("TDS_RAW","TDS_GPIO36_ADC",109),("TURB_RAW","TURB_GPIO32_ADC",136)]
ref = 1
for raw, adc, row in channels:
    add_resistor(f"R{ref}", "15k 1%", 220, row, raw, adc); ref += 1
    add_resistor(f"R{ref}", "20k 1%", 248, row, adc, "GND"); ref += 1

# Soil sensor is powered from 3V3; 15k/75k attenuates a rail-level output below ADC range.
add_resistor("R14", "15k 1%", 220, 92, "SOIL_RAW", "SOIL_GPIO35_ADC")
add_resistor("R15", "75k 1%", 248, 92, "SOIL_GPIO35_ADC", "GND")

# DS18B20 1-Wire pull-up.
add_resistor("R9", "4.7k", 220, 167, "+3V3", "TEMP_GPIO4")

# NPN pulse conditioner supports open-collector or 5V push-pull flow outputs; pulse is inverted.
add_resistor("R10", "4.7k", 220, 205, "FLOW_RAW", "FLOW_BASE")
add_resistor("R11", "100k", 248, 205, "FLOW_BASE", "GND")
add_resistor("R12", "10k", 276, 205, "+5V", "FLOW_RAW")
add_resistor("R13", "10k", 304, 205, "+3V3", "FLOW_GPIO27")
add_transistor("Q1", "NPN - exact part TBD", 280, 230)

# Populate exactly one relay-input bias after verifying the module active level; both options DNP in draft.
add_resistor("R16", "10k pull-up option DNP", 220, 231, "+3V3", "RELAY_GPIO26", dnp=True)
add_resistor("R17", "10k pull-down option DNP", 248, 231, "RELAY_GPIO26", "GND", dnp=True)

out.extend(items)
out += [
    '  (text "R1-R8: 15k/20k 1% dividers for confirmed <=5V outputs. R14/R15: soil 15k/75k divider from 3V3. R9: DS18B20 pull-up; flow conditioner is inverting." (at 195 250 0) (effects (font (size 1.25 1.25)) (justify left bottom)))',
    '  (text "ACS712-05B nominal ±5A maps ~1.575-3.425V to ~0.90-1.96V through divider; verify exact module and pump startup current. ADC span is reduced." (at 25 260 0) (effects (font (size 1.25 1.25)) (justify left bottom)))',
    '  (text "Verify each module max output <=5V; J4 measures isolated low-voltage DC only, never mains. Relay logic compatibility and safe reset state are unresolved until exact module is identified." (at 25 267 0) (effects (font (size 1.25 1.25)) (justify left bottom)))',
    '  (text "REFERENCE 30-pin map: J1 pins 7/8/5/6/3 = GPIO32 turbidity / GPIO33 ACS712 / GPIO34 voltage / GPIO35 soil / GPIO36 TDS; pins 10/11 = GPIO26 relay / GPIO27 flow." (at 25 274 0) (effects (font (size 1.2 1.2)) (justify left bottom)))',
    '  (text "J2 pins 1/2/4/7/8/14 = VIN/GND/GPIO22/GPIO21/GND/GPIO4. Common reference only; verify clone pin order, row spacing, and orientation. J1/J2 footprints intentionally blank." (at 25 281 0) (effects (font (size 1.2 1.2)) (justify left bottom)))',
    '  (text "R16/R17 are DNP relay-bias choices: populate exactly one only after verifying module active level and input circuit. Relay must not be operated until GPIO26 startup is safely biased." (at 25 288 0) (effects (font (size 1.2 1.2)) (justify left bottom)))',
    '  (title_block (title "AuraPump electrical interface schematic") (date "2026-10-15") (rev "A - module interface draft") (company "IGNITE 1.0 IETE Hackathon"))',
    '  (sheet_instances (path "/" (page "1")))',
    ")",
]

dest = HERE / "odyssey.kicad_sch"
dest.write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"Wrote {dest} with {len(items)} electrical objects and {len(lib_names)} embedded symbol definitions")
