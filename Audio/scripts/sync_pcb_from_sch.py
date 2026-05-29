#!/usr/bin/env python3
"""
Sync module .kicad_pcb footprints to match hierarchical schematics (AudioCase paths).

Rebuilds each module PCB from a clean template:
  - Footprints from schematic (position = schematic symbol coordinates)
  - Edge.Cuts / silk graphics copied from the previous PCB file
  - All routing cleared

Then run merge_audio_pcbs.py to rebuild AudioCase.kicad_pcb.

  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 \\
    Audio/scripts/sync_pcb_from_sch.py
"""

from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path

import wx  # noqa: E402

wx.App(False)

import pcbnew  # noqa: E402

AUDIO_DIR = Path(__file__).resolve().parent.parent
ROOT_UUID = "760b9589-09e7-434e-9ca2-6e4136e3b7a2"
KICAD_FP = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"
PROJECT_FP = str(AUDIO_DIR / "Library.pretty")
TEMPLATE = AUDIO_DIR / "AudioCase.empty.kicad_pcb"

MODULES = [
    {
        "name": "EQModule",
        "sch": "EQModule.kicad_sch",
        "pcb": "EQModule.kicad_pcb",
        "sheet": "/EQModule/",
        "sheet_uuid": "2b28f946-3cc3-4b39-916f-5bfe14900d1b",
        "outline": (69.9, 45.925, 165.7, 99.075),
    },
    {
        "name": "AmpModule",
        "sch": "AmpModule.kicad_sch",
        "pcb": "AmpModule.kicad_pcb",
        "sheet": "/AmpModule/",
        "sheet_uuid": "477be123-54b6-4d91-ae02-fb2ccb128622",
        "outline": (113.2, 62.5, 165.7, 104.0),
    },
    {
        "name": "PowerModule",
        "sch": "PowerModule.kicad_sch",
        "pcb": "PowerModule.kicad_pcb",
        "sheet": "/PowerModule/",
        "sheet_uuid": "c17b312b-fe0a-430c-8356-b220c9b28aff",
        "outline": (113.2, 104.0, 175.15, 141.020411),
    },
]


def parse_schematic(cfg: dict) -> dict[str, dict]:
    text = (AUDIO_DIR / cfg["sch"]).read_text()
    path_pat = (
        rf'path "/{ROOT_UUID}/{cfg["sheet_uuid"]}"\s*\n\s*\(reference "([^"]+)"'
    )
    components: dict[str, dict] = {}

    for block in re.findall(
        r"\t\(symbol\n.*?(?=\n\t\(symbol\n|\n\t\(sheet\n|\n\t\(wire\n|\n\t\(label\n|\n\t\(sheet_instances|\Z)",
        text,
        re.DOTALL,
    ):
        inst = re.search(path_pat, block)
        if not inst:
            continue
        ref = inst.group(1)
        if ref.startswith("#"):
            continue
        header = block.split("(instances)")[0]
        if "(on_board no)" in header:
            continue
        val = re.search(r'\(property "Value" "([^"]*)"', block)
        fp = re.search(r'\(property "Footprint" "([^"]*)"', block)
        at = re.search(r"\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)", block)
        footprint = fp.group(1) if fp else ""
        if not footprint:
            continue
        components[ref] = {
            "value": val.group(1) if val else "",
            "footprint": footprint,
            "x": float(at.group(1)) if at else 0.0,
            "y": float(at.group(2)) if at else 0.0,
            "rot": float(at.group(3)) if at and at.group(3) else 0.0,
        }
    return components


def fp_lib_path(lib: str) -> str | None:
    if lib == "Library":
        return PROJECT_FP
    path = os.path.join(KICAD_FP, f"{lib}.pretty")
    return path if os.path.isdir(path) else None


def load_footprint_template(
    board: pcbnew.BOARD, fpid: str, cache: dict
) -> pcbnew.FOOTPRINT | None:
    if fpid in cache:
        fp = pcbnew.FOOTPRINT(board)
        fp.CopyFrom(cache[fpid])
        return fp

    if ":" not in fpid:
        return None
    lib, name = fpid.split(":", 1)
    libpath = fp_lib_path(lib)
    if not libpath:
        print(f"    WARN: unknown lib for {fpid}")
        return None
    try:
        loaded = pcbnew.FootprintLoad(libpath, name)
        cache[fpid] = loaded
        fp = pcbnew.FOOTPRINT(board)
        fp.CopyFrom(loaded)
        return fp
    except Exception as exc:  # noqa: BLE001
        print(f"    WARN: cannot load {fpid}: {exc}")
        return None


def build_cache_from_boards() -> dict:
    cache: dict = {}
    for cfg in MODULES:
        path = AUDIO_DIR / cfg["pcb"]
        if not path.exists():
            continue
        board = pcbnew.LoadBoard(str(path))
        for fp in board.GetFootprints():
            key = fp.GetFPIDAsString()
            if ":" not in key:
                key = (
                    f"{fp.GetFPID().GetFullLibraryName()}:"
                    f"{fp.GetFPID().GetLibItemName()}"
                )
            if key not in cache:
                cache[key] = fp
    return cache


def copy_drawings(src: pcbnew.BOARD, dst: pcbnew.BOARD) -> int:
    count = 0
    makers = {
        "PCB_SHAPE": pcbnew.PCB_SHAPE,
        "PCB_TEXT": pcbnew.PCB_TEXT,
        "PCB_TEXTBOX": pcbnew.PCB_TEXTBOX,
    }
    for drawing in src.GetDrawings():
        maker = makers.get(drawing.GetClass())
        if maker is None:
            continue
        d = maker(dst)
        d.CopyFrom(drawing)
        dst.Add(d)
        count += 1
    return count


def add_footprint(
    board: pcbnew.BOARD,
    template: pcbnew.FOOTPRINT,
    ref: str,
    value: str,
    x_mm: float,
    y_mm: float,
    rot_deg: float,
    sheet: str,
    sch_file: str,
) -> None:
    fp = pcbnew.FOOTPRINT(board)
    fp.CopyFrom(template)
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x_mm), pcbnew.FromMM(y_mm)))
    fp.SetOrientation(pcbnew.EDA_ANGLE(rot_deg, pcbnew.DEGREES_T))
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetSheetname(sheet)
    fp.SetSheetfile(sch_file)
    board.Add(fp)


def add_board_outline(board: pcbnew.BOARD, outline: tuple[float, float, float, float]) -> None:
    x0, y0, x1, y1 = outline
    shape = pcbnew.PCB_SHAPE(board)
    shape.SetShape(pcbnew.SHAPE_T_RECT)
    shape.SetLayer(pcbnew.Edge_Cuts)
    shape.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x0), pcbnew.FromMM(y0)))
    shape.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
    shape.SetWidth(pcbnew.FromMM(0.05))
    board.Add(shape)


def sync_module(cfg: dict, cache: dict) -> None:
    sch = parse_schematic(cfg)
    pcb_path = AUDIO_DIR / cfg["pcb"]
    sheet = cfg["sheet"]
    sch_file = cfg["sch"]

    # Preserve board graphics from existing file
    old_board = pcbnew.LoadBoard(str(pcb_path)) if pcb_path.exists() else None

    shutil.copy2(TEMPLATE, pcb_path)
    board = pcbnew.LoadBoard(str(pcb_path))

    if old_board is not None:
        n_draw = copy_drawings(old_board, board)
    else:
        n_draw = 0

    has_edge = any(
        d.GetLayer() == pcbnew.Edge_Cuts for d in board.GetDrawings()
    )
    if not has_edge:
        add_board_outline(board, cfg["outline"])
        n_draw += 1

    placed = skipped = 0
    for ref, comp in sorted(sch.items()):
        template = load_footprint_template(board, comp["footprint"], cache)
        if template is None:
            print(f"    SKIP {ref}: no template for {comp['footprint']}")
            skipped += 1
            continue
        add_footprint(
            board,
            template,
            ref,
            comp["value"],
            comp["x"],
            comp["y"],
            comp["rot"],
            sheet,
            sch_file,
        )
        placed += 1

    pcbnew.SaveBoard(str(pcb_path), board)
    print(
        f"  {cfg['name']}: sch={len(sch)} placed={placed} "
        f"skipped={skipped} graphics={n_draw}"
    )


def main() -> int:
    os.chdir(str(AUDIO_DIR))
    if not TEMPLATE.exists():
        raise FileNotFoundError(f"Missing template: {TEMPLATE}")
    cache = build_cache_from_boards()
    print(f"Footprint template cache: {len(cache)} types")
    for cfg in MODULES:
        sync_module(cfg, cache)
    print("Done. Run merge_audio_pcbs.py next.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
