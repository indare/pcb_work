#!/usr/bin/env python3
"""リレー娘: AMP_SEL の L と R を別の通り道に分ける（2026-09-24）。

問題（実測）:
  - R（表）が L（裏）の真裏・真横を走っていた。コネクタ下で y=260.67 / 260.3（ずれ 0.37 mm）、
    K303 へは x=533.7 / 537.25（3.5 mm）。反対層で 1 mm 以内 11 mm・4 mm 以内 60 mm 超
  - R の縦線がオペアンプ本体の上を ＋入力の表の線から 1.9 mm で通っていた（2 mm 以内 28 mm）
  - R の K301 への横線が +5V_COIL の表（y=286.3）と 1.3 mm で 23 mm 並走

制約（配置から決まる）:
  - y≈286.3 の +5V_COIL は「リレーの中（pin1↔pin10）は裏・リレー間は表」。なので R はリレーの内側を
    表で、L はリレーの間を裏で降りる
  - 北側は表が空き・裏は ±15V と各チャンネルの SMD で混んでいる → R は表のまま
  - 南から L を K301/K302 へ入れる道は無い（U321・C322・±15V の裏の縦線）→ L の K301/K302 は北から

組み直し:
  R  北の幹線を表 y=283.79（±15V の表と +5V_COIL の表のほぼ中間）に1本。各リレーの内側
     （pin4 の東 2.6 mm）を表で降りて 45° で pin4 へ。コネクタからは裏で南西へ下り
     （TONE_R の表とは直角に交差）、ビアで表へ上がって x=509.23 を幹線まで
  L  東の枝を張り替え: 既存の横線から裏で南へ → ビア → 表で CH2 と CH3 の間を降り、±15V の手前で裏へ →
     R の幹線を直角にくぐって x=527.3 の既存ビア（K302 と南のバスへ）
  ±15V  y=281.3 のうち旧 R を通すために裏へ落としていた x=530.25〜535.25 を表に戻す（ビア2本減）

経路は `sel_route2l.py`（表裏2層の A*）で探し、折れの細部を手で整えて明示座標にした。

    python3 AudioV2.1/scripts/relay_lr_separate.py --board out/relay/lr_try.kicad_pcb --dry-run
    python3 AudioV2.1/scripts/relay_lr_separate.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).resolve().parent))
import amp_sel_hop as hop  # noqa: E402
from pcb_preview import sheet_region  # noqa: E402

PCB = Path(__file__).resolve().parents[1] / "AudioV2Case.kicad_pcb"
F, B = hop.F, hop.B
SR, SL = "/AMP_SEL_R", "/AMP_SEL_L"

REMOVE = [
    # R: 表の旧経路をすべて（コネクタ直下の裏の短い区間も）
    (F, SR, (517.729999, 252.29), (517.729999, 252.320001)), (F, SR, (517.729999, 252.320001), (514.78, 255.27)),
    (F, SR, (514.78, 255.27), (511.51, 255.27)), (B, SR, (511.51, 255.27), (511.51, 257.74)),
    (B, SR, (511.51, 257.74), (511.5, 257.75)),
    (F, SR, (511.51, 257.74), (507.384365, 257.74)), (F, SR, (507.384365, 257.74), (505.8, 259.324365)),
    (F, SR, (505.8, 259.324365), (505.8, 286.7)), (F, SR, (505.8, 286.7), (504.9, 287.6)),
    (F, SR, (504.9, 287.6), (482.2475, 287.6)), (F, SR, (482.2475, 287.6), (475.995, 293.8525)),
    (F, SR, (511.51, 257.74), (508.25, 261.0)), (F, SR, (508.25, 261.0), (508.25, 289.8275)),
    (F, SR, (508.25, 289.8275), (504.125, 293.9525)),
    (F, SR, (511.51, 257.74), (514.44, 260.67)), (F, SR, (514.44, 260.67), (532.57, 260.67)),
    (F, SR, (532.57, 260.67), (533.7, 261.8)), (F, SR, (533.7, 261.8), (533.7, 292.387499)),
    (F, SR, (533.7, 292.387499), (532.045, 294.042499)),
    (F, SR, (533.06, 261.16), (559.105635, 261.16)), (F, SR, (559.105635, 261.16), (560.935, 262.989365)),
    (F, SR, (560.935, 262.989365), (560.935, 292.7125)), (F, SR, (560.935, 292.7125), (559.485, 294.1625)),
    # L: 東の枝（コネクタ下 → R の真裏 → x=537.25 → x=527.3 の既存ビア）
    (B, SL, (513.51, 253.05), (512.75, 253.81)), (B, SL, (512.75, 253.81), (512.75, 258.55)),
    (B, SL, (512.75, 258.55), (514.5, 260.3)), (B, SL, (514.5, 260.3), (521.25, 260.3)),
    (B, SL, (521.25, 260.3), (525.5, 264.55)), (B, SL, (525.5, 264.55), (537.25, 264.55)),
    (B, SL, (537.25, 264.55), (537.25, 283.05)), (B, SL, (537.25, 283.05), (531.75, 283.05)),
    (B, SL, (531.75, 283.05), (527.3, 287.5)), (B, SL, (527.3, 287.5), (527.3, 292.7)),
    # ±15V: 旧 R のために裏へ落としていた区間
    (B, "/+15V", (530.25, 281.3), (535.25, 281.3)),
]
REMOVE_VIAS = [(SR, (511.51, 255.27)), (SR, (511.51, 257.74)), ("/+15V", (530.25, 281.3)), ("/+15V", (535.25, 281.3))]

W = 0.2
Y_TRUNK = 283.79
ADD = [
    # R: 北の幹線と、各リレーの内側の降り線（pin4 の東 2.6 mm → 45° で pin4）
    (F, SR, [(478.595, Y_TRUNK), (562.085, Y_TRUNK)], W),
    (F, SR, [(478.595, Y_TRUNK), (478.595, 291.2525), (475.995, 293.8525)], W),
    (F, SR, [(506.725, Y_TRUNK), (506.725, 291.3525), (504.125, 293.9525)], W),
    (F, SR, [(534.645, Y_TRUNK), (534.645, 291.4425), (532.045, 294.042499)], W),
    (F, SR, [(562.085, Y_TRUNK), (562.085, 291.5625), (559.485, 294.1625)], W),
    # R: コネクタ pin10 → 裏で南西（TONE_R の表 y=256.48 は 0.25 mm の縦で直角に跨ぐ）→ ビア → 表で幹線へ
    (B, SR, [(517.729999, 252.29), (513.73, 256.29), (513.73, 256.54), (509.23, 261.04)], W),
    (F, SR, [(509.23, 261.04), (509.23, Y_TRUNK)], W),
    # L: 東の枝（既存の横線 y=253.05 から）
    (B, SL, [(510.26, 253.05), (510.26, 257.3)], W),
    (F, SL, [(510.26, 257.3), (513.26, 260.3), (517.26, 260.3), (523.51, 266.55), (523.51, 276.05), (527.76, 280.3)], W),
    (B, SL, [(527.76, 280.3), (530.01, 282.55), (530.01, 286.55), (525.7, 290.86), (525.7, 291.1), (527.3, 292.7)], W),
    # ±15V: 表に戻す
    (F, "/+15V", [(530.25, 281.3), (535.25, 281.3)], 1.0),
]
ADD_VIAS = [(SR, (509.23, 261.04)), (SL, (510.26, 257.3)), (SL, (527.76, 280.3))]


def find_track(board, layer, net, a, b, eps=0.012):
    hits = [t for t in board.GetTracks() if not hop.is_via(t) and t.GetLayer() == layer and t.GetNetname() == net
            and ((hop.near(hop.xy(t.GetStart()), a, eps) and hop.near(hop.xy(t.GetEnd()), b, eps))
                 or (hop.near(hop.xy(t.GetStart()), b, eps) and hop.near(hop.xy(t.GetEnd()), a, eps)))]
    if len(hits) != 1:
        raise SystemExit(f"{'F' if layer == F else 'B'} {net} {a}->{b}: {len(hits)} 本（1本を期待）")
    return hits[0]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--board", type=Path, default=PCB)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    board = pcbnew.LoadBoard(str(a.board))
    nc = board.GetNetcodeFromNetname
    d = hop.design(board)
    # 消すものは先に全部集めてからまとめて消す（SWIG のラッパーが壊れないように）
    doomed = [find_track(board, L, net, p, q) for L, net, p, q in REMOVE]
    for net, pt in REMOVE_VIAS:
        vs = [t for t in board.GetTracks() if hop.is_via(t) and t.GetNetname() == net
              and hop.near(hop.xy(t.GetPosition()), pt, 0.012)]
        if len(vs) != 1:
            raise SystemExit(f"ビア {net} {pt}: {len(vs)} 本（1本を期待）")
        doomed += vs
    sample = next(t for t in board.GetTracks() if hop.is_via(t) and t.GetNetname() == SL)
    via_w, via_d = hop.mm(sample.GetWidth(F)), hop.mm(sample.GetDrill())
    for t in doomed:
        board.Remove(t)
    # 全部足してから、衝突・角度・交差（新しい L と R どうしも含む）を見る。問題があれば保存しない
    for net, pt in ADD_VIAS:
        hop.add_via_like(board, pt, sample, nc(net))
    for L, net, pts, w in ADD:
        for p, q in zip(pts, pts[1:]):
            hop.add_track(board, p, q, L, hop.iu(w), nc(net))
    problems = []
    for L, net, pts, w in ADD:
        obs = hop.Obstacles(board, nc(net), layers=(L,))
        for p, q in zip(pts, pts[1:]):
            if not hop.octilinear(p, q):
                problems.append(f"{net} {p}->{q}: 45°/直交でない")
            problems += [f"{'F' if L == F else 'B'} {net} {p}->{q}: {h}" for h in obs.seg_hits(L, p, q, w, d["clr"])]
        if "AMP_SEL" in net:
            problems += hop.check_crossings(board, pts, L, own=net, strict_analog=True)
    for net, pt in ADD_VIAS:
        obs = hop.Obstacles(board, nc(net))
        problems += [f"ビア {net} {pt}: {h}" for h in obs.via_hits(pt, via_w, via_d, d["clr"], d["hole2hole"])
                     if "hole @(" + f"{pt[0]:.2f},{pt[1]:.2f})" not in h]
    if problems:
        print("問題あり。保存しない:")
        for pr in problems:
            print("  ", pr)
        return 2
    if a.dry_run:
        print("dry-run: 保存しない")
        return 0
    print(f"ゾーン再充填: {hop.refill(board, sheet_region(board, 'AmpBankRelay'))} 枚")
    board.Save(str(a.board))
    print(f"保存: {a.board}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
