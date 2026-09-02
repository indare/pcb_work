#!/usr/bin/env python3
"""入力ブロードキャスト構成の3案（A/B/C）を比較する。

## 3案

    A案（各DUT個別バイアス、PT2314 直結）
        PT2314 ─┬─[C]─┬─Rb─GND
                │     └─ DUT1 +in            （×10）

    B案（共通バイアス、PT2314 直結）
        PT2314 ─[C]─┬─Rb_c─GND
                    ├─[Rs]─ DUT1 +in         （×10）

    C案（共通バッファ + 各DUT個別バイアス）
        PT2314 ─[共通 L/R バッファ]─┬─[C]─┬─Rb─GND
                                     │     └─ DUT1 +in   （×10）

PT2314 の特性規定は RL=10kΩ なので、直結する A/B案は「10本並列で 10kΩ 以上」の制約を
受ける（A案 Rb=100k、B案 Rb_c=10k）。C案はバッファが受けるので Rb を小さくできる。

## 見るもの

1. 前段（PT2314 またはバッファ）が見る負荷
2. DUT + 入力の**交流**雑音（前段の出力インピーダンスを含む Thevenin。
   開放端 sqrt(4kTR) で評価してはいけない）
3. **直流**オフセット。結合Cが直流を切るので DC 経路は Rb だけ。したがって
   オフセットは Rb に比例する（交流雑音と違って前段の低インピーダンスに助けられない）
   - 入力バイアス電流 Ib × Rb
   - **結合コンデンサの漏れ電流 × Rb**（電解なら µA オーダーになりうる）
4. 必要な結合容量とフィルム化の可否
"""
from __future__ import annotations

import numpy as np

K = 1.380649e-23
T = 298.0
RO_PT2314 = 1.9        # PT2314 Audio Output Resistance typ（データシート実測値）
RO_BUF = 0.1           # 一般的なラインバッファの閉ループ出力インピーダンス（仮定）
V_DC = 4.5             # PT2314 出力の直流電位（データシート DC Voltage Level typ）
NCH = 10
F3DB_TARGET = 2.0      # 結合C設計の目標 -3dB 周波数 [Hz]

# 手持ちオペアンプの入力バイアス電流（Audio/datasheets/opamps/ の各データシート）
IB = {
    "LT1364": (600e-9, 2000e-9),
    "NE5532": (200e-9, 800e-9),
    "MUSES02": (100e-9, 500e-9),
    "OPA1612": (60e-9, 250e-9),
    "FET入力 (OPA1656等)": (1e-12, 10e-12),
}

# 結合コンデンサの漏れ電流
#   電解: 一般的なスペックは I <= 0.01*C*V または 3µA の大きい方（定格電圧・2分後）。
#         実効値は印加 4.5V / 定格 25-50V なら桁で小さいが、設計はスペック上限で見る。
#   フィルム: 絶縁抵抗 >= 10000 MΩ·µF 級。4.5V 印加なら pA〜nA。
def leak_elec(c_uf: float, v_rated: float = 25.0) -> float:
    return max(0.01 * c_uf * v_rated, 3.0) * 1e-6

def leak_film(c_uf: float) -> float:
    ir = 10_000e6 / max(c_uf, 1e-9)      # ohm
    return V_DC / ir


def cap_for(rb: float) -> float:
    """目標 -3dB を満たす結合容量 [µF]。"""
    return 1e6 / (2 * np.pi * F3DB_TARGET * rb)


def ac_noise(f: float, rshunt: float, ro: float, rseries: float = 0.0) -> float:
    """DUT + 入力から見た交流雑音電圧密度 [V/rtHz]（Nyquist: 4kT*Re(Z)）。"""
    c = cap_for(rshunt) * 1e-6
    z1 = ro + 1 / (1j * 2 * np.pi * f * c)
    zn = (z1 * rshunt) / (z1 + rshunt)
    return float(np.sqrt(4 * K * T * max(zn.real + rseries, 0.0)))


PLANS = {
    # name: (Rb per DUT, 前段Ro, 前段が見る負荷, 直列Rs, 部品点数, 独立性)
    "A案 (個別 Rb=100k)": (100e3, RO_PT2314, 100e3 / NCH, 0.0, "C×10 + R×10 = 20", "独立"),
    "B案 (共通 Rb=10k)": (10e3, RO_PT2314, 10e3, 100.0, "C×1 + R×1 + Rs×10 = 12", "全ch連動"),
    "C案 (buf + Rb=22k)": (22e3, RO_BUF, 22e3 / NCH, 0.0, "buf + C×10 + R×10 = 21+", "独立"),
    "C案 (buf + Rb=10k)": (10e3, RO_BUF, 10e3 / NCH, 0.0, "buf + C×10 + R×10 = 21+", "独立"),
}


def main() -> None:
    print("=== 1. 前段が見る負荷 / 必要な結合容量 ===")
    print(f"  （目標 -3dB = {F3DB_TARGET:.0f} Hz）\n")
    print(f"  {'案':22s}{'Rb':>9s}{'前段負荷':>11s}{'必要C':>10s}  フィルム化")
    for name, (rb, ro, load, rs, _, _) in PLANS.items():
        c = cap_for(rb)
        film = "現実的（1µF級）" if c <= 1.5 else ("やや大きい" if c <= 4 else "非現実的→電解")
        print(f"  {name:22s}{rb/1e3:7.0f}k{load/1e3:10.1f}k{c:9.2f}µF  {film}")
    print("\n  A案の Rb=100k は PT2314 の 10kΩ 制約から来る値だが、その副産物として")
    print("  必要な結合容量が 0.8µF まで下がり、**フィルムコンデンサが使える**。")

    print("\n=== 2. DUT + 入力の交流雑音 [nV/rtHz] ===")
    print(f"  {'案':22s}" + "".join(f"{f'{f:.0f}Hz':>11s}" for f in (20, 1e3, 20e3)))
    for name, (rb, ro, _, rs, _, _) in PLANS.items():
        cells = "".join(f"{ac_noise(f, rb, ro, rs)*1e9:11.3f}" for f in (20.0, 1e3, 20e3))
        print(f"  {name:22s}{cells}")
    print("  ※ どの案も前段の出力抵抗が支配的。B案だけ直列 Rs 自身の熱雑音が乗る。")

    print("\n=== 3. 直流オフセット [mV]（Rb に比例。交流と違い前段に助けられない） ===")
    print("\n  3-1. 入力バイアス電流 Ib × Rb")
    print(f"  {'石':22s}" + "".join(f"{n.split(' ')[0]:>17s}" for n in PLANS))
    for nm, (typ, mx) in IB.items():
        cells = "".join(f"{typ*rb*1e3:8.1f}/{mx*rb*1e3:<8.1f}" for (rb, *_ ) in PLANS.values())
        print(f"  {nm:22s}{cells}")
    print("                        （typ / max）")

    print("\n  3-2. 結合コンデンサの漏れ電流 × Rb")
    print(f"  {'案':22s}{'C':>9s}{'電解(スペック上限)':>20s}{'フィルム':>14s}")
    for name, (rb, *_ ) in PLANS.items():
        c = cap_for(rb)
        e = leak_elec(c) * rb * 1e3
        f_ = leak_film(c) * rb * 1e3
        print(f"  {name:22s}{c:8.2f}µF{e:18.1f}mV{f_:12.4f}mV")
    print("  → **A案は 100k が効いて電解なら最大 300mV。ただし必要Cが 0.8µF なので")
    print("     フィルムにでき、その場合 0.0005mV まで落ちて問題が消える。**")
    print("     C案は Rb が小さいぶん電解のままでも 30-66mV に収まるが、")
    print("     必要Cが 7-16µF でフィルムは非現実的なので電解確定。")

    print("\n=== 4. まとめ ===")
    print(f"  {'案':22s}{'部品':>26s}{'独立性':>12s}")
    for name, (_, _, _, _, parts, indep) in PLANS.items():
        print(f"  {name:22s}{parts:>26s}{indep:>12s}")
    print("""
  A案 + フィルム結合C:
    交流雑音・漏れ電流とも最小。ch 独立。前段の追加なし。
    代償は Ib×100k の直流オフセット（LT1364 max で 200mV）。
    ただし出力は 47Ω+2.2µF で AC 結合されるので後段には出ない。
  B案:
    部品は最小だが、共通ノードの直流が「刺さっている全10石の Ib の和」で決まり、
    1石差し替えると全chが動く。比較装置としては筋が悪い。
  C案:
    Rb を小さくできるので Ib・漏れ電流の影響が 1/5〜1/10。ch 独立も保てる。
    代償は (a) バッファ自身の歪み・雑音が全DUTの前に入る (b) 電解C確定
    (c) 部品と電源が増える。
    **(a) は全chに共通なので「比較」には効かないが、DIRECT 経路で
    「オペアンプ単体の絶対THD」を測る用途では新しい床になる。**
    その用途を残すなら DIRECT はバッファも迂回する必要がある。""")


if __name__ == "__main__":
    main()
