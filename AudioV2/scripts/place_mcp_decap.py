#!/usr/bin/env python3
"""MCP23017 の 100 nF（C_IO301 / C_IO302）を 0603 にして、VDD（pin9）・VSS（pin10）の真上（本体の下の裏）へ。

いままでは 1206 を本体の下の裏に置き、3V3 側だけ線で足へ（Relay は 5 mm の斜め線）、
GND 側は線が無く D_GND のベタとステッチビア経由で VSS へ戻っていた。VDD と VSS は隣り合う足
（2.54 mm）なので、0603 の電源パッドを pin9 の真上、GND パッドを pin10 の脇に置き、
両側を約 1.6 mm の裏の線で足へ直結する（ループは足2本の間で閉じる）。

  Switch: 既存の 3V3 の縦線（パッド → pin9）の上に電源パッドが乗る。足すのは GND パッド → pin10 だけ
  Relay:  3V3 の斜め線（旧パッド → pin9）を、旧パッドの節点 → 新しい電源パッド → pin9 に付け替える。
          置き場所に重なる D_GND のステッチビアを1本外す（他の2本とベタで足りる）

    python3 AudioV2/scripts/place_mcp_decap.py --board out/relay/mcp_try.kicad_pcb --dry-run
    python3 AudioV2/scripts/place_mcp_decap.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).resolve().parent))
import amp_sel_hop as hop  # noqa: E402
import place_tmux_1u as p1u  # noqa: E402
from place_tmux_100n_underbody import swap_to_0603  # noqa: E402
from pcb_preview import sheet_region  # noqa: E402

PCB = Path(__file__).resolve().parents[1] / "AudioV2Case.kicad_pcb"
B = hop.B
W = 0.2

# ref: (中心 x, y, 回転, 期待する電源パッド位置, 外す B 線, 足す B 折れ線, 外すビア, 再充填する基板)
SPEC = {
    "C_IO301": dict(at=(550.4975, 209.36, 0), pwr=(549.635, 209.36),
                    remove=[], add=[("/D_GND", [(551.36, 209.36), (552.175, 210.175), (552.175, 210.97)])],
                    vias=[], sheet="AmpBankSwitch"),
    "C_IO302": dict(at=(521.8625, 319.25, 0), pwr=(521.0, 319.25),
                    remove=[((524.5625, 317.2975), (521.0, 320.86))],
                    add=[("/3V3", [(524.5625, 317.2975), (522.9525, 317.2975), (521.0, 319.25), (521.0, 320.86)]),
                         ("/D_GND", [(522.725, 319.25), (523.54, 320.065), (523.54, 320.86)])],
                    vias=[("/D_GND", (521.25, 318.8))], sheet="AmpBankRelay"),
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--board", type=Path, default=PCB)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    board = pcbnew.LoadBoard(str(a.board))
    clr = hop.design(board)["clr"]
    nc = board.GetNetcodeFromNetname
    doomed = []
    for ref, s in SPEC.items():
        for p, q in s["remove"]:
            doomed.append(next(t for t in board.GetTracks() if not hop.is_via(t) and t.GetLayer() == B
                               and t.GetNetname() == "/3V3" and {hop.xy(t.GetStart()), hop.xy(t.GetEnd())} == {p, q}))
        for net, pt in s["vias"]:
            doomed.append(next(t for t in board.GetTracks() if hop.is_via(t) and t.GetNetname() == net
                               and hop.near(hop.xy(t.GetPosition()), pt)))
    for t in doomed:
        board.Remove(t)
    problems = []
    for ref, s in SPEC.items():
        x, y, rot = s["at"]
        fp = swap_to_0603(board, ref, x, y, rot)
        pads = {p.GetNetname(): hop.xy(p.GetPosition()) for p in fp.Pads()}
        print(f"{ref}: " + ", ".join(f"{n}@{q}" for n, q in pads.items()))
        if not hop.near(pads["/3V3"], s["pwr"], 0.01):
            problems.append(f"{ref}: 電源パッドが {pads['/3V3']}（{s['pwr']} を期待。回転を見直す）")
        for net, pts in s["add"]:
            for p, q in zip(pts, pts[1:]):
                hop.add_track(board, p, q, B, hop.iu(W), nc(net))
    for ref, s in SPEC.items():
        for net, pts in s["add"]:
            obs = hop.Obstacles(board, nc(net), layers=(B,))
            for p, q in zip(pts, pts[1:]):
                if not hop.octilinear(p, q):
                    problems.append(f"{ref} {net} {p}->{q}: 45°/直交でない")
                problems += [f"{ref} {net} {p}->{q}: {h}" for h in obs.seg_hits(B, p, q, W, clr)]
        fp = board.FindFootprintByReference(ref)
        for p in fp.Pads():
            obs = hop.Obstacles(board, p.GetNetCode(), layers=(B,))
            pp = hop.xy(p.GetPosition())
            problems += [f"{ref}.{p.GetNumber()}: {h}" for h in obs.hits(B, p.GetEffectiveShape(B), (*pp, *pp), clr)
                         if not h.startswith(f"pad {ref}.")]
    if problems:
        print("問題あり。保存しない:")
        for pr in problems:
            print("  ", pr)
        return 2
    for ref in SPEC:
        if not p1u.place_ref(board, board.FindFootprintByReference(ref)):
            print(f"  ⚠ {ref} の参照番号を置ける場所が無い（そのまま）")
    if a.dry_run:
        print("dry-run: 保存しない")
        return 0
    for s in SPEC.values():
        print(f"ゾーン再充填 {s['sheet']}: {hop.refill(board, sheet_region(board, s['sheet']))} 枚")
    board.Save(str(a.board))
    print(f"保存: {a.board}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
