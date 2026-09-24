#!/usr/bin/env python3
"""FrontPanel 子基板ラフ: 正方形 Edge.Cuts ＋関係部品をその中へ載せる。

- 親外枠・AmpBank 娘外形は触らない（追記のみ）
- 動かすのは FrontPanel シートの実部品だけ（J_PNL1601 / Pico / ヘッダは残す）
- 向きは維持。配線は触らない

座標（編集用・親の南）：(15,470)–(125,580) = 110×110 mm
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PCB = ROOT / "AudioV2.1" / "AudioV2Case.kicad_pcb"

# 親南の空き。AmpBank 娘 (340–450)×(130–240)・親 (5–455) と非交差
# 操作系（ENC+ポット+SW+表示）を載せるので 150×150
OUTLINE_FP = (15.0, 470.0, 165.0, 620.0)  # 150×150
OX, OY = OUTLINE_FP[0], OUTLINE_FP[1]

# 基板ローカル（原点=外形 NW）。Y 下向き。
# 左→右: PWR → ENC_CH → LCD → BASS → TREBLE → VOL×2 → DEST（HP/LINE は母板右端）
PLACE: dict[str, tuple[float, float]] = {
    "SW402": (15.0, 30.0),
    "D403": (27.0, 30.0),
    "R401": (27.0, 42.0),
    "ENC1601": (39.0, 30.0),       # CH
    "LCDDisplay1601": (57.0, 35.0),
    "ENC1602": (79.0, 30.0),       # BASS
    "ENC1603": (95.0, 30.0),       # TREBLE
    "RV501": (109.0, 30.0),
    "RV502": (121.0, 30.0),
    "SW501": (133.0, 30.0),        # DEST
    "R1651": (125.0, 48.0),
    "D1610": (133.0, 48.0),
    "R1652": (125.0, 58.0),
    "D1611": (133.0, 58.0),
    "U1609": (110.0, 85.0),
    "R1620": (100.0, 85.0),
    "C1633": (110.0, 98.0),
    "C1631": (100.0, 98.0),
    "C1630": (90.0, 98.0),
    "C1629": (90.0, 110.0),
    "U1610": (75.0, 105.0),
    "C1650": (93.0, 105.0),
    "R1661": (60.0, 105.0),
    "R1662": (60.0, 115.0),
    "J_PNL1602_1": (25.0, 135.0),
    "J_PNL1602_2": (55.0, 135.0),
    "J_PNL_A1602_1": (85.0, 135.0),
    "J_PNL_A1602_2": (110.0, 135.0),
}

FRONTPANEL_REFS = set(PLACE)


def _pcbnew():
    for ver in ("10.0", "9.0"):
        ki = Path(r"C:\Program Files\KiCad") / ver / "bin"
        if ki.is_dir():
            sys.path.extend([str(ki), str(ki / "Lib" / "site-packages")])
            break
    import pcbnew
    return pcbnew


def _edge_rects(pcbnew, board) -> list[tuple[float, float, float, float]]:
    """既存 Edge.Cuts の軸平行 bbox を返す（粗い）。"""
    xs: list[float] = []
    ys: list[float] = []
    segs = []
    for d in board.GetDrawings():
        if d.GetLayer() != pcbnew.Edge_Cuts:
            continue
        if hasattr(d, "GetStart"):
            segs.append((
                pcbnew.ToMM(d.GetStart().x), pcbnew.ToMM(d.GetStart().y),
                pcbnew.ToMM(d.GetEnd().x), pcbnew.ToMM(d.GetEnd().y),
            ))
    # 既に FrontPanel 外形があるか（中心が OUTLINE_FP 内）
    return segs


def _has_frontpanel_outline(pcbnew, board) -> bool:
    cx = (OUTLINE_FP[0] + OUTLINE_FP[2]) / 2
    cy = (OUTLINE_FP[1] + OUTLINE_FP[3]) / 2
    for d in board.GetDrawings():
        if d.GetLayer() != pcbnew.Edge_Cuts:
            continue
        if not hasattr(d, "GetStart"):
            continue
        for pt in (d.GetStart(), d.GetEnd()):
            x, y = pcbnew.ToMM(pt.x), pcbnew.ToMM(pt.y)
            if abs(x - OUTLINE_FP[0]) < 0.2 or abs(x - OUTLINE_FP[2]) < 0.2:
                if abs(y - OUTLINE_FP[1]) < 0.2 or abs(y - OUTLINE_FP[3]) < 0.2:
                    return True
            if abs(x - cx) < 60 and abs(y - cy) < 60 and (
                abs(x - OUTLINE_FP[0]) < 0.2 or abs(x - OUTLINE_FP[2]) < 0.2
                or abs(y - OUTLINE_FP[1]) < 0.2 or abs(y - OUTLINE_FP[3]) < 0.2
            ):
                # loose: any segment endpoint on FP outline
                if (abs(x - OUTLINE_FP[0]) < 0.2 or abs(x - OUTLINE_FP[2]) < 0.2) and \
                   OUTLINE_FP[1] - 0.2 <= y <= OUTLINE_FP[3] + 0.2:
                    return True
                if (abs(y - OUTLINE_FP[1]) < 0.2 or abs(y - OUTLINE_FP[3]) < 0.2) and \
                   OUTLINE_FP[0] - 0.2 <= x <= OUTLINE_FP[2] + 0.2:
                    return True
    return False


def _add_rect(pcbnew, board, x0: float, y0: float, x1: float, y1: float) -> None:
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    for (ax, ay), (bx, by) in zip(corners, corners[1:]):
        seg = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(ax), pcbnew.FromMM(ay)))
        seg.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(bx), pcbnew.FromMM(by)))
        seg.SetWidth(pcbnew.FromMM(0.1))
        board.Add(seg)


def _remove_frontpanel_outline(pcbnew, board) -> None:
    """旧 FrontPanel Edge（y≥470 の矩形辺）を消してから載せ直す。"""
    to_del = []
    for d in board.GetDrawings():
        if d.GetLayer() != pcbnew.Edge_Cuts or not hasattr(d, "GetStart"):
            continue
        ys = [pcbnew.ToMM(d.GetStart().y), pcbnew.ToMM(d.GetEnd().y)]
        xs = [pcbnew.ToMM(d.GetStart().x), pcbnew.ToMM(d.GetEnd().x)]
        if min(ys) >= 469.0 and max(ys) <= 621.0 and min(xs) >= 14.0 and max(xs) <= 166.0:
            to_del.append(d)
    for d in to_del:
        board.Remove(d)


def main() -> int:
    pcbnew = _pcbnew()
    board = pcbnew.LoadBoard(str(PCB))

    _remove_frontpanel_outline(pcbnew, board)
    _add_rect(pcbnew, board, *OUTLINE_FP)
    print(f"Edge.Cuts: FrontPanel {OUTLINE_FP[2]-OUTLINE_FP[0]:.0f}×"
          f"{OUTLINE_FP[3]-OUTLINE_FP[1]:.0f} @ ({OUTLINE_FP[0]},{OUTLINE_FP[1]})")

    moved = 0
    missing = []
    for fp in board.Footprints():
        ref = fp.GetReference()
        if ref not in PLACE:
            continue
        lx, ly = PLACE[ref]
        x, y = OX + lx, OY + ly
        # 向きは維持
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
        moved += 1
        print(f"  {ref:16} -> ({x:.2f}, {y:.2f})")

    for ref in sorted(FRONTPANEL_REFS):
        if not any(f.GetReference() == ref for f in board.Footprints()):
            missing.append(ref)

    pcbnew.SaveBoard(str(PCB), board)
    print(f"配置 {moved} 個。欠番（PCB に無し）: {missing or 'なし'}")
    print(f"書き出し: {PCB}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
