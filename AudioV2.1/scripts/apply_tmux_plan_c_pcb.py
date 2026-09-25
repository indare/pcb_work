#!/usr/bin/env python3
"""案C: PCB 上の TMUX を 270° にし、TMUX_MAP どおりにパッドネットを張り直す。

回路図は build_daughter 済み前提。旧モデルBの近傍配線は消す（引き出しから再開）。
`--skip-decap` でデカップの再配置を飛ばす（電源を先に詰めている途中など、
盤面の他の部品を動かしたくないとき）。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pcbnew

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_daughter import TMUX_MAP  # noqa: E402

PCB = ROOT / "AudioV2Case.kicad_pcb"

# U311=ch1/2, U312=ch3/4
TMUX_CHS = {"U311": (1, 2), "U312": (3, 4)}

# デカップ（裏面）: 各 TMUX の ±15V 近傍
DECAP = {
    "U311": {"C311": "+15V", "C312": "-15V"},
    "U312": {"C313": "+15V", "C314": "-15V"},
}


def mm(x: float, y: float):
    return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))


def to_mm(v):
    return pcbnew.ToMM(v.x), pcbnew.ToMM(v.y)


def pcb_net_name(tmpl: str, a: int, b: int) -> str:
    name = tmpl.format(a=a, b=b)
    if name in ("+15V", "-15V", "A_GND") or name.startswith("AMP_SEL"):
        return "/" + name
    return f"/AmpBankSwitch/{name}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-decap", action="store_true",
                    help="デカップ（C311..C314）を動かさない")
    args = ap.parse_args()

    board = pcbnew.LoadBoard(str(PCB))
    fps = {f.GetReference(): f for f in board.GetFootprints()}

    rewrite_nets: set[str] = set()
    for a, b in TMUX_CHS.values():
        for tmpl in TMUX_MAP.values():
            rewrite_nets.add(pcb_net_name(tmpl, a, b))

    # 1) ネット張り直し + 270°（ピン1–8が北＝CH{a}）
    for ref, (a, b) in TMUX_CHS.items():
        fp = fps[ref]
        fp.SetOrientationDegrees(270)
        for pad in fp.Pads():
            num = pad.GetNumber()
            if num not in TMUX_MAP:
                continue
            nname = pcb_net_name(TMUX_MAP[num], a, b)
            net = board.FindNet(nname)
            if net is None:
                raise SystemExit(f"net not found: {nname} ({ref}.pad{num})")
            pad.SetNet(net)
        print(f"{ref}: rot=270 nets updated (ch{a}/{b})")

    # 2) デカップを電源ピン直下（裏面）へ
    for ref, caps in ({} if args.skip_decap else DECAP).items():
        u = fps[ref]
        ux, uy = to_mm(u.GetPosition())
        # 270°: VSS=4 北辺、VDD=13 南辺
        p13 = next(p for p in u.Pads() if p.GetNumber() == "13")
        p4 = next(p for p in u.Pads() if p.GetNumber() == "4")
        for cref, which in caps.items():
            if cref not in fps:
                print(f"  skip missing {cref}")
                continue
            c = fps[cref]
            if not c.IsFlipped():
                c.Flip(c.GetPosition(), True)
            if which == "+15V":
                x, y = to_mm(p13.GetPosition())
                c.SetOrientationDegrees(0)
                c.SetPosition(mm(x, y))
            else:
                x, y = to_mm(p4.GetPosition())
                c.SetOrientationDegrees(0)
                c.SetPosition(mm(x, y))
            print(f"  {cref}: under {which} @ ({x:.2f},{y:.2f}) B")

    # 3) TMUX 近傍の旧配線を削除（対象ネットのみ）
    centers = [to_mm(fps[r].GetPosition()) for r in TMUX_CHS]
    doomed = []
    for t in board.GetTracks():
        if t.GetNetname() not in rewrite_nets:
            continue
        for end in (t.GetStart(), t.GetEnd()):
            ex, ey = to_mm(end)
            if any(abs(ex - cx) < 20 and abs(ey - cy) < 20 for cx, cy in centers):
                doomed.append(t)
                break
    for t in doomed:
        board.Remove(t)
    print(f"removed {len(doomed)} nearby tracks on TMUX nets")

    board.Save(str(PCB))
    print(f"saved {PCB}")

    # 確認: 北辺 L/R
    u = fps["U311"]
    cx, cy = to_mm(u.GetPosition())
    print("U311 pad check:")
    for num in ("6", "3", "7", "2", "14", "11", "15", "10"):
        p = next(p for p in u.Pads() if p.GetNumber() == num)
        x, y = to_mm(p.GetPosition())
        print(f"  pin{num} ({x:.3f},{y:.3f}) {'N' if y < cy else 'S'}{'W' if x < cx else 'E'} {p.GetNetname()}")


if __name__ == "__main__":
    main()
