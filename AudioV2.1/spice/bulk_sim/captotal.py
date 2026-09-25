#!/usr/bin/env python3
"""レール容量の合計（片レール）vs RS6 の 660 µF。公称と上振れ（電解 +20 %、MLCC +10 %〔仮定〕）。"""
PARENT_E, PARENT_M = 47.0, 0.1 + 10.0 + 0.1       # C201（電解）/ C202, C503, C505
def dau(cin, sw):  # 1 枚あたり（公称）: LDO CIN×4 ＋ 100nF×4 ＋ TMUX(0.1+1)×4
    return 4 * cin + 0.4 + (4 * 1.1 if sw else 0.0)
rows = []
for lab, cd, cpb in (("(1) 娘ダンパ 45 µF", 45.0, 0.0), ("(1) 娘ダンパ 35 µF", 35.0, 0.0),
                     ("(2)/(3) 親 +100 µF", 0.0, 100.0), ("(2)/(3) 親 +220 µF", 0.0, 220.0), ("(2)/(3) C201 のみ", 0.0, 0.0)):
    for cin, sw, dl in ((10.0, True, "Switch・CIN 10 µF"), (2.2, False, "Relay・CIN 2.2 µF")):
        vals = []
        for n in (1, 2, 3, 4):
            nom = PARENT_E + PARENT_M + cpb + n * (dau(cin, sw) + cd)
            up = 1.2 * (PARENT_E + cpb) + 1.1 * PARENT_M + n * 1.1 * (dau(cin, sw) + cd)  # ダンパは MLCC と見なす
            vals.append(f"{nom:.0f} / {up:.0f}（{up/660*100:.0f} %）")
        print(f"| {lab} | {dl} | " + " | ".join(vals) + " |")
