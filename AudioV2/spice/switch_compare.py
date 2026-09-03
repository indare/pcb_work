#!/usr/bin/env python3
"""入力ブロードキャスト＋出力のみMUX構成で、切替素子候補を同条件で比較する。

## 評価条件（AudioV2 の実条件）

    電源 ±15V / DUT ゲイン2 / DUT出力最大 ±13Vpk (9.2Vrms)
    出力負荷 50kΩ / 出力直列 47Ω / 10 DUT 中 1ch ON・9ch OFF
    入力は全DUTへ常時配信（入力側スイッチなし）

## データの確度が部品ごとに違う（重要）

    実カーブ抽出 : TMUX7612 / DG412 / ADG1407 / DG507B
        データシートの Ron vs 信号電圧グラフをベクタパスから数値抽出したもの。
    モデル       : MAX14753 / MAX14778
        両者ともグラフの y 軸分解能が flatness を解像できない（MAX14753）か、
        Ron(V) グラフ自体が無い（MAX14778）。flatness スペックを満たす
        滑らかな仮定形状から作った近似。**実カーブ抽出と同列に扱わないこと。**
        実チップにキンクや非対称があれば外れる。

使い方:
  python3 AudioV2/spice/switch_compare.py
  python3 AudioV2/spice/switch_compare.py --stage both
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import switch_thd  # noqa: E402
from switch_offiso import PARTS as OFF_PARTS  # noqa: E402
from switch_offiso import coff_from_oiso, solve_broadcast  # noqa: E402

DATA = Path(__file__).resolve().parent / "data"

# name: (表示名, 出力のみに必要なIC数, データ確度)
CANDIDATES = {
    "tmux7612": ("TMUX7612 (4xSPST)", 5, "実カーブ"),
    "adg1407": ("ADG1407 (dual 8:1)", 2, "実カーブ"),
    "dg507b": ("DG507B (dual 8:1)", 2, "実カーブ"),
    "max14753_model": ("MAX14753 (dual 4:1)", 3, "モデル"),
    "max14778_model": ("MAX14778 (dual 4:1)", 3, "モデル"),
}
# switch_offiso.PARTS のキー対応（モデル名の接尾辞を落とす）
OFF_KEY = {k: k.replace("_model", "") for k in CANDIDATES}


def ensure_model_curves() -> None:
    """flatness スペックだけが分かっている部品の仮定カーブを作る（無ければ）。"""
    specs = {
        # name: (Ron center, flatness, 信号範囲, 出典条件のメモ)
        "max14753_model": (60.0, 0.03, 20.0),
        "max14778_model": (0.84, 0.003, 25.0),
    }
    for name, (ron0, flat, span) in specs.items():
        path = DATA / f"{name}_ron_curve.json"
        if path.exists():
            continue
        v = np.linspace(-span, span, 201)
        ron = ron0 - flat / 2 + flat * (v / span) ** 2   # 対称パラボラ
        json.dump([[float(a), float(b)] for a, b in zip(v, ron)],
                  open(path, "w"), indent=0)
        print(f"# generated model curve: {path.name}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", choices=["input", "output", "both"], default="output")
    ap.add_argument("--rload", type=float, default=50e3)
    ap.add_argument("--rbias", type=float, default=47e3)
    a = ap.parse_args()

    ensure_model_curves()
    switch_thd.DATA = DATA
    db = switch_thd.db
    levels = (4.0, 7.07, 8.0, 9.2)

    print(f"\n段={a.stage} / 負荷{a.rload/1e3:.0f}kΩ / Riso={switch_thd.R_ISO:.0f}Ω / "
          f"ゲイン{switch_thd.GAIN:g} / 1kHz\n")
    print(f"{'部品':22s}{'IC':>3s}{'確度':>7s}" + "".join(f"{v:>9.2f}Vrms" for v in levels))
    TOTALS = {}   # 下の次数別テーブルと条件が一致しているか突き合わせるために控える
    for key, (name, nic, conf) in CANDIDATES.items():
        cells = []
        for v in levels:
            thd, _, _, _ = switch_thd.run(key, "pchip", v, a.rbias, a.rload, a.stage)
            TOTALS.setdefault(key, {})[v] = db(thd)
            cells.append(f"{db(thd):9.1f}dB")
        print(f"{name:22s}{nic:>3d}{conf:>7s}" + "".join(cells))
    print("\n  ⚠ 「モデル」行の数値は実 Ron(V) から得たものではない（後述）。")
    print("     部品間の差を語るときは必ず『仮定モデル上では』と付けること。")

    print("\n--- Ron(V) の実効的な広がり（抽出/モデルカーブから） ---")
    print(f"{'部品':22s}{'Ron@0V':>10s}{'|V|<=13V の flatness':>22s}")
    for key, (name, _, _) in CANDIDATES.items():
        pts = json.load(open(DATA / f"{key}_ron_curve.json"))
        sub = [p for p in pts if abs(p[0]) <= 13.05]
        ys = [p[1] for p in sub]
        c = min(sub, key=lambda p: abs(p[0]))[1]
        print(f"{name:22s}{c:9.2f}Ω{max(ys)-min(ys):20.3f}Ω")

    print(f"\n--- ON経路の歪みを次数別に（段={a.stage}。上の表と同一条件） ---")
    #   #33: 総THD同士をベクトル合成してはいけない。合成できるのは同じ次数の成分だけ。
    #   総THD は H2..H9 の RSS なので、次数別に見ると像が変わる部品がある。
    print(f"{'部品':22s}{'Vrms':>6s}{'THD(RSS)':>11s}{'H2':>10s}{'H3':>10s}")
    #   上の総THD表と同じ (rbias, rload, stage) で回し、一致するか自分で検証する。
    #   ここを固定値でハードコードして構成がズレる事故を起こしたので（#33）。
    mismatched = []
    for key, (name, _, _) in CANDIDATES.items():
        if not (DATA / f"{key}_ron_curve.json").exists():
            continue
        for v in (4.0, 9.2):
            try:
                thd, h2, h3, _ = switch_thd.run(key, "pchip", v, a.rbias, a.rload,
                                                a.stage)
            except Exception:
                continue
            if v in TOTALS.get(key, {}) and abs(db(thd) - TOTALS[key][v]) > 0.05:
                mismatched.append(f"{name}@{v}Vrms")
            print(f"{name:22s}{v:6.1f}{db(thd):10.1f}dB{db(h2):9.1f}dB{db(h3):9.1f}dB")
    print("  → ADG1407 は H3 支配（9.2Vrms で H2 -133.4 / H3 -96.3 と 37dB 差）。")
    print("     総THD だけ見ていると次数の偏りが見えない。")
    print("  ⚠ MAX14753/14778 の H2 が両振幅で同値(-169dB)なのは数値床。")
    print("     モデルが左右対称パラボラなので偶数次が原理的に出ない（実チップの値ではない）。")
    if mismatched:
        print("  ✗ 上の総THD表と条件がズレている: " + ", ".join(mismatched))
    else:
        print("  ✓ THD(RSS) 列は上の総THD表と一致（同一条件で計算されている）")

    print("\n--- 判定の目安（#33 で3回訂正。確定値ではない。README が正） ---")
    print("  ① 理想化した概算 bin floor  約 -137 dBFS")
    print("       DR112dB(A特性) + 処理利得。実使用 N=1024 / Hann 窓 ENBW 1.5bin")
    print("       ⚠ 112dB は A特性の積分値。雑音が白色・平坦でない限り、ここから")
    print("         正確な 1bin floor は決まらない（ΔΣ は雑音整形で高域が持ち上がる）。")
    print("         実際の bin floor は ADC 無入力の実測で確定。")
    print("  ② PCM1804 の THD+N データシート基準値  typ -102 dB")
    print("       DS p.7: fIN=1kHz, AP System Two, 20k LPF + 400Hz HPF（無加重）")
    print("       ⚠ DR/SNR は A特性。加重が違うので THD+N から SNR は引けない。")
    print("       ⚠ これは THD+N の基準値であって『絶対THDの床』そのものではない。")
    print("         実際の高調波測定限界は H2/H3 baseline 実測で決まる。")
    print("  ③ PT2314                  -60 dB  通常経路では常にこれが支配")
    print()
    print("  やってはいけないこと:")
    print("   ・①を『歪みの床』として使う（①は雑音。処理利得は離散トーンに効かない）")
    print("   ・①②を確定した測定床として部品を落とす（どちらも実測前の目安）")
    print("   ・②より下だから『見えない』と結論する（同次数は複素和で残る）")
    print("   ・②(総THD+N) と素子の総THD をそのままベクトル合成する（次数別に扱う）")
    print()
    print("  → 総量の段階で確定できるのは『②より上の DG507B と ADG1407@9.2Vrms は")
    print("     確実に測定を汚す』まで。残りは ADC 直結 baseline で H2/H3 の")
    print("     振幅・位相を実測してから。")

    print("\n--- OFF側: ブロードキャスト構成でのBUS合成誤差（20kHz、非選択9ch） ---")
    print(f"{'部品':22s}{'OISO条件':>18s}{'C_off':>9s}{'振幅誤差':>11s}{'漏れ歪み':>11s}")
    for key, (name, _, _) in CANDIDATES.items():
        ok = OFF_KEY[key]
        if ok not in OFF_PARTS:
            continue
        oiso, f0, rl0, ron, _ = OFF_PARTS[ok]
        c = coff_from_oiso(oiso, f0, rl0)
        mism = [(1.0, 0.0, -94.0)] * 9
        _, gerr, dleak, _ = solve_broadcast(ok, 20e3, a.rload, 10, mism)
        print(f"{name:22s}{f'{oiso:.0f}dB@{f0/1e3:.0f}k':>18s}{c*1e12:8.2f}p"
              f"{db(abs(gerr)):10.4f}dB{db(dleak):10.1f}dB")


if __name__ == "__main__":
    main()
