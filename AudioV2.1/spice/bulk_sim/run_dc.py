#!/usr/bin/env python3
"""DC 降下（.op）: 縦積み 4 枚、設計点（最上段の娘で 1 ch ON）と故障（4 枚とも 1 ch ON）。"""
import re, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from model import Var, emit, I_ON, I_OFF
lines = ["* DC drop", ".options klu"]
cases = []
i = 0
for plan, rser in (("1", 1e-4), ("3", 0.15), ("3", 0.33), ("3", 0.5)):
    for rhop in (0.01, 0.05):
        for src in ("A", "C"):
            for mode in ("design", "fault"):
                v = Var(plan=plan, n=4, lhop=300e-9, rhop=rhop, cer="nom", src=src, esr201=0.05,
                        cd=40e-6 if plan == "1" else 0, rd=0.15, cpb=0 if plan == "1" else 100e-6, esrpb=0.02, rser=rser)
                loads = {4: f"DC {I_ON*1e-3}"} if mode == "design" else {k: f"DC {I_ON*1e-3}" for k in range(1, 5)}
                p = f"c{i}"
                lines += emit(v, p, inject_k=None, src_ac=False, loads=loads)
                cases.append((p, plan, rser, rhop, src, mode))
                i += 1
lines += [".control", "set noaskquit", "op"]
for c in cases:
    p = c[0]
    lines.append(f"print v({p}_P) v({p}_D1) v({p}_D4)")
lines += ["quit", ".endc", ".end"]
cir = HERE / "netlists" / "dc_drop.cir"
cir.write_text("\n".join(lines) + "\n")
out = subprocess.run(["ngspice", "-b", str(cir)], capture_output=True, text=True).stdout
vals = dict((m.group(1), float(m.group(2))) for m in re.finditer(r"v\((c\d+_\w+)\)\s*=\s*([-+0-9.eE]+)", out))
print(f"I_ON = {I_ON:.2f} mA, I_OFF = {I_OFF:.3f} mA, 親の固定負荷は model.I_PARENT")
print("plan | Rser | Rhop | src | mode | V(P) | V(P)-V(D1) mV | V(P)-V(D4) mV | 15-V(D4) mV")
for p, plan, rser, rhop, src, mode in cases:
    P, D1, D4 = vals[p + "_p"], vals[p + "_d1"], vals[p + "_d4"]
    print(f"{plan} | {rser:g} | {rhop} | {src} | {mode} | {P:.4f} | {(P-D1)*1e3:.2f} | {(P-D4)*1e3:.2f} | {(15-D4)*1e3:.1f}")
