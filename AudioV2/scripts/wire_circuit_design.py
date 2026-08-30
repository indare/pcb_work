#!/usr/bin/env python3
"""Wire AudioV2 schematics per CIRCUIT_DESIGN.md — label-based net connections.

Connectivity is by local/hier labels placed **on pin tips** (KiCad pin ``(at)``).
Wires are optional visual aids only; tip coordinates come from ``pin_connect``.
"""

from __future__ import annotations

import sys
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
    pin_connect,
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
    "Switch:SW_SP3T",  # L/R as separate refs (avoid SW_DP3T multi-unit tip bug)
    "Connector:Screw_Terminal_01x02",
]


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
    """Local label. ``(at x y)`` must sit on a pin tip / wire end / junction."""
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


def net_at(name: str, tip: tuple[float, float], angle: int = 0) -> str:
    """Place a local label exactly on an electrical tip."""
    return label(name, tip[0], tip[1], angle)


def tip(sx: float, sy: float, px: float, py: float, rot: int = 0) -> tuple[float, float]:
    """Lib pin ``(at px py)`` → global tip (Y-flip + symbol rotation)."""
    return pin_connect(sx, sy, rot, px, py, 0, 0.0)


def at(x: float, y: float) -> tuple[float, float]:
    """Snap placement to KiCad grid — must match ``symbol_inst_v10``."""
    return grid(x), grid(y)


def r_pins(rx: float, ry: float, rot: int = 0) -> tuple[tuple[float, float], tuple[float, float]]:
    """Device:R tips (pin1 / pin2)."""
    p1 = tip(rx, ry, 0.0, 3.81, rot)
    p2 = tip(rx, ry, 0.0, -3.81, rot)
    return p1, p2


def led_pins(lx: float, ly: float, rot: int = 0) -> tuple[tuple[float, float], tuple[float, float]]:
    """Device:LED tips (K=1 / A=2)."""
    return tip(lx, ly, -3.81, 0.0, rot), tip(lx, ly, 3.81, 0.0, rot)


def sw_spst_pins(sx: float, sy: float, rot: int = 0) -> tuple[tuple[float, float], tuple[float, float]]:
    return tip(sx, sy, -5.08, 0.0, rot), tip(sx, sy, 5.08, 0.0, rot)


def conn04_pins(
    cx: float, cy: float, rot: int = 0
) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]]:
    return (
        tip(cx, cy, 5.08, 2.54, rot),
        tip(cx, cy, 5.08, 0.0, rot),
        tip(cx, cy, 5.08, -2.54, rot),
        tip(cx, cy, 5.08, -5.08, rot),
    )


def enc_pins(ex: float, ey: float, rot: int = 0) -> dict[str, tuple[float, float]]:
    return {
        "A": tip(ex, ey, -7.62, 2.54, rot),
        "B": tip(ex, ey, -7.62, -2.54, rot),
        "C": tip(ex, ey, -7.62, 0.0, rot),
        "S1": tip(ex, ey, 7.62, 2.54, rot),
        "S2": tip(ex, ey, 7.62, -2.54, rot),
    }


def bp5293_pins(ux: float, uy: float, rot: int = 0) -> dict[str, tuple[float, float]]:
    return {
        "VIN": tip(ux, uy, -7.62, 1.27, rot),
        "GND": tip(ux, uy, 0.0, -6.35, rot),
        "VOUT": tip(ux, uy, 7.62, 1.27, rot),
    }


def pico_pin(sx: float, sy: float, num: int, rot: int = 0) -> tuple[float, float]:
    """RaspberryPi_Pico pin number → tip. GPIO0=1 … GPIO15=20, GPIO26=31, 3V3=36."""
    table: dict[int, tuple[float, float]] = {
        1: (-22.86, 15.24),  # GP0
        2: (-22.86, 12.70),  # GP1
        4: (-22.86, 10.16),  # GP2
        5: (-22.86, 7.62),  # GP3
        6: (-22.86, 5.08),  # GP4
        7: (-22.86, 2.54),  # GP5
        9: (-22.86, 0.0),  # GP6
        10: (-22.86, -2.54),  # GP7
        11: (-22.86, -5.08),  # GP8
        19: (-22.86, -20.32),  # GP14
        20: (-22.86, -22.86),  # GP15
        26: (22.86, 2.54),  # GP20 I2C SDA
        27: (22.86, 0.0),  # GP21 I2C SCL
        31: (22.86, -12.70),  # GP26 ADC0
        36: (5.08, 38.10),  # 3V3
        38: (0.0, -35.56),  # GND
    }
    px, py = table[num]
    return tip(sx, sy, px, py, rot)


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
    """DIP-28 tip coords (lib ``(at)`` + Y flip)."""
    if 1 <= num <= 14:
        return tip(sx, sy, -12.7, 16.51 - (num - 1) * 2.54)
    if 15 <= num <= 28:
        idx = 28 - num
        return tip(sx, sy, 12.7, 16.51 - idx * 2.54)
    raise ValueError(num)


def pot_dual_pin(sx: float, sy: float, num: int) -> tuple[float, float]:
    table = {
        1: (-10.16, -2.54),
        2: (-6.35, 2.54),
        3: (-2.54, -2.54),
        4: (2.54, -2.54),
        5: (6.35, 2.54),
        6: (10.16, -2.54),
    }
    px, py = table[num]
    return tip(sx, sy, px, py)


def sw_dp3t_pin(sx: float, sy: float, num: int) -> tuple[float, float]:
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
    return tip(sx, sy, px, py)


def sw_sp3t_pin(sx: float, sy: float, num: int) -> tuple[float, float]:
    local = {
        1: (5.08, 2.54),
        2: (5.08, 0.0),
        3: (-5.08, 0.0),
        4: (5.08, -2.54),
    }
    px, py = local[num]
    return tip(sx, sy, px, py)


def _cap_net(
    parts: list[str],
    nets: list[str],
    ref: str,
    val: str,
    cx: float,
    cy: float,
    top_net: str,
    bot_net: str,
    path: str,
) -> None:
    """Place C; label pin1 (top) / pin2 (bot) with net names."""
    cx, cy = at(cx, cy)
    top, bot = cap_pins(cx, cy)
    parts.append(cap(ref, val, cx, cy, path))
    nets.append(net_at(top_net, top))
    nets.append(net_at(bot_net, bot))


def _res_net(
    parts: list[str],
    nets: list[str],
    ref: str,
    val: str,
    rx: float,
    ry: float,
    p1_net: str,
    p2_net: str,
    path: str,
) -> None:
    rx, ry = at(rx, ry)
    p1, p2 = r_pins(rx, ry)
    parts.append(res(ref, val, rx, ry, path))
    nets.append(net_at(p1_net, p1))
    nets.append(net_at(p2_net, p2))


def power_module_wired() -> str:
    """PowerModule — label nets on pin tips (primary PD_* ≠ secondary A_GND)."""
    nets: list[str] = []
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
    j_pdx, j_pdy = grid(175.0), grid(33.0)
    j202x, j202y = grid(175.0), grid(55.0)

    pch = ch224_pins(u2x, u2y)
    pdk = dkmw_pins(u1x, u1y)
    pusb = usb16_pins(j1x, j1y)
    u3 = lm7809_pins(u3x, u3y)

    y_sw = pch["12V"][1]
    f1x, f1y = grid(81.28), y_sw
    f1_a, f1_b = fuse_pins(f1x, f1y, 90)
    f1_in, f1_out = (f1_a, f1_b) if f1_a[0] < f1_b[0] else (f1_b, f1_a)

    jpd1, jpd2 = conn02_pins(j_pdx, j_pdy)
    j12, jm12, jagnd = conn03_pins(j202x, j202y)
    hier_x = grid(210.0)

    # USB-C ↔ CH224
    nets.append(net_at("VBUS", pusb["VBUS"]))
    nets.append(net_at("VBUS", pch["VBUS"]))
    nets.append(net_at("PD_GND", pusb["GND"]))
    nets.append(net_at("PD_GND", pch["GND"]))

    # CH224 12V → PD_12V → J_PD / hier
    nets.append(net_at("PD_12V", pch["12V"]))
    nets.append(net_at("PD_12V", jpd1))

    # Panel return PD_12V_SW → F1 → DKMW +Vin
    nets.append(net_at("PD_12V_SW", f1_in))
    nets.append(net_at("DKMW_VIN", f1_out))
    nets.append(net_at("DKMW_VIN", pdk["1"]))
    _cap_net(parts, nets, "C101", "47u", grid(f1_out[0] + 7.62), grid((f1_out[1] + pdk["1"][1]) / 2),
             "DKMW_VIN", "PD_GND", PATH_PWR)

    # PD_GND primary: CH224, DKMW -Vin, J_PD — NOT R.C., NOT 7809
    nets.append(net_at("PD_GND", pdk["2"]))
    nets.append(net_at("PD_GND", jpd2))
    # R.C. (pin 6) open = ON — unique label only on that tip
    nets.append(net_at("RC_OPEN", pdk["6"]))

    # ±12 V / A_GND secondary
    nets.append(net_at("+12V", pdk["3"]))
    nets.append(net_at("+12V", j12))
    nets.append(net_at("-12V", pdk["5"]))
    nets.append(net_at("-12V", jm12))
    nets.append(net_at("A_GND", pdk["4"]))
    nets.append(net_at("A_GND", jagnd))

    _cap_net(parts, nets, "C102", "47u", pdk["3"][0] + 15.24, pdk["3"][1] + 3.81, "+12V", "A_GND", PATH_PWR)
    _cap_net(parts, nets, "C103", "47u", pdk["5"][0] + 15.24, pdk["5"][1] + 3.81, "-12V", "A_GND", PATH_PWR)
    _cap_net(parts, nets, "C104", "0.1u", pdk["3"][0] + 27.94, pdk["3"][1] + 3.81, "+12V", "A_GND", PATH_PWR)

    # LM7809 → VCC_TONE; GND on A_GND only
    nets.append(net_at("+12V", u3["VI"]))
    nets.append(net_at("A_GND", u3["GND"]))
    nets.append(net_at("VCC_TONE", u3["VO"]))
    _cap_net(parts, nets, "C301", "10u", u3x - 12.7, u3["VI"][1] + 3.81, "+12V", "A_GND", PATH_PWR)
    _cap_net(parts, nets, "C302", "0.1u", u3x + 12.7, u3["VO"][1] + 3.81, "VCC_TONE", "A_GND", PATH_PWR)

    nets.append(net_at("PG_NOCONN", pch["PG"]))

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
    "AudioV2 PowerModule — label-wired (§9 / CIRCUIT_DESIGN §4)",
    "USB-C → CH224 → PD_12V/J_PD → (panel SW) → PD_12V_SW → F1 → DKMW_VIN",
    "Primary PD_GND ≠ secondary A_GND. DKMW R.C.=RC_OPEN (open=ON). LM7809 GND→A_GND.",
    "Connectivity = local labels on pin tips (same name = same net).",
])}
{hier_label("PD_12V_SW", "input", 30.48, y_sw, 180)}
{net_at("PD_12V_SW", (30.48, y_sw))}
{hier_label("PD_12V", "output", hier_x, jpd1[1], 0)}
{net_at("PD_12V", (hier_x, jpd1[1]))}
{hier_label("PD_GND", "bidirectional", hier_x, jpd2[1], 0)}
{net_at("PD_GND", (hier_x, jpd2[1]))}
{hier_label("+12V", "output", hier_x, j12[1], 0)}
{net_at("+12V", (hier_x, j12[1]))}
{hier_label("-12V", "output", hier_x, jm12[1], 0)}
{net_at("-12V", (hier_x, jm12[1]))}
{hier_label("A_GND", "bidirectional", hier_x, jagnd[1], 0)}
{net_at("A_GND", (hier_x, jagnd[1]))}
{hier_label("VCC_TONE", "output", hier_x, u3["VO"][1], 0)}
{net_at("VCC_TONE", (hier_x, u3["VO"][1]))}
{"".join(parts)}
{"".join(nets)}
"""
    return sch_open(UUID_POWER_FILE, body)


def control_panel_wired() -> str:
    """ControlPanel — label nets: Pico / ENC×3 / OLED / PT2314 / DEST / PWR SW."""
    u2x, u2y = at(160.0, 120.0)
    picox, picoy = at(76.2, 78.0)
    nets: list[str] = []
    parts: list[str] = []

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
        parts.append(hier_label(name, shape, 30.48, hy, 180))
        nets.append(net_at(name, (30.48, hy)))

    # BP5293 +5V (VIN from +12V, GND D_GND)
    bpx, bpy = at(50.8, 145.0)
    bp = bp5293_pins(bpx, bpy)
    parts.append(sym("BP5293_ROHM:BP5293-50", "U5", "BP5293-50 +5V", bpx, bpy, 0, PATH_CTRL))
    nets.append(net_at("+12V", bp["VIN"]))
    nets.append(net_at("D_GND", bp["GND"]))
    nets.append(net_at("+5V", bp["VOUT"]))

    # PT2314 power / I2C / audio
    nets.append(net_at("VCC_TONE", pt2314_pin(u2x, u2y, 1)))
    nets.append(net_at("A_GND", pt2314_pin(u2x, u2y, 2)))
    nets.append(net_at("D_GND", pt2314_pin(u2x, u2y, 25)))
    _cap_net(parts, nets, "C201", "0.1u", u2x - 22, u2y - 20, "VCC_TONE", "A_GND", PATH_CTRL)

    # COMMON → coupling → LIN(17) / RIN(5)
    _cap_net(parts, nets, "C202", "2.2u", 95.0, 118.0, "COMMON_L", "PT_LIN", PATH_CTRL)
    _cap_net(parts, nets, "C203", "2.2u", 95.0, 121.0, "COMMON_R", "PT_RIN", PATH_CTRL)
    nets.append(net_at("PT_LIN", pt2314_pin(u2x, u2y, 17)))
    nets.append(net_at("PT_RIN", pt2314_pin(u2x, u2y, 5)))

    # REF pin28: R 5.6k + C 22u → A_GND
    nets.append(net_at("PT_REF", pt2314_pin(u2x, u2y, 28)))
    _res_net(parts, nets, "R201", "5.6k", u2x + 20, u2y - 22, "PT_REF", "A_GND", PATH_CTRL)
    _cap_net(parts, nets, "C204", "22u", u2x + 28, u2y - 22, "PT_REF", "A_GND", PATH_CTRL)

    # Bass L/R networks — rows ≥7.62 apart so R/C pin tips never coincide
    for pin_n, ref_r, ref_c, net_name, dx, dy in (
        (19, "R202", "C205", "PT_BIN_L", -35.56, 12.7),
        (20, "R203", "C206", "PT_BOUT_L", -35.56, -12.7),
        (21, "R204", "C207", "PT_BIN_R", 35.56, 12.7),
        (22, "R205", "C208", "PT_BOUT_R", 35.56, -12.7),
    ):
        nets.append(net_at(net_name, pt2314_pin(u2x, u2y, pin_n)))
        _res_net(parts, nets, ref_r, "2.4k", u2x + dx, u2y + dy, net_name, "A_GND", PATH_CTRL)
        _cap_net(
            parts, nets, ref_c, "100n",
            u2x + dx + (10.16 if dx < 0 else -10.16), u2y + dy,
            net_name, "A_GND", PATH_CTRL,
        )

    # Treble — clear of C201 (left of U2); place below pin tips
    for pin_n, ref_c, ref_r, net_name, mid, yoff in (
        (3, "C209", "R206", "PT_TREB_L", "PT_TREB_L_MID", 15.24),
        (4, "C210", "R207", "PT_TREB_R", "PT_TREB_R_MID", 25.4),
    ):
        px = pt2314_pin(u2x, u2y, pin_n)
        nets.append(net_at(net_name, px))
        cx, cy = at(px[0] - 25.4, px[1] + yoff)
        _cap_net(parts, nets, ref_c, "2.7n", cx, cy, net_name, mid, PATH_CTRL)
        _res_net(parts, nets, ref_r, "2.4k", cx - 10.16, cy, mid, "A_GND", PATH_CTRL)

    # OUT → TONE hier (caps spaced > 7.62 so tips don't meet)
    nets.append(net_at("PT_OUT_L", pt2314_pin(u2x, u2y, 24)))
    nets.append(net_at("PT_OUT_R", pt2314_pin(u2x, u2y, 23)))
    _cap_net(parts, nets, "C211", "2.2u", 190.5, 110.0, "PT_OUT_L", "TONE_L", PATH_CTRL)
    _cap_net(parts, nets, "C212", "2.2u", 190.5, 125.0, "PT_OUT_R", "TONE_R", PATH_CTRL)
    parts.append(hier_label("TONE_L", "output", 200.66, 118.0, 0))
    parts.append(hier_label("TONE_R", "output", 200.66, 121.0, 0))
    nets.append(net_at("TONE_L", (200.66, 118.0)))
    nets.append(net_at("TONE_R", (200.66, 121.0)))

    # I2C: PT2314 DATA/CLK + Pico GP20/21 + pullups + OLED
    nets.append(net_at("I2C_SDA", pt2314_pin(u2x, u2y, 26)))
    nets.append(net_at("I2C_SCL", pt2314_pin(u2x, u2y, 27)))
    nets.append(net_at("I2C_SDA", pico_pin(picox, picoy, 26)))
    nets.append(net_at("I2C_SCL", pico_pin(picox, picoy, 27)))
    _res_net(parts, nets, "R210", "4.7k", picox + 15, picoy - 10, "I2C_SDA", "+3V3", PATH_CTRL)
    _res_net(parts, nets, "R211", "4.7k", picox + 15, picoy - 5, "I2C_SCL", "+3V3", PATH_CTRL)
    parts.append(hier_label("I2C_SDA", "bidirectional", 30.48, 135.08, 180))
    parts.append(hier_label("I2C_SCL", "bidirectional", 30.48, 137.62, 180))
    nets.append(net_at("I2C_SDA", (30.48, 135.08)))
    nets.append(net_at("I2C_SCL", (30.48, 137.62)))

    # Pico 3V3 / GND
    nets.append(net_at("+3V3", pico_pin(picox, picoy, 36)))
    nets.append(net_at("D_GND", pico_pin(picox, picoy, 38)))

    # OLED 1×4: GND / 3V3 / SCL / SDA
    oled_x, oled_y = at(101.6, 78.0)
    o1, o2, o3, o4 = conn04_pins(oled_x, oled_y)
    nets.append(net_at("D_GND", o1))
    nets.append(net_at("+3V3", o2))
    nets.append(net_at("I2C_SCL", o3))
    nets.append(net_at("I2C_SDA", o4))

    # DEST sense: 3V3--Rh--ADC--Rl--GND; COM=ADC; LINE→3V3 via Rs; PHONE→GND via Rs
    lad_x, lad_y = at(55.0, 95.0)
    _res_net(parts, nets, "R230", "10k", lad_x, lad_y, "+3V3", "DEST_ADC", PATH_CTRL)
    _res_net(parts, nets, "R231", "10k", lad_x + 12, lad_y, "DEST_ADC", "D_GND", PATH_CTRL)
    _res_net(parts, nets, "R232", "1k", lad_x + 6, lad_y - 10, "DEST_SENSE_LINE", "+3V3", PATH_CTRL)
    _res_net(parts, nets, "R233", "1k", lad_x + 6, lad_y + 10, "DEST_SENSE_PHONE", "D_GND", PATH_CTRL)
    nets.append(net_at("DEST_ADC", pico_pin(picox, picoy, 31)))  # GP26

    swsx, swsy = at(80.0, 95.0)
    nets.append(net_at("DEST_SENSE_LINE", sw_sp3t_pin(swsx, swsy, 1)))
    nets.append(net_at("DEST_SENSE_MUTE_NC", sw_sp3t_pin(swsx, swsy, 2)))
    nets.append(net_at("DEST_ADC", sw_sp3t_pin(swsx, swsy, 3)))
    nets.append(net_at("DEST_SENSE_PHONE", sw_sp3t_pin(swsx, swsy, 4)))

    # DEST LEDs: +3V3 -- R -- A/K -- GP (MCU sink)
    for ref_d, ref_r, gy, gp_pin, net_led in (
        ("D2", "R234", 90.0, 19, "GP14"),
        ("D3", "R235", 100.0, 20, "GP15"),
    ):
        lx, ly = at(100.0, gy)
        rx, ry = at(110.0, gy)
        dk, da = led_pins(lx, ly)
        rp1, rp2 = r_pins(rx, ry)
        parts.append(sym("Device:LED", ref_d, f"DEST {net_led}", lx, ly, 0, PATH_CTRL))
        parts.append(res(ref_r, "1k", rx, ry, PATH_CTRL))
        nets.append(net_at("+3V3", rp1))
        nets.append(net_at(f"LED_{net_led}", rp2))
        nets.append(net_at(f"LED_{net_led}", da))
        nets.append(net_at(net_led, dk))
        nets.append(net_at(net_led, pico_pin(picox, picoy, gp_pin)))

    # PWR SW: PD_12V ↔ PD_12V_SW + panel LED
    sw1x, sw1y = at(165.1, 150.32)
    s1, s2 = sw_spst_pins(sw1x, sw1y)
    nets.append(net_at("PD_12V", s1))
    nets.append(net_at("PD_12V_SW", s2))
    parts.append(hier_label("PD_12V", "input", 30.48, 150.32, 180))
    parts.append(hier_label("PD_12V_SW", "output", 200.66, 150.32, 0))
    parts.append(hier_label("PD_GND", "bidirectional", 200.66, 152.86, 0))
    nets.append(net_at("PD_12V", (30.48, 150.32)))
    nets.append(net_at("PD_12V_SW", (200.66, 150.32)))
    nets.append(net_at("PD_GND", (200.66, 152.86)))
    d1x, d1y = at(177.8, 152.86)
    dk, da = led_pins(d1x, d1y)
    nets.append(net_at("PD_12V_SW", da))
    nets.append(net_at("PD_GND", dk))

    # ENC×3 → GP0–8; C/S2 → D_GND
    encs = [
        ("ENC1", "ENC_CH", 40.64, ("GP0", "GP1", "GP2"), (1, 2, 4)),
        ("ENC2", "ENC_BASS", 55.88, ("GP3", "GP4", "GP5"), (5, 6, 7)),
        ("ENC3", "ENC_TREBLE", 71.12, ("GP6", "GP7", "GP8"), (9, 10, 11)),
    ]
    for ref, name, ey, gp_names, gp_pins in encs:
        ex, ey = at(35.56, ey)
        ep = enc_pins(ex, ey)
        parts.append(sym("Device:RotaryEncoder_Switch", ref, f"EC11 {name}", ex, ey, 0, PATH_CTRL))
        nets.append(net_at(gp_names[0], ep["A"]))
        nets.append(net_at(gp_names[1], ep["B"]))
        nets.append(net_at(gp_names[2], ep["S1"]))
        nets.append(net_at("D_GND", ep["C"]))
        nets.append(net_at("D_GND", ep["S2"]))
        nets.append(net_at(gp_names[0], pico_pin(picox, picoy, gp_pins[0])))
        nets.append(net_at(gp_names[1], pico_pin(picox, picoy, gp_pins[1])))
        nets.append(net_at(gp_names[2], pico_pin(picox, picoy, gp_pins[2])))

    body = f"""{embed_lib_symbols(CTRL_LIBS)}
{text_note(25.4, 25.4, [
    "ControlPanel — label-wired (DECISIONS manual volume)",
    "PT2314 / Pico2 / ENC×3 / 2.42″ OLED I2C / DEST ladder+LED / PWR SW",
    "J_OLED: 1=GND 2=3V3 3=SCL 4=SDA. ENC→GP0-8, DEST_ADC→GP26, LED→GP14/15.",
    "Connectivity = local labels on pin tips (grid-snapped).",
])}
{sym("MCU_Module:RaspberryPi_Pico", "U1", "Pico 2 / RP2350", picox, picoy, 0, PATH_CTRL)}
{sym("AudioV2:PT2314", "U2", "PT2314-D", u2x, u2y, 0, PATH_CTRL)}
{sym("Connector:Conn_01x04_Pin", "J_OLED", "2.42 OLED I2C GND/3V3/SCL/SDA", oled_x, oled_y, 0, PATH_CTRL)}
{sym("Switch:SW_SPST", "SW1", "PWR SW", sw1x, sw1y, 0, PATH_CTRL)}
{sym("Device:LED", "D1", "12V panel LED", d1x, d1y, 0, PATH_CTRL)}
{sym("Switch:SW_SP3T", "SW2", "DEST sense (3PDT 3rd pole)", swsx, swsy, 0, PATH_CTRL)}
{"".join(parts)}
{"".join(nets)}
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
    """OutputStage — label nets: AMP_SEL → SW_SP3T×2 → A50k pots → PHONE/LINE."""
    nets: list[str] = []
    parts: list[str] = []
    rvh_x, rvh_y = at(127.0, 45.72)
    rvl_x, rvl_y = at(127.0, 66.04)
    sw1x, sw1y = at(88.9, 50.8)
    sw2x, sw2y = at(88.9, 66.04)
    jhp_x, jhp_y = at(165.1, 45.72)
    jln_x, jln_y = at(165.1, 55.88)

    parts.append(hier_label("AMP_SEL_L", "input", 30.48, 50.8, 180))
    parts.append(hier_label("AMP_SEL_R", "input", 30.48, 53.34, 180))
    parts.append(hier_label("A_GND", "bidirectional", 30.48, 66.04, 180))
    nets.append(net_at("AMP_SEL_L", (30.48, 50.8)))
    nets.append(net_at("AMP_SEL_R", (30.48, 53.34)))
    nets.append(net_at("A_GND", (30.48, 66.04)))

    # SW_SP3T: COM=3 ← AMP_SEL; 1=PHONE, 2=MUTE NC, 4=LINE
    nets.append(net_at("AMP_SEL_L", sw_sp3t_pin(sw1x, sw1y, 3)))
    nets.append(net_at("AMP_SEL_R", sw_sp3t_pin(sw2x, sw2y, 3)))
    nets.append(net_at("PHONE_PRE_L", sw_sp3t_pin(sw1x, sw1y, 1)))
    nets.append(net_at("PHONE_PRE_R", sw_sp3t_pin(sw2x, sw2y, 1)))
    nets.append(net_at("LINE_PRE_L", sw_sp3t_pin(sw1x, sw1y, 4)))
    nets.append(net_at("LINE_PRE_R", sw_sp3t_pin(sw2x, sw2y, 4)))
    nets.append(net_at("MUTE_NC_L", sw_sp3t_pin(sw1x, sw1y, 2)))
    nets.append(net_at("MUTE_NC_R", sw_sp3t_pin(sw2x, sw2y, 2)))

    # HP pot RV101
    nets.append(net_at("PHONE_PRE_L", pot_dual_pin(rvh_x, rvh_y, 1)))
    nets.append(net_at("PHONE_PRE_R", pot_dual_pin(rvh_x, rvh_y, 4)))
    nets.append(net_at("PHONE_L", pot_dual_pin(rvh_x, rvh_y, 2)))
    nets.append(net_at("PHONE_R", pot_dual_pin(rvh_x, rvh_y, 5)))
    nets.append(net_at("A_GND", pot_dual_pin(rvh_x, rvh_y, 3)))
    nets.append(net_at("A_GND", pot_dual_pin(rvh_x, rvh_y, 6)))

    # LINE pot RV102
    nets.append(net_at("LINE_PRE_L", pot_dual_pin(rvl_x, rvl_y, 1)))
    nets.append(net_at("LINE_PRE_R", pot_dual_pin(rvl_x, rvl_y, 4)))
    nets.append(net_at("LINE_L", pot_dual_pin(rvl_x, rvl_y, 2)))
    nets.append(net_at("LINE_R", pot_dual_pin(rvl_x, rvl_y, 5)))
    nets.append(net_at("A_GND", pot_dual_pin(rvl_x, rvl_y, 3)))
    nets.append(net_at("A_GND", pot_dual_pin(rvl_x, rvl_y, 6)))

    parts.append(hier_label("PHONE_L", "output", 200.66, 45.72, 0))
    parts.append(hier_label("PHONE_R", "output", 200.66, 48.26, 0))
    parts.append(hier_label("LINE_L", "output", 200.66, 50.8, 0))
    parts.append(hier_label("LINE_R", "output", 200.66, 53.34, 0))
    nets.append(net_at("PHONE_L", (200.66, 45.72)))
    nets.append(net_at("PHONE_R", (200.66, 48.26)))
    nets.append(net_at("LINE_L", (200.66, 50.8)))
    nets.append(net_at("LINE_R", (200.66, 53.34)))

    jhp1, jhp2 = (tip(jhp_x, jhp_y, -5.08, 0.0), tip(jhp_x, jhp_y, -5.08, -2.54))
    jln1, jln2 = (tip(jln_x, jln_y, -5.08, 0.0), tip(jln_x, jln_y, -5.08, -2.54))
    nets.append(net_at("PHONE_L", jhp1))
    nets.append(net_at("PHONE_R", jhp2))
    nets.append(net_at("LINE_L", jln1))
    nets.append(net_at("LINE_R", jln2))

    sw_syms = (
        sym("Switch:SW_SP3T", "SW101", "DEST L (PHONE/MUTE/LINE)", sw1x, sw1y, 0, PATH_OUT)
        + sym("Switch:SW_SP3T", "SW102", "DEST R (PHONE/MUTE/LINE)", sw2x, sw2y, 0, PATH_OUT)
    )
    pot_syms = (
        sym("Device:R_Potentiometer_Dual", "RV101", "A50k Dual HP", rvh_x, rvh_y, 0, PATH_OUT)
        + sym("Device:R_Potentiometer_Dual", "RV102", "A50k Dual LINE", rvl_x, rvl_y, 0, PATH_OUT)
    )
    j_syms = (
        sym("Connector:Screw_Terminal_01x02", "J_HP", "to Audio HP Buffer", jhp_x, jhp_y, 0, PATH_OUT)
        + sym("Connector:Screw_Terminal_01x02", "J_LINE", "LINE OUT", jln_x, jln_y, 0, PATH_OUT)
    )

    body = f"""{embed_lib_symbols(OUTPUT_LIBS)}
{text_note(25.4, 25.4, [
    "OutputStage — label-wired DEST + volume (Q2-A)",
    "AMP_SEL → SW101/102 SP3T → RV101/102 A50k Dual → PHONE/LINE",
    "MUTE throws = MUTE_NC_*. Sense pole on ControlPanel SW2.",
    "Connectivity = local labels on pin tips (grid-snapped).",
])}
{sw_syms}
{pot_syms}
{j_syms}
{"".join(parts)}
{"".join(nets)}
"""
    return sch_open(UUID_OUTPUT_FILE, body)


def parent_wired() -> str:
    """Parent — same-named sheet pins auto-connect in KiCad; no extra labels on pins.

    Only place labels for nets that need an off-sheet stub (AMP_SEL) or explicit
    Relay-B ↔ Relay-A / Control bridges when pin coords differ.
    """
    nets: list[str] = []

    def join(name: str, pts: list[tuple[float, float]]) -> None:
        for p in pts:
            nets.append(net_at(name, p))

    # Power / Control / Output pin coords — on sheet edges, ≥10.16 mm apart
    # Power @ (35.56, 30.48) w=30.48 → L=35.56 R=66.04
    power_pins = [
        ("+12V_IN", "input", 35.56, 66.04, 180),
        ("-12V_IN", "input", 35.56, 76.2, 180),
        ("PD_12V_SW", "input", 35.56, 86.36, 180),
        ("+12V", "output", 66.04, 35.56, 0),
        ("-12V", "output", 66.04, 45.72, 0),
        ("A_GND", "bidirectional", 66.04, 55.88, 0),
        ("VCC_TONE", "output", 66.04, 66.04, 0),
        ("PD_12V", "output", 66.04, 76.2, 0),
        ("PD_GND", "bidirectional", 66.04, 86.36, 0),
    ]
    relay_pins_a = [
        ("I2C_SDA", "bidirectional", 88.9, 40.64, 180),
        ("I2C_SCL", "bidirectional", 88.9, 50.8, 180),
        ("3V3", "input", 88.9, 60.96, 180),
        ("D_GND", "input", 88.9, 71.12, 180),
        ("COMMON_L", "output", 144.78, 40.64, 0),
        ("COMMON_R", "output", 144.78, 50.8, 0),
        ("A_GND", "bidirectional", 144.78, 60.96, 0),
    ]
    relay_pins_b = [
        ("I2C_SDA", "bidirectional", 88.9, 83.82, 180),
        ("I2C_SCL", "bidirectional", 88.9, 93.98, 180),
        ("3V3", "input", 88.9, 104.14, 180),
        ("D_GND", "input", 88.9, 114.3, 180),
        ("COMMON_L", "output", 144.78, 83.82, 0),
        ("COMMON_R", "output", 144.78, 93.98, 0),
        ("A_GND", "bidirectional", 144.78, 104.14, 0),
    ]
    control_pins = [
        ("COMMON_L", "input", 152.4, 30.48, 180),
        ("COMMON_R", "input", 152.4, 40.64, 180),
        ("I2C_SDA", "bidirectional", 152.4, 50.8, 180),
        ("I2C_SCL", "bidirectional", 152.4, 60.96, 180),
        ("+12V", "input", 152.4, 71.12, 180),
        ("-12V", "input", 152.4, 81.28, 180),
        ("A_GND", "bidirectional", 152.4, 91.44, 180),
        ("D_GND", "input", 152.4, 101.6, 180),
        ("VCC_TONE", "input", 152.4, 111.76, 180),
        ("PD_12V", "input", 152.4, 121.92, 180),
        ("PD_12V_SW", "output", 208.28, 121.92, 0),
        ("PD_GND", "bidirectional", 208.28, 132.08, 0),
        ("TONE_L", "output", 208.28, 30.48, 0),
        ("TONE_R", "output", 208.28, 40.64, 0),
    ]
    output_pins = [
        ("AMP_SEL_L", "input", 215.9, 40.64, 180),
        ("AMP_SEL_R", "input", 215.9, 50.8, 180),
        ("A_GND", "bidirectional", 215.9, 71.12, 180),
        ("PHONE_L", "output", 266.7, 40.64, 0),
        ("PHONE_R", "output", 266.7, 50.8, 0),
        ("LINE_L", "output", 266.7, 60.96, 0),
        ("LINE_R", "output", 266.7, 71.12, 0),
    ]

    # Explicit label bridges on every sheet pin tip (KiCad 10 does not
    # reliably auto-join same-named pins without a parent-side net object).
    join("+12V", [(66.04, 35.56), (152.4, 71.12)])
    join("-12V", [(66.04, 45.72), (152.4, 81.28)])
    join("A_GND", [
        (66.04, 55.88), (144.78, 60.96), (144.78, 104.14),
        (152.4, 91.44), (215.9, 71.12),
    ])
    join("VCC_TONE", [(66.04, 66.04), (152.4, 111.76)])
    join("PD_12V", [(66.04, 76.2), (152.4, 121.92)])
    join("PD_GND", [(66.04, 86.36), (208.28, 132.08)])
    join("PD_12V_SW", [(35.56, 86.36), (208.28, 121.92)])
    join("I2C_SDA", [(88.9, 40.64), (88.9, 83.82), (152.4, 50.8)])
    join("I2C_SCL", [(88.9, 50.8), (88.9, 93.98), (152.4, 60.96)])
    join("COMMON_L", [(144.78, 40.64), (144.78, 83.82), (152.4, 30.48)])
    join("COMMON_R", [(144.78, 50.8), (144.78, 93.98), (152.4, 40.64)])
    join("D_GND", [(88.9, 71.12), (88.9, 114.3), (152.4, 101.6)])
    join("3V3", [(88.9, 60.96), (88.9, 104.14)])
    join("AMP_SEL_L", [(215.9, 40.64)])
    join("AMP_SEL_R", [(215.9, 50.8)])
    join("TONE_L", [(208.28, 30.48)])
    join("TONE_R", [(208.28, 40.64)])
    join("PHONE_L", [(266.7, 40.64)])
    join("PHONE_R", [(266.7, 50.8)])
    join("LINE_L", [(266.7, 60.96)])
    join("LINE_R", [(266.7, 71.12)])

    from generate_kicad_scaffold import UUID_POWER_INST, UUID_RELAY_A, UUID_RELAY_B  # noqa: E402

    sheets = (
        sheet_block(UUID_POWER_INST, "PowerModule", "PowerModule.kicad_sch", 35.56, 30.48, 30.48, 60.96, power_pins, "2")
        + sheet_block(UUID_RELAY_A, "RelayBoard_A", "RelayBoard.kicad_sch", 88.9, 30.48, 55.88, 45.72, relay_pins_a, "3")
        + sheet_block(UUID_RELAY_B, "RelayBoard_B", "RelayBoard.kicad_sch", 88.9, 78.74, 55.88, 45.72, relay_pins_b, "4")
        + sheet_block(UUID_CONTROL_INST, "ControlPanel", "ControlPanel.kicad_sch", 152.4, 25.4, 55.88, 111.76, control_pins, "5")
        + sheet_block(UUID_OUTPUT_INST, "OutputStage", "OutputStage.kicad_sch", 215.9, 30.48, 50.8, 50.8, output_pins, "6")
    )
    body = f"""\t(lib_symbols)
{text_note(25.4, 15.24, [
    "AudioV2Case — label-wired parent",
    "Sheet pins ≥10.16 mm apart; bridges via local labels on pin tips only.",
    "AMP_SEL_* = stubs until Amp sheet exists.",
])}
{sheets}
{"".join(nets)}
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
