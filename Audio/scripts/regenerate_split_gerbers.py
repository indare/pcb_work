#!/usr/bin/env python3
"""Regenerate split AudioCase boards and fabrication outputs.

The source AudioCase board intentionally keeps four board outlines in one
layout.  KiKit can separate them, but the standard RK097 potentiometer
footprints contain open Edge.Cuts guide lines that make KiKit reject the
outline.  This script creates a temporary copy where those footprint guide
lines are moved to Dwgs.User, then regenerates:

  - Audio/split/AudioCase_*.kicad_pcb
  - Audio/split/Gerber/<board>/*
  - Audio/split/Gerber/<board>.zip
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


AUDIO_DIR = Path(__file__).resolve().parent.parent
SOURCE_PCB = AUDIO_DIR / "AudioCase.kicad_pcb"
SPLIT_DIR = AUDIO_DIR / "split"
TEMP_PCB = SPLIT_DIR / "AudioCase_for_separate.kicad_pcb"
GERBER_DIR = SPLIT_DIR / "Gerber"

LAYERS = ",".join(
    [
        "F.Cu",
        "B.Cu",
        "F.Paste",
        "B.Paste",
        "F.SilkS",
        "B.SilkS",
        "F.Mask",
        "B.Mask",
        "Edge.Cuts",
    ]
)

BOARDS = [
    {
        "name": "01_main",
        "pcb": "AudioCase_1_main.kicad_pcb",
        "source": "rectangle; tlx: 18.75mm; tly: 18.425mm; brx: 182.7mm; bry: 117.625mm",
    },
    {
        "name": "02_rv_panel",
        "pcb": "AudioCase_2_rv_panel.kicad_pcb",
        # Must match the RV panel gr_rect on Edge.Cuts (KiKit fails with GeometryCollection otherwise).
        "source": "rectangle; tlx: 38.05mm; tly: 125.4mm; brx: 121.45mm; bry: 178.304748mm",
    },
    {
        "name": "03_power",
        "pcb": "AudioCase_3_power.kicad_pcb",
        "source": "rectangle; tlx: 215.23mm; tly: 18.49mm; brx: 271.5mm; bry: 63.5mm",
    },
    {
        "name": "04_amp",
        "pcb": "AudioCase_4_amp.kicad_pcb",
        "source": "rectangle; tlx: 215.42mm; tly: 73.326743mm; brx: 278mm; bry: 115.826743mm",
    },
]

FP_LIB_TABLE = """(fp_lib_table
\t(version 7)
\t(lib (name "Library") (type "KiCad") (uri "${KIPRJMOD}/../Library.pretty") (options "") (descr ""))
\t(lib (name "ULN2803A_HTC_DIP_ONLY") (type "KiCad") (uri "${KIPRJMOD}/../Library.pretty") (options "") (descr ""))
\t(lib (name "BP5293_ROHM") (type "KiCad") (uri "${KIPRJMOD}/../Library.pretty") (options "") (descr ""))
)
"""


def run(cmd: list[str]) -> None:
    print("+ " + " ".join(quote_arg(c) for c in cmd))
    subprocess.run(cmd, check=True)


def quote_arg(arg: str) -> str:
    return f'"{arg}"' if " " in arg else arg


def find_tool(name: str, candidates: list[Path]) -> str:
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    found = shutil.which(name)
    if found:
        return found
    raise SystemExit(f"Could not find {name}. Install it or add it to PATH.")


def matching_paren(text: str, start: int) -> int:
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i + 1
    raise ValueError("unbalanced KiCad s-expression")


def footprint_blocks(text: str) -> list[tuple[int, int, str]]:
    blocks: list[tuple[int, int, str]] = []
    pos = 0
    marker = "\n\t(footprint "
    while True:
        start = text.find(marker, pos)
        if start == -1:
            break
        start += 1
        end = matching_paren(text, start)
        blocks.append((start, end, text[start:end]))
        pos = end
    return blocks


def prepare_temp_board() -> None:
    SPLIT_DIR.mkdir(parents=True, exist_ok=True)
    text = SOURCE_PCB.read_text(encoding="utf-8")
    replacements: list[tuple[int, int, str]] = []

    for start, end, block in footprint_blocks(text):
        if 'Potentiometer_THT:Potentiometer_Alps_RK097_Dual_Horizontal' not in block:
            continue
        if not any(f'property "Reference" "RV{i}"' in block for i in (1, 2, 3)):
            continue
        updated = block.replace('(layer "Edge.Cuts")', '(layer "Dwgs.User")')
        if updated != block:
            replacements.append((start, end, updated))

    if len(replacements) != 3:
        raise SystemExit(f"Expected to update 3 RV footprints, updated {len(replacements)}.")

    for start, end, updated in reversed(replacements):
        text = text[:start] + updated + text[end:]

    TEMP_PCB.write_text(text, encoding="utf-8")
    (SPLIT_DIR / "fp-lib-table").write_text(FP_LIB_TABLE, encoding="utf-8")
    print(f"Wrote {TEMP_PCB} with RV Edge.Cuts guide lines moved to Dwgs.User")


def clean_output_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def zip_directory(folder: Path) -> Path:
    zip_path = folder.with_suffix(".zip")
    if zip_path.exists():
        zip_path.unlink()
    with ZipFile(zip_path, "w", ZIP_DEFLATED) as archive:
        for item in sorted(folder.iterdir()):
            if item.is_file():
                archive.write(item, arcname=item.name)
    return zip_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-gerbers", action="store_true", help="only regenerate split KiCad PCB files")
    args = parser.parse_args()

    kikit = find_tool(
        "kikit",
        [
            Path("/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/kikit"),
            Path.home() / "Documents/KiCad/10.0/3rdparty/Python311/Scripts/kikit.exe",
        ],
    )
    kicad_cli = find_tool(
        "kicad-cli",
        [
            Path("C:/Program Files/KiCad/10.0/bin/kicad-cli.exe"),
            Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"),
        ],
    )

    prepare_temp_board()

    for board in BOARDS:
        out_pcb = SPLIT_DIR / board["pcb"]
        run([kikit, "separate", "--source", board["source"], str(TEMP_PCB), str(out_pcb)])

    if args.skip_gerbers:
        return 0

    GERBER_DIR.mkdir(parents=True, exist_ok=True)
    for board in BOARDS:
        pcb = SPLIT_DIR / board["pcb"]
        out_dir = GERBER_DIR / board["name"]
        clean_output_dir(out_dir)
        zip_path = out_dir.with_suffix(".zip")
        if zip_path.exists():
            zip_path.unlink()

        run(
            [
                kicad_cli,
                "pcb",
                "export",
                "gerbers",
                "--output",
                str(out_dir),
                "--layers",
                LAYERS,
                "--subtract-soldermask",
                "--precision",
                "6",
                "--check-zones",
                str(pcb),
            ]
        )
        run(
            [
                kicad_cli,
                "pcb",
                "export",
                "drill",
                "--output",
                str(out_dir),
                "--format",
                "excellon",
                "--excellon-units",
                "mm",
                "--excellon-zeros-format",
                "decimal",
                "--excellon-oval-format",
                "alternate",
                "--generate-map",
                "--map-format",
                "gerberx2",
                "--generate-report",
                "--report-path",
                str(out_dir / "drill_report.rpt"),
                str(pcb),
            ]
        )
        created = zip_directory(out_dir)
        print(f"Wrote {created}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
