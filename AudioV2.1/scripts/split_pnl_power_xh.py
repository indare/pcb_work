#!/usr/bin/env python3
"""FrontPanel 渡りから 12V を電源専用 XH へ分離する（回路図のみ・外科的）。

方針:
  - 音声 `J_PNL_A*` から PD_12V / PD_12V_SW / PD_GND を外し NC にする
  - 母板 `J_PNL_P1601`/`J_PNL_P1602`、FP `J_PNL_P1611`/`J_PNL_P1612` を新設（XH3）
  - A_GND は音声 XH、D_GND はデジ XH、PD_GND は電源 XH のみ（同居しない）

全面再生成はしない。`build_motherboard.py` は回さない。
"""
from __future__ import annotations

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

_NS = uuid.UUID("b2000050-0050-4050-8050-000000000050")
_seq = 0

LIB3 = "Connector_Generic:Conn_01x03"
FP3 = "Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical"

# 外すネット（音声コネクタ先端）
POWER_NETS = {"PD_12V", "PD_12V_SW", "PD_GND"}


def uid() -> str:
    global _seq
    _seq += 1
    return str(uuid.uuid5(_NS, f"pnlpwr/{_seq}"))


def _key(p: tuple[float, float], nd: int = 2) -> tuple[float, float]:
    return (round(p[0], nd), round(p[1], nd))


def _label(name: str, x: float, y: float, left: bool, hierarchical: bool) -> str:
    rot, just = (180, "right") if left else (0, "left")
    if hierarchical:
        shape = {
            "PD_12V": "input",
            "PD_12V_SW": "bidirectional",
            "PD_GND": "bidirectional",
        }.get(name, "bidirectional")
        return (
            f'\t(hierarchical_label "{name}"\n'
            f'\t\t(shape {shape})\n'
            f'\t\t(at {x} {y} {rot})\n'
            f'\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n'
            f'\t\t\t(justify {just})\n\t\t)\n'
            f'\t\t(uuid "{uid()}")\n\t)\n'
        )
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


def _strip_power_from_ana(sheet: sch_import.Sheet, ana_refs: list[str]) -> None:
    """音声 XH 先端の PD_* ラベル／hier を NC に置換。"""
    tip_keys: set[tuple[float, float]] = set()
    for ref in ana_refs:
        el = next((e for e in sheet.elements if e.ref == ref), None)
        if el is None:
            raise SystemExit(f"missing {ref}")
        tip_keys |= {_key(t) for t in sch_edit.symbol_tips(el)}

    kept: list[sch_import.Element] = []
    stripped = 0
    for e in sheet.elements:
        if (
            e.kind in ("label", "hierarchical_label")
            and e.at
            and _key(e.at) in tip_keys
            and e.name in POWER_NETS
        ):
            tx, ty = e.at
            kept.append(sch_import.Element("no_connect", _nc(tx, ty), None, None, (tx, ty)))
            stripped += 1
            continue
        kept.append(e)
    sheet.elements = kept
    print(f"  stripped PD_* tips -> NC: {stripped}")


def _add_power_pair(
    sheet: sch_import.Sheet,
    path: str,
    refs: tuple[str, str],
    values: tuple[str, str],
    nets: tuple[dict[str, str | None], dict[str, str | None]],
    origin: tuple[float, float],
    dx: float,
    hierarchical: bool,
) -> None:
    if any(e.ref == refs[0] for e in sheet.elements):
        print(f"  skip power pair (already have {refs[0]})")
        return
    ox, oy = origin
    for i, (ref, value, netmap) in enumerate(zip(refs, values, nets)):
        x, y = ox + i * dx, oy
        sheet.elements.append(sch_import.Element(
            "symbol",
            symbol_inst_v10(LIB3, ref, value, x, y, 0, path, footprint=FP3),
            ref, None, (x, y)))
        tip_map = dict(zip(
            sch_edit.lib_pins(LIB3).keys(),
            sch_edit.symbol_tips(sheet.elements[-1])))
        for num, net in netmap.items():
            tx, ty = tip_map[num]
            if net is None:
                sheet.elements.append(sch_import.Element(
                    "no_connect", _nc(tx, ty), None, None, (tx, ty)))
            else:
                sheet.elements.append(sch_import.Element(
                    "label" if not hierarchical else "hierarchical_label",
                    _label(net, tx, ty, tx < x, hierarchical),
                    None, net, (tx, ty)))
        print(f"  + {ref} @ ({x:.2f},{y:.2f}) {netmap}")


def main() -> None:
    pwr_a = {"1": "PD_12V", "2": "PD_GND", "3": None}
    pwr_b = {"1": "PD_12V_SW", "2": "PD_GND", "3": None}

    # --- mother ---
    mother = ROOT / "AudioV2Case.kicad_sch"
    print(f"== {mother.name}")
    sheet = sch_import.load(mother)
    _ensure_libs(sheet, [LIB3])
    _strip_power_from_ana(sheet, ["J_PNL_A1601_1", "J_PNL_A1601_2"])
    # 音声コネクタの右へ
    ana = next(e for e in sheet.elements if e.ref == "J_PNL_A1601_2")
    _add_power_pair(
        sheet, ROOT_PATH,
        ("J_PNL_P1601", "J_PNL_P1602"),
        ("FrontPanel 12V raw", "FrontPanel 12V switched"),
        (pwr_a, pwr_b),
        (ana.at[0] + 25.4, ana.at[1]),
        15.24,
        hierarchical=False,
    )
    sch_helpers.write_sch(mother, sheet.render())
    print(f"  wrote {mother.name}")

    # --- FrontPanel ---
    fp = ROOT / "FrontPanel.kicad_sch"
    print(f"== {fp.name}")
    sheet = sch_import.load(fp)
    _ensure_libs(sheet, [LIB3])
    _strip_power_from_ana(sheet, ["J_PNL_A1602_1", "J_PNL_A1602_2"])
    ana = next(e for e in sheet.elements if e.ref == "J_PNL_A1602_2")
    _add_power_pair(
        sheet, FP_PATH,
        ("J_PNL_P1611", "J_PNL_P1612"),
        ("FrontPanel 12V raw", "FrontPanel 12V switched"),
        (pwr_a, pwr_b),
        (ana.at[0] + 25.4, ana.at[1]),
        15.24,
        hierarchical=True,
    )
    sch_helpers.write_sch(fp, sheet.render())
    print(f"  wrote {fp.name}")


if __name__ == "__main__":
    main()
