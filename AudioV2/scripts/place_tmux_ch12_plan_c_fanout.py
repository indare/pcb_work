#!/usr/bin/env python3
"""案C: U311 の S ピン引き出し + CH1/CH2 カップリング/47Ω/220k を北南へ置く。

前提: apply_tmux_plan_c_pcb.py 済み（TMUX 270°・ネット同期）。
      place_a2_slot_connectors.py 済み（北=J_ANA / 南=J_PWR）。
クリアランスは詰めない。TSSOP パッド上ビア禁止。
S=各ch出力（表・フィルム）。D=AMP_SEL バス（裏で短絡してよい）。
AMP_SEL: 南北 D 短絡はパッケージの外側を回す（パッド列に沿わせない）。
本線はビアで B.Cu へ落とし、北の J_ANA301（PTH）へ。±15V も裏前提（未配線）。
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

    # --- 配置（TMUX 北=CH1=ピン1–8 / 南=CH2=ピン9–16） ---
    # フィルム: CH パッドを S ピン x に揃え、Amp 側を外へ（FKS2 P5）
    pitch = 5.0
    s6x, _ = to_mm(pad("U311", "6").GetPosition())    # S4 CH1_OUT_L 西
    s3x, _ = to_mm(pad("U311", "3").GetPosition())    # S1 CH1_OUT_R 東
    s14x, _ = to_mm(pad("U311", "14").GetPosition())  # S2 CH2_OUT_L 東
    s11x, _ = to_mm(pad("U311", "11").GetPosition())  # S3 CH2_OUT_R 西
    # C601 pad1=Amp pad2=CH rot0 → CH が東
    place("C601", s6x - pitch, 183.00, 0)
    # C604 pad1=CH pad2=Amp rot0 → Amp 東
    place("C604", s3x, 183.00, 0)
    # C704 pad1=CH pad2=Amp / rot180 → Amp 西（CH2 R）
    place("C704", s11x, 200.00, 180)
    # C701 pad1=Amp pad2=CH / rot180 → CH 西（CH2 L、本体は東）
    place("C701", s14x + pitch, 200.00, 180)

    # 47Ω（DIP 本体の外・カップリングとのあいだ）
    place("R602", 360.50, 181.00, -90)  # Amp 西外
    place("R608", 386.00, 181.50, 90)   # Amp 東外・R704/R612 から離す
    place("R702", 386.00, 202.20, 90)   # Amp701 東外・R704 から離す
    place("R708", 358.00, 202.00, -90)  # Amp701 西外・R707 から離す

    # 220k はフィルムの外側。TMUX 北のビア通り道を空ける。
    place("R603", 362.00, 180.50, 180)
    place("R609", 378.00, 180.50, 0)
    place("R709", 362.00, 202.50, 180)
    place("R703", 378.00, 202.50, 0)

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

    # S → CH パッド（北へ/南へまっすぐ）
    link(pad("U311", "6"), pad("C601", "2"))
    link(pad("U311", "3"), pad("C604", "1"))
    link(pad("U311", "11"), pad("C704", "1"))
    link(pad("U311", "14"), pad("C701", "2"))

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

    # AMP_SEL: D ピン。ピン列に沿わせない。表はパッケージの外まで出してビア。
    # 南北短絡と本線は B.Cu（±15V と同じ層。S/TONE は表のまま）。
    p7, p15 = pad("U311", "7"), pad("U311", "15")   # D4 北 L / D2 南 L
    p2, p10 = pad("U311", "2"), pad("U311", "10")   # D1 北 R / D3 南 R
    _, y7 = to_mm(p7.GetPosition())
    _, y15 = to_mm(p15.GetPosition())
    _, y2 = to_mm(p2.GetPosition())
    _, y10 = to_mm(p10.GetPosition())
    y_n = min(y7, y2) - 2.5
    y_s_l = y15 + 2.5
    y_s_r = y10 + 4.5                   # L/R の南スタブが同じ Y で交差しない
    xw = 363.0
    xe = 377.0

    def add_via(x, y, netcode):
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(mm(x, y))
        v.SetViaType(pcbnew.VIATYPE_THROUGH)
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetWidth(pcbnew.FromMM(0.6))
        v.SetDrill(pcbnew.FromMM(0.3))
        v.SetNetCode(netcode)
        board.Add(v)

    def stub_via(src, vx, vy):
        sx, sy = to_mm(src.GetPosition())
        add_track(src.GetPosition(), mm(sx, vy), src.GetNetCode())
        add_track(mm(sx, vy), mm(vx, vy), src.GetNetCode())
        add_via(vx, vy, src.GetNetCode())

    stub_via(p7, xw, y_n)
    stub_via(p15, xw, y_s_l)
    stub_via(p2, xe, y_n)
    stub_via(p10, xe, y_s_r)
    add_track(mm(xw, y_n), mm(xw, y_s_l), p7.GetNetCode(), layer=pcbnew.B_Cu)
    add_track(mm(xe, y_n), mm(xe, y_s_r), p2.GetNetCode(), layer=pcbnew.B_Cu)

    # 本線: 北ビアから J_ANA へ。PTH なので裏からパッドに入れる。
    # ピン列（奇数 x=360 / 偶数 x=362.54）を横に走らせない。
    j7 = pad("J_ANA301", "7")    # AMP_SEL_L
    j10 = pad("J_ANA301", "10")  # AMP_SEL_R
    j7x, j7y = to_mm(j7.GetPosition())
    j10x, j10y = to_mm(j10.GetPosition())
    xl, xr = 346.0, j10x + 3.0         # L は C602 の西。ピン列を横に走らせない
    add_track(mm(xw, y_n), mm(xl, y_n), p7.GetNetCode(), layer=pcbnew.B_Cu)
    add_track(mm(xl, y_n), mm(xl, j7y), p7.GetNetCode(), layer=pcbnew.B_Cu)
    add_track(mm(xl, j7y), j7.GetPosition(), p7.GetNetCode(), layer=pcbnew.B_Cu)
    add_track(mm(xe, y_n), mm(xr, y_n), p2.GetNetCode(), layer=pcbnew.B_Cu)
    add_track(mm(xr, y_n), mm(xr, j10y), p2.GetNetCode(), layer=pcbnew.B_Cu)
    add_track(mm(xr, j10y), j10.GetPosition(), p2.GetNetCode(), layer=pcbnew.B_Cu)

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
