#!/usr/bin/env python3
"""案1: 娘/親スロットコネクタを A2 どおりの上下関係に直す。

カードローカル（110×110、原点=外形 NW、Y 下向き）:
  J_ANA  pin1 = (20.00, 10.00)   北辺・AMP_SEL
  J_PWR  pin1 = (60.00, 97.46)   南辺・電源/CTRL

娘の外形は取付穴 H303(NW)/H304(NE)/H301(SW)/H302(SE) から決める
（穴は端から 5.0 mm → 原点 = NW穴 − (5,5)）。

親スロットは同じ ΔY（97.46−10.00 = 87.46）で ANA を北・PWR を南。
3 枚横並びは別件（仮置きのまま X だけ間隔を空ける）。

向きは母板ソケットに合わせ rot=0（ピン列が +Y）。
配線は触らない（AMP_SEL 本線は place_tmux_ch12_plan_c_fanout.py）。
"""
from __future__ import annotations

from pathlib import Path

import pcbnew

PCB = Path(__file__).resolve().parents[1] / "AudioV2Case.kicad_pcb"

# A2 カードローカル
ANA_LOCAL = (20.00, 10.00)
PWR_LOCAL = (60.00, 97.46)
A2_DY = PWR_LOCAL[1] - ANA_LOCAL[1]  # 87.46

# 親スロット仮置き（ANA 北 / PWR 南、ΔY = A2）。X は 110 幅を意識して離す。
MOTHER_SLOTS = {
    1: (50.00, 40.00),
    2: (170.00, 40.00),
    3: (290.00, 40.00),
}


def mm(x, y):
    return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))


def to_mm(v):
    return pcbnew.ToMM(v.x), pcbnew.ToMM(v.y)


def place(fp, x, y, rot=0.0):
    if fp.IsFlipped():
        fp.Flip(fp.GetPosition(), True)
    fp.SetOrientationDegrees(rot)
    fp.SetPosition(mm(x, y))


def main() -> None:
    board = pcbnew.LoadBoard(str(PCB))
    fps = {f.GetReference(): f for f in board.GetFootprints()}

    # --- 娘カード原点（取付穴） ---
    nw = fps["H303"]  # 局所 (5,5)
    ox, oy = to_mm(nw.GetPosition())
    ox -= 5.0
    oy -= 5.0
    print(f"daughter origin ({ox:.2f},{oy:.2f})  size 110×110")

    ana_x, ana_y = ox + ANA_LOCAL[0], oy + ANA_LOCAL[1]
    pwr_x, pwr_y = ox + PWR_LOCAL[0], oy + PWR_LOCAL[1]

    place(fps["J_ANA301"], ana_x, ana_y, 0)
    place(fps["J_PWR301"], pwr_x, pwr_y, 0)
    print(f"J_ANA301 → ({ana_x:.2f},{ana_y:.2f}) rot=0  (north / AMP_SEL)")
    print(f"J_PWR301 → ({pwr_x:.2f},{pwr_y:.2f}) rot=0  (south / PWR)")

    # MCP は J_PWR（デジタル）側へ — タイル（案C）は触らない
    if "U_IO301" in fps:
        # pin1 を PWR の西・やや北（コネクタ本体の外）
        place(fps["U_IO301"], pwr_x - 18.0, pwr_y - 8.0, -90)
        ux, uy = to_mm(fps["U_IO301"].GetPosition())
        print(f"U_IO301 → ({ux:.2f},{uy:.2f}) near J_PWR")

    # --- 親スロット ---
    for slot, (ax, ay) in MOTHER_SLOTS.items():
        ana_ref = f"J_ANA10{slot}"
        pwr_ref = f"J_PWR10{slot}"
        if ana_ref not in fps or pwr_ref not in fps:
            print(f"skip slot {slot}: missing refs")
            continue
        place(fps[ana_ref], ax, ay, 0)
        place(fps[pwr_ref], ax, ay + A2_DY, 0)
        print(f"{ana_ref}/{pwr_ref} → ANA({ax:.2f},{ay:.2f}) PWR({ax:.2f},{ay + A2_DY:.2f})")

    board.Save(str(PCB))
    print(f"saved {PCB}")


if __name__ == "__main__":
    main()
