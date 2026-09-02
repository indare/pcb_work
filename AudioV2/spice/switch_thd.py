#!/usr/bin/env python3
"""アナログスイッチ（DG412 / TMUX7612）が AmpBank の信号経路に足す THD を数値で出す。

## なぜこれが要るか

`ΔRon / R_load` は **THD ではない**。あれは非線形分圧の「大きさ」の目安で、
実際の THD は `Ron(V)` 曲線の**形**で決まる（直線的に変化すれば主に2次、
左右対称な U 字なら3次が強い）。同じ ΔRon でも THD は桁で違いうる。
TI 自身も MUX の THD をこの「信号振幅による非線形分圧」として説明している
（SCDA058）。なので曲線を数値で持ち、時系列を解いて FFT する。

## Ron(V) の出どころ

データシートのグラフを **PDF のベクタパスから直接抽出**した（目視ではない）。
  data/dg412_ron_curve.json     Vishay DG411/412/413 (61564) Fig. On-Resistance vs VD、±15V 電源
  data/tmux7612_ron_curve.json  TI TMUX7612 Figure 5-4、±15V 電源

**⚠ グラフから mΩ 精度を主張しないこと。** Figure 5-4 は縦軸が Ω 単位なので、
ベクタ座標が精密でも元グラフが mΩ を表現していない。TMUX7612 の平坦領域は
仕様表の `RON flatness = 0.0003 Ω typ` が主根拠で、抽出値（約 0.001 Ω）は
グラフの分解能限界。よってこのスクリプトの平坦領域の結果は **THD の上限**として読む。
逆にレール近傍（±11V 超）は曲線が目に見えて立ち上がるので抽出値が主根拠になる。

## 回路モデル

    Vsrc ─[SW1 Ron(V)]─┬─ Rbias ─ GND        入力側（信号 = 出力の 1/2）
                        └─ OpAmp(×2) ─ Riso ─[SW2 Ron(V)]─┬─ RL   出力側
                                                            └ (A50k + 後段)

入力と出力の両方にスイッチがあるので、**通しで一度に解いて FFT する**のが本番判定。
片側ずつの数字は診断用。入力側で出た高調波はオペアンプで2倍され、
その後さらに出力側スイッチの非線形性を通る。

## 補間

cubic spline は点間で勝手にオーバーシュートして、存在しない曲率＝偽の THD を作る。
**linear と PCHIP（単調保存）** の2種で回して差を見る（`--interp both`）。

使い方:
  python3 AudioV2/spice/switch_thd.py                    # 本番判定（通し）
  python3 AudioV2/spice/switch_thd.py --stage input      # 入力側だけ
  python3 AudioV2/spice/switch_thd.py --vout 7.07        # 出力振幅を変えて
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator

DATA = Path(__file__).resolve().parent / "data"
GAIN = 2.0            # AmpBank 1ch のゲイン（20k/20k、DECISIONS.md §8）
R_ISO = 47.0          # 出力直列抵抗 R602/R607
F0 = 1000.0           # 試験周波数


def load_ron(part: str, interp: str):
    pts = json.load(open(DATA / f"{part}_ron_curve.json"))
    v = np.array([p[0] for p in pts])
    r = np.array([p[1] for p in pts])
    o = np.argsort(v)
    v, r = v[o], r[o]
    # 同一 x の重複を平均（ベクタ抽出でノード共有があるため）
    uv, idx = np.unique(np.round(v, 4), return_inverse=True)
    ur = np.array([r[idx == k].mean() for k in range(len(uv))])
    if interp == "pchip":
        f = PchipInterpolator(uv, ur, extrapolate=False)
        return lambda x: np.nan_to_num(f(np.clip(x, uv[0], uv[-1])), nan=ur[-1])
    return lambda x: np.interp(np.clip(x, uv[0], uv[-1]), uv, ur)


def divider(vin: np.ndarray, ron, rload: float, rseries: float = 0.0,
            iters: int = 60) -> np.ndarray:
    """Vout = Vin * RL / (RL + Rseries + Ron(Vout)) を反復で解く。

    Ron を決める端子電圧は出力側ノード（= スイッチの drain/source 電位）。
    Ron << RL なので数回で収束するが、余裕を見て回す。
    """
    vout = vin * rload / (rload + rseries + ron(vin))
    for _ in range(iters):
        new = vin * rload / (rload + rseries + ron(vout))
        if np.max(np.abs(new - vout)) < 1e-12:
            vout = new
            break
        vout = new
    return vout


def harmonics(sig: np.ndarray, fs: float, f0: float, n_harm: int = 9):
    """定常部を FFT して基本波と高調波の振幅、THD を返す。"""
    w = np.hanning(len(sig))
    sp = np.fft.rfft(sig * w)
    freq = np.fft.rfftfreq(len(sig), 1 / fs)
    def amp_at(f):
        k = int(round(f / (freq[1] - freq[0])))
        # ハニング窓の漏れを拾うため近傍3ビンを合成
        return np.sqrt(sum(abs(sp[k + d]) ** 2 for d in (-1, 0, 1)))
    a1 = amp_at(f0)
    hs = [amp_at(f0 * k) for k in range(2, n_harm + 1)]
    thd = np.sqrt(sum(h ** 2 for h in hs)) / a1
    return a1, [h / a1 for h in hs], thd


def db(x: float) -> float:
    return 20 * np.log10(max(x, 1e-30))


def run(part: str, interp: str, vout_rms: float, rbias: float, rload: float,
        stage: str, cycles: int = 64, spc: int = 2048):
    ron = load_ron(part, interp)
    fs = F0 * spc
    t = np.arange(cycles * spc) / fs
    # 出力 vout_rms になるよう入力振幅を決める（スイッチの損失は小さいので近似で足りる）
    vin_pk = vout_rms * np.sqrt(2) / GAIN
    src = vin_pk * np.sin(2 * np.pi * F0 * t)

    if stage in ("input", "both"):
        a = divider(src, ron, rbias)
    else:
        a = src
    b = a * GAIN
    if stage in ("output", "both"):
        c = divider(b, ron, rload, rseries=R_ISO)
    else:
        c = b
    skip = 8 * spc                       # 過渡はないが窓端を避ける
    _, hr, thd = harmonics(c[skip:], fs, F0)
    return thd, hr[0], hr[1], float(np.max(np.abs(c)))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vout", type=float, default=9.2, help="出力 Vrms（既定 9.2 = ±13V）")
    ap.add_argument("--rload", type=float, default=50e3, help="出力負荷 Ω（既定 A50k）")
    ap.add_argument("--stage", choices=["input", "output", "both"], default="both")
    ap.add_argument("--interp", choices=["linear", "pchip", "both"], default="both")
    a = ap.parse_args()

    biases = [1e3, 10e3, 22e3, 47e3, 100e3]
    interps = ["linear", "pchip"] if a.interp == "both" else [a.interp]

    print(f"出力 {a.vout:.2f} Vrms (±{a.vout*1.414:.1f} V) / 負荷 {a.rload/1e3:.0f} kΩ / "
          f"段 {a.stage} / ゲイン {GAIN:g} / {F0:.0f} Hz\n")
    print(f"{'部品':10s}{'補間':7s}{'Rbias':>8s}{'THD':>11s}{'H2':>10s}{'H3':>10s}")
    for part in ("tmux7612", "dg412"):
        for interp in interps:
            for rb in biases:
                thd, h2, h3, pk = run(part, interp, a.vout, rb, a.rload, a.stage)
                print(f"  {part:8s}{interp:7s}{rb/1e3:7.0f}k{db(thd):10.1f}dB"
                      f"{db(h2):9.1f}dB{db(h3):9.1f}dB")
        print()


if __name__ == "__main__":
    main()
