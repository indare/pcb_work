#!/usr/bin/env python3
"""加算ノードまわりの 4 部品を、層の入れ替えを含めて置き直す。

plan_summing_node2.py が出した配置を適用する。旧パッドに端点を持っていた
配線は宙に浮くので削除し、引き直し待ちにする。

層をまたぐ部品は反転が入り、パッドの相対位置が鏡像になる。
そのため適用後に実際のパッド座標を読み戻して計画値と突き合わせ、
ずれていれば向きを 180° 補正し、それでも合わなければ保存せずに中止する。

  確認: kicad-python apply_summing_node.py board.kicad_pcb
  適用: kicad-python apply_summing_node.py board.kicad_pcb --apply
"""
import argparse
import math
import sys

import pcbnew

MM = pcbnew.ToMM
FM = pcbnew.FromMM

# ref: (x, y, rot, 層, {pad番号: (期待する絶対座標)})
PLAN = {
    "R31": (251.76, 92.08, 0, "B.Cu", {"1": (250.210, 92.080), "2": (253.310, 92.080)}),
    "R27": (251.76, 89.58, 180, "B.Cu", {"1": (253.310, 89.580), "2": (250.210, 89.580)}),
    "R32": (248.97, 99.70, 0, "B.Cu", {"1": (247.420, 99.700), "2": (250.520, 99.700)}),
    "R30": (243.72, 99.70, 0, "B.Cu", {"1": (242.170, 99.700), "2": (245.270, 99.700)}),
}
LIVE_NETS = {"Net-(AMP1A--)", "Net-(AMP1-Pad1)", "Net-(AMP1B--)", "Net-(AMP1-Pad7)"}
ISLAND = (219.0, 71.0, 287.0, 121.0)
TOL = 0.02


def prad(p):
    s = p.GetSize()
    return math.hypot(MM(s.x), MM(s.y)) / 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pcb")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    board = pcbnew.LoadBoard(args.pcb)
    fps = {}
    for f in board.GetFootprints():
        fps.setdefault(f.GetReference(), f)

    to_delete, seen = [], set()
    for ref in PLAN:
        fp = fps[ref]
        old = [(MM(p.GetPosition().x), MM(p.GetPosition().y), prad(p)) for p in fp.Pads()]
        x, y, deg, lay, _ = PLAN[ref]
        print(f"--- {ref} {fp.GetValue()}")
        print(f"    ({MM(fp.GetPosition().x):.2f}, {MM(fp.GetPosition().y):.2f}) "
              f"rot {fp.GetOrientationDegrees():.0f}° {board.GetLayerName(fp.GetLayer())}"
              f"  →  ({x}, {y}) rot {deg}° {lay}"
              + ("   ※層を入れ替え" if board.GetLayerName(fp.GetLayer()) != lay else ""))
        for t in board.GetTracks():
            # SWIG は反復ごとに別のプロキシを返すので id() では重複を判定できない。
            # また str(m_Uuid) はプロキシの repr であって UUID ではない。AsString() を使う。
            uid = t.m_Uuid.AsString()
            if t.Type() == pcbnew.PCB_VIA_T or uid in seen:
                continue
            for end in (t.GetStart(), t.GetEnd()):
                ex, ey = MM(end.x), MM(end.y)
                if any(math.hypot(ex - ox, ey - oy) <= orad for ox, oy, orad in old):
                    to_delete.append(t)
                    seen.add(uid)
                    print(f"      削除: {board.GetLayerName(t.GetLayer()):5s} "
                          f"{MM(t.GetLength()):5.2f} mm  {t.GetNetname()}")
                    break

    if not args.apply:
        print(f"\n[dry-run] 移動 {len(PLAN)} 件 / 削除 {len(to_delete)} 本。--apply で書き込む。")
        return

    for t in to_delete:
        board.Remove(t)

    for ref, (x, y, deg, lay, want) in PLAN.items():
        fp = fps[ref]
        target = pcbnew.F_Cu if lay == "F.Cu" else pcbnew.B_Cu
        if fp.GetLayer() != target:
            fp.SetLayerAndFlip(target)
        fp.SetPosition(pcbnew.VECTOR2I(FM(x), FM(y)))
        fp.SetOrientationDegrees(deg)

        def mismatch():
            worst = 0.0
            for p in fp.Pads():
                w = want.get(p.GetNumber())
                if w is None:
                    continue
                worst = max(worst, math.hypot(MM(p.GetPosition().x) - w[0],
                                              MM(p.GetPosition().y) - w[1]))
            return worst

        m = mismatch()
        if m > TOL:
            fp.SetOrientationDegrees((deg + 180) % 360)
            m2 = mismatch()
            print(f"    {ref}: 反転でパッドが鏡像化 → 向きを {(deg+180) % 360}° に補正（ずれ {m:.3f}→{m2:.3f}mm）")
            m = m2
        if m > TOL:
            sys.exit(f"中止: {ref} のパッドが計画位置に一致しない（ずれ {m:.3f}mm）。保存していない。")

    # 移動で行き場を失った短いスタブを掃除する。
    # 片端がそのネットのどのパッド・ビア・他の配線端にも触れていないものを消す。
    x0, y0, x1, y1 = ISLAND
    anchors = {}
    for f in board.GetFootprints():
        for pd in f.Pads():
            n = pd.GetNetname()
            if n in LIVE_NETS:
                q = pd.GetPosition()
                anchors.setdefault(n, []).append((MM(q.x), MM(q.y), prad(pd)))
    for t in board.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() in LIVE_NETS:
            q = t.GetPosition()
            anchors.setdefault(t.GetNetname(), []).append((MM(q.x), MM(q.y), 0.3))

    def free_end(track, end, others):
        ex, ey = MM(end.x), MM(end.y)
        for ax, ay, ar in anchors.get(track.GetNetname(), []):
            if math.hypot(ex - ax, ey - ay) <= ar:
                return False
        for o in others:
            if o.m_Uuid.AsString() == track.m_Uuid.AsString() or o.GetNetname() != track.GetNetname():
                continue
            for oe in (o.GetStart(), o.GetEnd()):
                if math.hypot(ex - MM(oe.x), ey - MM(oe.y)) < 0.01:
                    return False
        return True

    live = [t for t in board.GetTracks()
            if t.Type() != pcbnew.PCB_VIA_T and t.GetNetname() in LIVE_NETS
            and x0 < MM(t.GetStart().x) < x1 and y0 < MM(t.GetStart().y) < y1]
    stubs = [t for t in live
             if free_end(t, t.GetStart(), live) or free_end(t, t.GetEnd(), live)]
    for t in stubs:
        print(f"    スタブ削除: {board.GetLayerName(t.GetLayer()):5s} "
              f"{MM(t.GetLength()):5.2f} mm  {t.GetNetname()}")
        board.Remove(t)

    targets = pcbnew.ZONES()
    for z in board.Zones():
        if z.GetNetname() != "GND" or not z.IsFilled():
            continue
        bb = z.GetBoundingBox()
        if 220 < MM(bb.GetLeft()) < 230 and 70 < MM(bb.GetTop()) < 80:
            targets.append(z)
    pcbnew.ZONE_FILLER(board).Fill(targets)
    board.Save(args.pcb)
    print(f"\n配線 {len(to_delete)} 本を削除し、{len(PLAN)} 部品を移動して保存した。")

    # 保存後にもう一度 LoadBoard すると SIGBUS で落ちるため、
    # メモリ上のフットプリントからそのまま出す。
    print("\n移動後のパッド位置:")
    for ref in PLAN:
        f = fps[ref]
        for pd in f.Pads():
            print(f"   {ref}.{pd.GetNumber()}  ({MM(pd.GetPosition().x):7.3f}, "
                  f"{MM(pd.GetPosition().y):7.3f})  {board.GetLayerName(f.GetLayer()):5s}  "
                  f"{pd.GetNetname()}")


if __name__ == "__main__":
    main()
