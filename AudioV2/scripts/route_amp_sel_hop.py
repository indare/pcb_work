#!/usr/bin/env python3
"""Exploratory one-hop route for AMP_SEL on AmpBankSwitch.

First hop (default): U311 pin7 (/AMP_SEL_L) F fanout tip → existing B via/trunk.
Follows NOW + audiov2-pcb-layout:
  - AMP_SEL trunk on B.Cu
  - no via on TSSOP pad (via at fanout tip only)
  - prefer 45° / orthogonal; avoid 90° corners when cheap
  - clearance vs other nets; soft penalty near SEL_CH
"""

from __future__ import annotations

import argparse
import heapq
import math
import sys
from pathlib import Path

import pcbnew

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BOARD = ROOT / "AudioV2" / "AudioV2Case.kicad_pcb"
F, B = pcbnew.F_Cu, pcbnew.B_Cu


def mm(iu: int) -> float:
    return pcbnew.ToMM(iu)


def iu(x: float) -> int:
    return int(pcbnew.FromMM(x))


def sample_via(board, net: str):
    for t in board.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() == net:
            return t
    return None


def add_via(board, x_mm, y_mm, netcode, sample):
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(pcbnew.VECTOR2I(iu(x_mm), iu(y_mm)))
    via.SetNetCode(netcode)
    if sample is not None:
        via.SetViaType(sample.GetViaType())
        via.SetDrill(sample.GetDrill())
        w = sample.GetWidth(F)
        if hasattr(via, "SetFrontWidth"):
            via.SetFrontWidth(w)
        try:
            via.SetWidth(F, w)
            via.SetWidth(B, w)
        except TypeError:
            via.SetWidth(w)
        try:
            via.SetLayerPair(F, B)
        except Exception:
            pass
    board.Add(via)
    return via


def add_track(board, x1, y1, x2, y2, layer, width, netcode):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pcbnew.VECTOR2I(iu(x1), iu(y1)))
    t.SetEnd(pcbnew.VECTOR2I(iu(x2), iu(y2)))
    t.SetLayer(layer)
    t.SetWidth(width)
    t.SetNetCode(netcode)
    board.Add(t)
    return t


def collect_obstacles(board, netcode, clearance_mm, track_w_mm):
    """List of (x1,y1,x2,y2,half_w_mm) obstacles on B + vias (as points)."""
    need = clearance_mm + track_w_mm / 2.0
    obs = []
    for t in board.GetTracks():
        if t.GetNetCode() == netcode:
            continue
        if t.Type() == pcbnew.PCB_VIA_T:
            try:
                r = mm(t.GetWidth(B)) / 2.0
            except TypeError:
                r = 0.3
            x, y = mm(t.GetX()), mm(t.GetY())
            obs.append((x, y, x, y, r + need))
            continue
        if t.Type() != pcbnew.PCB_TRACE_T or t.GetLayer() != B:
            continue
        obs.append(
            (
                mm(t.GetStart().x),
                mm(t.GetStart().y),
                mm(t.GetEnd().x),
                mm(t.GetEnd().y),
                mm(t.GetWidth()) / 2.0 + need,
            )
        )
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetCode() == netcode or not pad.IsOnLayer(B):
                continue
            pos = pad.GetPosition()
            try:
                r = max(mm(pad.GetSizeX()), mm(pad.GetSizeY())) / 2.0
            except Exception:
                r = 0.5
            obs.append((mm(pos.x), mm(pos.y), mm(pos.x), mm(pos.y), r + need))
    return obs


def seg_dist(ax, ay, bx, by, cx, cy, dx, dy):
    """Min distance between AB and CD."""

    def clamp(t):
        return 0.0 if t < 0 else 1.0 if t > 1 else t

    abx, aby = bx - ax, by - ay
    cdx, cdy = dx - cx, dy - cy
    ab2 = abx * abx + aby * aby
    cd2 = cdx * cdx + cdy * cdy
    best = 1e9
    steps = max(6, int(math.sqrt(max(ab2, cd2)) / 0.15))
    for i in range(steps + 1):
        t = i / steps
        px, py = ax + abx * t, ay + aby * t
        if cd2 < 1e-12:
            qx, qy = cx, cy
        else:
            u = clamp(((px - cx) * cdx + (py - cy) * cdy) / cd2)
            qx, qy = cx + cdx * u, cy + cdy * u
        best = min(best, math.hypot(px - qx, py - qy))
    return best


def point_clear(x, y, obs):
    for x1, y1, x2, y2, r in obs:
        if seg_dist(x, y, x, y, x1, y1, x2, y2) < r:
            return False
    return True


def edge_clear(x1, y1, x2, y2, obs):
    for ox1, oy1, ox2, oy2, r in obs:
        if seg_dist(x1, y1, x2, y2, ox1, oy1, ox2, oy2) < r:
            return False
    return True


def sel_penalty(board, x, y, net: str) -> float:
    """Soft cost if near SEL_CH tracks (TMUX §8.5: no parallel analog/digital)."""
    pen = 0.0
    for t in board.GetTracks():
        if "SEL_CH" not in t.GetNetname() or t.Type() != pcbnew.PCB_TRACE_T:
            continue
        ax, ay = mm(t.GetStart().x), mm(t.GetStart().y)
        bx, by = mm(t.GetEnd().x), mm(t.GetEnd().y)
        d = seg_dist(x, y, x, y, ax, ay, bx, by)
        if d < 1.0:
            pen += (1.0 - d) * 2.0
    return pen


def astar(board, start, goal, obs, grid=0.25, net="/AMP_SEL_L"):
    """8-connected A* on B.Cu. Returns list of (x,y) including start/goal."""
    sx, sy = start
    gx, gy = goal

    def key(p):
        return (round(p[0] / grid), round(p[1] / grid))

    def heur(p):
        # octile
        dx, dy = abs(p[0] - gx), abs(p[1] - gy)
        return max(dx, dy) + (math.sqrt(2) - 1) * min(dx, dy)

    neighbors = [
        (grid, 0),
        (-grid, 0),
        (0, grid),
        (0, -grid),
        (grid, grid),
        (grid, -grid),
        (-grid, grid),
        (-grid, -grid),
    ]

    start_k = key(start)
    goal_k = key(goal)
    open_h = [(heur(start), 0.0, start_k, start)]
    came = {}
    gscore = {start_k: 0.0}
    closed = set()

    # expand search box
    margin = 8.0
    xmin = min(sx, gx) - margin
    xmax = max(sx, gx) + margin
    ymin = min(sy, gy) - margin
    ymax = max(sy, gy) + margin

    while open_h:
        _, g, ck, cur = heapq.heappop(open_h)
        if ck in closed:
            continue
        closed.add(ck)
        if ck == goal_k or math.hypot(cur[0] - gx, cur[1] - gy) < grid * 0.75:
            # reconstruct
            path = [cur]
            while ck in came:
                ck, cur = came[ck]
                path.append(cur)
            path.reverse()
            if path[-1] != goal:
                path.append(goal)
            return path

        for dx, dy in neighbors:
            nxt = (cur[0] + dx, cur[1] + dy)
            if not (xmin <= nxt[0] <= xmax and ymin <= nxt[1] <= ymax):
                continue
            if not point_clear(nxt[0], nxt[1], obs):
                continue
            if not edge_clear(cur[0], cur[1], nxt[0], nxt[1], obs):
                continue
            step = math.hypot(dx, dy)
            # prefer ortho slightly less than diagonal already via step length
            cost = step + 0.15 * sel_penalty(board, nxt[0], nxt[1], net)
            nk = key(nxt)
            ng = g + cost
            if nk not in gscore or ng < gscore[nk] - 1e-9:
                gscore[nk] = ng
                came[nk] = (ck, cur)
                heapq.heappush(open_h, (ng + heur(nxt), ng, nk, nxt))

    return None


def simplify(path, obs):
    """Remove intermediate points when direct segment is clear (keeps 45/ortho)."""
    if len(path) <= 2:
        return path
    out = [path[0]]
    i = 0
    while i < len(path) - 1:
        j = len(path) - 1
        advanced = False
        while j > i + 1:
            if edge_clear(path[i][0], path[i][1], path[j][0], path[j][1], obs):
                out.append(path[j])
                i = j
                advanced = True
                break
            j -= 1
        if not advanced:
            out.append(path[i + 1])
            i += 1
    # dedupe consecutive
    clean = [out[0]]
    for p in out[1:]:
        if math.hypot(p[0] - clean[-1][0], p[1] - clean[-1][1]) > 1e-4:
            clean.append(p)
    return clean


def find_u311_pin7_hop(board):
    """Return (via_xy on F stub, target_xy, netcode, width, pad, kind)."""
    net = "/AMP_SEL_L"
    pad = None
    netcode = 0
    for fp in board.GetFootprints():
        if fp.GetReference() != "U311":
            continue
        for p in fp.Pads():
            if p.GetNumber() == "7" and p.GetNetname() == net:
                pad = (mm(p.GetPosition().x), mm(p.GetPosition().y))
                netcode = p.GetNetCode()
    if pad is None:
        raise SystemExit("U311.7 /AMP_SEL_L not found")

    # Existing F stub endpoints (fanout column)
    f_points = []
    width = iu(0.2)
    for t in board.GetTracks():
        if t.GetNetname() != net or t.Type() != pcbnew.PCB_TRACE_T or t.GetLayer() != F:
            continue
        a = (mm(t.GetStart().x), mm(t.GetStart().y))
        b = (mm(t.GetEnd().x), mm(t.GetEnd().y))
        if min(math.hypot(a[0] - pad[0], a[1] - pad[1]), math.hypot(b[0] - pad[0], b[1] - pad[1])) < 5:
            f_points.extend([a, b])
            # also sample along segment
            for i in range(1, 8):
                tfr = i / 8
                f_points.append((a[0] + (b[0] - a[0]) * tfr, a[1] + (b[1] - a[1]) * tfr))
            width = t.GetWidth()
    if not f_points:
        raise SystemExit("no F fanout near U311.7")

    clearance = mm(board.GetDesignSettings().GetSmallestClearanceValue())
    obs = collect_obstacles(board, netcode, clearance, mm(width))
    # Via annulus ~0.3; stiffen obstacle radius for via placement
    via_obs = collect_obstacles(board, netcode, clearance, 0.6)

    goal_cands = []
    for t in board.GetTracks():
        if t.GetNetname() != net:
            continue
        if t.Type() == pcbnew.PCB_VIA_T:
            x, y = mm(t.GetX()), mm(t.GetY())
            if 480 < x < 580 and 120 < y < 230:
                goal_cands.append((x, y, "via"))
        elif t.Type() == pcbnew.PCB_TRACE_T and t.GetLayer() == B:
            a = (mm(t.GetStart().x), mm(t.GetStart().y))
            b = (mm(t.GetEnd().x), mm(t.GetEnd().y))
            if 480 < a[0] < 580:
                goal_cands.append((a[0], a[1], "B"))
                goal_cands.append((b[0], b[1], "B"))
    if not goal_cands:
        raise SystemExit("no B target")
    vias = [c for c in goal_cands if c[2] == "via"]
    pool = vias if vias else goal_cands
    # pick goal first (nearest existing via to pad)
    goal_t = min(pool, key=lambda c: math.hypot(c[0] - pad[0], c[1] - pad[1]))
    goal = (goal_t[0], goal_t[1])

    # Via site: on F stub, >=1.0mm from pad center (off TSSOP), clear of foreign B copper
    # Prefer not sitting on SEL (caught by via_obs). Rank by dist to goal.
    via_site = None
    best = 1e9
    for p in f_points:
        if math.hypot(p[0] - pad[0], p[1] - pad[1]) < 1.0:
            continue
        if not point_clear(p[0], p[1], via_obs):
            continue
        d = math.hypot(p[0] - goal[0], p[1] - goal[1])
        if d < best:
            best = d
            via_site = p
    if via_site is None:
        raise SystemExit("no clear via site on F fanout (SEL/copper blocking tip)")

    return via_site, goal, netcode, width, pad, goal_t[2]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--board", type=Path, default=DEFAULT_BOARD)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--grid", type=float, default=0.25)
    args = ap.parse_args()

    board = pcbnew.LoadBoard(str(args.board))
    tip, goal, netcode, width, pad, kind = find_u311_pin7_hop(board)
    print(f"hop1 U311.7 /AMP_SEL_L")
    print(f"  pad={pad}")
    print(f"  via_site(on F stub, clear of SEL)={tip} pad_dist={math.hypot(tip[0]-pad[0], tip[1]-pad[1]):.2f} mm")
    print(f"  goal(B {kind})={goal} dist={math.hypot(goal[0]-tip[0], goal[1]-tip[1]):.2f} mm")
    print("  refs: NOW AMP_SEL=B.Cu; TMUX7612 §8.5 no via on pad, avoid SEL∥analog, prefer non-90°")

    clearance = mm(board.GetDesignSettings().GetSmallestClearanceValue())
    track_w = mm(width)
    obs = collect_obstacles(board, netcode, clearance, track_w)
    via_obs = collect_obstacles(board, netcode, clearance, 0.6)
    if not point_clear(tip[0], tip[1], via_obs):
        print("WARNING: via site not clear — abort")
        return 1

    path = astar(board, tip, goal, obs, grid=args.grid)
    if not path:
        print("A* failed")
        return 2
    path = simplify(path, obs)
    print(f"  path points={len(path)}")
    for p in path:
        print(f"    {p[0]:.3f}, {p[1]:.3f}")

    if args.dry_run:
        print("dry-run: not saved")
        return 0

    sample = sample_via(board, "/AMP_SEL_L")
    add_via(board, tip[0], tip[1], netcode, sample)
    for i in range(len(path) - 1):
        add_track(
            board,
            path[i][0],
            path[i][1],
            path[i + 1][0],
            path[i + 1][1],
            B,
            width,
            netcode,
        )
    board.Save(str(args.board))
    print("saved", args.board)
    return 0


if __name__ == "__main__":
    sys.exit(main())
