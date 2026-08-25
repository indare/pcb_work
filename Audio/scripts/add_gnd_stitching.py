#!/usr/bin/env python3
"""AMP 島の GND ベタに縫合ビアを追加する。

F 面と B 面の GND ゾーンが両方とも埋まっている場所だけを選び、
既存の銅から十分離れた位置に、ネットクラス Default の via を打つ。

  適用前の確認:  kicad-python add_gnd_stitching.py
  実際に書き込む: kicad-python add_gnd_stitching.py --apply

kicad-python は KiCad 同梱の python3.9（pcbnew が import できるもの）。
"""
import argparse
import math
import sys

import pcbnew

MM = pcbnew.ToMM
FM = pcbnew.FromMM

# AMP 島の範囲。MeasurementADC 島には触らない。
ISLAND = (219.0, 71.0, 287.0, 121.0)

VIA_DIA_MM = 0.6      # ネットクラス Default
VIA_DRILL_MM = 0.3
TARGET_MM = 10.0      # ベタ上の任意点から最寄ビアまでの目標上限

# 候補点が満たすべき離隔（すべて中心からの距離）
CLR_PAD_MM = 2.0      # パッド中心から
CLR_TRACK_OTHER_MM = 1.5   # GND 以外の配線の芯から
CLR_TRACK_GND_MM = 1.0     # GND 配線の芯から
CLR_VIA_MM = 2.5      # 既存ビアから
CLR_COURTYARD_MM = 1.0  # THT 部品のコートヤード外形から（缶の座面に当てない）
FIT_RADIUS_MM = 0.55  # この半径の円が両面ともベタに乗っていること
VIA_RADIUS_MM = VIA_DIA_MM / 2


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def seg_dist(p, a, b):
    vx, vy = b[0] - a[0], b[1] - a[1]
    L = vx * vx + vy * vy
    if L == 0:
        return dist(p, a)
    t = max(0.0, min(1.0, ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / L))
    return math.hypot(p[0] - (a[0] + t * vx), p[1] - (a[1] + t * vy))


def island_gnd_zones(board):
    """AMP 島にかかる GND ゾーンを F/B それぞれ返す。"""
    x0, y0, x1, y1 = ISLAND
    f = bz = None
    for z in board.Zones():
        if z.GetNetname() != "GND" or not z.IsFilled():
            continue
        bb = z.GetBoundingBox()
        if not (x0 <= MM(bb.GetLeft()) and MM(bb.GetRight()) <= x1
                and y0 <= MM(bb.GetTop()) and MM(bb.GetBottom()) <= y1):
            continue
        if z.IsOnLayer(pcbnew.F_Cu):
            f = z
        if z.IsOnLayer(pcbnew.B_Cu):
            bz = z
    return f, bz


def on_copper(zone, layer, x, y, radius):
    """(x,y) を中心とする半径 radius の円が、そのゾーンの塗り面に完全に乗るか。"""
    pts = [(x, y)] + [(x + radius * math.cos(a), y + radius * math.sin(a))
                      for a in (i * math.pi / 4 for i in range(8))]
    for px, py in pts:
        if not zone.HitTestFilledArea(layer, pcbnew.VECTOR2I(FM(px), FM(py))):
            return False
    return True


def collect_obstacles(board):
    x0, y0, x1, y1 = ISLAND

    def inside(px, py):
        return x0 <= px <= x1 and y0 <= py <= y1

    pads, tr_gnd, tr_other, vias, courtyards = [], [], [], [], []
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            p = pad.GetPosition()
            if inside(MM(p.x), MM(p.y)):
                pads.append((MM(p.x), MM(p.y)))
        # THT 部品の胴の下は避ける（缶やソケットの座面に当たらないように）。
        # SMD は CLR_PAD_MM のパッド離隔で足りるので対象外。
        if not any(pd.GetAttribute() == pcbnew.PAD_ATTRIB_PTH for pd in fp.Pads()):
            continue
        for layer in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
            poly = fp.GetCourtyard(layer)
            if poly.OutlineCount() == 0:
                continue
            bb = poly.BBox()
            # 島と少しでも重なるコートヤードは拾う
            if (MM(bb.GetRight()) >= x0 and MM(bb.GetLeft()) <= x1
                    and MM(bb.GetBottom()) >= y0 and MM(bb.GetTop()) <= y1):
                courtyards.append(poly)

    for t in board.GetTracks():
        p = t.GetPosition()
        if not inside(MM(p.x), MM(p.y)):
            continue
        if t.Type() == pcbnew.PCB_VIA_T:
            vias.append((MM(p.x), MM(p.y)))
        else:
            seg = ((MM(t.GetStart().x), MM(t.GetStart().y)),
                   (MM(t.GetEnd().x), MM(t.GetEnd().y)))
            (tr_gnd if t.GetNetname() == "GND" else tr_other).append(seg)
    return pads, tr_gnd, tr_other, vias, courtyards


def in_courtyard(courtyards, x, y):
    """コートヤードの内側、またはその外形から所定の距離以内なら弾く。

    SHAPE_POLY_SET.Collide() は外形線との当たりしか見ないので、
    内側判定は Contains() を併用する必要がある。
    """
    pt = pcbnew.VECTOR2I(FM(x), FM(y))
    margin = FM(CLR_COURTYARD_MM + VIA_RADIUS_MM)
    for c in courtyards:
        if c.Contains(pt) or c.Collide(pt, margin):
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pcb")
    ap.add_argument("--apply", action="store_true", help="実際に保存する")
    ap.add_argument("--target", type=float, default=TARGET_MM)
    ap.add_argument("--max-vias", type=int, default=40)
    args = ap.parse_args()

    board = pcbnew.LoadBoard(args.pcb)
    zf, zb = island_gnd_zones(board)
    if zf is None or zb is None:
        sys.exit("AMP 島の GND ゾーンが F/B 両面そろっていない。先に両面ベタにすること。")

    pads, tr_gnd, tr_other, vias0, courtyards = collect_obstacles(board)
    print(f"AMP 島: パッド {len(pads)} / GND配線 {len(tr_gnd)} / 他ネット配線 {len(tr_other)} "
          f"/ 既存ビア {len(vias0)} / コートヤード {len(courtyards)}")

    # 1) ベタ上のサンプル点（カバレッジ評価用）
    x0, y0, x1, y1 = ISLAND
    samples = []
    x = x0
    while x <= x1:
        y = y0
        while y <= y1:
            if zf.HitTestFilledArea(pcbnew.F_Cu, pcbnew.VECTOR2I(FM(x), FM(y))):
                samples.append((x, y))
            y += 0.5
        x += 0.5
    print(f"F 面ベタ上のサンプル点: {len(samples)}")

    # 2) ビアを置ける候補点
    cands = []
    x = x0
    while x <= x1:
        y = y0
        while y <= y1:
            p = (x, y)
            ok = (on_copper(zf, pcbnew.F_Cu, x, y, FIT_RADIUS_MM)
                  and on_copper(zb, pcbnew.B_Cu, x, y, FIT_RADIUS_MM)
                  and not in_courtyard(courtyards, x, y)
                  and all(dist(p, q) >= CLR_PAD_MM for q in pads)
                  and all(dist(p, q) >= CLR_VIA_MM for q in vias0)
                  and all(seg_dist(p, a, b) >= CLR_TRACK_OTHER_MM for a, b in tr_other)
                  and all(seg_dist(p, a, b) >= CLR_TRACK_GND_MM for a, b in tr_gnd))
            if ok:
                cands.append(p)
            y += 0.5
        x += 0.5
    print(f"ビアを置ける候補点: {len(cands)}")
    if not cands:
        sys.exit("候補点なし。離隔条件が厳しすぎる可能性あり。")

    # 3) 最遠点を潰す順に貪欲に選ぶ
    placed = list(vias0)

    def worst():
        d = [min(dist(s, v) for v in placed) for s in samples] if placed else [1e9] * len(samples)
        return max(d), d

    w0, _ = worst()
    print(f"追加前: ベタ上の最遠点から最寄 GND ビアまで {w0:.1f} mm")

    chosen = []
    while len(chosen) < args.max_vias:
        w, dists = worst()
        if w <= args.target:
            break
        # いま一番遠いサンプル点に最も近い候補を選ぶ
        far = samples[max(range(len(samples)), key=lambda i: dists[i])]
        c = min(cands, key=lambda p: dist(p, far))
        if min(dist(c, v) for v in placed) < CLR_VIA_MM:
            cands.remove(c)
            continue
        chosen.append(c)
        placed.append(c)
        cands = [p for p in cands if dist(p, c) >= CLR_VIA_MM]
        if not cands:
            break

    w1, _ = worst()
    print(f"追加後: 最遠 {w1:.1f} mm / 追加ビア {len(chosen)} 本")
    for i, (cx, cy) in enumerate(chosen, 1):
        print(f"   {i:2d}. ({cx:7.2f}, {cy:7.2f})")

    if not args.apply:
        print("\n[dry-run] 保存していない。--apply で書き込む。")
        return

    net = board.FindNet("GND")
    for cx, cy in chosen:
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I(FM(cx), FM(cy)))
        v.SetWidth(FM(VIA_DIA_MM))
        v.SetDrill(FM(VIA_DRILL_MM))
        v.SetViaType(pcbnew.VIATYPE_THROUGH)
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetNet(net)
        board.Add(v)

    # 再充填は AMP 島の 2 ゾーンだけに絞る。
    # 全ゾーンを塗り直すと、作業途中の MeasurementADC 島にも差分が出るため。
    targets = pcbnew.ZONES()
    targets.append(zf)
    targets.append(zb)
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(targets)
    board.Save(args.pcb)
    print(f"\n{len(chosen)} 本を追加してゾーンを再充填、{args.pcb} に保存した。")


if __name__ == "__main__":
    main()
