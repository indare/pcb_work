#!/usr/bin/env python3
"""Align PCB footprint positions within each module to match schematic layout.

PowerModule footprints are left unchanged (already routed).
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PCB = ROOT / "AudioCase.kicad_pcb"

SCH_FILES = {
    "Controll.kicad_sch": ROOT / "Controll.kicad_sch",
    "EQModule.kicad_sch": ROOT / "EQModule.kicad_sch",
    "AmpModule.kicad_sch": ROOT / "AmpModule.kicad_sch",
}

SKIP_SHEETS = {"PowerModule.kicad_sch"}
MARGIN = 0.92  # fit inside current module cluster


def fmt_num(v: float) -> str:
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return s if s else "0"


def parse_schematic(path: Path) -> dict[str, tuple[float, float, float]]:
    text = path.read_text()
    pos: dict[str, tuple[float, float, float]] = {}
    for m in re.finditer(
        r'\(symbol\n\t\t\(lib_id "[^"]+"\)\n\t\t\(at\s+([\d.-]+)\s+([\d.-]+)(?:\s+([\d.-]+))?\)'
        r'[\s\S]*?property "Reference" "([^"]+)"',
        text,
    ):
        pos[m.group(4)] = (float(m.group(1)), float(m.group(2)), float(m.group(3) or 0))
    return pos


def bbox(points: list[tuple[float, float]]) -> tuple[float, float, float, float]:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def center(bb: tuple[float, float, float, float]) -> tuple[float, float]:
    return (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2


def split_footprints(text: str) -> list[tuple[int, int, str]]:
    """Return list of (start, end, block) for each footprint."""
    parts: list[tuple[int, int, str]] = []
    for m in re.finditer(r"\n\t\(footprint ", text):
        start = m.start() + 1
        depth = 0
        i = start
        while i < len(text):
            if text[i : i + 11] == "(footprint ":
                depth += 1
            elif text[i : i + 1] == "(":
                depth += 1
            elif text[i : i + 1] == ")":
                depth -= 1
                if depth == 0:
                    parts.append((start, i + 1, text[start : i + 1]))
                    break
            i += 1
    return parts


def footprint_meta(block: str) -> dict | None:
    m_at = re.search(
        r'\(layer "[^"]+"\)\s*\n\t\t\(uuid "[^"]+"\)\s*\n\t\t\(at\s+([\d.-]+)\s+([\d.-]+)(?:\s+([\d.-]+))?\)',
        block,
    )
    m_ref = re.search(r'property "Reference" "([^"]+)"', block)
    m_sheet = re.search(r'sheetfile "([^"]+)"', block)
    if not (m_at and m_ref and m_sheet):
        return None
    return {
        "ref": m_ref.group(1),
        "sheet": m_sheet.group(1),
        "x": float(m_at.group(1)),
        "y": float(m_at.group(2)),
        "r": float(m_at.group(3) or 0),
        "at_match": m_at,
    }


def set_footprint_at(block: str, x: float, y: float, r: float | None = None) -> str:
    m = re.search(
        r'(\(layer "[^"]+"\)\s*\n\t\t\(uuid "[^"]+"\)\s*\n\t\t\(at\s+)([\d.-]+)\s+([\d.-]+)(?:\s+([\d.-]+))?(\))',
        block,
    )
    if not m:
        raise ValueError("could not find footprint placement (at ...)")
    rot = r if r is not None else float(m.group(4) or 0)
    repl = f"{m.group(1)}{fmt_num(x)} {fmt_num(y)} {fmt_num(rot)}{m.group(5)}"
    return block[: m.start()] + repl + block[m.end() :]


def main() -> int:
    sch_pos = {sheet: parse_schematic(path) for sheet, path in SCH_FILES.items()}
    pcb_text = PCB.read_text()
    footprints = split_footprints(pcb_text)

    moves: dict[str, list[tuple[str, float, float, float, float, float]]] = {}
    updated_blocks: dict[tuple[int, int], str] = {}

    by_sheet: dict[str, list[dict]] = {}
    for start, end, block in footprints:
        meta = footprint_meta(block)
        if not meta:
            continue
        by_sheet.setdefault(meta["sheet"], []).append({**meta, "start": start, "end": end, "block": block})

    for sheet, items in by_sheet.items():
        if sheet in SKIP_SHEETS:
            print(f"skip {sheet} ({len(items)} footprints)")
            continue

        sch = sch_pos.get(sheet, {})
        matched = [it for it in items if it["ref"] in sch]
        if len(matched) < 2:
            print(f"skip {sheet}: too few matched refs ({len(matched)})")
            continue

        pcb_pts = [(it["x"], it["y"]) for it in matched]
        sch_pts = [(sch[it["ref"]][0], sch[it["ref"]][1]) for it in matched]

        pcb_bb = bbox(pcb_pts)
        sch_bb = bbox(sch_pts)
        pcb_c = center(pcb_bb)
        sch_c = center(sch_bb)

        sch_w = max(sch_bb[2] - sch_bb[0], 1.0)
        sch_h = max(sch_bb[3] - sch_bb[1], 1.0)
        pcb_w = max(pcb_bb[2] - pcb_bb[0], 1.0)
        pcb_h = max(pcb_bb[3] - pcb_bb[1], 1.0)
        scale = min(pcb_w / sch_w, pcb_h / sch_h) * MARGIN

        sheet_moves = []
        for it in matched:
            sx, sy, sr = sch[it["ref"]]
            nx = pcb_c[0] + scale * (sx - sch_c[0])
            ny = pcb_c[1] + scale * (sy - sch_c[1])
            new_block = set_footprint_at(it["block"], nx, ny, it["r"])
            updated_blocks[(it["start"], it["end"])] = new_block
            dx, dy = nx - it["x"], ny - it["y"]
            sheet_moves.append((it["ref"], it["x"], it["y"], nx, ny, dx))
        moves[sheet] = sheet_moves
        print(
            f"{sheet}: moved {len(matched)} fp, scale={scale:.3f}, "
            f"pcb area {pcb_w:.1f}x{pcb_h:.1f} mm"
        )

    if not updated_blocks:
        print("nothing to update")
        return 1

  # rebuild pcb from end to start
    out = pcb_text
    for start, end in sorted(updated_blocks.keys(), reverse=True):
        out = out[:start] + updated_blocks[(start, end)] + out[end:]

    PCB.write_text(out)
    print(f"written {PCB}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
