#!/usr/bin/env python3
import json, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "results_ac.json")))
print("runs", len(R))

def w(rows, k, fn=max):
    v = [r[k] for r in rows if r.get(k) is not None]
    return fn(v) if v else float("nan")

def db(x):
    return 20 * math.log10(x)

print("\n== 表A: Rser × 娘のバルクごとの最悪（全角: セラミック 4・L 3・段 1/4・源 A/B/C・親バルク 0/+100）==")
print("Rser | バルク | T の山 1k–3M（倍 @Hz） | T max fsw 200k–1M（倍, dB） | |Z| 20k–3M の山 [Ω] | |Z| fsw max [Ω] | |Z|@1k max [Ω] | |Z| 100–20k の山 [Ω]")
for rser in sorted({r["rser"] for r in R}):
    for bulk in ["none", "b22", "b45"]:
        rows = [r for r in R if r["rser"] == rser and r["bulk"] == bulk]
        tp = max(rows, key=lambda r: r["t_pk"])
        tf = w(rows, "t_fsw")
        print(f"{rser:7} | {bulk:4} | {tp['t_pk']:.2f} @{tp['t_pk_f']/1e3:.0f}k | {tf:.4f} ({db(tf):.1f} dB) | {w(rows,'z_pk_20k_3M'):.3f} | {w(rows,'z_fsw'):.3f} | {w(rows,'z_1k'):.2f} | {w(rows,'z_pk_lf'):.2f}")

print("\n== 表B: セラミックの角ごと（バルクなし）: T max fsw [dB] ==")
for rser in sorted({r["rser"] for r in R}):
    cells = []
    for cer in ["lo", "mid", "nom", "hi"]:
        rows = [r for r in R if r["rser"] == rser and r["bulk"] == "none" and r["cer"] == cer]
        cells.append(f"{db(w(rows,'t_fsw')):.1f}")
    print(f"{rser:7} | " + " | ".join(cells))

print("\n== 表C: 共振の山があるか: T の山が 1.05 倍を超える組の数 / 全数 ==")
for rser in sorted({r["rser"] for r in R}):
    for bulk in ["none", "b45"]:
        rows = [r for r in R if r["rser"] == rser and r["bulk"] == bulk]
        n = sum(1 for r in rows if r["t_pk"] > 1.05)
        print(f"{rser:7} | {bulk} | {n}/{len(rows)}")
