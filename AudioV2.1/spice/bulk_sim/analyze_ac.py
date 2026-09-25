#!/usr/bin/env python3
"""results_ac_*.json を設計の選択ごとに畳む（不確かな角 = L, Rhop, セラミック, 源, C201 ESR の最悪）。"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
topo = sys.argv[1] if len(sys.argv) > 1 else "chain"
res = json.loads((HERE / f"results_ac_{topo}.json").read_text())


def design(r):
    if r["plan"] == "1":
        return ("1", f"Cd {r['cd']*1e6:.0f}µ Rd {r['rd']}")
    pb = "C201 のみ" if r["cpb"] == 0 else f"+{r['cpb']*1e6:.0f}µ ESR {r['esrpb']}"
    if r["plan"] == "2":
        return ("2", pb)
    return ("3", f"{pb} / Rser {r['rser']}")


def fmt_f(f):
    return f"{f/1e3:.0f}k" if f < 1e6 else f"{f/1e6:.2f}M"


groups = defaultdict(list)
for r in res:
    groups[(design(r), r["n"])].append(r)

rows = []
for (d, n), rs in groups.items():
    w = {"hf": (-1, 0, None), "au": (-1, 0, None), "z200": (-1, None), "tpk": (-1, 0, None), "t200": (-1, None), "zf": (-1, 0, None), "tf": (-1, 0, None)}
    for r in rs:
        for z in r["Z"]:
            if z["zpk_hf"][0] > w["hf"][0]:
                w["hf"] = (z["zpk_hf"][0], z["zpk_hf"][1], (r, z["k"]))
            if z["zpk_audio"][0] > w["au"][0]:
                w["au"] = (z["zpk_audio"][0], z["zpk_audio"][1], (r, z["k"]))
            if z["zfsw"][0] > w["zf"][0]:
                w["zf"] = (z["zfsw"][0], z["zfsw"][1], (r, z["k"]))
            if z["z200k"] > w["z200"][0]:
                w["z200"] = (z["z200k"], (r, z["k"]))
        for t in r["T"]:
            if t["tpk"][0] > w["tpk"][0]:
                w["tpk"] = (t["tpk"][0], t["tpk"][1], (r, t["k"]))
            if t["tfsw"][0] > w["tf"][0]:
                w["tf"] = (t["tfsw"][0], t["tfsw"][1], (r, t["k"]))
            if t["t200k"] > w["t200"][0]:
                w["t200"] = (t["t200k"], (r, t["k"]))
    rows.append((d, n, w))


def corner(rk):
    r, k = rk
    return f"L{r['lhop']*1e9:.0f}n R{r['rhop']} {r['cer']} src{r['src']} e201={r['esr201']} k={k}"


rows.sort(key=lambda x: (x[0][0], x[0][1], x[1]))
print(f"# topo={topo}: 設計の選択ごと・娘 n 枚。値は不確かな角の最悪")
print("plan | design | n | Zpk(20k-3M) Ω @f | worst corner | Zpk(100-20k) Ω @f | Z@200k Ω | Zmax(200k-1M) @f | Tpk(1k-3M) @f | T@200k | Tmax(200k-1M) @f")
for d, n, w in rows:
    print(f"{d[0]} | {d[1]} | {n} | {w['hf'][0]:.3f} @{fmt_f(w['hf'][1])} | {corner(w['hf'][2])} | "
          f"{w['au'][0]:.3f} @{fmt_f(w['au'][1])} | {w['z200'][0]:.3f} | {w['zf'][0]:.3f} @{fmt_f(w['zf'][1])} | "
          f"{w['tpk'][0]:.2f} @{fmt_f(w['tpk'][1])} | {w['t200'][0]:.3f} | {w['tf'][0]:.3f} @{fmt_f(w['tf'][1])}")
