#!/usr/bin/env python3
"""課題 B: 娘 4 枚・娘ごとに 1 ch まで ON（デコーダ）のときの ±15 V 負荷。数値の出典は md の表と同じ。"""
from __future__ import annotations

# rail_budget.py --adc-from-pd の固定側（typ, max）[mA]。ここから今の回路図の U311/U312（TMUX×2）を抜いて、娘ごとに積み直す
FIX = {"+": (71.1, 90.8), "-": (35.9, 42.6)}
TMUX1 = {"+": (0.435, 0.48), "-": (0.34, 0.38)}          # rail_budget.py L38（TMUX7612 p7、±16.5 V 全 ON）
PARENT = {r: (FIX[r][0] - 2 * TMUX1[r][0], FIX[r][1] - 2 * TMUX1[r][1]) for r in FIX}
INA = (10.5, 12.0)                                        # tap.md L106 / MPC L60
TMUX_PER_SW_DAUGHTER = 4                                  # 出力選択 2（U311/U312）＋入力切替 2（計画、decisions_audit_1 L7）
SOCK = {"NE5532 typ": 6.0, "NE5532 max": 16.0, "在庫の最悪": 20.0}   # opamps.md L26 / rail_budget.py L48-49
LDO_SELF = (0.4, 1.0)                                     # MPC L63, L73
LDO_SHDN = 0.003                                          # 3 µA max（power.md L192, L318）
HP = {"無音": (0, 0), "1 mW": (5.0, 5.0), "最大（歪み始め）": (25.5, 25.5), "上限（過大入力）": (50.0, 42.0)}  # MPC L85-89
RATED = 200.0
P_RATED = 6.0


def load(n_on, sock, hp, mx, n_sw=4, n_daughters=4):
    i = 1 if mx else 0
    out = {}
    for r in ("+", "-"):
        v = PARENT[r][i] + INA[i]
        v += n_sw * TMUX_PER_SW_DAUGHTER * TMUX1[r][i]
        v += (n_daughters * 4 - n_on) * LDO_SHDN
        v += n_on * (SOCK[sock] + LDO_SELF[i])
        v += HP[hp][0 if r == "+" else 1]
        out[r] = v
    return out


def row(label, n_on, sock, hp, mx, n_sw=4):
    L = load(n_on, sock, hp, mx, n_sw)
    ptot = (L["+"] + L["-"]) * 15 / 1000
    return (f"| {label} | {n_on} | {sock} | {hp} | {L['+']:.1f} | {L['-']:.1f} | "
            f"{L['+']/RATED*100:.0f} % | {L['-']/RATED*100:.0f} % | {ptot:.2f} W（{ptot/P_RATED*100:.0f} %） |")


print(f"親の固定（U311/U312 を抜いた値）: + {PARENT['+'][0]:.2f}/{PARENT['+'][1]:.2f}, − {PARENT['-'][0]:.2f}/{PARENT['-'][1]:.2f} mA")
print("| 積み方 | ON の ch 数 | ソケット | HP | +15V mA | −15V mA | +15V / 200 mA | −15V / 200 mA | 合計電力 / 6 W |")
print("|---|---:|---|---|---:|---:|---:|---:|---:|")
for n in (1, 2, 3, 4):
    print(row("typ（Switch 娘 4 枚）", n, "NE5532 typ", "無音", False))
    print(row("typ（Switch 娘 4 枚）", n, "NE5532 typ", "1 mW", False))
for n in (1, 2, 3, 4):
    print(row("max（Switch 娘 4 枚）", n, "NE5532 max", "無音", True))
    print(row("max（Switch 娘 4 枚）", n, "在庫の最悪", "無音", True))
    print(row("max（Switch 娘 4 枚）", n, "在庫の最悪", "最大（歪み始め）", True))
    print(row("max（Switch 娘 4 枚）", n, "在庫の最悪", "上限（過大入力）", True))
print("\n# 娘の構成で変わる分（Switch 2 + Relay 2）")
for n in (3, 4):
    print(row("max（Switch 2 + Relay 2）", n, "在庫の最悪", "最大（歪み始め）", True, n_sw=2))

# 100 % を超える最小の ch 数
print("\n# +15 V が 200 mA を超える最小の ON ch 数（max 積み・在庫の最悪）")
for hp in HP:
    first = next((n for n in (1, 2, 3, 4) if load(n, "在庫の最悪", hp, True)["+"] > RATED), None)
    firstt = next((n for n in (1, 2, 3, 4) if (lambda L: (L["+"] + L["-"]) * 15 / 1000 > P_RATED)(load(n, "在庫の最悪", hp, True))), None)
    print(f"  HP {hp}: 出力ごと 100 % 超 = {first} ch、合計電力 100 % 超 = {firstt} ch")
