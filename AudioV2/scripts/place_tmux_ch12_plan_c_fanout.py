#!/usr/bin/env python3
"""案C: U311 の D ピン引き出し + CH1/CH2 カップリング/47Ω/220k を北南へ置く。

前提: apply_tmux_plan_c_pcb.py 済み（TMUX 90°・ネット同期）。
      place_a2_slot_connectors.py 済み（北=J_ANA / 南=J_PWR）。
クリアランスは詰めない。TSSOP パッド上ビア禁止。
AMP_SEL: 南北 S 短絡は東西の短い縦。本線は北の J_ANA301 へ（kivu 型）。
"""
from __future__ import annotations

from pathlib import Path

import pcbnew

PCB = Path(__file__).resolve().parents[1] / "AudioV2Case.kicad_pcb"

REWRITE = {
    "/AmpBankSwitch/CH1_OUT_L",
    "/AmpBankSwitch/CH1_OUT_R",
    "/AmpBankSwitch/CH2_OUT_L",
    "/AmpBankSwitch/CH2_OUT_R",
    "/AMP_SEL_L",
    "/AMP_SEL_R",
    "Net-(C601-Pad1)",
    "Net-(C604-Pad2)",
    "Net-(C701-Pad1)",
    "Net-(C704-Pad2)",
    "Net-(AMP601-Pad1)",
    "Net-(AMP601-Pad7)",
    "Net-(AMP701-Pad1)",
    "Net-(AMP701-Pad7)",
}
# AMP_SEL 本線は J_ANA301（北）まで伸ばすので、削除窓を北方向に広めに取る
REWRITE_WINDOW = (35.0, 55.0)  # (|dx|, |dy|) from U311


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

    def set_front(ref):
        f = fp(ref)
        if f.IsFlipped():
            f.Flip(f.GetPosition(), True)

    def place(ref, x, y, rot):
        set_front(ref)
        f = fp(ref)
        f.SetOrientationDegrees(rot)
        f.SetPosition(mm(x, y))

    # --- 配置（TMUX 北=CH1 / 南=CH2、余裕） ---
    # フィルム: CH パッドを D ピン x に揃え、Amp 側を外へ
    # C601 pad1=Amp pad2=CH rot0 → CH が東。CH をピン15 x に: pad2@(368.38,183.0) → pad1@363.38
    place("C601", 363.38, 183.00, 0)
    # C604 pad1=CH pad2=Amp rot0 → Amp 東。CH@(371.63,183.0)
    place("C604", 371.63, 183.00, 0)
    # C704 pad1=CH pad2=Amp / rot180 → Amp 西。CH@(368.38,200.0) → Amp@363.38
    place("C704", 368.38, 200.00, 180)
    # C701 pad1=Amp pad2=CH / rot180 → CH 西。CH@(371.63,200.0) → Amp@376.63
    place("C701", 376.63, 200.00, 180)

    # 47Ω（DIP 本体の外・カップリングとのあいだ）
    place("R602", 360.50, 181.00, -90)  # Amp 西外
    place("R608", 381.50, 181.50, 90)   # Amp 東外・R607 から離す
    place("R702", 381.50, 202.20, 90)   # Amp701 東外
    place("R708", 358.00, 202.00, -90)  # Amp701 西外・R707 から離す

    # 220k（CH 近傍・表面）
    place("R603", 366.00, 185.50, 180)  # pad1東寄り CH1_L
    place("R609", 374.00, 185.50, 0)
    place("R709", 366.00, 197.50, 180)
    place("R703", 374.00, 197.50, 0)

    # --- 旧配線削除（U311 近傍の対象ネット） ---
    ux, uy = to_mm(fp("U311").GetPosition())
    wx, wy = REWRITE_WINDOW
    doomed = []
    for t in board.GetTracks():
        if t.GetNetname() not in REWRITE:
            continue
        for end in (t.GetStart(), t.GetEnd()):
            ex, ey = to_mm(end)
            if abs(ex - ux) < wx and abs(ey - uy) < wy:
                doomed.append(t)
                break
    for t in doomed:
        board.Remove(t)

    width = pcbnew.FromMM(0.4)

    def add_track(p1, p2, netcode, layer=pcbnew.F_Cu):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(p1)
        t.SetEnd(p2)
        t.SetWidth(width)
        t.SetLayer(layer)
        t.SetNetCode(netcode)
        board.Add(t)

    def ortho(a, b, netcode, first="y"):
        x1, y1 = to_mm(a)
        x2, y2 = to_mm(b)
        mid = mm(x2, y1) if first == "x" else mm(x1, y2)
        add_track(a, mid, netcode)
        if mid != b:
            add_track(mid, b, netcode)

    def link(a, b):
        add_track(a.GetPosition(), b.GetPosition(), a.GetNetCode())

    # D → CH パッド（北へ/南へまっすぐ）
    link(pad("U311", "15"), pad("C601", "2"))
    link(pad("U311", "10"), pad("C604", "1"))
    link(pad("U311", "2"), pad("C704", "1"))
    link(pad("U311", "7"), pad("C701", "2"))

    # 220k
    link(pad("R603", "1"), pad("C601", "2"))
    link(pad("R609", "1"), pad("C604", "1"))
    link(pad("R709", "1"), pad("C704", "1"))
    link(pad("R703", "1"), pad("C701", "2"))

    # フィルム Amp 側 → 47Ω
    def amp_side(cref, key):
        return next(p for p in fp(cref).Pads() if key not in p.GetNetname())

    for rref, cref, key in [
        ("R602", "C601", "CH1_OUT_L"),
        ("R608", "C604", "CH1_OUT_R"),
        ("R702", "C701", "CH2_OUT_L"),
        ("R708", "C704", "CH2_OUT_R"),
    ]:
        cp = amp_side(cref, key)
        rp = next(p for p in fp(rref).Pads() if p.GetNetname() == cp.GetNetname())
        ortho(cp.GetPosition(), rp.GetPosition(), cp.GetNetCode(), first="y")

    # 47Ω → Amp + フィードバック
    def stitch_out(rref, ampref, amp_pin, fb_ref, fb_pin, key):
        p_amp = pad(ampref, amp_pin)
        p_fb = pad(fb_ref, fb_pin)
        p_r = next(p for p in fp(rref).Pads() if key in p.GetNetname())
        link(p_amp, p_fb)
        ortho(p_r.GetPosition(), p_amp.GetPosition(), p_amp.GetNetCode(), first="y")

    stitch_out("R602", "AMP601", "1", "R606", "1", "AMP601-Pad1")
    stitch_out("R608", "AMP601", "7", "R612", "2", "AMP601-Pad7")
    stitch_out("R702", "AMP701", "1", "R706", "1", "AMP701-Pad1")
    stitch_out("R708", "AMP701", "7", "R712", "2", "AMP701-Pad7")

    # AMP_SEL: 南北 S の短絡は東西の短い縦だけ（本線とは分離）
    # L: pin14 (北) ↔ pin6 (南) — 西へ出して縦
    p14, p6 = pad("U311", "14"), pad("U311", "6")
    x14, y14 = to_mm(p14.GetPosition())
    x6, y6 = to_mm(p6.GetPosition())
    xw = min(x14, x6) - 3.0
    pts = [p14.GetPosition(), mm(xw, y14), mm(xw, y6), p6.GetPosition()]
    for a, b in zip(pts, pts[1:]):
        add_track(a, b, p14.GetNetCode())

    # R: pin11 (北) ↔ pin3 (南) — 東へ出して縦
    p11, p3 = pad("U311", "11"), pad("U311", "3")
    x11, y11 = to_mm(p11.GetPosition())
    x3, y3 = to_mm(p3.GetPosition())
    xe = max(x11, x3) + 3.0
    pts = [p11.GetPosition(), mm(xe, y11), mm(xe, y3), p3.GetPosition()]
    for a, b in zip(pts, pts[1:]):
        add_track(a, b, p11.GetNetCode())

    # 本線（kivu 型）: 北辺の S から北の J_ANA301 へ
    # A2: J_ANA はカード北辺。pin7=AMP_SEL_L / pin10=AMP_SEL_R
    j7 = pad("J_ANA301", "7")
    j10 = pad("J_ANA301", "10")
    # 北辺ピン → いったん真北へ出してからコネクタへ（タイルを跨がない）
    for src, dst in ((p14, j7), (p11, j10)):
        sx, sy = to_mm(src.GetPosition())
        dx, dy = to_mm(dst.GetPosition())
        # 北へ（Y 減）クリアしてから X 合わせ
        y_bus = min(sy, dy) - 2.0
        pts = [src.GetPosition(), mm(sx, y_bus), mm(dx, y_bus), dst.GetPosition()]
        for a, b in zip(pts, pts[1:]):
            if a != b:
                add_track(a, b, src.GetNetCode())

    board.Save(str(PCB))

    # 重なりざっくり
    refs = [
        "U311", "C601", "C604", "C701", "C704",
        "R602", "R603", "R608", "R609", "R702", "R703", "R708", "R709",
        "AMP601", "AMP701",
    ]
    items = []
    for r in refs:
        f = fp(r)
        b = f.GetBoundingBox(False, False)
        items.append((r, b, f.IsFlipped()))
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
    print("overlaps:", ols or "none")
    for r in ["C601", "C604", "C701", "C704", "R602", "R608"]:
        f = fp(r)
        x, y = to_mm(f.GetPosition())
        print(f"  {r} ({x:.2f},{y:.2f}) rot={f.GetOrientationDegrees()}")


if __name__ == "__main__":
    main()
