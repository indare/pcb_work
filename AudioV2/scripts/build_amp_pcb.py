#!/usr/bin/env python3
"""Build the standalone AudioV2 Amp PCB from the proven Audio split board.

The original split board is retained as historical/manufactured artwork.  This
script renumbers it to the AudioV2 schematic, shrinks the output capacitors,
adds per-rail polymer bulk and 1 nF high-speed bypass capacitors, and expands
only the top edge to make room for the new bulk parts.
"""

from __future__ import annotations

import re
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "Audio" / "split" / "AudioCase_4_amp.kicad_pcb"
TARGET = ROOT / "AmpModule.kicad_pcb"
SCHEMATIC = ROOT / "AmpModule.kicad_sch"
FP_ROOT = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints")
AMP_INST = "a1000008-0008-4008-8008-000000000008"

REF_MAP = {
    "AMP1": "AMP701",
    "J10": "J701",
    "J11": "J702",
    "J9": "J703",
    "H9": "H701",
    "H10": "H702",
    "H11": "H703",
    "H12": "H704",
    "R26": "R701",  # L input pulldown
    "R25": "R702",  # R input pulldown
    "R28": "R703",  # L non-inverting bias
    "R29": "R704",  # R non-inverting bias
    "R30": "R705",  # L gain resistor
    "R27": "R706",  # R gain resistor
    "R32": "R707",  # L feedback
    "R31": "R708",  # R feedback
    "R34": "R709",  # L output isolation
    "R33": "R710",  # R output isolation
    "C32": "C701",  # L input film
    "C33": "C702",  # L input electrolytic
    "C30": "C703",  # R input film
    "C31": "C704",  # R input electrolytic
    "C28": "C705",  # V+ 100 nF
    "C29": "C706",  # V- 100 nF
    "C35": "C707",  # L output coupling
    "C34": "C708",  # R output coupling
}

VALUES = {
    "R701": "220k",
    "R702": "220k",
    "R703": "1k",
    "R704": "1k",
    "R705": "20k",
    "R706": "20k",
    "R707": "20k",
    "R708": "20k",
    "R709": "47R",
    "R710": "47R",
    "C701": "100nF film",
    "C702": "10uF",
    "C703": "100nF film",
    "C704": "10uF",
    "C705": "100nF 50V X7R",
    "C706": "100nF 50V X7R",
    "C707": "470uF 25V",
    "C708": "470uF 25V",
    "AMP701": "NE5532 / DIP-8 compatible",
    "J701": "AMP_IN L/R",
    "J702": "AMP_OUT L/R",
    "J703": "+12V / A_GND / -12V",
}

NET_MAP = {
    "/AmpModule/L_IN": "L_IN",
    "/AmpModule/R_IN": "R_IN",
    "/AmpModule/V+_IN": "+12V",
    "/AmpModule/V-_IN": "-12V",
    "/MeasurementADC/AUDIO_L_IN": "L_OUT",
    "/MeasurementADC/AUDIO_R_IN": "R_OUT",
    "Net-(AMP1A-+)": "R_AC",
    "Net-(AMP1B-+)": "L_AC",
    "Net-(AMP1A--)": "R_INV",
    "Net-(AMP1B--)": "L_INV",
    "Net-(AMP1-Pad1)": "R_OUT_OP",
    "Net-(AMP1-Pad7)": "L_OUT_OP",
    "Net-(C34-Pad1)": "R_OUT_PRE",
    "Net-(C35-Pad1)": "L_OUT_PRE",
    "GND": "A_GND",
}


def uid() -> str:
    return str(uuid.uuid4())


def balanced_blocks(text: str, token: str) -> list[tuple[int, int, str]]:
    blocks: list[tuple[int, int, str]] = []
    pos = 0
    while True:
        match = re.search(rf"\({re.escape(token)}(?:\s|\")", text[pos:])
        if not match:
            return blocks
        start = pos + match.start()
        depth = 0
        quoted = False
        escaped = False
        for idx in range(start, len(text)):
            char = text[idx]
            if quoted:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    quoted = False
                continue
            if char == '"':
                quoted = True
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    end = idx + 1
                    blocks.append((start, end, text[start:end]))
                    pos = end
                    break
        else:
            raise ValueError(f"unbalanced {token} at {start}")


def schematic_symbol_uuids() -> dict[str, str]:
    text = SCHEMATIC.read_text(encoding="utf-8")
    result: dict[str, str] = {}
    for _, _, block in balanced_blocks(text, "symbol"):
        ref = re.search(r'\(property "Reference" "([^"]+)"', block)
        lib_id = re.search(r'\(lib_id "([^"]+)"\)', block)
        symbol_uuid = re.search(r'\n\t\t\(uuid "([^"]+)"\)', block)
        if ref and lib_id and symbol_uuid and ref.group(1) not in result:
            result[ref.group(1)] = symbol_uuid.group(1)
    return result


def replace_property(block: str, name: str, value: str) -> str:
    pattern = re.compile(rf'(\(property "{re.escape(name)}" ")[^"]*(")')
    return pattern.sub(rf"\g<1>{value}\2", block, count=1)


def transform_existing_footprints(text: str, symbol_uuids: dict[str, str]) -> str:
    blocks = balanced_blocks(text, "footprint")
    for start, end, original in reversed(blocks):
        ref_match = re.search(r'\(property "Reference" "([^"]+)"', original)
        if not ref_match:
            continue
        old_ref = ref_match.group(1)
        new_ref = REF_MAP.get(old_ref)
        if not new_ref:
            continue
        block = replace_property(original, "Reference", new_ref)
        if new_ref in VALUES:
            block = replace_property(block, "Value", VALUES[new_ref])
        if new_ref in symbol_uuids:
            path = f'/{AMP_INST}/{symbol_uuids[new_ref]}'
            block = re.sub(r'\(path "[^"]+"\)', f'(path "{path}")', block, count=1)
        block = block.replace('(sheetname "/AmpModule/")', '(sheetname "/AmpModule_Reference/")')
        block = block.replace('(sheetfile "AmpModule.kicad_sch")', '(sheetfile "AmpModule.kicad_sch")')
        text = text[:start] + block + text[end:]
    return text


def direct_children(block: str) -> list[tuple[int, int, str]]:
    children: list[tuple[int, int, str]] = []
    depth = 0
    quoted = False
    escaped = False
    child_start: int | None = None
    for idx, char in enumerate(block):
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            continue
        if char == '"':
            quoted = True
        elif char == "(":
            depth += 1
            if depth == 2:
                child_start = idx
        elif char == ")":
            if depth == 2 and child_start is not None:
                children.append((child_start, idx + 1, block[child_start : idx + 1]))
                child_start = None
            depth -= 1
    return children


def add_child_uuids(block: str) -> str:
    needs_uuid = {"property", "fp_line", "fp_arc", "fp_circle", "fp_rect", "fp_poly", "fp_text", "pad"}
    for start, end, child in reversed(direct_children(block)):
        head = re.match(r'\(([A-Za-z_]+)', child)
        if not head or head.group(1) not in needs_uuid or "(uuid " in child:
            continue
        child = child[:-1] + f'\n\t\t(uuid "{uid()}")\n\t)'
        block = block[:start] + child + block[end:]
    return block


def module_footprint(
    library: str,
    name: str,
    ref: str,
    value: str,
    x: float,
    y: float,
    rotation: int,
    pad_nets: dict[str, str],
    symbol_uuid: str,
    layer: str = "F.Cu",
) -> str:
    path = FP_ROOT / f"{library}.pretty" / f"{name}.kicad_mod"
    block = path.read_text(encoding="utf-8").strip()
    block = re.sub(rf'^\(footprint "{re.escape(name)}"', f'(footprint "{library}:{name}"', block)
    block = re.sub(r'\n\t\(version [^\n]+\)', "", block, count=1)
    block = re.sub(r'\n\t\(generator [^\n]+\)', "", block, count=1)
    block = block.replace('\n\t(layer "F.Cu")', f'\n\t(layer "F.Cu")\n\t(uuid "{uid()}")\n\t(at {x} {y} {rotation})', 1)
    if layer == "B.Cu":
        block = block.replace('"F.Cu"', '"B.Cu"')
        block = block.replace('"F.Mask"', '"B.Mask"')
        block = block.replace('"F.Paste"', '"B.Paste"')
        block = block.replace('"F.SilkS"', '"B.SilkS"')
        block = block.replace('"F.Fab"', '"B.Fab"')
        block = block.replace('"F.CrtYd"', '"B.CrtYd"')
    block = replace_property(block, "Reference", ref)
    block = replace_property(block, "Value", value)
    block = re.sub(
        r'\n\t\(property "KiLib_Generator"[\s\S]*?\n\t\)',
        "",
        block,
        count=1,
    )
    block = block[:-1] + (
        f'\n\t(path "/{AMP_INST}/{symbol_uuid}")'
        '\n\t(sheetname "/AmpModule_Reference/")'
        '\n\t(sheetfile "AmpModule.kicad_sch")'
        "\n)"
    )
    for pad_num, net_name in pad_nets.items():
        pattern = re.compile(rf'\(pad "{re.escape(pad_num)}"[\s\S]*?\n\t\)')
        match = pattern.search(block)
        if not match:
            raise ValueError(f"{name} pad {pad_num} not found")
        pad = match.group(0)
        zone_connect = "\n\t\t(zone_connect 2)" if net_name == "A_GND" else ""
        pad = pad[:-1] + (
            f'\n\t\t(net "{net_name}")'
            '\n\t\t(pintype "passive")'
            f"{zone_connect}\n\t)"
        )
        block = block[: match.start()] + pad + block[match.end() :]
    return add_child_uuids(block)


def duplicate_1206(
    source_block: str,
    ref: str,
    value: str,
    x: float,
    y: float,
    rotation: int,
    symbol_uuid: str,
) -> str:
    block = re.sub(
        r'^\(footprint "[^"]+"',
        '(footprint "Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder"',
        source_block,
    )
    block = re.sub(r'\n\t\t\(uuid "[^"]+"\)', f'\n\t\t(uuid "{uid()}")', block, count=1)
    block = re.sub(r'\n\t\t\(at [^\n]+\)', f'\n\t\t(at {x} {y} {rotation})', block, count=1)
    block = replace_property(block, "Reference", ref)
    block = replace_property(block, "Value", value)
    block = re.sub(r'\(path "[^"]+"\)', f'(path "/{AMP_INST}/{symbol_uuid}")', block, count=1)
    for old in re.findall(r'\(uuid "[^"]+"\)', block):
        block = block.replace(old, f'(uuid "{uid()}")', 1)
    return block


def segment(x1: float, y1: float, x2: float, y2: float, layer: str, net: str, width: float = 0.6) -> str:
    return f"""\t(segment
\t\t(start {x1} {y1})
\t\t(end {x2} {y2})
\t\t(width {width})
\t\t(layer "{layer}")
\t\t(net "{net}")
\t\t(uuid "{uid()}")
\t)"""


def via(x: float, y: float, net: str) -> str:
    return f"""\t(via
\t\t(at {x} {y})
\t\t(size 1.2)
\t\t(drill 0.6)
\t\t(layers "F.Cu" "B.Cu")
\t\t(net "{net}")
\t\t(uuid "{uid()}")
\t)"""


def main() -> None:
    symbols = schematic_symbol_uuids()
    required = set(VALUES) | {"C709", "C710", "C711", "C712"}
    missing = sorted(required - symbols.keys())
    if missing:
        raise ValueError(f"schematic refs missing: {missing}")

    text = SOURCE.read_text(encoding="utf-8")
    for old, new in NET_MAP.items():
        text = text.replace(f'"{old}"', f'"{new}"')
    text = transform_existing_footprints(text, symbols)
    # KiKit's split copy retained mounting-hole keepouts that also rejected the
    # mounting-hole footprint itself. Keep copper/track/via restrictions, but
    # permit the NPTH footprint in its own keepout.
    text = text.replace("\n\t\t\t(pads not_allowed)", "")

    footprint_blocks = {
        re.search(r'\(property "Reference" "([^"]+)"', block).group(1): (start, end, block)
        for start, end, block in balanced_blocks(text, "footprint")
        if re.search(r'\(property "Reference" "([^"]+)"', block)
    }

    # Replace the two large output capacitors with D12.5/P5 versions.
    replacements = {
        "C707": module_footprint(
            "Capacitor_THT", "CP_Radial_D12.5mm_P5.00mm", "C707", "470uF 25V",
            152.94, 52.323257, 0, {"1": "L_OUT_PRE", "2": "L_OUT"}, symbols["C707"]
        ),
        "C708": module_footprint(
            "Capacitor_THT", "CP_Radial_D12.5mm_P5.00mm", "C708", "470uF 25V",
            158.74, 29.123257, 0, {"1": "R_OUT_PRE", "2": "R_OUT"}, symbols["C708"]
        ),
    }
    for ref, replacement in replacements.items():
        start, end, _ = footprint_blocks[ref]
        text = text[:start] + replacement + text[end:]
        # Recompute positions because the first replacement changes offsets.
        footprint_blocks = {
            re.search(r'\(property "Reference" "([^"]+)"', block).group(1): (s, e, block)
            for s, e, block in balanced_blocks(text, "footprint")
            if re.search(r'\(property "Reference" "([^"]+)"', block)
        }

    # Expand only the top edge by 15 mm; terminal and mounting-hole coordinates stay fixed.
    text = text.replace("(start 119.41 20)\n\t\t(end 177.59 20)", "(start 119.41 5)\n\t\t(end 177.59 5)")
    text = text.replace("(end 119.41 20)", "(end 119.41 5)")
    text = text.replace("(start 177.59 20)", "(start 177.59 5)")

    # Add new footprints before board graphics.
    footprint_blocks = {
        re.search(r'\(property "Reference" "([^"]+)"', block).group(1): block
        for _, _, block in balanced_blocks(text, "footprint")
        if re.search(r'\(property "Reference" "([^"]+)"', block)
    }
    additions = [
        module_footprint(
            "Capacitor_SMD", "CP_Elec_10x12.6", "C709", "100uF 35V polymer",
            142.0, 11.5, 180, {"1": "+12V", "2": "A_GND"}, symbols["C709"]
        ),
        module_footprint(
            "Capacitor_SMD", "CP_Elec_10x12.6", "C710", "100uF 35V polymer",
            158.0, 11.5, 180, {"1": "A_GND", "2": "-12V"}, symbols["C710"]
        ),
        module_footprint(
            "Capacitor_SMD", "C_0603_1608Metric_Pad1.08x0.95mm_HandSolder",
            "C711", "1nF 50V C0G", 152.0, 34.0, 0,
            {"1": "A_GND", "2": "+12V"}, symbols["C711"], "B.Cu"
        ),
        module_footprint(
            "Capacitor_SMD", "C_0603_1608Metric_Pad1.08x0.95mm_HandSolder",
            "C712", "1nF 50V C0G", 141.0, 49.0, 0,
            {"1": "-12V", "2": "A_GND"}, symbols["C712"], "B.Cu"
        ),
    ]
    routes = [
        # Bulk capacitors: short F.Cu stubs; ground drops into the existing planes.
        segment(146.35, 11.5, 149.24, 26.723257, "F.Cu", "+12V", 0.8),
        segment(137.65, 11.5, 144.16, 26.723257, "F.Cu", "A_GND", 0.8),
        segment(162.35, 11.5, 162.35, 14.0, "F.Cu", "A_GND", 0.8),
        via(162.35, 14.0, "A_GND"),
        segment(162.35, 14.0, 144.16, 26.723257, "B.Cu", "A_GND", 0.8),
        segment(153.65, 11.5, 153.65, 14.0, "F.Cu", "-12V", 0.8),
        via(153.65, 14.0, "-12V"),
        segment(153.65, 14.0, 139.08, 26.723257, "B.Cu", "-12V", 0.8),
        # New 1 nF parts connect directly to the DIP supply pads on B.Cu;
        # their other pads connect to the existing A_GND plane.
        segment(152.8625, 34.0, 153.0, 38.5, "B.Cu", "+12V", 0.3),
        segment(153.0, 38.5, 146.65, 38.513257, "B.Cu", "+12V", 0.3),
        segment(140.1375, 49.0, 139.03, 46.133257, "B.Cu", "-12V", 0.3),
        # New P5 output capacitor pad 2 to the former P7.5 routed endpoint.
        segment(157.94, 52.323257, 160.44, 52.323257, "F.Cu", "L_OUT", 0.5),
        segment(163.74, 29.123257, 166.24, 29.123257, "F.Cu", "R_OUT", 0.5),
    ]
    insert_at = text.index("\n\t(gr_line")
    text = text[:insert_at] + "\n" + "\n".join(additions + routes) + text[insert_at:]
    text = text.replace('(gr_text "AMP"', '(gr_text "AudioV2 AMP x10"')
    TARGET.write_text(text, encoding="utf-8")
    print(f"Built {TARGET.relative_to(ROOT.parent)}")


if __name__ == "__main__":
    main()
