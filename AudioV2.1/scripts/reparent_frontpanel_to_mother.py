#!/usr/bin/env python3
"""FrontPanel を MeasureControl の子から AudioV2Case（母板）直下へ上げる。

やること:
  - MC 上の FrontPanel シートと J_PNL* メイトを外す
  - 母板上に FrontPanel シート＋ J_PNL1601/J_PNL_A1601 を置く
  - Pico 向けデジ（ENC_INT / LCD / TP / +5V_D）を MC の hier に出す
  - パネル渡り専用だった PHONE_BUF / LINE / PD_12V を MC 界面から外す
  - FP から未使用の DEST_ADC hier／コネクタピンを外す（プルは MC のまま）
  - 部品 instances パスと PCB path／sheetname を直す
  - build_motherboard.CHILD_SHEETS を同期（再生成はしない）

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
from generate_kicad_scaffold import PARENT, hier_label, sheet_block  # noqa: E402
from sch_helpers import embed_lib_symbols, symbol_inst_v10, wire  # noqa: E402

MC_INST = "43e41fda-fe26-43e3-950a-c017f3070bbf"
FP_INST = "b2000020-0020-4020-8020-000000000020"
MC_PATH = f"/{PARENT}/{MC_INST}"
FP_OLD = f"/{PARENT}/{MC_INST}/{FP_INST}"
FP_NEW = f"/{PARENT}/{FP_INST}"
ROOT_PATH = f"/{PARENT}"

_NS = uuid.UUID("b2000030-0030-4030-8030-000000000030")
_seq = 0

# MC → 母板へ新規に出す（Pico 側）
MC_NEW_HIER: list[tuple[str, str]] = [
    ("+5V_D", "output"),
    ("ENC_INTA", "input"),
    ("ENC_INTB", "input"),
    ("LCD_CS", "output"),
    ("LCD_DC", "output"),
    ("LCD_RST", "output"),
    ("LCD_EN", "output"),
    ("LCD_SCK", "output"),
    ("LCD_MOSI", "output"),
    ("TP_SDA", "bidirectional"),
    ("TP_SCL", "bidirectional"),
    ("TP_INT", "input"),
    ("TP_RST", "output"),
]

# MC 界面から外す（母板↔FrontPanel 直結になる）
MC_DROP_HIER = {"PHONE_BUF_L", "PHONE_BUF_R", "LINE_L", "LINE_R", "PD_12V"}

# FrontPanel シートピン（DEST_ADC は外す）
FP_PINS: list[tuple[str, str]] = [
    ("3V3", "input"),
    ("+5V_D", "input"),
    ("D_GND", "bidirectional"),
    ("I2C_SDA", "bidirectional"),
    ("I2C_SCL", "bidirectional"),
    ("ENC_INTA", "output"),
    ("ENC_INTB", "output"),
    ("LCD_CS", "input"),
    ("LCD_DC", "input"),
    ("LCD_RST", "input"),
    ("LCD_EN", "input"),
    ("LCD_SCK", "input"),
    ("LCD_MOSI", "input"),
    ("TP_SDA", "bidirectional"),
    ("TP_SCL", "bidirectional"),
    ("TP_INT", "output"),
    ("TP_RST", "input"),
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
]

DIG_NETS = {
    "1": "3V3", "2": "+5V_D", "3": "D_GND", "4": "D_GND",
    "5": "I2C_SDA", "6": "I2C_SCL", "7": "ENC_INTA", "8": "ENC_INTB",
    "9": "LCD_CS", "10": "LCD_DC", "11": "LCD_RST", "12": "LCD_EN",
    "13": "LCD_SCK", "14": "LCD_MOSI", "15": "TP_SDA", "16": "TP_SCL",
    "17": "TP_INT", "18": "TP_RST", "19": None, "20": None,
}
ANA_NETS = {
    "1": "AMP_SEL_L", "2": "AMP_SEL_R",
    "3": "PHONE_BUF_L", "4": "PHONE_BUF_R",
    "5": "LINE_L", "6": "LINE_R",
    "7": "A_GND", "8": "A_GND",
    "9": "PD_12V", "10": "PD_12V_SW",
    "11": "PD_GND", "12": None,  # was DEST_ADC
    "13": None, "14": None, "15": None, "16": None,
}

DIG_LIB = "Connector_Generic:Conn_02x10_Odd_Even"
DIG_FP = "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical"
ANA_LIB = "Connector_Generic:Conn_02x08_Odd_Even"
ANA_FP = "Connector_PinHeader_2.54mm:PinHeader_2x08_P2.54mm_Vertical"


def uid() -> str:
    global _seq
    _seq += 1
    return str(uuid.uuid5(_NS, f"reparent/{_seq}"))


def _label(name: str, x: float, y: float, left: bool = False) -> str:
    rot, just = (180, "right") if left else (0, "left")
    return (
        f'\t(label "{name}"\n\t\t(at {x} {y} {rot})\n\t\t(effects\n\t\t\t(font\n'
        f'\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify {just} bottom)\n\t\t)\n'
        f'\t\t(uuid "{uid()}")\n\t)\n'
    )


def _nc(x: float, y: float) -> str:
    return f'\t(no_connect\n\t\t(at {x} {y})\n\t\t(uuid "{uid()}")\n\t)\n'


def _rewrite_path(text: str, old: str, new: str) -> str:
    return text.replace(f'(path "{old}"', f'(path "{new}"')


def _drop_fp_sheet_and_connectors(mc: sch_import.Sheet) -> tuple[sch_import.Element, sch_import.Element]:
    """MC から FrontPanel シート／ピン列ラベル／J_PNL* を外し、コネクタ Element を返す。"""
    fp_sheet = next(e for e in mc.elements if e.kind == "sheet" and e.name == "FrontPanel")
    m_at = re.search(r"\(at ([-\d.]+) ([-\d.]+)\)", fp_sheet.text)
    m_sz = re.search(r"\(size ([-\d.]+) ([-\d.]+)\)", fp_sheet.text)
    sx, sy = float(m_at.group(1)), float(m_at.group(2))
    sw, sh = float(m_sz.group(1)), float(m_sz.group(2))

    dig = ana = None
    tip: set[tuple[float, float]] = set()
    keep = []
    for e in mc.elements:
        if e.kind == "sheet" and e.name == "FrontPanel":
            continue
        if e.kind == "symbol" and e.ref in ("J_PNL1601", "J_PNL_A1601"):
            try:
                tip |= {(round(t[0], 2), round(t[1], 2)) for t in sch_edit.symbol_tips(e)}
            except Exception:
                pass
            if e.ref == "J_PNL1601":
                dig = e
            else:
                ana = e
            continue
        # シート左ピン列のラベル
        if e.kind == "label" and e.at and abs(e.at[0] - sx) < 0.3 and sy - 1 <= e.at[1] <= sy + sh + 1:
            continue
        keep.append(e)

    # コネクタ先端のラベル／NC／短いワイヤも落とす
    out = []
    for e in keep:
        if e.kind in ("label", "no_connect") and e.at and (round(e.at[0], 2), round(e.at[1], 2)) in tip:
            continue
        if e.kind == "wire":
            cs = e.coords()
            if cs and all((round(c[0], 2), round(c[1], 2)) in tip for c in cs):
                continue
        out.append(e)
    mc.elements = out
    if dig is None or ana is None:
        raise SystemExit("J_PNL1601 / J_PNL_A1601 が MeasureControl に無い")
    return dig, ana


def _drop_mc_passthrough_hier(mc: sch_import.Sheet) -> None:
    """PHONE_BUF / LINE / PD_12V の hier と、それにぶら下がる短いラベル列を外す。"""
    drop_pts: set[tuple[float, float]] = set()
    keep = []
    for e in mc.elements:
        if e.kind == "hierarchical_label" and e.name in MC_DROP_HIER:
            if e.at:
                drop_pts.add((round(e.at[0], 2), round(e.at[1], 2)))
            continue
        keep.append(e)
    out = []
    for e in keep:
        if e.kind == "label" and e.name in MC_DROP_HIER:
            # 渡り専用スタブ（hier 近傍）だけ落とす。他に無いはず
            continue
        if e.kind == "wire":
            cs = e.coords()
            if cs and any((round(c[0], 2), round(c[1], 2)) in drop_pts for c in cs):
                # hier に直結する短い水平スタブだけ
                if len(cs) == 2 and abs(cs[0][1] - cs[1][1]) < 0.01 and abs(cs[0][0] - cs[1][0]) <= 6.0:
                    continue
        out.append(e)
    # DEST_ADC のシート／コネクタ向けラベルで、プル抵抗以外を落とす
    # R1657 先端 (≈360.68, 336.55) の DEST_ADC は残す
    keep2 = []
    for e in out:
        if e.kind == "label" and e.name == "DEST_ADC" and e.at:
            x, y = e.at
            # プル近傍以外（旧 FP シート列 y≈171、コネクタ列）は削除
            if abs(y - 336.55) > 2.0 and abs(x - 360.68) > 2.0:
                continue
        keep2.append(e)
    mc.elements = keep2


def _add_mc_new_hier(mc: sch_import.Sheet) -> None:
    existing = {e.name for e in mc.elements if e.kind == "hierarchical_label"}
    # 既存 hier 群の右端付近に縦に足す
    x0, y0 = 520.0, 360.0
    i = 0
    for name, shape in MC_NEW_HIER:
        if name in existing:
            continue
        hx, hy = x0, y0 + i * 2.54
        mc.elements.append(sch_import.Element(
            "hierarchical_label", hier_label(name, shape, hx, hy, 0),
            None, name, (hx, hy)))
        # 既存ローカル同名ラベルと hier をワイヤで結ぶ必要は無い（同名ラベルで繋がる）
        # ただし hier だけだと孤立するので、短いスタブ＋同名ラベル
        mc.elements.append(sch_import.Element(
            "label", _label(name, hx + 5.08, hy), None, name, (hx + 5.08, hy)))
        mc.elements.append(sch_import.Element(
            "wire", wire(hx, hy, hx + 5.08, hy), None, None, (hx, hy)))
        i += 1


def _rebuild_root_sheets(case: sch_import.Sheet) -> None:
    """MeasureControl シートだけ CHILD_SHEETS で作り直し、FrontPanel シートを母板直下に追加。

    AmpBank* は触らない（手配置・既存ラベルを壊さない）。
    """
    from build_motherboard import CHILD_SHEETS as CS

    pos = {}
    for e in case.elements:
        if e.kind != "sheet" or not e.name:
            continue
        m_at = re.search(r"\(at ([-\d.]+) ([-\d.]+)\)", e.text)
        m_sz = re.search(r"\(size ([-\d.]+) ([-\d.]+)\)", e.text)
        pos[e.name] = (
            float(m_at.group(1)), float(m_at.group(2)),
            float(m_sz.group(1)), float(m_sz.group(2)),
        )

    def on_pin_col(e: sch_import.Element, sx: float, sy: float, sw: float, sh: float) -> bool:
        if e.kind != "label" or not e.at:
            return False
        x, y = e.at
        if not (sy - 1 <= y <= sy + sh + 1):
            return False
        return abs(x - sx) < 0.4 or abs(x - (sx + sw)) < 0.4

    new_els = []
    for e in case.elements:
        if e.kind == "sheet" and e.name in ("MeasureControl", "FrontPanel"):
            continue
        drop = False
        for name in ("MeasureControl", "FrontPanel"):
            if name not in pos:
                continue
            sx, sy, sw, sh = pos[name]
            if on_pin_col(e, sx, sy, sw, sh):
                drop = True
                break
        if drop:
            continue
        new_els.append(e)
    case.elements = new_els

    mc_entry = next(c for c in CS if c[0] == "MeasureControl")
    name, fname, inst, (csx, csy), (csw, csh), pins = mc_entry
    sx, sy, sw, sh = pos.get("MeasureControl", (csx, csy, csw, csh))
    lefts = [p for p in pins if p[2] == "L"]
    rights = [p for p in pins if p[2] == "R"]
    blk = []
    for i, (pn, kind, side, net) in enumerate(lefts):
        blk.append((pn, kind, sx, sy + 2.54 + i * 2.54, 180))
    for i, (pn, kind, side, net) in enumerate(rights):
        blk.append((pn, kind, sx + sw, sy + 2.54 + i * 2.54, 0))
    need = sy + 2.54 + (max(len(lefts), len(rights), 1) - 1) * 2.54
    new_h = max(sh, need - sy + 2.54)
    for pn, kind, px, py, ang in blk:
        net = next(t[3] for t in pins if t[0] == pn)
        case.elements.append(sch_import.Element(
            "label", _label(net, px, py, ang == 180), None, net, (px, py)))
    case.elements.append(sch_import.Element(
        "sheet",
        sheet_block(inst, name, fname, sx, sy, sw, new_h, blk, "2"),
        None, name, (sx, sy)))

    # FrontPanel シート（母板直下）
    fp_sx, fp_sy = 470.0, 160.0
    fp_sw = 55.88
    fp_sh = max(55.88, 2.54 + len(FP_PINS) * 2.54 + 2.54)
    blk = []
    for i, (pn, kind) in enumerate(FP_PINS):
        py = fp_sy + 2.54 + i * 2.54
        blk.append((pn, kind, fp_sx, py, 180))
        case.elements.append(sch_import.Element(
            "label", _label(pn, fp_sx, py, True), None, pn, (fp_sx, py)))
    case.elements.append(sch_import.Element(
        "sheet",
        sheet_block(FP_INST, "FrontPanel", "FrontPanel.kicad_sch",
                    fp_sx, fp_sy, fp_sw, fp_sh, blk, "5",
                    parent_path=ROOT_PATH),
        None, "FrontPanel", (fp_sx, fp_sy)))


def _place_root_connectors(case: sch_import.Sheet) -> None:
    """母板上に J_PNL1601 / J_PNL_A1601 をラベル直置きで置く。"""
    libs = [DIG_LIB, ANA_LIB]
    blocks = [h for h in case.header if h.lstrip().startswith("(lib_symbols")]
    from build_motherboard import _merge_lib_symbols
    merged = _merge_lib_symbols(blocks + [embed_lib_symbols(libs)])
    new_h, done = [], False
    for h in case.header:
        if h.lstrip().startswith("(lib_symbols"):
            if not done:
                new_h.append(merged if merged.startswith("\n") else "\n" + merged)
                done = True
        else:
            new_h.append(h)
    case.header = new_h

    placements = [
        ("J_PNL1601", DIG_LIB, "FrontPanel digital", DIG_FP, DIG_NETS, 320.0, 160.0),
        ("J_PNL_A1601", ANA_LIB, "FrontPanel analog/power", ANA_FP, ANA_NETS, 360.0, 200.0),
    ]
    for ref, lib, value, fp, nets, x, y in placements:
        case.elements.append(sch_import.Element(
            "symbol",
            symbol_inst_v10(lib, ref, value, x, y, 0, ROOT_PATH, footprint=fp),
            ref, None, (x, y)))
        tips = dict(zip(sch_edit.lib_pins(lib).keys(),
                        sch_edit.symbol_tips(case.elements[-1])))
        for num, net in nets.items():
            tx, ty = tips[num]
            if net is None:
                case.elements.append(sch_import.Element(
                    "no_connect", _nc(tx, ty), None, None, (tx, ty)))
            else:
                case.elements.append(sch_import.Element(
                    "label", _label(net, tx, ty, tx < x), None, net, (tx, ty)))


def _clean_frontpanel(fp: sch_import.Sheet) -> None:
    """DEST_ADC hier を外し、J_PNL_A1602 pin12 を NC に、instances パスを母板直下へ。"""
    # path rewrite on all elements
    for e in fp.elements:
        e.text = _rewrite_path(e.text, FP_OLD, FP_NEW)
    # drop DEST_ADC hierarchical_label
    fp.elements = [
        e for e in fp.elements
        if not (e.kind == "hierarchical_label" and e.name == "DEST_ADC")
    ]
    # J_PNL_A1602: replace DEST_ADC tip label with NC
    ana = next(e for e in fp.elements if e.ref == "J_PNL_A1602")
    tips = dict(zip(sch_edit.lib_pins(ANA_LIB).keys(), sch_edit.symbol_tips(ana)))
    dest_tip = (round(tips["12"][0], 2), round(tips["12"][1], 2))
    out = []
    for e in fp.elements:
        if e.kind == "label" and e.name == "DEST_ADC" and e.at and (
                round(e.at[0], 2), round(e.at[1], 2)) == dest_tip:
            continue
        if e.kind == "hierarchical_label" and e.name == "DEST_ADC":
            continue
        out.append(e)
    fp.elements = out
    if not any(
        e.kind == "no_connect" and e.at
        and (round(e.at[0], 2), round(e.at[1], 2)) == dest_tip
        for e in fp.elements
    ):
        tx, ty = tips["12"]
        fp.elements.append(sch_import.Element(
            "no_connect", _nc(tx, ty), None, None, (tx, ty)))
    # connector value text
    for e in fp.elements:
        if e.ref == "J_PNL1602":
            e.text = e.text.replace(
                "FrontPanel ↔ MeasureControl", "FrontPanel ↔ Mother")
        if e.ref == "J_PNL_A1602":
            e.text = e.text.replace(
                "FrontPanel analog/power", "FrontPanel analog/power")


def _update_child_sheets_code() -> None:
    path = ROOT / "scripts" / "build_motherboard.py"
    text = path.read_text(encoding="utf-8")
    # MeasureControl pins: drop PHONE/LINE/PD_12V, add digital panel nets
    mc_start = text.index('("MeasureControl", "MeasureControl.kicad_sch",')
    mc_end = text.index('("AmpBankSwitch", "AmpBankSwitch.kicad_sch",')
    new_mc = (
        '("MeasureControl", "MeasureControl.kicad_sch",\n'
        '     "43e41fda-fe26-43e3-950a-c017f3070bbf", (400.0, 220.0), (45.72, 55.88), [\n'
        '         ("+15V_A", "input", "L", "+15V"), ("-15V_A", "input", "L", "-15V"),\n'
        '         ("ADC_GND_IN", "input", "L", "PD_GND"), ("ADC_V_IN", "input", "L", "PD_12V_SW"),\n'
        '         ("AUDIO_L_IN", "input", "L", "AMP_SEL_L"), ("AUDIO_R_IN", "input", "L", "AMP_SEL_R"),\n'
        '         ("A_GND", "bidirectional", "L", "A_GND"),\n'
        '         ("I2C_SDA", "bidirectional", "R", "I2C_SDA"), ("I2C_SCL", "bidirectional", "R", "I2C_SCL"),\n'
        '         ("3V3", "output", "R", "3V3"), ("D_GND", "bidirectional", "R", "D_GND"),\n'
        '         ("+5V_D", "output", "R", "+5V_D"),\n'
        '         ("ENC_INTA", "input", "R", "ENC_INTA"), ("ENC_INTB", "input", "R", "ENC_INTB"),\n'
        '         ("LCD_CS", "output", "R", "LCD_CS"), ("LCD_DC", "output", "R", "LCD_DC"),\n'
        '         ("LCD_RST", "output", "R", "LCD_RST"), ("LCD_EN", "output", "R", "LCD_EN"),\n'
        '         ("LCD_SCK", "output", "R", "LCD_SCK"), ("LCD_MOSI", "output", "R", "LCD_MOSI"),\n'
        '         ("TP_SDA", "bidirectional", "R", "TP_SDA"), ("TP_SCL", "bidirectional", "R", "TP_SCL"),\n'
        '         ("TP_INT", "input", "R", "TP_INT"), ("TP_RST", "output", "R", "TP_RST"),\n'
        '     ]),\n    '
    )
    text = text[:mc_start] + new_mc + text[mc_end:]

    if '("FrontPanel",' not in text:
        # AmpBankRelay の末尾（CHILD_SHEETS 最後）に FrontPanel を足す
        relay_tail = (
            '         ("AMP_SEL_L", "output", "R", "AMP_SEL_L"), '
            '("AMP_SEL_R", "output", "R", "AMP_SEL_R"),\n'
            '     ]),\n]'
        )
        idx = text.rfind(relay_tail)
        if idx < 0:
            raise SystemExit("CHILD_SHEETS 末尾（AmpBankRelay）が見つからない")
        end = idx + len(relay_tail)
        fp_entry = (
            '         ("AMP_SEL_L", "output", "R", "AMP_SEL_L"), '
            '("AMP_SEL_R", "output", "R", "AMP_SEL_R"),\n'
            '     ]),\n'
            '    ("FrontPanel", "FrontPanel.kicad_sch",\n'
            '     "b2000020-0020-4020-8020-000000000020", (470.0, 160.0), (55.88, 76.2), [\n'
            + ",\n".join(
                f'         ("{n}", "{s}", "L", "{n}")' for n, s in FP_PINS
            )
            + "\n     ]),\n]"
        )
        text = text[:idx] + fp_entry + text[end:]

    # REPLACED_SHEETS に FrontPanel を足す（再実行で親に二重に置かない）
    if '"FrontPanel"' not in text.split("REPLACED_SHEETS", 1)[1][:400]:
        text = text.replace(
            '"MeasureControl", "AmpBankSwitch", "AmpBankRelay")',
            '"MeasureControl", "AmpBankSwitch", "AmpBankRelay", "FrontPanel")',
            1,
        )

    # rewrite_child_instance_paths 対象に FrontPanel を足す（将来用）
    if 'for fname in ("MeasureControl.kicad_sch",):' in text:
        text = text.replace(
            'for fname in ("MeasureControl.kicad_sch",):',
            'for fname in ("MeasureControl.kicad_sch", "FrontPanel.kicad_sch"):',
            1,
        )

    path.write_text(text, encoding="utf-8", newline="\n")
    print("更新: build_motherboard.py CHILD_SHEETS")


def _patch_pcb_paths() -> None:
    pcb = ROOT / "AudioV2Case.kicad_pcb"
    text = pcb.read_text(encoding="utf-8")
    old_fp = f"/{MC_INST}/{FP_INST}/"
    new_fp = f"/{FP_INST}/"
    n1 = text.count(old_fp)
    text = text.replace(old_fp, new_fp)
    text = text.replace('sheetname "/MeasureControl/FrontPanel/"', 'sheetname "/FrontPanel/"')
    # J_PNL1601 / J_PNL_A1601: MC 配下 → ルート
    # path "/MC_INST/<symuuid>" → path "/<symuuid>" は危険なので参照で絞る
    for ref in ("J_PNL1601", "J_PNL_A1601"):
        # footprint ブロックを粗く探して path を直す
        pattern = (
            rf'(\(footprint [\s\S]*?\(property "Reference" "{ref}"[\s\S]*?'
            rf'\(path ")/{re.escape(MC_INST)}/([^"]+)(")'
        )
        text2, n = re.subn(pattern, rf'\1/\2\3', text, count=1)
        if n:
            text = text2
            print(f"PCB: {ref} path → ルート")
        # sheetname if any
        text = text.replace(
            f'(property "Reference" "{ref}"',
            f'(property "Reference" "{ref}"',
            1,
        )
    pcb.write_text(text, encoding="utf-8", newline="\n")
    print(f"PCB: FrontPanel path 置換 {n1} 箇所")


def _patch_pro() -> None:
    # sheets リストの順序は UUID 列挙なので FrontPanel は既にある。階層は KiCad が直す。
    pass


def main() -> int:
    saved_new, sch_helpers.new_uid = sch_helpers.new_uid, uid
    saved_sc, scaffold.uid = scaffold.uid, uid
    try:
        _update_child_sheets_code()
        # CHILD_SHEETS 更新後に import し直す
        import importlib
        import build_motherboard as bm
        importlib.reload(bm)

        mc = sch_import.load(ROOT / "MeasureControl.kicad_sch")
        fp = sch_import.load(ROOT / "FrontPanel.kicad_sch")
        case = sch_import.load(ROOT / "AudioV2Case.kicad_sch")

        _drop_fp_sheet_and_connectors(mc)
        _drop_mc_passthrough_hier(mc)
        _add_mc_new_hier(mc)

        _clean_frontpanel(fp)

        _rebuild_root_sheets(case)
        _place_root_connectors(case)

        # J_PNL value on mother
        for e in case.elements:
            if e.ref == "J_PNL1601":
                e.text = e.text.replace(
                    "MeasureControl ↔ FrontPanel", "Mother ↔ FrontPanel")

        sch_helpers.write_sch(ROOT / "MeasureControl.kicad_sch", mc.render())
        sch_helpers.write_sch(ROOT / "FrontPanel.kicad_sch", fp.render())
        sch_helpers.write_sch(ROOT / "AudioV2Case.kicad_sch", case.render())

        sch_helpers.canonicalize_sch([
            ROOT / "MeasureControl.kicad_sch",
            ROOT / "FrontPanel.kicad_sch",
            ROOT / "AudioV2Case.kicad_sch",
        ])
        _patch_pcb_paths()
        print("完了: FrontPanel を母板直下へ")
        return 0
    finally:
        sch_helpers.new_uid = saved_new
        scaffold.uid = saved_sc


if __name__ == "__main__":
    raise SystemExit(main())
