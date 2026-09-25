#!/usr/bin/env python3
"""results_tran.json を設計ごと・娘枚数ごとに畳む（角 = L 100/300 nH、セラミック lo/hi、源 A/B の最悪）。"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
res = json.loads((HERE / "results_tran.json").read_text())


def design(r):
    if r["plan"] == "1":
        return f"(1) Cd {r['cd']*1e6:.0f}µ Rd {r['rd']}"
    pb = "C201 のみ" if r["cpb"] == 0 else f"+{r['cpb']*1e6:.0f}µ ESR {r['esrpb']}"
    if r["plan"] == "2":
        return f"(2) {pb}"
    return f"(3) {pb} Rser {r['rser']}"


def corner(r):
    return f"L{r['lhop']*1e9:.0f}n {r['cer']} src{r['src']}"


g = defaultdict(list)
for r in res:
    g[(r["exp"], design(r), r["n"])].append(r)

order = sorted(g, key=lambda k: (k[0], k[1], k[2]))
for exp in ("hotplug", "softstart", "step20", "ilim"):
    print(f"\n## {exp}")
    if exp == "hotplug":
        print("design | n | 新しい娘の Vmax [V] (角) | VDD−VSS=2×Vmax [V] | 親 P の最小 [V] | 既存の娘1 の最小 [V] | hop 電流 max [A] | 300µs 後の新しい娘 [V]")
    else:
        print("design | n | 娘 N の低下 max [mV] (角) | 娘 N の上振れ [mV] | 親 P の低下 [mV] | 娘1 の低下 [mV] | 2ms 後の娘 N の降下 [mV]")
    for k in order:
        if k[0] != exp:
            continue
        rs = g[k]
        if exp == "hotplug":
            w = max(rs, key=lambda r: r["dmax"])
            pmin = min(r["pmin"] for r in rs)
            omin = min((r["omin"] for r in rs if "omin" in r), default=float("nan"))
            imax = max(r["imax"] for r in rs)
            dend = min(r["dend"] for r in rs)
            print(f"{k[1]} | {k[2]} | {w['dmax']:.2f} ({corner(w)}) | {2*w['dmax']:.1f} | {pmin:.2f} | {omin:.2f} | {imax:.1f} | {dend:.3f}")
        else:
            w = max(rs, key=lambda r: r["d0"] - r["dmin"])
            up = max(r["dmax"] - r["d0"] for r in rs)
            pd = max(r["p0"] - r["pmin"] for r in rs)
            od = max((r["o0"] - r["omin"] for r in rs if "omin" in r), default=float("nan"))
            de = max(r["d0"] - r["dend"] for r in rs)
            print(f"{k[1]} | {k[2]} | {(w['d0']-w['dmin'])*1e3:.1f} ({corner(w)}) | {up*1e3:.1f} | {pd*1e3:.1f} | {od*1e3:.1f} | {de*1e3:.1f}")
