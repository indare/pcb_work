#!/usr/bin/env python3
"""±15 V の負荷の積み上げ（回路図の部品 × データシートの電流）。読み取り専用。

v2.1 は「選んだ ch だけ電源と入力を生かす」構成を採る（2026-09-25）。ソケット常時通電の前提が消えるので、
DC-DC の要求（電流・軽負荷・正負の非対称）を積み直すための道具。

- **部品と、どのレールに載っているか**は回路図から数える（`sch_facts.Design`）。ここに数を書かない
- **1 個あたりの電流**だけを下の表に持つ。各行に出典（DS のファイルと節）を書く
- 下位レール（`VCC_TONE` / `+3V3_A` / `+5V_A`）は、その負荷の合計＋レギュレータの自己消費を
  入力側のレールへ積む（リニアなので入力電流 ≈ 出力電流）
- ソケットはシナリオで数を変える（全 ch 通電 / 2 ch / 1 ch）。1 個あたりは NE5532 と在庫の最悪で2通り

    python3 AudioV2.1/scripts/rail_budget.py
    python3 AudioV2.1/scripts/rail_budget.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sch_facts  # noqa: E402

ROOT = Path(__file__).resolve().parents[1] / "AudioV2Case.kicad_sch"
TOP = ("+15V", "-15V")

# 1 個あたりの電流 [mA]（typ, max）。キーは (lib_id, value) の value を優先して照合。
# 出典の「DECISIONS」は AudioV2.1/DECISIONS.md（DS を引いて記録済みの行）
PER_PART = {
    # value / lib の一部 : {レール役割: (typ, max)} と出典
    "OPA1656": ({"+": (7.8, 9.2), "-": (7.8, 9.2)},
                "Audio/datasheets/opamps/TI_OPA1656.pdf 電気的特性 IQ 3.9/4.6 mA per ch × 2"),
    "OPA1652": ({"+": (4.0, 5.0), "-": (4.0, 5.0)},
                "Audio/datasheets/opamps/TI_OPA1652.pdf 電気的特性 IQ 2/2.5 mA per ch × 2"),
    "TMUX7612": ({"+": (0.435, 0.48), "-": (0.34, 0.38)},
                 "AudioV2.1/datasheets/TI_TMUX7612.pdf p7 IDD/ISS all switches ON, ±16.5 V"),
    "PT2314E": ({"+": (30.0, 40.0)},
                "AudioV2.1/datasheets/Princeton_PT2314E.pdf 電気的特性 Is @VDD=9V"),
    "TPS3307": ({"+": (0.015, 0.03)}, "監視 IC。µA 級（DS 未照合・影響なし）"),
}
# PCM1804 モジュール（A1601）と発振器（Y1601）は +5V_A / +3V3_A の合計で持つ（内訳の typ が DS から取れない）
ADC_TOTAL = ((59.0, 84.0), "DECISIONS「電流はデータシートから積み上がった」: PCM1804 VCC max 45 + VDD max 20 "
             "＋ 発振器 max 15 ＝ ≤84 mA（typ ≈59）")
# ソケット（AmpChannel のデュアルオペアンプ）1 個あたり
SOCKET = {"NE5532": ((6.0, 16.0), "Audio/datasheets/opamps/TI_NE5532.pdf ICC total VO=0 無負荷 6/16 mA"),
          "在庫の最悪": ((20.0, 20.0), "DECISIONS「在庫石の最悪 Icc を実読」MUSES03 変換基板 10 mA max × 2")}
# 下位レール: レール名 → (レギュレータの参照, 自己消費 (typ, max) [mA], 出典)
SUBRAIL = {
    "VCC_TONE": ("U202", (5.0, 8.0), "L7809 の Iq。**一次 DS 未入手（web 由来）** — DECISIONS も同じ注記"),
    "+3V3_A": ("U1603", (0.8, 1.3), "AudioV2.1/datasheets/ADI_LT1763.pdf GND Pin Current（35 mA 付近の内挿）"),
    "+5V_A": ("U1606", (1.1, 1.6), "AudioV2.1/datasheets/ADI_LT1763.pdf GND Pin Current @50 mA"),
}
CONVERTERS = {"REC20K-2415DZ（現行）": 667, "REC10K-2415DAW/H2（旧）": 333}


def classify(value: str, lib: str) -> str | None:
    for key in PER_PART:
        if key in value or key in lib:
            return key
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--adc-from-pd", action="store_true",
                    help="計測系の LDO（+3V3_A / +5V_A）を ±15 V ではなく PD 12 V から取る案（v2.1 の C）")
    a = ap.parse_args()
    d = sch_facts.Design(a.root)
    by_net = {n.name: n for n in d.nets}

    # 部品ごとに、どのレールのピンを持つか
    parts: dict[str, dict] = defaultdict(lambda: {"rails": set(), "lib": "", "value": ""})
    for rail in list(TOP) + list(SUBRAIL):
        n = by_net.get(rail)
        if n is None:
            print(f"⚠ ネット {rail} が回路図に無い")
            continue
        for ref, _pin, lib, val in n.detail:
            parts[ref]["rails"].add(rail)
            parts[ref]["lib"], parts[ref]["value"] = lib, val

    fixed = {r: [0.0, 0.0] for r in list(TOP) + list(SUBRAIL)}
    lines = []
    sockets = [r for r, p in parts.items() if "DIP-8 compatible" in p["value"]]
    unknown = []
    for ref, p in sorted(parts.items()):
        if ref in sockets or ref.startswith(("C", "R", "J", "F", "NT", "D", "L", "TP")):
            continue
        if ref in {v[0] for v in SUBRAIL.values()}:
            continue   # レギュレータは下位レールの合計で積む
        if ref in ("A1601", "Y1601"):
            continue   # ADC_TOTAL でまとめて持つ
        if "REC20K" in p["value"] or "REC10K" in p["value"]:
            continue   # 供給元（DC-DC）
        key = classify(p["value"], p["lib"])
        if key is None:
            unknown.append(f"{ref} {p['value']} {sorted(p['rails'])}")
            continue
        cur, src = PER_PART[key]
        rails = sorted(p["rails"])
        pos = next((r for r in rails if r in ("+15V", "VCC_TONE", "+3V3_A", "+5V_A")), None)
        neg = "-15V" if "-15V" in rails else None
        for role, rail in (("+", pos), ("-", neg)):
            if rail and role in cur:
                fixed[rail][0] += cur[role][0]
                fixed[rail][1] += cur[role][1]
        lines.append((ref, key, rails, src))
    # ADC モジュール＋発振器は +5V_A / +3V3_A の合計（どちらも LT1763 経由で +15V から）
    adc_typ, adc_max = ADC_TOTAL[0]
    # 下位レールを入力側へ
    for rail, (reg, (iq_t, iq_m), _src) in SUBRAIL.items():
        load_t, load_m = fixed[rail]
        if rail in ("+3V3_A", "+5V_A"):
            continue
        fixed["+15V"][0] += load_t + iq_t
        fixed["+15V"][1] += load_m + iq_m
    ldo_iq = [sum(SUBRAIL[r][1][i] for r in ("+3V3_A", "+5V_A")) for i in (0, 1)]
    other_a = [fixed["+3V3_A"][i] + fixed["+5V_A"][i] for i in (0, 1)]
    if a.adc_from_pd:
        print(f"※ --adc-from-pd: 計測系の LDO の入力（typ {adc_typ + ldo_iq[0] + other_a[0]:.1f} / max {adc_max + ldo_iq[1] + other_a[1]:.1f} mA）は PD 12 V 側へ（±15 V に積まない）")
    else:
        fixed["+15V"][0] += adc_typ + ldo_iq[0] + other_a[0]
        fixed["+15V"][1] += adc_max + ldo_iq[1] + other_a[1]

    out = {"fixed_mA": {r: fixed[r] for r in TOP}, "sockets_in_schematic": len(sockets), "scenarios": []}
    print(f"回路図: ソケット {len(sockets)} 個（{', '.join(sorted(sockets))}）")
    print("固定側（ソケット以外、typ / max mA）:")
    for r in TOP:
        print(f"  {r:5s} {fixed[r][0]:7.1f} / {fixed[r][1]:7.1f}")
    if unknown:
        print("⚠ 電流の表に無い部品（積んでいない）:", "; ".join(unknown))
    print()
    print(f"{'シナリオ':24s} {'ソケット 1 個':10s} {'+15V typ/max':>16s} {'-15V typ/max':>16s}   "
          + "   ".join(f"{k} 負荷率 +/−（max）" for k in CONVERTERS))
    for n_on in (len(sockets), 2, 1):
        for sname, ((st, sm), _src) in SOCKET.items():
            p = (fixed["+15V"][0] + n_on * st, fixed["+15V"][1] + n_on * sm)
            m = (fixed["-15V"][0] + n_on * st, fixed["-15V"][1] + n_on * sm)
            fr = "   ".join(f"{p[1] / cap * 100:5.1f}% / {m[1] / cap * 100:5.1f}%" + " " * 14
                           for cap in CONVERTERS.values())
            label = f"{n_on} ch 通電" + ("（全 ch）" if n_on == len(sockets) else "")
            print(f"{label:24s} {sname:10s} {p[0]:7.1f} / {p[1]:6.1f} {m[0]:7.1f} / {m[1]:6.1f}   {fr}")
            out["scenarios"].append({"n_on": n_on, "socket": sname, "+15V": p, "-15V": m})
    print()
    print("出典:")
    for key, (_c, src) in PER_PART.items():
        print(f"  {key}: {src}")
    print(f"  ADC1804_F＋発振器: {ADC_TOTAL[1]}")
    for k, (_c, src) in SOCKET.items():
        print(f"  ソケット {k}: {src}")
    for r, (reg, _c, src) in SUBRAIL.items():
        print(f"  {r}（{reg}）の自己消費: {src}")
    print("※ 帰還網・負荷の信号電流は含めない（20 k 網で 0.2 mA 級）。リレーのコイルは +5V_COIL（±15 V ではない）")
    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
