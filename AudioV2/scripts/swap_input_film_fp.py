#!/usr/bin/env python3
"""入力カップリング 1µF film の PCB フットプリントを P5/W4.5 へ差し替える。

対象: Value が「1uF film」かつ旧 P10 MKT の部品。位置・回転・ネットは維持。
本命部品: TDK B32529C0105J000（7.3×4.5、P5.00）。
"""
from __future__ import annotations

from pathlib import Path

import pcbnew

PCB = Path(__file__).resolve().parents[1] / "AudioV2Case.kicad_pcb"
KICAD_FP_DIR = Path(r"C:\Program Files\KiCad\10.0\share\kicad\footprints")
OLD_FP = "Capacitor_THT:C_Rect_L11.0mm_W4.2mm_P10.00mm_MKT"
NEW_FP = "Capacitor_THT:C_Rect_L7.2mm_W4.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2"


def load_fp(lib_id: str):
    lib, name = lib_id.split(":", 1)
    pretty = KICAD_FP_DIR / f"{lib}.pretty"
    io = pcbnew.PCB_IO_KICAD_SEXPR()
    fp = io.FootprintLoad(str(pretty), name, False)
    if fp is None:
        raise RuntimeError(f"FootprintLoad failed: {lib_id}")
    return fp


def main() -> None:
    board = pcbnew.LoadBoard(str(PCB))
    swapped = []
    for old in list(board.GetFootprints()):
        fpid = old.GetFPIDAsString()
        if old.GetValue() != "1uF film" or fpid != OLD_FP:
            continue
        new = load_fp(NEW_FP)
        new.SetReference(old.GetReference())
        new.SetValue(old.GetValue())
        new.SetPosition(old.GetPosition())
        new.SetOrientation(old.GetOrientation())
        new.SetLayer(old.GetLayer())
        if old.IsFlipped():
            new.Flip(new.GetPosition(), True)
        try:
            new.SetPath(old.GetPath())
        except Exception:
            pass
        for pad in new.Pads():
            op = old.FindPadByNumber(pad.GetNumber())
            if op is not None:
                pad.SetNet(op.GetNet())
        board.Remove(old)
        board.Add(new)
        swapped.append(old.GetReference())

    board.Save(str(PCB))
    print(f"swapped {len(swapped)}: {', '.join(sorted(swapped))}")
    print(f"  {OLD_FP}")
    print(f"→ {NEW_FP}")
    print(f"saved {PCB}")


if __name__ == "__main__":
    main()
