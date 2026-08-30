#!/usr/bin/env python3
"""DEST ON-OFF-ON sense ladder simulation for Pico ADC (GP26).

Topology (MUTE = center open):
  3V3 -- Rh -- ADC -- Rl -- GND
  ADC -- Rs -- SW_LINE  -- 3V3
  ADC -- Rs -- SW_PHONE -- GND

Usage:
  python3 AudioV2/scripts/dest_ladder_sim.py
"""
from __future__ import annotations

VCC = 3.3
ADC_BITS = 12
ADC_FS = (1 << ADC_BITS) - 1
ADC_LSB = VCC / ADC_FS


def adc_code(v: float) -> int:
    v = max(0.0, min(VCC, v))
    return int(round(v / ADC_LSB))


def parallel(a: float, b: float) -> float:
    return 1.0 / (1.0 / a + 1.0 / b)


def voltages(rh: float, rl: float, rs: float) -> dict[str, float]:
    v_mute = VCC * rl / (rh + rl)
    rhi_eq = parallel(rh, rs)
    v_line = VCC * rl / (rhi_eq + rl)
    rlo_eq = parallel(rl, rs)
    v_phone = VCC * rlo_eq / (rh + rlo_eq)
    return {"LINE": v_line, "MUTE": v_mute, "PHONE": v_phone}


def with_tol(rh: float, rl: float, rs: float, tol: float) -> dict[str, tuple[float, float]]:
    corners = []
    for s_h in (1 - tol, 1 + tol):
        for s_l in (1 - tol, 1 + tol):
            for s_s in (1 - tol, 1 + tol):
                corners.append(voltages(rh * s_h, rl * s_l, rs * s_s))
    out: dict[str, tuple[float, float]] = {}
    for pos in ("LINE", "MUTE", "PHONE"):
        vals = [c[pos] for c in corners]
        out[pos] = (min(vals), max(vals))
    return out


def main() -> None:
    candidates = [
        ("equal 10k / Rs=1k", 10_000, 10_000, 1_000),
        ("equal 10k / Rs=2.2k", 10_000, 10_000, 2_200),
        ("equal 4.7k / Rs=1k", 4_700, 4_700, 1_000),
        ("equal 22k / Rs=2.2k", 22_000, 22_000, 2_200),
        ("Rh=10k Rl=10k Rs=470", 10_000, 10_000, 470),
        ("Rh=4.7k Rl=4.7k Rs=470", 4_700, 4_700, 470),
    ]

    print("DEST sense ladder simulation (ON-OFF-ON)")
    print(f"VCC={VCC} V, Pico ADC {ADC_BITS}-bit, LSB={ADC_LSB * 1000:.3f} mV")
    print()
    print("Topology:")
    print("  3V3 -- Rh -- ADC -- Rl -- GND")
    print("  ADC -- Rs -- SW to 3V3 (LINE) or GND (PHONE); MUTE = open")
    print()

    best: tuple | None = None
    for name, rh, rl, rs in candidates:
        v = voltages(rh, rl, rs)
        wc1 = with_tol(rh, rl, rs, 0.01)
        wc5 = with_tol(rh, rl, rs, 0.05)
        gap_lm5 = wc5["LINE"][0] - wc5["MUTE"][1]
        gap_mp5 = wc5["MUTE"][0] - wc5["PHONE"][1]
        i_mute = VCC / (rh + rl) * 1000
        i_line = VCC / (parallel(rh, rs) + rl) * 1000
        i_phone = VCC / (rh + parallel(rl, rs)) * 1000

        print(f"=== {name} ===")
        print(f"  Rh={rh}, Rl={rl}, Rs={rs}")
        for pos in ("LINE", "MUTE", "PHONE"):
            vv = v[pos]
            print(
                f"  {pos:5s}: {vv:.3f} V  code={adc_code(vv):4d}  "
                f"±1%: [{wc1[pos][0]:.3f},{wc1[pos][1]:.3f}]  "
                f"±5%: [{wc5[pos][0]:.3f},{wc5[pos][1]:.3f}]"
            )
        print(f"  gap @5%: LINE-MUTE {gap_lm5 * 1000:.0f} mV, MUTE-PHONE {gap_mp5 * 1000:.0f} mV")
        print(f"  I_MUTE={i_mute:.2f} mA  I_LINE≈{i_line:.2f} mA  I_PHONE≈{i_phone:.2f} mA")
        print()
        score = min(gap_lm5, gap_mp5)
        if best is None or score > best[0]:
            best = (score, name, rh, rl, rs, v, wc5, gap_lm5, gap_mp5)

    assert best is not None
    _score, name, rh, rl, rs, v, wc5, gap_lm5, gap_mp5 = best
    # Prefer practical E24: 10k/10k/1k (document both)
    rh, rl, rs = 10_000, 10_000, 1_000
    v = voltages(rh, rl, rs)
    wc5 = with_tol(rh, rl, rs, 0.05)
    hi_lo = (wc5["LINE"][0] + wc5["MUTE"][1]) / 2
    lo_hi = (wc5["MUTE"][0] + wc5["PHONE"][1]) / 2
    gap_lm5 = wc5["LINE"][0] - wc5["MUTE"][1]
    gap_mp5 = wc5["MUTE"][0] - wc5["PHONE"][1]

    print("### ADOPT (E24 / low current) ###")
    print(f"  Rh={rh}, Rl={rl}, Rs={rs}  (10k / 10k / 1k)")
    print(f"  Nominal: LINE={v['LINE']:.3f}V  MUTE={v['MUTE']:.3f}V  PHONE={v['PHONE']:.3f}V")
    print("  Firmware thresholds (midpoint between ±5% clusters):")
    print(f"    if adc_v > {hi_lo:.3f} V  (code > {adc_code(hi_lo)}) → LINE")
    print(f"    elif adc_v < {lo_hi:.3f} V (code < {adc_code(lo_hi)}) → PHONE")
    print("    else → MUTE")
    print(f"  Min separation @5%: {gap_lm5 * 1000:.0f} / {gap_mp5 * 1000:.0f} mV")


if __name__ == "__main__":
    main()
