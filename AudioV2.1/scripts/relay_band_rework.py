#!/usr/bin/env python3
"""リレー娘: リレー列と U321（TBD62083）の間の帯を組み直す（2026-09-24）。

問題（実測）:
  - CH3/CH4 のコイル駆動線が U321 の上下の列の間を東へ抜け、COMMON（pin10）と GND（pin9）を
    表でも裏でも隔てていた → 駆動 IC の足元にデカップを置けない
  - 裏の CH4_RSTC / CH4_SETC が AMP_SEL_L の裏の横線と同じ層で約 36 mm 平行（間隔 2.15 / 4.15 mm）
  - +5V_COIL は J_PWR から基板の左端を大回り（約 90 mm）してリレー列へ。100 nF（C322）は U321 から 36 mm

組み直し:
  段1 駆動線 CH3/CH4 を上の列から北へ出し、表のレーン（y 297.9〜300.0）で東へ → K303/K304 のコイルへ 45° で入る
  段3 AMP_SEL_L: K302 の pin7 は表 y=293.95 を東へ延ばして x=527.3 の裏の縦線にビアで合流。
      裏の横線（y=300.67）は外し、南 y=304.8 に L のバスを新設、K303/K304 の pin7 へは列の東脇から立ち上げる
      （コイルレーンとは直角に交差）
  段2 C322（100 nF → 0603）を U321 の pin10/pin9 の間の裏へ。+5V_COIL は J_PWR302 pin5 から裏 0.3 mm で
      表の GND_COIL の真裏を上げ、C322 の＋側へ（供給と帰りを重ねてループを潰す）。左端の大回りは外す

    python3 AudioV2.1/scripts/relay_band_rework.py --board out/relay/try.kicad_pcb --dry-run
    python3 AudioV2.1/scripts/relay_band_rework.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).resolve().parent))
import amp_sel_hop as hop  # noqa: E402
import place_tmux_1u as p1u  # noqa: E402
from pcb_preview import sheet_region  # noqa: E402

PCB = Path(__file__).resolve().parents[1] / "AudioV2Case.kicad_pcb"
F, B = hop.F, hop.B
C0603 = "Capacitor_SMD:C_0603_1608Metric_Pad1.08x0.95mm_HandSolder"
R = "/AmpBankRelay/"

# 外す線（層, 始点, 終点）。座標は 0.01 mm で突き合わせる
REMOVE = [
    # 段1: 列の間を抜けていた駆動線と、表の CH3_SETC（引き直す）
    (F, R + "CH3_SETC", (510.86, 302.235), (513.045, 300.05)), (F, R + "CH3_SETC", (513.045, 300.05), (523.03, 300.05)),
    (F, R + "CH3_SETC", (523.03, 300.05), (524.25, 301.27)), (F, R + "CH3_SETC", (524.25, 301.27), (527.3575, 301.27)),
    (F, R + "CH3_SETC", (527.3575, 301.27), (532.045, 296.5825)),
    (F, R + "CH3_RSTC", (513.4, 302.235), (515.465, 304.3)), (F, R + "CH3_RSTC", (515.465, 304.3), (531.9475, 304.3)),
    (F, R + "CH3_RSTC", (531.9475, 304.3), (539.665, 296.5825)),
    (B, R + "CH4_SETC", (515.94, 302.235), (518.005, 304.3)), (B, R + "CH4_SETC", (518.005, 304.3), (555.75, 304.3)),
    (B, R + "CH4_SETC", (555.75, 304.3), (556.75, 303.3)), (F, R + "CH4_SETC", (556.75, 303.3), (556.75, 300.05)),
    (F, R + "CH4_SETC", (556.75, 300.05), (557.5, 299.3)), (B, R + "CH4_SETC", (557.5, 299.3), (559.485, 297.315)),
    (B, R + "CH4_SETC", (559.485, 297.315), (559.485, 296.7025)),
    (B, R + "CH4_RSTC", (518.48, 302.235), (520.045, 303.8)), (B, R + "CH4_RSTC", (520.045, 303.8), (521.75, 303.8)),
    (B, R + "CH4_RSTC", (521.75, 303.8), (523.25, 302.3)), (B, R + "CH4_RSTC", (523.25, 302.3), (561.5075, 302.3)),
    (B, R + "CH4_RSTC", (561.5075, 302.3), (567.105, 296.7025)),
    # 段3: L の表の斜め線と裏の横線・斜め線
    (F, "/AMP_SEL_L", (518.8425, 293.9525), (522.33, 297.44)), (F, "/AMP_SEL_L", (522.33, 297.44), (522.37, 297.44)),
    (F, "/AMP_SEL_L", (522.37, 297.44), (525.6, 300.67)), (F, "/AMP_SEL_L", (525.6, 300.67), (525.58, 300.69)),
    (B, "/AMP_SEL_L", (525.6, 300.67), (527.29, 300.67)), (B, "/AMP_SEL_L", (527.3, 300.03), (527.94, 300.67)),
    (B, "/AMP_SEL_L", (527.31, 300.67), (532.74, 300.67)), (B, "/AMP_SEL_L", (532.74, 300.67), (532.75, 300.68)),
    (B, "/AMP_SEL_L", (532.75, 300.68), (560.5875, 300.68)), (B, "/AMP_SEL_L", (560.5875, 300.68), (567.105, 294.1625)),
    (B, "/AMP_SEL_L", (539.3875, 294.0425), (532.75, 300.68)), (B, "/AMP_SEL_L", (539.665, 294.0425), (539.3875, 294.0425)),
    # 段2: +5V_COIL の左端の大回りと旧 C322 まわり
    (F, "/+5V_COIL", (494.5, 327.3625), (494.5, 329.55)), (F, "/+5V_COIL", (494.5, 329.55), (494.5, 333.55)),
    (F, "/+5V_COIL", (494.5, 333.55), (500.75, 339.8)), (F, "/+5V_COIL", (500.75, 339.8), (503.08, 339.8)),
    (F, "/+5V_COIL", (494.5, 329.55), (492.75, 327.8)), (F, "/+5V_COIL", (492.75, 327.8), (492.75, 307.8)),
    (F, "/+5V_COIL", (492.75, 307.8), (485.1, 300.15)), (F, "/+5V_COIL", (485.1, 300.15), (469.02, 300.15)),
    (F, "/+5V_COIL", (469.02, 300.15), (465.815635, 296.945635)),
    (F, "/+5V_COIL", (465.815635, 296.945635), (465.815635, 286.774365)),
    (F, "/+5V_COIL", (465.815635, 286.774365), (466.37, 286.22)), (F, "/+5V_COIL", (466.37, 286.22), (475.9825, 286.22)),
    (F, "/+5V_COIL", (475.9825, 286.22), (475.995, 286.2325)),
    (F, "/GND_COIL", (494.5, 324.2375), (495.4275, 324.2375)), (F, "/GND_COIL", (495.4275, 324.2375), (495.5525, 324.2375)),
    (F, "/GND_COIL", (495.5525, 324.2375), (496.49, 323.3)), (F, "/GND_COIL", (496.49, 323.3), (503.0, 323.3)),
]
REMOVE_VIAS = [("/AMP_SEL_L", (525.6, 300.67)), (R + "CH4_SETC", (556.75, 303.3)), (R + "CH4_SETC", (557.5, 299.3)),
               # コイル帯の A_GND ステッチ3本（どの線にもつながらない。1本は表のレーンを塞いでいた）。
               # A_GND の表裏は帯の外のステッチでつながっている（外したあと DRC の未接続・孤島で確認）
               ("/A_GND", (549.75, 299.55)), ("/A_GND", (551.0, 301.55)), ("/A_GND", (551.5, 303.3))]
MOVE_VIAS: list = []

W = 0.2
# 足す線（層, ネット, 折れ線, 幅）
ADD = [
    # 段1: 上の列から北へ出して表のレーンへ
    (F, R + "CH3_SETC", [(510.86, 302.235), (510.86, 300.2), (513.16, 297.9), (530.7275, 297.9), (532.045, 296.5825)], W),
    (F, R + "CH3_RSTC", [(513.4, 302.235), (513.4, 299.3), (514.1, 298.6), (537.6475, 298.6), (539.665, 296.5825)], W),
    (F, R + "CH4_SETC", [(515.94, 302.235), (515.94, 300.0), (516.64, 299.3), (556.8875, 299.3), (559.485, 296.7025)], W),
    (F, R + "CH4_RSTC", [(518.48, 302.235), (518.48, 300.7), (519.18, 300.0), (563.8075, 300.0), (567.105, 296.7025)], W),
    # 段3: L
    # 合流点の東隣に A_GND ステッチビア (528.05, 293.95) があるので、45° で北へ上げてから合流
    (F, "/AMP_SEL_L", [(518.8425, 293.9525), (526.0475, 293.9525), (527.3, 292.7)], W),
    (B, "/AMP_SEL_L", [(527.3, 300.03), (527.3, 304.1), (528.0, 304.8), (568.5, 304.8), (569.2, 304.1), (569.2, 296.2525),
                       (567.105, 294.1575)], W),
    (B, "/AMP_SEL_L", [(541.6, 304.8), (541.6, 295.9775), (539.665, 294.0425)], W),
    # 段2: +5V_COIL の近道（GND_COIL の真裏）と C322 の足
    (B, "/+5V_COIL", [(517.58, 337.48), (518.85, 336.21), (518.85, 333.2), (519.73, 332.32), (519.73, 306.48),
                      (521.02, 305.19)], 0.3),
    (B, "/+5V_COIL", [(521.02, 305.19), (521.02, 302.235)], 0.3),
    (B, "/GND_COIL", [(521.02, 306.91), (521.02, 309.855)], 0.3),
]
ADD_VIAS = [("/AMP_SEL_L", (527.3, 292.7))]
C322 = ("C322", 521.02, 306.05, 270)   # 0603 縦置き、pad1(+5V_COIL)=北・pad2(GND_COIL)=南
SPLIT = [(B, "/AMP_SEL_L", (527.3, 292.7))]   # 合流点で既存の縦線を分割


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
    clr = hop.design(board)["clr"]
    # 消すものは先に全部集めてからまとめて消す（1本ずつ消しながら GetTracks() を取り直すと
    # SWIG のラッパーが壊れる）。消した物への参照は最後まで持っておく
    doomed = [find_track(board, L, net, p, q) for L, net, p, q in REMOVE]
    doomed += [next(t for t in board.GetTracks() if hop.is_via(t) and t.GetNetname() == net
                    and hop.near(hop.xy(t.GetPosition()), pt, 0.012)) for net, pt in REMOVE_VIAS]
    for t in doomed:
        board.Remove(t)
    for net, old, new in MOVE_VIAS:
        next(t for t in board.GetTracks() if hop.is_via(t) and t.GetNetname() == net
             and hop.near(hop.xy(t.GetPosition()), old, 0.012)).SetPosition(hop.P(*new))
    for L, net, pt in SPLIT:
        t = next(t for t in board.GetTracks() if not hop.is_via(t) and t.GetLayer() == L and t.GetNetname() == net
                 and hop.on_segment(pt, hop.xy(t.GetStart()), hop.xy(t.GetEnd()))
                 and not hop.near(pt, hop.xy(t.GetStart())) and not hop.near(pt, hop.xy(t.GetEnd())))
        s, e, w = hop.xy(t.GetStart()), hop.xy(t.GetEnd()), t.GetWidth()
        board.Remove(t)
        hop.add_track(board, s, pt, L, w, nc(net))
        hop.add_track(board, pt, e, L, w, nc(net))
    # C322 を 0603 にして U321 の足元（裏）へ
    ref, x, y, rot = C322
    old = board.FindFootprintByReference(ref)
    nets = {p.GetNumber(): p.GetNetname() for p in old.Pads()}
    path, sn, sf, val = old.GetPath(), old.GetSheetname(), old.GetSheetfile(), old.GetValue()
    board.Remove(old)
    fp = p1u.load_fp(C0603)
    lib, name = C0603.split(":", 1)
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    fp.SetReference(ref)
    fp.SetValue(val)
    fp.SetPath(path)
    fp.SetSheetname(sn)
    fp.SetSheetfile(sf)
    board.Add(fp)
    fp.SetPosition(hop.P(x, y))
    fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
    fp.SetOrientationDegrees(rot)
    for p in fp.Pads():
        p.SetNet(board.FindNet(nets[p.GetNumber()]))
    print("C322: " + ", ".join(f"{p.GetNumber()}={p.GetNetname()}@{hop.xy(p.GetPosition())}" for p in fp.Pads()))
    # 足す前に衝突を見る（KiCad の形状で）
    problems = []
    for L, net, pts, w in ADD:
        obs = hop.Obstacles(board, nc(net), layers=(L,))
        for p, q in zip(pts, pts[1:]):
            if not hop.octilinear(p, q):
                problems.append(f"{net} {p}->{q}: 45°/直交でない")
            problems += [f"{'F' if L == F else 'B'} {net} {p}->{q}: {h}" for h in obs.seg_hits(L, p, q, w, clr)]
        if "AMP_SEL" in net:
            problems += hop.check_crossings(board, pts, L, own=net, strict_analog=True)
    for net, pt in ADD_VIAS + [(n, new) for n, _, new in MOVE_VIAS]:
        obs = hop.Obstacles(board, nc(net))
        problems += [f"ビア {net} {pt}: {h}" for h in obs.via_hits(pt, 0.6, 0.3, clr, 0.25)]
    if problems:
        print("衝突あり。保存しない:")
        for pr in problems:
            print("  ", pr)
        return 2
    sample = next(t for t in board.GetTracks() if hop.is_via(t) and t.GetNetname() == "/AMP_SEL_L")
    for net, pt in ADD_VIAS:
        hop.add_via_like(board, pt, sample, nc(net))
    for L, net, pts, w in ADD:
        for p, q in zip(pts, pts[1:]):
            hop.add_track(board, p, q, L, hop.iu(w), nc(net))
    if not p1u.place_ref(board, fp):
        print("  ⚠ C322 の参照番号を置ける場所が無い（そのまま）")
    if a.dry_run:
        print("dry-run: 保存しない")
        return 0
    # MCP 周りの D_GND ベタ（優先度 6）は孤立片を残す設定（never）だったので、近道と C322 の間などに
    # どこにもつながらない切れ端（0.2 / 1.2 mm²）ができる。既に設定済みの最小面積（10 mm²）未満の
    # 孤立片だけ消す設定（area）にする。パッドにつながる銅は孤立片ではないので消えない
    for z in board.Zones():
        if z.GetNetname() == "/D_GND" and z.GetAssignedPriority() == 6:
            z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_AREA)
    print(f"ゾーン再充填: {hop.refill(board, sheet_region(board, 'AmpBankRelay'))} 枚")
    board.Save(str(a.board))
    print(f"保存: {a.board}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
