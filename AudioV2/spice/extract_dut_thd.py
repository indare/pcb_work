#!/usr/bin/env python3
"""DUT（オペアンプ）の THD+N vs 出力振幅カーブをデータシートのベクタパスから抽出する。

## なぜ要るか

`switch_compare.py` の一次スクリーニングは、スイッチ側（この回路の実条件）と
DUT 側（データシートの規定点）を比べていて**条件が揃っていない**（issue #33）。
規定点はどれも 3〜5 Vrms で、こちらが問題にしている 4.0 / 9.2 Vrms ではない。

各データシートには THD+N vs 出力振幅のグラフがあるので、Ron 曲線と同じ手法で
ベクタパスから数値を起こせば、**少なくとも振幅軸は条件を揃えられる**。
（ゲインと負荷の差は残る。下の「限界」を読むこと）

## 抽出できたもの

  OPA1612   TI_OPA1612.pdf p.1  6本（G=+1/-1/+10 × RL=600Ω/2kΩ）

## 校正の検証

`G=+1, RL=2k` の 3.0 Vrms を読むと **−138.4 dB**。データシート実表の規定値は
`G=+1, f=1kHz, VO=3Vrms` で **−136 dB**。2.4 dB の差で、typ 値と実測トレースの
差として妥当な範囲。軸校正（x: log 0.01〜20V、y: −80〜−160dB）は左軸の %
目盛（0.01% = −80dB）とも一致する。

## ⚠ 限界

- **これは THD+N**（雑音込み）。スイッチ側の H2/H3 とは量の種類が違う
- **負荷が違う**。DS は RL=600Ω/2kΩ、こちらは 50kΩ。軽い負荷のぶん実回路の
  DUT はこれより良い可能性がある（＝スイッチが支配的になる方向）
- **ゲインが違う**。DS は G=+1/-1/+10、こちらは G=+2
- **末端のクリップ点を補間しないこと。** 曲線の最後の1〜2点は出力が電源に
  当たって THD が数十dB跳ね上がる。そこをまたいで内挿すると無意味な値が出る
  （実際にやらかした。9.2Vrms を 8.94V/-141.3 と 9.59V/-99.8 の間で内挿して
  「-124.8dB」という存在しない値を作った）

使い方:
  python3 AudioV2/spice/extract_dut_thd.py            # 抽出して JSON へ保存
  python3 AudioV2/spice/extract_dut_thd.py --report   # 保存済み JSON から読み値を出す
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

DATA = Path(__file__).resolve().parent / "data"
DS = Path(__file__).resolve().parents[2] / "Audio" / "datasheets" / "opamps"

#   OPA1612 p.1「THD+N Ratio vs Output Amplitude」
#   軸校正はラベル中心から: x は 1Vrms が px 203.1、1 decade = 51.2 px。
#   y は -80dB が px 515.6、20dB = 28.8 px。左軸の % 目盛とも一致する。
OPA1612 = {
    "pdf": "TI_OPA1612.pdf", "page": 0,
    "box": (98, 275, 508, 636),
    "x1v": 203.1, "xdec": 51.2, "y80": 515.6, "ydb20": 28.8,
    "legend": {
        (0.961, 0.51, 0.123): "G=+1, RL=600R",
        (0.182, 0.19, 0.573): "G=+1, RL=2k",
        (0.137, 0.122, 0.125): "G=-1, RL=600R",
        (0.0, 0.681, 0.938): "G=-1, RL=2k",
        (0.0, 0.65, 0.315): "G=+10, RL=600R",
        (0.926, 0.0, 0.548): "G=+10, RL=2k",
    },
}


def extract(spec: dict) -> dict:
    import fitz  # PyMuPDF。抽出時のみ必要
    page = fitz.open(DS / spec["pdf"])[spec["page"]]
    x0, x1, y0, y1 = spec["box"]
    out = {}
    for dr in page.get_drawings():
        col = dr.get("color")
        if not col:
            continue
        key = tuple(round(v, 3) for v in col)
        if key not in spec["legend"]:
            continue
        pts = [(q.x, q.y) for it in dr["items"] for q in it[1:] if hasattr(q, "x")]
        pts = [q for q in pts if x0 <= q[0] <= x1 and y0 <= q[1] <= y1]
        if len(pts) < 50:
            continue
        v = np.array([10 ** ((q[0] - spec["x1v"]) / spec["xdec"]) for q in pts])
        db = np.array([-80.0 - (q[1] - spec["y80"]) * (20.0 / spec["ydb20"])
                       for q in pts])
        o = np.argsort(v)
        v, db = v[o], db[o]
        uv, idx = np.unique(np.round(v, 5), return_inverse=True)
        udb = np.array([db[idx == i].mean() for i in range(len(uv))])
        out[spec["legend"][key]] = [uv.tolist(), udb.tolist()]
    return out


def clip_onset(v: list, db: list, jump: float = 15.0):
    """クリップが始まる振幅を返す。末端で THD が jump dB 以上跳ねた最初の点。"""
    for i in range(1, len(v)):
        if db[i] - db[i - 1] > jump:
            return v[i - 1], v[i]
    return v[-1], None


def read_at(v: list, db: list, target: float):
    """target Vrms での値。クリップ点をまたぐ場合は None（内挿してはいけない）。"""
    safe, first_clip = clip_onset(v, db)
    if target > safe:
        return None, safe, first_clip
    return float(np.interp(target, v, db)), safe, first_clip


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--report", action="store_true", help="保存済み JSON から読むだけ")
    a = ap.parse_args()

    path = DATA / "opa1612_thdn_curve.json"
    if not a.report:
        curves = extract(OPA1612)
        json.dump(curves, open(path, "w"), indent=1)
        print(f"抽出 {len(curves)} 本 → {path}")
    curves = json.load(open(path))

    print("\n=== 校正の検証（DS 実表: G=+1, f=1kHz, VO=3Vrms → -136 dB）===")
    v, db = curves["G=+1, RL=2k"]
    print(f"  抽出 G=+1,RL=2k @3.0Vrms = {np.interp(3.0, v, db):.1f} dB")

    print("\n=== 振幅ごとの読み（クリップ点をまたぐ内挿はしない）===")
    print(f"  {'条件':16s}{'3.0V':>9s}{'4.0V':>9s}{'9.2V':>9s}   クリップ開始")
    for name, (v, db) in curves.items():
        cells = []
        for t in (3.0, 4.0, 9.2):
            val, safe, first = read_at(v, db, t)
            cells.append(f"{val:8.1f}" if val is not None else "  クリップ")
        safe, first = clip_onset(v, db)
        rng = f"{safe:.2f}〜{first:.2f}Vrms" if first else f">{safe:.2f}Vrms"
        print(f"  {name:16s}" + "".join(cells) + f"   {rng}")

    print("\n  ⚠ G=+1 だけ 8.94〜9.59Vrms で先にクリップするのは、非反転バッファの")
    print("     入力同相電圧の制限（入力が出力と同電位まで振れる）。")
    print("     **こちらの回路は G=+2 なので入力は Vout/2 までしか振れず、この制限は付かない。**")
    print("     出力振幅の限界を見るなら G=-1 系（同相制限なし）が適切な代理。")
    print("     9.2Vrms = ±13.0Vpk で、±15V 電源の出力振幅限界にかなり近い。")

    print("\n=== 振幅を揃えた比較: TMUX7612 の H2/H3 vs OPA1612 の THD+N ===")
    #   代理カーブに G=-1, RL=2k を使う理由（#33 で補強された）:
    #   ・G=-1 のノイズゲインは 2 で、非反転 G=+2 のノイズゲインと一致する
    #   ・非反転 G=+1 は入力が出力と同電位まで振れるので入力同相制限で先にクリップする。
    #     OPA1612 の同相入力範囲は電源レールから 2V 内側＝±15V なら約±13V。
    #     G=+2 で 9.2Vrms 出力なら +入力は約 6.5Vpk しか振れないので余裕がある。
    import switch_thd
    v, db = curves["G=-1, RL=2k"]
    print(f"  {'Vrms':>7s}{'Vpk':>7s}{'switch最大次数':>15s}{'OPA1612':>11s}{'差':>9s}")
    cross = None
    for amp in (4.0, 5.0, 6.0, 7.0, 7.5, 7.78, 7.9, 8.0, 9.2):
        _, h2, h3, _ = switch_thd.run("tmux7612", "pchip", amp, 47e3, 50e3, "output")
        worst = max(switch_thd.db(h2), switch_thd.db(h3))
        dut = float(np.interp(amp, v, db))
        if cross is None and worst > dut:
            cross = amp
        print(f"  {amp:7.2f}{amp * 1.414:7.2f}{worst:13.1f}dB{dut:10.1f}dB"
              f"{worst - dut:8.1f}dB")
    print(f"  → 交差は {cross} Vrms 付近。Ron 平坦領域の膝（±11V = 7.78Vrms）とほぼ一致する。")
    print("     膝を越えた瞬間に switch が DUT を上回る。")
    print()
    print("  ⚠ OPA1612 の値は typical グラフのベクタ抽出なので、小数点1桁の絶対値として")
    print("     扱わないこと。9.2Vrms なら『概ね -144〜-146dB 級』が適切な言い方。")
    print("  ⚠ 残る不一致: switch は H2/H3 の個別次数、DUT は THD+N 総量。")
    print("     負荷 DS 2k / 実回路 50k（軽いぶん実 DUT はもっと良い＝ switch に不利）。")


if __name__ == "__main__":
    main()
