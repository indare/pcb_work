#!/usr/bin/env python3
"""`AmpBank` に切替段（出力のみ MUX）を足す — D22 の実装。

`AmpChannel` から `TMUX7612` が抜けたぶんをこのシートで受ける。
**1 IC = 2ch**（4スイッチ ÷ L/R）なので 10ch で 5 個。

    S 側が ch ごと、D 側が共通バス（現行の使い方をそのまま踏襲）
    chA_OUT_L → S1(3)  D1(2)  → AMP_SEL_L     SEL1(1) + SEL2(16) ← SEL_CH_A
    chA_OUT_R → S2(14) D2(15) → AMP_SEL_R
    chB_OUT_L → S3(11) D3(10) → AMP_SEL_L     SEL3(9) + SEL4(8)  ← SEL_CH_B
    chB_OUT_R → S4(6)  D4(7)  → AMP_SEL_R

このシートは**ワイヤを使わずピン先のラベルで結線する流儀**（既に label 109・wire 36）
なので、追加分もラベルで書く。

⚠ 娘基板は 5ch×2枚（D19）なので、ここは最終形ではない。1枚 5ch＝TMUX 3個への
分割は別ステップ。いまは「10ch 1枚」のまま D22 を成立させて検証できる状態にする。

    python3 AudioV2/scripts/build_ampbank.py --dry-run

⚠ **これは一度きりの移行スクリプトで、冪等ではない。** 変換済みのAmpBank を
もう一度食わせると「外す部品が見つからない」で **書き込む前に**落ちる（そう作ってある）。
やり直すなら `git checkout AudioV2/AmpBank.kicad_sch` してから回すこと。
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
import sch_helpers  # noqa: E402
import sch_import  # noqa: E402
from generate_kicad_scaffold import PARENT  # noqa: E402
from build_motherboard import _merge_lib_symbols  # noqa: E402
from sch_helpers import embed_lib_symbols, symbol_inst_v10  # noqa: E402

UUID_BANK_INST = "a1000011-0011-4011-8011-000000000011"
_UID_NS = uuid.UUID("b2000011-0011-4011-8011-000000000011")
_seq = 0


def uid() -> str:
    global _seq
    _seq += 1
    return str(uuid.uuid5(_UID_NS, f"ampbank/{_seq}"))


TMUX = "AudioV2:TMUX7612"
# (IC 参照, 担当する2ch, 配置座標, パスコン2個の参照)
BLOCKS = [
    ("U311", (1, 2), (66.04, 233.68), ("C311", "C312")),
    ("U312", (3, 4), (129.54, 233.68), ("C313", "C314")),
    ("U313", (5, 6), (193.04, 233.68), ("C315", "C316")),
    ("U314", (7, 8), (256.54, 233.68), ("C317", "C318")),
    ("U315", (9, 10), (320.04, 233.68), ("C319", "C320")),
]
# TMUX7612 のピン番号 → そのピンに置くラベル名（{a}/{b} は担当 ch 番号）
PINMAP = {
    "3": "CH{a}_OUT_L", "2": "AMP_SEL_L",
    "14": "CH{a}_OUT_R", "15": "AMP_SEL_R",
    "11": "CH{b}_OUT_L", "10": "AMP_SEL_L",
    "6": "CH{b}_OUT_R", "7": "AMP_SEL_R",
    "1": "SEL_CH{a}", "16": "SEL_CH{a}",
    "9": "SEL_CH{b}", "8": "SEL_CH{b}",
    "13": "+15V", "4": "-15V", "5": "A_GND",
}
NC_PIN = "12"
# 左半分のピンは左向き、右半分は右向きにラベルを出す
LEFT_PINS = {"1", "2", "3", "4", "5", "6", "7", "8"}


def _label(name: str, x: float, y: float, left: bool) -> str:
    rot, just = (180, "right") if left else (0, "left")
    return (f'\t(label "{name}"\n\t\t(at {x} {y} {rot})\n\t\t(effects\n\t\t\t(font\n'
            f'\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify {just} bottom)\n\t\t)\n'
            f'\t\t(uuid "{uid()}")\n\t)\n')


def build(dry_run: bool = False) -> str:
    s = sch_import.load(ROOT / "AmpBank.kicad_sch")
    path = f"/{PARENT}/{UUID_BANK_INST}"

    # --- 1) 各 AmpChannel インスタンスのピンを新しい AmpChannel へ合わせる ---
    sel_pins: list[tuple[float, float]] = []
    out_pins: dict[tuple[float, float], str] = {}
    for i, e in enumerate(s.elements):
        if e.kind != "sheet":
            continue
        ch = int(re.search(r"AmpCh(\d+)", e.name).group(1))
        txt = e.text
        m = re.search(r'\t\t\(pin "SEL" \w+\n\t\t\t\(at ([\d.-]+) ([\d.-]+) [\d.-]+\)'
                      r"[\s\S]*?\n\t\t\)\n", txt)
        if m:
            sel_pins.append((float(m.group(1)), float(m.group(2))))
            txt = txt.replace(m.group(0), "")
        for old, new in (("AMP_SEL_L", f"CH{ch}_OUT_L"), ("AMP_SEL_R", f"CH{ch}_OUT_R")):
            pm = re.search(rf'\(pin "{old}" \w+\n\t\t\t\(at ([\d.-]+) ([\d.-]+) ', txt)
            if pm:
                out_pins[(float(pm.group(1)), float(pm.group(2)))] = new
            txt = txt.replace(f'(pin "{old}" output', f'(pin "{new.split("_",1)[1]}" output')
        s.elements[i] = sch_import.Element(e.kind, txt, e.ref, e.name, e.at)

    # --- 2) ピン上のラベルを差し替える ---
    kept: list[sch_import.Element] = []
    dropped, renamed = [], []
    for e in s.elements:
        if e.kind == "label" and e.at:
            k = (round(e.at[0], 2), round(e.at[1], 2))
            if any(abs(k[0] - x) < 0.01 and abs(k[1] - y) < 0.01 for x, y in sel_pins):
                dropped.append(f"{e.name}@{k}")      # シート側の SEL ラベル（MCP 側は残る）
                continue
            hit = next((v for (x, y), v in out_pins.items()
                        if abs(k[0] - x) < 0.01 and abs(k[1] - y) < 0.01), None)
            if hit:
                renamed.append(f"{e.name}@{k} -> {hit}")
                kept.append(sch_import.Element(
                    "label", _label(hit, e.at[0], e.at[1], False), None, hit, e.at))
                continue
        kept.append(e)
    s.elements = kept

    # --- 3) TMUX7612 ×5 とパスコンを足す（ラベルだけで結線） ---
    saved_new, sch_helpers.new_uid = sch_helpers.new_uid, uid
    added = []
    try:
        cap_pins = sch_edit.lib_pins("Device:C")
        for ref, (a, b), (x, y), caps in BLOCKS:
            s.elements.append(sch_import.Element(
                "symbol", symbol_inst_v10(TMUX, ref, "TMUX7612", x, y, 0, path,
                                          footprint="Package_SO:TSSOP-16_4.4x5mm_P0.65mm"),
                ref, None, (x, y)))
            tips = {n: t for n, t in zip(sch_edit.lib_pins(TMUX).keys(),
                                         sch_edit.symbol_tips(s.elements[-1]))}
            for num, tmpl in PINMAP.items():
                tx, ty = tips[num]
                s.elements.append(sch_import.Element(
                    "label", _label(tmpl.format(a=a, b=b), tx, ty, num in LEFT_PINS),
                    None, tmpl.format(a=a, b=b), (tx, ty)))
            nx, ny = tips[NC_PIN]
            s.elements.append(sch_import.Element(
                "no_connect", f'\t(no_connect\n\t\t(at {nx} {ny})\n\t\t(uuid "{uid()}")\n\t)\n',
                None, None, (nx, ny)))
            for j, (cref, net) in enumerate(zip(caps, ("+15V", "-15V"))):
                cx, cy = x - 12.7 + j * 7.62, y + 25.4
                s.elements.append(sch_import.Element(
                    "symbol", symbol_inst_v10("Device:C", cref, "100nF", cx, cy, 0, path,
                                              footprint="Capacitor_SMD:C_1206_3216Metric_"
                                                        "Pad1.33x1.80mm_HandSolder"),
                    cref, None, (cx, cy)))
                ct = sch_edit.symbol_tips(s.elements[-1])
                top, bot = sorted(ct, key=lambda p: p[1])
                s.elements.append(sch_import.Element(
                    "label", _label(net, top[0], top[1], False), None, net, top))
                s.elements.append(sch_import.Element(
                    "label", _label("A_GND", bot[0], bot[1], False), None, "A_GND", bot))
            added.append(f"{ref}(ch{a}/ch{b}) + {caps[0]}/{caps[1]}")
    finally:
        sch_helpers.new_uid = saved_new

    # ⚠ TMUX7612 は元々 AmpChannel 側にいたので、AmpBank の lib_symbols に無い。
    #    入れ忘れると KiCad がピンを解決できず、そのシンボルが**ネットリストから
    #    丸ごと消える**（2026-09-03 に実際に踏んだ。母板でも同じ罠を踏んでいる）。
    for i, h in enumerate(s.header):
        if h.lstrip().startswith("(lib_symbols"):
            s.header[i] = _merge_lib_symbols([h, embed_lib_symbols([TMUX, "Device:C"])])
            break

    if dry_run:
        print("シート側 SEL ラベルを外した:", len(dropped))
        print("出力ラベルを改名:")
        for r in renamed[:4]:
            print("   ", r)
        print(f"   … 計 {len(renamed)} 件")
        print("足した切替段:")
        for a in added:
            print("   ", a)
        print("階層ピン:", ", ".join(sorted(e.name for e in s.of_kind("hierarchical_label"))))
        return ""
    return s.render()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    out = build(dry_run=a.dry_run)
    if out:
        (ROOT / "AmpBank.kicad_sch").write_text(out, encoding="utf-8")
        print(f"書き換え: AudioV2/AmpBank.kicad_sch ({len(out)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
