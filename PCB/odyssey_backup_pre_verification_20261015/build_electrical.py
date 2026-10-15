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
    '  (text "LOW-VOLTAGE CONTROL BOARD | DevKit V1 30-pin header mapping shown as a draft; verify the exact board before PCB layout." (at 25 28 0) (effects (font (size 1.4 1.4)) (justify left bottom)))',
    '  (text "5V INPUT: regulated external 5V supply to ESP32 VIN and modules. Do not route pump power through this logic PCB." (at 25 274 0) (effects (font (size 1.35 1.35)) (justify left bottom)))',
    '  (text "Analog module outputs use 15k series / 20k to GND dividers (0-5V -> <2.9V with 1% resistors). Use only after confirming module maximum output." (at 25 281 0) (effects (font (size 1.35 1.35)) (justify left bottom)))',
    '  (text "Use a motor-rated external contactor/protection for the pump. Relay command is not shutdown feedback. Voltage sensing is low-voltage DC only." (at 25 288 0) (effects (font (size 1.35 1.35)) (justify left bottom)))',
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
    items.append(f'    (property "Footprint" "{footprint}" (at {x:g} {y:g} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
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

def add_resistor(ref, value, x, y, pin1_net, pin2_net):
    x, y = snap(x), snap(y)
    items.append("  (symbol")
    items.append(f'    (lib_id "Device:R") (at {x:g} {y:g} 0) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid()}")')
    items.append(f'    (property "Reference" "{ref}" (at {x+2:g} {y-1:g} 0) (effects (font (size 1.15 1.15)) (justify left)))')
    items.append(f'    (property "Value" "{value}" (at {x+2:g} {y+1.5:g} 0) (effects (font (size 1.15 1.15)) (justify left)))')
    items.append(f'    (property "Footprint" "Resistor_SMD:R_0805_2012Metric" (at {x:g} {y:g} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
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
    add_wire_label(x+2.54, y-5.08, x+10.16, y-5.08, "FLOW_GPIO", 0)
    add_wire_label(x+2.54, y+5.08, x+10.16, y+5.08, "GND", 0)

# ESP32 DevKit V1 30-pin carrier headers. Verify pinout and connector orientation against the supplied board.
left = {1:"+3V3", 2:None, 3:"TURB_ADC", 4:None, 5:"ACS_ADC", 6:"VOLT_ADC", 7:"SOIL_ADC", 8:"TDS_ADC", 9:None, 10:"RELAY_IN", 11:"FLOW_GPIO", 12:None, 13:None, 14:"GND", 15:None}
right = {1:"+5V", 2:"GND", 3:None, 4:"I2C_SCL", 5:None, 6:None, 7:"I2C_SDA", 8:"GND", 9:None, 10:None, 11:None, 12:None, 13:None, 14:"TEMP_DATA", 15:None}
add_connector("J1", "ESP32 DevKit V1 left header - verify", 15, 67, 130, left, "")
add_connector("J2", "ESP32 DevKit V1 right header - verify", 15, 137, 130, right, "")

# External module headers. Pin order is defined on this interface PCB.
add_connector("J3", "ACS712 5A module LV: 5V, GND, OUT", 3, 355, 48, {1:"+5V",2:"GND",3:"ACS_RAW"}, "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical")
add_connector("J4", "Voltage module: 5V, GND, OUT", 3, 355, 70, {1:"+5V",2:"GND",3:"VOLT_RAW"}, "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical")
add_connector("J5", "Capacitive soil module: 3V3, GND, OUT", 3, 355, 92, {1:"+3V3",2:"GND",3:"SOIL_ADC"}, "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical")
add_connector("J6", "TDS module: 5V, GND, OUT", 3, 355, 114, {1:"+5V",2:"GND",3:"TDS_RAW"}, "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical")
add_connector("J7", "Turbidity module: 5V, GND, OUT", 3, 355, 136, {1:"+5V",2:"GND",3:"TURB_RAW"}, "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical")
add_connector("J8", "DS18B20: 3V3, GND, DATA", 3, 355, 158, {1:"+3V3",2:"GND",3:"TEMP_DATA"}, "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical")
add_connector("J9", "Flow module: 5V, GND, PULSE", 3, 355, 180, {1:"+5V",2:"GND",3:"FLOW_RAW"}, "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical")
add_connector("J10", "OLED I2C: 3V3, GND, SDA, SCL", 4, 355, 205, {1:"+3V3",2:"GND",3:"I2C_SDA",4:"I2C_SCL"}, "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical")
add_connector("J11", "5V relay module: VCC, GND, IN", 3, 355, 231, {1:"+5V",2:"GND",3:"RELAY_IN"}, "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical")
add_connector("J12", "Regulated 5V input", 3, 355, 253, {1:"+5V",2:"GND",3:None}, "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical")

# 15k/20k dividers scale confirmed 0-5V outputs below 2.9V using 1% resistors.
channels = [("ACS_RAW","ACS_ADC",55),("VOLT_RAW","VOLT_ADC",82),("TDS_RAW","TDS_ADC",109),("TURB_RAW","TURB_ADC",136)]
ref = 1
for raw, adc, row in channels:
    add_resistor(f"R{ref}", "15k 1%", 220, row, raw, adc); ref += 1
    add_resistor(f"R{ref}", "20k 1%", 248, row, adc, "GND"); ref += 1

# DS18B20 1-Wire pull-up.
add_resistor("R9", "4.7k", 220, 167, "+3V3", "TEMP_DATA")

# NPN pulse conditioner supports open-collector or 5V push-pull flow outputs; pulse is inverted.
add_resistor("R10", "4.7k", 220, 205, "FLOW_RAW", "FLOW_BASE")
add_resistor("R11", "100k", 248, 205, "FLOW_BASE", "GND")
add_resistor("R12", "10k", 276, 205, "+5V", "FLOW_RAW")
add_resistor("R13", "10k", 304, 205, "+3V3", "FLOW_GPIO")
add_transistor("Q1", "2N3904", 280, 230)

out.extend(items)
out += [
    '  (text "R1-R8: 15k/20k 1% dividers (confirmed 0-5V outputs only); R9: DS18B20 pull-up; R10-R13 + Q1: inverting flow conditioner." (at 195 250 0) (effects (font (size 1.25 1.25)) (justify left bottom)))',
    '  (text "ACS712 5A: 15k/20k divider maps nominal 1.575-3.425V (±5A) to ~0.90-1.96V. Verify module variant, calibration and pump startup current; divider reduces ADC span." (at 25 260 0) (effects (font (size 1.25 1.25)) (justify left bottom)))',
    '  (text "J4 voltage sensor output must be verified <=5V before using divider. DC isolated sensing only; never connect mains. Relay input active polarity/startup state requires exact module validation before use." (at 25 267 0) (effects (font (size 1.25 1.25)) (justify left bottom)))',
    '  (text "DRAFT COMMON 30-pin DevKit map: J1 pins 3/5/6/7/8 = GPIO36/34/35/32/33 ADC; J1 pins 10/11 = GPIO26 relay / GPIO27 flow." (at 25 274 0) (effects (font (size 1.2 1.2)) (justify left bottom)))',
    '  (text "J2 pins 1/2/4/7/8/14 = VIN/GND/GPIO22/GPIO21/GND/GPIO4. Confirm exact board pin order and polarity before connecting; J1/J2 footprints intentionally blank." (at 25 281 0) (effects (font (size 1.2 1.2)) (justify left bottom)))',
    '  (text "RELAY_IN startup state is unresolved until module active level is identified. Do not operate relay/pump from this draft; select correct inactive bias/interface after verification." (at 25 288 0) (effects (font (size 1.2 1.2)) (justify left bottom)))',
    '  (title_block (title "AuraPump electrical interface schematic") (date "2026-10-15") (rev "A - module interface draft") (company "IGNITE 1.0 IETE Hackathon"))',
    '  (sheet_instances (path "/" (page "1")))',
    ")",
]

dest = HERE / "odyssey.kicad_sch"
dest.write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"Wrote {dest} with {len(items)} electrical objects and {len(lib_names)} embedded symbol definitions")
