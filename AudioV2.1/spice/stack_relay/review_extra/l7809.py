#!/usr/bin/env python3
"""査読の追加: 親 +15 V の落ち込みで L7809→VCC_TONE（PT2314E）がどう動くか。
L7809 は挙動モデル: VOUT ≤ 9 V、ドロップアウト Vd（Figure 28 目読み 20〜200 mA で 1.5〜1.6 V → 1.6 V）、
入口の F203（PPTC 0.1 A hold）を R_pptc で〔仮定: 2.5 / 7.5 Ω〕。VCC_TONE は C203 10 µF＋0.2 µF、
PT2314E 40 mA max（定電流、4 V 以下で消える）。親の固定負荷から 40 mA を差し引いて二重計上を避ける。"""
import sys, os, subprocess, tempfile, itertools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import model
from model import netlist
HERE = os.path.dirname(os.path.abspath(__file__))
def run(rser, bulk, cpb, src, rp):
    model.I_PARENT["+"] = 0.1018 - 0.040
    net = netlist(rser=rser, bulk=bulk, cer="hi", lhop=300e-9, rhop=0.01, hops=4, src=src,
                  esr201=0.05, cpb=cpb, bounce="none", tend=20e-3)
    reg = f"""
Rpptc P TIN {rp}
Ctin TIN 0 0.33u
Breg TIN VT I=min(1.5, max(0, 20*(9-V(VT)))) * (0.5+0.5*tanh((V(TIN)-V(VT)-1.6)/0.05))
Cvt VT 0 10.2u
Bpt VT 0 I=0.040*(0.5+0.5*tanh((V(VT)-4)/0.2))
"""
    fd, dat = tempfile.mkstemp(suffix=".dat", dir=HERE); os.close(fd)
    ctl = f"""
.options method=gear
.nodeset v(p)=15 v(vt)=9 v(tin)=14.7
.control
set noaskquit
set wr_singlescale
tran 0.5u 20m 0 0.5u
wrdata {dat} v(p) v(vt)
quit
.endc
.end
"""
    with tempfile.NamedTemporaryFile("w", suffix=".cir", delete=False, dir=HERE) as f:
        f.write("* l7809\n" + net + reg + ctl); fn = f.name
    subprocess.run(["ngspice", "-b", fn], capture_output=True, text=True, timeout=600)
    rows = []
    for line in open(dat):
        a = line.split()
        try: rows.append(tuple(float(x) for x in a[:3]))
        except ValueError: pass
    os.unlink(fn); os.unlink(dat)
    post = [r for r in rows if r[0] > 0.99e-3]
    pre = [r for r in rows if 0.8e-3 < r[0] < 0.99e-3]
    dt = 0.5e-6
    return (pre[-1][2], min(r[1] for r in post), min(r[2] for r in post),
            sum(dt for r in post if r[2] < 8.55)*1e3, sum(dt for r in post if r[2] < 8.9)*1e3)
print("Rser 娘バルク 親+ 源 Rpptc | VCC_TONE 前 | 親最低 | VCC_TONE 最低 | 8.55 V 未満 ms | 8.9 V 未満 ms")
for rser, bulk, cpb, src, rp in itertools.product([4.7, 10.0, 22.0], ["none", "b45"], [0.0, 100e-6], ["L03", "L06"], [7.5]):
    r = run(rser, bulk, cpb, src, rp)
    print(f"{rser:4} {bulk:4} {'+100u' if cpb else '  -  '} {src} {rp} | {r[0]:.2f} | {r[1]:.2f} | {r[2]:.2f} | {r[3]:.2f} | {r[4]:.2f}")
