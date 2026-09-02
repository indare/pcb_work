#!/usr/bin/env python3
"""入力ブロードキャスト構成の2案（A: 各DUT個別バイアス / B: 共通バイアス）を比較する。

## 2案

    A案（個別）                          B案（共通）
    TONE ─┬─[C]─┬─Rb─GND               TONE ─[C]─┬─Rb_c─GND
          │     └─ DUT1 +in                       ├─[Rs]─ DUT1 +in
          ├─[C]─┬─Rb─GND                          ├─[Rs]─ DUT2 +in
          │     └─ DUT2 +in                       ⋮
          ⋮                                       └─[Rs]─ DUT10 +in

PT2314 が見る負荷を同じ（>=10kΩ、データシートの特性規定条件）に揃えると、
A案は Rb=100k×10並列=10k、B案は Rb_c=10k 単体になる。

## 見るもの

1. PT2314 が見る負荷
2. DUT + 入力の雑音（PT2314 の出力インピーダンス 1.9Ω を含む Thevenin で計算。
   開放端 sqrt(4kTR) で評価してはいけない）
3. 入力バイアス電流による DC オフセット（バイポーラ入力石で効く）
4. DUT 間の相互作用（ある石を差し替えたとき他chの動作点が動くか）
"""
from __future__ import annotations

import numpy as np

K = 1.380649e-23
T = 298.0
RO_PT2314 = 1.9        # PT2314 Audio Output Resistance typ (データシート実測値)
CC = 10e-6 + 100e-9    # 結合コンデンサ 10uF || 100nF
NCH = 10

# 手持ちオペアンプの入力バイアス電流（各データシートから、Audio/datasheets/opamps/）
IB = {
    "NE5532": (200e-9, 800e-9),
    "OPA1612": (60e-9, 250e-9),
    "MUSES02": (100e-9, 500e-9),
    "LT1364": (600e-9, 2000e-9),
    "OPA1656 等 FET入力": (1e-12, 10e-12),
}


def node_noise(f: float, rshunt: float, rseries: float = 0.0) -> float:
    """DUT + 入力から見た雑音電圧密度 [V/rtHz]。

    受動網の熱雑音は 4kT*Re(Z) （Nyquist）。PT2314 の出力抵抗と結合Cの直列が
    Rshunt と並列になり、さらに直列抵抗 Rseries が加わる。
    """
    w = 2 * np.pi * f
    z1 = RO_PT2314 + 1 / (1j * w * CC)
    znode = (z1 * rshunt) / (z1 + rshunt)
    return float(np.sqrt(4 * K * T * max(znode.real + rseries, 0.0)))


def main() -> None:
    rb_a = 100e3          # A案: 各chのバイアス抵抗
    rb_b = 10e3           # B案: 共通バイアス抵抗
    rs_list = (10.0, 100.0, 1e3)   # B案の個別直列抵抗の候補

    print("=== 1. PT2314 が見る負荷（データシート特性規定は RL=10kΩ） ===")
    print(f"  A案 Rb={rb_a/1e3:.0f}kΩ ×{NCH}並列  -> {rb_a/NCH/1e3:.1f} kΩ")
    print(f"  B案 Rb_c={rb_b/1e3:.0f}kΩ 単体      -> {rb_b/1e3:.1f} kΩ")

    print("\n=== 2. DUT + 入力の雑音密度 [nV/rtHz]（PT2314 出力 1.9Ω 込みの Thevenin） ===")
    print(f"  {'周波数':>8s}{'A案':>10s}" + "".join(f"{'B案 Rs=' + str(int(r)):>13s}" for r in rs_list))
    for f in (20.0, 100.0, 1e3, 20e3):
        cells = [f"{node_noise(f, rb_a)*1e9:9.3f}"]
        cells += [f"{node_noise(f, rb_b, r)*1e9:13.3f}" for r in rs_list]
        print(f"  {f:7.0f}Hz" + "".join(cells))
    print("  ※ A案はどの周波数でも PT2314 の 1.9Ω が支配的。")
    print("     B案は直列 Rs 自身の熱雑音が上乗せされるので Rs は小さいほどよい。")

    print("\n=== 3. 入力バイアス電流による DC オフセット [mV] ===")
    print("  A案: 自分の Ib だけが自分の Rb を流れる（他chと独立）")
    print("  B案: 全10chの Ib の合計が共通 Rb_c を流れる（=他chの石に依存する）")
    print(f"\n  {'石':22s}{'A案 typ/max':>16s}{'B案 全ch同一種 typ/max':>26s}")
    for name, (typ, mx) in IB.items():
        a_typ, a_max = typ * rb_a * 1e3, mx * rb_a * 1e3
        b_typ, b_max = NCH * typ * rb_b * 1e3, NCH * mx * rb_b * 1e3
        print(f"  {name:22s}{a_typ:7.1f}/{a_max:7.1f}{b_typ:15.1f}/{b_max:7.1f}")

    print("\n  B案の混載ケース（比較試聴なので実際はこれ）:")
    mix = ("LT1364", "NE5532", "MUSES02", "OPA1612") + ("OPA1656 等 FET入力",) * 6
    tot_typ = sum(IB[m][0] for m in mix)
    tot_max = sum(IB[m][1] for m in mix)
    print(f"    LT1364+NE5532+MUSES02+OPA1612+FET×6 -> "
          f"Σ Ib = {tot_typ*1e9:.0f}nA typ / {tot_max*1e9:.0f}nA max")
    print(f"    共通ノードの DC = {tot_typ*rb_b*1e3:.1f} mV typ / {tot_max*rb_b*1e3:.1f} mV max"
          f"  （全10chが同じこの値を共有する）")
    d = IB["LT1364"][0] * rb_b * 1e3
    print(f"    LT1364 を1個抜くと全chが {d:.1f} mV 動く（A案なら動くのはその ch だけ）")

    print("\n=== 4. まとめ ===")
    print("  A案: 部品 20点（C×10 + R×10）。各chが電気的に独立。")
    print("       差し替えても他chの動作点は不変。")
    print("  B案: 部品 12点（C×1 + R_c×1 + Rs×10）。フィルムC×9個分の面積が浮く。")
    print("       ただし共通ノードの DC が「刺さっている全10石の Ib の和」で決まるため、")
    print("       1個差し替えると全chの動作点が動く。比較試聴装置としては筋が悪い。")
    print("  → 出力は 47Ω+2.2µF で AC 結合されるので DC 自体の実害は無いが、")
    print("     『他chに影響されない』ことが装置の目的そのものなので A案を推す。")


if __name__ == "__main__":
    main()
