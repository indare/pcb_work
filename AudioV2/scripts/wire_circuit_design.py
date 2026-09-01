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
    UUID_AMP_FILE,
    UUID_AMP_INST,
    UUID_CONTROL_FILE,
    UUID_CONTROL_INST,
    UUID_OUTPUT_FILE,
    UUID_OUTPUT_INST,
    UUID_POWER_FILE,
    UUID_POWER_INST,
    UUID_RELAY_A,
    UUID_RELAY_B,
    UUID_RELAY_FILE,
    hier_label,
    sch_open,
    sheet_block,
    text_note,
    uid,
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
PATH_RELAY_B = f"/{PARENT}/{UUID_RELAY_B}"
PATH_AMP = f"/{PARENT}/{UUID_AMP_INST}"

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
    "Device:C",
    "Device:R",
    "Interface_Expansion:MCP23017-E/SP",
    "Jumper:SolderJumper_2_Open",
    "Transistor_Array:ULN2803A",
    "Relay:AZ850P2-x",
    "Connector:Conn_01x05_Pin",
    "Connector:Conn_01x02_Pin",
    "Connector:Screw_Terminal_01x02",
    "Connector:Screw_Terminal_01x03",
]

OUTPUT_LIBS = [
    "Device:R_Potentiometer_Dual",
    "Switch:SW_SP3T",  # L/R as separate refs (avoid SW_DP3T multi-unit tip bug)
    "Connector:Screw_Terminal_01x02",
]

AMP_LIBS = [
    "Amplifier_Operational:NE5532",
    "Device:R",
    "Device:C",
    "Device:C_Polarized",
    "Connector:Screw_Terminal_01x02",
    "Connector:Screw_Terminal_01x03",
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


def label(name: str, x: float, y: float, angle: int = 0, justify: str = "left") -> str:
    """Local label. ``(at x y)`` must sit on a pin tip / wire end / junction."""
    return f"""\t(label "{name}"
\t\t(at {x} {y} {angle})
\t\t(effects
\t\t\t(font
\t\t\t\t(size 1.27 1.27)
\t\t\t)
\t\t\t(justify {justify} bottom)
\t\t)
\t\t(uuid "{uid()}")
\t)
"""


# KiCad draws label text from the anchor toward the justified side, so the
# direction the text runs is set by justification, not by rotation alone.
LABEL_DIRS = {"r": (0, "left"), "l": (0, "right"), "u": (90, "left"), "d": (90, "right")}


def net_at(name: str, tip: tuple[float, float], direction: str | int = "r") -> str:
    """Place a local label on an electrical tip, text running away from the pin."""
    angle, justify = LABEL_DIRS[direction] if isinstance(direction, str) else (direction, "left")
    return label(name, tip[0], tip[1], angle, justify)


def no_connect_at(tip_xy: tuple[float, float]) -> str:
    """Mark one electrical tip intentionally unconnected."""
    return f"""\t(no_connect
\t\t(at {grid(tip_xy[0])} {grid(tip_xy[1])})
\t\t(uuid "{uid()}")
\t)
"""


def tip(sx: float, sy: float, px: float, py: float, rot: int = 0) -> tuple[float, float]:
    """Lib pin ``(at px py)`` → global tip (Y-flip + symbol rotation)."""
    return pin_connect(sx, sy, rot, px, py, 0, 0.0)


def at(x: float, y: float, step: float = 2.54) -> tuple[float, float]:
    """Snap placement to KiCad grid — must match ``symbol_inst_v10``'s ``grid_step``."""
    return grid(x, step), grid(y, step)


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

    # Panel return PD_12V_SW → F201 → DKMW +Vin
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
            symbol_inst_v10("Device:Fuse", "F201", "3A slow", f1x, f1y, 90, PATH_PWR),
            symbol_inst_v10("AudioV2:DKMW20F-12", "U201", "DKMW20F-12", u1x, u1y, 0, PATH_PWR),
            symbol_inst_v10("Regulator_Linear:LM7809_TO220", "U202", "LM7809 +9V", u3x, u3y, 0, PATH_PWR),
            symbol_inst_v10("Connector:Conn_01x02_Pin", "J_PD", "PD_12V/GND to panel", j_pdx, j_pdy, 0, PATH_PWR),
            symbol_inst_v10("Connector:Conn_01x03_Pin", "J201", "+12/-12/A_GND out", j202x, j202y, 0, PATH_PWR),
        ]
    )

    body = f"""{embed_lib_symbols(lib_ids)}
{text_note(25.4, 20.32, [
    "AudioV2 PowerModule — label-wired (§9 / CIRCUIT_DESIGN §4)",
    "USB-C → CH224 → PD_12V/J_PD → (panel SW) → PD_12V_SW → F201 → DKMW_VIN",
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
        "+5V": 115.0,
    }
    for name, hy in buses.items():
        if name == "A_GND":
            shape = "bidirectional"
        elif name in {"+3V3", "+5V"}:
            shape = "output"
        else:
            shape = "input"
        parts.append(hier_label(name, shape, 30.48, hy, 180))
        nets.append(net_at(name, (30.48, hy)))

    # BP5293 +5V (VIN from +12V, GND D_GND)
    bpx, bpy = at(50.8, 145.0)
    bp = bp5293_pins(bpx, bpy)
    parts.append(sym("BP5293_ROHM:BP5293-50", "U503", "BP5293-50 +5V", bpx, bpy, 0, PATH_CTRL))
    nets.append(net_at("+12V", bp["VIN"]))
    nets.append(net_at("D_GND", bp["GND"]))
    nets.append(net_at("+5V", bp["VOUT"]))

    # PT2314 power / I2C / audio
    nets.append(net_at("VCC_TONE", pt2314_pin(u2x, u2y, 1)))
    nets.append(net_at("A_GND", pt2314_pin(u2x, u2y, 2)))
    nets.append(net_at("D_GND", pt2314_pin(u2x, u2y, 25)))
    _cap_net(parts, nets, "C502", "0.1u", u2x - 22, u2y - 20, "VCC_TONE", "A_GND", PATH_CTRL)

    # COMMON → coupling → LIN(17) / RIN(5)
    _cap_net(parts, nets, "C506", "2.2u", 95.0, 118.0, "COMMON_L", "PT_LIN", PATH_CTRL)
    _cap_net(parts, nets, "C507", "2.2u", 95.0, 121.0, "COMMON_R", "PT_RIN", PATH_CTRL)
    nets.append(net_at("PT_LIN", pt2314_pin(u2x, u2y, 17)))
    nets.append(net_at("PT_RIN", pt2314_pin(u2x, u2y, 5)))

    # REF pin28: R 5.6k + C 22u → A_GND
    nets.append(net_at("PT_REF", pt2314_pin(u2x, u2y, 28)))
    _res_net(parts, nets, "R507", "5.6k", u2x + 20, u2y - 22, "PT_REF", "A_GND", PATH_CTRL)
    _cap_net(parts, nets, "C501", "22u", u2x + 28, u2y - 22, "PT_REF", "A_GND", PATH_CTRL)

    # Bass L/R networks — rows ≥7.62 apart so R/C pin tips never coincide
    for pin_n, ref_r, ref_c, net_name, dx, dy in (
        (19, "R513", "C510", "PT_BIN_L", -35.56, 12.7),
        (20, "R510", "C503", "PT_BOUT_L", -35.56, -12.7),
        (21, "R514", "C511", "PT_BIN_R", 35.56, 12.7),
        (22, "R511", "C504", "PT_BOUT_R", 35.56, -12.7),
    ):
        nets.append(net_at(net_name, pt2314_pin(u2x, u2y, pin_n)))
        _res_net(parts, nets, ref_r, "2.4k", u2x + dx, u2y + dy, net_name, "A_GND", PATH_CTRL)
        _cap_net(
            parts, nets, ref_c, "100n",
            u2x + dx + (10.16 if dx < 0 else -10.16), u2y + dy,
            net_name, "A_GND", PATH_CTRL,
        )

    # Treble — clear of C502 (left of U502); place below pin tips
    for pin_n, ref_c, ref_r, net_name, mid, yoff in (
        (3, "C508", "R512", "PT_TREB_L", "PT_TREB_L_MID", 15.24),
        (4, "C512", "R515", "PT_TREB_R", "PT_TREB_R_MID", 25.4),
    ):
        px = pt2314_pin(u2x, u2y, pin_n)
        nets.append(net_at(net_name, px))
        cx, cy = at(px[0] - 25.4, px[1] + yoff)
        _cap_net(parts, nets, ref_c, "2.7n", cx, cy, net_name, mid, PATH_CTRL)
        _res_net(parts, nets, ref_r, "2.4k", cx - 10.16, cy, mid, "A_GND", PATH_CTRL)

    # OUT → TONE hier (caps spaced > 7.62 so tips don't meet)
    nets.append(net_at("PT_OUT_L", pt2314_pin(u2x, u2y, 24)))
    nets.append(net_at("PT_OUT_R", pt2314_pin(u2x, u2y, 23)))
    _cap_net(parts, nets, "C505", "2.2u", 190.5, 110.0, "PT_OUT_L", "TONE_L", PATH_CTRL)
    _cap_net(parts, nets, "C509", "2.2u", 190.5, 125.0, "PT_OUT_R", "TONE_R", PATH_CTRL)
    parts.append(hier_label("TONE_L", "output", 200.66, 118.0, 0))
    parts.append(hier_label("TONE_R", "output", 200.66, 121.0, 0))
    nets.append(net_at("TONE_L", (200.66, 118.0)))
    nets.append(net_at("TONE_R", (200.66, 121.0)))

    # I2C: PT2314 DATA/CLK + Pico GP20/21 + pullups + OLED
    nets.append(net_at("I2C_SDA", pt2314_pin(u2x, u2y, 26)))
    nets.append(net_at("I2C_SCL", pt2314_pin(u2x, u2y, 27)))
    nets.append(net_at("I2C_SDA", pico_pin(picox, picoy, 26)))
    nets.append(net_at("I2C_SCL", pico_pin(picox, picoy, 27)))
    _res_net(parts, nets, "R501", "4.7k", picox + 15, picoy - 10, "I2C_SDA", "+3V3", PATH_CTRL)
    _res_net(parts, nets, "R502", "4.7k", picox + 15, picoy - 5, "I2C_SCL", "+3V3", PATH_CTRL)
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
    _res_net(parts, nets, "R505", "10k", lad_x, lad_y, "+3V3", "DEST_ADC", PATH_CTRL)
    _res_net(parts, nets, "R506", "10k", lad_x + 12, lad_y, "DEST_ADC", "D_GND", PATH_CTRL)
    _res_net(parts, nets, "R503", "1k", lad_x + 6, lad_y - 10, "DEST_SENSE_LINE", "+3V3", PATH_CTRL)
    _res_net(parts, nets, "R509", "1k", lad_x + 6, lad_y + 10, "DEST_SENSE_PHONE", "D_GND", PATH_CTRL)
    nets.append(net_at("DEST_ADC", pico_pin(picox, picoy, 31)))  # GP26

    swsx, swsy = at(80.0, 95.0)
    nets.append(net_at("DEST_SENSE_LINE", sw_sp3t_pin(swsx, swsy, 1)))
    nets.append(net_at("DEST_SENSE_MUTE_NC", sw_sp3t_pin(swsx, swsy, 2)))
    nets.append(net_at("DEST_ADC", sw_sp3t_pin(swsx, swsy, 3)))
    nets.append(net_at("DEST_SENSE_PHONE", sw_sp3t_pin(swsx, swsy, 4)))

    # DEST LEDs: +3V3 -- R -- A/K -- GP (MCU sink)
    for ref_d, ref_r, gy, gp_pin, net_led in (
        ("D501", "R504", 90.0, 19, "GP14"),
        ("D502", "R508", 100.0, 20, "GP15"),
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
        ("ENC501", "ENC_CH", 40.64, ("GP0", "GP1", "GP2"), (1, 2, 4)),
        ("ENC502", "ENC_BASS", 55.88, ("GP3", "GP4", "GP5"), (5, 6, 7)),
        ("ENC503", "ENC_TREBLE", 71.12, ("GP6", "GP7", "GP8"), (9, 10, 11)),
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
    "J_OLED501: 1=GND 2=3V3 3=SCL 4=SDA. ENC→GP0-8, DEST_ADC→GP26, LED→GP14/15.",
    "Connectivity = local labels on pin tips (grid-snapped).",
])}
{sym("MCU_Module:RaspberryPi_Pico", "U501", "Pico 2 / RP2350", picox, picoy, 0, PATH_CTRL)}
{sym("AudioV2:PT2314", "U502", "PT2314-D", u2x, u2y, 0, PATH_CTRL)}
{sym("Connector:Conn_01x04_Pin", "J_OLED501", "2.42 OLED I2C GND/3V3/SCL/SDA", oled_x, oled_y, 0, PATH_CTRL)}
{sym("Switch:SW_SPST", "SW502", "PWR SW", sw1x, sw1y, 0, PATH_CTRL)}
{sym("Device:LED", "D503", "12V panel LED", d1x, d1y, 0, PATH_CTRL)}
{sym("Switch:SW_SP3T", "SW501", "DEST sense (3PDT 3rd pole)", swsx, swsy, 0, PATH_CTRL)}
{"".join(parts)}
{"".join(nets)}
"""
    return sch_open(UUID_CONTROL_FILE, body)


def relay_board_wired() -> str:
    """Five-channel Amp input/power selector; instantiate twice for ten Amps."""
    parts: list[str] = []
    nets: list[str] = []
    ncs: list[str] = []

    # A3 with generous column pitch: pin labels are the only wiring here, so
    # every label needs room to point away from its symbol.
    mcp_x, mcp_y = at(88.9, 76.2)
    set_x, set_y = at(134.62, 50.8)
    reset_x, reset_y = at(134.62, 111.76)
    LEFT, RIGHT, UP, DOWN = "l", "r", "u", "d"

    def rsym(
        lib_id: str,
        ref_a: str,
        ref_b: str,
        value: str,
        x: float,
        y: float,
        extra: list[tuple[str, str]] | None = None,
        description: str = "",
        prop_dx: float = 0.0,
        rot: int = 0,
        footprint: str = "",
        grid_step: float = 2.54,
    ) -> str:
        """One shared-sheet symbol with unique A/B instance references."""
        return symbol_inst_v10(
            lib_id,
            ref_a,
            value,
            x,
            y,
            rot,
            PATH_RELAY,
            extra_props=extra,
            footprint=footprint,
            description=description,
            instance_refs=[(PATH_RELAY, ref_a), (PATH_RELAY_B, ref_b)],
            prop_dx=prop_dx,
            grid_step=grid_step,
        )

    def mcp_pin(px: float, py: float) -> tuple[float, float]:
        return tip(mcp_x, mcp_y, px, py)

    def uln_pin(x: float, y: float, channel: int, output: bool) -> tuple[float, float]:
        px = 10.16 if output else -10.16
        py = 5.08 - (channel - 1) * 2.54
        return tip(x, y, px, py)

    def relay_pins(x: float, y: float) -> dict[int, tuple[float, float]]:
        local = {
            1: (-12.7, 7.62),
            2: (-2.54, 7.62),
            3: (0, -7.62),
            4: (2.54, 7.62),
            5: (-7.62, 7.62),
            6: (-7.62, -7.62),
            7: (12.7, 7.62),
            8: (10.16, -7.62),
            9: (7.62, 7.62),
            10: (-12.7, -7.62),
        }
        return {num: tip(x, y, px, py) for num, (px, py) in local.items()}

    parts.append(
        rsym(
            "Interface_Expansion:MCP23017-E/SP",
            "U302",
            "U402",
            "MCP23017",
            mcp_x,
            mcp_y,
            [("Addr", "JP A1/A0 → 0x20-0x23; A2=0")],
            description="Coil command expander, address strapped by JP301/JP302",
        )
    )
    parts.append(
        rsym(
            "Transistor_Array:ULN2803A",
            "U301",
            "U401",
            "ULN2803A",
            set_x,
            set_y,
            description="SET pulse driver, one output per channel pair",
        )
    )
    parts.append(
        rsym(
            "Transistor_Array:ULN2803A",
            "U303",
            "U403",
            "ULN2803A",
            reset_x,
            reset_y,
            description="RESET pulse driver, one output per channel pair",
        )
    )

    # MCP core: shared I2C, 3.3 V logic. A2=0; A1/A0 are strap-selectable.
    for name, point, angle in [
        ("I2C_SCL", mcp_pin(-12.7, 20.32), LEFT),
        ("I2C_SDA", mcp_pin(-12.7, 17.78), LEFT),
        ("3V3", mcp_pin(0, 25.4), UP),
        ("D_GND", mcp_pin(0, -25.4), DOWN),
        ("3V3", mcp_pin(-12.7, -2.54), LEFT),
        ("ADDR_A0", mcp_pin(-12.7, -15.24), LEFT),
        ("ADDR_A1", mcp_pin(-12.7, -17.78), LEFT),
        ("D_GND", mcp_pin(-12.7, -20.32), LEFT),
    ]:
        nets.append(net_at(name, point, angle))
    ncs.extend([no_connect_at(mcp_pin(-12.7, 5.08)), no_connect_at(mcp_pin(-12.7, 2.54))])

    # Default 0x20 (both jumpers open). Close A0 and/or A1 for 0x21-0x23.
    # Hand-tuned layout (2026-08-31): strap sits beside U302, 0R/1206 hand-solder
    # jumper (SolderJumper_2_Open has no footprint with a fittable 0R pad). R
    # pin1 faces U302's ADDR pin, pin2 faces D_GND. JP pin1 faces the pulldown,
    # pin2 ties to U302's 3V3 pin (shared by both straps).
    strap_fp = "Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder"

    def addr_strap(
        ref_r_a: str,
        ref_r_b: str,
        ref_j_a: str,
        ref_j_b: str,
        net: str,
        r_x: float,
        r_y: float,
        r_rot: int,
        jp_x: float,
        jp_y: float,
    ) -> None:
        parts.append(
            rsym(
                "Device:R",
                ref_r_a,
                ref_r_b,
                "10k",
                r_x,
                r_y,
                rot=r_rot,
                footprint=strap_fp,
                description=f"MCP {net} pulldown",
                grid_step=1.27,
            )
        )
        parts.append(
            rsym(
                "Device:R",
                ref_j_a,
                ref_j_b,
                "0R",
                jp_x,
                jp_y,
                rot=90,
                footprint=strap_fp,
                description=f"0R strap: fit to tie {net} to 3V3, leave empty for 0",
                grid_step=1.27,
            )
        )
        rp1, rp2 = r_pins(r_x, r_y, r_rot)
        jp1, jp2 = r_pins(jp_x, jp_y, 90)
        nets.extend(
            [
                net_at(net, rp1, UP),
                net_at("D_GND", rp2, DOWN),
                net_at(net, jp1, RIGHT),
                net_at("3V3", jp2, LEFT),
            ]
        )

    # RelayBoard's hand layout sits on a 1.27 mm (half-grid) pitch, finer than
    # this generator's default 2.54 mm — at(..., 1.27) keeps these exact.
    addr_strap("R301", "R401", "JP301", "JP401", "ADDR_A0", *at(71.12, 87.63, 1.27), 180, *at(63.5, 91.44, 1.27))
    addr_strap("R302", "R402", "JP302", "JP402", "ADDR_A1", *at(71.12, 97.79, 1.27), 0, *at(63.5, 96.52, 1.27))

    # Local decoupling sits on the J_I2C entry (3V3 / +5V), not the analog rails.
    # Hand-tuned layout (2026-08-31): C301/C302 stack vertically and share one
    # D_GND pin between them (C301 top pin=3V3, C302 bottom pin=+5V).
    for ref_a, ref_b, value, x, y, rail, rail_up in [
        ("C301", "C401", "100nF", 38.1, 49.53, "3V3", True),
        ("C302", "C402", "100nF", 38.1, 57.15, "+5V", False),
    ]:
        cx, cy = at(x, y, 1.27)
        parts.append(rsym("Device:C", ref_a, ref_b, value, cx, cy, grid_step=1.27))
        cp1, cp2 = cap_pins(cx, cy)
        if rail_up:
            nets.extend([net_at(rail, cp1, UP), net_at("D_GND", cp2, DOWN)])
        else:
            nets.extend([net_at("D_GND", cp1, UP), net_at(rail, cp2, DOWN)])

    # GPA0..4 drive SET; GPB0..4 drive RESET. Audio and power relay coils
    # are paired per channel so their state can never diverge.
    for channel in range(1, 6):
        set_cmd = f"CH{channel}_SET_CMD"
        reset_cmd = f"CH{channel}_RST_CMD"
        nets.append(net_at(set_cmd, mcp_pin(12.7, 20.32 - (channel - 1) * 2.54), RIGHT))
        nets.append(net_at(reset_cmd, mcp_pin(12.7, -2.54 - (channel - 1) * 2.54), RIGHT))
        nets.append(net_at(set_cmd, uln_pin(set_x, set_y, channel, False), LEFT))
        nets.append(net_at(reset_cmd, uln_pin(reset_x, reset_y, channel, False), LEFT))
        nets.append(net_at(f"CH{channel}_SET", uln_pin(set_x, set_y, channel, True), RIGHT))
        nets.append(net_at(f"CH{channel}_RST", uln_pin(reset_x, reset_y, channel, True), RIGHT))

    # Unused MCP GPIO and ULN channels are explicit NCs.
    for index in range(5, 8):
        ncs.append(no_connect_at(mcp_pin(12.7, 20.32 - index * 2.54)))
        ncs.append(no_connect_at(mcp_pin(12.7, -2.54 - index * 2.54)))
    for x, y in [(set_x, set_y), (reset_x, reset_y)]:
        for channel in range(6, 9):
            ncs.append(no_connect_at(uln_pin(x, y, channel, False)))
            ncs.append(no_connect_at(uln_pin(x, y, channel, True)))
        nets.append(net_at("D_GND", tip(x, y, 0, -17.78), DOWN))
        nets.append(net_at("+5V", tip(x, y, 10.16, 7.62), RIGHT))

    # Per channel: one DPDT selects stereo Amp input, another selects ±12 V.
    # Their SET and RESET coils share one ULN output pair.
    for channel in range(1, 6):
        row_y = grid(40.64 + (channel - 1) * 40.64)
        audio_x, power_x = 190.5, 241.3
        audio_num, power_num = 300 + 2 * channel - 1, 300 + 2 * channel
        parts.append(
            rsym(
                "Relay:AZ850P2-x",
                f"K{audio_num}",
                f"K{audio_num + 100}",
                f"CH{channel} AUDIO",
                audio_x,
                row_y,
                description=f"AZ850P2-5 — routes TONE_L/R to Amp {channel} input",
            )
        )
        parts.append(
            rsym(
                "Relay:AZ850P2-x",
                f"K{power_num}",
                f"K{power_num + 100}",
                f"CH{channel} POWER",
                power_x,
                row_y,
                description=f"AZ850P2-5 — routes +/-12V to Amp {channel}",
            )
        )
        audio = relay_pins(audio_x, row_y)
        power = relay_pins(power_x, row_y)

        # Coil-side labels run vertically so the four per edge stay legible.
        for relay in (audio, power):
            nets.extend(
                [
                    net_at("+5V", relay[1], UP),
                    net_at("+5V", relay[10], DOWN),
                    net_at(f"CH{channel}_SET", relay[5], UP),
                    net_at(f"CH{channel}_RST", relay[6], DOWN),
                ]
            )
            ncs.extend([no_connect_at(relay[2]), no_connect_at(relay[9])])

        # Contact commons receive the toned source and ±12 V rails.
        nets.extend(
            [
                net_at("TONE_L", audio[8], DOWN),
                net_at("TONE_R", audio[3], DOWN),
                net_at(f"AMP{channel}_L", audio[7], UP),
                net_at(f"AMP{channel}_R", audio[4], UP),
                net_at("+12V", power[8], DOWN),
                net_at("-12V", power[3], DOWN),
                net_at(f"AMP{channel}_V+", power[7], UP),
                net_at(f"AMP{channel}_V-", power[4], UP),
            ]
        )

        audio_jx, power_jx = 297.18, 342.9
        parts.append(
            rsym(
                "Connector:Screw_Terminal_01x02",
                f"J_AUD{300 + channel}",
                f"J_AUD{400 + channel}",
                f"AMP{channel} IN",
                audio_jx,
                row_y,
                description=f"To Amp {channel} J701 (L/R)",
                prop_dx=12.7,
            )
        )
        parts.append(
            rsym(
                "Connector:Screw_Terminal_01x03",
                f"J_PWR{300 + channel}",
                f"J_PWR{400 + channel}",
                f"AMP{channel} PWR",
                power_jx,
                row_y,
                description=f"To Amp {channel} J703 (+12 / A_GND / -12)",
                prop_dx=12.7,
            )
        )
        # Screw-terminal symbols face left (generic Conn helpers face right).
        ja1, ja2 = (audio_jx - 5.08, row_y), (audio_jx - 5.08, row_y + 2.54)
        jp1, jpg, jp3 = (
            (power_jx - 5.08, row_y - 2.54),
            (power_jx - 5.08, row_y),
            (power_jx - 5.08, row_y + 2.54),
        )
        nets.extend(
            [
                net_at(f"AMP{channel}_L", ja1, LEFT),
                net_at(f"AMP{channel}_R", ja2, LEFT),
                net_at(f"AMP{channel}_V+", jp1, LEFT),
                net_at("A_GND", jpg, LEFT),
                net_at(f"AMP{channel}_V-", jp3, LEFT),
            ]
        )

    # Board harnesses: control, toned stereo source, analog rails.
    # Left column = connectors. Caps sit on J_I2C; address straps sit on MCP A0/A1.
    ji_x, ji_y = at(16.51, 46.99, 1.27)
    jt_x, jt_y = at(50.8, 91.44)
    jr_x, jr_y = at(50.8, 121.92)
    parts.append(
        rsym(
            "Connector:Conn_01x05_Pin",
            "J_I2C301",
            "J_I2C401",
            "CTRL",
            ji_x,
            ji_y,
            description="From ControlPanel: SDA / SCL / 3V3 / +5V / D_GND",
            prop_dx=-12.7,
            grid_step=1.27,
        )
    )
    for pin_y, name in zip([5.08, 2.54, 0, -2.54, -5.08], ["I2C_SDA", "I2C_SCL", "3V3", "+5V", "D_GND"], strict=True):
        nets.append(net_at(name, tip(ji_x, ji_y, 5.08, pin_y), RIGHT))
    parts.append(
        rsym(
            "Connector:Conn_01x02_Pin",
            "J_TONE301",
            "J_TONE401",
            "TONE IN",
            jt_x,
            jt_y,
            description="From ControlPanel PT2314: TONE_L / TONE_R. Shield at Control only.",
            prop_dx=-12.7,
        )
    )
    jt1, jt2 = conn02_pins(jt_x, jt_y)
    nets.extend([net_at("TONE_L", jt1, RIGHT), net_at("TONE_R", jt2, RIGHT)])

    # Analog rail entry from PowerModule J201. A_GND passes straight through to
    # every J_PWR so one 3P cable per Amp carries both rails and the return.
    parts.append(
        rsym(
            "Connector:Screw_Terminal_01x03",
            "J_RAIL301",
            "J_RAIL401",
            "RAIL IN",
            jr_x,
            jr_y,
            description="From PowerModule J201: +12V / A_GND / -12V (relays switch rails only)",
            prop_dx=12.7,
        )
    )
    for name, pin_y in [("+12V", -2.54), ("A_GND", 0.0), ("-12V", 2.54)]:
        nets.append(net_at(name, (jr_x - 5.08, jr_y + pin_y), LEFT))

    body = f"""{embed_lib_symbols(RELAY_LIBS)}
{text_note(20.32, 15.24, [
    "RelayBoard — 5ch input + power selector; instantiate twice",
    "CHn_SET / CHn_RST = coil pulse nets; CHn_*_CMD = MCP to ULN logic.",
    "Audio and power AZ850 pairs share SET/RESET: 100ms pulse, never hold.",
    "JP A1/A0 (open=0): 00=0x20 A, 01=0x21 B, 10=0x22 C, 11=0x23 D. A2=GND.",
    "Silk table next to JP301/JP302 on the PCB.",
    "J_TONE = L/R only. Cable shield drains at ControlPanel, not here (J_RAIL has A_GND).",
    "+5V/D_GND from ControlPanel; contacts switch +/-12V only.",
    "J_RAIL = PowerModule J201. A_GND is never switched: straight to each J_PWR.",
])}
{hier_label("I2C_SDA", "bidirectional", 25.4, 39.37, 0)}
{hier_label("I2C_SCL", "bidirectional", 34.29, 41.91, 0)}
{hier_label("3V3", "input", 27.94, 46.99, 0)}
{hier_label("+5V", "input", 26.67, 57.15, 180)}
{hier_label("D_GND", "input", 31.75, 50.8, 180)}
{hier_label("TONE_L", "input", 34.29, 90.17, 90)}
{hier_label("TONE_R", "input", 34.29, 92.71, 270)}
{hier_label("+12V", "input", 30.48, 114.3, 90)}
{hier_label("-12V", "input", 30.48, 119.38, 270)}
{hier_label("A_GND", "bidirectional", 29.21, 115.57, 180)}
{"".join(parts)}
{"".join(nets)}
{"".join(ncs)}
"""
    return sch_open(UUID_RELAY_FILE, body, paper="A3")


def amp_module_wired() -> str:
    """AudioV2 Amp reference design; manufacture ten identical PCBs."""
    parts: list[str] = []
    nets: list[str] = []
    wires: list[str] = []
    r_fp = "Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder"
    c_fp = "Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder"
    bulk_fp = "Capacitor_SMD:CP_Elec_10x12.6"
    out_fp = "Capacitor_THT:CP_Radial_D12.5mm_P5.00mm"
    conn2_fp = (
        "TerminalBlock_Phoenix:"
        "TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal"
    )
    conn3_fp = (
        "TerminalBlock_Phoenix:"
        "TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal"
    )

    def two_pin(
        lib_id: str,
        ref: str,
        value: str,
        x: float,
        y: float,
        net1: str,
        net2: str,
        footprint: str,
        description: str,
        polarized: bool = False,
    ) -> None:
        parts.append(
            symbol_inst_v10(
                lib_id,
                ref,
                value,
                x,
                y,
                0,
                PATH_AMP,
                footprint=footprint,
                description=description,
            )
        )
        p1, p2 = cap_pins(x, y)
        if lib_id == "Device:R":
            p1, p2 = r_pins(x, y)
        nets.append(net_at(net1, p1))
        nets.append(net_at(net2, p2))

    # Physical connectors.
    for ref, value, x, y, footprint in [
        ("J701", "AMP_IN L/R", 30.48, 60.96, conn2_fp),
        ("J702", "AMP_OUT L/R", 160.02, 60.96, conn2_fp),
        ("J703", "+12V / A_GND / -12V", 30.48, 111.76, conn3_fp),
    ]:
        lib_id = (
            "Connector:Screw_Terminal_01x03"
            if ref == "J703"
            else "Connector:Screw_Terminal_01x02"
        )
        parts.append(
            symbol_inst_v10(
                lib_id,
                ref,
                value,
                x,
                y,
                0,
                PATH_AMP,
                footprint=footprint,
            )
        )
    def screw02_pins(x: float, y: float) -> tuple[tuple[float, float], tuple[float, float]]:
        return (x - 5.08, y), (x - 5.08, y + 2.54)

    def screw03_pins(
        x: float, y: float
    ) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
        return (x - 5.08, y - 2.54), (x - 5.08, y), (x - 5.08, y + 2.54)

    for name, p in zip(("L_IN", "R_IN"), screw02_pins(30.48, 60.96), strict=True):
        nets.append(net_at(name, p))
    for name, p in zip(("L_OUT", "R_OUT"), screw02_pins(160.02, 60.96), strict=True):
        nets.append(net_at(name, p))
    for name, p in zip(
        ("+12V", "A_GND", "-12V"), screw03_pins(30.48, 111.76), strict=True
    ):
        nets.append(net_at(name, p))

    # Input coupling and bias. 100 nF film and 10 uF electrolytic are parallel.
    two_pin("Device:R", "R701", "220k", 45.72, 45.72, "L_IN", "A_GND", r_fp, "L input pulldown")
    two_pin("Device:R", "R706", "220k", 45.72, 78.74, "R_IN", "A_GND", r_fp, "R input pulldown")
    two_pin("Device:C", "C701", "100nF film", 55.88, 45.72, "L_IN", "L_AC", "Capacitor_THT:C_Rect_L7.2mm_W2.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2", "L input film coupling")
    two_pin("Device:C_Polarized", "C702", "10uF", 66.04, 45.72, "L_IN", "L_AC", "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm", "L input electrolytic coupling", True)
    two_pin("Device:C", "C704", "100nF film", 55.88, 78.74, "R_IN", "R_AC", "Capacitor_THT:C_Rect_L7.2mm_W2.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2", "R input film coupling")
    two_pin("Device:C_Polarized", "C705", "10uF", 66.04, 78.74, "R_IN", "R_AC", "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm", "R input electrolytic coupling", True)
    two_pin("Device:R", "R702", "1k", 76.2, 45.72, "L_AC", "A_GND", r_fp, "L non-inverting bias; 1/10 refine")
    two_pin("Device:R", "R707", "1k", 76.2, 78.74, "R_AC", "A_GND", r_fp, "R non-inverting bias; 1/10 refine")

    # Draw the input bus so the signal path reads left-to-right like the v1
    # schematic (net_at labels above still carry the actual connectivity).
    j701_l, j701_r = screw02_pins(30.48, 60.96)
    wires.extend(
        [
            wire(j701_l[0], j701_l[1], j701_l[0], 41.91),
            wire(j701_l[0], 41.91, 66.04, 41.91),
            junction(45.72, 41.91),
            junction(55.88, 41.91),
            wire(j701_r[0], j701_r[1], j701_r[0], 74.93),
            wire(j701_r[0], 74.93, 66.04, 74.93),
            junction(45.72, 74.93),
            junction(55.88, 74.93),
        ]
    )

    # Dual op amp, gain = 1 + 20k/20k = 2 (headroom; source volume handles loudness).
    # Unit A/B = R/L is fixed by the proven PCB routing; only the *schematic*
    # position is chosen here, so each unit sits in its own channel's row
    # (R701-704/R709/R710/R708/C706 are already at y=78.74-99.06; L's
    # counterparts at y=45.72-66.04) instead of crossing to the other row.
    for unit, x, y in [(1, 101.6, 83.82), (2, 101.6, 50.8), (3, 127.0, 111.76)]:
        parts.append(
            symbol_inst_v10(
                "Amplifier_Operational:NE5532",
                "AMP701",
                "NE5532 / DIP-8 compatible",
                x,
                y,
                0,
                PATH_AMP,
                unit=unit,
                footprint="Package_DIP:DIP-8_W7.62mm_Socket",
                extra_props=[("AssemblyQty", "10")],
                description="AudioV2 replaceable dual op amp; high-speed decoupling fitted",
            )
        )
    for net, p in [
        # Unit A = R, unit B = L (proven PCB routing); positions match the
        # row swap above.
        ("R_OUT_OP", tip(101.6, 83.82, 7.62, 0)),
        ("R_INV", tip(101.6, 83.82, -7.62, -2.54)),
        ("R_AC", tip(101.6, 83.82, -7.62, 2.54)),
        ("L_OUT_OP", tip(101.6, 50.8, 7.62, 0)),
        ("L_INV", tip(101.6, 50.8, -7.62, -2.54)),
        ("L_AC", tip(101.6, 50.8, -7.62, 2.54)),
        ("-12V", tip(127.0, 111.76, -2.54, -7.62)),
        ("+12V", tip(127.0, 111.76, -2.54, 7.62)),
    ]:
        nets.append(net_at(net, p))
    two_pin("Device:R", "R704", "20k", 88.9, 66.04, "L_INV", "A_GND", r_fp, "L gain resistor; Rf=Rg=20k")
    two_pin("Device:R", "R709", "20k", 88.9, 99.06, "R_INV", "A_GND", r_fp, "R gain resistor; Rf=Rg=20k")
    two_pin("Device:R", "R705", "20k", 111.76, 66.04, "L_OUT_OP", "L_INV", r_fp, "L feedback; gain 2")
    two_pin("Device:R", "R710", "20k", 111.76, 99.06, "R_OUT_OP", "R_INV", r_fp, "R feedback; gain 2")
    two_pin("Device:R", "R703", "47R", 127.0, 50.8, "L_OUT_OP", "L_OUT_PRE", r_fp, "L output isolation")
    two_pin("Device:R", "R708", "47R", 127.0, 83.82, "R_OUT_OP", "R_OUT_PRE", r_fp, "R output isolation")
    two_pin("Device:C_Polarized", "C703", "470uF 25V", 139.7, 50.8, "L_OUT_PRE", "L_OUT", out_fp, "L output coupling; compact D12.5/P5", True)
    two_pin("Device:C_Polarized", "C706", "470uF 25V", 139.7, 83.82, "R_OUT_PRE", "R_OUT", out_fp, "R output coupling; compact D12.5/P5", True)

    # Draw the output tail so it visibly lands on J702 (net_at labels above
    # still carry the actual connectivity).
    j702_l, j702_r = screw02_pins(160.02, 60.96)
    wires.extend(
        [
            wire(139.7, 54.61, j702_l[0], 54.61),
            wire(j702_l[0], 54.61, j702_l[0], j702_l[1]),
            wire(139.7, 87.63, j702_r[0], 87.63),
            wire(j702_r[0], 87.63, j702_r[0], j702_r[1]),
        ]
    )

    # Power reservoir and high-frequency bypass. Negative bulk has + at A_GND.
    two_pin("Device:C_Polarized", "C707", "100uF 35V polymer", 55.88, 111.76, "+12V", "A_GND", bulk_fp, "V+ local bulk at power connector", True)
    two_pin("Device:C_Polarized", "C708", "100uF 35V polymer", 66.04, 111.76, "A_GND", "-12V", bulk_fp, "V- local bulk at power connector", True)
    two_pin("Device:C", "C709", "100nF 50V X7R", 78.74, 111.76, "+12V", "A_GND", c_fp, "V+ local decoupling")
    two_pin("Device:C", "C710", "100nF 50V X7R", 88.9, 111.76, "A_GND", "-12V", c_fp, "V- local decoupling")
    two_pin("Device:C", "C711", "1nF 50V C0G", 99.06, 111.76, "+12V", "A_GND", c_fp, "V+ high-speed bypass")
    two_pin("Device:C", "C712", "1nF 50V C0G", 109.22, 111.76, "A_GND", "-12V", c_fp, "V- high-speed bypass")

    body = f"""{embed_lib_symbols(AMP_LIBS)}
{text_note(25.4, 20.32, [
    "AudioV2 AmpModule — reference circuit; manufacture x10",
    "Supply: +/-12 V. Gain: 2 (20k/20k). DIP-8 socket.",
    "100uF/rail bulk + 100nF + 1nF local bypass for high-speed op amps.",
    "AMP* selection remains on RelayBoard terminal interfaces.",
])}
{hier_label("L_IN", "input", 20.32, 60.96, 180)}
{hier_label("R_IN", "input", 20.32, 71.12, 180)}
{hier_label("+12V", "input", 20.32, 101.6, 180)}
{hier_label("-12V", "input", 20.32, 111.76, 180)}
{hier_label("A_GND", "bidirectional", 20.32, 121.92, 180)}
{hier_label("L_OUT", "output", 180.34, 60.96, 0)}
{hier_label("R_OUT", "output", 180.34, 71.12, 0)}
{"".join(parts)}
{"".join(nets)}
{"".join(wires)}
"""
    return sch_open(UUID_AMP_FILE, body)


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

    # HP pot RV601
    nets.append(net_at("PHONE_PRE_L", pot_dual_pin(rvh_x, rvh_y, 1)))
    nets.append(net_at("PHONE_PRE_R", pot_dual_pin(rvh_x, rvh_y, 4)))
    nets.append(net_at("PHONE_L", pot_dual_pin(rvh_x, rvh_y, 2)))
    nets.append(net_at("PHONE_R", pot_dual_pin(rvh_x, rvh_y, 5)))
    nets.append(net_at("A_GND", pot_dual_pin(rvh_x, rvh_y, 3)))
    nets.append(net_at("A_GND", pot_dual_pin(rvh_x, rvh_y, 6)))

    # LINE pot RV602
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
        sym("Switch:SW_SP3T", "SW601", "DEST L (PHONE/MUTE/LINE)", sw1x, sw1y, 0, PATH_OUT)
        + sym("Switch:SW_SP3T", "SW602", "DEST R (PHONE/MUTE/LINE)", sw2x, sw2y, 0, PATH_OUT)
    )
    pot_syms = (
        sym("Device:R_Potentiometer_Dual", "RV601", "A50k Dual HP", rvh_x, rvh_y, 0, PATH_OUT)
        + sym("Device:R_Potentiometer_Dual", "RV602", "A50k Dual LINE", rvl_x, rvl_y, 0, PATH_OUT)
    )
    j_syms = (
        sym("Connector:Screw_Terminal_01x02", "J_HP601", "to Audio HP Buffer", jhp_x, jhp_y, 0, PATH_OUT)
        + sym("Connector:Screw_Terminal_01x02", "J_LINE601", "LINE OUT", jln_x, jln_y, 0, PATH_OUT)
    )

    body = f"""{embed_lib_symbols(OUTPUT_LIBS)}
{text_note(25.4, 25.4, [
    "OutputStage — label-wired DEST + volume (Q2-A)",
    "AMP_SEL → SW601/102 SP3T → RV601/102 A50k Dual → PHONE/LINE",
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
        ("TONE_L", "input", 144.78, 35.56, 0),
        ("TONE_R", "input", 144.78, 40.64, 0),
        ("+12V", "input", 144.78, 45.72, 0),
        ("-12V", "input", 144.78, 50.8, 0),
        ("A_GND", "bidirectional", 144.78, 55.88, 0),
        ("+5V", "input", 144.78, 60.96, 0),
    ]
    relay_pins_b = [
        ("I2C_SDA", "bidirectional", 88.9, 83.82, 180),
        ("I2C_SCL", "bidirectional", 88.9, 93.98, 180),
        ("3V3", "input", 88.9, 104.14, 180),
        ("D_GND", "input", 88.9, 114.3, 180),
        ("TONE_L", "input", 144.78, 83.82, 0),
        ("TONE_R", "input", 144.78, 88.9, 0),
        ("+12V", "input", 144.78, 93.98, 0),
        ("-12V", "input", 144.78, 99.06, 0),
        ("A_GND", "bidirectional", 144.78, 104.14, 0),
        ("+5V", "input", 144.78, 109.22, 0),
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
        ("+3V3", "output", 152.4, 132.08, 180),
        ("+5V", "output", 208.28, 111.76, 0),
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
    amp_pins = [
        ("L_IN", "input", 88.9, 142.24, 180),
        ("R_IN", "input", 88.9, 152.4, 180),
        ("+12V", "input", 88.9, 162.56, 180),
        ("-12V", "input", 88.9, 172.72, 180),
        ("A_GND", "bidirectional", 88.9, 182.88, 180),
        ("L_OUT", "output", 144.78, 142.24, 0),
        ("R_OUT", "output", 144.78, 152.4, 0),
    ]

    # Explicit label bridges on every sheet pin tip (KiCad 10 does not
    # reliably auto-join same-named pins without a parent-side net object).
    join("+12V", [(66.04, 35.56), (152.4, 71.12)])
    join("-12V", [(66.04, 45.72), (152.4, 81.28)])
    join("A_GND", [
        (66.04, 55.88), (144.78, 55.88), (144.78, 104.14),
        (152.4, 91.44), (215.9, 71.12), (88.9, 182.88),
    ])
    join("VCC_TONE", [(66.04, 66.04), (152.4, 111.76)])
    join("PD_12V", [(66.04, 76.2), (152.4, 121.92)])
    join("PD_GND", [(66.04, 86.36), (208.28, 132.08)])
    join("PD_12V_SW", [(35.56, 86.36), (208.28, 121.92)])
    join("I2C_SDA", [(88.9, 40.64), (88.9, 83.82), (152.4, 50.8)])
    join("I2C_SCL", [(88.9, 50.8), (88.9, 93.98), (152.4, 60.96)])
    # External line/source input into the tone stage.
    join("COMMON_L", [(152.4, 30.48)])
    join("COMMON_R", [(152.4, 40.64)])
    join("D_GND", [(88.9, 71.12), (88.9, 114.3), (152.4, 101.6)])
    join("3V3", [(88.9, 60.96), (88.9, 104.14), (152.4, 132.08)])
    join("+5V", [(144.78, 60.96), (144.78, 109.22), (208.28, 111.76)])
    join("AMP_SEL_L", [(215.9, 40.64), (144.78, 142.24)])
    join("AMP_SEL_R", [(215.9, 50.8), (144.78, 152.4)])
    join("TONE_L", [(208.28, 30.48), (144.78, 35.56), (144.78, 83.82), (88.9, 142.24)])
    join("TONE_R", [(208.28, 40.64), (144.78, 40.64), (144.78, 88.9), (88.9, 152.4)])
    join("+12V", [(144.78, 45.72), (144.78, 93.98), (88.9, 162.56)])
    join("-12V", [(144.78, 50.8), (144.78, 99.06), (88.9, 172.72)])
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
        + sheet_block(UUID_AMP_INST, "AmpModule_Reference", "AmpModule.kicad_sch", 88.9, 132.08, 55.88, 60.96, amp_pins, "7")
    )
    body = f"""\t(lib_symbols)
{text_note(25.4, 15.24, [
    "AudioV2Case — label-wired parent",
    "Sheet pins ≥10.16 mm apart; bridges via local labels on pin tips only.",
    "AmpModule_Reference = one circuit/BOM instance; manufacture x10.",
    "RelayBoard J_AMP terminal wiring selects the physical Amp; see WIRING.md.",
])}
{sheets}
{"".join(nets)}
"""
    return sch_open(PARENT, body)


def main() -> None:
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    flags = sys.argv[2:]

    # 手編集所有シート（AudioV2/AGENT_HANDOFF.md §2.8）。KiCad 側が正なので
    # 機械的に上書きしない。--force-<name> は「シートを丸ごと作り直す」ときだけの
    # 脱出ハッチで、通常運用では使わない。
    HAND_EDITED = {
        "relay": (
            "RelayBoard.kicad_sch",
            relay_board_wired,
            "addr strap footprint/position, C301/C302, J_I2C — see §2.6",
        ),
        "power": (
            "PowerModule.kicad_sch",
            power_module_wired,
            "generator is a generation behind: it still emits the on-board USB-C + CH224 "
            "PD front-end, while the sheet takes PD from an external module (J202/J203)",
        ),
        "output": (
            "OutputStage.kicad_sch",
            output_stage_wired,
            "generator does not emit J_RAIL601 (RAIL IN); 5 parts differ in position",
        ),
    }
    # 生成コード所有シート（回せばそのまま正）
    GENERATED = {
        "amp": ("AmpModule.kicad_sch", amp_module_wired),
        "control": ("ControlPanel.kicad_sch", control_panel_wired),
        "parent": ("AudioV2Case.kicad_sch", parent_wired),
    }

    for name, (fn, build) in GENERATED.items():
        if target in ("all", name):
            (ROOT / fn).write_text(build(), encoding="utf-8")

    skipped = []
    for name, (fn, build, why) in HAND_EDITED.items():
        if target not in ("all", name):
            continue
        if f"--force-{name}" in flags:
            (ROOT / fn).write_text(build(), encoding="utf-8")
        else:
            skipped.append(name)
            print(
                f"SKIPPED {fn}: hand-edited sheet (AGENT_HANDOFF.md §2.8). {why}. "
                f"Make logic changes in KiCad, or pass --force-{name} to overwrite anyway.",
                file=sys.stderr,
            )

    print(f"Wired: {target}" + (f" (skipped: {', '.join(skipped)})" if skipped else ""))


if __name__ == "__main__":
    main()
