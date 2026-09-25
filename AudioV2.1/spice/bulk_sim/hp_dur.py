#!/usr/bin/env python3
"""活線挿入で、既存の娘1 の入力が 13 V（12 V 出力＋ヘッドルーム約 1 V）を割っている時間。"""
import re, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from model import Var, emit
cases = [("(1) Cd40 Rd0.15", dict(plan="1", cd=40e-6, rd=0.15), "hi", "B"),
         ("(1) Cd40 Rd0.15", dict(plan="1", cd=40e-6, rd=0.15), "lo", "A"),
         ("(3) +100µ Rser0.33", dict(plan="3", cpb=100e-6, esrpb=0.02, rser=0.33), "lo", "A"),
         ("(3) +100µ Rser0.33", dict(plan="3", cpb=100e-6, esrpb=0.02, rser=0.33), "hi", "B"),
         ("(3) +100µ Rser0.5", dict(plan="3", cpb=100e-6, esrpb=0.02, rser=0.5), "lo", "A"),
         ("(2) +100µ ESR0.1", dict(plan="2", cpb=100e-6, esrpb=0.1), "lo", "A")]
for lab, kw, cer, src in cases:
    for n in (2, 4):
        v = Var(n=n, lhop=300e-9, rhop=0.01, cer=cer, src=src, esr201=0.05, **kw)
        L = ["* hp dur", ".options klu method=gear", ".model SWMOD SW(Ron=5m Roff=1e9 Vt=0.5 Vh=0)"]
        L += emit(v, "c0", inject_k=None, src_ac=False, loads={1: "DC 0.02292"}, hotplug_k=n)
        L += [".save v(c0_D1) v(c0_P)", ".control", "set noaskquit", "tran 20n 300u 0 20n",
              "meas tran tf WHEN v(c0_D1)=13 FALL=1", "meas tran tr WHEN v(c0_D1)=13 RISE=1",
              "meas tran vmin MIN v(c0_D1) from=10u to=300u", "quit", ".endc", ".end"]
        cir = HERE / "netlists" / "tmp_hpdur.cir"
        cir.write_text("\n".join(L) + "\n")
        out = subprocess.run(["ngspice", "-b", str(cir)], capture_output=True, text=True).stdout
        g = dict((m.group(1), float(m.group(2))) for m in re.finditer(r"^(tf|tr|vmin)\s+=\s+([-+0-9.eE]+)", out, re.M))
        dur = (g["tr"] - g["tf"]) * 1e6 if "tf" in g and "tr" in g else 0.0
        print(f"{lab} cer={cer} src{src} n={n}: 娘1 最小 {g.get('vmin', float('nan')):.2f} V, 13 V 未満 {dur:.1f} µs")
cir.unlink()
