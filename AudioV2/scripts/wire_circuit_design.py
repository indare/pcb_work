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
    UUID_RELAY_A,
    UUID_RELAY_FILE,
    hier_label,
    sch_open,
    sheet_block,
    symbol_inst,
    text_note,
    uid,
    global_label,
)
from sch_helpers import (  # noqa: E402
    cap_pins,
    ch224_pins,
    conn02_pins,
    conn03_pins,
    dkmw_pins,
    embed_lib_symbols,
    fuse_pins,
    grid,
    lm7809_pins,
    symbol_inst_v10,
    usb16_pins,
)

PATH_CTRL = f"/{PARENT}/{UUID_CONTROL_INST}"
PATH_PWR = f"/{PARENT}/{UUID_POWER_INST}"
PATH_OUT = f"/{PARENT}/{UUID_OUTPUT_INST}"
PATH_RELAY = f"/{PARENT}/{UUID_RELAY_A}"

CTRL_LIBS = [
    "Device:C",
    "Device:R",
    "Device:LED",
    "Device:RotaryEncoder_Switch",
    "Switch:SW_SPST",
    "Switch:SW_SP3T",
    "AudioV2:PT2314",
    "MCU_Module:RaspberryPi_Pico",
    "Connector:Conn_01x04_Pin",  # 2.42″ OLED I2C header (not ER_OLEDM0.91)
    "BP5293_ROHM:BP5293-50",
]

RELAY_LIBS = [
    "Interface_Expansion:MCP23017-E/SP",
    "Transistor_Array:ULN2803A",
    "Relay:AZ850P2-x",
    "Connector:Conn_01x04_Pin",
    "Connector:Conn_01x03_Pin",
    "Connector:Screw_Terminal_01x02",
]

OUTPUT_LIBS = [
    "Device:R_Potentiometer_Dual",
    "Switch:SW_DP3T",
    "Connector:Screw_Terminal_01x02",
]


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
    return symbol_inst_v10("Device:C", ref, val, x, y, 0, path)


def res(ref: str, val: str, x: float, y: float, path: str) -> str:
    return symbol_inst_v10("Device:R", ref, val, x, y, 0, path)


def sym(
    lib_id: str,
    ref: str,
    val: str,
    x: float,
    y: float,
    rot: int,
    path: str,
    extra: list[tuple[str, str]] | None = None,
    unit: int = 1,
) -> str:
    return symbol_inst_v10(lib_id, ref, val, x, y, rot, path, extra_props=extra, unit=unit)


def pt2314_pin(sx: float, sy: float, num: int) -> tuple[float, float]:
    """DIP-28: left 1..14 top→bottom, right 28..15 top→bottom. Tip coords."""
    if 1 <= num <= 14:
        return pin(sx, sy, -12.7, 16.51 - (num - 1) * 2.54)
    if 15 <= num <= 28:
        # right: 28 at top index0 … 15 at bottom index13
        idx = 28 - num
        return pin(sx, sy, 12.7, 16.51 - idx * 2.54)
    raise ValueError(num)


def pot_dual_pin(sx: float, sy: float, num: int) -> tuple[float, float]:
    """Device:R_Potentiometer_Dual — tip = symbol (at)."""
    table = {
        1: (-10.16, -2.54),
        2: (-6.35, 2.54),
        3: (-2.54, -2.54),
        4: (2.54, -2.54),
        5: (6.35, 2.54),
        6: (10.16, -2.54),
    }
    px, py = table[num]
    return sx + px, sy + py


def sw_dp3t_pin(sx: float, sy: float, num: int) -> tuple[float, float]:
    """SW_DP3T tip coords for a single unit origin (unit1: 1-4, unit2: 5-8)."""
    local = {
        1: (5.08, 2.54),
        2: (5.08, 0.0),
        3: (-5.08, 0.0),
        4: (5.08, -2.54),
        5: (5.08, 2.54),
        6: (5.08, 0.0),
        7: (-5.08, 0.0),
        8: (5.08, -2.54),
    }
    px, py = local[num]
    return sx + px, sy + py


def sw_sp3t_pin(sx: float, sy: float, num: int) -> tuple[float, float]:
    local = {
        1: (5.08, 2.54),
        2: (5.08, 0.0),
        3: (-5.08, 0.0),
        4: (5.08, -2.54),
    }
    px, py = local[num]
    return sx + px, sy + py


def pga2310_pin(sx: float, sy: float, num: str) -> tuple[float, float]:
    """Deprecated — PGA removed; kept to avoid import errors if referenced."""
    raise RuntimeError("PGA2310 removed from AudioV2 — use manual volume")


def bus_hier(name: str, hy: float, bx: float = 55.0, shape: str = "input") -> str:
    """Horizontal bus from hierarchical label (30.48) to bx at hy."""
    return (
        hier_label(name, shape, 30.48, hy, 180)
        + wire(30.48, hy, bx, hy)
        + label(name, bx + 2, hy - 0.5)
        + junction(bx, hy)
    )


def _cap_to_rail(
    wires: list[str],
    parts: list[str],
    ref: str,
    val: str,
    cx: float,
    cy: float,
    rail: tuple[float, float],
    gnd_y: float,
    path: str,
) -> None:
    """Place C symbol; top pin to rail, bottom pin to gnd_y."""
    top, bot = cap_pins(cx, cy)
    parts.append(cap(ref, val, cx, cy, path))
    wires.append(wire(rail[0], rail[1], top[0], top[1]))
    wires.append(wire(bot[0], bot[1], bot[0], gnd_y))
    wires.append(junction(bot[0], gnd_y))


def power_module_wired() -> str:
    """Simplified PowerModule per DECISIONS §9 / CIRCUIT_DESIGN §4.

    Primary (PD_*) and secondary (A_GND / ±12V / VCC_TONE) stay isolated.
    DKMW R.C. left open (= ON per DS). LM7809 GND on A_GND only.
    """
    wires: list[str] = []
    parts: list[str] = []

    lib_ids = [
        "Connector:USB_C_Receptacle_USB2.0_16P",
        "AudioV2:CH224_50224",
        "Device:Fuse",
        "AudioV2:DKMW20F-12",
        "Regulator_Linear:LM7809_TO220",
        "Connector:Conn_01x02_Pin",
        "Connector:Conn_01x03_Pin",
        "Device:C",
    ]

    j1x, j1y = grid(25.4), grid(50.8)
    u2x, u2y = grid(55.88), grid(48.26)
    u1x, u1y = grid(110.0), grid(53.34)
    u3x, u3y = grid(155.0), grid(66.0)
    # Keep J_PD pins off the PD_12V_SW / F1 Y (y_pd) to avoid accidental co-linear shorts.
    j_pdx, j_pdy = grid(175.0), grid(33.0)
    j202x, j202y = grid(175.0), grid(55.0)

    pch = ch224_pins(u2x, u2y)
    pdk = dkmw_pins(u1x, u1y)
    pusb = usb16_pins(j1x, j1y)
    u3 = lm7809_pins(u3x, u3y)

    y_pd = pch["12V"][1]
    y_gnd = pch["GND"][1]
    # Switched 12V rail must NOT share Y with PD_GND (was the 83.82,45.72 short).
    y_sw = y_pd

    f1x, f1y = grid(81.28), y_sw
    f1_in, f1_out = fuse_pins(f1x, f1y, 90)
    if f1_in[0] > f1_out[0]:
        f1_in, f1_out = f1_out, f1_in

    jpd1, jpd2 = conn02_pins(j_pdx, j_pdy)
    j12, jm12, jagnd = conn03_pins(j202x, j202y)

    hier_x = grid(210.0)
    pd_bus_x = grid(72.0)
    # Primary GND bus X clear of F1 tip (F1 out ≈ f1x+2.54).
    gnd_bus_x = grid(92.0)
    tone_bus_x = grid(195.0)
    agnd_y = pdk["4"][1]
    agnd_bus_x = grid(pdk["4"][0] + 5.08)

    # USB-C → CH224
    wires.append(wire(*pusb["VBUS"], *pch["VBUS"]))
    wires.append(wire(*pusb["GND"], *pch["GND"]))

    # CH224 12V → PD_12V (panel feed, before PWR SW) → J_PD / hier
    wires.append(wire(*pch["12V"], pd_bus_x, y_pd))
    wires.append(junction(pd_bus_x, y_pd))
    wires.append(wire(pd_bus_x, y_pd, *jpd1))
    wires.append(label("PD_12V", grid(90), y_pd - 1.27))

    # Panel return PD_12V_SW → F1 → DKMW +Vin (primary hot only)
    wires.append(wire(30.48, y_sw, *f1_in))
    wires.append(label("PD_12V_SW", grid(32), y_sw - 1.27))
    wires.append(wire(*f1_out, f1_out[0], pdk["1"][1]))
    wires.append(junction(f1_out[0], pdk["1"][1]))
    wires.append(wire(f1_out[0], pdk["1"][1], *pdk["1"]))
    _cap_to_rail(
        wires, parts, "C101", "47u", grid(f1_out[0] + 7.62), grid((f1_out[1] + pdk["1"][1]) / 2),
        (f1_out[0], pdk["1"][1]), y_gnd, PATH_PWR,
    )

    # PD_GND primary: CH224 GND, DKMW -Vin, panel return — NOT R.C., NOT 7809
    wires.append(wire(*pch["GND"], gnd_bus_x, y_gnd))
    wires.append(junction(gnd_bus_x, y_gnd))
    wires.append(wire(gnd_bus_x, y_gnd, pdk["2"][0], y_gnd))
    wires.append(junction(pdk["2"][0], y_gnd))
    wires.append(wire(pdk["2"][0], y_gnd, *pdk["2"]))
    wires.append(wire(gnd_bus_x, y_gnd, *jpd2))
    # R.C. (pin 6) open = ON (DKMW DS) — label only, no net join
    wires.append(label("R.C. open=ON", pdk["6"][0] - 12.7, pdk["6"][1] - 1.27))

    # ±12 V / A_GND outputs (secondary)
    wires.append(wire(*pdk["3"], *j12))
    wires.append(wire(*pdk["5"], *jm12))
    wires.append(wire(*pdk["4"], *jagnd))
    wires.append(label("+12V_OUT", grid(125), pdk["3"][1] - 1.27))
    wires.append(label("-12V_OUT", grid(125), pdk["5"][1] - 1.27))
    wires.append(label("A_GND", grid(125), pdk["4"][1] - 1.27))

    wires.append(wire(*pdk["4"], agnd_bus_x, agnd_y))
    wires.append(junction(agnd_bus_x, agnd_y))

    _cap_to_rail(wires, parts, "C102", "47u", grid(pdk["3"][0] + 10.16), pdk["3"][1], pdk["3"], agnd_y, PATH_PWR)
    _cap_to_rail(wires, parts, "C103", "47u", grid(pdk["5"][0] + 10.16), pdk["5"][1], pdk["5"], agnd_y, PATH_PWR)
    _cap_to_rail(wires, parts, "C104", "0.1u", grid(pdk["3"][0] + 20.32), pdk["3"][1], pdk["3"], agnd_y, PATH_PWR)

    # LM7809 from +12V secondary → VCC_TONE; GND on A_GND only
    wires.append(wire(*j12, *u3["VI"]))
    wires.append(wire(*u3["GND"], u3["GND"][0], agnd_y))
    wires.append(junction(u3["GND"][0], agnd_y))
    wires.append(wire(u3["GND"][0], agnd_y, agnd_bus_x, agnd_y))
    wires.append(wire(*u3["VO"], tone_bus_x, u3["VO"][1]))
    wires.append(label("VCC_TONE", grid(180), u3["VO"][1] - 1.27))
    _cap_to_rail(wires, parts, "C301", "10u", grid(u3x - 10.16), grid(u3y + 10.16), u3["VI"], agnd_y, PATH_PWR)
    _cap_to_rail(wires, parts, "C302", "0.1u", grid(u3x + 10.16), grid(u3y + 10.16), u3["VO"], agnd_y, PATH_PWR)

    # CH224 PG (open drain) — pull-up TBD
    wires.append(label("PG_noconn", pch["PG"][0] + 2.54, pch["PG"][1] - 1.27))

    parts.extend(
        [
            symbol_inst_v10("Connector:USB_C_Receptacle_USB2.0_16P", "J1", "USB-C PD in", j1x, j1y, 0, PATH_PWR),
            symbol_inst_v10("AudioV2:CH224_50224", "U2", "50224_CH224 12V", u2x, u2y, 0, PATH_PWR),
            symbol_inst_v10("Device:Fuse", "F1", "3A slow", f1x, f1y, 90, PATH_PWR),
            symbol_inst_v10("AudioV2:DKMW20F-12", "U1", "DKMW20F-12", u1x, u1y, 0, PATH_PWR),
            symbol_inst_v10("Regulator_Linear:LM7809_TO220", "U3", "LM7809 +9V", u3x, u3y, 0, PATH_PWR),
            symbol_inst_v10("Connector:Conn_01x02_Pin", "J_PD", "PD_12V/GND to panel", j_pdx, j_pdy, 0, PATH_PWR),
            symbol_inst_v10("Connector:Conn_01x03_Pin", "J202", "+12/-12/A_GND out", j202x, j202y, 0, PATH_PWR),
        ]
    )

    body = f"""{embed_lib_symbols(lib_ids)}
{text_note(25.4, 20.32, [
    "AudioV2 PowerModule — simplified wired (§9 / CIRCUIT_DESIGN §4)",
    "USB-C → 50224 CH224 → PD_12V/J_PD → (panel SW) → PD_12V_SW → F1 → DKMW20F-12",
    "Primary PD_GND ≠ secondary A_GND. DKMW R.C. open=ON. LM7809 GND → A_GND.",
    "±12V + A_GND → J202 / hier.  LM7809 → VCC_TONE (+9V).  Bench +12V_IN: TBD.",
])}
{hier_label("PD_12V_SW", "input", 30.48, y_sw, 180)}
{hier_label("PD_12V", "output", hier_x, jpd1[1], 0)}
{wire(jpd1[0], jpd1[1], hier_x, jpd1[1])}
{hier_label("PD_GND", "bidirectional", hier_x, jpd2[1], 0)}
{wire(jpd2[0], jpd2[1], hier_x, jpd2[1])}
{hier_label("+12V_OUT", "output", hier_x, j12[1], 0)}
{wire(j12[0], j12[1], hier_x, j12[1])}
{hier_label("-12V_OUT", "output", hier_x, jm12[1], 0)}
{wire(jm12[0], jm12[1], hier_x, jm12[1])}
{hier_label("A_GND", "bidirectional", hier_x, jagnd[1], 0)}
{wire(jagnd[0], jagnd[1], hier_x, jagnd[1])}
{hier_label("VCC_TONE", "output", hier_x, u3["VO"][1], 0)}
{wire(tone_bus_x, u3["VO"][1], hier_x, u3["VO"][1])}
{"".join(parts)}
{"".join(wires)}
"""
    return sch_open(UUID_POWER_FILE, body)


def control_panel_wired() -> str:
    """ControlPanel: Pico / ENC×3 / OLED / PT2314 / DEST sense+LED / PWR SW.

    Volume pots and DEST audio switch live on OutputStage (same PCB Q2-A).
    """
    u2x, u2y = 160.0, 120.0
    picox, picoy = 76.2, 78.0
    wires: list[str] = []

    buses = {
        "COMMON_L": 118.0,
        "COMMON_R": 121.0,
        "VCC_TONE": 110.0,
        "A_GND": 125.0,
        "D_GND": 128.0,
        "+12V": 131.0,
        "-12V": 133.0,
        "+3V3": 112.0,
    }
    for name, hy in buses.items():
        shape = "bidirectional" if name == "A_GND" else "input"
        wires.append(bus_hier(name, hy, 50.0, shape))

    # BP5293 +5V (digital / Pico USB alt — keep for 5V rail label)
    parts_bp: list[str] = []
    parts_bp.append(sym("BP5293_ROHM:BP5293-50", "U5", "BP5293-50 +5V", 50.8, 115.0, 0, PATH_CTRL))
    wires.append(label("+5V", 52, 114))

    # --- PT2314 power (DS: VDD=1, AGND=2, DGND=25) ---
    p_vdd = pt2314_pin(u2x, u2y, 1)
    p_agnd = pt2314_pin(u2x, u2y, 2)
    p_dgnd = pt2314_pin(u2x, u2y, 25)
    wires.append(wire(50.0, 110.0, p_vdd[0], p_vdd[1]))
    wires.append(wire(50.0, 125.0, p_agnd[0], p_agnd[1]))
    wires.append(wire(50.0, 128.0, p_dgnd[0], p_dgnd[1]))
    wires.append(cap("C201", "0.1u", u2x - 22, u2y - 20, PATH_CTRL))

    # Input coupling COMMON → LIN(17) / RIN(5)
    wires.append(cap("C202", "2.2u", 95.0, 118.0, PATH_CTRL))
    wires.append(cap("C203", "2.2u", 95.0, 121.0, PATH_CTRL))
    plin = pt2314_pin(u2x, u2y, 17)
    prin = pt2314_pin(u2x, u2y, 5)
    wires.append(wire(50.0, 118.0, 92.46, 118.0))
    wires.append(wire(97.54, 118.0, plin[0], plin[1]))
    wires.append(wire(50.0, 121.0, 92.46, 121.0))
    wires.append(wire(97.54, 121.0, prin[0], prin[1]))

    # REF pin28: R 5.6k + C 22u → AGND (DS)
    pref = pt2314_pin(u2x, u2y, 28)
    wires.append(res("R201", "5.6k", u2x + 20, u2y - 22, PATH_CTRL))
    wires.append(cap("C204", "22u", u2x + 28, u2y - 22, PATH_CTRL))
    wires.append(wire(pref[0], pref[1], u2x + 17.46, u2y - 22))
    wires.append(wire(u2x + 17.46, u2y - 22, u2x + 17.46, 125.0))
    wires.append(wire(u2x + 17.46, 125.0, 50.0, 125.0))

    # Bass L: BIN_L(19) / BOUT_L(20) — R 2.4k + C 100n to AGND (DS app)
    for pin_n, ref_r, ref_c, dy in ((19, "R202", "C205", 0), (20, "R203", "C206", -8)):
        px = pt2314_pin(u2x, u2y, pin_n)
        rx, ry = u2x - 28, u2y + dy
        wires.append(res(ref_r, "2.4k", rx, ry, PATH_CTRL))
        wires.append(cap(ref_c, "100n", rx + 8, ry, PATH_CTRL))
        wires.append(wire(px[0], px[1], rx + 2.54, ry))

    # Bass R: BIN_R(21) / BOUT_R(22)
    for pin_n, ref_r, ref_c, dy in ((21, "R204", "C207", 0), (22, "R205", "C208", -8)):
        px = pt2314_pin(u2x, u2y, pin_n)
        rx, ry = u2x + 28, u2y + dy
        wires.append(res(ref_r, "2.4k", rx, ry, PATH_CTRL))
        wires.append(cap(ref_c, "100n", rx - 8, ry, PATH_CTRL))
        wires.append(wire(px[0], px[1], rx - 2.54, ry))

    # Treble: TREB_L(3) / TREB_R(4) — C 2.7n + R 2.4k (DS)
    for pin_n, ref_c, ref_r in ((3, "C209", "R206"), (4, "C210", "R207")):
        px = pt2314_pin(u2x, u2y, pin_n)
        wires.append(cap(ref_c, "2.7n", px[0] - 10, px[1], PATH_CTRL))
        wires.append(res(ref_r, "2.4k", px[0] - 18, px[1], PATH_CTRL))

    # Outputs OUT_L(24) / OUT_R(23) → TONE_L/R (to Amp path)
    pout_l = pt2314_pin(u2x, u2y, 24)
    pout_r = pt2314_pin(u2x, u2y, 23)
    wires.append(cap("C211", "2.2u", 185.0, 118.0, PATH_CTRL))
    wires.append(cap("C212", "2.2u", 185.0, 121.0, PATH_CTRL))
    wires.append(wire(pout_l[0], pout_l[1], 182.46, 118.0))
    wires.append(wire(pout_r[0], pout_r[1], 182.46, 121.0))
    wires.append(hier_label("TONE_L", "output", 200.66, 118.0, 0))
    wires.append(hier_label("TONE_R", "output", 200.66, 121.0, 0))
    wires.append(wire(187.54, 118.0, 200.66, 118.0))
    wires.append(wire(187.54, 121.0, 200.66, 121.0))

    # DATA(26) / CLK(27) + 4.7k pullups to 3V3
    pdata = pt2314_pin(u2x, u2y, 26)
    pclk = pt2314_pin(u2x, u2y, 27)
    wires.append(res("R210", "4.7k", picox + 15, picoy - 10, PATH_CTRL))
    wires.append(res("R211", "4.7k", picox + 15, picoy - 5, PATH_CTRL))
    wires.append(wire(picox + 17.54, picoy - 10, pdata[0], pdata[1]))
    wires.append(wire(picox + 17.54, picoy - 5, pclk[0], pclk[1]))
    wires.append(label("I2C_SDA", picox + 18, picoy - 11))
    wires.append(label("I2C_SCL", picox + 18, picoy - 6))

    # --- DEST sense ladder (Rh/Rl=10k, Rs=1k) + LEDs ---
    # 3V3 -- Rh -- ADC -- Rl -- GND; ADC -- Rs -- SW_SP3T throws
    lad_x, lad_y = 55.0, 95.0
    wires.append(res("R230", "10k", lad_x, lad_y, PATH_CTRL))  # Rh
    wires.append(res("R231", "10k", lad_x + 12, lad_y, PATH_CTRL))  # Rl
    wires.append(res("R232", "1k", lad_x + 6, lad_y - 10, PATH_CTRL))  # Rs LINE
    wires.append(res("R233", "1k", lad_x + 6, lad_y + 10, PATH_CTRL))  # Rs PHONE
    wires.append(label("DEST_ADC", lad_x + 8, lad_y - 1))
    wires.append(label("+3V3", lad_x - 2, lad_y - 1))
    wires.append(label("D_GND", lad_x + 16, lad_y - 1))
    # Sense switch SP3T: COM=3 → ADC; 1=LINE→3V3 via R232; 2=MUTE NC; 4=PHONE→GND via R233
    swsx, swsy = 80.0, 95.0
    sense_sw = sym("Switch:SW_SP3T", "SW2", "DEST sense (3PDT 3rd pole)", swsx, swsy, 0, PATH_CTRL)
    wires.append(label("to 3V3 via R232", swsx + 8, swsy - 4))
    wires.append(label("MUTE=NC", swsx + 8, swsy))
    wires.append(label("to GND via R233", swsx + 8, swsy + 4))
    # LEDs
    led_syms = (
        sym("Device:LED", "D2", "DEST LINE", 100.0, 90.0, 0, PATH_CTRL)
        + sym("Device:LED", "D3", "DEST PHONE", 100.0, 100.0, 0, PATH_CTRL)
        + res("R234", "1k", 110.0, 90.0, PATH_CTRL)
        + res("R235", "1k", 110.0, 100.0, PATH_CTRL)
    )
    wires.append(label("GP14 LED_LINE", 112, 89))
    wires.append(label("GP15 LED_PHONE", 112, 99))

    # PWR SW + LED
    wires.append(wire(50.0, 150.32, 165.1, 150.32))
    wires.append(hier_label("PD_12V_SW", "output", 200.66, 150.32, 0))
    wires.append(wire(177.8, 150.32, 200.66, 150.32))

    encs = [
        ("ENC_CH", "ENC1", "GP0/1/2", 40.64),
        ("ENC_BASS", "ENC2", "GP3/4/5", 55.88),
        ("ENC_TREBLE", "ENC3", "GP6/7/8", 71.12),
    ]
    enc_syms = "\n".join(
        sym("Device:RotaryEncoder_Switch", ref, f"EC11 {name} {gps}", 35.56, y, 0, PATH_CTRL)
        for name, ref, gps, y in encs
    )

    body = f"""{embed_lib_symbols(CTRL_LIBS)}
{text_note(25.4, 25.4, [
    "ControlPanel — DECISIONS manual volume (2026-08-30)",
    "PT2314 28pin DS / Pico2 / ENC×3 (CH BASS TREBLE) / 2.42″ OLED I2C",
    "J_OLED Conn_01x04: 1=GND 2=3V3 3=SCL 4=SDA (2.42″ SSD1309 128×64 I2C header)",
    "DEST sense: Rh Rl=10k Rs=1k → ADC GP26 + LED GP14/15",
    "Audio DEST SW + A50k pots → OutputStage sheet (same PCB)",
    "Unused PT2314 inputs (LIN1-4/RIN1-4/LOUD): AC-GND or NC — layout TBD",
])}
{hier_label("PD_12V", "input", 30.48, 150.32, 180)}
{hier_label("PD_GND", "bidirectional", 200.66, 152.86, 0)}
{hier_label("I2C_SDA", "bidirectional", 30.48, 135.08, 180)}
{hier_label("I2C_SCL", "bidirectional", 30.48, 137.62, 180)}
{wire(30.48, 135.08, 50.0, 135.08)}
{wire(30.48, 137.62, 50.0, 137.62)}
{sym("MCU_Module:RaspberryPi_Pico", "U1", "Pico 2 / RP2350", picox, picoy, 0, PATH_CTRL)}
{sym("AudioV2:PT2314", "U2", "PT2314-D", u2x, u2y, 0, PATH_CTRL)}
{sym("Connector:Conn_01x04_Pin", "J_OLED", "2.42 OLED I2C GND/3V3/SCL/SDA", 101.6, 78.0, 0, PATH_CTRL)}
{sym("Switch:SW_SPST", "SW1", "PWR SW", 165.1, 150.32, 0, PATH_CTRL)}
{sym("Device:LED", "D1", "12V panel LED", 177.8, 152.86, 0, PATH_CTRL)}
{sense_sw}
{led_syms}
{"".join(parts_bp)}
{enc_syms}
{"".join(wires)}
"""
    return sch_open(UUID_CONTROL_FILE, body)


def relay_board_wired() -> str:
    """RelayBoard with embedded lib_symbols (§11 Q1-B template)."""
    labels = []
    for n in range(1, 6):
        labels.append(hier_label(f"AMP{n}_L", "bidirectional", 200.66, 30.48 + n * 5.08, 0))
        labels.append(hier_label(f"AMP{n}_R", "bidirectional", 210.82, 30.48 + n * 5.08, 0))
        labels.append(hier_label(f"AMP{n}_V+", "output", 220.98, 30.48 + n * 5.08, 0))
        labels.append(hier_label(f"AMP{n}_V-", "output", 231.14, 30.48 + n * 5.08, 0))

    body = f"""{embed_lib_symbols(RELAY_LIBS)}
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
{sym("Interface_Expansion:MCP23017-E/SP", "U1", "MCP23017 addr0x20", 63.5, 50.8, 0, PATH_RELAY, [("Addr", "0x20 A / 0x21 B")])}
{sym("Transistor_Array:ULN2803A", "U2", "ULN2803A", 88.9, 50.8, 0, PATH_RELAY)}
{sym("Relay:AZ850P2-x", "K1", "AZ850 CH1 audio", 114.3, 40.64, 0, PATH_RELAY)}
{sym("Relay:AZ850P2-x", "K2", "AZ850 CH1 pwr", 114.3, 50.8, 0, PATH_RELAY)}
{sym("Relay:AZ850P2-x", "K3", "AZ850 CH2 audio", 127.0, 40.64, 0, PATH_RELAY)}
{sym("Relay:AZ850P2-x", "K4", "AZ850 CH2 pwr", 127.0, 50.8, 0, PATH_RELAY)}
{sym("Relay:AZ850P2-x", "K5", "AZ850 CH3 audio", 139.7, 40.64, 0, PATH_RELAY)}
{sym("Connector:Conn_01x04_Pin", "J_I2C", "I2C to Control", 25.4, 43.18, 0, PATH_RELAY)}
{sym("Connector:Conn_01x03_Pin", "J_COMMON", "COMMON_LR_OUT", 165.1, 90.17, 0, PATH_RELAY)}
{sym("Connector:Screw_Terminal_01x02", "J_AMP1", "AMP1 L/R", 165.1, 35.56, 0, PATH_RELAY)}
"""
    return sch_open(UUID_RELAY_FILE, body)


def output_stage_wired() -> str:
    """OutputStage: AMP_SEL → SW_DP3T DEST → A50k dual pots → PHONE/LINE.

    SW mapping (Audio SW101 / KiCad SW_DP3T):
      L: COM=3, PHONE=1, MUTE=2 (NC), LINE=4
      R: COM=7, PHONE=5, MUTE=6 (NC), LINE=8
    Pot: CW=1/4 from SW, wiper=2/5 out, CCW=3/6 to A_GND.
    """
    wires: list[str] = []
    rvh_x, rvh_y = 127.0, 45.72
    rvl_x, rvl_y = 127.0, 66.04
    sw1x, sw1y = 88.9, 50.8
    sw2x, sw2y = 88.9, 63.5

    wires.append(hier_label("AMP_SEL_L", "input", 30.48, 50.8, 180))
    wires.append(hier_label("AMP_SEL_R", "input", 30.48, 53.34, 180))
    wires.append(hier_label("A_GND", "bidirectional", 30.48, 66.04, 180))
    wires.append(wire(30.48, 50.8, 70.0, 50.8))
    wires.append(wire(30.48, 53.34, 70.0, 53.34))
    wires.append(label("AMP_SEL_L", 50, 50))
    wires.append(label("AMP_SEL_R", 50, 52.5))

    sw_syms = (
        sym("Switch:SW_DP3T", "SW101", "DEST L (PHONE/MUTE/LINE)", sw1x, sw1y, 0, PATH_OUT, unit=1)
        + sym("Switch:SW_DP3T", "SW101", "DEST R (PHONE/MUTE/LINE)", sw2x, sw2y, 0, PATH_OUT, unit=2)
    )
    wires.append(wire(70.0, 50.8, *sw_dp3t_pin(sw1x, sw1y, 3)))
    wires.append(wire(70.0, 53.34, *sw_dp3t_pin(sw2x, sw2y, 7)))
    wires.append(wire(*sw_dp3t_pin(sw1x, sw1y, 1), rvh_x - 12, rvh_y))
    wires.append(wire(*sw_dp3t_pin(sw2x, sw2y, 5), rvh_x - 12, rvh_y + 5))
    wires.append(wire(*sw_dp3t_pin(sw1x, sw1y, 4), rvl_x - 12, rvl_y))
    wires.append(wire(*sw_dp3t_pin(sw2x, sw2y, 8), rvl_x - 12, rvl_y + 5))
    wires.append(label("MUTE NC (2/6)", sw1x + 10, sw1y))

    pot_syms = (
        sym("Device:R_Potentiometer_Dual", "RV101", "A50k Dual HP", rvh_x, rvh_y, 0, PATH_OUT)
        + sym("Device:R_Potentiometer_Dual", "RV102", "A50k Dual LINE", rvl_x, rvl_y, 0, PATH_OUT)
    )
    wires.append(wire(rvh_x - 12, rvh_y, *pot_dual_pin(rvh_x, rvh_y, 1)))
    wires.append(wire(rvh_x - 12, rvh_y + 5, *pot_dual_pin(rvh_x, rvh_y, 4)))
    wires.append(wire(*pot_dual_pin(rvh_x, rvh_y, 3), rvh_x, 80.0))
    wires.append(wire(*pot_dual_pin(rvh_x, rvh_y, 6), rvh_x + 5, 80.0))
    wires.append(wire(rvh_x, 80.0, 30.48, 66.04))
    wires.append(hier_label("PHONE_L", "output", 200.66, 45.72, 0))
    wires.append(hier_label("PHONE_R", "output", 200.66, 48.26, 0))
    wires.append(wire(*pot_dual_pin(rvh_x, rvh_y, 2), 200.66, 45.72))
    wires.append(wire(*pot_dual_pin(rvh_x, rvh_y, 5), 200.66, 48.26))

    wires.append(wire(rvl_x - 12, rvl_y, *pot_dual_pin(rvl_x, rvl_y, 1)))
    wires.append(wire(rvl_x - 12, rvl_y + 5, *pot_dual_pin(rvl_x, rvl_y, 4)))
    wires.append(wire(*pot_dual_pin(rvl_x, rvl_y, 3), rvl_x, 80.0))
    wires.append(wire(*pot_dual_pin(rvl_x, rvl_y, 6), rvl_x + 5, 80.0))
    wires.append(hier_label("LINE_L", "output", 200.66, 50.8, 0))
    wires.append(hier_label("LINE_R", "output", 200.66, 53.34, 0))
    wires.append(wire(*pot_dual_pin(rvl_x, rvl_y, 2), 200.66, 50.8))
    wires.append(wire(*pot_dual_pin(rvl_x, rvl_y, 5), 200.66, 53.34))

    j_syms = (
        sym("Connector:Screw_Terminal_01x02", "J_HP", "to Audio HP Buffer", 165.1, 45.72, 0, PATH_OUT)
        + sym("Connector:Screw_Terminal_01x02", "J_LINE", "LINE OUT", 165.1, 55.88, 0, PATH_OUT)
    )

    body = f"""{embed_lib_symbols(OUTPUT_LIBS)}
{text_note(25.4, 25.4, [
    "OutputStage — manual DEST + volume (Q2-A same PCB as Control)",
    "AMP_SEL → SW_DP3T (LINE/MUTE/PHONE) → RV101/102 A50k Dual",
    "MUTE throws unconnected. Sense pole on ControlPanel SW2.",
    "HP path: wiper → HeadphoneBuffer (Audio/ physical). No PGA.",
])}
{sw_syms}
{pot_syms}
{j_syms}
{"".join(wires)}
"""
    return sch_open(UUID_OUTPUT_FILE, body)


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

    # Control TONE / PD only — volume path is Amp → OutputStage
    for hy in (38.0, 38.5):
        wires.append(junction(200.0, hy))

    # Amp select bus (off-sheet / Relay COMMON after Amp) → Output
    wires.append(wire(140.0, 48.0, 230.0, 40.0))
    wires.append(wire(140.0, 50.54, 230.0, 42.54))
    wires.append(label("AMP_SEL_L", 180, 41))
    wires.append(label("AMP_SEL_R", 180, 43))

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
        ("VCC_TONE", "input", 170.0, 65.0, 180),
        ("TONE_L", "output", 200.0, 38.0, 0),
        ("TONE_R", "output", 200.0, 38.5, 0),
    ]
    output_pins = [
        ("AMP_SEL_L", "input", 230.0, 40.0, 180),
        ("AMP_SEL_R", "input", 230.0, 42.54, 180),
        ("A_GND", "bidirectional", 230.0, 55.24, 180),
        ("PHONE_L", "output", 260.0, 40.0, 0),
        ("PHONE_R", "output", 260.0, 42.54, 0),
        ("LINE_L", "output", 260.0, 45.08, 0),
        ("LINE_R", "output", 260.0, 47.62, 0),
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
    "AudioV2Case — manual volume (DECISIONS 2026-08-30)",
    "Signal: CH→PT2314→Amp→SW_DEST→RV→PHONE/LINE",
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
    if target in ("all", "relay"):
        (ROOT / "RelayBoard.kicad_sch").write_text(relay_board_wired(), encoding="utf-8")
    if target in ("all", "control"):
        (ROOT / "ControlPanel.kicad_sch").write_text(control_panel_wired(), encoding="utf-8")
    if target in ("all", "output"):
        (ROOT / "OutputStage.kicad_sch").write_text(output_stage_wired(), encoding="utf-8")
    if target in ("all", "parent"):
        (ROOT / "AudioV2Case.kicad_sch").write_text(parent_wired(), encoding="utf-8")
    print(f"Wired: {target}")


if __name__ == "__main__":
    main()
