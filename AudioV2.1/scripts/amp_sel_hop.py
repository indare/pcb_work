#!/usr/bin/env python3
"""AMP_SEL 本線を B.Cu へ寄せる — 1ホップずつ、衝突判定付きで。

方針（NOW / AMP_SEL_ROUTING_HANDOFF / TMUX7612 §8.5）:
  - AMP_SEL の本線は B.Cu。パッドからのファンアウト（TSSOP はパッド上ビア禁止）だけ F に残す
  - SEL とアナログを並走させない。交差は直角だけ。90° の角を作らない
  - 無検査の載せ替え（SetLayer）はしない。全面の自動載せ替えもしない。**1回に1ホップ**

サブコマンド:
  report   基板ごとの AMP_SEL の F/B 長・ビア数と、SEL_CH*・アナログ（CH*_OUT_* / TONE_*）との並走長
  propose  B.Cu 上で A* 探索して経路点を出す（保存しない）。45°/直交のみ、SEL との並走に罰則
  apply    明示した経路点で1ホップ入れる。パッドから旧ビアまでの F を落とし、パッド直近に
           新ビアを打って B で合流させる（F ファンアウトは短い直線か 45° 折れ、既定の上限 4 mm）。不要になった旧ビアと B の尻尾は消す。
           衝突があれば保存しない。Switch 内のゾーンだけ再充填して保存
  tie      同じ部品の南北 D を本体の下で F 直結し、要らなくなった古い枝を分岐点まで消す
           （TSSOP は底面パッドが無いので本体下は空いている。DS §8.5 に禁止条項なし）
  rebend   既存の折れ線（既定 B、--layer F も可）を同じ両端の別の折れ線に差し替える（交差角の手直しなど）
  drc      kicad-cli の DRC を基準リビジョンと比べる（新しい違反 0・基板ごとの未接続数が不変なら 0 で終わる）

    python3 AudioV2.1/scripts/amp_sel_hop.py report
    python3 AudioV2.1/scripts/amp_sel_hop.py propose --net /AMP_SEL_L --from 557.675,170.6 --to 564.875,170.6
    python3 AudioV2.1/scripts/amp_sel_hop.py apply --pad U311:7 --via 557.675,170.6 --path 557.675,170.6 564.875,170.6
    python3 AudioV2.1/scripts/amp_sel_hop.py drc --base 3cc2748

衝突判定は KiCad 自身の形状（GetEffectiveShape().Collide()）で行う。正は最後に回す DRC。
"""
from __future__ import annotations

import argparse
import heapq
import json
import math
import os
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pcb_preview import sheet_region  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PCB = ROOT / "AudioV2.1" / "AudioV2Case.kicad_pcb"
OUT = ROOT / "out" / "amp_sel_hop"
F, B = pcbnew.F_Cu, pcbnew.B_Cu
NETS = ("/AMP_SEL_L", "/AMP_SEL_R")
BOARDS = ("AmpBankSwitch", "AmpBankRelay")
EPS = 0.005  # mm。端点一致の許容

mm = pcbnew.ToMM


def iu(v: float) -> int:
    return int(round(pcbnew.FromMM(v)))


def P(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(iu(x), iu(y))


def xy(v) -> tuple[float, float]:
    return mm(v.x), mm(v.y)


def parse_pt(s: str) -> tuple[float, float]:
    x, y = s.split(",")
    return float(x), float(y)


def near(a, b, eps=EPS) -> bool:
    return math.hypot(a[0] - b[0], a[1] - b[1]) <= eps


def load(path: Path = PCB):
    return pcbnew.LoadBoard(str(path))


def regions(board) -> dict[str, tuple]:
    return {name: sheet_region(board, name) for name in BOARDS}


def region_of(regs, x, y) -> str:
    for name, (x0, y0, x1, y1) in regs.items():
        if x0 <= x <= x1 and y0 <= y <= y1:
            return name
    return "親ほか"


def is_via(t) -> bool:
    return t.Type() == pcbnew.PCB_VIA_T


def design(board):
    ds = board.GetDesignSettings()
    return {
        "clr": mm(ds.GetSmallestClearanceValue()),
        "hole_clr": mm(ds.m_HoleClearance) if hasattr(ds, "m_HoleClearance") else 0.25,
        "hole2hole": mm(ds.m_HoleToHoleMin) if hasattr(ds, "m_HoleToHoleMin") else 0.25,
    }


# ---------------------------------------------------------------------------
# 障害物（他ネットの銅）
# ---------------------------------------------------------------------------

class Obstacles:
    """層ごとの他ネット銅を 2 mm バケットに入れて、近傍だけ Collide する。"""

    BUCKET = 2.0

    def __init__(self, board, netcode: int, layers=(F, B), box=None, ignore=()):
        self.items = {L: [] for L in layers}
        self.buckets = {L: defaultdict(list) for L in layers}
        self.holes = []  # (x, y, r)
        ignore = set(ignore)

        def keep(bb):
            if box is None:
                return True
            x0, y0, x1, y1 = box
            return not (mm(bb.GetRight()) < x0 or mm(bb.GetLeft()) > x1 or mm(bb.GetBottom()) < y0 or mm(bb.GetTop()) > y1)

        def add(L, shape, bb, desc):
            idx = len(self.items[L])
            self.items[L].append((shape, desc))
            bx0, by0 = int(mm(bb.GetLeft()) // self.BUCKET), int(mm(bb.GetTop()) // self.BUCKET)
            bx1, by1 = int(mm(bb.GetRight()) // self.BUCKET), int(mm(bb.GetBottom()) // self.BUCKET)
            for i in range(bx0, bx1 + 1):
                for j in range(by0, by1 + 1):
                    self.buckets[L][(i, j)].append(idx)

        for t in board.GetTracks():
            if t.GetNetCode() == netcode or t.m_Uuid.AsString() in ignore:
                continue
            bb = t.GetBoundingBox()
            if not keep(bb):
                continue
            kind = "via" if is_via(t) else "trk"
            for L in layers:
                if t.IsOnLayer(L):
                    add(L, t.GetEffectiveShape(L), bb, f"{kind} {t.GetNetname()} @{xy(t.GetPosition() if is_via(t) else t.GetStart())}")
            if is_via(t):
                self.holes.append((mm(t.GetX()), mm(t.GetY()), mm(t.GetDrill()) / 2))
        for fp in board.GetFootprints():
            for p in fp.Pads():
                bb = p.GetBoundingBox()
                if not keep(bb):
                    continue
                if p.GetDrillSizeX() > 0:
                    self.holes.append((mm(p.GetPosition().x), mm(p.GetPosition().y), mm(p.GetDrillSizeX()) / 2))
                if p.GetNetCode() == netcode:
                    continue
                for L in layers:
                    if p.IsOnLayer(L):
                        add(L, p.GetEffectiveShape(L), bb, f"pad {fp.GetReference()}.{p.GetNumber()} {p.GetNetname()}")

    def _cands(self, L, x0, y0, x1, y1):
        seen = set()
        for i in range(int(x0 // self.BUCKET), int(x1 // self.BUCKET) + 1):
            for j in range(int(y0 // self.BUCKET), int(y1 // self.BUCKET) + 1):
                for idx in self.buckets[L].get((i, j), ()):
                    if idx not in seen:
                        seen.add(idx)
                        yield self.items[L][idx]

    def hits(self, L, shape, box, clr) -> list[str]:
        x0, y0, x1, y1 = box
        m = clr + 1.0
        return [d for s, d in self._cands(L, x0 - m, y0 - m, x1 + m, y1 + m) if s.Collide(shape, iu(clr))]

    def seg_hits(self, L, a, b, width, clr) -> list[str]:
        shape = pcbnew.SHAPE_SEGMENT(P(*a), P(*b), iu(width))
        box = (min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))
        return self.hits(L, shape, box, clr)

    def via_hits(self, pos, dia, drill, clr, hole2hole) -> list[str]:
        shape = pcbnew.SHAPE_CIRCLE(P(*pos), iu(dia / 2))
        box = (pos[0], pos[1], pos[0], pos[1])
        out = [("F:" if L == F else "B:") + d for L in self.items for d in self.hits(L, shape, box, clr)]
        for hx, hy, hr in self.holes:
            if math.hypot(hx - pos[0], hy - pos[1]) - hr - drill / 2 < hole2hole - 1e-6:
                out.append(f"hole @({hx:.2f},{hy:.2f})")
        return out


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------

def _segs(board, pred):
    for t in board.GetTracks():
        if not is_via(t) and pred(t.GetNetname()):
            yield (xy(t.GetStart()), xy(t.GetEnd()), t.GetLayer())


def parallel_length(victims, aggressors, dist=1.0, ang_deg=20.0, step=0.1):
    """victim をなめて、近く（dist 以内）でほぼ平行（ang 未満）な aggressor がある長さ。層の同異で分ける。"""
    cos_min = math.cos(math.radians(ang_deg))
    same = other = 0.0
    agg = []
    for a, b, L in aggressors:
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy)
        if n > 1e-9:
            agg.append((a, b, L, dx / n, dy / n, n))
    for a, b, L in victims:
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy)
        if n < 1e-9:
            continue
        ux, uy = dx / n, dy / n
        cand = [g for g in agg if abs(ux * g[3] + uy * g[4]) >= cos_min
                and min(g[0][0], g[1][0]) - dist <= max(a[0], b[0]) and max(g[0][0], g[1][0]) + dist >= min(a[0], b[0])
                and min(g[0][1], g[1][1]) - dist <= max(a[1], b[1]) and max(g[0][1], g[1][1]) + dist >= min(a[1], b[1])]
        if not cand:
            continue
        k = max(1, int(n / step))
        for i in range(k):
            t = (i + 0.5) / k
            px, py = a[0] + dx * t, a[1] + dy * t
            best_same = best_other = False
            for (ga, gb, gL, gx, gy, gn) in cand:
                u = max(0.0, min(gn, (px - ga[0]) * gx + (py - ga[1]) * gy))
                qx, qy = ga[0] + gx * u, ga[1] + gy * u
                if math.hypot(px - qx, py - qy) <= dist:
                    if gL == L:
                        best_same = True
                    else:
                        best_other = True
            if best_same:
                same += n / k
            elif best_other:
                other += n / k
    return same, other


def cmd_report(a) -> int:
    board = load(a.board)
    regs = regions(board)
    stat = defaultdict(lambda: [0.0, 0.0, 0])  # (region, net) -> [F, B, vias]
    for t in board.GetTracks():
        n = t.GetNetname()
        if n not in NETS:
            continue
        if is_via(t):
            stat[(region_of(regs, mm(t.GetX()), mm(t.GetY())), n)][2] += 1
            continue
        (sx, sy), (ex, ey) = xy(t.GetStart()), xy(t.GetEnd())
        r = region_of(regs, (sx + ex) / 2, (sy + ey) / 2)
        stat[(r, n)][0 if t.GetLayer() == F else 1] += mm(t.GetLength())
    print("基板      ネット         F.Cu[mm]  B.Cu[mm]  ビア")
    for (r, n), (f, b, v) in sorted(stat.items()):
        print(f"{r.replace('AmpBank', ''):10s}{n:12s}{f:9.1f}{b:10.1f}{v:6d}")

    sel = list(_segs(board, lambda n: "SEL_CH" in n))
    ana = list(_segs(board, lambda n: "_OUT_" in n or "TONE_" in n))
    print("\n並走長 [mm]（1 mm 以内・20° 未満。同層 / 反対層）")
    print("基板      ネット        vs SEL_CH*        vs CH*_OUT/TONE")
    for name, (x0, y0, x1, y1) in regs.items():
        inb = lambda s: x0 <= (s[0][0] + s[1][0]) / 2 <= x1 and y0 <= (s[0][1] + s[1][1]) / 2 <= y1  # noqa: E731
        for n in NETS:
            vic = [s for s in _segs(board, lambda m, n=n: m == n) if inb(s)]
            s1 = parallel_length(vic, [s for s in sel if inb(s)])
            s2 = parallel_length(vic, [s for s in ana if inb(s)])
            print(f"{name.replace('AmpBank', ''):10s}{n:12s}{s1[0]:6.1f} / {s1[1]:5.1f}     {s2[0]:6.1f} / {s2[1]:5.1f}")
    return 0


# ---------------------------------------------------------------------------
# propose（A*）
# ---------------------------------------------------------------------------

DIRS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]


def octilinear(a, b, tol_deg=0.5) -> bool:
    ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 45.0
    return ang < tol_deg or ang > 45.0 - tol_deg


def _intersect(a, b, c, d):
    r = (b[0] - a[0], b[1] - a[1])
    q = (d[0] - c[0], d[1] - c[1])
    den = r[0] * q[1] - r[1] * q[0]
    if abs(den) < 1e-12:
        return None
    t = ((c[0] - a[0]) * q[1] - (c[1] - a[1]) * q[0]) / den
    u = ((c[0] - a[0]) * r[1] - (c[1] - a[1]) * r[0]) / den
    return (a[0] + t * r[0], a[1] + t * r[1]) if 0 <= t <= 1 and 0 <= u <= 1 else None


def crossings(board, pts, layer, own: str = ""):
    """経路 pts（layer 上）が反対層の SEL_CH* / アナログ（もう一方の AMP_SEL を含む）と交わる点と角度。
    §8.5: SEL とは直角だけ。アナログどうしも直角が望ましい（SCAA082 p14: 隣の層どうしも 90°）。"""
    other = F if layer == B else B
    names = {}
    for t in board.GetTracks():
        if not is_via(t) and t.GetLayer() == other:
            names[(xy(t.GetStart()), xy(t.GetEnd()))] = t.GetNetname()
    res = []
    for (c, d, L) in _segs(board, lambda n: ("SEL_CH" in n or "_OUT_" in n or "TONE_" in n
                                            or (n in NETS and n != own))):
        if L != other:
            continue
        for a, e in zip(pts, pts[1:]):
            x = _intersect(a, e, c, d)
            if x is not None:
                a1 = math.atan2(e[1] - a[1], e[0] - a[0])
                a2 = math.atan2(d[1] - c[1], d[0] - c[0])
                res.append((names.get((c, d), "?"), x, abs((math.degrees(a1 - a2) + 90) % 180 - 90)))
    return res


def check_crossings(board, pts, layer, tol=5.0, own: str = "", strict_analog: bool = False) -> list[str]:
    bad = []
    for net, x, ang in crossings(board, pts, layer, own):
        tag = f"{net} と ({x[0]:.2f},{x[1]:.2f}) で {ang:.0f}°"
        print(f"  交差: {tag}")
        if "SEL_CH" in net and ang < 90 - tol:
            bad.append(f"SEL と直角でない交差: {tag}")
        elif strict_analog and ang < 90 - tol:
            bad.append(f"アナログと直角でない交差: {tag}")
    return bad


def astar(board, net: str, start, goal, grid=0.1, margin=3.0, width=0.2):
    netcode = board.GetNetcodeFromNetname(net)
    clr = design(board)["clr"]
    box = (min(start[0], goal[0]) - margin, min(start[1], goal[1]) - margin,
           max(start[0], goal[0]) + margin, max(start[1], goal[1]) + margin)
    obs = Obstacles(board, netcode, layers=(B,), box=box)
    # 並走の罰則をかける相手（SEL は重く、同層はさらに重く）
    aggr = []
    for pred, w in ((lambda n: "SEL_CH" in n, 2.0), (lambda n: "_OUT_" in n or "TONE_" in n, 0.7)):
        for (a, b, L) in _segs(board, pred):
            if max(a[0], b[0]) < box[0] - 1 or min(a[0], b[0]) > box[2] + 1 or max(a[1], b[1]) < box[1] - 1 or min(a[1], b[1]) > box[3] + 1:
                continue
            dx, dy = b[0] - a[0], b[1] - a[1]
            n = math.hypot(dx, dy)
            if n > 1e-9:
                aggr.append((a, dx / n, dy / n, n, w * (2.0 if L == B else 1.0)))

    free_cache: dict = {}
    circle_r = width / 2

    def free(ix, iy):
        k = (ix, iy)
        if k not in free_cache:
            x, y = start[0] + ix * grid, start[1] + iy * grid
            if not (box[0] <= x <= box[2] and box[1] <= y <= box[3]):
                free_cache[k] = False
            else:
                c = pcbnew.SHAPE_CIRCLE(P(x, y), iu(circle_r))
                # 格子の間を斜めに抜けるぶんの余裕を足す
                free_cache[k] = not obs.hits(B, c, (x, y, x, y), clr + grid * 0.36)
        return free_cache[k]

    def penalty(x, y, ux, uy):
        """並走（30° 未満・1.2 mm 以内）への罰則。SEL は重く、同じ B 層はさらに重く。"""
        pen = 0.0
        for (a, gx, gy, gn, w) in aggr:
            if abs(ux * gx + uy * gy) < 0.87:
                continue
            u = max(0.0, min(gn, (x - a[0]) * gx + (y - a[1]) * gy))
            d = math.hypot(x - (a[0] + gx * u), y - (a[1] + gy * u))
            if d < 1.2:
                pen += w * (1.2 - d)
        return pen

    gi = (round((goal[0] - start[0]) / grid), round((goal[1] - start[1]) / grid))

    def h(ix, iy):
        dx, dy = abs(ix - gi[0]), abs(iy - gi[1])
        return grid * (max(dx, dy) + (math.sqrt(2) - 1) * min(dx, dy))

    openh = [(h(0, 0), 0.0, (0, 0), -1)]
    best = {((0, 0), -1): 0.0}
    came = {}
    while openh:
        f, g, node, d = heapq.heappop(openh)
        if best.get((node, d), 1e18) < g - 1e-12:
            continue
        if node == gi:
            path = [node]
            key = (node, d)
            while key in came:
                key = came[key]
                path.append(key[0])
            path.reverse()
            pts = [(start[0] + ix * grid, start[1] + iy * grid) for ix, iy in path]
            pts[-1] = goal
            return compress(pts)
        for nd, (dx, dy) in enumerate(DIRS):
            if d >= 0:
                turn = min((nd - d) % 8, (d - nd) % 8)
                if turn >= 3:
                    continue  # 135° 以上の折り返し・90° 以上は作らない
                tc = (0.0, 0.25, 3.0)[turn]
            else:
                tc = 0.0
            nx, ny = node[0] + dx, node[1] + dy
            if not free(nx, ny):
                continue
            step = grid * math.hypot(dx, dy)
            ux, uy = dx / math.hypot(dx, dy), dy / math.hypot(dx, dy)
            x, y = start[0] + nx * grid, start[1] + ny * grid
            ng = g + step + tc + step * penalty(x, y, ux, uy)
            key = ((nx, ny), nd)
            if ng < best.get(key, 1e18) - 1e-12:
                best[key] = ng
                came[key] = (node, d)
                heapq.heappush(openh, (ng + h(nx, ny), ng, (nx, ny), nd))
    return None


def compress(pts):
    """同じ向きの連続点をまとめる。"""
    out = [pts[0]]
    for p in pts[1:]:
        if len(out) >= 2:
            a, b = out[-2], out[-1]
            c1 = (b[0] - a[0]) * (p[1] - b[1]) - (b[1] - a[1]) * (p[0] - b[0])
            if abs(c1) < 1e-9 and (b[0] - a[0]) * (p[0] - b[0]) + (b[1] - a[1]) * (p[1] - b[1]) > 0:
                out[-1] = p
                continue
        out.append(p)
    return out


def cmd_propose(a) -> int:
    board = load(a.board)
    path = astar(board, a.net, a.frm, a.to, grid=a.grid, margin=a.margin)
    if not path:
        print("経路なし")
        return 2
    netcode = board.GetNetcodeFromNetname(a.net)
    obs = Obstacles(board, netcode, layers=(B,))
    clr = design(board)["clr"]
    total = 0.0
    bad = False
    for p, q in zip(path, path[1:]):
        hits = obs.seg_hits(B, p, q, 0.2, clr)
        total += math.hypot(q[0] - p[0], q[1] - p[1])
        flag = "" if octilinear(p, q) else "  (非45°)"
        if hits:
            bad = True
            flag += f"  衝突: {hits[:3]}"
        print(f"  ({p[0]:.3f},{p[1]:.3f}) -> ({q[0]:.3f},{q[1]:.3f}){flag}")
    print(f"長さ {total:.2f} mm（直線 {math.hypot(a.to[0] - a.frm[0], a.to[1] - a.frm[1]):.2f} mm）")
    print("--path " + " ".join(f"{p[0]:.3f},{p[1]:.3f}" for p in path))
    return 1 if bad else 0


# ---------------------------------------------------------------------------
# apply
# ---------------------------------------------------------------------------

def uid(o) -> str:
    """SWIG のラッパーは呼ぶたびに別物なので、id() ではなく UUID で見分ける。"""
    return o.m_Uuid.AsString()


def pad_of(board, spec: str):
    ref, num = spec.split(":")
    fp = board.FindFootprintByReference(ref)
    if fp is None:
        raise SystemExit(f"{ref} が無い")
    for p in fp.Pads():
        if p.GetNumber() == num:
            return p
    raise SystemExit(f"{spec} のパッドが無い")


def touching(board, netcode, pt, layer=None, exclude=()):
    """pt に端点がある同ネットのトラック（layer 指定可）。"""
    ex = {uid(e) for e in exclude}
    out = []
    for t in board.GetTracks():
        if t.GetNetCode() != netcode or is_via(t) or uid(t) in ex:
            continue
        if layer is not None and t.GetLayer() != layer:
            continue
        if near(xy(t.GetStart()), pt) or near(xy(t.GetEnd()), pt):
            out.append(t)
    return out


def via_at(board, netcode, pt):
    for t in board.GetTracks():
        if is_via(t) and t.GetNetCode() == netcode and near(xy(t.GetPosition()), pt):
            return t
    return None


def pad_at(board, netcode, pt, layer):
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.GetNetCode() == netcode and p.IsOnLayer(layer) and p.HitTest(P(*pt)):
                return p
    return None


def f_chain(board, pad):
    """パッドから F を辿って最初のビアまで。途中で分岐したら止める。"""
    netcode = pad.GetNetCode()
    cur = xy(pad.GetPosition())
    chain, seen = [], set()
    while True:
        nxt = [t for t in touching(board, netcode, cur, F) if t.m_Uuid.AsString() not in seen]
        if len(nxt) != 1:
            raise SystemExit(f"F の経路が {cur} で {len(nxt)} 本に分かれる（1本を期待）")
        t = nxt[0]
        seen.add(t.m_Uuid.AsString())
        chain.append(t)
        s, e = xy(t.GetStart()), xy(t.GetEnd())
        cur = e if near(s, cur) else s
        v = via_at(board, netcode, cur)
        if v is not None:
            return chain, v
        if pad_at(board, netcode, cur, F) is not None:
            raise SystemExit(f"F の経路が {cur} で別のパッドに入る（ビアを期待）")


def on_segment(p, a, b, eps=EPS) -> bool:
    dx, dy = b[0] - a[0], b[1] - a[1]
    n2 = dx * dx + dy * dy
    if n2 < 1e-12:
        return near(p, a, eps)
    u = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / n2
    if u < -1e-9 or u > 1 + 1e-9:
        return False
    return math.hypot(a[0] + dx * u - p[0], a[1] + dy * u - p[1]) <= eps


def add_track(board, a, b, layer, width, netcode):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(P(*a))
    t.SetEnd(P(*b))
    t.SetLayer(layer)
    t.SetWidth(width)
    t.SetNetCode(netcode)
    board.Add(t)
    return t


def add_via_like(board, pos, sample, netcode):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(P(*pos))
    v.SetViaType(sample.GetViaType())
    v.SetLayerPair(F, B)
    v.SetDrill(sample.GetDrill())
    v.SetWidth(F, sample.GetWidth(F))
    v.SetWidth(B, sample.GetWidth(B))
    v.SetNetCode(netcode)
    board.Add(v)
    return v


def prune_tail(board, netcode, pt, keep):
    """pt から伸びる B の尻尾（行き止まり）を消す。分岐・パッド・ビア・keep に当たったら止める。"""
    removed = []
    keep_ids = {uid(k) for k in keep}
    while True:
        if via_at(board, netcode, pt) is not None or pad_at(board, netcode, pt, B) is not None:
            return removed
        ts = touching(board, netcode, pt, B)
        if len(ts) != 1 or uid(ts[0]) in keep_ids:
            return removed
        t = ts[0]
        s, e = xy(t.GetStart()), xy(t.GetEnd())
        nxt = e if near(s, pt) else s
        removed.append((s, e))
        board.Remove(t)
        pt = nxt


def refill(board, region_box):
    x0, y0, x1, y1 = region_box
    zs = pcbnew.ZONES()
    for z in board.Zones():
        if z.GetIsRuleArea():
            continue
        bb = z.GetBoundingBox()
        if x0 - 0.5 <= mm(bb.GetLeft()) and mm(bb.GetRight()) <= x1 + 0.5 and y0 - 0.5 <= mm(bb.GetTop()) and mm(bb.GetBottom()) <= y1 + 0.5:
            zs.append(z)
    board.BuildConnectivity()
    pcbnew.ZONE_FILLER(board).Fill(zs)
    return len(zs)


def cmd_apply(a) -> int:
    board = load(a.board)
    pad = pad_of(board, a.pad)
    netcode, net = pad.GetNetCode(), pad.GetNetname()
    if net not in NETS:
        raise SystemExit(f"{a.pad} は {net}（AMP_SEL ではない）")
    padpt = xy(pad.GetPosition())
    via_pt, path = a.via, a.path
    if not near(path[0], via_pt):
        raise SystemExit("--path の始点は --via と同じ点にする")
    if pad.HitTest(P(*via_pt)):
        raise SystemExit("パッド上ビアは禁止（TSSOP）")
    for p, q in zip(path, path[1:]):
        if not octilinear(p, q):
            raise SystemExit(f"45°/直交でない区間: {p} -> {q}")
    for s1, s2, s3 in zip(path, path[1:], path[2:]):
        v1 = (s2[0] - s1[0], s2[1] - s1[1])
        v2 = (s3[0] - s2[0], s3[1] - s2[1])
        if v1[0] * v2[0] + v1[1] * v2[1] <= 1e-9:
            raise SystemExit(f"{s2} の角が 90° 以上")

    chain, old_via = f_chain(board, pad)
    width = chain[0].GetWidth()
    # F のファンアウト: パッド中心 →（--escape の折れ点）→ 新ビア。45°/直交のみ
    escape = [padpt] + list(a.escape or []) + [via_pt]
    for p, q in zip(escape, escape[1:]):
        if not octilinear(p, q):
            raise SystemExit(f"ファンアウトが 45°/直交でない: {p} -> {q}")
    esc = sum(math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(escape, escape[1:]))
    if esc > a.max_escape:
        raise SystemExit(f"ファンアウト {esc:.2f} mm が上限 {a.max_escape} mm を超える（F の本線を残すことになる）")
    old_via_pt = xy(old_via.GetPosition())
    print(f"{a.pad} {net}: F {len(chain)} 本・{sum(mm(t.GetLength()) for t in chain):.2f} mm → 旧ビア {old_via_pt}")

    # 合流点: 既存の B（同ネット）の端点か、その途中（途中なら分割する）
    join = path[-1]
    targets = [t for t in board.GetTracks() if t.GetNetCode() == netcode and not is_via(t)
               and t.GetLayer() == B and t not in chain]
    at_end = [t for t in targets if near(xy(t.GetStart()), join) or near(xy(t.GetEnd()), join)]
    mid = [t for t in targets if not at_end and on_segment(join, xy(t.GetStart()), xy(t.GetEnd()))]
    join_is_old_via = near(join, old_via_pt)
    if not at_end and not mid and not join_is_old_via:
        raise SystemExit(f"合流点 {join} が同ネットの B.Cu に乗っていない")

    # 事前の衝突判定（KiCad の形状で）
    clr = design(board)["clr"]
    d = design(board)
    ignore = {t.m_Uuid.AsString() for t in chain}
    obs = Obstacles(board, netcode, ignore=ignore)
    problems = []
    problems += [f"via: {h}" for h in obs.via_hits(via_pt, mm(old_via.GetWidth(F)), mm(old_via.GetDrill()), clr, d["hole2hole"])]
    for p, q in zip(escape, escape[1:]):
        problems += [f"F escape {p}->{q}: {h}" for h in obs.seg_hits(F, p, q, mm(width), clr)]
    for p, q in zip(path, path[1:]):
        problems += [f"B {p}->{q}: {h}" for h in obs.seg_hits(B, p, q, mm(width), clr)]
    problems += check_crossings(board, path, B)
    problems += check_crossings(board, escape, F)
    if problems:
        print("衝突あり。保存しない:")
        for pr in problems:
            print("  ", pr)
        return 2

    # 編集
    for t in chain:
        board.Remove(t)
    for p, q in zip(escape, escape[1:]):
        add_track(board, p, q, F, width, netcode)
    add_via_like(board, via_pt, old_via, netcode)
    new = [add_track(board, p, q, B, width, netcode) for p, q in zip(path, path[1:])]
    for t in mid:
        s, e = xy(t.GetStart()), xy(t.GetEnd())
        board.Remove(t)
        add_track(board, s, join, B, width, netcode)
        add_track(board, join, e, B, width, netcode)
    # 旧ビア: F 側に何も残らなければ不要（B 同士の合流にビアは要らない）
    removed_tail = []
    if not touching(board, netcode, old_via_pt, F) and pad_at(board, netcode, old_via_pt, F) is None:
        board.Remove(old_via)
        print(f"  旧ビア {old_via_pt} を削除")
        removed_tail = prune_tail(board, netcode, old_via_pt, keep=new)
        for s, e in removed_tail:
            print(f"  行き止まりの B {s}->{e} を削除")
    blen = sum(math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(path, path[1:]))
    print(f"  F ファンアウト {esc:.2f} mm ＋ 新ビア {via_pt} ＋ B {blen:.2f} mm（{len(path) - 1} 区間）")

    if a.dry_run:
        print("dry-run: 保存しない")
        return 0
    n = refill(board, sheet_region(board, "AmpBankSwitch") if a.refill == "AmpBankSwitch" else sheet_region(board, a.refill))
    print(f"  ゾーン再充填: {a.refill} 内 {n} 枚")
    board.Save(str(a.board))
    print(f"保存: {a.board}")
    return 0


def cmd_rebend(a) -> int:
    """既存の折れ線（同ネット・同じ層。既定 B）を、同じ両端の別の折れ線に差し替える。"""
    board = load(a.board)
    LY = F if a.layer == "F" else B
    netcode = board.GetNetcodeFromNetname(a.net)
    old, new_pts = a.old, a.new
    if not (near(old[0], new_pts[0]) and near(old[-1], new_pts[-1])):
        raise SystemExit("--old と --new の両端を揃える")
    for p, q in zip(new_pts, new_pts[1:]):
        if not octilinear(p, q):
            raise SystemExit(f"45°/直交でない区間: {p} -> {q}")
    for s1, s2, s3 in zip(new_pts, new_pts[1:], new_pts[2:]):
        if (s2[0] - s1[0]) * (s3[0] - s2[0]) + (s2[1] - s1[1]) * (s3[1] - s2[1]) <= 1e-9:
            raise SystemExit(f"{s2} の角が 90° 以上")
    segs = []
    for p, q in zip(old, old[1:]):
        hit = [t for t in board.GetTracks() if not is_via(t) and t.GetNetCode() == netcode and t.GetLayer() == LY
               and ((near(xy(t.GetStart()), p) and near(xy(t.GetEnd()), q)) or (near(xy(t.GetStart()), q) and near(xy(t.GetEnd()), p)))]
        if len(hit) != 1:
            raise SystemExit(f"{a.layer} 区間 {p}->{q} が {len(hit)} 本（1本を期待）")
        segs.append(hit[0])
    width = segs[0].GetWidth()
    obs = Obstacles(board, netcode, layers=(LY,))
    clr = design(board)["clr"]
    problems = [f"{a.layer} {p}->{q}: {h}" for p, q in zip(new_pts, new_pts[1:]) for h in obs.seg_hits(LY, p, q, mm(width), clr)]
    problems += check_crossings(board, new_pts, LY, own=a.net, strict_analog=a.strict_analog)
    if problems:
        print("衝突あり。保存しない:")
        for pr in problems:
            print("  ", pr)
        return 2
    for t in segs:
        board.Remove(t)
    for p, q in zip(new_pts, new_pts[1:]):
        add_track(board, p, q, LY, width, netcode)
    print(f"{a.net}: {a.layer} {len(segs)} 区間 → {len(new_pts) - 1} 区間")
    if a.dry_run:
        print("dry-run: 保存しない")
        return 0
    print(f"  ゾーン再充填: {refill(board, sheet_region(board, a.refill))} 枚")
    board.Save(str(a.board))
    print(f"保存: {a.board}")
    return 0


def _connected_at(board, netcode, pt, layers, skip):
    """pt で同ネットにつながるもの（端点のトラック・ビア・パッド・pt を途中に含むトラック）。"""
    ends, mids, vias, pads = [], [], [], []
    for t in board.GetTracks():
        if t.GetNetCode() != netcode or uid(t) in skip:
            continue
        if is_via(t):
            if near(xy(t.GetPosition()), pt):
                vias.append(t)
            continue
        if t.GetLayer() not in layers:
            continue
        s, e = xy(t.GetStart()), xy(t.GetEnd())
        if near(s, pt) or near(e, pt):
            ends.append(t)
        elif on_segment(pt, s, e):
            mids.append(t)
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.GetNetCode() == netcode and uid(p) not in skip and any(p.IsOnLayer(L) for L in layers) and p.HitTest(P(*pt)):
                pads.append(p)
    return ends, mids, vias, pads


def prune_branch(board, netcode, start, layers, skip, dry_run_log):
    """start から、分岐・パッド・端に当たるまで銅を辿って消す。途中に T 字の接続があればそこで切って止める。"""
    pt, layers, skip = start, set(layers), set(skip)
    removed = []
    while True:
        ends, mids, vias, pads = _connected_at(board, netcode, pt, layers, skip)
        if pads or mids or len(ends) + len(vias) != 1:
            return removed
        if vias:
            v = vias[0]
            removed.append(f"ビア {xy(v.GetPosition())}")
            skip.add(uid(v))
            board.Remove(v)
            layers = {F, B}
            continue
        t = ends[0]
        s, e = xy(t.GetStart()), xy(t.GetEnd())
        far = e if near(s, pt) else s
        # このトラックの途中に他の銅の端がつながっていれば（T 字）、そこから先は残す
        tees = []
        for o in board.GetTracks():
            if uid(o) == uid(t) or o.GetNetCode() != netcode or uid(o) in skip:
                continue
            cands = [xy(o.GetPosition())] if is_via(o) else ([xy(o.GetStart()), xy(o.GetEnd())] if o.GetLayer() == t.GetLayer() else [])
            for c in cands:
                if on_segment(c, s, e) and not near(c, s) and not near(c, e):
                    tees.append(c)
        if tees:
            cut = min(tees, key=lambda c: math.hypot(c[0] - pt[0], c[1] - pt[1]))
            width, layer = t.GetWidth(), t.GetLayer()
            board.Remove(t)
            kept = add_track(board, cut, far, layer, width, netcode)
            removed.append(f"{'F' if layer == F else 'B'} {pt}->{cut}（T 字で切って残りは保持）")
            # 残した区間にすっぽり重なる同ネットの短い区間は、切り口の外に端が浮くので消す
            for o in list(board.GetTracks()):
                if is_via(o) or o.GetNetCode() != netcode or o.GetLayer() != layer or uid(o) == uid(kept):
                    continue
                os_, oe = xy(o.GetStart()), xy(o.GetEnd())
                if on_segment(os_, cut, far) and on_segment(oe, cut, far):
                    removed.append(f"{'F' if layer == F else 'B'} {os_}->{oe}（残した区間と重複）")
                    board.Remove(o)
            return removed
        removed.append(f"{'F' if t.GetLayer() == F else 'B'} {s}->{e}")
        skip.add(uid(t))
        layers = {t.GetLayer()}
        board.Remove(t)
        pt = far


def cmd_tie(a) -> int:
    """同じネットの D パッド2つを本体の下で F 直結し、--drop 側の古い引き回しを分岐点まで消す。"""
    board = load(a.board)
    pa, pb = pad_of(board, a.drop), pad_of(board, a.keep)
    if pa.GetNetCode() != pb.GetNetCode() or pa.GetNetname() not in NETS:
        raise SystemExit("同じ AMP_SEL ネットのパッド2つを渡す")
    if pa.GetParentFootprint().GetReference() != pb.GetParentFootprint().GetReference():
        raise SystemExit("同じ部品の中だけ（本体下の南北 D 直結）")
    netcode = pa.GetNetCode()
    A, Bp = xy(pa.GetPosition()), xy(pb.GetPosition())
    if not octilinear(A, Bp):
        raise SystemExit("パッド間が 45°/直交でない")
    old = [t for t in touching(board, netcode, A, F)]
    width = old[0].GetWidth() if old else iu(0.2)
    obs = Obstacles(board, netcode, layers=(F,))
    problems = [f"F {A}->{Bp}: {h}" for h in obs.seg_hits(F, A, Bp, mm(width), design(board)["clr"])]
    problems += check_crossings(board, [A, Bp], F)
    if problems:
        print("衝突あり。保存しない:")
        for pr in problems:
            print("  ", pr)
        return 2
    tie = add_track(board, A, Bp, F, width, netcode)
    removed = prune_branch(board, netcode, A, {F}, {uid(tie), uid(pa)}, None)
    print(f"{a.drop}↔{a.keep} を F {math.hypot(Bp[0] - A[0], Bp[1] - A[1]):.2f} mm で直結。消したもの:")
    for r in removed:
        print("  ", r)
    if a.dry_run:
        print("dry-run: 保存しない")
        return 0
    print(f"  ゾーン再充填: {refill(board, sheet_region(board, a.refill))} 枚")
    board.Save(str(a.board))
    print(f"保存: {a.board}")
    return 0


# ---------------------------------------------------------------------------
# drc（基準リビジョンと比べる）
# ---------------------------------------------------------------------------

def _stage(pcb_bytes: bytes, dest: Path) -> Path:
    """AudioV2 の中身を symlink した作業場所に PCB だけ実体で置く（ライブラリ解決を本物と同じにする）。"""
    if dest.exists():
        shutil.rmtree(dest)
    (dest / "AudioV2.1").mkdir(parents=True)
    os.symlink(ROOT / "Audio", dest / "Audio")
    src = ROOT / "AudioV2.1"
    for e in src.iterdir():
        if e.name in ("AudioV2Case.kicad_pcb", "AudioV2Case.kicad_prl") or e.name.startswith("~"):
            continue
        if e.name == "AudioV2Case.kicad_pro":
            shutil.copy2(e, dest / "AudioV2.1" / e.name)
        else:
            os.symlink(e, dest / "AudioV2.1" / e.name)
    pcb = dest / "AudioV2.1" / "AudioV2Case.kicad_pcb"
    pcb.write_bytes(pcb_bytes)
    return pcb


def run_drc(pcb: Path, report: Path) -> dict:
    cli = os.environ.get("KICAD_CLI", "kicad-cli")
    subprocess.run([cli, "pcb", "drc", "--format", "json", "--severity-all", "--schematic-parity",
                    "-o", str(report), str(pcb)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return json.loads(report.read_text())


def _summ(rep: dict) -> tuple[Counter, Counter, int]:
    """違反は (種類, 相手の説明) の多重集合。未接続はネットごとの本数で数える
    （ratsnest のどの端を代表に出すかは実行ごとに変わるので、位置や基板では比べない）。"""
    vio = Counter()
    for v in rep.get("violations", []):
        # 同じ部品の複数パッドが同時に当たっているとき、DRC はどれか1つだけを報告し、どれを選ぶかは
        # ファイル内の並びで変わる。パッド番号とそのネットは落として部品単位で比べる
        vio[(v["type"], tuple(sorted(re.sub(r"Pad \S+ \[[^\]]*\] of (\S+)", r"Pad of \1", i["description"])
                                     for i in v.get("items", []))))] += 1
    unc = Counter()
    for v in rep.get("unconnected_items", []):
        m = re.search(r"\[([^\]]*)\]", v.get("items", [{}])[0].get("description", ""))
        unc[m.group(1) if m else "?"] += 1
    return vio, unc, len(rep.get("schematic_parity", []))


def cmd_drc(a) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    base_rev = subprocess.run(["git", "rev-parse", "--short", a.base], cwd=ROOT, check=True,
                              capture_output=True, text=True).stdout.strip()
    base_json = OUT / f"drc_{base_rev}.json"
    if not base_json.exists():
        blob = subprocess.run(["git", "show", f"{base_rev}:AudioV2.1/AudioV2Case.kicad_pcb"], cwd=ROOT,
                              check=True, capture_output=True).stdout
        run_drc(_stage(blob, OUT / "stage_base"), base_json)
    cur = run_drc(_stage(a.board.read_bytes(), OUT / "stage_cur"), OUT / "drc_cur.json")
    base = json.loads(base_json.read_text())
    bv, bu, bp = _summ(base)
    cv, cu, cp = _summ(cur)
    new, gone = cv - bv, bv - cv
    print(f"違反: 基準 {sum(bv.values())} → いま {sum(cv.values())}（新規 {sum(new.values())}・解消 {sum(gone.values())}）")
    for (typ, items), n in sorted(new.items()):
        print(f"  + {typ} ×{n}: {' | '.join(items)}")
    for (typ, items), n in sorted(gone.items()):
        print(f"  - {typ} ×{n}: {' | '.join(items)}")
    changed = sorted(n for n in set(bu) | set(cu) if bu[n] != cu[n])
    print(f"未接続: 基準 {sum(bu.values())} → いま {sum(cu.values())}"
          + ("" if not changed else "  変わったネット: " + "  ".join(f"{n} {bu[n]}→{cu[n]}" for n in changed)))
    for n in NETS:
        print(f"  {n}: {bu[n]} → {cu[n]}（基板をまたぐ ratsnest を含む）")
    print(f"schematic parity: {bp} → {cp}")
    worse = sum(new.values()) > 0 or any(cu[n] > bu[n] for n in cu) or cp > bp
    print("NG" if worse else "OK（新しい違反なし・どのネットも未接続は増えていない）")
    return 1 if worse else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--board", type=Path, default=PCB)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("report")
    p = sub.add_parser("propose")
    p.add_argument("--net", required=True, choices=NETS)
    p.add_argument("--from", dest="frm", type=parse_pt, required=True, help="新ビアの位置 x,y")
    p.add_argument("--to", type=parse_pt, required=True, help="B 本線への合流点 x,y")
    p.add_argument("--grid", type=float, default=0.1)
    p.add_argument("--margin", type=float, default=3.0)
    p = sub.add_parser("apply")
    p.add_argument("--pad", required=True, help="REF:番号（例 U311:7）")
    p.add_argument("--via", type=parse_pt, required=True)
    p.add_argument("--path", type=parse_pt, nargs="+", required=True, help="B の経路点（始点=新ビア、終点=合流点）")
    p.add_argument("--escape", type=parse_pt, nargs="*", help="F ファンアウトの折れ点（パッドと新ビアの間。既定は直線）")
    p.add_argument("--max-escape", type=float, default=4.0, help="F ファンアウトの長さの上限 [mm]")
    p.add_argument("--refill", default="AmpBankSwitch", help="再充填するゾーンの基板（シート名）")
    p.add_argument("--dry-run", action="store_true")
    p = sub.add_parser("rebend")
    p.add_argument("--net", required=True, choices=NETS)
    p.add_argument("--old", type=parse_pt, nargs="+", required=True, help="いまの折れ線")
    p.add_argument("--new", type=parse_pt, nargs="+", required=True, help="差し替え後（両端は同じ）")
    p.add_argument("--layer", choices=("B", "F"), default="B")
    p.add_argument("--strict-analog", action="store_true", help="アナログとの交差も直角以外は保存しない")
    p.add_argument("--refill", default="AmpBankSwitch")
    p.add_argument("--dry-run", action="store_true")
    p = sub.add_parser("tie")
    p.add_argument("--drop", required=True, help="古い引き回しを消す側のパッド（例 U311:2）")
    p.add_argument("--keep", required=True, help="つなぎ先のパッド（例 U311:15）")
    p.add_argument("--refill", default="AmpBankSwitch")
    p.add_argument("--dry-run", action="store_true")
    p = sub.add_parser("drc")
    p.add_argument("--base", default="HEAD", help="比べる基準のリビジョン")
    a = ap.parse_args()
    return {"report": cmd_report, "propose": cmd_propose, "apply": cmd_apply, "rebend": cmd_rebend, "tie": cmd_tie, "drc": cmd_drc}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
