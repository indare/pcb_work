#!/usr/bin/env python3
"""Amp 入力カップリング C602/C605/C702/C705 をソケット脇へ再配置する。

TONE_* → 大容量フィルム → Amp +/- 入力。TMUX 出力カップリングとは別物。
3層は保留。旧の長い斜め配線は消して短く引き直す。
"""
from __future__ import annotations

from pathlib import Path

import pcbnew

PCB = Path(__file__).resolve().parents[1] / "AudioV2Case.kicad_pcb"

REWRITE = {
    "Net-(AMP601A-+)",
    "Net-(AMP601B-+)",
    "Net-(AMP701A-+)",
    "Net-(AMP701B-+)",
}


def mm(x, y):
    return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))


def to_mm(v):
    return pcbnew.ToMM(v.x), pcbnew.ToMM(v.y)


def main() -> None:
    board = pcbnew.LoadBoard(str(PCB))
    fps = {f.GetReference(): f for f in board.GetFootprints()}

    def fp(ref):
        return fps[ref]

    def pad(ref, num):
        for p in fp(ref).Pads():
            if p.GetNumber() == str(num):
                return p
        raise KeyError((ref, num))

    def place(ref, x, y, rot):
        f = fp(ref)
        if f.IsFlipped():
            f.Flip(f.GetPosition(), True)
        f.SetOrientationDegrees(rot)
        f.SetPosition(mm(x, y))

    # P10 フィルム: rot0 で pad2 = pad1+(10,0)、rot180 で pad2 = pad1+(-10,0)
    # Amp 脇・バイアス抵抗の外側に置き、電源ピン列は避ける
    place("C602", 348.06, 176.47, 0)     # pad2@(358.06,176.47) → R601 / AMP601.3
    # CH3 タイル手前・Amp601 東（U_IO の巨大シルクは無視して本体空きを使う）
    place("C605", 396.00, 180.00, 180)   # pad2@(386.00,180.00) → R607 / AMP601.5
    place("C702", 395.55, 208.10, 180)    # pad2@(385.55,208.10) → R701 / AMP701.3
    place("C705", 342.00, 218.00, 0)      # pad2@(352.00,218.00) Amp701 南・板内

    # 旧配線削除（対象ネット全体。TONE バスは触らない）
    doomed = [t for t in board.GetTracks() if t.GetNetname() in REWRITE]
    for t in doomed:
        board.Remove(t)

    width = pcbnew.FromMM(0.5)

    def add_track(a, b, netcode):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(a)
        t.SetEnd(b)
        t.SetWidth(width)
        t.SetLayer(pcbnew.F_Cu)
        t.SetNetCode(netcode)
        board.Add(t)

    def ortho(a, b, netcode, first="x"):
        x1, y1 = to_mm(a)
        x2, y2 = to_mm(b)
        mid = mm(x2, y1) if first == "x" else mm(x1, y2)
        add_track(a, mid, netcode)
        if mid != b:
            add_track(mid, b, netcode)

    def link(a, b):
        add_track(a.GetPosition(), b.GetPosition(), a.GetNetCode())

    # C602.2 → R601.2 → AMP601.3
    link(pad("C602", "2"), pad("R601", "2"))
    ortho(pad("R601", "2").GetPosition(), pad("AMP601", "3").GetPosition(),
          pad("AMP601", "3").GetNetCode(), first="y")

    # C605.2 → 西へ → R607.1 → AMP601.5（+15V パッドの真上は通らない）
    p_c = pad("C605", "2").GetPosition()
    p_r = pad("R607", "1").GetPosition()
    p_a = pad("AMP601", "5").GetPosition()
    nc = pad("AMP601", "5").GetNetCode()
    cx, cy = to_mm(p_c)
    rx, ry = to_mm(p_r)
    ax, ay = to_mm(p_a)
    # まず y=180 のまま R607 の東まで、その後 R607 / Amp へ
    add_track(p_c, mm(rx + 1.0, cy), nc)
    add_track(mm(rx + 1.0, cy), mm(rx + 1.0, ry), nc)
    add_track(mm(rx + 1.0, ry), p_r, nc)
    ortho(p_r, p_a, nc, first="x")

    # C702.2 → R701.2 → AMP701.3
    link(pad("C702", "2"), pad("R701", "2"))
    ortho(pad("R701", "2").GetPosition(), pad("AMP701", "3").GetPosition(),
          pad("AMP701", "3").GetNetCode(), first="y")

    # C705.2 → 北へ → R707.1 → AMP701.5
    p_c = pad("C705", "2").GetPosition()
    p_r = pad("R707", "1").GetPosition()
    p_a = pad("AMP701", "5").GetPosition()
    nc = pad("AMP701", "5").GetNetCode()
    cx, cy = to_mm(p_c)
    rx, ry = to_mm(p_r)
    add_track(p_c, mm(cx, ry), nc)
    add_track(mm(cx, ry), p_r, nc)
    ortho(p_r, p_a, nc, first="x")

    board.Save(str(PCB))

    # 重なりチェック（近傍）
    check = [
        "C602", "C605", "C702", "C705",
        "AMP601", "AMP701",
        "R601", "R607", "R701", "R707",
        "R602", "R608", "R702", "R708",
        "R606", "R612", "R706", "R712", "R610", "R710",
        "C601", "C604", "C701", "C704", "C801",
    ]
    items = []
    for r in check:
        f = fp(r)
        items.append((r, f.GetBoundingBox(False, False), f.IsFlipped()))
    ols = []
    for i, (ra, ba, fa) in enumerate(items):
        for rb, bb, fb in items[i + 1 :]:
            if fa != fb:
                continue
            if ba.GetLeft() < bb.GetRight() and ba.GetRight() > bb.GetLeft() and ba.GetTop() < bb.GetBottom() and ba.GetBottom() > bb.GetTop():
                ox = pcbnew.ToMM(min(ba.GetRight(), bb.GetRight()) - max(ba.GetLeft(), bb.GetLeft()))
                oy = pcbnew.ToMM(min(ba.GetBottom(), bb.GetBottom()) - max(ba.GetTop(), bb.GetTop()))
                if ox > 0.3 and oy > 0.3:
                    ols.append(f"{ra}x{rb} {ox:.2f}x{oy:.2f}")

    print(f"removed {len(doomed)} tracks; saved {PCB}")
    for r in ["C602", "C605", "C702", "C705"]:
        f = fp(r)
        x, y = to_mm(f.GetPosition())
        print(f"  {r} ({x:.2f},{y:.2f}) rot={f.GetOrientationDegrees()} {'B' if f.IsFlipped() else 'F'}")
        for p in f.Pads():
            px, py = to_mm(p.GetPosition())
            print(f"    .{p.GetNumber()} ({px:.2f},{py:.2f}) {p.GetNetname()}")
    print("overlaps:", ols or "none")


if __name__ == "__main__":
    main()
