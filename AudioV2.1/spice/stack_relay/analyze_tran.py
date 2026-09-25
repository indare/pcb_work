#!/usr/bin/env python3
import json, os, collections
HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "results_tran.json")))
bad = [r for r in R if r["ipk"] is None or r["nrows"] < 1000]
print("runs", len(R), "failed", len(bad))
for b in bad[:10]:
    print("  FAIL", {k: b[k] for k in ["rser", "bulk", "cer", "lhop", "src", "cpb", "bounce", "rail", "hops"]})
R = [r for r in R if r not in bad]
main = [r for r in R if r["hops"] == 4 and r["rail"] == "+" and r["rhop"] == 0.01]

def worst(rows, key, fn=max):
    v = [r[key] for r in rows if r[key] is not None]
    return fn(v) if v else None

print("\n== 表1: 接点電流と I²t（+15 V、4 段、全角の最悪。バウンス有無を分けて）==")
print("Rser | バルク | Ipk 最大 [A] | I²t 最大 [A²s] (バウンス無/有) | E_R=I²t·R [mJ] | Rser 瞬時電力 [W]")
for rser in sorted({r["rser"] for r in main}):
    for bulk in ["none", "b22", "b45"]:
        rows = [r for r in main if r["rser"] == rser and r["bulk"] == bulk]
        nb = [r for r in rows if r["bounce"] == "none"]
        b3 = [r for r in rows if r["bounce"] == "b3"]
        ipk = worst(rows, "ipk")
        print(f"{rser:5} | {bulk:4} | {ipk:.3f} | {worst(nb,'i2t'):.2e} / {worst(b3,'i2t'):.2e} | {worst(rows,'i2t')*rser*1e3:.2f} | {ipk**2*rser:.1f}")

print("\n== 表2: 親ノードの最低電圧 [V]（+15 V 側、4 段、最悪: セラミック・L・バウンスの全角）。括弧は 11.5 V 未満の最長時間 [ms] ==")
srcs = ["A", "B", "C", "L10", "L06", "L03"]
for cpb in [0.0, 100e-6]:
    print(f"-- 親バルク {'なし（C201 だけ）' if cpb == 0 else '+100 µF'}")
    print("Rser | バルク | " + " | ".join(srcs))
    for rser in sorted({r["rser"] for r in main}):
        for bulk in ["none", "b22", "b45"]:
            cells = []
            for s in srcs:
                rows = [r for r in main if r["rser"] == rser and r["bulk"] == bulk and r["src"] == s and r["cpb"] == cpb]
                vm = worst(rows, "vpmin", min); tb = worst(rows, "tb115")
                cells.append(f"{vm:.2f} ({tb*1e3:.2f})" if tb and tb > 1e-6 else f"{vm:.2f}")
            print(f"{rser:5} | {bulk:4} | " + " | ".join(cells))

print("\n== 表3: 娘のレールが 13.5 V を最後に越えるまでの時間 [ms]（接点が触れてから、最悪）と RS6 の電流のピーク [A] ==")
for rser in sorted({r["rser"] for r in main}):
    for bulk in ["none", "b45"]:
        cells = []
        for s in srcs:
            rows = [r for r in main if r["rser"] == rser and r["bulk"] == bulk and r["src"] == s]
            cells.append(f"{worst(rows,'t_rg')*1e3:.2f} / {worst(rows,'ipeakrs'):.2f}")
        print(f"{rser:5} | {bulk:4} | " + " | ".join(cells))

print("\n== 表4: -15 V（親の固定 53.8 mA）と 1 段目（hops=1, Rhop 0.05）==")
sub = [r for r in R if r["rhop"] == 0.05]
for rail in ["-", "+"]:
    for hops in [1, 4]:
        rows0 = [r for r in sub if r["rail"] == rail and r["hops"] == hops]
        if not rows0: continue
        for rser in [4.7, 10.0, 22.0]:
            for s in ["B", "L06", "L03"]:
                rows = [r for r in rows0 if r["rser"] == rser and r["src"] == s]
                print(f"rail {rail} hops {hops} R {rser} src {s}: Vp min {worst(rows,'vpmin',min):.2f} V, <11.5 V {worst(rows,'tb115')*1e3:.2f} ms, <13 V {worst(rows,'tb13')*1e3:.2f} ms, Ipk {worst(rows,'ipk'):.2f} A")
