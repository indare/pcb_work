#!/usr/bin/env python3
"""Generate AudioV2 KiCad draft scaffold (Phase 0–6). Run once; output under AudioV2/."""

from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT.parent / "Audio"

# Fixed UUIDs — parent sheet instance IDs must match AudioV2Case.kicad_pro "sheets"
PARENT = "a1000001-0001-4001-8001-000000000001"
UUID_POWER_INST = "a1000002-0002-4002-8002-000000000002"
UUID_RELAY_A = "a1000004-0004-4004-8004-000000000004"
UUID_RELAY_B = "a1000005-0005-4005-8005-000000000005"
UUID_CONTROL_INST = "a1000006-0006-4006-8006-000000000006"
UUID_OUTPUT_INST = "a1000007-0007-4007-8007-000000000007"

# Child file root UUIDs (distinct from sheet instance UUIDs)
UUID_POWER_FILE = "b2000002-0002-4002-8002-000000000002"
UUID_RELAY_FILE = "b2000003-0003-4003-8003-000000000003"
UUID_CONTROL_FILE = "b2000006-0006-4006-8006-000000000006"
UUID_OUTPUT_FILE = "b2000007-0007-4007-8007-000000000007"

PROJECT = "AudioV2Case"


def uid() -> str:
    return str(uuid.uuid4())


def sch_open(file_uuid: str, body: str) -> str:
    return f"""(kicad_sch
\t(version 20260306)
\t(generator "eeschema")
\t(generator_version "10.0")
\t(uuid "{file_uuid}")
\t(paper "A4")
{body}
\t(sheet_instances
\t\t(path "/"
\t\t\t(page "1")
\t\t)
\t)
)
"""


def text_note(x: float, y: float, lines: list[str]) -> str:
    content = "\\n".join(lines)
    return f"""\t(text "{content}"
\t\t(at {x} {y} 0)
\t\t(effects
\t\t\t(font
\t\t\t\t(size 1.27 1.27)
\t\t\t)
\t\t\t(justify left top)
\t\t)
\t\t(uuid "{uid()}")
\t)
"""


def hier_label(name: str, shape: str, x: float, y: float, angle: int = 0) -> str:
    justify = "left"
    if angle == 180:
        justify = "right"
    elif angle == 90:
        justify = "left"
    elif angle == 270:
        justify = "right"
    return f"""\t(hierarchical_label "{name}"
\t\t(shape {shape})
\t\t(at {x} {y} {angle})
\t\t(effects
\t\t\t(font
\t\t\t\t(size 1.27 1.27)
\t\t\t)
\t\t\t(justify {justify})
\t\t)
\t\t(uuid "{uid()}")
\t)
"""


def global_label(name: str, x: float, y: float, angle: int = 0) -> str:
    return f"""\t(global_label "{name}"
\t\t(shape input)
\t\t(at {x} {y} {angle})
\t\t(fields_autoplaced yes)
\t\t(effects
\t\t\t(font
\t\t\t\t(size 1.27 1.27)
\t\t\t)
\t\t\t(justify left)
\t\t)
\t\t(uuid "{uid()}")
\t\t(property "Intersheetrefs" "${{INTERSHEET_REFS}}"
\t\t\t(at {x} {y} 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(hide yes)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(justify left)
\t\t\t)
\t\t)
\t)
"""


def sym_prop(name: str, value: str, x: float, y: float, hide: bool = False) -> str:
    hide_line = "\n\t\t\t(hide yes)" if hide else ""
    return f"""\t\t(property "{name}" "{value}"
\t\t\t(at {x} {y} 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no){hide_line}
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
"""


def symbol_inst(
    lib_id: str,
    ref: str,
    value: str,
    x: float,
    y: float,
    rot: int,
    parent_path: str,
    extra_props: list[tuple[str, str]] | None = None,
) -> str:
    props = [
        sym_prop("Reference", ref, x, y - 2.54),
        sym_prop("Value", value, x, y + 2.54),
        sym_prop("Footprint", "", 0, 0, hide=True),
        sym_prop("Datasheet", "", 0, 0, hide=True),
        sym_prop("Description", "AudioV2 draft placeholder", 0, 0, hide=True),
    ]
    if extra_props:
        for n, v in extra_props:
            props.append(sym_prop(n, v, 0, 0, hide=True))
    props_str = "\n".join(props)
    return f"""\t(symbol
\t\t(lib_id "{lib_id}")
\t\t(at {x} {y} {rot})
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(fields_autoplaced yes)
\t\t(uuid "{uid()}")
{props_str}
\t\t(instances
\t\t\t(project "{PROJECT}"
\t\t\t\t(path "{parent_path}"
\t\t\t\t\t(reference "{ref}")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)
"""


def sheet_block(
    sheet_uuid: str,
    name: str,
    filename: str,
    x: float,
    y: float,
    w: float,
    h: float,
    pins: list[tuple[str, str, float, float, int]],
    page: str,
) -> str:
    pin_lines = []
    for pname, ptype, px, py, pangle in pins:
        justify = "left"
        if pangle in (0, 90):
            justify = "right" if pangle == 0 else "left"
        elif pangle == 180:
            justify = "left"
        pin_lines.append(
            f"""\t\t(pin "{pname}" {ptype}
\t\t\t(at {px} {py} {pangle})
\t\t\t(uuid "{uid()}")
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(justify {justify})
\t\t\t)
\t\t)"""
        )
    pins_str = "\n".join(pin_lines)
    return f"""\t(sheet
\t\t(at {x} {y})
\t\t(size {w} {h})
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(stroke
\t\t\t(width 0.1524)
\t\t\t(type solid)
\t\t)
\t\t(fill
\t\t\t(color 0 0 0 0)
\t\t)
\t\t(uuid "{sheet_uuid}")
\t\t(property "Sheetname" "{name}"
\t\t\t(at {x} {y - 0.8716} 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(justify left bottom)
\t\t\t)
\t\t)
\t\t(property "Sheetfile" "{filename}"
\t\t\t(at {x + w / 2} {y + h + 2.54} 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(justify left top)
\t\t\t)
\t\t)
{pins_str}
\t\t(instances
\t\t\t(project "{PROJECT}"
\t\t\t\t(path "/{PARENT}"
\t\t\t\t\t(page "{page}")
\t\t\t\t)
\t\t\t)
\t\t)
\t)
"""


def make_dkmw20f12_sym() -> str:
    src = (AUDIO / "DKMW20.kicad_sym").read_text(encoding="utf-8")
    return (
        src.replace("DKMW20F-15", "DKMW20F-12")
        .replace("±15V/±660mA", "±12V/±830mA")
        .replace("650uF/rail", "800uF/rail")
    )


def make_pt2314_sym() -> str:
    return """(kicad_symbol_lib
\t(version 20251024)
\t(generator "kicad_symbol_editor")
\t(generator_version "10.0")
\t(symbol "PT2314"
\t\t(pin_names
\t\t\t(offset 1.016)
\t\t)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(in_pos_files yes)
\t\t(duplicate_pin_numbers_are_jumpers no)
\t\t(property "Reference" "U"
\t\t\t(at 0 11.43 0)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Value" "PT2314"
\t\t\t(at 0 -11.43 0)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Footprint" "Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm"
\t\t\t(at 0 0 0)
\t\t\t(hide yes)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Description" "PT2314 Bass/Treble tone control I2C — AudioV2 draft"
\t\t\t(at 0 0 0)
\t\t\t(hide yes)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(symbol "PT2314_0_1"
\t\t\t(rectangle
\t\t\t\t(start -7.62 10.16)
\t\t\t\t(end 7.62 -10.16)
\t\t\t\t(stroke
\t\t\t\t\t(width 0.254)
\t\t\t\t\t(type default)
\t\t\t\t)
\t\t\t\t(fill
\t\t\t\t\t(type background)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(symbol "PT2314_1_1"
\t\t\t(pin power_in line
\t\t\t\t(at -10.16 7.62 0)
\t\t\t\t(length 2.54)
\t\t\t\t(name "VCC"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(number "20"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t\t(pin power_in line
\t\t\t\t(at -10.16 -7.62 0)
\t\t\t\t(length 2.54)
\t\t\t\t(name "GND"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(number "10"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t\t(pin bidirectional line
\t\t\t\t(at -10.16 0 0)
\t\t\t\t(length 2.54)
\t\t\t\t(name "SDA"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(number "1"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t\t(pin bidirectional line
\t\t\t\t(at -10.16 2.54 0)
\t\t\t\t(length 2.54)
\t\t\t\t(name "SCL"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(number "2"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t\t(pin passive line
\t\t\t\t(at 10.16 5.08 180)
\t\t\t\t(length 2.54)
\t\t\t\t(name "L_IN"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(number "11"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t\t(pin passive line
\t\t\t\t(at 10.16 2.54 180)
\t\t\t\t(length 2.54)
\t\t\t\t(name "R_IN"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(number "12"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t\t(pin passive line
\t\t\t\t(at 10.16 -2.54 180)
\t\t\t\t(length 2.54)
\t\t\t\t(name "L_OUT"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(number "15"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t\t(pin passive line
\t\t\t\t(at 10.16 -5.08 180)
\t\t\t\t(length 2.54)
\t\t\t\t(name "R_OUT"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(number "16"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(embedded_fonts no)
\t)
)
"""


def make_pga2310_sym() -> str:
    return """(kicad_symbol_lib
\t(version 20251024)
\t(generator "kicad_symbol_editor")
\t(generator_version "10.0")
\t(symbol "PGA2310PA"
\t\t(pin_names
\t\t\t(offset 1.016)
\t\t)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(in_pos_files yes)
\t\t(duplicate_pin_numbers_are_jumpers no)
\t\t(property "Reference" "U"
\t\t\t(at 0 11.43 0)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Value" "PGA2310PA"
\t\t\t(at 0 -13.97 0)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Footprint" "Package_DIP:DIP-16_W7.62mm"
\t\t\t(at 0 0 0)
\t\t\t(hide yes)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Description" "PGA2310PA stereo digital volume SPI — AudioV2 draft"
\t\t\t(at 0 0 0)
\t\t\t(hide yes)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(symbol "PGA2310PA_0_1"
\t\t\t(rectangle
\t\t\t\t(start -7.62 10.16)
\t\t\t\t(end 7.62 -10.16)
\t\t\t\t(stroke
\t\t\t\t\t(width 0.254)
\t\t\t\t\t(type default)
\t\t\t\t)
\t\t\t\t(fill
\t\t\t\t\t(type background)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(symbol "PGA2310PA_1_1"
\t\t\t(pin power_in line
\t\t\t\t(at -10.16 7.62 0)
\t\t\t\t(length 2.54)
\t\t\t\t(name "V+"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(number "16"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t\t(pin power_in line
\t\t\t\t(at -10.16 -7.62 0)
\t\t\t\t(length 2.54)
\t\t\t\t(name "V-"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(number "8"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t\t(pin input line
\t\t\t\t(at -10.16 2.54 0)
\t\t\t\t(length 2.54)
\t\t\t\t(name "SCLK"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(number "2"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t\t(pin input line
\t\t\t\t(at -10.16 0 0)
\t\t\t\t(length 2.54)
\t\t\t\t(name "SDI"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(number "3"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t\t(pin input line
\t\t\t\t(at -10.16 -2.54 0)
\t\t\t\t(length 2.54)
\t\t\t\t(name "CS"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(number "1"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t\t(pin input line
\t\t\t\t(at -10.16 -5.08 0)
\t\t\t\t(length 2.54)
\t\t\t\t(name "MUTE"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(number "15"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t\t(pin output line
\t\t\t\t(at 10.16 5.08 180)
\t\t\t\t(length 2.54)
\t\t\t\t(name "SDO"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(number "4"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t\t(pin passive line
\t\t\t\t(at 10.16 2.54 180)
\t\t\t\t(length 2.54)
\t\t\t\t(name "L_OUT"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(number "6"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t\t(pin passive line
\t\t\t\t(at 10.16 -2.54 180)
\t\t\t\t(length 2.54)
\t\t\t\t(name "R_OUT"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(number "7"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(embedded_fonts no)
\t)
)
"""


def make_ch224_module_sym() -> str:
    return """(kicad_symbol_lib
\t(version 20251024)
\t(generator "kicad_symbol_editor")
\t(generator_version "10.0")
\t(symbol "CH224_50224"
\t\t(pin_names
\t\t\t(offset 1.016)
\t\t)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(in_pos_files yes)
\t\t(duplicate_pin_numbers_are_jumpers no)
\t\t(property "Reference" "U"
\t\t\t(at 0 8.89 0)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Value" "50224_CH224"
\t\t\t(at 0 -8.89 0)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Description" "StrawberryLinux 50224 USB-C PD module (CH224K) — draft frame"
\t\t\t(at 0 0 0)
\t\t\t(hide yes)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(symbol "CH224_50224_0_1"
\t\t\t(rectangle
\t\t\t\t(start -10.16 7.62)
\t\t\t\t(end 10.16 -7.62)
\t\t\t\t(stroke
\t\t\t\t\t(width 0.254)
\t\t\t\t\t(type default)
\t\t\t\t)
\t\t\t\t(fill
\t\t\t\t\t(type background)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(symbol "CH224_50224_1_1"
\t\t\t(pin power_in line
\t\t\t\t(at -12.7 5.08 0)
\t\t\t\t(length 2.54)
\t\t\t\t(name "VBUS"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(number "1"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t\t(pin power_in line
\t\t\t\t(at -12.7 2.54 0)
\t\t\t\t(length 2.54)
\t\t\t\t(name "GND"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(number "2"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t\t(pin power_out line
\t\t\t\t(at 12.7 5.08 180)
\t\t\t\t(length 2.54)
\t\t\t\t(name "12V"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(number "3"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t\t(pin power_out line
\t\t\t\t(at 12.7 2.54 180)
\t\t\t\t(length 2.54)
\t\t\t\t(name "PG"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(number "4"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(embedded_fonts no)
\t)
)
"""


def write_sym_lib_table() -> None:
    content = """(sym_lib_table
\t(version 7)
\t(lib (name "DKMW20") (type "KiCad") (uri "${KIPRJMOD}/../Audio/DKMW20.kicad_sym") (options "") (descr "MEAN WELL DKMW20 (Audio ref)"))
\t(lib (name "BP5293_ROHM") (type "KiCad") (uri "${KIPRJMOD}/../Audio/BP5293_ROHM.kicad_sym") (options "") (descr "ROHM BP5293-50"))
\t(lib (name "ULN2803A") (type "KiCad") (uri "${KIPRJMOD}/../Audio/ULN2803A_HTC_DIP_ONLY.kicad_sym") (options "") (descr "ULN2803A DIP"))
\t(lib (name "AudioV2") (type "KiCad") (uri "${KIPRJMOD}/AudioV2.kicad_sym") (options "") (descr "AudioV2 local symbols"))
)
"""
    (ROOT / "sym-lib-table").write_text(content, encoding="utf-8")


def write_fp_lib_table() -> None:
    content = """(fp_lib_table
\t(version 7)
\t(lib (name "Library") (type "KiCad") (uri "${KIPRJMOD}/../Audio/Library.pretty") (options "") (descr "Audio project footprints"))
)
"""
    (ROOT / "fp-lib-table").write_text(content, encoding="utf-8")


def _sym_body(text: str) -> str:
    """Extract symbol definitions from a one-symbol kicad_sym file."""
    lines = text.splitlines()
    out: list[str] = []
    depth = 0
    started = False
    for line in lines:
        if line.strip().startswith("(symbol ") and not started:
            started = True
        if started:
            out.append(line)
            depth += line.count("(") - line.count(")")
            if depth == 0 and len(out) > 1:
                break
    return "\n".join(out) + "\n"


def write_symbols() -> None:
    merged = (
        "(kicad_symbol_lib\n"
        "\t(version 20251024)\n"
        "\t(generator \"kicad_symbol_editor\")\n"
        "\t(generator_version \"10.0\")\n"
    )
    for maker in (make_dkmw20f12_sym, make_pt2314_sym, make_pga2310_sym, make_ch224_module_sym):
        merged += _sym_body(maker())
    merged += "\t(embedded_fonts no)\n)\n"
    (ROOT / "AudioV2.kicad_sym").write_text(merged, encoding="utf-8")


def power_module_sch() -> str:
    path = f"/{PARENT}/{UUID_POWER_INST}"
    body = f"""\t(lib_symbols)
{text_note(25.4, 25.4, [
    "AudioV2 PowerModule — DRAFT (§8/§9)",
    "U1 DKMW20F-12 ±12V / U2 50224 CH224 USB-C PD",
    "F1 → DKMW20 +Vin. PD_12V → panel PWR SW → PD_12V_SW",
    "U3 LDO TODO: VCC_TONE for PT2314 (+9V or +5V — DS pending)",
])}
{hier_label("+12V_IN", "input", 30.48, 50.8, 180)}
{hier_label("-12V_IN", "input", 30.48, 53.34, 180)}
{hier_label("PD_12V", "output", 200.66, 45.72, 0)}
{hier_label("PD_GND", "bidirectional", 200.66, 48.26, 0)}
{hier_label("PD_12V_SW", "input", 30.48, 55.88, 180)}
{hier_label("+12V_OUT", "output", 200.66, 35.56, 0)}
{hier_label("-12V_OUT", "output", 200.66, 38.1, 0)}
{hier_label("A_GND", "bidirectional", 200.66, 40.64, 0)}
{hier_label("VCC_TONE", "output", 200.66, 43.18, 0)}
{symbol_inst("AudioV2:DKMW20F-12", "U1", "DKMW20F-12", 88.9, 50.8, 0, path)}
{symbol_inst("AudioV2:CH224_50224", "U2", "50224_CH224", 50.8, 50.8, 0, path)}
{symbol_inst("Device:Fuse", "F1", "3A T DNP", 68.58, 50.8, 0, path)}
{symbol_inst("Regulator_Linear:AP1117-33", "U3", "LDO_VCC_TONE TODO", 127.0, 50.8, 0, path)}
{symbol_inst("Connector:USB_C_Receptacle_USB2.0", "J1", "USB-C PD in", 25.4, 50.8, 0, path)}
{symbol_inst("Connector:Conn_01x02_Pin", "J_PD", "PD_12V to panel", 165.1, 45.72, 0, path)}
{symbol_inst("Connector:Conn_01x03_Pin", "J202", "±12+A_GND out", 165.1, 35.56, 0, path)}
"""
    return sch_open(UUID_POWER_FILE, body)


def relay_board_sch() -> str:
    path_a = f"/{PARENT}/{UUID_RELAY_A}"
    path_b = f"/{PARENT}/{UUID_RELAY_B}"
    labels = []
    for n in range(1, 6):
        labels.append(hier_label(f"AMP{n}_L", "bidirectional", 200.66, 30.48 + n * 5.08, 0))
        labels.append(hier_label(f"AMP{n}_R", "bidirectional", 210.82, 30.48 + n * 5.08, 0))
        labels.append(hier_label(f"AMP{n}_V+", "output", 220.98, 30.48 + n * 5.08, 0))
        labels.append(hier_label(f"AMP{n}_V-", "output", 231.14, 30.48 + n * 5.08, 0))
    body = f"""\t(lib_symbols)
{text_note(25.4, 25.4, [
    "RelayBoard — 5ch template (§11 Q1-B)",
    "MCP23017 @0x20 (Board A) / @0x21 (Board B — same sch, addr strap note)",
    "AZ850 latching + ULN2803. NO child Pico.",
    "COMMON_LR_OUT → ControlPanel PT2314 input",
])}
{hier_label("I2C_SDA", "bidirectional", 30.48, 40.64, 180)}
{hier_label("I2C_SCL", "bidirectional", 30.48, 43.18, 180)}
{hier_label("3V3", "input", 30.48, 45.72, 180)}
{hier_label("D_GND", "input", 30.48, 48.26, 180)}
{hier_label("COMMON_L", "output", 200.66, 88.9, 0)}
{hier_label("COMMON_R", "output", 200.66, 91.44, 0)}
{hier_label("A_GND", "bidirectional", 200.66, 93.98, 0)}
{"".join(labels)}
{symbol_inst("Interface_Expansion:MCP23017-E/SP", "U1", "MCP23017 addr0x20", 63.5, 50.8, 0, path_a, [("Addr", "0x20 A / 0x21 B")])}
{symbol_inst("ULN2803A:ULN2803A", "U2", "ULN2803A", 88.9, 50.8, 0, path_a)}
{symbol_inst("Relay:AZ850P2-x", "K1", "AZ850 CH1 audio", 114.3, 40.64, 0, path_a)}
{symbol_inst("Relay:AZ850P2-x", "K2", "AZ850 CH1 pwr", 114.3, 50.8, 0, path_a)}
{symbol_inst("Relay:AZ850P2-x", "K3", "AZ850 CH2 audio", 127.0, 40.64, 0, path_a)}
{symbol_inst("Relay:AZ850P2-x", "K4", "AZ850 CH2 pwr", 127.0, 50.8, 0, path_a)}
{symbol_inst("Relay:AZ850P2-x", "K5", "AZ850 CH3 audio", 139.7, 40.64, 0, path_a)}
{symbol_inst("Connector:Conn_01x04_Pin", "J_I2C", "I2C to Control", 25.4, 43.18, 0, path_a)}
{symbol_inst("Connector:Conn_01x03_Pin", "J_COMMON", "COMMON_LR_OUT", 165.1, 90.17, 0, path_a)}
{symbol_inst("Connector:Screw_Terminal_01x02", "J_AMP1", "AMP1 L/R", 165.1, 35.56, 0, path_a)}
"""
    # Second instance path for B (same file, different parent sheet)
    _ = path_b
    return sch_open(UUID_RELAY_FILE, body)


def control_panel_sch() -> str:
    path = f"/{PARENT}/{UUID_CONTROL_INST}"
    encs = [
        ("ENC_CH", "J_ENC1", "GP0/1/12", 40.64),
        ("ENC_HP", "J_ENC2", "GP2/3/13", 55.88),
        ("ENC_LINE", "J_ENC3", "GP4/5/14", 71.12),
        ("ENC_DEST", "J_ENC4", "GP6/7/15", 86.36),
        ("ENC_BASS", "J_ENC5", "GP8/9/26", 101.6),
        ("ENC_TREBLE", "J_ENC6", "GP10/11/27", 116.84),
    ]
    enc_syms = "\n".join(
        symbol_inst("Connector:Conn_01x05_Pin", j, f"{name} {gps}", 35.56, y, 0, path)
        for name, j, gps, y in encs
    )
    body = f"""\t(lib_symbols)
{text_note(25.4, 25.4, [
    "ControlPanel — DRAFT (§10)",
    "Pico 2 / ENC×6 GPIO direct / SSD1306 I2C0",
    "PT2314 tone / PGA2310PA×2 SPI daisy / BP5293 +5V",
    "PWR SW + 12V LED on PD_12V (§9)",
])}
{hier_label("COMMON_L", "input", 30.48, 130.0, 180)}
{hier_label("COMMON_R", "input", 30.48, 132.54, 180)}
{hier_label("I2C_SDA", "bidirectional", 30.48, 135.08, 180)}
{hier_label("I2C_SCL", "bidirectional", 30.48, 137.62, 180)}
{hier_label("+12V", "input", 30.48, 140.16, 180)}
{hier_label("-12V", "input", 30.48, 142.7, 180)}
{hier_label("A_GND", "bidirectional", 30.48, 145.24, 180)}
{hier_label("D_GND", "input", 30.48, 147.78, 180)}
{hier_label("PD_12V", "input", 30.48, 150.32, 180)}
{hier_label("PD_12V_SW", "output", 200.66, 150.32, 0)}
{hier_label("PD_GND", "bidirectional", 200.66, 152.86, 0)}
{hier_label("PGA_HP_L", "output", 200.66, 130.0, 0)}
{hier_label("PGA_HP_R", "output", 200.66, 132.54, 0)}
{hier_label("PGA_LINE_L", "output", 200.66, 135.08, 0)}
{hier_label("PGA_LINE_R", "output", 200.66, 137.62, 0)}
{hier_label("VCC_TONE", "input", 30.48, 155.42, 180)}
{symbol_inst("MCU_Module:Raspberry_Pi_Pico", "U1", "Pico 2 / RP2350", 88.9, 88.9, 0, path)}
{symbol_inst("AudioV2:PT2314", "U2", "PT2314 tone", 127.0, 130.0, 0, path)}
{symbol_inst("AudioV2:PGA2310PA", "U3", "PGA2310 HP", 127.0, 88.9, 0, path)}
{symbol_inst("AudioV2:PGA2310PA", "U4", "PGA2310 LINE", 127.0, 101.6, 0, path)}
{symbol_inst("BP5293_ROHM:BP5293-50", "U5", "BP5293-50 +5V", 63.5, 88.9, 0, path)}
{symbol_inst("Display_Graphic:SSD1306-128x64", "U6", "OLED ctrl I2C", 101.6, 88.9, 0, path)}
{symbol_inst("Switch:SW_SPST", "SW1", "PWR SW", 165.1, 150.32, 0, path)}
{symbol_inst("Device:LED", "D1", "12V panel LED", 177.8, 152.86, 0, path)}
{symbol_inst("Device:R", "R1", "DNP C/R PT2314", 139.7, 130.0, 0, path)}
{symbol_inst("Device:C", "C1", "DNP C/R PT2314", 152.4, 130.0, 0, path)}
{enc_syms}
"""
    return sch_open(UUID_CONTROL_FILE, body)


def output_stage_sch() -> str:
    path = f"/{PARENT}/{UUID_OUTPUT_INST}"
    body = f"""\t(lib_symbols)
{text_note(25.4, 25.4, [
    "OutputStage — DRAFT (§11 Q2-A, same PCB as ControlPanel)",
    "DEST latching relays: LINE / PHONE / MUTE (AZ850 ×2~3)",
    "Drive: MCP23017/ULN on RelayBoard OR spare ULN on Control — TODO review",
    "Startup default: LINE",
])}
{hier_label("PGA_HP_L", "input", 30.48, 50.8, 180)}
{hier_label("PGA_HP_R", "input", 30.48, 53.34, 180)}
{hier_label("PGA_LINE_L", "input", 30.48, 55.88, 180)}
{hier_label("PGA_LINE_R", "input", 30.48, 58.42, 180)}
{hier_label("+12V", "input", 30.48, 60.96, 180)}
{hier_label("-12V", "input", 30.48, 63.5, 180)}
{hier_label("A_GND", "bidirectional", 30.48, 66.04, 180)}
{hier_label("PHONE_L", "output", 200.66, 45.72, 0)}
{hier_label("PHONE_R", "output", 200.66, 48.26, 0)}
{hier_label("LINE_L", "output", 200.66, 50.8, 0)}
{hier_label("LINE_R", "output", 200.66, 53.34, 0)}
{hier_label("MUTE", "output", 200.66, 55.88, 0)}
{symbol_inst("Relay:AZ850P2-x", "K1", "DEST LINE", 88.9, 50.8, 0, path)}
{symbol_inst("Relay:AZ850P2-x", "K2", "DEST PHONE", 101.6, 50.8, 0, path)}
{symbol_inst("Relay:AZ850P2-x", "K3", "DEST MUTE", 114.3, 50.8, 0, path)}
{symbol_inst("ULN2803A:ULN2803A", "U1", "ULN spare/TODO", 63.5, 50.8, 0, path)}
{symbol_inst("Connector:Screw_Terminal_01x02", "J_HP", "to Audio HP Buffer", 165.1, 45.72, 0, path)}
{symbol_inst("Connector:Screw_Terminal_01x02", "J_LINE", "LINE OUT", 165.1, 50.8, 0, path)}
"""
    return sch_open(UUID_OUTPUT_FILE, body)


def parent_sch() -> str:
    # Global power bus labels on parent
    power_pins = [
        ("+12V_IN", "input", 40.64, 50.8, 180),
        ("-12V_IN", "input", 40.64, 53.34, 180),
        ("PD_12V", "output", 60.96, 45.72, 0),
        ("PD_GND", "bidirectional", 60.96, 48.26, 0),
        ("PD_12V_SW", "input", 40.64, 55.88, 180),
        ("+12V_OUT", "output", 60.96, 35.56, 0),
        ("-12V_OUT", "output", 60.96, 38.1, 0),
        ("A_GND", "bidirectional", 60.96, 40.64, 0),
        ("VCC_TONE", "output", 60.96, 43.18, 0),
    ]
    relay_pins = [
        ("I2C_SDA", "bidirectional", 110.0, 40.0, 180),
        ("I2C_SCL", "bidirectional", 110.0, 42.54, 180),
        ("3V3", "input", 110.0, 45.08, 180),
        ("D_GND", "input", 110.0, 47.62, 180),
        ("COMMON_L", "output", 140.0, 40.0, 0),
        ("COMMON_R", "output", 140.0, 42.54, 0),
        ("A_GND", "bidirectional", 140.0, 45.08, 0),
    ]
    control_pins = [
        ("COMMON_L", "input", 170.0, 40.0, 180),
        ("COMMON_R", "input", 170.0, 42.54, 180),
        ("I2C_SDA", "bidirectional", 170.0, 45.08, 180),
        ("I2C_SCL", "bidirectional", 170.0, 47.62, 180),
        ("+12V", "input", 170.0, 50.16, 180),
        ("-12V", "input", 170.0, 52.7, 180),
        ("A_GND", "bidirectional", 170.0, 55.24, 180),
        ("D_GND", "input", 170.0, 57.78, 180),
        ("PD_12V", "input", 170.0, 60.32, 180),
        ("PD_12V_SW", "output", 200.0, 60.32, 0),
        ("PD_GND", "bidirectional", 200.0, 62.86, 0),
        ("PGA_HP_L", "output", 200.0, 40.0, 0),
        ("PGA_HP_R", "output", 200.0, 42.54, 0),
        ("PGA_LINE_L", "output", 200.0, 45.08, 0),
        ("PGA_LINE_R", "output", 200.0, 47.62, 0),
        ("VCC_TONE", "input", 170.0, 65.0, 180),
    ]
    output_pins = [
        ("PGA_HP_L", "input", 230.0, 40.0, 180),
        ("PGA_HP_R", "input", 230.0, 42.54, 180),
        ("PGA_LINE_L", "input", 230.0, 45.08, 180),
        ("PGA_LINE_R", "input", 230.0, 47.62, 180),
        ("+12V", "input", 230.0, 50.16, 180),
        ("-12V", "input", 230.0, 52.7, 180),
        ("A_GND", "bidirectional", 230.0, 55.24, 180),
        ("PHONE_L", "output", 260.0, 40.0, 0),
        ("PHONE_R", "output", 260.0, 42.54, 0),
        ("LINE_L", "output", 260.0, 45.08, 0),
        ("LINE_R", "output", 260.0, 47.62, 0),
        ("MUTE", "output", 260.0, 50.16, 0),
    ]
    sheets = (
        sheet_block(UUID_POWER_INST, "PowerModule", "PowerModule.kicad_sch", 35.56, 35.56, 30.48, 25.4, power_pins, "2")
        + sheet_block(UUID_RELAY_A, "RelayBoard_A", "RelayBoard.kicad_sch", 88.9, 35.56, 55.88, 30.48, relay_pins, "3")
        + sheet_block(UUID_RELAY_B, "RelayBoard_B", "RelayBoard.kicad_sch", 88.9, 73.66, 55.88, 30.48, relay_pins, "4")
        + sheet_block(UUID_CONTROL_INST, "ControlPanel", "ControlPanel.kicad_sch", 152.4, 35.56, 55.88, 35.56, control_pins, "5")
        + sheet_block(UUID_OUTPUT_INST, "OutputStage", "OutputStage.kicad_sch", 215.9, 35.56, 50.8, 25.4, output_pins, "6")
    )
    body = f"""\t(lib_symbols)
{text_note(25.4, 20.32, [
    "AudioV2Case — hierarchy parent (D1.5 draft)",
    "Amp×10 / HeadphoneBuffer / MeasurementADC = Audio/ manufactured — NOT on this schematic",
    "See WIRING.md for off-sheet terminal connections",
    "DRAFT — circuit review pending (Q3 I2C topology, etc.)",
])}
{global_label("+12V", 127.0, 100.0, 0)}
{global_label("-12V", 127.0, 102.54, 0)}
{global_label("A_GND", 127.0, 105.08, 0)}
{global_label("I2C_SDA", 127.0, 107.62, 0)}
{global_label("I2C_SCL", 127.0, 110.16, 0)}
{sheets}
"""
    return sch_open(PARENT, body)


def write_kicad_pro() -> None:
    src = json.loads((AUDIO / "AudioCase.kicad_pro").read_text(encoding="utf-8"))
    src["schematic"]["legacy_lib_dir"] = ""
    src["schematic"]["legacy_lib_list"] = []
    src["schematic"]["top_level_sheets"] = [
        {
            "filename": "AudioV2Case.kicad_sch",
            "name": "AudioV2Case",
            "uuid": PARENT,
        }
    ]
    src["schematic"]["used_designators"] = ""
    src["sheets"] = [
        [PARENT, "AudioV2Case"],
        [UUID_POWER_INST, "PowerModule"],
        [UUID_RELAY_A, "RelayBoard_A"],
        [UUID_RELAY_B, "RelayBoard_B"],
        [UUID_CONTROL_INST, "ControlPanel"],
        [UUID_OUTPUT_INST, "OutputStage"],
    ]
    (ROOT / "AudioV2Case.kicad_pro").write_text(json.dumps(src, indent=2) + "\n", encoding="utf-8")


def write_wiring_md() -> None:
    content = """# AudioV2 箱配線 IF 素案（draft）

**目的:** KiCad 図外（`Audio/` 流用基板）との端子接続一覧。回路レビュー前のたたき台。

## 電源星型（PowerModule → 各所）

| Net | 源 | 先 | 形式 |
|---|---|---|---|
| `+12V` | PowerModule J202-1 | RelayBoard×2, ControlPanel, Amp×10 `V+` 端子 | 端子台 3P 幹線 |
| `-12V` | PowerModule J202-2 | 同上 `V-` | 同上 |
| `A_GND` | PowerModule J202-3 | 全アナログ島（NetTie 一点 — **位置未決**） | 端子台 |
| `PD_12V` | PowerModule J_PD | ControlPanel PWR SW 入力 | 2P ケーブル |
| `PD_12V_SW` | ControlPanel SW 出力 | PowerModule F1/DKMW20 +Vin | 2P 戻り |
| `PD_GND` | CH224/DKMW −Vin | Panel LED 戻り | 2P |
| `VCC_TONE` | PowerModule LDO | ControlPanel PT2314 | 2P or 同一 PCB |

## デジタル / I²C（Q3 拓扑 **保留**）

| Net | 源 | 先 | 備考 |
|---|---|---|---|
| `I2C_SDA/SCL` | ControlPanel Pico GP20/21 | RelayBoard_A MCP23017, RelayBoard_B, SSD1306, PT2314 | daisy vs スター — **未決** |
| `3V3` / `D_GND` | ControlPanel BP5293 | RelayBoard J_I2C | |

## 音声幹線

| Net | 源 | 先 | 備考 |
|---|---|---|---|
| `COMMON_L/R` | RelayBoard_A/B 合流 → Control PT2314 入力 | §11.8 共通バス | 4P コネクタ想定 |
| PT2314 OUT → | ControlPanel | **Audio/ Amp×10 入力端子**（図外） | 箱配線 |
| Amp 出力（選択後）→ | Audio/ 製造済み | ControlPanel PGA2310 入力 | 図外 |
| `PGA_HP_L/R` | ControlPanel U3 | OutputStage → **Audio/ HeadphoneBuffer** | 0 Ω 固定パッド廃止 |
| `PGA_LINE_L/R` | ControlPanel U4 | OutputStage → LINE 端子 | |
| `PHONE_L/R` | OutputStage J_HP | Audio/ HeadphoneBuffer 入力 | |
| `LINE_L/R` | OutputStage J_LINE | 前面 LINE OUT | |

## Audio/ 流用（図に載せない）

| 基板 | 接続 |
|---|---|
| AmpModule ×10 | RelayBoard `AMP{n}_L/R`, `AMP{n}_V±` |
| HeadphoneBufferModule | OutputStage `PHONE_L/R`, ±12V |
| AdcBuffer / MeasurementADC | ±12V + 測定タップ（**位置 MD で固定**） |

## 意図的未決

- **Q3** I²C 拓扑（daisy / スター）
- GND NetTie 物理位置
- DEST リレー本数・駆動元（Control ULN 余裕 vs Relay MCP ビット）
- PT2314 外部 C/R 値
- ERC / ネットリスト整合
"""
    (ROOT / "WIRING.md").write_text(content, encoding="utf-8")


def update_readme() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    line = "- **KiCad 素案あり** — `AudioV2Case.kicad_pro` + 子シート 4 枚（draft・要レビュー）"
    if "KiCad 素案あり" not in readme:
        readme = readme.replace(
            "回路図（`.kicad_sch` / `.kicad_pro`）は未作成。",
            line + "\n",
        )
        readme = readme.replace(
            "- **次:** KiCad 起こし可（Q3 I²C・Q2 物理はレイアウト時）",
            "- **次:** 回路レビュー（Q3 I²C・ピンアサイン・ERC）",
        )
    (ROOT / "README.md").write_text(readme, encoding="utf-8")


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    (ROOT / "scripts").mkdir(exist_ok=True)
    write_sym_lib_table()
    write_fp_lib_table()
    write_symbols()
    (ROOT / "PowerModule.kicad_sch").write_text(power_module_sch(), encoding="utf-8")
    (ROOT / "RelayBoard.kicad_sch").write_text(relay_board_sch(), encoding="utf-8")
    (ROOT / "ControlPanel.kicad_sch").write_text(control_panel_sch(), encoding="utf-8")
    (ROOT / "OutputStage.kicad_sch").write_text(output_stage_sch(), encoding="utf-8")
    (ROOT / "AudioV2Case.kicad_sch").write_text(parent_sch(), encoding="utf-8")
    write_kicad_pro()
    write_wiring_md()
    update_readme()
    print("Generated AudioV2 KiCad scaffold under", ROOT)


if __name__ == "__main__":
    main()
