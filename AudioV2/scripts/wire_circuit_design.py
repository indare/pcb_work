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
    "Device:D_Schottky",
    "power:PWR_FLAG",
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


def screw_pins(cx: float, cy: float, n: int, rot: int = 0) -> list[tuple[float, float]]:
    """Connector:Screw_Terminal_01x0n のピン先端。

    注意: 端子台はピンが **x=-5.08（左側）**。`Conn_01x0n_Pin`（x=+5.08）用の
    conn02_pins / conn03_pins をそのまま使うと座標が 10.16 mm ずれて繋がらない。
    """
    # 実シンボルの (at): 01x02 は pin1@y=0、01x03 は pin1@y=2.54。
    # 中心対称ではないので (n-1)*1.27 では 2 ピンのときに 1.27 ずれる。
    top = 0.0 if n == 2 else (n - 1) * 1.27
    return [tip(cx, cy, -5.08, top - i * 2.54, rot) for i in range(n)]


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
    """RaspberryPi_Pico pin number → tip. GPIO0=1 … GPIO15=20, GPIO26=31, 3V3=36, VSYS=39."""
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
        36: (5.08, 38.10),  # 3V3 (Pico 内蔵レギュレータの「出力」)
        39: (-5.08, 38.10),  # VSYS (Pico への給電「入力」)
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

    # ±15 V / A_GND secondary
    nets.append(net_at("+15V", pdk["3"]))
    nets.append(net_at("+15V", j12))
    nets.append(net_at("-15V", pdk["5"]))
    nets.append(net_at("-15V", jm12))
    nets.append(net_at("A_GND", pdk["4"]))
    nets.append(net_at("A_GND", jagnd))

    _cap_net(parts, nets, "C102", "47u", pdk["3"][0] + 15.24, pdk["3"][1] + 3.81, "+15V", "A_GND", PATH_PWR)
    _cap_net(parts, nets, "C103", "47u", pdk["5"][0] + 15.24, pdk["5"][1] + 3.81, "-15V", "A_GND", PATH_PWR)
    _cap_net(parts, nets, "C104", "0.1u", pdk["3"][0] + 27.94, pdk["3"][1] + 3.81, "+15V", "A_GND", PATH_PWR)

    # LM7809 → VCC_TONE; GND on A_GND only
    nets.append(net_at("+15V", u3["VI"]))
    nets.append(net_at("A_GND", u3["GND"]))
    nets.append(net_at("VCC_TONE", u3["VO"]))
    _cap_net(parts, nets, "C301", "10u", u3x - 12.7, u3["VI"][1] + 3.81, "+15V", "A_GND", PATH_PWR)
    _cap_net(parts, nets, "C302", "0.1u", u3x + 12.7, u3["VO"][1] + 3.81, "VCC_TONE", "A_GND", PATH_PWR)

    nets.append(net_at("PG_NOCONN", pch["PG"]))

    parts.extend(
        [
            symbol_inst_v10("Connector:USB_C_Receptacle_USB2.0_16P", "J1", "USB-C PD in", j1x, j1y, 0, PATH_PWR),
            symbol_inst_v10("AudioV2:CH224_50224", "U2", "50224_CH224 12V", u2x, u2y, 0, PATH_PWR),
            symbol_inst_v10("Device:Fuse", "F201", "3A slow", f1x, f1y, 90, PATH_PWR),
            symbol_inst_v10("AudioV2:DKMW20F-15", "U201", "DKMW20F-15", u1x, u1y, 0, PATH_PWR),
            symbol_inst_v10("Regulator_Linear:LM7809_TO220", "U202", "LM7809 +9V", u3x, u3y, 0, PATH_PWR),
            symbol_inst_v10("Connector:Conn_01x02_Pin", "J_PD", "PD_12V/GND to panel", j_pdx, j_pdy, 0, PATH_PWR),
            symbol_inst_v10("Connector:Conn_01x03_Pin", "J201", "+15/-15/A_GND out", j202x, j202y, 0, PATH_PWR),
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
{hier_label("+15V", "output", hier_x, j12[1], 0)}
{net_at("+15V", (hier_x, j12[1]))}
{hier_label("-15V", "output", hier_x, jm12[1], 0)}
{net_at("-15V", (hier_x, jm12[1]))}
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
        "+15V": 131.0,
        "+3V3": 112.0,
    }
    # -15V と +5V は 2026-09-02 にインタフェースから外した。
    #   -15V: ControlPanel は +15V しか使わない（BP5293 の入力）。受け取るだけで
    #         中で誰も使っておらず label_dangling になっていた
    #   +5V : BP5293 の出力。旧 RelayBoard の AZ850 コイル用に外へ出していたが、
    #         アナログスイッチ化で消費先が消えた。いまは D404 経由で Pico VSYS が
    #         内部で使うだけなので、外へ出す意味がない
    for name, hy in buses.items():
        if name == "A_GND":
            shape = "bidirectional"
        elif name == "+3V3":
            shape = "output"
        else:
            shape = "input"
        parts.append(hier_label(name, shape, 30.48, hy, 180))
        nets.append(net_at(name, (30.48, hy)))

    # BP5293 +5V (VIN from +15V, GND D_GND)
    bpx, bpy = at(50.8, 145.0)
    bp = bp5293_pins(bpx, bpy)
    parts.append(sym("BP5293_ROHM:BP5293-50", "U403", "BP5293-50 +5V", bpx, bpy, 0, PATH_CTRL))
    nets.append(net_at("+15V", bp["VIN"]))
    nets.append(net_at("D_GND", bp["GND"]))
    nets.append(net_at("+5V", bp["VOUT"]))

    # PT2314 power / I2C / audio
    nets.append(net_at("VCC_TONE", pt2314_pin(u2x, u2y, 1)))
    nets.append(net_at("A_GND", pt2314_pin(u2x, u2y, 2)))
    nets.append(net_at("D_GND", pt2314_pin(u2x, u2y, 25)))
    _cap_net(parts, nets, "C402", "0.1u", u2x - 22, u2y - 20, "VCC_TONE", "A_GND", PATH_CTRL)

    # COMMON → coupling → LIN(17) / RIN(5)
    _cap_net(parts, nets, "C406", "2.2u", 95.0, 118.0, "COMMON_L", "PT_LIN", PATH_CTRL)
    _cap_net(parts, nets, "C407", "2.2u", 95.0, 121.0, "COMMON_R", "PT_RIN", PATH_CTRL)
    nets.append(net_at("PT_LIN", pt2314_pin(u2x, u2y, 17)))
    nets.append(net_at("PT_RIN", pt2314_pin(u2x, u2y, 5)))

    # REF pin28: R 5.6k + C 22u → A_GND
    nets.append(net_at("PT_REF", pt2314_pin(u2x, u2y, 28)))
    _res_net(parts, nets, "R407", "5.6k", u2x + 20, u2y - 22, "PT_REF", "A_GND", PATH_CTRL)
    _cap_net(parts, nets, "C401", "22u", u2x + 28, u2y - 22, "PT_REF", "A_GND", PATH_CTRL)

    # Bass L/R networks — rows ≥7.62 apart so R/C pin tips never coincide
    for pin_n, ref_r, ref_c, net_name, dx, dy in (
        (19, "R413", "C410", "PT_BIN_L", -35.56, 12.7),
        (20, "R410", "C403", "PT_BOUT_L", -35.56, -12.7),
        (21, "R414", "C411", "PT_BIN_R", 35.56, 12.7),
        (22, "R411", "C404", "PT_BOUT_R", 35.56, -12.7),
    ):
        nets.append(net_at(net_name, pt2314_pin(u2x, u2y, pin_n)))
        _res_net(parts, nets, ref_r, "2.4k", u2x + dx, u2y + dy, net_name, "A_GND", PATH_CTRL)
        _cap_net(
            parts, nets, ref_c, "100n",
            u2x + dx + (10.16 if dx < 0 else -10.16), u2y + dy,
            net_name, "A_GND", PATH_CTRL,
        )

    # Treble — clear of C402 (left of U402); place below pin tips
    for pin_n, ref_c, ref_r, net_name, mid, yoff in (
        (3, "C408", "R412", "PT_TREB_L", "PT_TREB_L_MID", 15.24),
        (4, "C412", "R415", "PT_TREB_R", "PT_TREB_R_MID", 25.4),
    ):
        px = pt2314_pin(u2x, u2y, pin_n)
        nets.append(net_at(net_name, px))
        cx, cy = at(px[0] - 25.4, px[1] + yoff)
        _cap_net(parts, nets, ref_c, "2.7n", cx, cy, net_name, mid, PATH_CTRL)
        _res_net(parts, nets, ref_r, "2.4k", cx - 10.16, cy, mid, "A_GND", PATH_CTRL)

    # OUT → TONE hier (caps spaced > 7.62 so tips don't meet)
    nets.append(net_at("PT_OUT_L", pt2314_pin(u2x, u2y, 24)))
    nets.append(net_at("PT_OUT_R", pt2314_pin(u2x, u2y, 23)))
    _cap_net(parts, nets, "C405", "2.2u", 190.5, 110.0, "PT_OUT_L", "TONE_L", PATH_CTRL)
    _cap_net(parts, nets, "C409", "2.2u", 190.5, 125.0, "PT_OUT_R", "TONE_R", PATH_CTRL)
    parts.append(hier_label("TONE_L", "output", 200.66, 118.0, 0))
    parts.append(hier_label("TONE_R", "output", 200.66, 121.0, 0))
    nets.append(net_at("TONE_L", (200.66, 118.0)))
    nets.append(net_at("TONE_R", (200.66, 121.0)))

    # I2C: PT2314 DATA/CLK + Pico GP20/21 + pullups + OLED
    nets.append(net_at("I2C_SDA", pt2314_pin(u2x, u2y, 26)))
    nets.append(net_at("I2C_SCL", pt2314_pin(u2x, u2y, 27)))
    nets.append(net_at("I2C_SDA", pico_pin(picox, picoy, 26)))
    nets.append(net_at("I2C_SCL", pico_pin(picox, picoy, 27)))
    _res_net(parts, nets, "R401", "4.7k", picox + 15, picoy - 10, "I2C_SDA", "+3V3", PATH_CTRL)
    _res_net(parts, nets, "R402", "4.7k", picox + 15, picoy - 5, "I2C_SCL", "+3V3", PATH_CTRL)
    parts.append(hier_label("I2C_SDA", "bidirectional", 30.48, 135.08, 180))
    parts.append(hier_label("I2C_SCL", "bidirectional", 30.48, 137.62, 180))
    nets.append(net_at("I2C_SDA", (30.48, 135.08)))
    nets.append(net_at("I2C_SCL", (30.48, 137.62)))

    # Pico 3V3 / GND
    nets.append(net_at("+3V3", pico_pin(picox, picoy, 36)))
    nets.append(net_at("D_GND", pico_pin(picox, picoy, 38)))

    # Pico VSYS 給電: BP5293 の +5V をショットキー経由で入れる。
    # pin36 の 3V3 は Pico 内蔵レギュレータの「出力」で、OLED / I2C プルアップ /
    # PT2314 ロジックはそこから貰っている。VSYS を繋がないと Pico 自身が起動せず、
    # 基板単体で動かない（2026-09-02 に ERC の pin_not_connected で発見）。
    # ダイオードを挟むのは Raspberry Pi の推奨。Pico 内部は VBUS→ショットキー→VSYS
    # なので、開発中に USB を挿しても外部 5V と衝突しない。
    dsx, dsy = at(76.2, 145.0)
    dk, da = led_pins(dsx, dsy)          # D_Schottky は LED と同じピン配置（K=1 / A=2）
    parts.append(sym("Device:D_Schottky", "D404", "1N5817", dsx, dsy, 0, PATH_CTRL))
    nets.append(net_at("+5V", da, "r"))
    nets.append(net_at("VSYS", dk, "l"))
    nets.append(net_at("VSYS", pico_pin(picox, picoy, 39)))
    # VSYS はダイオード（パッシブ）の先なので、ERC から見ると電源供給元が居ない。
    # PWR_FLAG で「ここから先は給電されている」と宣言する。
    # sym() は座標を 2.54 グリッドにスナップするので、at() で揃えた値を
    # シンボルとラベルの両方に使う（生の座標を渡すとラベルだけずれる）。
    fx, fy = at(71.12, 149.86)
    parts.append(sym("power:PWR_FLAG", "#FLG0401", "PWR_FLAG", fx, fy, 0, PATH_CTRL))
    nets.append(net_at("VSYS", (fx, fy), "u"))

    # OLED 1×4: GND / 3V3 / SCL / SDA
    oled_x, oled_y = at(101.6, 78.0)
    o1, o2, o3, o4 = conn04_pins(oled_x, oled_y)
    nets.append(net_at("D_GND", o1))
    nets.append(net_at("+3V3", o2))
    nets.append(net_at("I2C_SCL", o3))
    nets.append(net_at("I2C_SDA", o4))

    # DEST sense: 3V3--Rh--ADC--Rl--GND; COM=ADC; LINE→3V3 via Rs; PHONE→GND via Rs
    lad_x, lad_y = at(55.0, 95.0)
    _res_net(parts, nets, "R405", "10k", lad_x, lad_y, "+3V3", "DEST_ADC", PATH_CTRL)
    _res_net(parts, nets, "R406", "10k", lad_x + 12, lad_y, "DEST_ADC", "D_GND", PATH_CTRL)
    _res_net(parts, nets, "R403", "1k", lad_x + 6, lad_y - 10, "DEST_SENSE_LINE", "+3V3", PATH_CTRL)
    _res_net(parts, nets, "R409", "1k", lad_x + 6, lad_y + 10, "DEST_SENSE_PHONE", "D_GND", PATH_CTRL)
    nets.append(net_at("DEST_ADC", pico_pin(picox, picoy, 31)))  # GP26

    swsx, swsy = at(80.0, 95.0)
    nets.append(net_at("DEST_SENSE_LINE", sw_sp3t_pin(swsx, swsy, 1)))
    nets.append(net_at("DEST_SENSE_MUTE_NC", sw_sp3t_pin(swsx, swsy, 2)))
    nets.append(net_at("DEST_ADC", sw_sp3t_pin(swsx, swsy, 3)))
    nets.append(net_at("DEST_SENSE_PHONE", sw_sp3t_pin(swsx, swsy, 4)))

    # DEST LEDs: +3V3 -- R -- A/K -- GP (MCU sink)
    for ref_d, ref_r, gy, gp_pin, net_led in (
        ("D401", "R404", 90.0, 19, "GP14"),
        ("D402", "R408", 100.0, 20, "GP15"),
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
        ("ENC401", "ENC_CH", 40.64, ("GP0", "GP1", "GP2"), (1, 2, 4)),
        ("ENC402", "ENC_BASS", 55.88, ("GP3", "GP4", "GP5"), (5, 6, 7)),
        ("ENC403", "ENC_TREBLE", 71.12, ("GP6", "GP7", "GP8"), (9, 10, 11)),
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
    "J_OLED401: 1=GND 2=3V3 3=SCL 4=SDA. ENC→GP0-8, DEST_ADC→GP26, LED→GP14/15.",
    "Connectivity = local labels on pin tips (grid-snapped).",
])}
{sym("MCU_Module:RaspberryPi_Pico", "U401", "Pico 2 / RP2350", picox, picoy, 0, PATH_CTRL)}
{sym("AudioV2:PT2314", "U402", "PT2314-D", u2x, u2y, 0, PATH_CTRL)}
{sym("Connector:Conn_01x04_Pin", "J_OLED401", "2.42 OLED I2C GND/3V3/SCL/SDA", oled_x, oled_y, 0, PATH_CTRL)}
{sym("Switch:SW_SPST", "SW402", "PWR SW", sw1x, sw1y, 0, PATH_CTRL)}
{sym("Device:LED", "D403", "12V panel LED", d1x, d1y, 0, PATH_CTRL)}
{sym("Switch:SW_SP3T", "SW401", "DEST sense (3PDT 3rd pole)", swsx, swsy, 0, PATH_CTRL)}
{"".join(parts)}
{"".join(nets)}
"""
    return sch_open(UUID_CONTROL_FILE, body)


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
    AmpBank ↔ Control bridges when pin coords differ.
    """
    nets: list[str] = []

    def join(name: str, pts: list[tuple[float, float]]) -> None:
        for p in pts:
            nets.append(net_at(name, p))

    # Power / AmpBank / Control / Output pin coords — on sheet edges, ≥10.16 mm apart
    # Power @ (35.56, 30.48) w=30.48 → L=35.56 R=66.04
    power_pins = [
        ("PD_12V_SW", "input", 35.56, 86.36, 180),
        ("+15V", "output", 66.04, 35.56, 0),
        ("-15V", "output", 66.04, 45.72, 0),
        ("A_GND", "bidirectional", 66.04, 55.88, 0),
        ("VCC_TONE", "output", 66.04, 66.04, 0),
        ("PD_12V", "output", 66.04, 76.2, 0),
        ("PD_GND", "bidirectional", 66.04, 86.36, 0),
    ]
    # AmpBank pin names must match the hier_label() names in amp_bank_wired() (§2.9).
    amp_bank_pins = [
        ("I2C_SDA", "bidirectional", 88.9, 40.64, 180),
        ("I2C_SCL", "bidirectional", 88.9, 50.8, 180),
        ("3V3", "input", 88.9, 60.96, 180),
        ("D_GND", "input", 88.9, 71.12, 180),
        ("TONE_L", "input", 88.9, 81.28, 180),
        ("TONE_R", "input", 88.9, 91.44, 180),
        ("+15V", "input", 88.9, 101.6, 180),
        ("-15V", "input", 88.9, 111.76, 180),
        ("A_GND", "bidirectional", 88.9, 121.92, 180),
        ("AMP_SEL_L", "output", 144.78, 40.64, 0),
        ("AMP_SEL_R", "output", 144.78, 50.8, 0),
    ]
    control_pins = [
        ("COMMON_L", "input", 152.4, 30.48, 180),
        ("COMMON_R", "input", 152.4, 40.64, 180),
        ("I2C_SDA", "bidirectional", 152.4, 50.8, 180),
        ("I2C_SCL", "bidirectional", 152.4, 60.96, 180),
        ("+15V", "input", 152.4, 71.12, 180),
        ("A_GND", "bidirectional", 152.4, 91.44, 180),
        ("D_GND", "input", 152.4, 101.6, 180),
        ("VCC_TONE", "input", 152.4, 111.76, 180),
        ("PD_12V", "input", 152.4, 121.92, 180),
        ("PD_12V_SW", "output", 208.28, 121.92, 0),
        ("PD_GND", "bidirectional", 208.28, 132.08, 0),
        ("TONE_L", "output", 208.28, 30.48, 0),
        ("TONE_R", "output", 208.28, 40.64, 0),
        ("+3V3", "output", 152.4, 132.08, 180),
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
    join("+15V", [(66.04, 35.56), (152.4, 71.12), (88.9, 101.6)])
    join("-15V", [(66.04, 45.72), (88.9, 111.76)])  # Control は -15V を使わない
    join("A_GND", [
        (66.04, 55.88), (152.4, 91.44), (215.9, 71.12), (88.9, 121.92),
    ])
    join("VCC_TONE", [(66.04, 66.04), (152.4, 111.76)])
    join("PD_12V", [(66.04, 76.2), (152.4, 121.92)])
    join("PD_GND", [(66.04, 86.36), (208.28, 132.08)])
    join("PD_12V_SW", [(35.56, 86.36), (208.28, 121.92)])
    join("I2C_SDA", [(88.9, 40.64), (152.4, 50.8)])
    join("I2C_SCL", [(88.9, 50.8), (152.4, 60.96)])
    # External line/source input into the tone stage.
    join("COMMON_L", [(152.4, 30.48)])
    join("COMMON_R", [(152.4, 40.64)])
    join("D_GND", [(88.9, 71.12), (152.4, 101.6)])
    join("3V3", [(88.9, 60.96), (152.4, 132.08)])
    # BP5293 +5V is now a spare output on Control — its only consumer (RelayBoard
    # coil driver) was removed in §2.9. Single-point join keeps the stub from
    # reading as an unconnected pin in ERC.
    join("AMP_SEL_L", [(215.9, 40.64), (144.78, 40.64)])
    join("AMP_SEL_R", [(215.9, 50.8), (144.78, 50.8)])
    join("TONE_L", [(208.28, 30.48), (88.9, 81.28)])
    join("TONE_R", [(208.28, 40.64), (88.9, 91.44)])
    join("PHONE_L", [(266.7, 40.64)])
    join("PHONE_R", [(266.7, 50.8)])
    join("LINE_L", [(266.7, 60.96)])
    join("LINE_R", [(266.7, 71.12)])

    from generate_kicad_scaffold import UUID_POWER_INST  # noqa: E402

    sheets = (
        sheet_block(UUID_POWER_INST, "PowerModule", "PowerModule.kicad_sch", 35.56, 30.48, 30.48, 60.96, power_pins, "2")
        + sheet_block(UUID_BANK_INST, "AmpBank", "AmpBank.kicad_sch", 88.9, 25.4, 55.88, 111.76, amp_bank_pins, "3")
        + sheet_block(UUID_CONTROL_INST, "ControlPanel", "ControlPanel.kicad_sch", 152.4, 25.4, 55.88, 111.76, control_pins, "4")
        + sheet_block(UUID_OUTPUT_INST, "OutputStage", "OutputStage.kicad_sch", 215.9, 30.48, 50.8, 50.8, output_pins, "5")
    )
    body = f"""\t(lib_symbols)
{text_note(25.4, 15.24, [
    "AudioV2Case — label-wired parent",
    "Sheet pins ≥10.16 mm apart; bridges via local labels on pin tips only.",
    "AmpBank = 10ch socketed op amp bank, one channel selected at a time (§2.9).",
])}
{sheets}
{"".join(nets)}
"""
    return sch_open(PARENT, body)


# ---------------------------------------------------------------- AmpBank
# AmpBank = 10ch 分のアンプと切替を載せた1枚の基板（AGENT_HANDOFF §2.9）。
# AmpChannel サブシートを 10 回インスタンス化する構成なので、生成するのは
# 1ch 分（22点）と Bank 側の共通部（16点）だけで済む。

AMP_CHANNELS = 10

CHANNEL_LIBS = [
    "Device:C",
    "Device:C_Polarized",
    "Device:R",
    "Amplifier_Operational:NE5532",
    "AudioV2:TMUX7612",
]

UUID_BANK_FILE = "a1000010-0010-4010-8010-000000000010"
UUID_BANK_INST = "a1000011-0011-4011-8011-000000000011"
UUID_CHAN_FILE = "a1000012-0012-4012-8012-000000000012"
PATH_BANK = f"/{PARENT}/{UUID_BANK_INST}"

# AmpChannel の 10 インスタンス UUID（親から見た path を固定するため決め打ち）
UUID_CHAN_INST = [f"a1000{20+i:03d}-00{20+i:02d}-40{20+i:02d}-80{20+i:02d}-0000000000{20+i:02d}"
                  for i in range(AMP_CHANNELS)]


def tmux_pin(sx: float, sy: float, num: int) -> tuple[float, float]:
    """AudioV2:TMUX7612 のピン先端。lib の (at) を Y 反転して返す。"""
    left = {  # 左辺: SEL と S
        1: (-12.7, 10.16), 3: (-12.7, 7.62),
        16: (-12.7, 2.54), 14: (-12.7, 0.0),
        9: (-12.7, -5.08), 11: (-12.7, -7.62),
        8: (-12.7, -12.7), 6: (-12.7, -15.24),
    }
    right = {2: (12.7, 8.89), 15: (12.7, 1.27), 10: (12.7, -6.35), 7: (12.7, -13.97)}
    power = {13: (-2.54, 17.78), 4: (-2.54, -17.78), 5: (2.54, -17.78), 12: (2.54, 17.78)}
    for tbl in (left, right, power):
        if num in tbl:
            return tip(sx, sy, tbl[num][0], tbl[num][1])
    raise ValueError(num)


def ne5532_pin(sx: float, sy: float, role: str, unit: int) -> tuple[float, float]:
    """Amplifier_Operational:NE5532（LM2904 継承）のピン先端。

    実ピン番号は unit1 = 1/2/3、unit2 = 7/6/5、unit3 = 8(V+)/4(V-)。
    番号ではなく役割（out/inv/nin/vp/vn）で引く。
    """
    if unit in (1, 2):
        return {
            "out": tip(sx, sy, 7.62, 0.0),
            "inv": tip(sx, sy, -7.62, -2.54),
            "nin": tip(sx, sy, -7.62, 2.54),
        }[role]
    return {"vp": tip(sx, sy, -2.54, 7.62), "vn": tip(sx, sy, -2.54, -7.62)}[role]


def amp_channel_wired() -> str:
    """AmpChannel: 1ch 分。AmpBank から 10 回インスタンス化される。

    構成（AGENT_HANDOFF §2.9、ngspice 検証済み）:
      TONE_x ─[SW]─┬─ 220k ─ A_GND
                    └─ 100nF ∥ 10uF ─┬─ 1k ─ A_GND
                                       └─ AMP + 入力（帰還 20k/20k = GAIN 2）
                    AMP 出力 ─ 47R ─ 2.2uF ─┬─ 220k ─ A_GND
                                              └─[SW]─ AMP_SEL_x

    220k は入力側・出力側とも「SW の側」に置く。カップリング C と SW ピンの
    間は非選択中に浮くので、オフ漏れ電流（TMUX7612 max 0.15 nA）で充電され、
    再接続時に段差になる。出力側は 2026-09-02 に追加（それまで抜けていた）。

    参照は ch1=7xx, ch2=8xx ... と 100 番刻みで instance_refs に与える。
    与えないと KiCad が「同名 AMP の unit1/2/3 が別ネット」と誤検出する。
    末尾番号は既存 AmpModule の採番（220k=R701/R706 など L/R 対）を踏襲。
    """
    parts: list[str] = []
    nets: list[str] = []
    r_fp = "Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder"
    c_fp = "Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder"
    film_fp = "Capacitor_THT:C_Rect_L7.2mm_W2.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2"
    elec_fp = "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm"

    def refs(prefix: str, num: int) -> list[tuple[str, str]]:
        return [(f"{PATH_BANK}/{u}", f"{prefix}{700 + i * 100 + num}")
                for i, u in enumerate(UUID_CHAN_INST)]

    def two_pin(lib_id, prefix, num, val, x, y, net1, net2, fp, desc, rot=0):
        ref = f"{prefix}{700 + num}"
        parts.append(symbol_inst_v10(lib_id, ref, val, x, y, rot, PATH_BANK,
                                     footprint=fp, description=desc,
                                     instance_refs=refs(prefix, num)))
        p1, p2 = (cap_pins(x, y, rot) if lib_id.startswith("Device:C") else r_pins(x, y, rot))
        nets.append(net_at(net1, p1, "u" if rot == 0 else "r"))
        nets.append(net_at(net2, p2, "d" if rot == 0 else "l"))

    #  ch   R: 220k  1k  47R  Rg   Rf  出力220k  /  C: film  elec  out
    plan = {"L": dict(pd=1, bias=2, iso=3, rg=4, rf=5, opd=11,
                      cf=1, ce=2, co=3, y=0.0),
            "R": dict(pd=6, bias=7, iso=8, rg=9, rf=10, opd=12,
                      cf=4, ce=5, co=6, y=63.5)}
    for ch, q in plan.items():
        y0 = q["y"]
        sw_in, ac, inv = f"IN_{ch}", f"AC_{ch}", f"INV_{ch}"
        op, pre = f"OPOUT_{ch}", f"PRE_{ch}"
        two_pin("Device:R", "R", q["pd"], "220k", 50.8, y0 + 45.72,
                sw_in, "A_GND", r_fp, f"{ch} input pulldown (after switch)")
        two_pin("Device:C", "C", q["cf"], "100nF film", 63.5, y0 + 38.1,
                sw_in, ac, film_fp, f"{ch} input film coupling", rot=90)
        two_pin("Device:C_Polarized", "C", q["ce"], "10uF", 63.5, y0 + 45.72,
                sw_in, ac, elec_fp, f"{ch} input electrolytic coupling", rot=90)
        two_pin("Device:R", "R", q["bias"], "1k", 76.2, y0 + 45.72,
                ac, "A_GND", r_fp, f"{ch} non-inverting bias")
        two_pin("Device:R", "R", q["rg"], "20k", 99.06, y0 + 45.72,
                inv, "A_GND", r_fp, f"{ch} gain resistor Rg; GAIN=1+Rf/Rg")
        two_pin("Device:R", "R", q["rf"], "20k", 111.76, y0 + 33.02,
                op, inv, r_fp, f"{ch} feedback Rf; default 20k = GAIN 2", rot=90)
        two_pin("Device:R", "R", q["iso"], "47R", 127.0, y0 + 38.1,
                op, pre, r_fp, f"{ch} output isolation", rot=90)
        two_pin("Device:C", "C", q["co"], "2.2uF film", 139.7, y0 + 38.1,
                pre, f"OUT_{ch}", film_fp, f"{ch} output coupling (before switch)", rot=90)
        two_pin("Device:R", "R", q["opd"], "220k", 152.4, y0 + 45.72,
                f"OUT_{ch}", "A_GND", r_fp, f"{ch} output pulldown (before switch)")

    # --- OpAmp（DIP-8 ソケット。unit1=L, unit2=R, unit3=電源）---
    ox, oy = 88.9, 38.1
    for unit, ch, dy in ((1, "L", 0.0), (2, "R", 63.5)):
        parts.append(symbol_inst_v10(
            "Amplifier_Operational:NE5532", "AMP701", "NE5532 / DIP-8 compatible",
            ox, oy + dy, 0, PATH_BANK, unit=unit,
            footprint="Package_DIP:DIP-8_W7.62mm_Socket",
            description="Socketed dual op amp under test",
            instance_refs=refs("AMP", 1)))
        nets.append(net_at(f"AC_{ch}", ne5532_pin(ox, oy + dy, "nin", unit), "l"))
        nets.append(net_at(f"INV_{ch}", ne5532_pin(ox, oy + dy, "inv", unit), "l"))
        nets.append(net_at(f"OPOUT_{ch}", ne5532_pin(ox, oy + dy, "out", unit), "r"))
    parts.append(symbol_inst_v10(
        "Amplifier_Operational:NE5532", "AMP701", "NE5532 / DIP-8 compatible",
        ox, 127.0, 0, PATH_BANK, unit=3,
        footprint="Package_DIP:DIP-8_W7.62mm_Socket",
        description="Socketed dual op amp under test",
        instance_refs=refs("AMP", 1)))

    # --- 切替 SW（TMUX7612 1個で 1ch 分 = L入/R入/L出/R出）---
    sx, sy = 33.02, 63.5
    parts.append(symbol_inst_v10(
        "AudioV2:TMUX7612", "U701", "TMUX7612", sx, sy, 0, PATH_BANK,
        footprint="Package_SO:TSSOP-16_4.4x5mm_P0.65mm",
        datasheet="datasheets/TI_TMUX7612.pdf",
        description="4ch SPST; ch1/2=input L/R, ch3/4=output L/R",
        instance_refs=refs("U", 1)))
    # TONE/AMP_SEL/A_GND/SEL は階層ラベルを直接ピンに置くので、ここでは付けない
    for num, net, d in ((2, "IN_L", "r"), (15, "IN_R", "r"),
                        (11, "OUT_L", "l"), (6, "OUT_R", "l"),
                        (13, "+15V", "u"), (4, "-15V", "d")):
        nets.append(net_at(net, tmux_pin(sx, sy, num), d))
    for num in (16, 9, 8):      # SEL1 は階層ラベル、残り3本をローカルで束ねる
        nets.append(net_at("SEL", tmux_pin(sx, sy, num), "l"))
    parts.append(no_connect_at(tmux_pin(sx, sy, 12)))

    # --- デカップリング（各 IC 直近に 100nF。バルクは Bank 入口）---
    for num, x, y, n1, n2, note in (
        (7, 165.1, 20.32, "+15V", "A_GND", "op amp V+ local decoupling"),
        (8, 177.8, 20.32, "A_GND", "-15V", "op amp V- local decoupling"),
        (9, 165.1, 33.02, "+15V", "A_GND", "switch VDD local decoupling"),
        (10, 177.8, 33.02, "A_GND", "-15V", "switch VSS local decoupling"),
    ):
        two_pin("Device:C", "C", num, "100nF", x, y, n1, n2, c_fp, note)

    # --- 階層ラベルは実ピン先端に置く（浮かせると label_dangling、§2.9）---
    hiers = "".join(
        hier_label(name, shape, xy[0], xy[1], ang)
        for name, shape, xy, ang in (
            ("TONE_L", "input", tmux_pin(sx, sy, 3), 180),
            ("TONE_R", "input", tmux_pin(sx, sy, 14), 180),
            ("SEL", "input", tmux_pin(sx, sy, 1), 180),
            ("AMP_SEL_L", "output", tmux_pin(sx, sy, 10), 0),
            ("AMP_SEL_R", "output", tmux_pin(sx, sy, 7), 0),
            ("+15V", "input", ne5532_pin(ox, 127.0, "vp", 3), 90),
            ("-15V", "input", ne5532_pin(ox, 127.0, "vn", 3), 270),
            ("A_GND", "bidirectional", tmux_pin(sx, sy, 5), 270),
        )
    )

    body = f"""{embed_lib_symbols(CHANNEL_LIBS)}
{text_note(25.4, 12.7, [
    "AmpBank / AmpChannel - one channel, instantiated x10.",
    "SW selects this channel's input AND output. Supply is always on.",
    "GAIN = 1 + Rf/Rg  (default 20k/20k = 2)",
])}
{hiers}
{"".join(parts)}
{"".join(nets)}
"""
    return sch_open(UUID_CHAN_FILE, body, paper="A3")


BANK_LIBS = [
    "Device:C",
    "Device:C_Polarized",
    "Interface_Expansion:MCP23017x-x-SP",
    "Connector:Screw_Terminal_01x02",
    "Connector:Screw_Terminal_01x03",
    "Connector:Conn_01x04_Pin",
]


def mcp_pin(sx: float, sy: float, num: int) -> tuple[float, float]:
    """Interface_Expansion:MCP23017x-x-SP のピン先端。"""
    tbl = {
        9: (0.0, 25.4), 10: (0.0, -25.4),
        12: (-12.7, 20.32), 13: (-12.7, 17.78),
        15: (-12.7, -15.24), 16: (-12.7, -17.78), 17: (-12.7, -20.32),
        18: (-12.7, -2.54), 19: (-12.7, 2.54), 20: (-12.7, 5.08),
        11: (-10.16, 15.24), 14: (-10.16, 12.7),
    }
    if num in tbl:
        return tip(sx, sy, tbl[num][0], tbl[num][1])
    if 1 <= num <= 8:      # GPB0-7
        return tip(sx, sy, 12.7, -2.54 - (num - 1) * 2.54)
    if 21 <= num <= 28:    # GPA0-7
        return tip(sx, sy, 12.7, 20.32 - (num - 21) * 2.54)
    raise ValueError(num)


def amp_bank_wired() -> str:
    """AmpBank: 共通部 + AmpChannel を 10 インスタンス。

    ch 毎に違うのは制御線 SEL_CHn だけ。TONE / AMP_SEL / 電源は全 ch 共通。
    """
    parts: list[str] = []
    nets: list[str] = []
    sheets: list[str] = []
    c_fp = "Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder"
    bulk_fp = "Capacitor_SMD:CP_Elec_10x12.6"
    conn2_fp = ("TerminalBlock_Phoenix:"
                "TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal")
    conn3_fp = ("TerminalBlock_Phoenix:"
                "TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal")

    def two_pin(lib_id, ref, val, x, y, net1, net2, fp, desc, rot=0):
        parts.append(symbol_inst_v10(lib_id, ref, val, x, y, rot, PATH_BANK,
                                     footprint=fp, description=desc))
        p1, p2 = cap_pins(x, y, rot)
        nets.append(net_at(net1, p1, "u" if rot == 0 else "r"))
        nets.append(net_at(net2, p2, "d" if rot == 0 else "l"))

    # --- コネクタ ---
    parts.append(symbol_inst_v10("Connector:Screw_Terminal_01x03", "J_PWR",
                                 "+15V / A_GND / -15V", 279.4, 38.1, 0, PATH_BANK,
                                 footprint=conn3_fp, description="Supply in from PowerModule"))
    p1, p2, p3 = screw_pins(279.4, 38.1, 3)
    for net, pt_ in (("+15V", p1), ("A_GND", p2), ("-15V", p3)):
        nets.append(net_at(net, pt_, "r"))

    parts.append(symbol_inst_v10("Connector:Screw_Terminal_01x02", "J_TONE",
                                 "TONE IN L/R", 279.4, 76.2, 0, PATH_BANK,
                                 footprint=conn2_fp, description="Tone stage output in"))
    t1, t2 = screw_pins(279.4, 76.2, 2)
    nets.append(net_at("TONE_L", t1, "r"))
    nets.append(net_at("TONE_R", t2, "r"))

    parts.append(symbol_inst_v10("Connector:Screw_Terminal_01x02", "J_OUT",
                                 "AMP_SEL OUT L/R", 279.4, 101.6, 0, PATH_BANK,
                                 footprint=conn2_fp, description="Selected amp out to OutputStage"))
    o1, o2 = screw_pins(279.4, 101.6, 2)
    nets.append(net_at("AMP_SEL_L", o1, "r"))
    nets.append(net_at("AMP_SEL_R", o2, "r"))

    parts.append(symbol_inst_v10("Connector:Conn_01x04_Pin", "J_CTRL",
                                 "I2C SDA/SCL/3V3/D_GND", 279.4, 127.0, 0, PATH_BANK,
                                 footprint="Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
                                 description="I2C from ControlPanel"))
    for i, net in enumerate(("I2C_SDA", "I2C_SCL", "3V3", "D_GND")):
        nets.append(net_at(net, conn04_pins(279.4, 127.0)[i], "l"))

    # --- 入口バルクと MCP デカップリング（ch 毎のバルクは持たない。§2.9）---
    two_pin("Device:C_Polarized", "C_BULK_P", "100uF 35V", 304.8, 38.1,
            "+15V", "A_GND", bulk_fp, "rail bulk at board entry")
    two_pin("Device:C_Polarized", "C_BULK_N", "100uF 35V", 317.5, 38.1,
            "A_GND", "-15V", bulk_fp, "rail bulk at board entry")
    two_pin("Device:C", "C_IO", "100nF", 304.8, 127.0,
            "3V3", "D_GND", c_fp, "MCP23017 decoupling")

    # --- MCP23017（切替IC の制御。GPIO 10 本）---
    mx, my = 330.2, 177.8
    parts.append(symbol_inst_v10("Interface_Expansion:MCP23017x-x-SP", "U_IO", "MCP23017",
                                 mx, my, 0, PATH_BANK,
                                 footprint="Package_DIP:DIP-28_W7.62mm",
                                 datasheet="datasheets/Microchip_MCP23017.pdf",
                                 description="I2C GPIO expander; 10 SEL lines"))
    nets.append(net_at("3V3", mcp_pin(mx, my, 9), "u"))
    nets.append(net_at("D_GND", mcp_pin(mx, my, 10), "d"))
    nets.append(net_at("I2C_SCL", mcp_pin(mx, my, 12), "l"))
    nets.append(net_at("I2C_SDA", mcp_pin(mx, my, 13), "l"))
    nets.append(net_at("3V3", mcp_pin(mx, my, 18), "l"))          # ~RESET は 3V3 直結
    for num in (15, 16, 17):                                       # A0-A2 = GND（基板1枚なので固定）
        nets.append(net_at("D_GND", mcp_pin(mx, my, num), "l"))
    for num in (19, 20, 11, 14):                                   # INTA/INTB/NC
        parts.append(no_connect_at(mcp_pin(mx, my, num)))
    # GPA0-7 → SEL_CH1-8、GPB0-1 → SEL_CH9-10
    for i in range(AMP_CHANNELS):
        num = 21 + i if i < 8 else 1 + (i - 8)
        nets.append(net_at(f"SEL_CH{i + 1}", mcp_pin(mx, my, num), "r"))
    for num in (3, 4, 5, 6, 7, 8):                                 # GPB2-7 未使用
        parts.append(no_connect_at(mcp_pin(mx, my, num)))

    # --- AmpChannel を 10 インスタンス ---
    cols, w, h = 2, 76.2, 30.48
    for i in range(AMP_CHANNELS):
        col, row = i % cols, i // cols
        x = 38.1 + col * 114.3
        y = 25.4 + row * (h + 5.08)
        pins = [
            ("TONE_L", "input", x, y + 5.08, 180),
            ("TONE_R", "input", x, y + 10.16, 180),
            ("SEL", "input", x, y + 15.24, 180),
            ("+15V", "input", x, y + 20.32, 180),
            ("-15V", "input", x, y + 25.4, 180),
            ("A_GND", "bidirectional", x, y + 27.94, 180),
            ("AMP_SEL_L", "output", x + w, y + 5.08, 0),
            ("AMP_SEL_R", "output", x + w, y + 10.16, 0),
        ]
        sheets.append(sheet_block(UUID_CHAN_INST[i], f"AmpCh{i + 1}", "AmpChannel.kicad_sch",
                                  x, y, w, h, pins, str(i + 2)))
        # シートピンにネット名を与える（SEL だけ ch 毎に違う）
        for pname, _t, px, py, _a in pins:
            net = f"SEL_CH{i + 1}" if pname == "SEL" else pname
            nets.append(label(net, px, py, 0, "right" if px == x else "left"))

    # --- 親（AudioV2Case）へのインタフェース。実ピン先端に置く ---
    hiers = "".join(
        hier_label(name, shape, xy[0], xy[1], ang)
        for name, shape, xy, ang in (
            ("TONE_L", "input", t1, 180),
            ("TONE_R", "input", t2, 180),
            ("AMP_SEL_L", "output", o1, 0),
            ("AMP_SEL_R", "output", o2, 0),
            ("+15V", "input", p1, 180),
            ("A_GND", "bidirectional", p2, 180),
            ("-15V", "input", p3, 180),
            ("I2C_SDA", "bidirectional", conn04_pins(279.4, 127.0)[0], 180),
            ("I2C_SCL", "input", conn04_pins(279.4, 127.0)[1], 180),
            ("3V3", "input", conn04_pins(279.4, 127.0)[2], 180),
            ("D_GND", "bidirectional", conn04_pins(279.4, 127.0)[3], 180),
        )
    )

    body = f"""{embed_lib_symbols(BANK_LIBS)}
{text_note(25.4, 12.7, [
    "AmpBank — 10 socketed op amp channels, one selected at a time.",
    "Input AND output are switched; supply is always on (see AGENT_HANDOFF 2.9).",
    "GAIN = 1 + Rf/Rg : 0R=1.0  10k=1.5  20k=2.0(default)  39k=3.0  62k=4.1  82k=5.1  180k=10.0",
])}
{hiers}
{"".join(sheets)}
{"".join(parts)}
{"".join(nets)}
"""
    return sch_open(UUID_BANK_FILE, body, paper="A2")

def main() -> None:
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    flags = sys.argv[2:]

    # 手編集所有シート（AudioV2/AGENT_HANDOFF.md §2.8）。KiCad 側が正なので
    # 機械的に上書きしない。--force-<name> は「シートを丸ごと作り直す」ときだけの
    # 脱出ハッチで、通常運用では使わない。
    # power / output は 2026-09-03 に MotherBoard へ統合され、シートごと legacy/ へ移した。
    # 親からも参照されていないので書き込み対象から外す。母板を作るのは
    # build_motherboard.py。power_module_wired() / output_stage_wired() は
    # 旧構成のロジックの記録として残してあるが、どこにも書き出されない。
    HAND_EDITED = {
        "channel": (
            "AmpChannel.kicad_sch",
            amp_channel_wired,
            "graduated to hand-edited on 2026-09-02 (user reworked AmpCh2 in KiCad); "
            "generator kept as logic documentation only",
        ),
        "bank": (
            "AmpBank.kicad_sch",
            amp_bank_wired,
            "graduated to hand-edited on 2026-09-02 alongside AmpChannel (bulk-cap wiring "
            "fixed in KiCad); generator kept as logic documentation only",
        ),
        "control": (
            "ControlPanel.kicad_sch",
            control_panel_wired,
            "graduated to hand-edited on 2026-09-03: the sheet now exports -15V and +5V "
            "to the parent, and the local +5V->Schottky->VSYS feed was removed in KiCad; "
            "generator kept as logic documentation only",
        ),
        "parent": (
            "AudioV2Case.kicad_sch",
            parent_wired,
            "graduated to hand-edited on 2026-09-03: the MeasureControl sheet was placed "
            "in KiCad and the generator does not emit it; regenerating would delete it",
        ),
    }
    # 生成コード所有シート（回せばそのまま正）
    GENERATED: dict[str, tuple[str, object]] = {}

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
                f"SKIPPED {fn}: hand-edited sheet (AGENT_HANDOFF.md sec 2.8). {why}. "
                f"Make logic changes in KiCad, or pass --force-{name} to overwrite anyway.",
                file=sys.stderr,
            )

    print(f"Wired: {target}" + (f" (skipped: {', '.join(skipped)})" if skipped else ""))


if __name__ == "__main__":
    main()
