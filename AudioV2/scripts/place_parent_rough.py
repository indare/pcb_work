#!/usr/bin/env python3
"""親基板ラフ（案 B）: Edge.Cuts を親外枠にし、娘以外だけ再グリッド。

- 動かさない: /AmpBankSwitch 配下、スロット J_ANA101–103 / J_PWR101–103
- 動かす: root_audio / root_power / root_out / meas / panel / star
- 配線・向きは触らない
"""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PCB = ROOT / "AudioV2" / "AudioV2Case.kicad_pcb"

# 親外枠 + 娘カード外形（同一ファイル上の編集用。製造は板ごとに切り出す）
OUTLINE_PARENT = (5.0, 5.0, 455.0, 455.0)
OUTLINE_DAUGHTER = (340.0, 130.0, 450.0, 240.0)
OUTLINE_FRONTPANEL = (15.0, 470.0, 165.0, 620.0)  # 150×150（place_frontpanel_pcb.py と一致）

# 配置グループ → (origin_x, origin_y, pitch, cols) — 娘 bbox 340–450×130–240 を避ける
LAYOUT: dict[str, tuple[float, float, float, int]] = {
    "root_audio": (15.0, 15.0, 12.0, 10),
    "root_power": (200.0, 15.0, 14.0, 8),
    "root_out": (15.0, 250.0, 14.0, 8),
    "meas": (15.0, 310.0, 12.0, 14),
    "panel": (15.0, 430.0, 14.0, 12),
    "star": (270.0, 440.0, 8.0, 3),
}

SLOT_REFS = {
    "J_ANA101", "J_ANA102", "J_ANA103",
    "J_PWR101", "J_PWR102", "J_PWR103",
}

# sheetpath が XML に無いことがある娘取付穴
DAUGHTER_HOLE_REFS = {"H301", "H302", "H303", "H304"}

# FrontPanel 子基板（place_frontpanel_pcb.py が載せる）。親ラフでは動かさない
FRONTPANEL_REFS = {
    "ENC1601", "ENC1602", "ENC1603",
    "RV501", "RV502",
    "SW501", "SW402",
    "D403", "R401",
    "U1610", "C1650", "R1661", "R1662",
    "D1610", "D1611", "R1651", "R1652",
    "LCDDisplay1601",
    "U1609", "R1620", "C1631", "C1633", "C1630", "C1629",
    "J_PNL1602", "J_PNL_A1602",
}

def main() -> int:
    for ver in ("10.0", "9.0"):
        ki = Path(r"C:\Program Files\KiCad") / ver / "bin"
        if ki.is_dir():
            sys.path.extend([str(ki), str(ki / "Lib" / "site-packages")])
            break
    import pcbnew

    # Reuse grouping from place_pcb_zones
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from place_pcb_zones import group_for, load_sheetpaths, place_grid, sort_key

    sheet_of = load_sheetpaths()
    board = pcbnew.LoadBoard(str(PCB))

    # --- snapshot AmpBankSwitch positions ---
    before: dict[str, tuple[float, float]] = {}
    for fp in board.Footprints():
        ref = fp.GetReference()
        sp = sheet_of.get(ref, "/")
        if sp.startswith("/AmpBankSwitch") or ref in SLOT_REFS or ref in DAUGHTER_HOLE_REFS \
                or ref in FRONTPANEL_REFS:
            before[ref] = (
                pcbnew.ToMM(fp.GetPosition().x),
                pcbnew.ToMM(fp.GetPosition().y),
            )

    # --- Edge.Cuts: delete all, add parent outer + daughter card ---
    to_del = [d for d in board.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts]
    for d in to_del:
        board.Remove(d)

    def add_rect(x0: float, y0: float, x1: float, y1: float) -> None:
        corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
        for (ax, ay), (bx, by) in zip(corners, corners[1:]):
            seg = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_SEGMENT)
            seg.SetLayer(pcbnew.Edge_Cuts)
            seg.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(ax), pcbnew.FromMM(ay)))
            seg.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(bx), pcbnew.FromMM(by)))
            seg.SetWidth(pcbnew.FromMM(0.1))
            board.Add(seg)

    add_rect(*OUTLINE_PARENT)
    add_rect(*OUTLINE_DAUGHTER)
    add_rect(*OUTLINE_FRONTPANEL)
    x0, y0, x1, y1 = OUTLINE_PARENT

    # --- group & place parent only ---
    by: dict[str, list] = defaultdict(list)
    frozen = 0
    for fp in board.Footprints():
        ref = fp.GetReference()
        sp = sheet_of.get(ref, "/")
        g = group_for(ref, sp)
        if ref in SLOT_REFS or ref in DAUGHTER_HOLE_REFS or ref in FRONTPANEL_REFS:
            frozen += 1
            continue
        if g.startswith("ampch") or g == "amp_bank":
            frozen += 1
            continue
        if g in LAYOUT:
            by[g].append(fp)
        else:
            # unexpected group — leave alone
            frozen += 1

    for g, (ox, oy, pitch, cols) in LAYOUT.items():
        items = by.get(g, [])
        place_grid(items, ox, oy, pitch, cols, pcbnew)
        print(f"  {g:12} n={len(items):3} origin=({ox},{oy})")

    pcbnew.SaveBoard(str(PCB), board)

    # --- verify frozen ---
    board2 = pcbnew.LoadBoard(str(PCB))
    moved = []
    for fp in board2.Footprints():
        ref = fp.GetReference()
        if ref not in before:
            continue
        now = (pcbnew.ToMM(fp.GetPosition().x), pcbnew.ToMM(fp.GetPosition().y))
        old = before[ref]
        if abs(now[0] - old[0]) > 1e-6 or abs(now[1] - old[1]) > 1e-6:
            moved.append((ref, old, now))

    # all FP inside outline?
    outside = []
    for fp in board2.Footprints():
        x, y = pcbnew.ToMM(fp.GetPosition().x), pcbnew.ToMM(fp.GetPosition().y)
        if not (x0 - 0.5 <= x <= x1 + 0.5 and y0 - 0.5 <= y <= y1 + 0.5):
            outside.append((fp.GetReference(), x, y))

    print(f"\nsaved {PCB}")
    print(f"frozen (AmpBank+slots+other): {frozen}")
    print(f"AmpBank/slots moved: {len(moved)}")
    if moved[:10]:
        for m in moved[:10]:
            print(" ", m)
    print(f"outside outline: {len(outside)}")
    if outside[:10]:
        for o in outside[:10]:
            print(" ", o)

    bbox = board2.GetBoardEdgesBoundingBox()
    print(
        f"Edge bbox: ({pcbnew.ToMM(bbox.GetLeft()):.1f},{pcbnew.ToMM(bbox.GetTop()):.1f})"
        f"-({pcbnew.ToMM(bbox.GetRight()):.1f},{pcbnew.ToMM(bbox.GetBottom()):.1f})"
    )
    return 1 if moved or outside else 0


if __name__ == "__main__":
    raise SystemExit(main())
