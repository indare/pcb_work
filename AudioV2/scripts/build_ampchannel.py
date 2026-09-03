#!/usr/bin/env python3
"""`AmpChannel` を D22/D23 の形へ書き換える（1ch＝オペアンプ1個ぶん、両版共通）。

- **D22（出力のみ MUX）**: `TMUX7612` をこのシートから外す。1 IC = 2ch になるので
  per-channel シートには置けない。切替は娘基板シート側へ。
  結果として **このシートはリレー版とスイッチ版で完全に同一**になる。
- **D23（入力 A案）**: 入力結合C を 1µF フィルム1個に、バイアスを 100k に。
  入力側の 220k プルダウンは撤去（ブロードキャストでは不要で、残すと 10ch 並列で
  6.9k になり PT2314 の RL=10k を割る）。

**書き起こし直さず、残す部分の手描き配線をそのまま置く。** アンプ本体（AMP601 と
帰還・出力段）は座標も配線もそのまま。触るのは入力部・切替部・階層ピンだけ。

    python3 AudioV2/scripts/build_ampchannel.py --dry-run
    python3 AudioV2/scripts/build_ampchannel.py

⚠ **これは一度きりの移行スクリプトで、冪等ではない。** 変換済みのAmpChannel を
もう一度食わせると「外す部品が見つからない」で **書き込む前に**落ちる（そう作ってある）。
やり直すなら `git checkout AudioV2/AmpChannel.kicad_sch` してから回すこと。
"""

from __future__ import annotations

import argparse
import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import sch_edit  # noqa: E402
import sch_import  # noqa: E402

_UID_NS = uuid.UUID("b2000008-0008-4008-8008-000000000008")
_seq = 0


def uid() -> str:
    global _seq
    _seq += 1
    return str(uuid.uuid5(_UID_NS, f"ampchannel/{_seq}"))


# 1µF はフィルムだと P5.00 には入らない。10mm ピッチの MKT へ。
FILM_1U_FP = "Capacitor_THT:C_Rect_L11.0mm_W4.2mm_P10.00mm_MKT"

# --- D23: 値の変更 -------------------------------------------------------
REVALUE = [
    ("C602", "1uF film", FILM_1U_FP),   # 旧 100nF film（10µF 電解と並列だった）
    ("C605", "1uF film", FILM_1U_FP),
    ("R601", "100k", None),             # 旧 1k。ブロードキャストのバイアス
    ("R607", "100k", None),
]

# --- 外す部品 -----------------------------------------------------------
DROP_SYMBOLS = {
    "U601",           # D22: TMUX7612 は娘基板シートへ
    "C603", "C606",   # D23: 入力の 10µF 電解（フィルム1個に統合）
    "R605", "R611",   # D23: 入力の 220k プルダウン（RL=10k を割るので撤去）
}

# 外す部品にぶら下がっていたワイヤ（端点で指定）。
DROP_WIRES = [
    # L 入力: IN_L → C603.2 / R605.2 → A_GND
    ((49.53, 44.45), (63.5, 44.45)),
    ((49.53, 54.61), (49.53, 52.07)),
    # R 入力: IN_R → C606.2 / R611.2 → A_GND
    ((49.53, 81.28), (62.23, 81.28)),
    ((49.53, 91.44), (49.53, 88.9)),
    # U601 のピンに直接繋がっていた3本
    ((139.7, 156.21), (139.7, 153.67)),
    ((134.62, 154.94), (134.62, 153.67)),
    ((134.62, 115.57), (134.62, 118.11)),
]
# 上を外すと片端が浮くもの
DROP_WIRES += [((127.0, 154.94), (134.62, 154.94))]

# 外す部品専用だったラベル（座標で指定）
DROP_LABELS = [
    (49.53, 54.61),    # R605 の A_GND
    (49.53, 91.44),    # R611 の A_GND
    # U601 のピン先にあった切替専用のラベル
    (124.46, 125.73), (124.46, 128.27), (124.46, 133.35), (124.46, 135.89),
    (124.46, 140.97), (124.46, 143.51), (124.46, 148.59), (124.46, 151.13),
    (149.86, 127.0), (149.86, 134.62), (149.86, 142.24), (149.86, 149.86),
]

# --- 階層ピンの差し替え -------------------------------------------------
# 旧: TONE_L/R は切替の入口、AMP_SEL_L/R が出口、SEL でチャンネル選択
# 新: TONE_L/R が直接アンプ入力（ブロードキャスト）、OUT_L/R が ch ごとの出力
RETAG = [
    # (元のローカルラベルの座標, 新しい名前, 種別, 回転)
    ((43.18, 44.45), "TONE_L", "input", 180),
    ((44.45, 81.28), "TONE_R", "input", 180),
    ((134.62, 39.37), "OUT_L", "output", 0),
    ((135.89, 76.2), "OUT_R", "output", 0),
]

_TOL = 0.01


def _same(a: tuple[float, float], b: tuple[float, float]) -> bool:
    return abs(a[0] - b[0]) < _TOL and abs(a[1] - b[1]) < _TOL


def _hier(name: str, shape: str, x: float, y: float, rot: int) -> str:
    just = "right" if rot == 180 else "left"
    return (f'\t(hierarchical_label "{name}"\n\t\t(shape {shape})\n\t\t(at {x} {y} {rot})\n'
            f'\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n'
            f'\t\t\t(justify {just})\n\t\t)\n\t\t(uuid "{uid()}")\n\t)\n')


def build(dry_run: bool = False) -> str:
    s = sch_import.load(ROOT / "AmpChannel.kicad_sch")
    before = {k: len(s.of_kind(k)) for k in
              ("symbol", "wire", "junction", "label", "hierarchical_label", "no_connect")}

    dropped_tips = {tuple(round(v, 2) for v in t)
                    for e in s.elements if e.kind == "symbol" and e.ref in DROP_SYMBOLS
                    for t in sch_edit.symbol_tips(e)}
    sch_edit.remove_symbols(s, DROP_SYMBOLS)

    kept: list[sch_import.Element] = []
    retagged: list[str] = []
    for e in s.elements:
        if e.kind == "wire":
            c = [tuple(x) for x in e.coords()]
            if any((_same(c[0], a) and _same(c[1], b)) or (_same(c[0], b) and _same(c[1], a))
                   for a, b in DROP_WIRES):
                continue
        elif e.kind in ("label", "hierarchical_label"):
            if e.at and any(_same(e.at, p) for p in DROP_LABELS):
                continue
            hit = next((r for r in RETAG if e.at and _same(e.at, r[0])), None)
            if hit and e.kind == "label":
                _, name, shape, rot = hit
                kept.append(sch_import.Element(
                    "hierarchical_label", _hier(name, shape, e.at[0], e.at[1], rot),
                    None, name, e.at))
                retagged.append(f"{e.name}@{e.at} -> 階層 {name}({shape})")
                continue
        elif e.kind == "no_connect":
            if e.at and any(_same(e.at, t) for t in dropped_tips):
                continue
        kept.append(e)
    s.elements = kept

    for ref, val, fp in REVALUE:
        sch_edit.set_value(s, ref, val, fp)

    if dry_run:
        after = {k: len(s.of_kind(k)) for k in before}
        print("要素数 " + "  ".join(f"{k}:{before[k]}→{after[k]}" for k in before))
        print("値の変更: " + ", ".join(f"{r}={v}" for r, v, _ in REVALUE))
        print("階層ピンへ差し替え:")
        for r in retagged:
            print("   ", r)
        print("階層ピン: " + ", ".join(sorted(e.name for e in s.of_kind("hierarchical_label"))))
        print("部品: " + ", ".join(sorted(e.ref for e in s.of_kind("symbol") if e.ref)))
        return ""
    return s.render()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    out = build(dry_run=a.dry_run)
    if out:
        (ROOT / "AmpChannel.kicad_sch").write_text(out, encoding="utf-8")
        print(f"書き換え: AudioV2/AmpChannel.kicad_sch ({len(out)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
