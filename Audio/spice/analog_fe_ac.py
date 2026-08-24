#!/usr/bin/env python3
"""Analog FE constants check (same linear AC as ideal-opamp SPICE).

One channel, schematic values:
  U701 invert 4.7k/4.7k
  AC couple 10uF
  2nd invert 3.3k/1k with 1.8nF across Rf, + at VCOM
  differential = VIN+ - VIN-
"""
from __future__ import annotations

import json
import math
from pathlib import Path

R1 = 4.7e3
RF1 = 4.7e3
RIN = 3.3e3
RF = 1.0e3
CF = 1.8e-9
CAC = 10e-6
T = 300.0
K = 1.380649e-23
# OPA1656 (datasheet): 4.3 nV/rtHz @ 1 kHz, 6 fA/rtHz
EN = 4.3e-9
IN = 6e-15
# PCM1804: full-scale differential ±2.5 V => 5 Vpp = 1.7678 Vrms
VFS_RMS = 2.5 / math.sqrt(2)


def h_first(s: complex) -> complex:
    return -RF1 / R1


def h_inv_ac(s: complex) -> complex:
    """Inverting stage: series C then Rin, Rf || 1/(s Cf)."""
    zin = 1.0 / (s * CAC) + RIN
    zf = 1.0 / (1.0 / RF + s * CF)
    return -zf / zin


def h_diff(s: complex) -> complex:
    h1 = h_first(s)
    hb = h_inv_ac(s)  # VIN+ from input
    ha = h1 * h_inv_ac(s)  # VIN- from inverted first stage
    return hb - ha


def db(mag: float) -> float:
    return 20.0 * math.log10(max(mag, 1e-18))


def find_f(freqs, mags, target_db, falling: bool) -> float | None:
    t = 10 ** (target_db / 20.0)
    for a, b, ma, mb in zip(freqs, freqs[1:], mags, mags[1:]):
        if falling:
            if ma >= t >= mb:
                # log interpolate
                g = (t - ma) / (mb - ma) if mb != ma else 0
                return a * (b / a) ** g
        else:
            if ma <= t <= mb:
                g = (t - ma) / (mb - ma) if mb != ma else 0
                return a * (b / a) ** g
    return None


def noise_1khz() -> dict:
    """Midband output-referred differential noise density at 1 kHz.

    Path B (VIN+): 2nd stage only.
    Path A (VIN-): 1st + 2nd. Uncorrelated, then vdiff = vp - vm.
    """
    ng1 = 1.0 + RF1 / R1  # 2
    ng2 = 1.0 + RF / RIN  # 1.303
    g2 = RF / RIN  # 0.303 signal gain of 2nd
    # resistor thermal (nV/rtHz)
    def johnson(r):
        return math.sqrt(4 * K * T * r)

    # 1st stage output noise (approx, audio midband)
    n_u701_out = math.sqrt(
        (EN * ng1) ** 2
        + (johnson(R1) * ng1) ** 2
        + johnson(RF1) ** 2
        + (IN * R1 * ng1) ** 2
    )
    # 2nd stage own output noise (each half)
    n_2nd = math.sqrt(
        (EN * ng2) ** 2
        + (johnson(RIN) * ng2) ** 2
        + johnson(RF) ** 2
        + (IN * RIN * ng2) ** 2
    )
    n_vinp = n_2nd
    n_vinm = math.sqrt(n_2nd**2 + (n_u701_out * g2) ** 2)
    n_diff = math.sqrt(n_vinp**2 + n_vinm**2)
    # 20-20k white-ish integral (overestimate; 1/f ignored)
    bw = 20e3 - 20
    n_rms = n_diff * math.sqrt(bw)
    snr_fs = 20 * math.log10(VFS_RMS / n_rms) if n_rms else None
    return {
        "n_diff_nv": n_diff * 1e9,
        "n_rms_20_20k_uV": n_rms * 1e6,
        "snr_vs_pcm1804_fs_dB": snr_fs,
        "en_opa_nV": EN * 1e9,
        "johnson_4k7_nV": johnson(R1) * 1e9,
        "johnson_3k3_nV": johnson(RIN) * 1e9,
    }


def main() -> None:
    freqs = [0.1 * 10 ** (i / 10) for i in range(0, 71)]  # 0.1 Hz .. 1 MHz
    mags, dbs, phases = [], [], []
    for f in freqs:
        s = 1j * 2 * math.pi * f
        h = h_diff(s)
        mag = abs(h)
        mags.append(mag)
        dbs.append(db(mag))
        phases.append(math.degrees(math.atan2(h.imag, h.real)))

    f1k = 1e3
    h1k = abs(h_diff(1j * 2 * math.pi * f1k))
    hp = find_f(freqs, mags, db(h1k) - 3, falling=False)
    lp = find_f(freqs, mags, db(h1k) - 3, falling=True)

    mid_theory = 2 * (RF / RIN)
    hp_theory = 1.0 / (2 * math.pi * RIN * CAC)
    lp_theory = 1.0 / (2 * math.pi * RF * CF)

    noise = noise_1khz()

    # downsample for chart (~15 pts)
    chart_idx = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70]
    chart = []
    for i in chart_idx:
        f = freqs[i]
        if f < 1:
            lab = f"{f:.1f} Hz"
        elif f < 1000:
            lab = f"{f:.0f} Hz"
        elif f < 1e6:
            lab = f"{f/1000:.0f} kHz"
        else:
            lab = "1 MHz"
        chart.append({"f": f, "label": lab, "dB": dbs[i], "mag": mags[i], "deg": phases[i]})

    out = {
        "gain_1kHz": h1k,
        "gain_1kHz_dB": db(h1k),
        "gain_theory": mid_theory,
        "hp_3dB_Hz": hp,
        "hp_theory_Hz": hp_theory,
        "lp_3dB_Hz": lp,
        "lp_theory_Hz": lp_theory,
        "vin_for_adc_fs_Vrms": VFS_RMS / h1k,
        "pcm1804_fs_Vrms": VFS_RMS,
        "noise": noise,
        "chart": chart,
    }
    dest = Path(__file__).with_name("analog_fe_results.json")
    dest.write_text(json.dumps(out, indent=2))
    print(json.dumps({k: v for k, v in out.items() if k != "chart"}, indent=2))
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
