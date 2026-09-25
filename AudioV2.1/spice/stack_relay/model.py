#!/usr/bin/env python3
"""縦積み娘の「電源用ラッチングリレー＋直列 R」を ngspice で見る（片レール）。

回路（片レール。-15 V は同じ網で、親の固定負荷だけ違う〔仮定〕）:

  V0(15V) -Ro- -Lo- X -[Blim: RS6 の電流制限〔仮定〕]- P ─┬ Cint 2.2u（RS6 内部〔仮定〕）
                                                           ├ C201/C207 47u（ESR 掃引）
                                                           ├ C503/C504 10u X7R ×50 %
                                                           ├ 親バルク +100u（任意）
                                                           ├ 親の固定負荷（電流源）
                                                           └ hop1 ─ H1 ─ hop2 ─ … ─ Hk（Lhop+Rhop）
  Hk ─ Vsense ─ S_NO（電源用リレーの NO 接点、バウンス付き）─ COM ─ Rser ─ D
  COM ─ S_NC ─ Rdis ─ GND（リセット側。t0 の手前で開く）
  D ─┬ 娘のバルク Cb（ESR Rb）
     ├ 娘のセラミック Ccer（ESR 5 mΩ）
     └ 娘の負荷（電流源。EN 前は TMUX＋ロジック、EN 後は +ch）
"""
from __future__ import annotations

V_NOM = 15.0
CINT = (2.2e-6, 0.010, 1e-9)
C201 = 47e-6
C201_ESL = 10e-9
C503 = (10e-6 * 0.5, 0.005, 1e-9)
CPB_ESL = 10e-9
CER_ESR, CER_ESL = 0.005, 0.5e-9
CB_ESL = 2e-9

# 娘のセラミック（1 枚・片レール・実効値 µF）。基板は 1 種類（TMUX 4 個）
CER = {
    "lo":  4.62,   # CIN 2.2µ×4×30 % + 100n×4 + TMUX(0.1µ×90 %+1µ×30 %)×4
    "mid": 7.12,   # CIN 2.2µ×4×50 % + 100n×4 + TMUX(0.1µ×90 %+1µ×50 %)×4
    "nom": 22.72,  # CIN 10µ×4×50 % + …
    "hi":  40.32,  # CIN 10µ×4×90 % + 100n×4 + TMUX(0.1µ×90 %+1µ×90 %)×4
}
# 娘のバルク（ダンパ）: 実効 µF と ESR
BULK = {
    "none": (0.0, 0.15),
    "b22":  (22.0, 0.15),
    "b45":  (45.0, 0.15),
}
SRC = {  # Ro, Lo, Ilim（Ilim=None は制限なし＝線形）
    "A":    (0.10, 2e-6, None),
    "B":    (0.10, 20e-6, None),
    "C":    (0.75, 20e-6, None),
    "L03":  (0.10, 20e-6, 0.30),   # OLP 150 % = 300 mA で定電流〔仮定〕
    "L06":  (0.10, 20e-6, 0.60),
    "L10":  (0.10, 20e-6, 1.00),
}
I_PARENT = {"+": 0.1018, "-": 0.0538}   # 親の固定（max、INA1650 込み）
I_BOARD_PRE = 4 * 0.48e-3 + 1.0e-3        # EN 前: TMUX×4 IDD max + 検知・デコーダ 1 mA〔仮定〕

T0 = 1.0e-3        # NO が最初に触れる時刻
T_TRANSFER = 0.5e-3  # NC が開いてから NO が触れるまで〔仮定〕

BOUNCE = {  # (開く時刻, 開いている長さ) — T0 からの相対〔仮定〕
    "none": [],
    "b3": [(50e-6, 30e-6), (200e-6, 20e-6), (450e-6, 10e-6)],
}


def sw_pwl(t0: float, bounce: list[tuple[float, float]], tend: float) -> str:
    """NO 接点の制御電圧 PWL（1 = 閉）。"""
    pts = [(0.0, 0.0), (t0 - 1e-9, 0.0), (t0, 1.0)]
    for (to, dt) in bounce:
        a = t0 + to
        pts += [(a - 1e-9, 1.0), (a, 0.0), (a + dt - 1e-9, 0.0), (a + dt, 1.0)]
    pts.append((tend, 1.0))
    return "PWL(" + " ".join(f"{t:.9g} {v:g}" for t, v in pts) + ")"


def netlist(*, rser, bulk, cer, lhop, rhop, hops, src, esr201, cpb, bounce,
            rail="+", rcont=0.05, rdis=1000.0, tend=40e-3, extra_load=None,
            ac=None, ac_node="D") -> str:
    ro, lo, ilim = SRC[src]
    cb, rb = BULK[bulk]
    L = [f"* rser={rser} bulk={bulk} cer={cer} L={lhop} hops={hops} src={src}"]
    if ac == "src":
        L.append(f"V0 V0 0 DC {V_NOM} AC 1")
    else:
        L.append(f"V0 V0 0 DC {V_NOM}")
    if ilim is None:
        L.append(f"Ro V0 R1 {ro}")
        L.append(f"Lo R1 X {lo}")
        L.append("Rlim X P 1e-6")
    else:
        # 電流制限つきの静的な源〔仮定〕: Ro の傾きで Ilim まで。ループの遅れ（Lo）は入れない
        L.append("Rv0 V0 0 1k")
        L.append(f"Blim 0 P I={ilim}*tanh(({V_NOM}-V(P))/({ro}*{ilim}))")
    L.append("Cp0 P 0 0.2u")   # C202 0.1u + C505 100n（ESL 無しでまとめる）
    c, e, l = CINT
    L += [f"Ci P ci1 {c}", f"Rci ci1 ci2 {e}", f"Lci ci2 0 {l}"]
    L += [f"C201 P c2a {C201}", f"R201 c2a c2b {esr201}", f"L201 c2b 0 {C201_ESL}"]
    c, e, l = C503
    L += [f"C503 P c5a {c}", f"R503 c5a c5b {e}", f"L503 c5b 0 {l}"]
    if cpb > 0:
        L += [f"Cpb P cpa {cpb}", "Rpb cpa cpb2 0.1", f"Lpb cpb2 0 {CPB_ESL}"]
    # 親の固定負荷: 2 V より上で定電流、0 V へ向けて消える〔仮定〕
    L.append(f"Bpar P 0 I={I_PARENT[rail]}*tanh(max(V(P),0)/1.0)")
    prev = "P"
    for k in range(1, hops + 1):
        L += [f"Lh{k} {prev} hm{k} {lhop}", f"Rh{k} hm{k} H{k} {rhop}"]
        prev = f"H{k}"
    # 電源用リレー
    L.append(f"Vsen {prev} NOa 0")
    if ac is None:
        L.append(f"Vc_no cno 0 {sw_pwl(T0, BOUNCE[bounce], tend)}")
        L.append(f"Vc_nc cnc 0 PWL(0 1 {T0 - T_TRANSFER - 1e-9:.9g} 1 {T0 - T_TRANSFER:.9g} 0 {tend} 0)")
        L.append(f"S_no NOa COM cno 0 swm")
        L.append(f"S_nc COM NCa cnc 0 swm")
        L.append(f"Rdis NCa 0 {rdis}")
        # バウンスで開く瞬間の誘導電圧のクランプ〔仮定〕: 両端 20 V（閉じる前の 15 V より上）で導通
        L.append("Darc NOa arc1 darc")
        L.append("Varc arc1 COM DC 20")
        L.append(".model darc d(is=1e-12 n=1)")
        L.append(f".model swm sw vt=0.5 vh=0.01 ron={rcont} roff=1e9")
    else:
        L.append(f"Rno NOa COM {rcont}")
    L.append(f"Rser COM D {rser}")
    if cb > 0:
        L += [f"Cb D cba {cb*1e-6}", f"Rb cba cbb {rb}", f"Lb cbb 0 {CB_ESL}"]
    L += [f"Cc D cca {CER[cer]*1e-6}", f"Rc cca ccb {CER_ESR}", f"Lc ccb 0 {CER_ESL}"]
    if ac is None:
        # 負荷は抵抗で（0 V で電流を流さないように）: 15 V で I_BOARD_PRE
        L.append(f"Rld D 0 {V_NOM / I_BOARD_PRE}")
        if extra_load:
            L.append(f"Iex D 0 {extra_load}")
    else:
        L.append(f"Rld D 0 {V_NOM / 0.024}")   # 1 ch ON の最大（線形化の負荷）
        if ac == "z":
            L.append(f"Iinj 0 {ac_node} DC 0 AC 1")
    return "\n".join(L) + "\n"
