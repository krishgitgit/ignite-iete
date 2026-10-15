from pathlib import Path

libdir = Path(r"C:\Users\KHIN\AppData\Local\Programs\KiCad\10.0\share\kicad\symbols")
targets = {
    "Connector_Generic.kicad_sym": ["Conn_01x03", "Conn_01x04", "Conn_01x15"],
    "Device.kicad_sym": ["R"],
    "Transistor_BJT.kicad_sym": ["Q_NPN_BCE"],
}

def extract(source: str, name: str) -> str:
    marker = f'(symbol "{name}"'
    start = source.find(marker)
    if start < 0:
        raise ValueError(f"Missing symbol {name}")
    depth = 0
    in_string = False
    escaped = False
    for i in range(start, len(source)):
        ch = source[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return source[start:i + 1]
    raise ValueError(f"Unbalanced symbol {name}")

parts = []
for filename, names in targets.items():
    source = (libdir / filename).read_text(encoding="utf-8")
    for name in names:
        parts.append(f";LIB {filename} {name}\n" + extract(source, name))
Path(__file__).with_name("library_snips.txt").write_text("\n\n".join(parts), encoding="utf-8")
print("Extracted:", ", ".join(n for v in targets.values() for n in v))
