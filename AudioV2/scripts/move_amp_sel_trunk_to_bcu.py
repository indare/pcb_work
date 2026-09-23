#!/usr/bin/env python3
"""Move AMP_SEL trunk copper from F.Cu to B.Cu after short fanouts.

Policy (NOW.md):
  - Keep pad fanout on F.Cu (default 3 mm geodesic along F).
  - After fanout reaches the next via / frontier, trunk runs on B.Cu.
  - At F/B frontier without a via, insert a through-via (clone geometry from
    an existing AMP_SEL via when possible).
  - Long F segments that cross the fanout radius are split at the frontier.

Scope: AmpBankSwitch and AmpBankRelay sheet footprints' bounding boxes.
Dry-run: pass --dry-run. Restore source board yourself if needed.
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict, deque
from pathlib import Path

import pcbnew

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BOARD = ROOT / "AudioV2" / "AudioV2Case.kicad_pcb"

F = pcbnew.F_Cu
B = pcbnew.B_Cu


def mm(iu: int) -> float:
    return pcbnew.ToMM(iu)


def from_mm(x: float) -> int:
    return int(pcbnew.FromMM(x))


def pt_key(p) -> tuple[float, float]:
    return (round(mm(p.x), 3), round(mm(p.y), 3))


def dist_mm(a: tuple[float, float], b: tuple[float, float]) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def sheet_fps(board, needle: str):
    out = []
    for fp in board.GetFootprints():
        sn = fp.GetSheetname() or ""
        if needle in sn:
            out.append(fp)
    return out


def bbox(fps):
    xs, ys = [], []
    for fp in fps:
        bb = fp.GetBoundingBox()
        xs += [bb.GetLeft(), bb.GetRight()]
        ys += [bb.GetTop(), bb.GetBottom()]
    return min(xs), min(ys), max(xs), max(ys)


def in_box(x, y, box, margin):
    l, t, r, b = box
    return l - margin <= x <= r + margin and t - margin <= y <= b + margin


def sample_amp_sel_via(board):
    for t in board.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T and "AMP_SEL" in t.GetNetname():
            return t
    return None


def add_via(board, x_iu, y_iu, netcode, sample):
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(pcbnew.VECTOR2I(int(x_iu), int(y_iu)))
    via.SetNetCode(netcode)
    if sample is not None:
        via.SetViaType(sample.GetViaType())
        via.SetDrill(sample.GetDrill())
        w = sample.GetWidth(F)
        # KiCad 10: prefer SetFrontWidth / SetWidth(layer)
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
    else:
        if hasattr(via, "SetFrontWidth"):
            via.SetFrontWidth(from_mm(0.6))
        via.SetDrill(from_mm(0.3))
        try:
            via.SetLayerPair(F, B)
        except Exception:
            pass
    board.Add(via)
    return via


def split_track_at(board, track, frac: float):
    """Split track at fraction frac from start; return (first, second)."""
    sx, sy = track.GetStart().x, track.GetStart().y
    ex, ey = track.GetEnd().x, track.GetEnd().y
    cut = pcbnew.VECTOR2I(int(sx + (ex - sx) * frac), int(sy + (ey - sy) * frac))

    t2 = pcbnew.PCB_TRACK(board)
    t2.SetNetCode(track.GetNetCode())
    t2.SetLayer(track.GetLayer())
    t2.SetWidth(track.GetWidth())
    t2.SetStart(cut)
    t2.SetEnd(track.GetEnd())
    board.Add(t2)
    track.SetEnd(cut)
    return track, t2


def collect_f_tracks(board, netname, box, margin):
    out = []
    for t in board.GetTracks():
        if t.Type() != pcbnew.PCB_TRACE_T:
            continue
        if t.GetNetname() != netname or t.GetLayer() != F:
            continue
        mx = (t.GetStart().x + t.GetEnd().x) // 2
        my = (t.GetStart().y + t.GetEnd().y) // 2
        if in_box(mx, my, box, margin):
            out.append(t)
    return out


def build_dist(f_tracks, pads, snap_mm=0.8):
    """Geodesic distance along F from nearest pad. Pads snap to nearest endpoint."""
    adj = defaultdict(list)
    for t in f_tracks:
        a, b = pt_key(t.GetStart()), pt_key(t.GetEnd())
        L = max(mm(t.GetLength()), 1e-6)
        adj[a].append((b, t, L))
        adj[b].append((a, t, L))

    pad_pts = [pt_key(p.GetPosition()) for p in pads]

    def snap(pk):
        best, bestd = None, 1e9
        for node in adj:
            d = dist_mm(node, pk)
            if d < bestd:
                bestd, best = d, node
        return best if best is not None and bestd <= snap_mm else None

    dist = {}
    for pk in pad_pts:
        s = snap(pk)
        if s is None:
            continue
        dist[s] = 0.0
    changed = True
    guard = 0
    while changed and guard < 10000:
        guard += 1
        changed = False
        for u, d0 in list(dist.items()):
            for v, track, L in adj[u]:
                nd = d0 + L
                if v not in dist or nd < dist[v] - 1e-12:
                    dist[v] = nd
                    changed = True
    return dist, adj, pad_pts


def process_net(board, label, box, fps, netname, fanout_mm, sample, dry_run, stats):
    margin = from_mm(5)
    pads = []
    netcode = 0
    vias = []
    for t in board.GetTracks():
        if t.GetNetname() != netname:
            continue
        if t.Type() == pcbnew.PCB_VIA_T and in_box(t.GetX(), t.GetY(), box, margin):
            vias.append(t)
            netcode = t.GetNetCode()
    for fp in fps:
        for pad in fp.Pads():
            if pad.GetNetname() == netname:
                pads.append(pad)
                netcode = pad.GetNetCode()

    f_tracks = collect_f_tracks(board, netname, box, margin)
    if not f_tracks:
        print(f"  {label} {netname}: no F.Cu tracks")
        return

    # Split tracks that straddle the fanout radius
    for _pass in range(12):
        f_tracks = collect_f_tracks(board, netname, box, margin)
        dist, adj, pad_pts = build_dist(f_tracks, pads)
        split_done = False
        for t in list(f_tracks):
            a_pt, b_pt = pt_key(t.GetStart()), pt_key(t.GetEnd())
            da, db = dist.get(a_pt, 1e9), dist.get(b_pt, 1e9)
            L = mm(t.GetLength())
            if L < 0.2:
                continue
            # start nearer
            if da <= db:
                near_d, far_d = da, db
                from_start = True
            else:
                near_d, far_d = db, da
                from_start = False
            if not (near_d < fanout_mm < far_d):
                continue
            # fraction along geometric start→end
            along = fanout_mm - near_d
            frac = along / L
            if not from_start:
                frac = 1.0 - frac
            if frac <= 0.05 or frac >= 0.95:
                continue
            if dry_run:
                # count only; cannot mutate
                stats["splits"] += 1
                split_done = True
                break
            split_track_at(board, t, frac)
            stats["splits"] += 1
            split_done = True
            break
        if not split_done:
            break

    f_tracks = collect_f_tracks(board, netname, box, margin)
    dist, adj, pad_pts = build_dist(f_tracks, pads)

    fanout_ids = set()
    movable = []
    for t in f_tracks:
        a, b = pt_key(t.GetStart()), pt_key(t.GetEnd())
        da, db = dist.get(a, 1e9), dist.get(b, 1e9)
        # unreached F (not connected to any snapped pad) → treat as trunk (move)
        if min(da, db) >= 1e8:
            movable.append(t)
            continue
        if max(da, db) <= fanout_mm + 0.05:
            fanout_ids.add(id(t))
        else:
            movable.append(t)

    via_pts = {pt_key(pcbnew.VECTOR2I(v.GetX(), v.GetY())) for v in vias}
    for t in board.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() == netname:
            if in_box(t.GetX(), t.GetY(), box, margin):
                via_pts.add(pt_key(pcbnew.VECTOR2I(t.GetX(), t.GetY())))

    fan_nodes = set()
    for t in f_tracks:
        if id(t) in fanout_ids:
            fan_nodes.add(pt_key(t.GetStart()))
            fan_nodes.add(pt_key(t.GetEnd()))
    move_nodes = set()
    for t in movable:
        move_nodes.add(pt_key(t.GetStart()))
        move_nodes.add(pt_key(t.GetEnd()))

    boundary = set(fan_nodes & move_nodes)
    for n in move_nodes:
        d = dist.get(n, 1e9)
        if abs(d - fanout_mm) <= 0.35 or d <= fanout_mm + 0.15:
            boundary.add(n)

    vias_added = 0
    for bp in boundary:
        if any(dist_mm(bp, vp) < 0.25 for vp in via_pts):
            continue
        if any(dist_mm(bp, pk) < 0.5 for pk in pad_pts):
            continue
        if not dry_run:
            add_via(board, from_mm(bp[0]), from_mm(bp[1]), netcode, sample)
        vias_added += 1
        via_pts.add(bp)

    moved_mm = 0.0
    for t in movable:
        moved_mm += mm(t.GetLength())
        if not dry_run:
            t.SetLayer(B)

    keep_mm = sum(mm(t.GetLength()) for t in f_tracks if id(t) in fanout_ids)
    stats["moved_mm"] += moved_mm
    stats["moved_segs"] += len(movable)
    stats["vias_added"] += vias_added
    stats["kept_mm"] += keep_mm
    print(
        f"  {label} {netname}: move {moved_mm:.1f} mm / {len(movable)} segs, "
        f"keep fanout {keep_mm:.1f} mm, vias+={vias_added}, splits~={stats['splits']}"
        f"{' [dry]' if dry_run else ''}"
    )


def length_report(board, box, label):
    margin = from_mm(5)
    from collections import defaultdict

    lengths = defaultdict(float)
    vias = 0
    for t in board.GetTracks():
        if "AMP_SEL" not in t.GetNetname():
            continue
        if t.Type() == pcbnew.PCB_VIA_T:
            if in_box(t.GetX(), t.GetY(), box, margin):
                vias += 1
            continue
        if t.Type() != pcbnew.PCB_TRACE_T:
            continue
        mx = (t.GetStart().x + t.GetEnd().x) // 2
        my = (t.GetStart().y + t.GetEnd().y) // 2
        if not in_box(mx, my, box, margin):
            continue
        key = f"{t.GetNetname()}|{board.GetLayerName(t.GetLayer())}"
        lengths[key] += mm(t.GetLength())
    print(f"-- {label} -- vias={vias}")
    for k, v in sorted(lengths.items()):
        print(f"   {k}: {v:.1f} mm")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--board", type=Path, default=DEFAULT_BOARD)
    ap.add_argument("--fanout-mm", type=float, default=3.0)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--switch-only", action="store_true")
    ap.add_argument("--relay-only", action="store_true")
    args = ap.parse_args()

    board = pcbnew.LoadBoard(str(args.board))
    sample = sample_amp_sel_via(board)
    switch_fps = sheet_fps(board, "AmpBankSwitch")
    relay_fps = sheet_fps(board, "AmpBankRelay")
    sb, rb = bbox(switch_fps), bbox(relay_fps)

    print(f"board={args.board} fanout={args.fanout_mm} mm dry={args.dry_run}")
    print("BEFORE:")
    length_report(board, sb, "Switch")
    length_report(board, rb, "Relay")

    stats = defaultdict(float)
    stats = {
        "moved_mm": 0.0,
        "moved_segs": 0,
        "vias_added": 0,
        "kept_mm": 0.0,
        "splits": 0,
    }

    do_switch = not args.relay_only
    do_relay = not args.switch_only
    if do_switch:
        print("APPLY Switch")
        for net in ("/AMP_SEL_L", "/AMP_SEL_R"):
            process_net(
                board, "Switch", sb, switch_fps, net, args.fanout_mm, sample, args.dry_run, stats
            )
    if do_relay:
        print("APPLY Relay (AMP_SEL; MCP side is ordering note — same rule on AMP_SEL)")
        for net in ("/AMP_SEL_L", "/AMP_SEL_R"):
            process_net(
                board, "Relay", rb, relay_fps, net, args.fanout_mm, sample, args.dry_run, stats
            )

    print("AFTER:")
    length_report(board, sb, "Switch")
    length_report(board, rb, "Relay")
    print(
        f"summary: moved={stats['moved_mm']:.1f} mm segs={stats['moved_segs']} "
        f"vias+={stats['vias_added']} splits={stats['splits']} kept={stats['kept_mm']:.1f}"
    )

    if not args.dry_run:
        board.Save(str(args.board))
        print("saved", args.board)
    return 0


if __name__ == "__main__":
    # defaultdict used in main
    from collections import defaultdict

    sys.exit(main())
