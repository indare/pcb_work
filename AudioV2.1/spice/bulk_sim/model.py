#!/usr/bin/env python3
"""±15 V 配電（片レール）の ngspice モデル生成。v2.1 の 3 案を比べる。

片レール（+15 V）だけを組む。−15 V は同じ網（TPS7A30 の入力も同じ値の CIN）と見なす〔仮定〕。
素子値の出典は bulk_parent_sim.md の「モデルの素子」表に書く。ここでは数値と記号だけ。

回路（chain = 縦積み。親スロット 1 個 → 娘1 → 娘2 …）:

  V0(15V) -Ro- -Lo- P ─┬ Cint(RS6 内部, 仮定)
                       ├ C201 47u (ESR 仮定)
                       ├ C503 HP 10u X7R (derate)
                       ├ Cpb 親バルク（案2/3）
                       └ Lhop1-Rhop1 ─ H1 ─ Lhop2-Rhop2 ─ H2 ─ …
  Hk ─ Rser_k(案3, それ以外 0.1 mΩ) ─ Dk ─┬ Cceramic_k（LDO CIN×4＋100n×4＋TMUX 0.1u/1u×4）
                                          ├ Cd-Rd（案1 の娘ダンパ）
                                          └ 負荷（電流源）
  star = 各娘が P から自分の Lhop-Rhop で直接（比較用）
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict


# ---- 固定の素子（仮定を含む。md の表と一致させる） ----
V_NOM = 15.0
CINT = (2.2e-6, 0.010, 1e-9)       # RS6 内部の出力容量〔仮定〕: C, ESR, ESL
C201 = 47e-6                       # 回路図 C201 "47u" CP_Radial_D8.0mm（ESR は掃引）
C201_ESL = 10e-9
C503 = (10e-6 * 0.5, 0.005, 1e-9)  # 回路図 C503 "10uF 25V X7R"（HP バッファ）。DC バイアスで 50 %〔仮定〕
CPB_ESL = 10e-9
CER_ESR, CER_ESL = 0.005, 0.5e-9   # 娘の MLCC 群をまとめた ESR/ESL〔仮定〕
CD_ESL = 2e-9                      # 案1 ダンパ（MLCC＋チップ R）の ESL〔仮定〕
RSER_ZERO = 1e-4

# 娘のセラミック（1 枚あたり・片レール、実効値）: (名前, µF, 内訳)
CER_CORNERS = {
    "lo":  (3.00, "Relay 娘・CIN 2.2µF×4 を DC バイアスで 30 %＋100nF×4（TMUX 無し）"),
    "mid": (7.12, "Switch 娘・CIN 2.2µF×4×50 %＋100nF×4＋TMUX(0.1µF×90 %＋1µF×50 %)×4"),
    "nom": (22.72, "Switch 娘・CIN 10µF×4×50 %＋100nF×4＋TMUX(0.1µF×90 %＋1µF×50 %)×4"),
    "hi":  (40.32, "Switch 娘・CIN 10µF×4×90 %＋100nF×4＋TMUX(0.1µF×90 %＋1µF×90 %)×4"),
}
SRC_CORNERS = {           # RS6 の閉ループ出力インピーダンスの近似 Ro + sLo〔仮定〕
    "A": (0.10, 2e-6),
    "B": (0.10, 20e-6),
    "C": (0.75, 20e-6),   # 0.75 Ω ＝ 負荷レギュレーション 1.0 % typ（0〜100 %）→ 0.15 V / 0.2 A
}

# 負荷（mA、片レール +15 V、max 積み）
I_ON = 20.0 + 1.0 + 4 * 0.48       # 在庫の最悪ソケット 20 ＋ ch LDO 自己消費 1.0 ＋ TMUX×4 IDD max
I_OFF = 4 * 0.48 + 4 * 0.003       # TMUX×4 ＋ 停止中 LDO 3 µA×4
I_PARENT = 89.84 + 12.0            # 親の固定（rail_budget 固定側 max − U311/U312）＋ INA1650 max


@dataclass
class Var:
    plan: str            # "1" / "2" / "3"
    n: int               # 娘の枚数
    lhop: float
    rhop: float
    cer: str
    src: str
    esr201: float
    cpb: float = 0.0     # 親に足すバルク [F]（案2/3）
    esrpb: float = 0.1
    cd: float = 0.0      # 案1 の娘ダンパ C [F]
    rd: float = 0.0
    rser: float = RSER_ZERO
    topo: str = "chain"

    def key(self) -> tuple:
        return tuple(asdict(self).values())


def emit(v: Var, pfx: str, *, inject_k: int | None, src_ac: bool,
         loads: dict[int, str] | None = None, parent_load: str | None = None,
         hotplug_k: int | None = None, hp_ron: float = 5e-3) -> list[str]:
    """1 コピー分の素子行。ノード名は pfx で分ける（コピー同士は GND 以外つながらない）。

    loads: 娘番号 → 電流源の値の文字列（"DC 0.0229" や "PWL(...)"）。無い娘は I_OFF
    hotplug_k: その娘の hop の手前にスイッチ（t=10 µs で閉じる）
    """
    L = []
    n = lambda s: f"{pfx}_{s}"  # noqa: E731
    ro, lo = SRC_CORNERS[v.src]
    ac = " AC 1" if src_ac else ""
    L += [f"V0{pfx} {n('src')} 0 DC {V_NOM}{ac}",
          f"Ro{pfx} {n('src')} {n('s1')} {ro}",
          f"Lo{pfx} {n('s1')} {n('P')} {lo}"]
    P = n("P")

    def cap(name, node, c, esr, esl, ic=None):
        a, b = n(name + "a"), n(name + "b")
        return [f"C{name}{pfx} {node} {a} {c}" + (f" IC={ic}" if ic is not None else ""),
                f"R{name}{pfx} {a} {b} {esr}",
                f"L{name}{pfx} {b} 0 {esl}"]

    L += cap("int", P, *CINT)
    L += cap("201", P, C201, v.esr201, C201_ESL)
    L += cap("503", P, *C503)
    if v.cpb > 0:
        L += cap("pb", P, v.cpb, v.esrpb, CPB_ESL)
    if parent_load:
        L.append(f"Ipar{pfx} {P} 0 {parent_load}")
    else:
        L.append(f"Ipar{pfx} {P} 0 DC {I_PARENT * 1e-3}")

    prev = P
    for k in range(1, v.n + 1):
        H = n(f"H{k}")
        up = prev if v.topo == "chain" else P
        if hotplug_k == k:
            sw_in = n(f"sw{k}")
            L += [f"S{k}{pfx} {up} {sw_in} {n('ctl')} 0 SWMOD",
                  f"Vctl{pfx} {n('ctl')} 0 PULSE(0 1 10u 10n 10n 1 2)"]
            up = sw_in
        L += [f"Lh{k}{pfx} {up} {n(f'h{k}m')} {v.lhop}",
              f"Rh{k}{pfx} {n(f'h{k}m')} {H} {v.rhop}"]
        D = n(f"D{k}")
        L.append(f"Rs{k}{pfx} {H} {D} {v.rser}")
        ccer = CER_CORNERS[v.cer][0] * 1e-6
        ic = 0 if hotplug_k == k else None
        L += cap(f"c{k}", D, ccer, CER_ESR, CER_ESL, ic)
        if v.cd > 0:
            L += cap(f"d{k}", D, v.cd, v.rd, CD_ESL, ic)
        if hotplug_k == k:
            # 挿す娘は ch がすべて OFF（TMUX の IDD だけ）→ 抵抗で表す（浮きノードを作らない）
            L.append(f"Rld{k}{pfx} {D} 0 {V_NOM / (I_OFF * 1e-3):.1f}")
            L.append(f"Rbl{k}{pfx} {H} 0 1e6")
        else:
            val = (loads or {}).get(k, f"DC {I_OFF * 1e-3}")
            L.append(f"Ild{k}{pfx} {D} 0 {val}")
        if inject_k == k:
            L.append(f"Iinj{pfx} {D} 0 DC 0 AC 1")
        prev = H
    return L
