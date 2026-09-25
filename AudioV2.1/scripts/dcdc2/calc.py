#!/usr/bin/env python3
"""v2.1 2 段制御での ±15 V DC-DC 要求の再計算（読み取り専用・リポジトリ外）。
値の出典は out/v21/dcdc_2stage.md の §1 表。ここでは算術だけ。"""
import itertools

# 親の固定側（RB-pd から今の U311/U312 の TMUX 2 個を抜いた値）[bulk_parent_sim L268]
P = {"+": (70.23, 89.84), "-": (35.22, 41.84)}
INA = {"min": 8.0, "typ": 10.5, "max": 12.0, "max_T": 14.0}          # tap:L106
TMUX_ON = {"+": (0.435, 0.48), "-": (0.34, 0.38)}                    # sw:L62,L64
TMUX_OFF = {"+": (0.035, 0.045), "-": (0.015, 0.020)}                # sw:L61,L63
SOCK = {"light": 3.6, "typ": 6.0, "ne_max": 16.0, "max": 20.0}       # opa:L310 x2, opa:L26, RB:L49
LDO = (0.4, 1.0)                                                     # MPC:L73 （各レール・1 個）
LDO_OFF = 0.003                                                      # pow:L192,L318
HP = {"none": (0, 0), "clip": (25.5, 25.5), "limit": (50.0, 42.0)}   # MPC:L86-89

CONV = {"RS6": (200, 6.0), "TMR9": (300, 9.0), "TMR10WI": (333, 10.0), "REC20K": (667, 20.0)}


def load(arch, n, corner, hp="none", board=True, tmux_board=True, direct=False):
    """arch: 'i' / 'ii'。n: 1 枚の ch 数。corner: light/typ/max。"""
    k = {"light": 0, "typ": 0, "max": 1}[corner]
    out = {}
    for r in "+-":
        v = P[r][k]
        v += {"light": INA["min"], "typ": INA["typ"], "max": INA["max"]}[corner]
        if board:
            nt = n if tmux_board else 0
            v += nt * TMUX_ON[r][k]
            s = {"light": SOCK["light"], "typ": SOCK["typ"], "max": SOCK["max"]}[corner]
            if arch == "i":
                v += n * s
                if not direct:
                    v += LDO[k]            # 1 枚に正負 1 組
            else:
                v += 1 * s + LDO[k] + (n - 1) * LDO_OFF
        v += HP[hp][0 if r == "+" else 1]
        out[r] = v
    return out


def pct(x, cap):
    return 100.0 * x / cap


rows = []
print("=== 1. 負荷（mA）と負荷率 ===")
hdr = "case          corner       +15   -15  |" + "|".join(f" {c:>7s} +/-/P " for c in CONV)
print(hdr)
cases = [("ii", 1), ("ii", 2), ("ii", 4), ("i", 1), ("i", 2), ("i", 4)]
for arch, n in cases:
    for corner, hp, tb, direct in [("light", "none", False, True), ("typ", "none", True, False),
                                   ("max", "none", True, False), ("max", "clip", True, False),
                                   ("max", "limit", True, False)]:
        L = load(arch, n, corner, hp, tmux_board=tb, direct=(direct if arch == "i" else False))
        pw = 15e-3 * (L["+"] + L["-"])
        s = f"({arch:>2s}) n={n}  {corner:5s}/{hp:5s} {L['+']:6.1f} {L['-']:6.1f} |"
        for c, (ia, w) in CONV.items():
            s += f" {pct(L['+'], ia):4.0f}/{pct(L['-'], ia):3.0f}/{pct(pw, w):3.0f} |"
        print(s + f"  P={pw:.2f} W")

print("\n--- 娘 0 枚（切替の合間・起動直後） ---")
for corner in ("light", "typ", "max"):
    L = load("ii", 1, corner, board=False)
    pw = 15e-3 * (L["+"] + L["-"])
    s = f"no board {corner:5s} {L['+']:6.1f} {L['-']:6.1f} |"
    for c, (ia, w) in CONV.items():
        s += f" {pct(L['+'], ia):4.0f}/{pct(L['-'], ia):3.0f}/{pct(pw, w):3.0f} |"
    print(s + f"  P={pw:.2f} W")

# ---- 2. レール容量 ----
print("\n=== 2. レール容量（片レール µF、公称） ===")
PAR = 57.2          # C201 47 + C202 0.1 + C503 10 + C505 0.1  [bulk L248]
DAMP = (35.0, 45.0)  # NOW:L20
CIN = (2.2, 10.0)    # pow:L160
LDO100N = 0.1        # MPCR:L127
TMUXC = 1.1          # 0.1 + 1 µF / TMUX  sw:L141


def cboard(arch, n, lo_hi, direct=False, tmux_board=True):
    i = lo_hi
    c = DAMP[i]
    nt = n if tmux_board else 0
    c += nt * TMUXC
    if arch == "ii":
        c += n * (CIN[i] + LDO100N)
    else:
        if direct:
            c += n * 0.1            # ソケットの 100 nF がレールに直に載る
        else:
            c += CIN[i] + LDO100N
    return c


for arch, n in cases:
    for direct in ((False, True) if arch == "i" else (False,)):
        lo, hi = cboard(arch, n, 0, direct), cboard(arch, n, 1, direct)
        tag = "direct" if direct else ""
        for pb in (0.0, 100.0):
            tot_lo, tot_hi = PAR + pb + lo, PAR + pb + hi
            up = (PAR - 0.2 + pb) * 1.2 + 0.2 + hi * 1.1  # 電解 +20 %、それ以外 +10 %（粗い）
            print(f"({arch}) n={n} {tag:6s} board {lo:5.1f}-{hi:5.1f}  parent+{pb:3.0f}: "
                  f"{tot_lo:6.1f}-{tot_hi:6.1f} (上振れ~{up:6.1f})  "
                  + " ".join(f"{c}:{100*up/cap:4.0f}%" for c, cap in
                             (("RS6", 660), ("TMR9", 200), ("TMR10", 220), ("REC20K", 3000))))

print("\n4 枚が同時に載る故障（片レール、上振れ）:")
for arch, n in cases:
    hi = cboard(arch, n, 1)
    for pb in (0.0, 100.0):
        up = (PAR - 0.2 + pb) * 1.2 + 0.2 + 4 * hi * 1.1
        up2 = (PAR - 0.2 + pb) * 1.2 + 0.2 + 2 * hi * 1.1
        print(f"({arch}) n={n} parent+{pb:3.0f}: 2 枚 {up2:6.1f}  4 枚 {up:6.1f} µF")

# ---- 3. 1 段目のステップ（ソフトスタート） ----
print("\n=== 3. 1 段目: 娘 1 枚の投入（ランプ終端のピーク、max 角、HP 無音） ===")
for arch, n in cases:
    for direct in ((False, True) if arch == "i" else (False,)):
        hi = cboard(arch, n, 1, direct) * 1.1
        base = load(arch, n, "max", board=False)
        # 娘の定常負荷（ランプ終端）: (ii) は TMUX＋停止中 LDO だけ。(i) は全 ch。
        if arch == "ii":
            bl = {r: n * TMUX_ON[r][1] + n * LDO_OFF for r in "+-"}
        else:
            full = load(arch, n, "max", direct=direct)
            bl = {r: full[r] - base[r] for r in "+-"}
        for tss in (1.0, 5.0, 10.0, 20.0, 50.0):
            inr = hi * 15.0 / tss  # µF*V/ms = mA
            pk = base["+"] + inr + bl["+"]
            print(f"({arch}) n={n} {'direct' if direct else '':6s} tss={tss:4.0f} ms  Cb={hi:5.1f}µF "
                  f"inrush={inr:6.1f} mA  board={bl['+']:5.1f}  step={inr+bl['+']:6.1f} mA  "
                  f"peak+15={pk:6.1f} mA  "
                  + " ".join(f"{c}:{pct(inr+bl['+'], ia):3.0f}%/{pct(pk, ia):3.0f}%" for c, (ia, w) in CONV.items()))

print("\n=== 3b. 2 段目: ch の切替（(ii) のみ電源のステップ） ===")
for corner, s in (("typ", SOCK["typ"]), ("max", SOCK["max"])):
    k = 0 if corner == "typ" else 1
    step = s + LDO[k] + 8.6   # 8.6 mA は COUT 10 µF・12 V・14 ms の充電 [MPCR:L89]
    print(f"(ii) {corner}: 1 ch ON のステップ 最大 {step:5.1f} mA  "
          + " ".join(f"{c}:{pct(step, ia):4.1f}%" for c, (ia, w) in CONV.items()))

# ---- 5. 故障 ----
print("\n=== 5. 故障（max 角、HP 歪み始め／無音） ===")


def multi(arch, n, boards_on, ch_on_total, hp):
    """boards_on 枚の娘が電源 ON、ON の ch が合計 ch_on_total。max 角。"""
    out = {}
    for r in "+-":
        v = P[r][1] + INA["max"] + HP[hp][0 if r == "+" else 1]
        v += boards_on * n * TMUX_ON[r][1]
        v += ch_on_total * SOCK["max"]
        if arch == "ii":
            v += ch_on_total * LDO[1] + (boards_on * n - ch_on_total) * LDO_OFF
        else:
            v += boards_on * LDO[1]
        out[r] = v
    return out


faults = []
for n in (1, 2, 4):
    # (i)
    faults += [("i", n, "設計点（1 枚・全 ch）", 1, n),
               ("i", n, "板スイッチ 1 個が短絡（2 枚）", 2, 2 * n),
               ("i", n, "1 段目デコーダ全出力 ON（4 枚）", 4, 4 * n)]
    # (ii)
    faults += [("ii", n, "設計点（1 枚・1 ch）", 1, 1),
               ("ii", n, "ch デコーダ無し＋ファームの誤り（1 枚の全 ch）", 1, n),
               ("ii", n, "板スイッチ 1 個が短絡（2 枚 ON、ch は 1）", 2, 1),
               ("ii", n, "板スイッチ短絡＋ファームの誤り（2 枚×1 ch）", 2, 2),
               ("ii", n, "1 段目デコーダ全出力 ON＋ch デコーダ有り（4 枚×1 ch、二重故障）", 4, 4)]
for arch, n, name, b, c in faults:
    for hp in ("none", "clip"):
        L = multi(arch, n, b, c, hp)
        pw = 15e-3 * (L["+"] + L["-"])
        print(f"({arch:>2s}) n={n} {name:40s} {hp:5s} +{L['+']:6.1f} -{L['-']:6.1f} P={pw:5.2f}W | "
              + " ".join(f"{cn}:{pct(L['+'], ia):4.0f}%/{pct(pw, w):3.0f}%" for cn, (ia, w) in CONV.items()))
