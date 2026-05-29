#!/usr/bin/env python3
"""
Merge EQ / Amp / Power module PCBs into AudioCase.kicad_pcb using KiCad's pcbnew API.

Modules are laid out side-by-side with a gap between board outlines.  Tracks and
graphics are filtered to each module's Edge.Cuts region, then moved together with
footprints so routing stays aligned.

Run with KiCad's Python:
  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 \\
    Audio/scripts/merge_audio_pcbs.py
"""

from __future__ import annotations

import os
import shutil
import sys

import wx  # noqa: E402

wx.App(False)

import pcbnew  # noqa: E402

AUDIO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Gap between adjacent board outlines (mm)
GAP_MM = 25.0

# outline = (x_min, y_min, x_max, y_max) in mm — matches Edge.Cuts in each source PCB
MODULES = [
    {
        "file": "EQModule.kicad_pcb",
        "sch": "EQModule.kicad_sch",
        "sheet": "/EQModule/",
        "outline": (69.9, 45.925, 165.7, 99.075),
    },
    {
        "file": "AmpModule.kicad_pcb",
        "sch": "AmpModule.kicad_sch",
        "sheet": "/AmpModule/",
        "outline": (113.2, 62.5, 165.7, 104.0),
    },
    {
        "file": "PowerModule.kicad_pcb",
        "sch": "PowerModule.kicad_sch",
        "sheet": "/PowerModule/",
        "outline": (113.2, 104.0, 175.15, 141.020411),
    },
]


def outline_bbox(cfg: dict) -> pcbnew.BOX2I:
    x0, y0, x1, y1 = cfg["outline"]
    return pcbnew.BOX2I(
        pcbnew.VECTOR2I(pcbnew.FromMM(x0), pcbnew.FromMM(y0)),
        pcbnew.VECTOR2I(pcbnew.FromMM(x1 - x0), pcbnew.FromMM(y1 - y0)),
    )


def offset_vec(dx_mm: float, dy_mm: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(pcbnew.FromMM(dx_mm), pcbnew.FromMM(dy_mm))


def assign_layout_offsets(modules: list[dict], gap_mm: float) -> None:
    """Place modules in a horizontal row, top-aligned, with gap between outlines."""
    x_cursor = 0.0
    y_top = 0.0

    for cfg in modules:
        x0, y0, x1, y1 = cfg["outline"]
        width = x1 - x0
        cfg["offset_mm"] = (x_cursor - x0, y_top - y0)
        x_cursor += width + gap_mm


def item_in_outline(item: pcbnew.BOARD_ITEM, cfg: dict) -> bool:
    bb = item.GetBoundingBox()
    ob = outline_bbox(cfg)
    return bb.Intersects(ob)


def copy_footprint(
    dst: pcbnew.BOARD,
    src_fp: pcbnew.FOOTPRINT,
    sheet: str,
    sch: str,
    move: pcbnew.VECTOR2I,
) -> None:
    fp = pcbnew.FOOTPRINT(dst)
    fp.CopyFrom(src_fp)
    fp.Move(move)
    fp.SetSheetname(sheet)
    fp.SetSheetfile(sch)
    dst.Add(fp)


def copy_track(dst: pcbnew.BOARD, src_t: pcbnew.BOARD_ITEM, move: pcbnew.VECTOR2I) -> None:
    if src_t.GetClass() == "PCB_VIA":
        t = pcbnew.PCB_VIA(dst)
    else:
        t = pcbnew.PCB_TRACK(dst)
    t.CopyFrom(src_t)
    t.Move(move)
    dst.Add(t)


def copy_drawing(dst: pcbnew.BOARD, src_d: pcbnew.BOARD_ITEM, move: pcbnew.VECTOR2I) -> None:
    makers = {
        "PCB_SHAPE": pcbnew.PCB_SHAPE,
        "PCB_TEXT": pcbnew.PCB_TEXT,
        "PCB_TEXTBOX": pcbnew.PCB_TEXTBOX,
    }
    maker = makers.get(src_d.GetClass())
    if maker is None:
        return
    d = maker(dst)
    d.CopyFrom(src_d)
    d.Move(move)
    dst.Add(d)


def import_module(dst: pcbnew.BOARD, cfg: dict) -> int:
    path = os.path.join(AUDIO_DIR, cfg["file"])
    src = pcbnew.LoadBoard(path)
    sheet = cfg["sheet"]
    dx, dy = cfg["offset_mm"]
    move = offset_vec(dx, dy)
    count = 0

    for fp in src.GetFootprints():
        if fp.GetSheetname() != sheet:
            continue
        copy_footprint(dst, fp, sheet, cfg["sch"], move)
        count += 1

    for track in src.GetTracks():
        if item_in_outline(track, cfg):
            copy_track(dst, track, move)

    for drawing in src.GetDrawings():
        if item_in_outline(drawing, cfg):
            copy_drawing(dst, drawing, move)

    return count


def main() -> int:
    os.chdir(AUDIO_DIR)
    out_path = os.path.join(AUDIO_DIR, "AudioCase.kicad_pcb")
    template_path = os.path.join(AUDIO_DIR, "AudioCase.empty.kicad_pcb")
    if not os.path.exists(template_path):
        raise FileNotFoundError(
            "Create AudioCase.empty.kicad_pcb (empty board) before running merge."
        )

    assign_layout_offsets(MODULES, GAP_MM)
    for cfg in MODULES:
        x0, y0, x1, _ = cfg["outline"]
        dx, dy = cfg["offset_mm"]
        print(
            f"  {cfg['sheet']} outline -> ({dx + x0:.1f}, {dy + y0:.1f}) mm  "
            f"[gap={GAP_MM} mm]"
        )

    shutil.copy2(template_path, out_path)
    dst = pcbnew.LoadBoard(out_path)

    total = 0
    for cfg in MODULES:
        n = import_module(dst, cfg)
        print(f"  {cfg['file']}: {n} footprints")
        total += n

    pcbnew.SaveBoard(out_path, dst)
    print(f"Saved {out_path} ({total} footprints total)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
