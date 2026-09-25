#!/usr/bin/env python3
"""results_ac_chain.json から、セラミックの角を絞った最悪値（CIN 10 µF を採った場合など）を出す。"""
import json, sys
from pathlib import Path
res = json.loads((Path(__file__).resolve().parent / "results_ac_chain.json").read_text())
def worst(filt):
    rs = [r for r in res if filt(r)]
    zhf = max(((z["zpk_hf"][0], z["zpk_hf"][1]) for r in rs for z in r["Z"]), default=(0, 0))
    zau = max(((z["zpk_audio"][0], z["zpk_audio"][1]) for r in rs for z in r["Z"]), default=(0, 0))
    zf = max((z["zfsw"][0] for r in rs for z in r["Z"]), default=0)
    tf = max(((t["tfsw"][0], t["tfsw"][1]) for r in rs for t in r["T"]), default=(0, 0))
    tp = max(((t["tpk"][0], t["tpk"][1]) for r in rs for t in r["T"]), default=(0, 0))
    return f"Zpk(20k-3M) {zhf[0]:.3f}@{zhf[1]/1e3:.0f}k | Zpk(100-20k) {zau[0]:.2f}@{zau[1]/1e3:.1f}k | Zmax(fsw) {zf:.3f} | Tpk {tp[0]:.2f}@{tp[1]/1e3:.0f}k | Tmax(fsw) {tf[0]:.2f}@{tf[1]/1e3:.0f}k | n_var={len(rs)}"
print("## セラミック nom/hi（CIN 10 µF）に限った最悪、n=1..4 全部")
for lab, f in [
    ("(1) Cd45 Rd0.15", lambda r: r["plan"]=="1" and r["cd"]==45e-6 and r["rd"]==0.15),
    ("(1) Cd35 Rd0.1", lambda r: r["plan"]=="1" and r["cd"]==35e-6 and r["rd"]==0.1),
    ("(2) +100 ESR0.02", lambda r: r["plan"]=="2" and r["cpb"]==100e-6 and r["esrpb"]==0.02),
    ("(2) +220 ESR0.3", lambda r: r["plan"]=="2" and r["cpb"]==220e-6 and r["esrpb"]==0.3),
    ("(3) +100 ESR0.02 Rser0.15", lambda r: r["plan"]=="3" and r["cpb"]==100e-6 and r["esrpb"]==0.02 and r["rser"]==0.15),
    ("(3) +100 ESR0.02 Rser0.33", lambda r: r["plan"]=="3" and r["cpb"]==100e-6 and r["esrpb"]==0.02 and r["rser"]==0.33),
    ("(3) +100 ESR0.02 Rser0.5", lambda r: r["plan"]=="3" and r["cpb"]==100e-6 and r["esrpb"]==0.02 and r["rser"]==0.5),
]:
    for cset in (("nom","hi"), ("lo","mid")):
        print(lab, cset, worst(lambda r, f=f: f(r) and r["cer"] in cset))
print("\n## (3) Rser 0.33 の親バルク別（全角・n=1..4）: 低域の山は RS6 の仮定モデル次第")
for cpb in (0, 100e-6, 220e-6):
    for e in ((0.1,) if cpb == 0 else (0.02, 0.1, 0.3)):
        for src in ("A","B","C"):
            print(f"Cpb {cpb*1e6:.0f} ESR {e} src{src}", worst(lambda r: r["plan"]=="3" and r["rser"]==0.33 and r["cpb"]==cpb and (cpb==0 or r["esrpb"]==e) and r["src"]==src))
print("\n## (1) Cd45 Rd0.15 の源別")
for src in ("A","B","C"):
    print(src, worst(lambda r: r["plan"]=="1" and r["cd"]==45e-6 and r["rd"]==0.15 and r["src"]==src))
