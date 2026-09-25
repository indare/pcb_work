#!/usr/bin/env python3
"""AC 掃引: 娘の LDO 入力で見たインピーダンス |Z(f)| と、親ノード→娘の伝達 |V(Dk)/V(P)|。

独立な回路のコピーを 1 つのネットリストに並べ（GND だけ共有）、ngspice を少ない回数で回す。
出力: results_ac.json（全変種）と netlists/ac_*.cir（実際に回したネットリスト）
"""
from __future__ import annotations

import itertools
import json
import math
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from model import Var, emit  # noqa: E402

NET = HERE / "netlists"
NET.mkdir(exist_ok=True)
FSTART, FSTOP, PPD = 100.0, 10e6, 40


def variants(topo="chain"):
    out = []
    grid = itertools.product([1, 2, 3, 4], [100e-9, 200e-9, 300e-9], [0.01, 0.05],
                             ["lo", "mid", "nom", "hi"], ["A", "B", "C"], [0.05, 0.3])
    for n, lh, rh, cer, src, e201 in grid:
        base = dict(n=n, lhop=lh, rhop=rh, cer=cer, src=src, esr201=e201, topo=topo)
        for cd in (35e-6, 45e-6):
            for rd in (0.1, 0.15, 0.2):
                out.append(Var(plan="1", cd=cd, rd=rd, **base))
        parents = [(0.0, 0.1)] + [(c, e) for c in (100e-6, 220e-6) for e in (0.02, 0.1, 0.3)]
        for cpb, e in parents:
            out.append(Var(plan="2", cpb=cpb, esrpb=e, **base))
            for rs in (0.05, 0.1, 0.15, 0.2, 0.33, 0.5):
                out.append(Var(plan="3", cpb=cpb, esrpb=e, rser=rs, **base))
    return out


def build(batch_id: int, vs: list[Var]) -> tuple[Path, list]:
    lines = [f"* AC batch {batch_id}", ".options klu"]
    meta = []   # (var index, kind, k, pfx)
    vecs = []
    for i, v in enumerate(vs):
        for k in range(1, v.n + 1):
            pfx = f"z{i}k{k}"
            lines += emit(v, pfx, inject_k=k, src_ac=False)
            vecs.append(f"vm({pfx}_D{k})")
            meta.append((i, "Z", k, len(vecs) - 1))
        pfx = f"t{i}"
        lines += emit(v, pfx, inject_k=None, src_ac=True)
        vecs.append(f"vm({pfx}_P)")
        meta.append((i, "TP", 0, len(vecs) - 1))
        for k in range(1, v.n + 1):
            vecs.append(f"vm({pfx}_D{k})")
            meta.append((i, "TD", k, len(vecs) - 1))
    out = NET / f"ac_{batch_id:03d}.dat"
    lines += [".control", "set noaskquit", "set wr_singlescale", "set wr_vecnames",
              f"ac dec {PPD} {FSTART} {FSTOP}"]
    # wrdata は 1 行が長すぎると困るので 200 本ずつ別ファイル
    chunks = [vecs[j:j + 200] for j in range(0, len(vecs), 200)]
    for ci, ch in enumerate(chunks):
        lines.append(f"wrdata {out}.{ci} " + " ".join(ch))
    lines += ["quit", ".endc", ".end"]
    cir = NET / f"ac_{batch_id:03d}.cir"
    cir.write_text("\n".join(lines) + "\n")
    return cir, meta, len(chunks), out


def parse(out: Path, nchunks: int):
    cols_all, freq = [], None
    for ci in range(nchunks):
        rows = Path(f"{out}.{ci}").read_text().split("\n")
        data = [list(map(float, r.split())) for r in rows[1:] if r.strip()]
        freq = [d[0] for d in data]
        ncol = len(data[0]) - 1
        cols_all += [[d[1 + j] for d in data] for j in range(ncol)]
    return freq, cols_all


def interp_log(freq, y, f0):
    for j in range(len(freq) - 1):
        if freq[j] <= f0 <= freq[j + 1]:
            t = (math.log(f0) - math.log(freq[j])) / (math.log(freq[j + 1]) - math.log(freq[j]))
            return y[j] * (1 - t) + y[j + 1] * t
    return float("nan")


def peak(freq, y, f1, f2):
    best = (-1.0, 0.0)
    for f, v in zip(freq, y):
        if f1 <= f <= f2 and v > best[0]:
            best = (v, f)
    return best


def run_batch(args):
    bid, vs = args
    cir, meta, nch, out = build(bid, vs)
    r = subprocess.run(["ngspice", "-b", str(cir)], capture_output=True, text=True)
    if r.returncode != 0 or not Path(f"{out}.0").exists():
        raise RuntimeError(f"batch {bid} failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")
    freq, cols = parse(out, nch)
    res = []
    per = {}
    for i, kind, k, col in meta:
        per.setdefault(i, {"Z": {}, "TD": {}, "TP": None})
        if kind == "TP":
            per[i]["TP"] = cols[col]
        else:
            per[i][kind][k] = cols[col]
    for i, v in enumerate(vs):
        d = per[i]
        rec = asdict(v)
        zs = []
        for k, z in d["Z"].items():
            zs.append({"k": k,
                       "zpk_audio": peak(freq, z, 100, 20e3),
                       "zpk_hf": peak(freq, z, 20e3, 3e6),
                       "z200k": interp_log(freq, z, 200e3),
                       "zfsw": peak(freq, z, 200e3, 1e6),
                       "z20k": interp_log(freq, z, 20e3),
                       "z1k": interp_log(freq, z, 1e3)})
        ts = []
        for k, vd in d["TD"].items():
            t = [a / b for a, b in zip(vd, d["TP"])]
            ts.append({"k": k, "tpk": peak(freq, t, 1e3, 3e6), "t200k": interp_log(freq, t, 200e3),
                       "tfsw": peak(freq, t, 200e3, 1e6)})
        rec["Z"], rec["T"] = zs, ts
        res.append(rec)
    for ci in range(nch):
        Path(f"{out}.{ci}").unlink()
    return res


def main():
    topo = sys.argv[1] if len(sys.argv) > 1 else "chain"
    vs = variants(topo)
    if topo == "star":   # 比較用に絞る
        vs = [v for v in vs if v.rhop == 0.01 and v.src == "A" and v.esr201 == 0.05]
    bs = 120
    batches = [(b, vs[j:j + bs]) for b, j in enumerate(range(0, len(vs), bs))]
    print(f"{len(vs)} variants, {len(batches)} batches", flush=True)
    res = []
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as ex:
        for r in ex.map(run_batch, batches):
            res += r
    # 最初のバッチのネットリストだけ残す（例示）。他は消す
    for p in NET.glob("ac_[0-9]*.cir"):
        if p.name not in ("ac_000.cir",):
            p.unlink()
    (NET / "ac_000.cir").rename(NET / f"ac_example_{topo}.cir")
    (HERE / f"results_ac_{topo}.json").write_text(json.dumps(res))
    print("done", len(res))


if __name__ == "__main__":
    main()
