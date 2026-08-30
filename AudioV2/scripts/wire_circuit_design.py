#!/usr/bin/env python3
"""Wire AudioV2 schematics per CIRCUIT_DESIGN.md — placement + net connections."""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate_kicad_scaffold import (  # noqa: E402
    PARENT,
    PROJECT,
    UUID_CONTROL_FILE,
    UUID_CONTROL_INST,
    UUID_OUTPUT_FILE,
    UUID_OUTPUT_INST,
    UUID_POWER_FILE,
    UUID_POWER_INST,
    hier_label,
    sch_open,
    sheet_block,
    symbol_inst,
    text_note,
    uid,
    global_label,
)

PATH_CTRL = f"/{PARENT}/{UUID_CONTROL_INST}"
PATH_PWR = f"/{PARENT}/{UUID_POWER_INST}"
PATH_OUT = f"/{PARENT}/{UUID_OUTPUT_INST}"


def pin(sx: float, sy: float, px: float, py: float) -> tuple[float, float]:
    return sx + px, sy + py


def wire(x1: float, y1: float, x2: float, y2: float) -> str:
    return f"""\t(wire
\t\t(pts
\t\t\t(xy {x1} {y1}) (xy {x2} {y2})
\t\t)
\t\t(stroke
\t\t\t(width 0)
\t\t\t(type default)
\t\t)
\t\t(uuid "{uid()}")
\t)
"""


def junction(x: float, y: float) -> str:
    return f"""\t(junction
\t\t(at {x} {y})
\t\t(diameter 0)
\t\t(color 0 0 0 0)
\t\t(uuid "{uid()}")
\t)
"""


def label(name: str, x: float, y: float, angle: int = 0) -> str:
    return f"""\t(label "{name}"
\t\t(at {x} {y} {angle})
\t\t(effects
\t\t\t(font
\t\t\t\t(size 1.27 1.27)
\t\t\t)
\t\t\t(justify left bottom)
\t\t)
\t\t(uuid "{uid()}")
\t)
"""


def pwr_flag(x: float, y: float) -> str:
    return f"""\t(symbol
\t\t(lib_id "power:PWR_FLAG")
\t\t(at {x} {y} 0)
\t\t(unit 1)
\t\t(exclude_from_sim yes)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(fields_autoplaced yes)
\t\t(uuid "{uid()}")
\t\t(property "Reference" "#FLG"
\t\t\t(at {x} {y - 3.81} 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(hide yes)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Value" "PWR_FLAG"
\t\t\t(at {x} {y + 3.81} 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(hide yes)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Footprint" ""
\t\t\t(at {x} {y} 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(hide yes)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Datasheet" ""
\t\t\t(at {x} {y} 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(hide yes)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Description" "Power flag"
\t\t\t(at {x} {y} 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(hide yes)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(instances
\t\t\t(project "{PROJECT}"
\t\t\t\t(path "{PATH_CTRL}"
\t\t\t\t\t(reference "#FLG{uid().hex[:4]}")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)
"""


def cap(ref: str, val: str, x: float, y: float, path: str) -> str:
    return symbol_inst("Device:C", ref, val, x, y, 0, path)


def res(ref: str, val: str, x: float, y: float, path: str) -> str:
    return symbol_inst("Device:R", ref, val, x, y, 0, path)


def pt2314_pin(sx: float, sy: float, index: int) -> tuple[float, float]:
    """index 0..27 left pins 0-13, right 14-27 per generate script layout."""
    if index < 14:
        return pin(sx, sy, -12.7, 16.51 - index * 2.54)
    return pin(sx, sy, 12.7, 16.51 - (index - 14) * 2.54)


def pga2310_pin(sx: float, sy: float, num: str) -> tuple[float, float]:
    """Pin offsets for KiCad standard lib Audio:PGA2310PA (extends PGA2310UA)."""
    table = {
        "1": (-12.7, 5.08),  # ZCEN
        "2": (-12.7, -2.54),  # ~CS
        "3": (-12.7, 0),  # SDI
        "4": (-5.08, 27.94),  # V_D+
        "5": (-5.08, -27.94),  # DGND
        "6": (-12.7, 2.54),  # SCLK
        "7": (-12.7, -7.62),  # SDO
        "8": (-12.7, 7.62),  # ~MUTE
        "9": (-12.7, -12.7),  # V_INR
        "10": (-12.7, -17.78),  # AGNDR
        "11": (12.7, -15.24),  # V_OUTR
        "12": (5.08, 27.94),  # V_A+
        "13": (5.08, -27.94),  # V_A-
        "14": (12.7, 15.24),  # V_OUTL
        "15": (-12.7, 17.78),  # AGNDL
        "16": (-12.7, 12.7),  # V_INL
    }
    px, py = table[num]
    return pin(sx, sy, px, py)


def bus_hier(name: str, hy: float, bx: float = 55.0, shape: str = "input") -> str:
    """Horizontal bus from hierarchical label (30.48) to bx at hy."""
    return (
        hier_label(name, shape, 30.48, hy, 180)
        + wire(30.48, hy, bx, hy)
        + label(name, bx + 2, hy - 0.5)
        + junction(bx, hy)
    )


def dkmw_pin(sx: float, sy: float, num: str) -> tuple[float, float]:
    table = {
        "1": (-12.7, -8.89),  # +Vin
        "2": (-12.7, -5.08),  # -Vin
        "3": (12.7, -6.35),  # +Vout
        "4": (12.7, -8.89),  # Common
        "5": (12.7, -11.43),  # -Vout
        "6": (-12.7, -13.97),  # R.C.
    }
    px, py = table[num]
    return pin(sx, sy, px, py)


def ch224_pin(sx: float, sy: float, name: str) -> tuple[float, float]:
    table = {
        "VBUS": (-12.7, 5.08),
        "GND": (-12.7, 2.54),
        "12V": (12.7, 5.08),
        "PG": (12.7, 2.54),
    }
    px, py = table[name]
    return pin(sx, sy, px, py)


def fuse_pin(fx: float, fy: float, end: int, rot: int = 90) -> tuple[float, float]:
    """Device:Fuse — rot=90 → pin1 left, pin2 right."""
    if rot == 90:
        return (fx - 3.81, fy) if end == 1 else (fx + 3.81, fy)
    return (fx, fy - 3.81) if end == 1 else (fx, fy + 3.81)


def lm7809_pin(ux: float, uy: float, name: str) -> tuple[float, float]:
    table = {"VI": (-7.62, 0), "GND": (0, -7.62), "VO": (7.62, 0)}
    px, py = table[name]
    return pin(ux, uy, px, py)


def conn02_pin(cx: float, cy: float, n: int) -> tuple[float, float]:
    return cx + 5.08, cy + (1.5 - n) * 2.54


def conn03_pin(cx: float, cy: float, n: int) -> tuple[float, float]:
    return cx + 5.08, cy + (n - 2) * 2.54


def usb_vbus_pin(jx: float, jy: float) -> tuple[float, float]:
    return pin(jx, jy, 15.24, 15.24)


def usb_gnd_pin(jx: float, jy: float) -> tuple[float, float]:
    return pin(jx, jy, 0, -22.86)


def power_module_wired() -> str:
    """Simplified PowerModule per DECISIONS §9 / CIRCUIT_DESIGN §4."""
    wires: list[str] = []

    # --- placement (left → right) ---
    j1x, j1y = 25.4, 50.8
    u2x, u2y = 55.88, 48.26
    u1x, u1y = 110.0, 53.34
    u3x, u3y = 140.0, 66.0
    j_pdx, j_pdy = 155.0, 58.0
    j202x, j202y = 155.0, 46.0

    y_pd = ch224_pin(u2x, u2y, "12V")[1]
    y_gnd = ch224_pin(u2x, u2y, "GND")[1]
    y_sw = y_pd + 3.56  # PD_12V_SW path — off PD_12V bus

    f1x, f1y = 81.28, y_sw

    p12 = ch224_pin(u2x, u2y, "12V")
    pgnd = ch224_pin(u2x, u2y, "GND")
    pvbus = ch224_pin(u2x, u2y, "VBUS")
    p_pg = ch224_pin(u2x, u2y, "PG")

    p_vin = dkmw_pin(u1x, u1y, "1")
    p_vin_n = dkmw_pin(u1x, u1y, "2")
    p_vout_p = dkmw_pin(u1x, u1y, "3")
    p_com = dkmw_pin(u1x, u1y, "4")
    p_vout_n = dkmw_pin(u1x, u1y, "5")
    p_rc = dkmw_pin(u1x, u1y, "6")

    f1_in = fuse_pin(f1x, f1y, 1, 90)
    f1_out = fuse_pin(f1x, f1y, 2, 90)

    jpd1 = conn02_pin(j_pdx, j_pdy, 1)
    jpd2 = conn02_pin(j_pdx, j_pdy, 2)
    j12 = conn03_pin(j202x, j202y, 1)
    jm12 = conn03_pin(j202x, j202y, 2)
    jagnd = conn03_pin(j202x, j202y, 3)

    u3_vi = lm7809_pin(u3x, u3y, "VI")
    u3_gnd = lm7809_pin(u3x, u3y, "GND")
    u3_vo = lm7809_pin(u3x, u3y, "VO")

    # USB-C → CH224 module
    wires.append(wire(*usb_vbus_pin(j1x, j1y), *pvbus))
    wires.append(wire(*usb_gnd_pin(j1x, j1y), *pgnd))
    wires.append(label("VBUS", 34, y_pd - 2))
    wires.append(label("PD_GND", 34, y_gnd - 2))

    # CH224 12V → PD_12V (panel feed, before PWR SW) → J_PD / hier
    pd_bus_x = 72.0
    wires.append(wire(*p12, pd_bus_x, y_pd))
    wires.append(junction(pd_bus_x, y_pd))
    wires.append(wire(pd_bus_x, y_pd, jpd1[0], jpd1[1]))
    wires.append(label("PD_12V", 90, y_pd - 1.5))

    # Panel return PD_12V_SW → F1 → DKMW +Vin (separate net from PD_12V)
    wires.append(wire(30.48, y_sw, *f1_in))
    wires.append(label("PD_12V_SW", 32, y_sw - 1.5))
    wires.append(wire(*f1_out, *p_vin))
    wires.append(cap("C101", "47u", f1_out[0] + 5, f1_out[1] + 6, PATH_PWR))
    wires.append(wire(f1_out[0] + 5, f1_out[1] + 3.5, f1_out[0], f1_out[1]))
    wires.append(wire(f1_out[0] + 5, f1_out[1] + 8.5, f1_out[0] + 5, y_gnd))
    wires.append(junction(f1_out[0] + 5, y_gnd))

    # PD_GND: CH224, DKMW -Vin, R.C., panel return
    wires.append(wire(*pgnd, u1x - 25, y_gnd))
    wires.append(junction(u1x - 25, y_gnd))
    wires.append(wire(u1x - 25, y_gnd, *p_vin_n))
    wires.append(wire(u1x - 25, y_gnd, *p_rc))
    wires.append(wire(u1x - 25, y_gnd, jpd2[0], jpd2[1]))
    wires.append(wire(u1x - 25, y_gnd, u3_gnd[0], u3_gnd[1]))

    # ±12 V / A_GND outputs
    wires.append(wire(*p_vout_p, j12[0], j12[1]))
    wires.append(wire(*p_vout_n, jm12[0], jm12[1]))
    wires.append(wire(*p_com, jagnd[0], jagnd[1]))
    wires.append(label("+12V_OUT", 125, p_vout_p[1] - 1.5))
    wires.append(label("-12V_OUT", 125, p_vout_n[1] - 1.5))
    wires.append(label("A_GND", 125, p_com[1] - 1.5))
    wires.append(cap("C102", "47u", p_vout_p[0] + 8, p_vout_p[1], PATH_PWR))
    wires.append(cap("C103", "47u", p_vout_n[0] + 8, p_vout_n[1], PATH_PWR))
    wires.append(cap("C104", "0.1u", p_vout_p[0] + 16, p_vout_p[1], PATH_PWR))
    wires.append(wire(p_vout_p[0] + 8, p_vout_p[1] + 2.5, p_vout_p[0], p_vout_p[1]))
    wires.append(wire(p_vout_p[0] + 16, p_vout_p[1] + 2.5, p_vout_p[0], p_vout_p[1]))
    wires.append(wire(p_vout_n[0] + 8, p_vout_n[1] + 2.5, p_vout_n[0], p_vout_n[1]))
    wires.append(wire(p_vout_p[0] + 8, p_vout_p[1] + 5, p_vout_p[0] + 8, p_com[1]))
    wires.append(wire(p_vout_n[0] + 8, p_vout_n[1] + 5, p_vout_n[0] + 8, p_com[1]))

    # LM7809 → VCC_TONE (+9 V for PT2314)
    wires.append(wire(j12[0], j12[1], u3_vi[0], u3_vi[1]))
    wires.append(wire(*u3_vo, 185.0, u3_vo[1]))
    wires.append(label("VCC_TONE", 170, u3_vo[1] - 1.5))
    wires.append(cap("C301", "10u", u3x - 10, u3y + 8, PATH_PWR))
    wires.append(cap("C302", "0.1u", u3x + 10, u3y + 8, PATH_PWR))
    wires.append(wire(u3x - 10, u3y + 10.5, *u3_vi))
    wires.append(wire(u3x + 10, u3y + 10.5, *u3_vo))
    wires.append(wire(u3x - 10, u3y + 13, u3x - 10, y_gnd))
    wires.append(wire(u3x + 10, u3y + 13, u3x + 10, y_gnd))

    # CH224 PG (open drain) — pull-up note only; leave pin visible
    wires.append(label("PG_noconn", p_pg[0] + 2, p_pg[1] - 1.5))

    body = f"""\t(lib_symbols)
{text_note(25.4, 20.32, [
    "AudioV2 PowerModule — simplified wired (§9 / CIRCUIT_DESIGN §4)",
    "USB-C → 50224 CH224 → PD_12V/J_PD → (panel SW) → PD_12V_SW → F1 → DKMW20F-12",
    "±12V + A_GND → J202 / hier.  LM7809 → VCC_TONE (+9V).  Bench +12V_IN: TBD.",
])}
{hier_label("PD_12V_SW", "input", 30.48, y_sw, 180)}
{hier_label("PD_12V", "output", 200.66, jpd1[1], 0)}
{wire(jpd1[0], jpd1[1], 200.66, jpd1[1])}
{hier_label("PD_GND", "bidirectional", 200.66, jpd2[1], 0)}
{wire(jpd2[0], jpd2[1], 200.66, jpd2[1])}
{hier_label("+12V_OUT", "output", 200.66, j12[1], 0)}
{wire(j12[0], j12[1], 200.66, j12[1])}
{hier_label("-12V_OUT", "output", 200.66, jm12[1], 0)}
{wire(jm12[0], jm12[1], 200.66, jm12[1])}
{hier_label("A_GND", "bidirectional", 200.66, jagnd[1], 0)}
{wire(jagnd[0], jagnd[1], 200.66, jagnd[1])}
{hier_label("VCC_TONE", "output", 200.66, u3_vo[1], 0)}
{wire(185.0, u3_vo[1], 200.66, u3_vo[1])}
{symbol_inst("Connector:USB_C_Receptacle_USB2.0", "J1", "USB-C PD in", j1x, j1y, 0, PATH_PWR)}
{symbol_inst("AudioV2:CH224_50224", "U2", "50224_CH224 12V", u2x, u2y, 0, PATH_PWR)}
{symbol_inst("Device:Fuse", "F1", "3A slow", f1x, f1y, 90, PATH_PWR)}
{symbol_inst("AudioV2:DKMW20F-12", "U1", "DKMW20F-12", u1x, u1y, 0, PATH_PWR)}
{symbol_inst("Regulator_Linear:LM7809_TO220", "U3", "LM7809 +9V", u3x, u3y, 0, PATH_PWR)}
{symbol_inst("Connector:Conn_01x02_Pin", "J_PD", "PD_12V/GND to panel", j_pdx, j_pdy, 0, PATH_PWR)}
{symbol_inst("Connector:Conn_01x03_Pin", "J202", "+12/-12/A_GND out", j202x, j202y, 0, PATH_PWR)}
{"".join(wires)}
"""
    return sch_open(UUID_POWER_FILE, body)


def control_panel_wired() -> str:
    u2x, u2y = 160.0, 120.0
    u3x, u3y = 127.0, 78.0
    u4x, u4y = 127.0, 95.0
    picox, picoy = 76.2, 78.0
    wires: list[str] = []

    # --- Buses from hierarchical labels ---
    buses = {
        "COMMON_L": 118.0,
        "COMMON_R": 121.0,
        "VCC_TONE": 110.0,
        "A_GND": 125.0,
        "D_GND": 128.0,
        "+12V": 131.0,
        "-12V": 133.0,
        "+5V": 115.0,
        "+3V3": 112.0,
    }
    for name, hy in buses.items():
        shape = "bidirectional" if name in ("A_GND",) else "input"
        if name == "+5V":
            continue
        wires.append(bus_hier(name, hy, 50.0, shape))

    # BP5293 +5V from +12V (simplified)
    wires.append(symbol_inst("BP5293_ROHM:BP5293-50", "U5", "BP5293-50 +5V", 50.8, 115.0, 0, PATH_CTRL))
    wires.append(wire(50.0, 131.0, 50.8 - 7.62, 115.0 + 1.27))
    wires.append(wire(50.8 + 7.62, 115.0, 50.0, 115.0))
    wires.append(label("+5V", 52, 114))

    # --- PT2314 power ---
    p_vdd = pt2314_pin(u2x, u2y, 0)
    p_agnd = pt2314_pin(u2x, u2y, 1)
    p_dgnd = pt2314_pin(u2x, u2y, 24)
    wires.append(wire(50.0, 110.0, p_vdd[0], p_vdd[1]))
    wires.append(wire(50.0, 125.0, p_agnd[0], p_agnd[1]))
    wires.append(wire(50.0, 128.0, p_dgnd[0], p_dgnd[1]))
    wires.append(cap("C201", "0.1u", u2x - 20, u2y - 18, PATH_CTRL))
    wires.append(wire(u2x - 20, u2y - 20.5, p_vdd[0], p_vdd[1]))

    # Input coupling COMMON → LIN/RIN
    wires.append(cap("C202", "2.2u", 95.0, 118.0, PATH_CTRL))
    wires.append(cap("C203", "2.2u", 95.0, 121.0, PATH_CTRL))
    plin = pt2314_pin(u2x, u2y, 16)
    prin = pt2314_pin(u2x, u2y, 4)
    wires.append(wire(50.0, 118.0, 92.46, 118.0))
    wires.append(wire(97.54, 118.0, plin[0], plin[1]))
    wires.append(wire(50.0, 121.0, 92.46, 121.0))
    wires.append(wire(97.54, 121.0, prin[0], prin[1]))

    # REF network pin28 (index 27)
    pref = pt2314_pin(u2x, u2y, 27)
    wires.append(res("R201", "5.6k", u2x + 18, u2y - 18, PATH_CTRL))
    wires.append(cap("C204", "22u", u2x + 25, u2y - 18, PATH_CTRL))
    wires.append(wire(pref[0], pref[1], u2x + 15.24, u2y - 18))
    wires.append(wire(u2x + 15.24, u2y - 18, u2x + 15.24, 125.0))
    wires.append(wire(u2x + 15.24, 125.0, 50.0, 125.0))
    wires.append(wire(u2x + 20.46, u2y - 18, u2x + 22.54, u2y - 18))
    wires.append(wire(u2x + 27.54, u2y - 18, u2x + 27.54, 125.0))

    # Bass L network BIN_L/BOUT_L (pin index 18,19)
    for idx, ref_r, ref_c in ((18, "R202", "C205"), (19, "R203", "C206")):
        px = pt2314_pin(u2x, u2y, idx)
        rx, ry = u2x - 25, u2y + 5 - (idx - 18) * 8
        wires.append(res(ref_r, "2.4k", rx, ry, PATH_CTRL))
        wires.append(cap(ref_c, "100n", rx + 7, ry, PATH_CTRL))
        wires.append(wire(px[0], px[1], rx + 2.54, ry))
        wires.append(wire(rx + 9.54, ry, rx + 9.54, 125.0))
        wires.append(wire(rx + 9.54, 125.0, 50.0, 125.0))

    # Bass R (index 20,21)
    for idx, ref_r, ref_c in ((20, "R204", "C207"), (21, "R205", "C208")):
        px = pt2314_pin(u2x, u2y, idx)
        rx, ry = u2x + 25, u2y + 5 - (idx - 20) * 8
        wires.append(res(ref_r, "2.4k", rx, ry, PATH_CTRL))
        wires.append(cap(ref_c, "100n", rx - 7, ry, PATH_CTRL))
        wires.append(wire(px[0], px[1], rx - 2.54, ry))
        wires.append(wire(rx - 9.54, ry, rx - 9.54, 125.0))

    # Treble caps on TREB_L/R (index 2,3)
    for idx, ref_c in ((2, "C209"), (3, "C210")):
        px = pt2314_pin(u2x, u2y, idx)
        wires.append(cap(ref_c, "2.7n", px[0] - 8, px[1], PATH_CTRL))
        wires.append(res(f"R{206+idx}", "2.4k", px[0] - 15, px[1], PATH_CTRL))
        wires.append(wire(px[0], px[1], px[0] - 5.46, px[1]))

    # Outputs OUT_L/R → hierarchical TONE_OUT (to Amp path)
    pout_l = pt2314_pin(u2x, u2y, 23)
    pout_r = pt2314_pin(u2x, u2y, 22)
    wires.append(cap("C211", "2.2u", 185.0, 118.0, PATH_CTRL))
    wires.append(cap("C212", "2.2u", 185.0, 121.0, PATH_CTRL))
    wires.append(wire(pout_l[0], pout_l[1], 182.46, 118.0))
    wires.append(wire(pout_r[0], pout_r[1], 182.46, 121.0))
    wires.append(hier_label("TONE_L", "output", 200.66, 118.0, 0))
    wires.append(hier_label("TONE_R", "output", 200.66, 121.0, 0))
    wires.append(wire(187.54, 118.0, 200.66, 118.0))
    wires.append(wire(187.54, 121.0, 200.66, 121.0))

    # DATA/CLK + pullups (Pico GP20/21)
    pdata = pt2314_pin(u2x, u2y, 25)
    pclk = pt2314_pin(u2x, u2y, 26)
    wires.append(res("R210", "4.7k", picox + 15, picoy - 10, PATH_CTRL))
    wires.append(res("R211", "4.7k", picox + 15, picoy - 5, PATH_CTRL))
    wires.append(wire(50.0, 112.0, picox + 12.46, 112.0))
    wires.append(wire(picox + 17.54, picoy - 10, pdata[0], pdata[1]))
    wires.append(wire(picox + 17.54, picoy - 5, pclk[0], pclk[1]))
    wires.append(wire(picox + 12.46, picoy - 10, picox + 12.46, 112.0))
    wires.append(label("I2C_SDA", picox + 18, picoy - 11))
    wires.append(label("I2C_SCL", picox + 18, picoy - 6))

    # --- PGA2310 HP (U3) ---
    wires.append(wire(50.0, 131.0, pga2310_pin(u3x, u3y, "12")[0], pga2310_pin(u3x, u3y, "12")[1]))
    wires.append(wire(50.0, 133.0, pga2310_pin(u3x, u3y, "13")[0], pga2310_pin(u3x, u3y, "13")[1]))
    wires.append(wire(50.0, 125.0, pga2310_pin(u3x, u3y, "15")[0], pga2310_pin(u3x, u3y, "15")[1]))
    wires.append(wire(50.0, 125.0, pga2310_pin(u3x, u3y, "10")[0], pga2310_pin(u3x, u3y, "10")[1]))
    wires.append(wire(50.0, 115.0, pga2310_pin(u3x, u3y, "4")[0], pga2310_pin(u3x, u3y, "4")[1]))
    wires.append(wire(50.0, 128.0, pga2310_pin(u3x, u3y, "5")[0], pga2310_pin(u3x, u3y, "5")[1]))
    zcen = pga2310_pin(u3x, u3y, "1")
    wires.append(wire(50.0, 115.0, zcen[0], zcen[1]))
    # SPI to Pico + daisy to U4
    for pga_pin, gp_y in (("6", picoy + 5), ("3", picoy + 2.5), ("2", picoy)):
        px, py = pga2310_pin(u3x, u3y, pga_pin)
        wires.append(wire(picox + 10, gp_y, px, py))
    sdo = pga2310_pin(u3x, u3y, "7")
    sdi2 = pga2310_pin(u4x, u4y, "3")
    wires.append(wire(sdo[0], sdo[1], sdi2[0], sdi2[1]))
    # MUTE + pulldown
    wires.append(res("R220", "10k", picox + 5, picoy + 10, PATH_CTRL))
    mute = pga2310_pin(u3x, u3y, "8")
    wires.append(wire(picox + 10, picoy + 7.5, mute[0], mute[1]))
    wires.append(wire(picox + 7.46, picoy + 10, picox + 7.46, 128.0))
    wires.append(wire(picox + 7.46, 128.0, 50.0, 128.0))
    # HP outputs → hier
    for pin_n, hy, hname in (("14", 130.0, "PGA_HP_L"), ("11", 132.54, "PGA_HP_R")):
        po = pga2310_pin(u3x, u3y, pin_n)
        wires.append(wire(po[0], po[1], 195.0, hy))
        wires.append(hier_label(hname, "output", 200.66, hy, 0))
        wires.append(wire(195.0, hy, 200.66, hy))

    # PGA LINE U4 — shared CS/SCLK/MUTE, inputs TONE would come from amps (hier placeholder)
    wires.append(hier_label("AMP_SEL_L", "input", 30.48, 105.0, 180))
    wires.append(hier_label("AMP_SEL_R", "input", 30.48, 107.0, 180))
    wires.append(wire(50.0, 105.0, pga2310_pin(u4x, u4y, "16")[0], pga2310_pin(u4x, u4y, "16")[1]))
    wires.append(wire(50.0, 107.0, pga2310_pin(u4x, u4y, "9")[0], pga2310_pin(u4x, u4y, "9")[1]))
    for pin_n, hy, hname in (("14", 135.08, "PGA_LINE_L"), ("11", 137.62, "PGA_LINE_R")):
        po = pga2310_pin(u4x, u4y, pin_n)
        wires.append(wire(po[0], po[1], 195.0, hy))
        wires.append(hier_label(hname, "output", 200.66, hy, 0))
        wires.append(wire(195.0, hy, 200.66, hy))

    # PWR SW + LED
    wires.append(wire(50.0, 150.32, 165.1, 150.32))
    wires.append(hier_label("PD_12V_SW", "output", 200.66, 150.32, 0))
    wires.append(wire(177.8, 150.32, 200.66, 150.32))

    encs = [
        ("ENC_CH", "ENC1", "GP0/1/12", 40.64),
        ("ENC_HP", "ENC2", "GP2/3/13", 55.88),
        ("ENC_LINE", "ENC3", "GP4/5/14", 71.12),
        ("ENC_DEST", "ENC4", "GP6/7/15", 86.36),
        ("ENC_BASS", "ENC5", "GP8/9/26", 101.6),
        ("ENC_TREBLE", "ENC6", "GP10/11/27", 116.84),
    ]
    enc_syms = "\n".join(
        symbol_inst("Device:RotaryEncoder_Switch", ref, f"EC11 {name} {gps}", 35.56, y, 0, PATH_CTRL)
        for name, ref, gps, y in encs
    )

    body = f"""\t(lib_symbols)
{text_note(25.4, 25.4, [
    "ControlPanel — CIRCUIT_DESIGN wired (§10 + §3)",
    "PT2314 @9V / PGA2310PA×2 / Pico2 / ENC×6",
    "TONE_L/R → Amp inputs (off-sheet). AMP_SEL ← selected Amp output",
])}
{hier_label("PD_12V", "input", 30.48, 150.32, 180)}
{hier_label("PD_GND", "bidirectional", 200.66, 152.86, 0)}
{hier_label("I2C_SDA", "bidirectional", 30.48, 135.08, 180)}
{hier_label("I2C_SCL", "bidirectional", 30.48, 137.62, 180)}
{wire(30.48, 135.08, 50.0, 135.08)}
{wire(30.48, 137.62, 50.0, 137.62)}
{symbol_inst("MCU_Module:Raspberry_Pi_Pico", "U1", "Pico 2 / RP2350", picox, picoy, 0, PATH_CTRL)}
{symbol_inst("AudioV2:PT2314", "U2", "PT2314", u2x, u2y, 0, PATH_CTRL)}
{symbol_inst("Audio:PGA2310PA", "U3", "PGA2310PA HP", u3x, u3y, 0, PATH_CTRL)}
{symbol_inst("Audio:PGA2310PA", "U4", "PGA2310PA LINE", u4x, u4y, 0, PATH_CTRL)}
{symbol_inst("Display_Graphic:SSD1306-128x64", "U6", "OLED ctrl I2C", 101.6, 78.0, 0, PATH_CTRL)}
{symbol_inst("Switch:SW_SPST", "SW1", "PWR SW", 165.1, 150.32, 0, PATH_CTRL)}
{symbol_inst("Device:LED", "D1", "12V panel LED", 177.8, 152.86, 0, PATH_CTRL)}
{enc_syms}
{"".join(wires)}
"""
    return sch_open(UUID_CONTROL_FILE, body)


def parent_wired() -> str:
    """Parent with global buses wired to sheet pins."""
    wires = []

    def bus_net(name: str, y: float, x_pins: list[tuple[float, float]]) -> str:
        """Horizontal bus at y from min to max x with junctions at each pin."""
        xs = [p[0] for p in x_pins] + [127.0]
        x0, x1 = min(xs) - 5, max(xs) + 5
        out = wire(x0, y, x1, y) + label(name, x0 + 2, y - 0.5)
        for px, py in x_pins:
            out += junction(px, py) + wire(px, py, px, y)
        out += junction(127.0, y)
        return out

    wires.append(bus_net("+12V", 100.0, [(60.96, 35.56), (170.0, 50.16), (230.0, 50.16)]))
    wires.append(bus_net("-12V", 102.54, [(60.96, 38.1), (170.0, 52.7), (230.0, 52.7)]))
    wires.append(bus_net("A_GND", 105.08, [(60.96, 40.64), (140.0, 45.08), (170.0, 55.24), (230.0, 55.24)]))
    wires.append(bus_net("I2C_SDA", 107.62, [(110.0, 40.0), (170.0, 45.08)]))
    wires.append(bus_net("I2C_SCL", 110.16, [(110.0, 42.54), (170.0, 47.62)]))

    # VCC_TONE PowerModule out → Control in
    wires.append(wire(60.96, 43.18, 170.0, 65.0))
    wires.append(junction(60.96, 43.18))
    wires.append(junction(170.0, 65.0))
    wires.append(label("VCC_TONE", 100, 44))

    # Relay COMMON → Control
    wires.append(wire(140.0, 40.0, 170.0, 40.0))
    wires.append(wire(140.0, 42.54, 170.0, 42.54))
    wires.append(junction(140.0, 40.0))
    wires.append(junction(170.0, 40.0))

    # Control PGA → Output
    for hy in (40.0, 42.54, 45.08, 47.62):
        wires.append(wire(200.0, hy, 230.0, hy))
        wires.append(junction(200.0, hy))
        wires.append(junction(230.0, hy))

    # PD panel loop: Power PD_12V → Control PD_12V; Control PD_12V_SW → Power PD_12V_SW
    wires.append(wire(60.96, 45.72, 170.0, 60.32))
    wires.append(wire(200.0, 60.32, 40.64, 55.88))
    wires.append(label("PD_12V", 115, 47))
    wires.append(label("PD_12V_SW", 120, 58))

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
        ("TONE_L", "output", 200.0, 38.0, 0),
        ("TONE_R", "output", 200.0, 38.5, 0),
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
    from generate_kicad_scaffold import UUID_POWER_INST, UUID_RELAY_A, UUID_RELAY_B  # noqa: E402

    sheets = (
        sheet_block(UUID_POWER_INST, "PowerModule", "PowerModule.kicad_sch", 35.56, 35.56, 30.48, 25.4, power_pins, "2")
        + sheet_block(UUID_RELAY_A, "RelayBoard_A", "RelayBoard.kicad_sch", 88.9, 35.56, 55.88, 30.48, relay_pins, "3")
        + sheet_block(UUID_RELAY_B, "RelayBoard_B", "RelayBoard.kicad_sch", 88.9, 73.66, 55.88, 30.48, relay_pins, "4")
        + sheet_block(UUID_CONTROL_INST, "ControlPanel", "ControlPanel.kicad_sch", 152.4, 35.56, 55.88, 35.56, control_pins, "5")
        + sheet_block(UUID_OUTPUT_INST, "OutputStage", "OutputStage.kicad_sch", 215.9, 35.56, 50.8, 25.4, output_pins, "6")
    )
    body = f"""\t(lib_symbols)
{text_note(25.4, 20.32, [
    "AudioV2Case — wired per CIRCUIT_DESIGN.md",
    "Global buses connect Power / Relay / Control / Output",
    "Amp/HP/計測 = Audio/ off-sheet (WIRING.md)",
])}
{global_label("+12V", 127.0, 100.0, 0)}
{global_label("-12V", 127.0, 102.54, 0)}
{global_label("A_GND", 127.0, 105.08, 0)}
{global_label("I2C_SDA", 127.0, 107.62, 0)}
{global_label("I2C_SCL", 127.0, 110.16, 0)}
{sheets}
{"".join(wires)}
"""
    return sch_open(PARENT, body)


def main() -> None:
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    if target in ("all", "power"):
        (ROOT / "PowerModule.kicad_sch").write_text(power_module_wired(), encoding="utf-8")
    if target in ("all", "control"):
        (ROOT / "ControlPanel.kicad_sch").write_text(control_panel_wired(), encoding="utf-8")
    if target in ("all", "parent"):
        (ROOT / "AudioV2Case.kicad_sch").write_text(parent_wired(), encoding="utf-8")
    print(f"Wired: {target}")


if __name__ == "__main__":
    main()
