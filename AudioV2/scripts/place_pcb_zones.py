#!/usr/bin/env python3
"""AudioV2Case.kicad_pcb を回路ツリー（sheetpath）に沿ってゾーン配置する。

方針:
  - 下辺 = パネル（MeasureControl の UI + ルートの箱配線ヘッダ）
  - 左上 = ルート音声（IN / Tone / Out）
  - 右上 = ルート電源
  - 中央 = AmpBankSwitch → AmpCh1..5 をタイル列
  - パネル直上 = MeasureControl 本体
  - NT1601-3 は下辺で近接

配線は触らない。向きは維持。KiCad の python（pcbnew）で実行。
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PCB = ROOT / "AudioV2" / "AudioV2Case.kicad_pcb"
SCH = ROOT / "AudioV2" / "AudioV2Case.kicad_sch"
OUT = ROOT / "out"
XML = OUT / "audiov2_pcb.xml"

# 配置グループ → (origin_x, origin_y, pitch, cols)
# KiCad: Y 下向き。
LAYOUT: dict[str, tuple[float, float, float, int]] = {
    "root_audio": (15.0, 15.0, 12.0, 10),
    "root_power": (320.0, 15.0, 14.0, 8),
    "amp_bank": (15.0, 90.0, 12.0, 8),
    # AmpCh タイルは別計算
    "root_out": (15.0, 250.0, 14.0, 8),
    "meas": (15.0, 310.0, 12.0, 14),
    "panel": (15.0, 430.0, 14.0, 12),
    "star": (270.0, 440.0, 8.0, 3),
}

AMPCH_ORIGIN = (15.0, 130.0)
AMPCH_TILE_W = 72.0  # mm per channel column
AMPCH_PITCH = 12.0
AMPCH_COLS = 5

PANEL_REFS = {
    "ENC1601", "ENC1602", "ENC1603",
    "A1602", "LCDDisplay1601", "J_OLED1601",
    "D1610", "D1611", "SW1601", "TP1601",
    "RV501", "RV502", "SW501", "SW502", "SW402",
}
STAR_REFS = {"NT1601", "NT1602", "NT1603"}


def _num(ref: str) -> int | None:
    m = re.match(r"[A-Z_#]+(\d+)", ref)
    return int(m.group(1)) if m else None


def sort_key(ref: str) -> tuple:
    n = _num(ref) or 0
    prefix = re.match(r"[A-Z_#]+", ref)
    p = prefix.group(0) if prefix else ref
    return (n // 100, p, n, ref)


def is_root_power(ref: str) -> bool:
    if ref in {"U201", "U202", "F201", "F202", "F203", "J201", "J202", "NT101"}:
        return True
    if re.match(r"^[CFUDR]20\d", ref) or re.match(r"^J20\d", ref):
        return True
    return False


def is_root_out(ref: str) -> bool:
    return ref in {
        "U501", "J_HP501", "J_LINE501", "J_RAIL501",
        "C501", "C502", "C503", "C504", "C505", "C506",
        "R501", "R502", "R503", "R504",
    }


def group_for(ref: str, sheetpath: str) -> str:
    """sheetpath 優先。ルートだけ音声/電源/出力に分割。"""
    if ref in STAR_REFS:
        return "star"
    if ref in PANEL_REFS or ref.startswith("R165"):
        return "panel"

    sp = sheetpath or "/"
    if sp.startswith("/AmpBankSwitch/AmpCh"):
        # /AmpBankSwitch/AmpCh3/ → ampch3
        m = re.search(r"AmpCh(\d+)", sp)
        return f"ampch{m.group(1)}" if m else "amp_bank"
    if sp.startswith("/AmpBankSwitch"):
        return "amp_bank"
    if sp.startswith("/MeasureControl"):
        return "meas"

    # ルート /
    if is_root_power(ref):
        return "root_power"
    if is_root_out(ref):
        return "root_out"
    return "root_audio"


def load_sheetpaths() -> dict[str, str]:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from update_pcb_from_sch import export_xml, parse_comps

    OUT.mkdir(parents=True, exist_ok=True)
    if not XML.is_file():
        export_xml(SCH, XML)
    try:
        comps = parse_comps(XML)
    except Exception:
        export_xml(SCH, XML)
        comps = parse_comps(XML)
    return {c["ref"]: c["sheetpath"] for c in comps}


def place_grid(items: list, ox: float, oy: float, pitch: float, cols: int, pcbnew) -> None:
    items = sorted(items, key=lambda fp: sort_key(fp.GetReference()))
    for i, fp in enumerate(items):
        col = i % cols
        row = i // cols
        fp.SetPosition(pcbnew.VECTOR2I(
            pcbnew.FromMM(ox + col * pitch),
            pcbnew.FromMM(oy + row * pitch),
        ))


def main() -> int:
    for ver in ("10.0", "9.0"):
        ki = Path(r"C:\Program Files\KiCad") / ver / "bin"
        if ki.is_dir():
            sys.path.extend([str(ki), str(ki / "Lib" / "site-packages")])
            break
    import pcbnew

    sheet_of = load_sheetpaths()
    board = pcbnew.LoadBoard(str(PCB))
    fps = list(board.GetFootprints())
    by: dict[str, list] = defaultdict(list)
    for fp in fps:
        ref = fp.GetReference()
        sp = sheet_of.get(ref, "/")
        by[group_for(ref, sp)].append(fp)

    for g, (ox, oy, pitch, cols) in LAYOUT.items():
        if g.startswith("ampch"):
            continue
        place_grid(by.get(g, []), ox, oy, pitch, cols, pcbnew)

    for ch in range(1, 6):
        g = f"ampch{ch}"
        ox = AMPCH_ORIGIN[0] + (ch - 1) * AMPCH_TILE_W
        oy = AMPCH_ORIGIN[1]
        place_grid(by.get(g, []), ox, oy, AMPCH_PITCH, AMPCH_COLS, pcbnew)

    board.Save(str(PCB))

    print(f"placed {len(fps)} footprints -> {PCB}")
    for g in sorted(by.keys(), key=lambda s: (s.startswith("ampch") and int(s[-1]) or 0, s)):
        refs = [fp.GetReference() for fp in sorted(by[g], key=lambda f: sort_key(f.GetReference()))]
        print(f"  {g:12} n={len(refs):3}  e.g. {refs[:6]}")
    missing = [fp.GetReference() for fp in fps if fp.GetReference() not in sheet_of]
    if missing:
        print("no sheetpath (treated as /):", missing[:20])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
