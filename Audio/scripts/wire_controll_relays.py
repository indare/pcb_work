#!/usr/bin/env python3
"""Wire Controll relay amp-side contacts (pin4/pin5) to J1-J10 harness terminals (step 4)."""

import math
import re
import uuid as uuid_mod
from pathlib import Path

SCH = Path(__file__).resolve().parent.parent / "Controll.kicad_sch"

# Schematic pin local coords from AZ850P2-x lib embedded in Controll.kicad_sch
PIN_LOCAL = {
    "1": (-12.7, 7.62),
    "2": (-2.54, 7.62),
    "3": (0, -7.62),
    "4": (2.54, 7.62),
    "5": (-7.62, 7.62),
    "6": (-7.62, -7.62),
    "7": (12.7, 7.62),
    "8": (10.16, -7.62),
    "9": (7.62, 7.62),
    "10": (-12.7, -7.62),
}

# Relay ref -> (amp_num, kind)  kind: audio | pwr
RELAY_MAP = {
    "K2": (1, "audio"),
    "K1": (1, "pwr"),
    "K4": (2, "audio"),
    "K3": (2, "pwr"),
    "K8": (3, "audio"),
    "K5": (3, "pwr"),
    "K9": (4, "audio"),
    "K6": (4, "pwr"),
    "K10": (5, "audio"),
    "K7": (5, "pwr"),
}

# J ref -> symbol anchor (at x y)
J_ANCHORS = {
    "J1": (327.66, 135.0),
    "J2": (327.66, 145.16),
    "J3": (327.66, 160.4),
    "J4": (327.66, 170.56),
    "J5": (327.66, 185.8),
    "J6": (327.66, 195.96),
    "J7": (327.66, 211.2),
    "J8": (327.66, 221.36),
    "J9": (327.66, 236.6),
    "J10": (327.66, 246.76),
}

TRUNK_X_BASE = 305.0
TRUNK_X_STEP = 6.0  # separate vertical trunks per Amp to avoid shorts


def trunk_x_for_amp(amp: int) -> float:
    return TRUNK_X_BASE - (amp - 1) * TRUNK_X_STEP


def uid():
    return str(uuid_mod.uuid4())


def rk(x, y):
    return round(x, 2), round(y, 2)


def pin_world(sx, sy, srot, px, py):
    r = math.radians(srot)
    return rk(px * math.cos(r) - py * math.sin(r) + sx, px * math.sin(r) + py * math.cos(r) + sy)


def fmt_xy(x, y):
    xs = f"{x:.2f}".rstrip("0").rstrip(".")
    ys = f"{y:.2f}".rstrip("0").rstrip(".")
    return xs, ys


def wire_block(x1, y1, x2, y2):
    ax, ay = fmt_xy(x1, y1)
    bx, by = fmt_xy(x2, y2)
    return f"""\t(wire
\t\t(pts
\t\t\t(xy {ax} {ay}) (xy {bx} {by})
\t\t)
\t\t(stroke
\t\t\t(width 0)
\t\t\t(type default)
\t\t)
\t\t(uuid "{uid()}")
\t)"""


def route_wire(x1, y1, x2, y2, trunk_x):
    """Horizontal-vertical-horizontal via trunk_x when useful."""
    if abs(y1 - y2) < 0.01:
        return [wire_block(x1, y1, x2, y2)]
    if abs(x1 - x2) < 0.01:
        return [wire_block(x1, y1, x2, y2)]
    out = []
    if abs(x1 - trunk_x) > 0.01:
        out.append(wire_block(x1, y1, trunk_x, y1))
    if abs(y1 - y2) > 0.01:
        out.append(wire_block(trunk_x, y1, trunk_x, y2))
    if abs(x2 - trunk_x) > 0.01:
        out.append(wire_block(trunk_x, y2, x2, y2))
    return out


def j_pins(j_ref):
    x, y = J_ANCHORS[j_ref]
    # Conn_01x02_Pin body_style 1: pins at (+5.08, 0) and (+5.08, +2.54)
    return rk(x + 5.08, y), rk(x + 5.08, y + 2.54)


def parse_relays(text):
    relays = {}
    for m in re.finditer(
        r'\(symbol\n\t\t\(lib_id "Relay:AZ850P2-x"\)\n\t\t\(at\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\)'
        r'[\s\S]*?property "Reference" "(K\d+)"',
        text,
    ):
        relays[m.group(4)] = (float(m.group(1)), float(m.group(2)), float(m.group(3)))
    return relays


def remove_no_connect_at(text, x, y):
    ax, ay = fmt_xy(x, y)
    pat = rf'\t\(no_connect\n\t\t\(at {ax} {ay}\)\n\t\t\(uuid "[^"]+"\)\n\t\)\n'
    return re.sub(pat, "", text, count=1)


def fix_label_at(text, label_name, new_x, new_y):
    nx, ny = fmt_xy(new_x, new_y)
    marker = f'(label "{label_name}"'
    pos = text.find(marker)
    if pos < 0:
        raise RuntimeError(f"label not found: {label_name}")
    at_pos = text.find("(at ", pos)
    if at_pos < 0:
        raise RuntimeError(f"at not found for label: {label_name}")
    end = text.find(")", at_pos)
    text = text[:at_pos] + f"(at {nx} {ny} 0)" + text[end + 1 :]
    return text


def strip_step4_wires(text):
    """Remove wires routed through step-4 trunk columns (idempotent re-run)."""
    trunks = {fmt_xy(trunk_x_for_amp(a), 0)[0] for a in range(1, 6)}
    trunks.update({"305", "300", "295", "290", "285"})  # legacy single-trunk run

    def is_step4_wire(block):
        pts = re.findall(r"\(xy ([\d.-]+) ([\d.-]+)\)", block)
        xs = {fmt_xy(float(x), 0)[0] for x, _ in pts}
        return bool(xs & trunks) and any(float(x) >= 280 for x, _ in pts)

    pattern = r"\t\(wire\n\t\t\(pts\n\t\t\t\(xy [\d.-]+ [\d.-]+\) \(xy [\d.-]+ [\d.-]+\)\n\t\t\)\n\t\t\(stroke\n\t\t\t\(width 0\)\n\t\t\t\(type default\)\n\t\t\)\n\t\t\(uuid \"[^\"]+\"\)\n\t\)\n"

    removed = 0

    def repl(m):
        nonlocal removed
        if is_step4_wire(m.group(0)):
            removed += 1
            return ""
        return m.group(0)

    text, _ = re.subn(pattern, repl, text)
    print(f"Removed {removed} prior step-4 wire segments")
    return text


def bus_point_for_relay(kind, rx, ry):
    """Return (bx, by) on existing pre-relay bus for pin10 hookup."""
    if kind == "audio":
        return rx + 7.62, 27.94
    return rx + 7.62, 24.13


def main():
    text = SCH.read_text()
    text = strip_step4_wires(text)
    relays = parse_relays(text)
    missing = set(RELAY_MAP) - set(relays)
    if missing:
        raise RuntimeError(f"missing relays in schematic: {sorted(missing)}")

    new_wires = []

    for ref, (amp, kind) in sorted(RELAY_MAP.items(), key=lambda x: (x[1][0], x[1][1])):
        sx, sy, rot = relays[ref]
        p4 = pin_world(sx, sy, rot, *PIN_LOCAL["4"])
        p5 = pin_world(sx, sy, rot, *PIN_LOCAL["5"])
        p10 = pin_world(sx, sy, rot, *PIN_LOCAL["10"])

        if kind == "audio":
            j_lr = f"J{amp * 2 - 1}"
            pin_a, pin_b = j_pins(j_lr)
            # fp pad2 -> pin4 (L), fp pad9 -> pin5 (R)
            sig_a = f"/AMP{amp}_L_IN"
            sig_b = f"/AMP{amp}_R_IN"
            src_a, src_b = p4, p5
            bus_x, bus_y = bus_point_for_relay("audio", sx, sy)
        else:
            j_pwr = f"J{amp * 2}"
            pin_a, pin_b = j_pins(j_pwr)
            sig_a = f"/AMP{amp}_V+_IN"
            sig_b = f"/AMP{amp}_V-_IN"
            src_a, src_b = p5, p4  # pin5 nearer V+ bus, pin4 nearer V-
            bus_x, bus_y = bus_point_for_relay("pwr", sx, sy)

        for pt in (p4, p5, p10):
            text = remove_no_connect_at(text, *pt)

        trunk = trunk_x_for_amp(amp)

        # pin10 -> common input bus (L_IN or AMP_V+_IN)
        new_wires.extend(route_wire(p10[0], p10[1], p10[0], bus_y, trunk))
        new_wires.append(wire_block(p10[0], bus_y, bus_x, bus_y))

        # relay amp outputs -> J terminals (labels sit on connector pins)
        text = fix_label_at(text, sig_a, pin_a[0], pin_a[1])
        text = fix_label_at(text, sig_b, pin_b[0], pin_b[1])

        for src, dst in ((src_a, pin_a), (src_b, pin_b)):
            new_wires.extend(route_wire(src[0], src[1], dst[0], dst[1], trunk))

        print(f"{ref} AMP{amp} {kind}: pin4{p4} pin5{p5} -> {j_lr if kind=='audio' else f'J{amp*2}'}")

    insert_at = text.find("\t(wire\n")
    if insert_at < 0:
        raise RuntimeError("could not find wire section")
    text = text[:insert_at] + "\n".join(new_wires) + "\n" + text[insert_at:]

    SCH.write_text(text)
    print(f"Added {len(new_wires)} wire segments to {SCH}")


if __name__ == "__main__":
    main()
