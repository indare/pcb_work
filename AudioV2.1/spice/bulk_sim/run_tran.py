#!/usr/bin/env python3
"""過渡: (a) 活線挿入、(b) ch LDO のソフトスタート電流、(c) 1 ch ぶんの負荷ステップ、(d) CNR 無しの電流制限パルス（上限）。

いずれも chain（縦積み）で、いちばん上の娘 N を対象にする。出力 results_tran.json、netlists/tran_example_*.cir
"""
from __future__ import annotations

import itertools
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from model import Var, emit, I_ON, I_OFF  # noqa: E402

NET = HERE / "netlists"
T0 = 10e-6   # イベント時刻

DESIGNS = (
    [("1", dict(cd=40e-6, rd=rd)) for rd in (0.1, 0.15, 0.2)]
    + [("2", dict(cpb=0.0))]
    + [("2", dict(cpb=100e-6, esrpb=e)) for e in (0.02, 0.1, 0.3)]
    + [("3", dict(cpb=100e-6, esrpb=0.02, rser=r)) for r in (0.05, 0.1, 0.15, 0.2, 0.33, 0.5)]
)
CORNERS = list(itertools.product([100e-9, 300e-9], ["lo", "hi"], ["A", "B"]))
EXPS = {
    # 名前: (tstop, tmax)
    "hotplug": (300e-6, 20e-9),
    "softstart": (2e-3, 100e-9),
    "step20": (2e-3, 100e-9),
    "ilim": (2e-3, 100e-9),
}


def load_expr(exp: str) -> str:
    t = T0
    if exp == "softstart":   # 8.6 mA（10 µF × 12 V / 14 ms、review/main_power_compare_review.md L89）＋ OFF 分
        return f"PWL(0 {I_OFF*1e-3} {t} {I_OFF*1e-3} {t+10e-6} {(I_OFF+8.6)*1e-3})"
    if exp == "step20":      # ON した ch の定常（ソケット 20 ＋ LDO 1.0 ＋ TMUX）へ 1 µs で
        return f"PWL(0 {I_OFF*1e-3} {t} {I_OFF*1e-3} {t+1e-6} {I_ON*1e-3})"
    if exp == "ilim":        # CNR 無しの上限: TPS7A49 ILIM max 500 mA で COUT 10 µF を 12 V まで（240 µs）
        tp = 10e-6 * 12 / 0.5
        return (f"PWL(0 {I_OFF*1e-3} {t} {I_OFF*1e-3} {t+1e-6} {0.5+I_OFF*1e-3} "
                f"{t+tp} {0.5+I_OFF*1e-3} {t+tp+1e-6} {I_ON*1e-3})")
    raise ValueError(exp)


def cases():
    out = []
    for exp in EXPS:
        for (plan, kw), (lh, cer, src), n in itertools.product(DESIGNS, CORNERS, [1, 2, 3, 4]):
            v = Var(plan=plan, n=n, lhop=lh, rhop=0.01, cer=cer, src=src, esr201=0.05, **kw)
            out.append((exp, v))
    return out


def build(bid, exp, items):
    tstop, tmax = EXPS[exp]
    lines = [f"* tran {exp} batch {bid}", ".options klu method=gear",
             ".model SWMOD SW(Ron=5m Roff=1e9 Vt=0.5 Vh=0)"]
    meas = []
    for i, v in enumerate(items):
        p = f"c{i}"
        N = v.n
        if exp == "hotplug":
            lines += emit(v, p, inject_k=None, src_ac=False, hotplug_k=N)
        else:
            lines += emit(v, p, inject_k=None, src_ac=False, loads={N: load_expr(exp)})
        meas.append(f"meas tran {p}_dmax MAX v({p}_D{N}) from={T0} to={tstop}")
        meas.append(f"meas tran {p}_dmin MIN v({p}_D{N}) from={T0} to={tstop}")
        meas.append(f"meas tran {p}_d0 FIND v({p}_D{N}) AT={T0*0.9}")
        meas.append(f"meas tran {p}_pmin MIN v({p}_P) from={T0} to={tstop}")
        meas.append(f"meas tran {p}_pmax MAX v({p}_P) from={T0} to={tstop}")
        meas.append(f"meas tran {p}_p0 FIND v({p}_P) AT={T0*0.9}")
        meas.append(f"meas tran {p}_imax MAX i(lh{N}{p}) from={T0} to={tstop}")
        if N >= 2:
            meas.append(f"meas tran {p}_omin MIN v({p}_D1) from={T0} to={tstop}")
            meas.append(f"meas tran {p}_omax MAX v({p}_D1) from={T0} to={tstop}")
            meas.append(f"meas tran {p}_o0 FIND v({p}_D1) AT={T0*0.9}")
        # 終値（落ち着いた値）
        meas.append(f"meas tran {p}_dend FIND v({p}_D{N}) AT={tstop*0.999}")
    saves = []
    for i, v in enumerate(items):
        p = f"c{i}"
        saves += [f"v({p}_D{v.n})", f"v({p}_P)", f"i(lh{v.n}{p})"] + ([f"v({p}_D1)"] if v.n >= 2 else [])
    lines.append(".save " + " ".join(saves))
    lines += [".control", "set noaskquit", f"tran {tmax} {tstop} 0 {tmax}"] + meas + ["quit", ".endc", ".end"]
    cir = NET / f"tran_{exp}_{bid:03d}.cir"
    cir.write_text("\n".join(lines) + "\n")
    return cir


def run(args):
    bid, exp, items = args
    cir = build(bid, exp, items)
    r = subprocess.run(["ngspice", "-b", str(cir)], capture_output=True, text=True)
    vals = {}
    for m in re.finditer(r"^(c\d+_\w+)\s+=\s+([-+0-9.eE]+)", r.stdout, re.M):
        vals[m.group(1)] = float(m.group(2))
    res = []
    for i, v in enumerate(items):
        p = f"c{i}"
        g = {k[len(p) + 1:]: val for k, val in vals.items() if k.startswith(p + "_")}
        if "dmax" not in g:
            raise RuntimeError(f"{cir}: missing meas for {p}\n{r.stdout[-3000:]}")
        res.append({"exp": exp, **asdict(v), **g})
    if bid != 0:
        cir.unlink()
    else:
        cir.rename(NET / f"tran_example_{exp}.cir")
    return res


def main():
    cs = cases()
    by = {}
    for exp, v in cs:
        by.setdefault(exp, []).append(v)
    batches = []
    for exp, vs in by.items():
        for b, j in enumerate(range(0, len(vs), 1)):
            batches.append((b, exp, vs[j:j + 1]))
    print(len(cs), "cases", len(batches), "batches", flush=True)
    res = []
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as ex:
        for r in ex.map(run, batches):
            res += r
    (HERE / "results_tran.json").write_text(json.dumps(res))
    print("done", len(res))


if __name__ == "__main__":
    main()
