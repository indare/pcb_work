#!/usr/bin/env python3
"""AMP_SEL trunk: keep short F fanouts, labor-save the rest.

Policy (NOW.md):
  - Keep pad fanout on F.Cu (default 3 mm geodesic along F).
  - Split at the fanout frontier; insert a through-via when missing.
  - Trunk beyond fanout:
      --mode rip (default): rip-up trunk F only (fanout+frontier vias kept).
        Leaves ratsnest for exploratory re-route. No blind B.Cu write.
      --mode safe: clearance-checked move to B else rip (heuristic; verify DRC).
      --mode blind: SetLayer(B) for all trunk (DRC-hostile; experiment only).

Scope: AmpBankSwitch and AmpBankRelay sheet footprints' bounding boxes.
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


def _seg_seg_dist_iu(ax, ay, bx, by, cx, cy, dx, dy) -> float:
    """Minimum distance between segment AB and CD (internal units)."""
    import math

    def dot(ux, uy, vx, vy):
        return ux * vx + uy * vy

    def clamp(t):
        return 0.0 if t < 0 else (1.0 if t > 1 else t)

    abx, aby = bx - ax, by - ay
    cdx, cdy = dx - cx, dy - cy
    acx, acy = cx - ax, cy - ay
    ab2 = abx * abx + aby * aby
    cd2 = cdx * cdx + cdy * cdy
    if ab2 < 1 and cd2 < 1:
        return math.hypot(acx, acy)
    # sample denser on longer seg
    best = 1e300
    steps = max(8, int(math.sqrt(max(ab2, cd2)) / from_mm(0.2)))
    for i in range(steps + 1):
        t = i / steps
        px, py = ax + abx * t, ay + aby * t
        if cd2 < 1:
            qx, qy = cx, cy
        else:
            u = clamp(dot(px - cx, py - cy, cdx, cdy) / cd2)
            qx, qy = cx + cdx * u, cy + cdy * u
        best = min(best, math.hypot(px - qx, py - qy))
    return best


def bcu_clearance_ok(board, track, netcode, clearance_iu, ignore_ids=None) -> bool:
    """True if track geometry is clear of other nets on B.Cu (+ via copper)."""
    ignore_ids = ignore_ids or set()
    ax, ay = track.GetStart().x, track.GetStart().y
    bx, by = track.GetEnd().x, track.GetEnd().y
    half = track.GetWidth() / 2.0
    need = half + clearance_iu

    for t in board.GetTracks():
        if id(t) in ignore_ids or id(t) == id(track):
            continue
        if t.GetNetCode() == netcode:
            continue
        if t.Type() == pcbnew.PCB_VIA_T:
            # via annular on B
            try:
                vw = t.GetWidth(B) / 2.0
            except TypeError:
                vw = t.GetFrontWidth() / 2.0 if hasattr(t, "GetFrontWidth") else from_mm(0.3)
            d = _seg_seg_dist_iu(ax, ay, bx, by, t.GetX(), t.GetY(), t.GetX(), t.GetY())
            if d < need + vw:
                return False
            continue
        if t.Type() != pcbnew.PCB_TRACE_T:
            continue
        if t.GetLayer() != B:
            continue
        d = _seg_seg_dist_iu(
            ax, ay, bx, by, t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y
        )
        if d < need + t.GetWidth() / 2.0:
            return False

    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetCode() == netcode:
                continue
            if not pad.IsOnLayer(B):
                continue
            pos = pad.GetPosition()
            # conservative: circle of pad size
            try:
                pr = max(pad.GetSizeX(), pad.GetSizeY()) / 2.0
            except Exception:
                pr = from_mm(0.5)
            d = _seg_seg_dist_iu(ax, ay, bx, by, pos.x, pos.y, pos.x, pos.y)
            if d < need + pr:
                return False
    return True


def point_clear_on_b(board, x_mm, y_mm, netcode, radius_iu, clearance_iu) -> bool:
    """Rough check: a via-sized disc at (x,y) clear of foreign B copper."""
    ax = ay = from_mm(x_mm)
    need = radius_iu / 2.0 + clearance_iu
    for t in board.GetTracks():
        if t.GetNetCode() == netcode:
            continue
        if t.Type() == pcbnew.PCB_VIA_T:
            try:
                vw = t.GetWidth(B) / 2.0
            except TypeError:
                vw = from_mm(0.3)
            d = ((t.GetX() - ax) ** 2 + (t.GetY() - ay) ** 2) ** 0.5
            if d < need + vw:
                return False
            continue
        if t.Type() != pcbnew.PCB_TRACE_T or t.GetLayer() != B:
            continue
        d = _seg_seg_dist_iu(
            ax, ay, ax, ay, t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y
        )
        if d < need + t.GetWidth() / 2.0:
            return False
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetCode() == netcode or not pad.IsOnLayer(B):
                continue
            pos = pad.GetPosition()
            try:
                pr = max(pad.GetSizeX(), pad.GetSizeY()) / 2.0
            except Exception:
                pr = from_mm(0.5)
            d = ((pos.x - ax) ** 2 + (pos.y - ay) ** 2) ** 0.5
            if d < need + pr:
                return False
    return True


def process_net(
    board, label, box, fps, netname, fanout_mm, sample, dry_run, stats, mode, no_new_vias=False
):
    margin = from_mm(5)
    clearance_iu = board.GetDesignSettings().GetSmallestClearanceValue()
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
            if da <= db:
                near_d, far_d = da, db
                from_start = True
            else:
                near_d, far_d = db, da
                from_start = False
            if not (near_d < fanout_mm < far_d):
                continue
            along = fanout_mm - near_d
            frac = along / L
            if not from_start:
                frac = 1.0 - frac
            if frac <= 0.05 or frac >= 0.95:
                continue
            if dry_run:
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
    move_nodes = {pt_key(t.GetStart()) for t in movable} | {
        pt_key(t.GetEnd()) for t in movable
    }

    boundary = set(fan_nodes & move_nodes)
    for n in move_nodes:
        d = dist.get(n, 1e9)
        if abs(d - fanout_mm) <= 0.35 or d <= fanout_mm + 0.15:
            boundary.add(n)

    via_w = sample.GetWidth(F) if sample else from_mm(0.6)
    vias_added = 0
    if not no_new_vias:
        for bp in boundary:
            if any(dist_mm(bp, vp) < 0.25 for vp in via_pts):
                continue
            if any(dist_mm(bp, pk) < 0.5 for pk in pad_pts):
                continue
            if mode != "blind" and not point_clear_on_b(
                board, bp[0], bp[1], netcode, via_w, clearance_iu
            ):
                continue
            if not dry_run:
                add_via(board, from_mm(bp[0]), from_mm(bp[1]), netcode, sample)
            vias_added += 1
            via_pts.add(bp)

    moved_mm = ripped_mm = 0.0
    moved_n = ripped_n = 0
    ignore = {id(t) for t in movable}
    to_remove = []
    for t in movable:
        L = mm(t.GetLength())
        if mode == "blind":
            do_move = True
        elif mode == "safe":
            do_move = bcu_clearance_ok(board, t, netcode, clearance_iu, ignore_ids=ignore)
        else:
            do_move = False
        if do_move:
            moved_mm += L
            moved_n += 1
            if not dry_run:
                t.SetLayer(B)
        else:
            ripped_mm += L
            ripped_n += 1
            to_remove.append(t)
    if not dry_run:
        for t in to_remove:
            board.Delete(t) if hasattr(board, "Delete") else board.Remove(t)

    keep_mm = sum(mm(t.GetLength()) for t in f_tracks if id(t) in fanout_ids)
    stats["moved_mm"] += moved_mm
    stats["moved_segs"] += moved_n
    stats["ripped_mm"] += ripped_mm
    stats["ripped_segs"] += ripped_n
    stats["vias_added"] += vias_added
    stats["kept_mm"] += keep_mm
    print(
        f"  {label} {netname}: move {moved_mm:.1f} mm/{moved_n}, "
        f"rip {ripped_mm:.1f} mm/{ripped_n}, keep fanout {keep_mm:.1f} mm, "
        f"vias+={vias_added}"
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
    ap.add_argument(
        "--mode",
        choices=("rip", "safe", "blind"),
        default="rip",
        help="rip=delete trunk F (default); safe=try B if clear else rip; blind=force B",
    )
    ap.add_argument(
        "--no-new-vias",
        action="store_true",
        help="Do not insert frontier vias (safer for rip; ratsnest from pads/existing vias)",
    )
    args = ap.parse_args()

    board = pcbnew.LoadBoard(str(args.board))
    sample = sample_amp_sel_via(board)
    switch_fps = sheet_fps(board, "AmpBankSwitch")
    relay_fps = sheet_fps(board, "AmpBankRelay")
    sb, rb = bbox(switch_fps), bbox(relay_fps)

    print(
        f"board={args.board} fanout={args.fanout_mm} mm mode={args.mode} dry={args.dry_run}"
    )
    print("BEFORE:")
    length_report(board, sb, "Switch")
    length_report(board, rb, "Relay")

    stats = {
        "moved_mm": 0.0,
        "moved_segs": 0,
        "ripped_mm": 0.0,
        "ripped_segs": 0,
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
                board,
                "Switch",
                sb,
                switch_fps,
                net,
                args.fanout_mm,
                sample,
                args.dry_run,
                stats,
                args.mode,
                args.no_new_vias,
            )
    if do_relay:
        print("APPLY Relay")
        for net in ("/AMP_SEL_L", "/AMP_SEL_R"):
            process_net(
                board,
                "Relay",
                rb,
                relay_fps,
                net,
                args.fanout_mm,
                sample,
                args.dry_run,
                stats,
                args.mode,
                args.no_new_vias,
            )

    print("AFTER:")
    length_report(board, sb, "Switch")
    length_report(board, rb, "Relay")
    print(
        f"summary: moved={stats['moved_mm']:.1f} mm/{stats['moved_segs']} "
        f"ripped={stats['ripped_mm']:.1f} mm/{stats['ripped_segs']} "
        f"vias+={stats['vias_added']} splits={stats['splits']} kept={stats['kept_mm']:.1f}"
    )

    if not args.dry_run:
        board.Save(str(args.board))
        print("saved", args.board)
    return 0


if __name__ == "__main__":
    sys.exit(main())
