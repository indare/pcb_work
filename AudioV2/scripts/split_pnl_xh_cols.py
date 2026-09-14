#!/usr/bin/env python3
"""母板↔FrontPanel の 2列ヘッダを、列ごとの XH 2本に割る。

Odd_Even の奇数列 → *A、偶数列 → *B。
  デジ 2×10 → XH10 + XH10
  アナ 2×8  → XH8  + XH8（空きピンは NC）

回路図のみ。PCB は別途同期。
"""
from __future__ import annotations

import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import sch_edit  # noqa: E402
import sch_helpers  # noqa: E402
import sch_import  # noqa: E402
from sch_helpers import embed_lib_symbols, symbol_inst_v10  # noqa: E402

PARENT = "a1000001-0001-4001-8001-000000000001"
FP_INST = "b2000020-0020-4020-8020-000000000020"
ROOT_PATH = f"/{PARENT}"
FP_PATH = f"/{PARENT}/{FP_INST}"

_NS = uuid.UUID("b2000040-0040-4040-8040-000000000040")
_seq = 0

# old Odd_Even pin → net（reparent 時点の正）
DIG_OLD = {
    "1": "3V3", "2": "+5V_D", "3": "D_GND", "4": "D_GND",
    "5": "I2C_SDA", "6": "I2C_SCL", "7": "ENC_INTA", "8": "ENC_INTB",
    "9": "LCD_CS", "10": "LCD_DC", "11": "LCD_RST", "12": "LCD_EN",
    "13": "LCD_SCK", "14": "LCD_MOSI", "15": "TP_SDA", "16": "TP_SCL",
    "17": "TP_INT", "18": "TP_RST", "19": None, "20": None,
}
ANA_OLD = {
    "1": "AMP_SEL_L", "2": "AMP_SEL_R",
    "3": "PHONE_BUF_L", "4": "PHONE_BUF_R",
    "5": "LINE_L", "6": "LINE_R",
    "7": "A_GND", "8": "A_GND",
    "9": "PD_12V", "10": "PD_12V_SW",
    "11": "PD_GND", "12": None,
    "13": None, "14": None, "15": None, "16": None,
}


def _col_nets(old: dict[str, str | None], odd: bool) -> dict[str, str | None]:
    """奇数列 or 偶数列を 1..N に詰め直す。"""
    pins = sorted((int(k) for k in old), key=int)
    selected = [p for p in pins if (p % 2 == 1) == odd]
    return {str(i + 1): old[str(p)] for i, p in enumerate(selected)}


DIG_A = _col_nets(DIG_OLD, odd=True)
DIG_B = _col_nets(DIG_OLD, odd=False)
ANA_A = _col_nets(ANA_OLD, odd=True)
ANA_B = _col_nets(ANA_OLD, odd=False)

LIB10 = "Connector_Generic:Conn_01x10"
LIB8 = "Connector_Generic:Conn_01x08"
FP10 = "Connector_JST:JST_XH_B10B-XH-A_1x10_P2.50mm_Vertical"
FP8 = "Connector_JST:JST_XH_B8B-XH-A_1x08_P2.50mm_Vertical"

# (sheet_path, old_ref, [(new_ref, value, lib, fp, nets, dx)])
JOBS: list[tuple[Path, str, list[tuple]]] = [
    (
        ROOT / "AudioV2Case.kicad_sch",
        ROOT_PATH,
        [
            ("J_PNL1601", [
                ("J_PNL1601_1", "FrontPanel digital A (odd)", LIB10, FP10, DIG_A, -12.7),
                ("J_PNL1601_2", "FrontPanel digital B (even)", LIB10, FP10, DIG_B, 12.7),
            ]),
            ("J_PNL_A1601", [
                ("J_PNL_A1601_1", "FrontPanel analog A (odd)", LIB8, FP8, ANA_A, -10.16),
                ("J_PNL_A1601_2", "FrontPanel analog B (even)", LIB8, FP8, ANA_B, 10.16),
            ]),
        ],
    ),
    (
        ROOT / "FrontPanel.kicad_sch",
        FP_PATH,
        [
            ("J_PNL1602", [
                ("J_PNL1602_1", "FrontPanel digital A (odd)", LIB10, FP10, DIG_A, -12.7),
                ("J_PNL1602_2", "FrontPanel digital B (even)", LIB10, FP10, DIG_B, 12.7),
            ]),
            ("J_PNL_A1602", [
                ("J_PNL_A1602_1", "FrontPanel analog A (odd)", LIB8, FP8, ANA_A, -10.16),
                ("J_PNL_A1602_2", "FrontPanel analog B (even)", LIB8, FP8, ANA_B, 10.16),
            ]),
        ],
    ),
]


def uid() -> str:
    global _seq
    _seq += 1
    return str(uuid.uuid5(_NS, f"xhcol/{_seq}"))


def _key(p: tuple[float, float], nd: int = 2) -> tuple[float, float]:
    return (round(p[0], nd), round(p[1], nd))


def _label(name: str, x: float, y: float, left: bool = False) -> str:
    rot, just = (180, "right") if left else (0, "left")
    return (
        f'\t(label "{name}"\n\t\t(at {x} {y} {rot})\n\t\t(effects\n\t\t\t(font\n'
        f'\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify {just} bottom)\n\t\t)\n'
        f'\t\t(uuid "{uid()}")\n\t)\n'
    )


def _nc(x: float, y: float) -> str:
    return f'\t(no_connect\n\t\t(at {x} {y})\n\t\t(uuid "{uid()}")\n\t)\n'


def _ensure_libs(sheet: sch_import.Sheet, libs: list[str]) -> None:
    from build_motherboard import _merge_lib_symbols

    blocks = [h for h in sheet.header if h.lstrip().startswith("(lib_symbols")]
    merged = _merge_lib_symbols(blocks + [embed_lib_symbols(libs)])
    new_h, done = [], False
    for h in sheet.header:
        if h.lstrip().startswith("(lib_symbols"):
            if not done:
                new_h.append(merged if merged.startswith("\n") else "\n" + merged)
                done = True
        else:
            new_h.append(h)
    sheet.header = new_h


def _replace_connector(
    sheet: sch_import.Sheet,
    path: str,
    old_ref: str,
    news: list[tuple],
) -> None:
    old = next(e for e in sheet.elements if e.ref == old_ref)
    ox, oy = old.at
    tips = {_key(t) for t in sch_edit.symbol_tips(old)}

    # drop old connector + tip labels / NC
    kept: list[sch_import.Element] = []
    for e in sheet.elements:
        if e.ref == old_ref:
            continue
        if e.kind in ("label", "no_connect", "hierarchical_label") and e.at and _key(e.at) in tips:
            continue
        kept.append(e)
    sheet.elements = kept

    for new_ref, value, lib, fp, nets, dx in news:
        x, y = ox + dx, oy
        sheet.elements.append(sch_import.Element(
            "symbol",
            symbol_inst_v10(lib, new_ref, value, x, y, 0, path, footprint=fp),
            new_ref, None, (x, y)))
        tip_map = dict(zip(sch_edit.lib_pins(lib).keys(),
                           sch_edit.symbol_tips(sheet.elements[-1])))
        for num, net in nets.items():
            tx, ty = tip_map[num]
            if net is None:
                sheet.elements.append(sch_import.Element(
                    "no_connect", _nc(tx, ty), None, None, (tx, ty)))
            else:
                sheet.elements.append(sch_import.Element(
                    "label", _label(net, tx, ty, tx < x), None, net, (tx, ty)))
        print(f"  + {new_ref} @ ({x:.2f},{y:.2f})")


def main() -> None:
    print("DIG_A", DIG_A)
    print("DIG_B", DIG_B)
    print("ANA_A", ANA_A)
    print("ANA_B", ANA_B)
    libs = [LIB10, LIB8]
    for sch_path, inst_path, group in JOBS:
        print(f"== {sch_path.name}")
        sheet = sch_import.load(sch_path)
        _ensure_libs(sheet, libs)
        for old_ref, news in group:
            if not any(e.ref == old_ref for e in sheet.elements):
                if any(e.ref == news[0][0] for e in sheet.elements):
                    print(f"  skip {old_ref} (already split)")
                    continue
                raise SystemExit(f"missing {old_ref} in {sch_path.name}")
            print(f"  replace {old_ref}")
            _replace_connector(sheet, inst_path, old_ref, news)
        sch_helpers.write_sch(sch_path, sheet.render())
        print(f"  wrote {sch_path.name}")


if __name__ == "__main__":
    main()
