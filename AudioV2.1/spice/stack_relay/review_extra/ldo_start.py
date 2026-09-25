#!/usr/bin/env python3
"""査読の追加: ch の LDO を EN したときの D ノードの落ち込み（22 Ω）。
LDO は挙動モデル: 出力の目標電圧が tSS で 0→12 V に上がる。出力電流 = min(ILIM, 追従に要る電流)、
ドロップアウトは VDO(24 mA)≈0.2 V（Figure 9 目読み）で頭打ち。出力側は COUT_total と op-amp 負荷（12 V で 20 mA の抵抗）。
D ノードは model.netlist（線形源 B / 0.3 A 頭打ち L03、4 段、セラミック lo/nom/hi、バルク無し）。
リレーは t=1 ms で閉じ、EN は t=15 ms。"""
import sys, os, subprocess, tempfile, itertools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model import netlist
HERE = os.path.dirname(os.path.abspath(__file__))
TEN = 15e-3
def run(rser, cer, src, cout, tss, ilim=0.22, v0=15.0):
    net = netlist(rser=rser, bulk="none", cer=cer, lhop=300e-9, rhop=0.05, hops=4, src=src,
                  esr201=0.05, cpb=0.0, bounce="none", tend=60e-3)
    if v0 != 15.0:
        net = net.replace("V0 V0 0 DC 15.0", f"V0 V0 0 DC {v0}")
    tend = TEN + max(3*tss, 5e-3) + 10e-3
    ldo = f"""
Vramp tgt 0 PWL(0 0 {TEN} 0 {TEN+tss} 12 1 12)
Bldo D LO I=min({ilim}, max(0, 50*(V(tgt)-V(LO)))) * (0.5+0.5*tanh((V(D)-V(LO)-0.2)/0.02))
Cout LO 0 {cout}
Rop LO 0 600
"""
    fd, dat = tempfile.mkstemp(suffix=".dat", dir=HERE); os.close(fd)
    ctl = f"""
.options method=gear
.nodeset v(p)=15
.control
set noaskquit
set wr_singlescale
tran 1u {tend} 0 1u
wrdata {dat} v(d) v(lo) v(p)
quit
.endc
.end
"""
    with tempfile.NamedTemporaryFile("w", suffix=".cir", delete=False, dir=HERE) as f:
        f.write("* ldo start\n" + net + ldo + ctl); fn = f.name
    subprocess.run(["ngspice", "-b", fn], capture_output=True, text=True, timeout=600)
    rows = []
    for line in open(dat):
        a = line.split()
        try: rows.append(tuple(float(x) for x in a[:4]))
        except ValueError: pass
    os.unlink(fn); os.unlink(dat)
    pre = [r for r in rows if 13e-3 < r[0] < TEN]
    vd_pre = pre[-1][1] if pre else None
    post = [r for r in rows if r[0] >= TEN]
    vdmin = min(r[1] for r in post); t13 = sum(1 for r in post if r[1] < 13.0) * 1e-3  # ms（1 µs 刻み）
    vpmin = min(r[3] for r in post)
    vlo_end = rows[-1][2]
    return vd_pre, vdmin, t13, vlo_end, vpmin
print("rser cer src COUT tSS | V(D) 直前 | V(D) 最低 | 13 V 未満 [ms] | Vout 終値 | 親最低")
for rser, cer, src, cout, tss in itertools.product([22.0], ["lo", "hi"], ["B", "L03"],
        [10e-6, 22e-6, 47e-6, 100e-6], [14e-3, 0.05e-3]):
    r = run(rser, cer, src, cout, tss)
    print(f"{rser} {cer} {src} {cout*1e6:.0f}u tSS={tss*1e3:.2f}ms | {r[0]:.2f} | {r[1]:.2f} | {r[2]:.2f} | {r[3]:.2f} | {r[4]:.2f}")
# 最悪の源（14.14 V 相当）で tSS 14 ms
print("-- 源を 14.14 V（クロスレギュ −5 %・Ro 0.75 Ω×150 mA 相当）に下げた場合、tSS 14 ms")
for cer, cout in itertools.product(["lo", "hi"], [10e-6, 22e-6, 47e-6, 100e-6]):
    r = run(22.0, cer, "B", cout, 14e-3, v0=14.14)
    print(f"22 {cer} B 14.14V {cout*1e6:.0f}u | {r[0]:.2f} | {r[1]:.2f} | {r[2]:.2f} | {r[3]:.2f}")
