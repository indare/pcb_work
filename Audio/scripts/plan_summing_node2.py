#!/usr/bin/env python3
"""加算ノード 2 組（A ch / B ch）を、表裏どちらに置くかも含めて最適化する。

AMP1 は F 面にしかコートヤードを持たないので、B 面はピン列の間まで使える。
一方 B 面には GND ベタが載っているので、部品を増やすとベタが分断される。
その両方を見るため、層の割り当て 4 通りを総当たりして、
  ・引くことになる配線長の合計（直線近似、すべて干渉なしであること）
を比べる。ベタの分断量は適用後に別途実測する。

  kicad-python plan_summing_node2.py board.kicad_pcb
"""
import argparse
import math

import pcbnew

MM = pcbnew.ToMM
FM = pcbnew.FromMM

GROUPS = [
    dict(key="A", name="A ch", node="Net-(AMP1A--)", fb="R31", gnd="R27",
         pin="2", out_pin="1", out_net="Net-(AMP1-Pad1)"),
    dict(key="B", name="B ch", node="Net-(AMP1B--)", fb="R32", gnd="R30",
         pin="6", out_pin="7", out_net="Net-(AMP1-Pad7)"),
]

CLEARANCE = 0.25
TRACK_HALF, TRACK_CLR = 0.25, 0.20
COURTYARD = 0.10
PTH_MARGIN = 0.15      # スルーホールのパッド外形からの余裕（同一ネットでも必須）
WINDOW, STEP = 6.0, 0.25
ROTS = (0, 90, 180, 270)
TOPK = 60


def prad(p):
    s = p.GetSize()
    return math.hypot(MM(s.x), MM(s.y)) / 2


def rot(dx, dy, deg):
    a = math.radians(deg)
    return (dx * math.cos(a) + dy * math.sin(a), -dx * math.sin(a) + dy * math.cos(a))


def segd(p, a, b):
    vx, vy = b[0] - a[0], b[1] - a[1]
    L = vx * vx + vy * vy
    if L == 0:
        return math.hypot(p[0] - a[0], p[1] - a[1])
    t = max(0.0, min(1.0, ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / L))
    return math.hypot(p[0] - (a[0] + t * vx), p[1] - (a[1] + t * vy))


def rect_overlap(a, c, margin=0.15):
    """回転が 90° の倍数なので、外形は軸並行矩形として扱える。"""
    (ax, ay), (aw, ah) = (a[0], a[1]), a[3]
    (cx, cy), (cw, ch) = (c[0], c[1]), c[3]
    return (abs(ax - cx) < (aw + cw) / 2 + margin
            and abs(ay - cy) < (ah + ch) / 2 + margin)


class Ctx:
    def __init__(self, board):
        self.board = board
        self.fps = {}
        for f in board.GetFootprints():
            self.fps.setdefault(f.GetReference(), f)
        self.amp = self.fps["AMP1"]
        self.pin = {p.GetNumber(): p for p in self.amp.Pads()}
        self.movers = {g[k] for g in GROUPS for k in ("fb", "gnd")}
        self.live = {g[n] for g in GROUPS for n in ("node", "out_net")}
        self.zones = [z for z in board.Zones()
                      if z.GetNetname() == "GND" and z.IsFilled()
                      and 220 < MM(z.GetBoundingBox().GetLeft()) < 230]
        self.pads, self.tracks, self.courts = [], [], []
        # スルーホールは「同じネットでも重ねてはいけない」。
        # DIP ソケットのピンは裏に飛び出すので、SMD をその上に置くと組めない。
        self.pth = []
        for f in board.GetFootprints():
            p = f.GetPosition()
            if not (233 < MM(p.x) < 272 and 78 < MM(p.y) < 122):
                continue
            if f.GetReference() in self.movers:
                continue
            for pd in f.Pads():
                q = pd.GetPosition()
                self.pads.append((MM(q.x), MM(q.y), prad(pd), pd.GetNetname()))
                if pd.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
                    self.pth.append((MM(q.x), MM(q.y), prad(pd)))
            for lay in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
                poly = f.GetCourtyard(lay)
                if poly.OutlineCount():
                    self.courts.append((lay, poly))
        for t in board.GetTracks():
            if t.Type() == pcbnew.PCB_VIA_T:
                q = t.GetPosition()
                if 233 < MM(q.x) < 272 and 78 < MM(q.y) < 122:
                    self.tracks.append(((MM(q.x), MM(q.y)), (MM(q.x), MM(q.y)),
                                        MM(t.GetWidth(pcbnew.F_Cu)) / 2, t.GetNetname(), None))
                continue
            if t.GetNetname() in self.live:
                continue
            s, e = t.GetStart(), t.GetEnd()
            if 233 < MM(s.x) < 272 and 78 < MM(s.y) < 122:
                self.tracks.append(((MM(s.x), MM(s.y)), (MM(e.x), MM(e.y)),
                                    MM(t.GetWidth()) / 2, t.GetNetname(), t.GetLayer()))

    def pad_ok(self, px, py, r, pnet, layer, extra):
        # スルーホールとはネットを問わず重ならないこと
        for ox, oy, orad in self.pth:
            if math.hypot(px - ox, py - oy) < r + orad + PTH_MARGIN:
                return False
        need = r + CLEARANCE
        for ox, oy, orad, onet in self.pads:
            if onet != pnet and math.hypot(px - ox, py - oy) < need + orad:
                return False
        for s, e, w, onet, tl in self.tracks:
            if onet == pnet or (tl is not None and tl != layer):
                continue
            if segd((px, py), s, e) < need + w:
                return False
        crt = pcbnew.F_CrtYd if layer == pcbnew.F_Cu else pcbnew.B_CrtYd
        pt = pcbnew.VECTOR2I(FM(px), FM(py))
        for cl, poly in self.courts:
            if cl == crt and (poly.Contains(pt) or poly.Collide(pt, FM(r + COURTYARD))):
                return False
        for ox, oy, orad, onet, ol in extra:
            if ol == layer and onet != pnet and math.hypot(px - ox, py - oy) < need + orad:
                return False
        return True

    def line_ok(self, a, b, layer, net, extra):
        need = TRACK_HALF + TRACK_CLR
        for ox, oy, orad, onet in self.pads:
            if onet != net and segd((ox, oy), a, b) < need + orad:
                return False
        for s, e, w, onet, tl in self.tracks:
            if onet == net or (tl is not None and tl != layer):
                continue
            if min(segd(s, a, b), segd(e, a, b)) < need + w:
                return False
        for ox, oy, orad, onet, ol in extra:
            if ol == layer and onet != net and segd((ox, oy), a, b) < need + orad:
                return False
        return True

    def places(self, ref, layer, cx0, cy0, extra):
        fp = self.fps[ref]
        crt = pcbnew.F_CrtYd if layer == pcbnew.F_Cu else pcbnew.B_CrtYd
        src = fp.GetCourtyard(pcbnew.F_CrtYd if fp.GetLayer() == pcbnew.F_Cu else pcbnew.B_CrtYd)
        bb = src.BBox()
        w0, h0 = MM(bb.GetWidth()), MM(bb.GetHeight())
        # src は「現在の向き」での外形なので、0° 相当に戻してから候補角度で組み直す
        if round(fp.GetOrientationDegrees()) % 180 == 90:
            w0, h0 = h0, w0
        local = [(MM(p.GetFPRelativePosition().x), MM(p.GetFPRelativePosition().y),
                  prad(p), p.GetNetname()) for p in fp.Pads()]
        out = []
        n = int(WINDOW / STEP)
        for i in range(-n, n + 1):
            for j in range(-n, n + 1):
                cx, cy = cx0 + i * STEP, cy0 + j * STEP
                for deg in ROTS:
                    placed = []
                    for lx, ly, r, pnet in local:
                        dx, dy = rot(lx, ly, deg)
                        placed.append((cx + dx, cy + dy, r, pnet))
                    if not all(self.pad_ok(px, py, r, pnet, layer, extra)
                               for px, py, r, pnet in placed):
                        continue
                    gp = [p for p in placed if p[3] == "GND"]
                    if gp:
                        lay = pcbnew.F_Cu if layer == pcbnew.F_Cu else pcbnew.B_Cu
                        if not any(z.HitTestFilledArea(lay, pcbnew.VECTOR2I(FM(gp[0][0]), FM(gp[0][1])))
                                   for z in self.zones if z.IsOnLayer(lay)):
                            continue
                    w, h = (w0, h0) if deg % 180 == 0 else (h0, w0)
                    out.append((cx, cy, deg, (w, h), {p[3]: (p[0], p[1]) for p in placed},
                                [(p[0], p[1], p[2], p[3], layer) for p in placed]))
        return out


def best_pairs(ctx, g, layer, extra):
    tp = ctx.pin[g["pin"]]
    tx, ty = MM(tp.GetPosition().x), MM(tp.GetPosition().y)
    op = ctx.pin[g["out_pin"]]
    ox_, oy_ = MM(op.GetPosition().x), MM(op.GetPosition().y)
    A = ctx.places(g["fb"], layer, tx, ty, extra)
    B = ctx.places(g["gnd"], layer, tx, ty, extra)
    A.sort(key=lambda a: math.hypot(a[4][g["node"]][0] - tx, a[4][g["node"]][1] - ty))
    res = []
    for a in A:
        pf = a[4][g["node"]]
        d1 = math.hypot(pf[0] - tx, pf[1] - ty)
        if len(res) >= TOPK and d1 > res[-1][0]:
            break
        if not ctx.line_ok(pf, (tx, ty), layer, g["node"], extra):
            continue
        po = a[4][g["out_net"]]
        d3 = math.hypot(po[0] - ox_, po[1] - oy_)
        if not ctx.line_ok(po, (ox_, oy_), layer, g["out_net"], extra):
            continue
        for c in B:
            if rect_overlap(a, c):
                continue
            pg = c[4][g["node"]]
            d2 = math.hypot(pg[0] - pf[0], pg[1] - pf[1])
            tot = d1 + d2 + d3
            if len(res) >= TOPK and tot >= res[-1][0]:
                continue
            if not ctx.line_ok(pg, pf, layer, g["node"], extra):
                continue
            res.append((tot, a, c, d1, d2, d3, layer))
            res.sort(key=lambda r: r[0])
            del res[TOPK:]
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pcb")
    args = ap.parse_args()
    ctx = Ctx(pcbnew.LoadBoard(args.pcb))

    def cur(net):
        return sum(MM(t.GetLength()) for t in ctx.board.GetTracks()
                   if t.Type() != pcbnew.PCB_VIA_T and t.GetNetname() == net)

    now = {g["key"]: cur(g["node"]) + cur(g["out_net"]) for g in GROUPS}
    print(f"現状: A {now['A']:.2f}mm / B {now['B']:.2f}mm / 合計 {now['A']+now['B']:.2f}mm\n")

    opts = {}
    for g in GROUPS:
        for layer, nm in ((pcbnew.F_Cu, "F.Cu"), (pcbnew.B_Cu, "B.Cu")):
            r = best_pairs(ctx, g, layer, [])
            opts[(g["key"], nm)] = r
            print(f"  {g['name']} を {nm} に置く: 候補 {len(r)} 組"
                  + (f" / 最良 {r[0][0]:.2f}mm" if r else " / なし"))

    print()
    best = None
    for la in ("F.Cu", "B.Cu"):
        for lb in ("F.Cu", "B.Cu"):
            for ra in opts[("A", la)][:TOPK]:
                exa = ra[1][5] + ra[2][5]
                for rb in opts[("B", lb)][:TOPK]:
                    exb = rb[1][5] + rb[2][5]
                    # 2 組が空間的にぶつからないか（同じ層のときだけ）
                    bad = False
                    if la == lb:
                        for pa in (ra[1], ra[2]):
                            for pb in (rb[1], rb[2]):
                                if rect_overlap(pa, pb):
                                    bad = True
                    for x1, y1, r1, n1, l1 in exa:
                        for x2, y2, r2, n2, l2 in exb:
                            if l1 == l2 and n1 != n2 and math.hypot(x1 - x2, y1 - y2) < r1 + r2 + CLEARANCE:
                                bad = True
                                break
                        if bad:
                            break
                    if bad:
                        continue
                    # 相手側のパッドを障害物に加えても直線が引けるか
                    if not ctx.line_ok(ra[1][4][GROUPS[0]["node"]],
                                       (MM(ctx.pin["2"].GetPosition().x), MM(ctx.pin["2"].GetPosition().y)),
                                       ra[6], GROUPS[0]["node"], exb):
                        continue
                    if not ctx.line_ok(rb[1][4][GROUPS[1]["node"]],
                                       (MM(ctx.pin["6"].GetPosition().x), MM(ctx.pin["6"].GetPosition().y)),
                                       rb[6], GROUPS[1]["node"], exa):
                        continue
                    tot = ra[0] + rb[0]
                    if best is None or tot < best[0]:
                        best = (tot, la, ra, lb, rb)
    if not best:
        print("成立する組み合わせなし")
        return
    tot, la, ra, lb, rb = best
    print(f"=== 最良: 合計 {tot:.2f}mm （現状 {now['A']+now['B']:.2f}mm から {tot-(now['A']+now['B']):+.2f}mm）")
    for g, lay, r in ((GROUPS[0], la, ra), (GROUPS[1], lb, rb)):
        f_now = ctx.fps[g["fb"]]
        gd_now = ctx.fps[g["gnd"]]
        print(f"  {g['name']}  → {lay}  節点まわり {r[0]:.2f}mm （現状 {now[g['key']]:.2f}mm）")
        print(f"    {g['fb']:4s} ({r[1][0]:.2f}, {r[1][1]:.2f}) rot {r[1][2]}° {lay}"
              f"   [現在 ({MM(f_now.GetPosition().x):.2f}, {MM(f_now.GetPosition().y):.2f}) "
              f"rot {f_now.GetOrientationDegrees():.0f}° {ctx.board.GetLayerName(f_now.GetLayer())}]")
        print(f"    {g['gnd']:4s} ({r[2][0]:.2f}, {r[2][1]:.2f}) rot {r[2][2]}° {lay}"
              f"   [現在 ({MM(gd_now.GetPosition().x):.2f}, {MM(gd_now.GetPosition().y):.2f}) "
              f"rot {gd_now.GetOrientationDegrees():.0f}° {ctx.board.GetLayerName(gd_now.GetLayer())}]")
        print(f"    内訳 pin{g['pin']}→{g['fb']} {r[3]:.2f} / {g['fb']}→{g['gnd']} {r[4]:.2f} / "
              f"{g['fb']}→pin{g['out_pin']} {r[5]:.2f}")


if __name__ == "__main__":
    main()
