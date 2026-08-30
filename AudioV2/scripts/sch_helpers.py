"""KiCad schematic helpers — grid snap, pin coords, lib_symbols embed."""

from __future__ import annotations

import math
import re
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KICAD_SYM_ROOT = Path("/tmp/kicad-symbols")


def new_uid() -> str:
    return str(uuid.uuid4())


def grid(x: float) -> float:
    return round(x / 2.54) * 2.54


def _rotate_point(ox: float, oy: float, rot: int) -> tuple[float, float]:
    if rot == 0:
        return ox, oy
    if rot == 90:
        return -oy, ox
    if rot == 180:
        return -ox, -oy
    if rot == 270:
        return oy, -ox
    return ox, oy


def pin_connect(
    sx: float,
    sy: float,
    sym_rot: int,
    px: float,
    py: float,
    pin_angle: int,
    length: float,
) -> tuple[float, float]:
    """Absolute wire endpoint at the pin tip (symbol Y is flipped on schematic)."""
    rad = math.radians(pin_angle)
    tip_x = px + length * math.cos(rad)
    tip_y = py + length * math.sin(rad)
    rx, ry = _rotate_point(tip_x, -tip_y, sym_rot)
    return sx + rx, sy + ry


def _pins(
    sx: float,
    sy: float,
    sym_rot: int,
    defs: list[tuple[float, float, int, float]],
) -> list[tuple[float, float]]:
    return [pin_connect(sx, sy, sym_rot, px, py, ang, ln) for px, py, ang, ln in defs]


def cap_pins(cx: float, cy: float, rot: int = 0) -> tuple[tuple[float, float], tuple[float, float]]:
    p1, p2 = _pins(
        cx,
        cy,
        rot,
        [(0, 3.81, 270, 2.794), (0, -3.81, 90, 2.794)],
    )
    return p1, p2


def fuse_pins(fx: float, fy: float, rot: int = 90) -> tuple[tuple[float, float], tuple[float, float]]:
    p1, p2 = _pins(
        fx,
        fy,
        rot,
        [(0, 3.81, 270, 1.27), (0, -3.81, 90, 1.27)],
    )
    return p1, p2


def lm7809_pins(ux: float, uy: float, rot: int = 0) -> dict[str, tuple[float, float]]:
    vi, gnd, vo = _pins(
        ux,
        uy,
        rot,
        [(-7.62, 0, 0, 2.54), (0, -7.62, 90, 2.54), (7.62, 0, 180, 2.54)],
    )
    return {"VI": vi, "GND": gnd, "VO": vo}


def dkmw_pins(sx: float, sy: float, rot: int = 0) -> dict[str, tuple[float, float]]:
    keys = ("1", "2", "3", "4", "5", "6")
    defs = [
        (-12.7, -8.89, 0, 2.54),
        (-12.7, -5.08, 0, 2.54),
        (12.7, -6.35, 180, 2.54),
        (12.7, -8.89, 180, 2.54),
        (12.7, -11.43, 180, 2.54),
        (-12.7, -13.97, 0, 2.54),
    ]
    pts = _pins(sx, sy, rot, defs)
    return dict(zip(keys, pts, strict=True))


def ch224_pins(sx: float, sy: float, rot: int = 0) -> dict[str, tuple[float, float]]:
    keys = ("VBUS", "GND", "12V", "PG")
    defs = [
        (-12.7, 5.08, 0, 2.54),
        (-12.7, 2.54, 0, 2.54),
        (12.7, 5.08, 180, 2.54),
        (12.7, 2.54, 180, 2.54),
    ]
    pts = _pins(sx, sy, rot, defs)
    return dict(zip(keys, pts, strict=True))


def usb16_pins(jx: float, jy: float, rot: int = 0) -> dict[str, tuple[float, float]]:
    vbus, gnd = _pins(
        jx,
        jy,
        rot,
        [(15.24, 15.24, 180, 5.08), (0, -22.86, 90, 5.08)],
    )
    return {"VBUS": vbus, "GND": gnd}


def conn02_pins(cx: float, cy: float, rot: int = 0) -> tuple[tuple[float, float], tuple[float, float]]:
    p1, p2 = _pins(
        cx,
        cy,
        rot,
        [(5.08, 0, 180, 3.81), (5.08, -2.54, 180, 3.81)],
    )
    return p1, p2


def conn03_pins(
    cx: float, cy: float, rot: int = 0
) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
    p1, p2, p3 = _pins(
        cx,
        cy,
        rot,
        [(5.08, 2.54, 180, 3.81), (5.08, 0, 180, 3.81), (5.08, -2.54, 180, 3.81)],
    )
    return p1, p2, p3


def pin_uuid_block(numbers: list[str]) -> str:
    lines = []
    for n in numbers:
        lines.append(
            f'\t\t(pin "{n}"\n\t\t\t(uuid "{new_uid()}")\n\t\t)'
        )
    return "\n".join(lines)


PIN_COUNTS: dict[str, list[str]] = {
    "Device:C": ["1", "2"],
    "Device:R": ["1", "2"],
    "Device:Fuse": ["1", "2"],
    "Device:LED": ["1", "2"],
    "Device:RotaryEncoder_Switch": ["A", "B", "C", "S1", "S2"],
    "Switch:SW_SPST": ["1", "2"],
    "Regulator_Linear:LM7809_TO220": ["1", "2", "3"],
    "Connector:USB_C_Receptacle_USB2.0_16P": [
        "A1", "A4", "A5", "A6", "A7", "A8", "A9", "A12",
        "B1", "B4", "B5", "B6", "B7", "B8", "B9", "B12", "SH",
    ],
    "Connector:Conn_01x02_Pin": ["1", "2"],
    "Connector:Conn_01x03_Pin": ["1", "2", "3"],
    "Connector:Conn_01x04_Pin": ["1", "2", "3", "4"],
    "Connector:Screw_Terminal_01x02": ["1", "2"],
    "AudioV2:CH224_50224": ["1", "2", "3", "4"],
    "AudioV2:DKMW20F-12": ["1", "2", "3", "4", "5", "6"],
    "AudioV2:PT2314": ["1", "2", "3", "4", "10", "11", "12", "15", "16", "20"],
    "BP5293_ROHM:BP5293-50": ["1", "2", "3"],
    "Relay:AZ850P2-x": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
    "Transistor_Array:ULN2803A": [str(i) for i in range(1, 19)],
}

# Schematic lib_id -> (source_lib, source_sym, extends chain base-first)
SYMBOL_SOURCES: dict[str, tuple[str, str, list[tuple[str, str]]]] = {
    "Interface_Expansion:MCP23017-E/SP": (
        "Interface_Expansion",
        "MCP23017x-x-SP",
        [("Interface_Expansion", "MCP23017x-x-SO")],
    ),
    "MCU_Module:Raspberry_Pi_Pico": ("MCU_Module", "RaspberryPi_Pico", []),
    "MCU_Module:RaspberryPi_Pico": ("MCU_Module", "RaspberryPi_Pico", []),
    "Display_Graphic:SSD1306-128x64": ("Display_Graphic", "ER_OLEDM0.91_1x-I2C", []),
    "Audio:PGA2310PA": ("Audio", "PGA2310PA", [("Audio", "PGA2310UA")]),
    "Regulator_Linear:LM7809_TO220": (
        "Regulator_Linear",
        "LM7809_TO220",
        [("Regulator_Linear", "LM7805_TO220")],
    ),
    "BP5293_ROHM:BP5293-50": ("BP5293_ROHM", "BP5293-50", []),
}


def _read_symbol_text(lib: str, name: str) -> str:
    if lib == "AudioV2":
        return (ROOT / "AudioV2.kicad_sym").read_text(encoding="utf-8")
    if lib == "BP5293_ROHM":
        return (ROOT.parent / "Audio" / "BP5293_ROHM.kicad_sym").read_text(encoding="utf-8")
    return _read_packed_or_dir(lib, name)


def _pin_numbers_from_sym_text(text: str, sym_name: str) -> list[str]:
    m = re.search(rf'\(symbol "{re.escape(sym_name)}"', text)
    if not m:
        return []
    start = m.start()
    depth = 0
    end = start
    for i in range(start, len(text)):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    chunk = text[start:end]
    nums = re.findall(r'\(number "([^"]+)"', chunk)
    seen: set[str] = set()
    out: list[str] = []
    for n in nums:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def pin_numbers_for(lib_id: str) -> list[str]:
    if lib_id in PIN_COUNTS:
        return PIN_COUNTS[lib_id]
    _, embed_name = lib_id.split(":", 1)
    if lib_id in SYMBOL_SOURCES:
        file_lib, file_name, extends = SYMBOL_SOURCES[lib_id]
    else:
        file_lib, file_name = lib_id.split(":", 1)
        extends = []
    merged: list[str] = []
    seen: set[str] = set()
    for elib, ename in extends:
        for p in _pin_numbers_from_sym_text(_read_symbol_text(elib, ename), ename):
            if p not in seen:
                seen.add(p)
                merged.append(p)
    for p in _pin_numbers_from_sym_text(_read_symbol_text(file_lib, file_name), file_name):
        if p not in seen:
            seen.add(p)
            merged.append(p)
    return merged or ["1"]


def _extract_symbol_body(
    kicad_sym_text: str,
    lib_name: str,
    embed_name: str,
    file_name: str | None = None,
) -> str:
    """Turn (symbol \"FILE\" ...) into embeddable (symbol \"Lib:EMBED\" ...)."""
    src = file_name or embed_name
    m = re.search(rf'\(symbol "{re.escape(src)}"', kicad_sym_text)
    if not m:
        raise ValueError(f"symbol {src} not found")
    start = m.start()
    depth = 0
    for i in range(start, len(kicad_sym_text)):
        if kicad_sym_text[i] == "(":
            depth += 1
        elif kicad_sym_text[i] == ")":
            depth -= 1
            if depth == 0:
                body = kicad_sym_text[start : i + 1]
                body = body.replace(f'(symbol "{src}"', f'(symbol "{lib_name}:{embed_name}"', 1)
                if src != embed_name:
                    body = body.replace(f'"{src}_', f'"{embed_name}_')
                return body
    raise ValueError(f"unbalanced symbol {src}")


def _read_packed_or_dir(lib: str, sym_name: str) -> str:
    symdir = KICAD_SYM_ROOT / f"{lib}.kicad_symdir" / f"{sym_name}.kicad_sym"
    if symdir.is_file():
        return symdir.read_text(encoding="utf-8")
    packed = KICAD_SYM_ROOT / f"{lib}.kicad_sym"
    if packed.is_file():
        return packed.read_text(encoding="utf-8")
    raise FileNotFoundError(symdir)


def _sanitize_embed_body(body: str) -> str:
    """KiCad 10 sch rejects some legacy symbol stroke types."""
    return body.replace("(type solid)", "(type default)")


def _indent_symbol_body(body: str) -> str:
    return "\n".join(("\t" + ln if ln.strip() else ln) for ln in body.splitlines())


def embed_lib_symbols(lib_ids: list[str]) -> str:
    """Build (lib_symbols ...) block with embedded symbol definitions."""
    chunks: list[str] = ["\t(lib_symbols"]
    seen: set[str] = set()

    for lib_id in lib_ids:
        if lib_id in seen:
            continue
        seen.add(lib_id)
        lib, embed_name = lib_id.split(":", 1)
        if lib_id in SYMBOL_SOURCES:
            file_lib, file_name, extends = SYMBOL_SOURCES[lib_id]
        else:
            file_lib, file_name = lib, embed_name
            extends = []
        for elib, ename in extends:
            ext_key = f"{elib}:{ename}"
            if ext_key in seen:
                continue
            seen.add(ext_key)
            text = _read_symbol_text(elib, ename)
            body = _extract_symbol_body(text, elib, ename)
            chunks.append(_indent_symbol_body(_sanitize_embed_body(body)))
        text = _read_symbol_text(file_lib, file_name)
        body = _extract_symbol_body(text, lib, embed_name, file_name)
        chunks.append(_indent_symbol_body(_sanitize_embed_body(body)))

    chunks.append("\t)")
    return "\n".join(chunks)


def symbol_inst_v10(
    lib_id: str,
    ref: str,
    value: str,
    x: float,
    y: float,
    rot: int,
    parent_path: str,
    project: str = "AudioV2Case",
    extra_props: list[tuple[str, str]] | None = None,
) -> str:
    from generate_kicad_scaffold import sym_prop  # noqa: WPS433

    props = [
        sym_prop("Reference", ref, x, y - 2.54),
        sym_prop("Value", value, x, y + 2.54),
        sym_prop("Footprint", "", 0, 0, hide=True),
        sym_prop("Datasheet", "", 0, 0, hide=True),
        sym_prop("Description", "", 0, 0, hide=True),
    ]
    if extra_props:
        for n, v in extra_props:
            props.append(sym_prop(n, v, 0, 0, hide=True))
    pin_block = pin_uuid_block(pin_numbers_for(lib_id))
    props_str = "\n".join(props)
    return f"""\t(symbol
\t\t(lib_id "{lib_id}")
\t\t(at {grid(x)} {grid(y)} {rot})
\t\t(unit 1)
\t\t(body_style 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(in_pos_files yes)
\t\t(dnp no)
\t\t(fields_autoplaced yes)
\t\t(uuid "{new_uid()}")
{props_str}
{pin_block}
\t\t(instances
\t\t\t(project "{project}"
\t\t\t\t(path "{parent_path}"
\t\t\t\t\t(reference "{ref}")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)
"""
