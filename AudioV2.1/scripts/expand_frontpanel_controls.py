#!/usr/bin/env python3
"""操作系（ポット・DEST/PWR SW・12V LED・DEST ラダー）を FrontPanel へ移す。

- 親ルート / MeasureControl から部品を外し FrontPanel にラベル直置きで再配置
- アナログ／電源用に J_PNL_A1601/1602（Conn_02x08）を追加
- MeasureControl の親向けピンに PHONE_BUF_*/LINE_*/PD_12V を追加
  （CHILD_SHEETS とルート上のシートピンも同期）

冪等ではない。失敗したら git checkout で戻すこと。
"""
from __future__ import annotations

import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_kicad_scaffold as scaffold  # noqa: E402
import sch_edit  # noqa: E402
import sch_helpers  # noqa: E402
import sch_import  # noqa: E402
from build_motherboard import CHILD_SHEETS, _merge_lib_symbols  # noqa: E402
from generate_kicad_scaffold import PARENT, hier_label, sheet_block  # noqa: E402
from sch_helpers import embed_lib_symbols, symbol_inst_v10  # noqa: E402

MC_INST = "43e41fda-fe26-43e3-950a-c017f3070bbf"
FP_INST = "b2000020-0020-4020-8020-000000000020"
MC_PATH = f"/{PARENT}/{MC_INST}"
FP_PATH = f"/{PARENT}/{MC_INST}/{FP_INST}"

_NS = uuid.UUID("b2000025-0025-4025-8025-000000000025")
_seq = 0


def uid() -> str:
    global _seq
    _seq += 1
    return str(uuid.uuid5(_NS, f"ctrl/{_seq}"))


def _label(name: str, x: float, y: float, left: bool = False) -> str:
    rot, just = (180, "right") if left else (0, "left")
    return (
        f'\t(label "{name}"\n\t\t(at {x} {y} {rot})\n\t\t(effects\n\t\t\t(font\n'
        f'\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify {just} bottom)\n\t\t)\n'
        f'\t\t(uuid "{uid()}")\n\t)\n'
    )


def _nc(x: float, y: float) -> str:
    return f'\t(no_connect\n\t\t(at {x} {y})\n\t\t(uuid "{uid()}")\n\t)\n'


def _drop_refs(sheet: sch_import.Sheet, refs: set[str]) -> None:
    tip: set[tuple[float, float]] = set()
    keep_syms = []
    for e in sheet.elements:
        if e.kind == "symbol" and e.ref in refs:
            try:
                tip |= {(round(t[0], 2), round(t[1], 2)) for t in sch_edit.symbol_tips(e)}
            except Exception:
                pass
            continue
        keep_syms.append(e)
    # also drop labels/nc at those tips and short wires that only touch them
    out = []
    for e in keep_syms:
        if e.kind in ("label", "no_connect") and e.at and (round(e.at[0], 2), round(e.at[1], 2)) in tip:
            continue
        if e.kind == "wire":
            cs = e.coords()
            if cs and all((round(c[0], 2), round(c[1], 2)) in tip for c in cs):
                continue
        out.append(e)
    sheet.elements = out


def _place(sheet: sch_import.Sheet, path: str, lib: str, ref: str, value: str,
           x: float, y: float, nets: dict[str, str], nc: list[str] | None = None,
           fp: str = "", rot: int = 0) -> None:
    el = sch_import.Element(
        "symbol",
        symbol_inst_v10(lib, ref, value, x, y, rot, path, footprint=fp),
        ref, None, (x, y))
    sheet.elements.append(el)
    tips = dict(zip(sch_edit.lib_pins(lib).keys(), sch_edit.symbol_tips(el)))
    for num, net in nets.items():
        tx, ty = tips[str(num)]
        sheet.elements.append(sch_import.Element(
            "label", _label(net, tx, ty, tx < x), None, net, (tx, ty)))
    for num in nc or []:
        tx, ty = tips[str(num)]
        sheet.elements.append(sch_import.Element(
            "no_connect", _nc(tx, ty), None, None, (tx, ty)))


# --- analog connector (2x08) ---
ANA_LIB = "Connector_Generic:Conn_02x08_Odd_Even"
ANA_FP = "Connector_PinHeader_2.54mm:PinHeader_2x08_P2.54mm_Vertical"
ANA_NETS: dict[str, str | None] = {
    "1": "AMP_SEL_L",
    "2": "AMP_SEL_R",
    "3": "PHONE_BUF_L",
    "4": "PHONE_BUF_R",
    "5": "LINE_L",
    "6": "LINE_R",
    "7": "A_GND",
    "8": "A_GND",
    "9": "PD_12V",
    "10": "PD_12V_SW",
    "11": "PD_GND",
    "12": "DEST_ADC",
    "13": None,
    "14": None,
    "15": None,
    "16": None,
}

ANA_HIER: list[tuple[str, str]] = [
    ("AMP_SEL_L", "input"),
    ("AMP_SEL_R", "input"),
    ("PHONE_BUF_L", "input"),
    ("PHONE_BUF_R", "input"),
    ("LINE_L", "output"),
    ("LINE_R", "output"),
    ("A_GND", "bidirectional"),
    ("PD_12V", "input"),
    ("PD_12V_SW", "bidirectional"),
    ("PD_GND", "bidirectional"),
    ("DEST_ADC", "output"),
]

# MeasureControl → 親へ足すピン（既存 AUDIO_* は AMP_SEL。PD_12V_SW は ADC_V_IN 経由で既にあるが
# 名前を揃えるため PD_12V だけ新規。BUF/LINE も新規）
NEW_MC_TO_ROOT: list[tuple[str, str, str]] = [
    # name, shape, parent_net_label
    ("PHONE_BUF_L", "input", "PHONE_BUF_L"),
    ("PHONE_BUF_R", "input", "PHONE_BUF_R"),
    ("LINE_L", "output", "LINE_L"),
    ("LINE_R", "output", "LINE_R"),
    ("PD_12V", "input", "PD_12V"),
]


def _ensure_lib(sheet: sch_import.Sheet, libs: list[str]) -> None:
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


def _rebuild_fp_sheet_pins(mc: sch_import.Sheet) -> None:
    """MeasureControl 上の FrontPanel シートを、既存デジ＋新アナログ hier で作り直す。"""
    # collect existing digital pin names from current sheet / FP hier
    fp = sch_import.load(ROOT / "FrontPanel.kicad_sch")
    dig = sorted({e.name for e in fp.elements if e.kind == "hierarchical_label"} - {n for n, _ in ANA_HIER})
    # stable order from known digital set
    dig_order = [
        "3V3", "+5V_D", "D_GND", "I2C_SDA", "I2C_SCL",
        "ENC_INTA", "ENC_INTB",
        "LCD_CS", "LCD_DC", "LCD_RST", "LCD_EN", "LCD_SCK", "LCD_MOSI",
        "TP_SDA", "TP_SCL", "TP_INT", "TP_RST",
    ]
    dig = [n for n in dig_order if n in dig] + sorted(set(dig) - set(dig_order))

    # drop old FrontPanel sheet + its pin labels (near sheet)
    old = next(e for e in mc.elements if e.kind == "sheet" and e.name == "FrontPanel")
    m_at = re.search(r"\(at ([-\d.]+) ([-\d.]+)\)", old.text)
    m_sz = re.search(r"\(size ([-\d.]+) ([-\d.]+)\)", old.text)
    sx, sy = float(m_at.group(1)), float(m_at.group(2))
    sw = float(m_sz.group(1))

    # remove sheet and labels sitting on left pin column
    new_els = []
    for e in mc.elements:
        if e.kind == "sheet" and e.name == "FrontPanel":
            continue
        if e.kind == "label" and e.at and abs(e.at[0] - sx) < 0.2 and sy <= e.at[1] <= sy + 80:
            continue
        new_els.append(e)
    mc.elements = new_els

    shapes = {
        "3V3": "input", "+5V_D": "input", "D_GND": "bidirectional",
        "I2C_SDA": "bidirectional", "I2C_SCL": "bidirectional",
        "ENC_INTA": "output", "ENC_INTB": "output",
        "LCD_CS": "input", "LCD_DC": "input", "LCD_RST": "input",
        "LCD_EN": "input", "LCD_SCK": "input", "LCD_MOSI": "input",
        "TP_SDA": "bidirectional", "TP_SCL": "bidirectional",
        "TP_INT": "output", "TP_RST": "input",
    }
    shapes.update(dict(ANA_HIER))

    pins_all = [(n, shapes[n]) for n in dig] + list(ANA_HIER)
    # de-dup A_GND if both
    seen = set()
    pins_u: list[tuple[str, str]] = []
    for n, s in pins_all:
        if n in seen:
            continue
        seen.add(n)
        pins_u.append((n, s))

    sh = max(55.88, 2.54 + len(pins_u) * 2.54 + 2.54)
    blk = []
    for i, (pn, kind) in enumerate(pins_u):
        py = sy + 2.54 + i * 2.54
        blk.append((pn, kind, sx, py, 180))
        # MC local: AMP_SEL ← AUDIO_* 、他はそのまま
        net = pn
        if pn == "AMP_SEL_L":
            net = "AUDIO_L_IN"
        elif pn == "AMP_SEL_R":
            net = "AUDIO_R_IN"
        mc.elements.append(sch_import.Element(
            "label", _label(net, sx, py, left=True), None, net, (sx, py)))
    mc.elements.append(sch_import.Element(
        "sheet",
        sheet_block(FP_INST, "FrontPanel", "FrontPanel.kicad_sch",
                    sx, sy, sw, sh, blk, "2", parent_path=MC_PATH),
        None, "FrontPanel", (sx, sy)))


def _add_ana_connector(sheet: sch_import.Sheet, path: str, ref: str,
                       x: float, y: float, hier_on_tips: bool) -> None:
    sheet.elements.append(sch_import.Element(
        "symbol",
        symbol_inst_v10(ANA_LIB, ref, "FrontPanel analog/power",
                        x, y, 0, path, footprint=ANA_FP),
        ref, None, (x, y)))
    tips = dict(zip(sch_edit.lib_pins(ANA_LIB).keys(),
                    sch_edit.symbol_tips(sheet.elements[-1])))
    shape = dict(ANA_HIER)
    for num, net in ANA_NETS.items():
        tx, ty = tips[num]
        if net is None:
            sheet.elements.append(sch_import.Element(
                "no_connect", _nc(tx, ty), None, None, (tx, ty)))
            continue
        rot = 180 if tx < x else 0
        if hier_on_tips:
            sheet.elements.append(sch_import.Element(
                "hierarchical_label",
                hier_label(net, shape[net], tx, ty, rot),
                None, net, (tx, ty)))
        else:
            sheet.elements.append(sch_import.Element(
                "label", _label(net, tx, ty, tx < x), None, net, (tx, ty)))


def _update_child_sheets_code() -> None:
    path = ROOT / "scripts" / "build_motherboard.py"
    text = path.read_text(encoding="utf-8")
    needle = '("3V3", "output", "R", "3V3"), ("D_GND", "bidirectional", "R", "D_GND"),'
    insert = (
        '("3V3", "output", "R", "3V3"), ("D_GND", "bidirectional", "R", "D_GND"),\n'
        '         ("PHONE_BUF_L", "input", "R", "PHONE_BUF_L"), '
        '("PHONE_BUF_R", "input", "R", "PHONE_BUF_R"),\n'
        '         ("LINE_L", "output", "R", "LINE_L"), '
        '("LINE_R", "output", "R", "LINE_R"),\n'
        '         ("PD_12V", "input", "L", "PD_12V"),'
    )
    if "PHONE_BUF_L" in text:
        print("build_motherboard CHILD_SHEETS: 既に PHONE_BUF あり")
        return
    if needle not in text:
        raise SystemExit("CHILD_SHEETS の差し込み位置が見つからない")
    path.write_text(text.replace(needle, insert, 1), encoding="utf-8", newline="\n")
    print("更新: build_motherboard.py CHILD_SHEETS")


def _patch_root_mc_sheet(case: sch_import.Sheet) -> None:
    """AudioV2Case の MeasureControl シートに新ピン＋ラベルを足す（手編集同期）。"""
    sh = next(e for e in case.elements if e.kind == "sheet" and e.name == "MeasureControl")
    # append pins on the right side below existing
    # parse current size / at
    m_at = re.search(r"\(at ([-\d.]+) ([-\d.]+)\)", sh.text)
    m_sz = re.search(r"\(size ([-\d.]+) ([-\d.]+)\)", sh.text)
    sx, sy = float(m_at.group(1)), float(m_at.group(2))
    sw, shh = float(m_sz.group(1)), float(m_sz.group(2))
    # existing right pins count from text
    right_pins = re.findall(r'\(pin "([^"]+)" (\w+)\s*\n\s*\(at ' + re.escape(f"{sx + sw}"), sh.text)
    # simpler: add hierarchical connectivity via bare labels next to sheet for new nets,
    # and extend sheet pin list by rewriting sheet block from CHILD_SHEETS definition.
    from build_motherboard import CHILD_SHEETS as CS
    mc_entry = next(c for c in CS if c[0] == "MeasureControl")
    name, fname, inst, (csx, csy), (csw, csh), pins = mc_entry
    # use live position
    lefts = [p for p in pins if p[2] == "L"]
    rights = [p for p in pins if p[2] == "R"]
    blk = []
    for i, (pn, kind, side, net) in enumerate(lefts):
        px = sx
        py = sy + 2.54 + i * 2.54
        blk.append((pn, kind, px, py, 180))
    for i, (pn, kind, side, net) in enumerate(rights):
        px = sx + sw
        py = sy + 2.54 + i * 2.54
        blk.append((pn, kind, px, py, 0))
    need = sy + 2.54 + (max(len(lefts), len(rights)) - 1) * 2.54
    new_h = max(shh, need - sy + 2.54)

    # drop old MC sheet and its pin-column labels
    new_els = []
    for e in case.elements:
        if e.kind == "sheet" and e.name == "MeasureControl":
            continue
        if e.kind == "label" and e.at:
            if abs(e.at[0] - sx) < 0.3 or abs(e.at[0] - (sx + sw)) < 0.3:
                if sy - 1 <= e.at[1] <= sy + new_h + 1:
                    # keep only if not a sheet-pin companion — drop all on pin columns
                    continue
        new_els.append(e)
    case.elements = new_els

    for pn, kind, px, py, ang in blk:
        net = next(t[3] for t in pins if t[0] == pn)
        left = ang == 180
        case.elements.append(sch_import.Element(
            "label", _label(net, px, py, left), None, net, (px, py)))
    case.elements.append(sch_import.Element(
        "sheet",
        sheet_block(inst, name, fname, sx, sy, sw, new_h, blk, "2"),
        None, "MeasureControl", (sx, sy)))


def _add_mc_hier(mc: sch_import.Sheet) -> None:
    existing = {e.name for e in mc.elements if e.kind == "hierarchical_label"}
    x0, y0 = 520.0, 340.0
    i = 0
    for name, shape, _ in NEW_MC_TO_ROOT:
        if name in existing:
            continue
        hx, hy = x0, y0 + i * 2.54
        mc.elements.append(sch_import.Element(
            "hierarchical_label", hier_label(name, shape, hx, hy, 0),
            None, name, (hx, hy)))
        # stub wire + local label so not dangling: short wire to local same-name label
        mc.elements.append(sch_import.Element(
            "label", _label(name, hx + 5.08, hy), None, name, (hx + 5.08, hy)))
        from sch_helpers import wire
        mc.elements.append(sch_import.Element(
            "wire", wire(hx, hy, hx + 5.08, hy), None, None, (hx, hy)))
        i += 1


def main() -> int:
    saved_new, sch_helpers.new_uid = sch_helpers.new_uid, uid
    saved_sc, scaffold.uid = scaffold.uid, uid
    try:
        _update_child_sheets_code()
        # reload CHILD_SHEETS after patch
        import importlib
        import build_motherboard as bm
        importlib.reload(bm)

        case = sch_import.load(ROOT / "AudioV2Case.kicad_sch")
        mc = sch_import.load(ROOT / "MeasureControl.kicad_sch")
        fp = sch_import.load(ROOT / "FrontPanel.kicad_sch")

        from_case = {"RV501", "RV502", "SW501", "SW502", "SW402", "D403", "R401"}
        from_mc = {"SW1601", "R1655", "R1656", "R1657", "R1658"}
        _drop_refs(case, from_case)
        _drop_refs(mc, from_mc)

        # FrontPanel controls island (right of existing UI)
        x0, y0 = 400.0, 340.0
        HDR4 = "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical"
        HDR6 = "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical"
        HDR2 = "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical"
        # 垂直実装（パネルネジ止め前提。品番確定までヘッダ垂直のまま）
        _place(fp, FP_PATH, "Device:R_Potentiometer_Dual", "RV501", "A50k Dual HP",
               x0, y0, {
                   "1": "PHONE_PRE_L", "2": "PHONE_BUF_L", "3": "A_GND",
                   "4": "PHONE_PRE_R", "5": "PHONE_BUF_R", "6": "A_GND",
               }, fp=HDR6)
        _place(fp, FP_PATH, "Device:R_Potentiometer_Dual", "RV502", "A50k Dual LINE",
               x0 + 40.64, y0, {
                   "1": "LINE_PRE_L", "2": "LINE_L", "3": "A_GND",
                   "4": "LINE_PRE_R", "5": "LINE_R", "6": "A_GND",
               }, fp=HDR6)
        _place(fp, FP_PATH, "Switch:SW_SP3T", "SW501", "DEST L",
               x0, y0 + 45.72, {
                   "1": "PHONE_PRE_L", "3": "AMP_SEL_L", "4": "LINE_PRE_L",
               }, nc=["2"], fp=HDR4)
        _place(fp, FP_PATH, "Switch:SW_SP3T", "SW502", "DEST R",
               x0 + 40.64, y0 + 45.72, {
                   "1": "PHONE_PRE_R", "3": "AMP_SEL_R", "4": "LINE_PRE_R",
               }, nc=["2"], fp=HDR4)
        _place(fp, FP_PATH, "Switch:SW_SP3T", "SW1601",
               "DEST sense (3PDT 3rd pole, same body as SW501/SW502)",
               x0 + 81.28, y0 + 45.72, {
                   "1": "DEST_SENSE_PHONE", "2": "DEST_SENSE_MUTE_NC",
                   "3": "DEST_ADC", "4": "DEST_SENSE_LINE",
               }, fp=HDR4)
        # DEST ladder
        for i, (ref, val, hi, lo) in enumerate((
            ("R1655", "1k", "3V3", "DEST_SENSE_LINE"),
            ("R1656", "10k", "3V3", "DEST_ADC"),
            ("R1657", "10k", "DEST_ADC", "D_GND"),
            ("R1658", "1k", "DEST_SENSE_PHONE", "D_GND"),
        )):
            _place(fp, FP_PATH, "Device:R", ref, val, x0 + i * 15.24, y0 + 81.28,
                   {"1": hi, "2": lo},
                   fp="Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder")
        _place(fp, FP_PATH, "Switch:SW_SPST", "SW402", "PWR SW",
               x0 + 81.28, y0, {"1": "PD_12V", "2": "PD_12V_SW"}, fp=HDR2)
        _place(fp, FP_PATH, "Device:R", "R401", "1k",
               x0 + 101.6, y0, {"1": "PD_12V_SW", "2": "LED_12V_A"},
               fp="Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder")
        _place(fp, FP_PATH, "Device:LED", "D403", "12V panel LED",
               x0 + 101.6, y0 + 15.24, {"1": "PD_GND", "2": "LED_12V_A"},
               fp="LED_THT:LED_D5.0mm")
        # MUTE NC
        # DEST_SENSE_MUTE_NC already on SW1601 pin4 — add isolated label ok via pin

        _add_ana_connector(fp, FP_PATH, "J_PNL_A1602", 500.38, 400.0, hier_on_tips=True)
        _add_ana_connector(mc, MC_PATH, "J_PNL_A1601", 360.0, 200.0, hier_on_tips=False)

        _ensure_lib(fp, [
            "Device:R_Potentiometer_Dual", "Switch:SW_SP3T", "Switch:SW_SPST",
            "Device:R", "Device:LED", ANA_LIB,
        ])
        _ensure_lib(mc, [ANA_LIB])

        _add_mc_hier(mc)
        _rebuild_fp_sheet_pins(mc)
        _patch_root_mc_sheet(case)

        sch_helpers.write_sch(ROOT / "FrontPanel.kicad_sch", fp.render())
        sch_helpers.write_sch(ROOT / "MeasureControl.kicad_sch", mc.render())
        sch_helpers.write_sch(ROOT / "AudioV2Case.kicad_sch", case.render())
        sch_helpers.canonicalize_sch([
            ROOT / "FrontPanel.kicad_sch",
            ROOT / "MeasureControl.kicad_sch",
            ROOT / "AudioV2Case.kicad_sch",
        ])
        print("完了: 操作系 → FrontPanel、J_PNL_A 追加")
        return 0
    finally:
        sch_helpers.new_uid = saved_new
        scaffold.uid = saved_sc


if __name__ == "__main__":
    raise SystemExit(main())
