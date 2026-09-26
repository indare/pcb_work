#!/usr/bin/env python3
"""片側だけ落ちる: −15 V の母線が 0 V へ（+ 側は生きたまま）。石が ±OUT の間に載って −OUT を押し上げる。"""
import subprocess, re, itertools, os
H=os.path.dirname(os.path.abspath(__file__))
def run(cout, i0, clamp, oi, encut):
    en = "0.5*(1+tanh((-v(inn)-10.5)/0.05))" if encut else "1"
    L=[f"* cout={cout} i0={i0} clamp={clamp} oi={oi} encut={encut}",
       "Vpp pp 0 14.1", "Rsp pp inp 22", "Cinp inp 0 22.7u IC=14.1",
       "Vpn pn 0 0", "Rsn pn inn 22", "Cinn inn 0 22.7u IC=-14.1",
       "Bmp inp 0 I = 2.9m*min(1,max(v(inp),0)/3)",
       f"Cop outp 0 {cout}u IC=12", f"Con outn 0 {cout}u IC=-12",
       f"Bldop inp outp I = {en}*min(0.5, max(0,(min(12, v(inp)-0.07)-v(outp))/0.5))",
       f"Bldon outn inn I = {en}*min(0.5, max(0,(v(outn)-max(-12, v(inn)+0.07))/0.5))",
       f"Bop outp outn I = {i0}m*pwl(v(outp)-v(outn), -1,0, 1.2,0, 2.0,0.4, 3.6,0.8, 5,0.87, 24,1, 32,1.03)",
       "Rdp outp 0 1meg", "Rdn outn 0 1meg",
       ".model DSCH D(IS=9.9e-8 N=1.343 RS=4 CJO=10p BV=30)"]
    if clamp:
        L += ["Dgn outn 0 DSCH", "Dgp 0 outp DSCH"]
    if oi:
        L += ["Dpo outp inp DSCH", "Dno inn outn DSCH"]
    L += [".options method=gear reltol=1e-3 abstol=1e-10 itl4=50", ".tran 2u 0.3 0 5u UIC",
          ".meas tran outnmax MAX v(outn)", ".meas tran onimin MIN par('v(outn)-v(inn)')",
          ".meas tran outpmin MIN v(outp)", ".meas tran outnend FIND v(outn) AT=0.3", ".meas tran outpend FIND v(outp) AT=0.3", ".end"]
    fn=os.path.join(H,"os.cir"); open(fn,"w").write("\n".join(L))
    o=subprocess.run(["ngspice","-b",fn],capture_output=True,text=True).stdout
    g=lambda k: float(re.search(rf"^{k}\s*=\s*([-\d.eE+]+)",o,re.M).group(1))
    return {k:g(k) for k in ["outnmax","onimin","outpmin","outnend","outpend"]}
for cout,i0,clamp,oi,encut in itertools.product([10,100],[8.7,20],[False,True],[False,True],[True,False]):
    r=run(cout,i0,clamp,oi,encut)
    print(f"Cout {cout:>3} Iop {i0:>4} GNDクランプ {'有' if clamp else '無'} OUT→IN {'有' if oi else '無'} EN{'切' if encut else '残'}: "
          f"max V(−OUT) {r['outnmax']:+.2f} V, min(−OUT − −IN) {r['onimin']:+.2f} V, min V(+OUT) {r['outpmin']:+.2f}, 末 +OUT {r['outpend']:+.2f} / −OUT {r['outnend']:+.2f}")
