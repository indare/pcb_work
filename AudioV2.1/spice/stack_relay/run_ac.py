#!/usr/bin/env python3
"""LDO 入力（娘のノード D）の |Z| と、親→娘のリプル伝達 |V(D)/V(P)| を掃引する（線形の源 A/B/C のみ）。"""
from __future__ import annotations

import itertools
import json
import math
import os
import subprocess
import sys
import tempfile
from multiprocessing import Pool

from model import netlist

HERE = os.path.dirname(os.path.abspath(__file__))


def ac_run(p: dict, mode: str):
    net = netlist(**p, ac=mode)
    fd, dat = tempfile.mkstemp(suffix=".dat", dir="/tmp"); os.close(fd)
    outv = "v(d)" if mode == "z" else "v(d) v(p)"
    ctl = f"""
.control
set noaskquit
set wr_singlescale
ac dec 40 100 10meg
wrdata {dat} {outv}
quit
.endc
.end
"""
    with tempfile.NamedTemporaryFile("w", suffix=".cir", delete=False, dir="/tmp") as f:
        f.write("* ac\n" + net + ctl)
        fn = f.name
    rows = []
    try:
        subprocess.run(["ngspice", "-b", fn], capture_output=True, text=True, timeout=120)
        for line in open(dat):
            a = line.split()
            try:
                rows.append([float(x) for x in a])
            except ValueError:
                pass
    finally:
        os.unlink(fn); os.unlink(dat)
    return rows


def run_one(p: dict) -> dict:
    r = dict(p)
    z = ac_run(p, "z")      # f, re, im
    zz = [(row[0], math.hypot(row[1], row[2])) for row in z if len(row) >= 3]
    t = ac_run(p, "src")    # f, re d, im d, re p, im p
    tt = [(row[0], math.hypot(row[1], row[2]) / max(math.hypot(row[3], row[4]), 1e-30)) for row in t if len(row) >= 5]

    def mx(seq, a, b):
        s = [(v, f) for f, v in seq if a <= f <= b]
        return max(s) if s else (None, None)

    def at(seq, f0):
        return min(seq, key=lambda x: abs(math.log(x[0] / f0)))[1]

    r["z_1k"] = at(zz, 1e3)
    r["z_20k"] = at(zz, 20e3)
    r["z_pk_20k_3M"], r["z_pk_f"] = mx(zz, 20e3, 3e6)
    r["z_pk_lf"], r["z_pk_lf_f"] = mx(zz, 100, 20e3)
    r["z_fsw"], _ = mx(zz, 200e3, 1e6)
    r["t_pk"], r["t_pk_f"] = mx(tt, 1e3, 3e6)
    r["t_fsw"], _ = mx(tt, 200e3, 1e6)
    r["t_200k"] = at(tt, 200e3)
    return r


def grid():
    for rser, bulk, cer, lhop, hops, src, cpb in itertools.product(
        [1e-4, 0.33, 1.0, 2.2, 4.7, 10.0, 15.0, 22.0, 33.0],
        ["none", "b22", "b45"],
        ["lo", "mid", "nom", "hi"],
        [100e-9, 200e-9, 300e-9],
        [1, 4],
        ["A", "B", "C"],
        [0.0, 100e-6],
    ):
        yield dict(rser=rser, bulk=bulk, cer=cer, lhop=lhop, rhop=0.01, hops=hops, src=src,
                   esr201=0.05, cpb=cpb, bounce="none")


if __name__ == "__main__":
    ps = list(grid())
    print(len(ps), file=sys.stderr)
    with Pool(4) as pool:
        res = pool.map(run_one, ps, chunksize=8)
    json.dump(res, open(os.path.join(HERE, "results_ac.json"), "w"))
    print("done", file=sys.stderr)
