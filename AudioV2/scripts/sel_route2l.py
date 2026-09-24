#!/usr/bin/env python3
"""AMP_SEL を表裏2層で引き直すための経路探索（保存しない。点列を出すだけ）。

`amp_sel_hop.py propose` は B.Cu だけの1ホップ用。Relay 娘では表が空き・裏が混んでいて、
L/R を別の通り道に分けるにはビアを挟んだ表裏の経路が要るので、2層の A* をここに置く。

コスト = 長さ + 45° の折れ + ビア + 近くを「ほぼ平行に」走る相手への罰則。
罰則の距離は、反対層の相手なら基板厚を足した 3 次元の距離で測る（真裏の並走は近い）。
アナログ（もう一方の AMP_SEL・オペアンプの入力・TONE・CH_OUT など）と反対層で交わるときは
**直角だけ**を許す（45° の交差は通さない）。衝突判定は KiCad の形状（amp_sel_hop.Obstacles）。

出力は層つきの点列（JSON）。適用は別のスクリプトが明示座標で行う（再現できるように）。

    python3 AudioV2/scripts/sel_route2l.py --board out/relay/lr.kicad_pcb --net /AMP_SEL_R \\
        --src pad:J_ANA302:10 --dst pad:K302:4 -o out/relay/r_k302.json
"""
from __future__ import annotations

import argparse
import heapq
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).resolve().parent))
import amp_sel_hop as hop  # noqa: E402

F, B = hop.F, hop.B
SQ2 = math.sqrt(2)

# 罰則の相手: (判定, 重み, アナログか＝反対層で直角以外の交差を禁じるか)
def categories(own: str):
    other_sel = "/AMP_SEL_L" if own == "/AMP_SEL_R" else "/AMP_SEL_R"
    return [
        (lambda n: n == other_sel, 5.0, True),
        (lambda n: n.startswith("Net-(AMP") and (n.endswith("-+)") or n.endswith("--)")), 4.0, True),   # オペアンプ入力
        (lambda n: n.startswith("/TONE_"), 2.0, True),
        (lambda n: "_OUT_" in n or (n.startswith("Net-(AMP") and "Pad" in n) or n.startswith("Net-(C1"), 1.5, True),
        (lambda n: n in ("/+5V_COIL", "/GND_COIL") or n.endswith("_SETC") or n.endswith("_RSTC")
         or n.endswith("_SET") or n.endswith("_RST") or "I2C" in n or "ADDR" in n, 1.5, False),
        (lambda n: n in ("/+15V", "/-15V", "/3V3"), 0.3, False),
    ]


class Field:
    """相手の線分を 2 mm バケットに入れて、罰則と交差角を引く。"""

    BK = 2.0

    def __init__(self, board, own, box, dmax=4.0, k=3.0, thick=1.6, extra=(), dpad=2.5):
        self.dmax, self.k, self.thick, self.dpad = dmax, k, thick, dpad
        self.segs = []
        self.bk = defaultdict(list)
        cats = categories(own)
        items = [(hop.xy(t.GetStart()), hop.xy(t.GetEnd()), t.GetLayer(), t.GetNetname())
                 for t in board.GetTracks() if not hop.is_via(t)] + list(extra)
        # パッドは点の相手（向きを問わず、近いだけで罰則）。THT は両層
        self.pads = []
        self.pbk = defaultdict(list)
        for fp in board.GetFootprints():
            for p in fp.Pads():
                n = p.GetNetname()
                if n == own:
                    continue
                w = next((w for pred, w, _ in cats if pred(n)), None)
                if w is None:
                    continue
                x, y = hop.xy(p.GetPosition())
                if not (box[0] - dmax <= x <= box[2] + dmax and box[1] - dmax <= y <= box[3] + dmax):
                    continue
                layers = tuple(L for L in (F, B) if p.IsOnLayer(L))
                i = len(self.pads)
                self.pads.append((x, y, layers, w))
                for bi in range(int((x - dmax) // self.BK), int((x + dmax) // self.BK) + 1):
                    for bj in range(int((y - dmax) // self.BK), int((y + dmax) // self.BK) + 1):
                        self.pbk[(bi, bj)].append(i)
        for a, b, L, n in items:
            if n == own:
                continue
            for pred, w, analog in cats:
                if pred(n):
                    break
            else:
                continue
            if max(a[0], b[0]) < box[0] - dmax or min(a[0], b[0]) > box[2] + dmax \
                    or max(a[1], b[1]) < box[1] - dmax or min(a[1], b[1]) > box[3] + dmax:
                continue
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy)
            if ln < 1e-9:
                continue
            i = len(self.segs)
            self.segs.append((a, b, dx / ln, dy / ln, ln, L, w, analog, n))
            for bi in range(int((min(a[0], b[0]) - dmax) // self.BK), int((max(a[0], b[0]) + dmax) // self.BK) + 1):
                for bj in range(int((min(a[1], b[1]) - dmax) // self.BK), int((max(a[1], b[1]) + dmax) // self.BK) + 1):
                    self.bk[(bi, bj)].append(i)

    def near(self, x, y):
        return self.bk.get((int(x // self.BK), int(y // self.BK)), ())

    def cost(self, p, q, L):
        """p→q（L 層）の罰則。直角以外でアナログと反対層で交わるなら None（通さない）。"""
        ux, uy = q[0] - p[0], q[1] - p[1]
        n = math.hypot(ux, uy)
        ux, uy = ux / n, uy / n
        mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        pen = 0.0
        for i in self.near(mx, my):
            a, b, gx, gy, gn, gL, w, analog, _ = self.segs[i]
            c = abs(ux * gx + uy * gy)
            if gL != L and analog and 0.1 < c and hop._intersect(p, q, a, b) is not None:
                return None
            if c < 0.87:
                continue
            u = max(0.0, min(gn, (mx - a[0]) * gx + (my - a[1]) * gy))
            d = math.hypot(mx - (a[0] + gx * u), my - (a[1] + gy * u))
            if gL != L:
                d = math.hypot(d, self.thick)
            if d < self.dmax:
                pen += w * ((self.dmax - d) / self.dmax) ** 2
        for i in self.pbk.get((int(mx // self.BK), int(my // self.BK)), ()):
            x, y, layers, w = self.pads[i]
            d = math.hypot(mx - x, my - y)
            if L not in layers:
                d = math.hypot(d, self.thick)
            if d < self.dpad:
                pen += w * ((self.dpad - d) / self.dpad) ** 2
        return pen * self.k * n


def route(board, net, sources, goals, box, goal_pts=(), grid=0.25, width=0.2, via_cost=4.0, turn_cost=0.8,
          field=None, origin=None, max_expand=3_000_000):
    """sources: [(x, y, L)]（格子上）/ goals: 関数 (x, y, L) -> bool / goal_pts: 推定距離の目標点。
    戻り値は ([(x, y, L)], コスト)。"""
    nc = board.GetNetcodeFromNetname(net)
    clr = hop.design(board)["clr"]
    obs = hop.Obstacles(board, nc, layers=(F, B), box=box)
    ox, oy = origin or sources[0][:2]
    via = next(t for t in board.GetTracks() if hop.is_via(t))
    vdia, vdrill = hop.mm(via.GetWidth(F)), hop.mm(via.GetDrill())
    free_c, via_c = {}, {}
    r = width / 2

    def xyc(ix, iy):
        return (round(ox + ix * grid, 4), round(oy + iy * grid, 4))

    def free(ix, iy, L):
        k = (ix, iy, L)
        if k not in free_c:
            x, y = xyc(ix, iy)
            if not (box[0] <= x <= box[2] and box[1] <= y <= box[3]):
                free_c[k] = False
            else:
                c = pcbnew.SHAPE_CIRCLE(hop.P(x, y), hop.iu(r))
                free_c[k] = not obs.hits(L, c, (x, y, x, y), clr + grid * 0.21)
        return free_c[k]

    def via_ok(ix, iy):
        k = (ix, iy)
        if k not in via_c:
            via_c[k] = not obs.via_hits(xyc(ix, iy), vdia, vdrill, clr, 0.25)
        return via_c[k]

    def h(ix, iy):
        if not goal_pts:
            return 0.0
        x, y = xyc(ix, iy)
        return min(max(abs(x - gx), abs(y - gy)) + (SQ2 - 1) * min(abs(x - gx), abs(y - gy)) for gx, gy in goal_pts)
    openh = []
    best = {}
    came = {}
    src_states = set()
    for (x, y, L) in sources:
        ix, iy = round((x - ox) / grid), round((y - oy) / grid)
        st = (ix, iy, L, -1)
        src_states.add(st)
        best[st] = 0.0
        heapq.heappush(openh, (h(ix, iy), 0.0, st))
    n_exp = 0
    while openh:
        f, g, st = heapq.heappop(openh)
        if best.get(st, 1e18) < g - 1e-9:
            continue
        ix, iy, L, d = st
        x, y = xyc(ix, iy)
        if st not in src_states and goals(x, y, L):
            path = [st]
            while path[-1] in came:
                path.append(came[path[-1]])
            path.reverse()
            return [(*xyc(p[0], p[1]), p[2]) for p in path], g
        n_exp += 1
        if n_exp > max_expand:
            break
        # ビア
        if True:
            L2 = B if L == F else F
            if via_ok(ix, iy) and free(ix, iy, L2):
                ns = (ix, iy, L2, -1)
                ng = g + via_cost
                if ng < best.get(ns, 1e18):
                    best[ns] = ng
                    came[ns] = st
                    heapq.heappush(openh, (ng + h(ix, iy), ng, ns))
        for nd, (dx, dy) in enumerate(hop.DIRS):
            if d >= 0:
                turn = min((nd - d) % 8, (d - nd) % 8)
                if turn >= 2:
                    continue
                tc = turn_cost * turn
            else:
                tc = 0.0
            jx, jy = ix + dx, iy + dy
            if not free(jx, jy, L):
                continue
            q = xyc(jx, jy)
            step = grid * (SQ2 if dx and dy else 1.0)
            pen = field.cost((x, y), q, L) if field else 0.0
            if pen is None:
                continue
            ns = (jx, jy, L, nd)
            ng = g + step + tc + pen
            if ng < best.get(ns, 1e18):
                best[ns] = ng
                came[ns] = st
                heapq.heappush(openh, (ng + h(jx, jy), ng, ns))
    return None, None


def to_polylines(path):
    """[(x, y, L)] → [(L, [点...])] と ビア位置。"""
    runs, vias = [], []
    cur = [path[0]]
    for p in path[1:]:
        if p[2] != cur[-1][2]:
            vias.append((p[0], p[1]))
            if len(cur) > 1:
                runs.append((cur[-1][2], hop.compress([(q[0], q[1]) for q in cur])))
            cur = [p]
        else:
            cur.append(p)
    if len(cur) > 1:
        runs.append((cur[-1][2], hop.compress([(q[0], q[1]) for q in cur])))
    return runs, vias
