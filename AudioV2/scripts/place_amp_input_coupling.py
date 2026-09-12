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

    # P5 フィルム（B32529C0105J000 / L7.2 W4.5）。KiCad THT の原点は pad1。
    # rot0 で pad2 = pad1+(5,0)、rot180 で pad2 = pad1+(-5,0)
    # Amp 脇・バイアス抵抗の外側に置き、電源ピン列は避ける
    place("C602", 353.06, 176.47, 0)     # pad2@(358.06,176.47) → R601 / AMP601.3
    # pad2 をバイアス抵抗の Amp 側パッドに載せる（GND パッドを横断しない）
    # C605 は R608（出力 47Ω）の北。Y=180 だと R608 に乗る。
    place("C605", 382.22, 165.00, 180)   # pad2@(377.22,165.00) = R607.1 の X。GND パッドを横断しない
    place("C702", 385.55, 211.50, 180)   # pad2@(380.55,211.50) → 北へ R701.2（GND を跨がない）
    place("C705", 357.78, 218.00, 0)     # pad2@(362.78,218.00) = R707.1 の X（GND を横断しない）

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

    # C602: R601 の Amp 側パッドだけに触る（GND パッドを横断しない）
    p_c = pad("C602", "2")
    p_r = next(p for p in fp("R601").Pads() if "A_GND" not in p.GetNetname())
    add_track(p_c.GetPosition(), mm(to_mm(p_r.GetPosition())[0], to_mm(p_c.GetPosition())[1]),
              p_c.GetNetCode())
    add_track(mm(to_mm(p_r.GetPosition())[0], to_mm(p_c.GetPosition())[1]),
              p_r.GetPosition(), p_c.GetNetCode())
    ortho(p_r.GetPosition(), pad("AMP601", "3").GetPosition(),
          pad("AMP601", "3").GetNetCode(), first="y")

    # C605.2 → 南へ R607 の東 → 西へ R607.1 → AMP601.5
    p_c = pad("C605", "2").GetPosition()
    p_r = pad("R607", "1").GetPosition()
    p_a = pad("AMP601", "5").GetPosition()
    nc = pad("AMP601", "5").GetNetCode()
    cx, cy = to_mm(p_c)
    rx, ry = to_mm(p_r)
    add_track(p_c, mm(cx, ry), nc)
    add_track(mm(cx, ry), p_r, nc)
    ortho(p_r, p_a, nc, first="x")

    # C702.2 → 北へ R701.2（同じ X。GND パッドは東なので跨がない）
    add_track(pad("C702", "2").GetPosition(), pad("R701", "2").GetPosition(),
              pad("R701", "2").GetNetCode())
    ortho(pad("R701", "2").GetPosition(), pad("AMP701", "3").GetPosition(),
          pad("AMP701", "3").GetNetCode(), first="y")

    # C705.2 → 北へ R707.1（同じ X）→ AMP701.5
    p_c = pad("C705", "2").GetPosition()
    p_r = pad("R707", "1").GetPosition()
    p_a = pad("AMP701", "5").GetPosition()
    nc = pad("AMP701", "5").GetNetCode()
    add_track(p_c, p_r, nc)
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
