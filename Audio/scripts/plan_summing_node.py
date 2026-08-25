#!/usr/bin/env python3
"""加算ノード（反転入力）まわりを 2 部品まとめて置き直す案を探す。

【注意】このバージョンは plan_summing_node2.py に置き換わっている。
本ファイルには次の欠陥がある:
  ・同一ネットならスルーホールとの重なりを許してしまう
    （DIP ソケットのピンは裏に飛び出すので、SMD をその上に置くと組めない）
  ・部品どうしの外形干渉を円近似かつ回転前の寸法で見ている
  ・層の入れ替えを検討しない
経緯の記録として残す。実際の配置検討には plan_summing_node2.py を使うこと。


単体で目標ピンに寄せると隣のピンの裏側に回り込んでしまうため、
節点を構成する 2 本（GND 側の 10k と帰還の 47k）を同時に動かし、
「必要な接続がすべて他ネットを避けた直線で引けること」を条件にする。

評価値は、その節点で引くことになる配線長の合計（直線近似）。
GND パッドはベタに落とすので配線には数えない。

  kicad-python plan_summing_node.py board.kicad_pcb
"""
import argparse
import itertools
import math

import pcbnew

MM = pcbnew.ToMM
FM = pcbnew.FromMM

GROUPS = [
    dict(name="A ch 加算ノード", node="Net-(AMP1A--)",
         parts=["R31", "R27"], pin="2", out_pin="1", out_net="Net-(AMP1-Pad1)"),
    dict(name="B ch 加算ノード", node="Net-(AMP1B--)",
         parts=["R32", "R30"], pin="6", out_pin="7", out_net="Net-(AMP1-Pad7)"),
]

CLEARANCE = 0.25       # パッド外形どうしの最小離隔
TRACK_CLR = 0.20       # 引く配線（0.5mm 幅）の縁と他ネット銅の離隔
TRACK_HALF = 0.25
COURTYARD = 0.10
WINDOW = 7.0           # 目標ピンからこの範囲を探す
STEP = 0.25
ROTS = (0, 90, 180, 270)


def prad(pad):
    s = pad.GetSize()
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pcb")
    args = ap.parse_args()
    board = pcbnew.LoadBoard(args.pcb)
    fps = {}
    for f in board.GetFootprints():
        fps.setdefault(f.GetReference(), f)
    amp = fps["AMP1"]
    pins = {p.GetNumber(): p for p in amp.Pads()}

    for g in GROUPS:
        movers = set(g["parts"])
        node, live_nets = g["node"], {g["node"], g["out_net"]}

        # 静的な障害物（動かす部品と、引き直す配線は除く）
        opads, otracks, ocourts = [], [], []
        for f in board.GetFootprints():
            p = f.GetPosition()
            if not (235 < MM(p.x) < 270 and 80 < MM(p.y) < 120):
                continue
            if f.GetReference() in movers:
                continue
            for pd in f.Pads():
                q = pd.GetPosition()
                opads.append((MM(q.x), MM(q.y), prad(pd), pd.GetNetname()))
            for lay in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
                poly = f.GetCourtyard(lay)
                if poly.OutlineCount():
                    ocourts.append((f.GetReference(), lay, poly))
        for t in board.GetTracks():
            if t.Type() == pcbnew.PCB_VIA_T:
                q = t.GetPosition()
                if 235 < MM(q.x) < 270 and 80 < MM(q.y) < 120:
                    otracks.append(((MM(q.x), MM(q.y)), (MM(q.x), MM(q.y)),
                                    MM(t.GetWidth(pcbnew.F_Cu)) / 2, t.GetNetname(), None))
                continue
            if t.GetNetname() in live_nets:
                continue          # これから引き直すので障害物に数えない
            s, e = t.GetStart(), t.GetEnd()
            if 235 < MM(s.x) < 270 and 80 < MM(s.y) < 120:
                otracks.append(((MM(s.x), MM(s.y)), (MM(e.x), MM(e.y)),
                                MM(t.GetWidth()) / 2, t.GetNetname(), t.GetLayer()))
        zones = [z for z in board.Zones()
                 if z.GetNetname() == "GND" and z.IsFilled()
                 and 220 < MM(z.GetBoundingBox().GetLeft()) < 230]

        def clear_line(a, b, layer, net):
            """a→b に 0.5mm 幅で引いたとき、他ネットの銅に当たらないか。"""
            need = TRACK_HALF + TRACK_CLR
            for ox, oy, orad, onet in opads:
                if onet == net:
                    continue
                if segd((ox, oy), a, b) < need + orad:
                    return False
            for s, e, w, onet, tl in otracks:
                if onet == net or (tl is not None and tl != layer):
                    continue
                if min(segd(s, a, b), segd(e, a, b)) < need + w:
                    return False
            return True

        # 各部品の妥当な配置を列挙
        cand = {}
        tgt = pins[g["pin"]]
        tx, ty = MM(tgt.GetPosition().x), MM(tgt.GetPosition().y)
        for ref in g["parts"]:
            fp = fps[ref]
            layer = fp.GetLayer()
            crt_lay = pcbnew.F_CrtYd if layer == pcbnew.F_Cu else pcbnew.B_CrtYd
            local = [(p.GetNumber(), MM(p.GetFPRelativePosition().x),
                      MM(p.GetFPRelativePosition().y), prad(p), p.GetNetname())
                     for p in fp.Pads()]
            half = MM(fp.GetCourtyard(crt_lay).BBox().GetWidth()) / 2
            out = []
            n = int(WINDOW / STEP)
            for i in range(-n, n + 1):
                for j in range(-n, n + 1):
                    cx, cy = tx + i * STEP, ty + j * STEP
                    for deg in ROTS:
                        placed = []
                        for num, lx, ly, r, pnet in local:
                            dx, dy = rot(lx, ly, deg)
                            placed.append((cx + dx, cy + dy, r, pnet))
                        ok = True
                        for px, py, r, pnet in placed:
                            need = r + CLEARANCE
                            for ox, oy, orad, onet in opads:
                                if onet != pnet and math.hypot(px - ox, py - oy) < need + orad:
                                    ok = False
                                    break
                            if not ok:
                                break
                            for s, e, w, onet, tl in otracks:
                                if onet == pnet or (tl is not None and tl != layer):
                                    continue
                                if segd((px, py), s, e) < need + w:
                                    ok = False
                                    break
                            if not ok:
                                break
                            pt = pcbnew.VECTOR2I(FM(px), FM(py))
                            for _, cl, poly in ocourts:
                                if cl != crt_lay:
                                    continue
                                if poly.Contains(pt) or poly.Collide(pt, FM(r + COURTYARD)):
                                    ok = False
                                    break
                            if not ok:
                                break
                        if not ok:
                            continue
                        gp = [p for p in placed if p[3] == "GND"]
                        if gp:
                            lay = pcbnew.F_Cu if layer == pcbnew.F_Cu else pcbnew.B_Cu
                            if not any(z.HitTestFilledArea(lay, pcbnew.VECTOR2I(FM(gp[0][0]), FM(gp[0][1])))
                                       for z in zones if z.IsOnLayer(lay)):
                                continue
                        out.append((cx, cy, deg, half, layer,
                                    {p[3]: (p[0], p[1]) for p in placed}))
            cand[ref] = out
            print(f"  {ref}: 妥当な配置 {len(out)} 通り")

        fb, gnd_r = g["parts"]           # 帰還 47k, GND 側 10k
        opin = pins[g["out_pin"]]
        ox_, oy_ = MM(opin.GetPosition().x), MM(opin.GetPosition().y)

        best = None
        for a in cand[fb]:
            if node not in a[5]:
                continue
            p_fb = a[5][node]
            d1 = math.hypot(p_fb[0] - tx, p_fb[1] - ty)
            if best and d1 > best[0]:
                continue
            if not clear_line(p_fb, (tx, ty), a[4], node):
                continue
            p_out = a[5][g["out_net"]]
            d3 = math.hypot(p_out[0] - ox_, p_out[1] - oy_)
            if not clear_line(p_out, (ox_, oy_), a[4], g["out_net"]):
                continue
            for c in cand[gnd_r]:
                if node not in c[5]:
                    continue
                if math.hypot(a[0] - c[0], a[1] - c[1]) < a[3] + c[3] + 0.15:
                    continue                      # 部品どうしが重なる
                p_g = c[5][node]
                d2 = math.hypot(p_g[0] - p_fb[0], p_g[1] - p_fb[1])
                tot = d1 + d2 + d3
                if best and tot >= best[0]:
                    continue
                if not clear_line(p_g, p_fb, c[4], node):
                    continue
                best = (tot, a, c, d1, d2, d3)

        # 現状
        def cur_len(net):
            return sum(MM(t.GetLength()) for t in board.GetTracks()
                       if t.Type() != pcbnew.PCB_VIA_T and t.GetNetname() == net)
        now = cur_len(node) + cur_len(g["out_net"])
        print(f"--- {g['name']}  現状: {node} {cur_len(node):.2f}mm + "
              f"{g['out_net']} {cur_len(g['out_net']):.2f}mm = {now:.2f}mm")
        if not best:
            print("    条件を満たす組み合わせなし")
            continue
        tot, a, c, d1, d2, d3 = best
        print(f"    提案 合計 {tot:.2f}mm （{tot - now:+.2f}mm）")
        print(f"      {fb:4s} → ({a[0]:.2f}, {a[1]:.2f}) rot {a[2]}°   "
              f"[現在 ({MM(fps[fb].GetPosition().x):.2f}, {MM(fps[fb].GetPosition().y):.2f}) "
              f"rot {fps[fb].GetOrientationDegrees():.0f}°]")
        print(f"      {gnd_r:4s} → ({c[0]:.2f}, {c[1]:.2f}) rot {c[2]}°   "
              f"[現在 ({MM(fps[gnd_r].GetPosition().x):.2f}, {MM(fps[gnd_r].GetPosition().y):.2f}) "
              f"rot {fps[gnd_r].GetOrientationDegrees():.0f}°]")
        print(f"      内訳: pin{g['pin']}→{fb} {d1:.2f}  {fb}→{gnd_r} {d2:.2f}  "
              f"{fb}→pin{g['out_pin']} {d3:.2f}  （すべて直線で引ける）")
        print()


if __name__ == "__main__":
    main()
