#!/usr/bin/env python3
"""電源用リレーが閉じる瞬間の過渡を掃引する。結果は results_tran.json。"""
from __future__ import annotations

import itertools
import math
import json
import os
import re
import subprocess
import sys
import tempfile
from multiprocessing import Pool

from model import netlist, T0, SRC

HERE = os.path.dirname(os.path.abspath(__file__))
TEND = 20e-3


def run_one(p: dict) -> dict:
    net = netlist(**p, tend=TEND)
    fd, dat = tempfile.mkstemp(suffix=".dat", dir="/tmp"); os.close(fd)
    ctl = f"""
.options method=gear
.nodeset v(p)=15
.control
set noaskquit
set wr_singlescale
tran 0.2u {TEND} 0 0.2u
wrdata {dat} v(p) v(d) i(vsen) {"i(lo)" if p["src"] in ("A","B","C") else "v(p)"}
quit
.endc
.end
"""
    with tempfile.NamedTemporaryFile("w", suffix=".cir", delete=False, dir="/tmp") as f:
        f.write("* stack relay tran\n" + net + ctl)
        fn = f.name
    try:
        subprocess.run(["ngspice", "-b", fn], capture_output=True, text=True, timeout=600)
        rows = []
        with open(dat) as fh:
            for line in fh:
                a = line.split()
                if len(a) >= 5:
                    try:
                        rows.append(tuple(float(x) for x in a[:5]))
                    except ValueError:
                        pass
    finally:
        os.unlink(fn); os.unlink(dat)
    r = dict(p)
    ts = T0 * 0.99
    ipk = vpmin = None; i2t = 0.0; tb115 = tb13 = tb14 = 0.0; t_rg = None; irs = 0.0
    prev = None
    vp_pre = None
    for (t, vp, vd, ic, il) in rows:
        if vp_pre is None and t >= 0.9e-3:
            vp_pre = vp
        if prev is not None and t >= ts:
            dt = t - prev[0]
            i2t += 0.5 * (ic * ic + prev[3] ** 2) * dt
            if vp < 11.5: tb115 += dt
            if vp < 13.0: tb13 += dt
            if vp < 14.0: tb14 += dt
            if prev[2] < 13.5 <= vd: t_rg = t - T0
            if vd < 13.5 <= prev[2]: t_rg = None
        if t >= ts:
            ipk = ic if ipk is None or ic > ipk else ipk
            vpmin = vp if vpmin is None or vp < vpmin else vpmin
            if SRC[p["src"]][2] is not None:
                ro_, _, il_ = SRC[p["src"]]
                il = il_ * math.tanh((15.0 - vp) / (ro_ * il_))
            irs = max(irs, il)
        prev = (t, vp, vd, ic, il)
    r.update(ipk=ipk, vpmin=vpmin, i2t=i2t, tb115=tb115, tb13=tb13, tb14=tb14, t_rg=t_rg,
             ipeakrs=irs, vdend=rows[-1][2] if rows else None, vpend=rows[-1][1] if rows else None,
             nrows=len(rows), vp_pre=vp_pre, vp0=rows[0][1] if rows else None)
    return r


def grid():
    for rser, bulk, cer, lhop, src, cpb, bounce, rail in itertools.product(
        [1.0, 2.2, 4.7, 10.0, 15.0, 22.0, 33.0],
        ["none", "b22", "b45"],
        ["lo", "nom", "hi"],
        [100e-9, 300e-9],
        ["A", "B", "C", "L03", "L06", "L10"],
        [0.0, 100e-6],
        ["none", "b3"],
        ["+"],
    ):
        if bounce == "b3" and not (lhop == 300e-9 and cpb == 0.0):
            continue
        yield dict(rser=rser, bulk=bulk, cer=cer, lhop=lhop, rhop=0.01, hops=4,
                   src=src, esr201=0.05, cpb=cpb, bounce=bounce, rail=rail)
    # -15 V（親の固定負荷が軽い）と縦積み 1 段目の比較（絞った集合）
    for rser, bulk, cer, src, rail, hops in itertools.product(
        [4.7, 10.0, 22.0], ["none", "b45"], ["lo", "hi"], ["B", "L03", "L06"], ["-", "+"], [1, 4]):
        if rail == "+" and hops == 4:
            continue
        yield dict(rser=rser, bulk=bulk, cer=cer, lhop=300e-9, rhop=0.05, hops=hops,
                   src=src, esr201=0.05, cpb=0.0, bounce="none", rail=rail)


if __name__ == "__main__":
    ps = list(grid())
    print(len(ps), "runs", file=sys.stderr)
    with Pool(4) as pool:
        res = pool.map(run_one, ps, chunksize=4)
    json.dump(res, open(os.path.join(HERE, "results_tran.json"), "w"), indent=0)
    print("done", file=sys.stderr)
