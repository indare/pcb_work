#!/usr/bin/env python3
"""ch LDO（片レール、正側で代表）の電源断で OUT−IN がどこまで開くか。ngspice の過渡。

モデル（すべて〔仮定〕の置き方、値は ch_ldo_reverse.md の表）:
  IN: 娘の切られたレール（4 ch の CIN＋TMUX のデカップの実効 C_IN）。t=0 に事象
  LDO: IN→OUT の片方向の電流源。OUT を min(12, IN−VDO) まで押し上げるだけ（吸い込まない）。
       EN: IN < 10.5 V（RAIL_OK の立ち下がり）で切れる／切れない を選ぶ。IN < 3 V（VIN min）で止まる
  OUT: C_OUT（実効）、帰還の分圧 Rdiv、ソケットの石（NJM5532 の Supply Current vs Supply Voltage の形を正規化）
  石の電流 g(V): V≥2.5 V で 0.87〜1、1.8 V 0.8、1.0 V 0.4（DS の破線の端）、0.6 V 以下 0〔外挿の仮定〕
  ショットキー OUT→IN（BAT54、DS p2 の max 点に合わせた N/IS/RS）を付ける／付けない
  LDO の中の寄生の経路は DS に無いので既定は「無し」（OUT−IN の上界）。--para で Si 接合 1 個を足す
"""
import itertools, subprocess, re, sys, os, math

HERE = os.path.dirname(os.path.abspath(__file__))

# BAT54 25°C: max 点 0.24V@0.1mA, 0.32@1mA, 0.40@10mA, 0.8@100mA → N·Vt=0.0347, IS=9.9e-8, RS≈4
BAT54_MAX = ".model DSCH D(IS=9.9e-8 N=1.343 RS=4 CJO=10p BV=30)"
# typ（Figure 1 目読み 25°C: 1mA≈0.25V, 10mA≈0.33V, 100mA≈0.5V）
BAT54_TYP = ".model DSCH D(IS=7.5e-7 N=1.343 RS=1.2 CJO=10p BV=30)"
PARA = ".model DPARA D(IS=1e-14 N=1 RS=2)"

def netlist(case):
    c = dict(case)
    L = [f"* {c}"]
    L.append(f".param CIN={c['cin']}u COUT={c['cout']}u I0={c['iop']}m RDIV={c['rdiv']}")
    L.append("Cin in 0 {CIN} IC=%g" % c['vin0'])
    L.append("Cout out 0 {COUT} IC=12")
    ev = c['event']
    if ev == 'prst':          # 電源リレーのリセット: COM が NC 側へ → 2.2 kΩ
        L.append("Rdis in 0 2.2k")
    elif ev.startswith('ramp'):  # 主電源断: 親が r V/ms で落ちる（接点はセットのまま、22 Ω 越し）
        r = float(ev[4:])
        t0 = c['vin0'] / r * 1e-3
        L.append(f"Vp p 0 PWL(0 {c['vin0']} {t0} 0 1 0)")
        L.append("Rser p in 22")
    elif ev == 'pshort':      # 親の +15 V が 0 V へ（22 Ω 越し）
        L.append("Vp p 0 0")
        L.append("Rser p in 22")
    elif ev == 'dshort':      # 娘のレールそのものの短絡
        L.append("Rsh in 0 0.05")
    # 娘の雑負荷（TMUX×4＋ロジック 2.9 mA、3 V 以下で比例）
    L.append("Bmisc in 0 I = 2.9m*min(1, max(v(in),0)/3)")
    # LDO（片方向）。EN
    ensig = "1" if not c['encut'] else "0.5*(1+tanh((v(in)-10.5)/0.05))"
    L.append("Bldo in out I = %s * 0.5*(1+tanh((v(in)-3)/0.05)) * min(0.5, max(0, (min(12, v(in)-0.07) - v(out))/0.5))" % ensig)
    # 石・分圧
    if c['iop'] > 0:
        L.append("Bop out 0 I = {I0}*pwl(v(out), -1,0, 0.6,0, 1.0,0.4, 1.8,0.8, 2.5,0.87, 12,1, 16,1.03)")
    L.append("Rdiv out 0 {RDIV}")
    if c.get('rbleed'):
        L.append(f"Rbl out 0 {c['rbleed']}")
    if c['schottky']:
        L.append(BAT54_MAX if c['schottky'] == 'max' else BAT54_TYP)
        L.append("Dsch out in DSCH")
    if c.get('para'):
        L.append(PARA)
        L.append("Dpar out in DPARA")
    tstop = c.get('tstop', 0.6)
    L.append(".options method=gear reltol=1e-3 abstol=1e-10 itl4=50")
    L.append(f".tran 2u {tstop} 0 5u UIC")
    L.append(".meas tran dmax MAX par('v(out)-v(in)')")
    L.append(".meas tran tdmax WHEN par('v(out)-v(in)')=0.3 CROSS=1")
    L.append(".meas tran outend FIND v(out) AT=%g" % tstop)
    L.append(".meas tran inend FIND v(in) AT=%g" % tstop)
    if c['schottky']:
        L.append(".meas tran idmax MAX i(Vsense)")
    L.append(".end")
    s = "\n".join(L)
    if c['schottky']:
        s = s.replace("Dsch out in DSCH", "Vsense out outd 0\nDsch outd in DSCH")
    return s

def run(case):
    s = netlist(case)
    fn = os.path.join(HERE, "run.cir")
    open(fn, "w").write(s)
    out = subprocess.run(["ngspice", "-b", fn], capture_output=True, text=True).stdout
    r = {}
    for k in ["dmax", "tdmax", "outend", "inend", "idmax"]:
        m = re.search(rf"^{k}\s*=\s*([-\d.eE+]+)", out, re.M)
        r[k] = float(m.group(1)) if m else None
    if r["dmax"] is None:
        sys.stderr.write(out[-2000:])
    return r

def fmt(case, r):
    if r['dmax'] is None: return f"{case} → 失敗"
    t = "—" if r['tdmax'] is None else f"{r['tdmax']*1e3:.1f} ms"
    idm = "" if r.get('idmax') is None else f" Id,max {r['idmax']*1e3:.1f} mA"
    return (f"{case['event']:>9} Cin{case['cin']:>5} Cout{case['cout']:>4} Iop{case['iop']:>3}mA Rdiv{case['rdiv']:>8} "
            f"EN{'切' if case['encut'] else '残'} D:{case['schottky'] or '-':>3}{' para' if case.get('para') else ''}"
            f"{' Rbl'+str(case['rbleed']) if case.get('rbleed') else ''}"
            f" → max(OUT−IN) {r['dmax']:+.2f} V, 0.3 V 越え {t}, 末 OUT {r['outend']:.2f} / IN {r['inend']:.2f}{idm}")

if __name__ == "__main__":
    base = dict(vin0=14.1, cin=22.7, cout=10, iop=8.7, rdiv=1e6, encut=True, schottky=None, event='prst')
    groups = {}
    # 1. ふつうの切替（PRST）: C_IN × C_OUT × 石
    g = []
    for cin, cout, iop in itertools.product([14, 22.7, 40.3], [5, 10, 22, 47, 100], [0, 6, 8.7, 20]):
        g.append(dict(base, cin=cin, cout=cout, iop=iop))
    groups['1_prst'] = g
    # EN を切らない（RAIL_OK が遅れた）比較
    groups['1_prst_ennot'] = [dict(base, encut=False, cin=cin, cout=cout, iop=iop)
                              for cin, cout, iop in itertools.product([22.7], [10, 100], [0, 8.7])]
    # 分圧 100 kΩ
    groups['1_prst_rdiv100k'] = [dict(base, rdiv=1e5, cin=cin, cout=cout, iop=0)
                                 for cin, cout in itertools.product([14, 22.7, 40.3], [10, 100])]
    # 2. 主電源断（0.26 / 0.45 V/ms）
    groups['2_ramp'] = [dict(base, event=f"ramp{r}", cin=22.7, cout=cout, iop=iop, tstop=0.2)
                        for r, cout, iop in itertools.product([0.26, 0.45], [10, 100], [0, 8.7, 20])]
    # 3. 親の短絡・娘の短絡
    groups['3_short'] = [dict(base, event=ev, cin=cin, cout=cout, iop=iop, tstop=0.05)
                         for ev, cin, cout, iop in itertools.product(['pshort', 'dshort'], [14, 40.3], [10, 100], [0, 8.7])]
    # 手当て: ショットキー（max/typ）・寄生・放電抵抗
    t = []
    for sch in ['max', 'typ']:
        for ev, cout, iop in itertools.product(['prst', 'ramp0.26', 'pshort', 'dshort'], [10, 100], [0, 8.7]):
            ts = 0.6 if ev == 'prst' else (0.2 if ev.startswith('ramp') else 0.05)
            t.append(dict(base, schottky=sch, event=ev, cin=14, cout=cout, iop=iop, tstop=ts))
    groups['T_schottky'] = t
    groups['T_para'] = [dict(base, para=True, event=ev, cin=14, cout=cout, iop=0, tstop=(0.6 if ev == 'prst' else 0.05))
                        for ev, cout in itertools.product(['prst', 'dshort'], [10, 100])]
    groups['T_bleed'] = [dict(base, rbleed=rb, cin=cin, cout=cout, iop=0)
                         for rb, cin, cout in itertools.product([2.2e3, 4.7e3, 10e3], [14, 40.3], [10, 22])]
    sel = sys.argv[1:] or list(groups)
    for k in sel:
        print(f"== {k}")
        for case in groups[k]:
            print("  " + fmt(case, run(case)), flush=True)
