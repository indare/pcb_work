#!/usr/bin/env python3
"""MeasureControl から FrontPanel 子シートへ UI／表示島を切り出す（一度きり）。

前提（計画どおり）:
  - Pico は MeasureControl に残す
  - FrontPanel は MeasureControl の子（build_motherboard は触らない）
  - I2C プルアップ R1653/R1654 は MC に残す
  - 両側に Conn_02x10（J_PNL1601 / J_PNL1602）

冪等ではない。やり直すなら MeasureControl を git checkout してから再実行。
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
from build_motherboard import _merge_lib_symbols  # noqa: E402
from generate_kicad_scaffold import PARENT, PROJECT, hier_label, sheet_block  # noqa: E402
from sch_helpers import embed_lib_symbols, symbol_inst_v10  # noqa: E402

MC_INST = "43e41fda-fe26-43e3-950a-c017f3070bbf"
FP_INST = "b2000020-0020-4020-8020-000000000020"
FP_FILE_UUID = "b2000021-0021-4021-8021-000000000021"
_NS = uuid.UUID("b2000022-0022-4022-8022-000000000022")
_seq = 0

MC_PATH = f"/{PARENT}/{MC_INST}"
FP_PATH = f"/{PARENT}/{MC_INST}/{FP_INST}"

# 移す部品（計画 + U1609 島のデカップ／PWR_FLAG／LCD_VCC バルク）
MOVE_REFS = {
    "ENC1601", "ENC1602", "ENC1603",
    "U1610", "C1650",
    "D1610", "D1611", "R1651", "R1652",
    "R1661", "R1662",
    "J_OLED1601",
    "LCDDisplay1601",
    "U1609", "R1620", "C1631", "C1633", "C1630", "C1629",
    "#FLG0702",
}

# 平行移動しない（元座標のまま。オフグリッド／負座標を避ける）
DX, DY = 0.0, 0.0

# 界面ネット（コネクタ 2x10）
PNL_NETS: dict[str, str | None] = {
    "1": "3V3",
    "2": "+5V_D",
    "3": "D_GND",
    "4": "D_GND",
    "5": "I2C_SDA",
    "6": "I2C_SCL",
    "7": "ENC_INTA",
    "8": "ENC_INTB",
    "9": "LCD_CS",
    "10": "LCD_DC",
    "11": "LCD_RST",
    "12": "LCD_EN",
    "13": "LCD_SCK",
    "14": "LCD_MOSI",
    "15": "TP_SDA",
    "16": "TP_SCL",
    "17": "TP_INT",
    "18": "TP_RST",
    "19": None,  # NC
    "20": None,
}

# 子シート階層ラベル（形は子から見た向き）
HIER_PINS: list[tuple[str, str]] = [
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
]

CONN_LIB = "Connector_Generic:Conn_02x10_Odd_Even"
CONN_FP = "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical"


def uid() -> str:
    global _seq
    _seq += 1
    return str(uuid.uuid5(_NS, f"fp/{_seq}"))


def _patch_measurement_adc_lib() -> None:
    """カスタム lib を sch_edit が読めるようにする。"""
    extras = (ROOT.parent / "Audio" / "MeasurementADC_Extras.kicad_sym")
    orig = sch_helpers._read_symbol_text

    def _read(lib: str, name: str) -> str:
        if lib == "MeasurementADC_Extras":
            return extras.read_text(encoding="utf-8")
        return orig(lib, name)

    sch_helpers._read_symbol_text = _read  # type: ignore[assignment]
    sch_edit._lib_cache.clear()


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


def _rewrite_path(text: str, old: str, new: str) -> str:
    return text.replace(old, new)


def _tips_of(el: sch_import.Element) -> set[tuple[float, float]]:
    try:
        return {_key(t) for t in sch_edit.symbol_tips(el)}
    except Exception as exc:  # noqa: BLE001
        print(f"  warn: tips failed for {el.ref}: {exc}")
        return set()


def _extract_lib_names(moved: list[sch_import.Element]) -> list[str]:
    names: list[str] = []
    for e in moved:
        m = re.search(r'\(lib_id "([^"]+)"\)', e.text)
        if m and m.group(1) not in names:
            names.append(m.group(1))
    return names


def _filter_lib_symbols(header_blocks: list[str], keep: set[str]) -> str:
    """MC の lib_symbols から keep に含まれるシンボルだけ残す。"""
    blocks = [h for h in header_blocks if h.lstrip().startswith("(lib_symbols")]
    if not blocks:
        return embed_lib_symbols(sorted(keep))
    src = blocks[0]
    # 各 (symbol "Lib:Name" ...) を抽出
    kept: list[str] = []
    for m in re.finditer(r'\n(\t+)\(symbol "([^"]+)"', src):
        full = m.group(2)
        if full not in keep:
            continue
        start = m.start(1)  # tab before (
        # find matching close from the '(' of symbol
        paren = src.find("(", start)
        depth = 0
        i = paren
        while i < len(src):
            if src[i] == "(":
                depth += 1
            elif src[i] == ")":
                depth -= 1
                if depth == 0:
                    kept.append(src[paren : i + 1])
                    break
            i += 1
    body = "\n".join("\t\t" + k if not k.startswith("\t") else k for k in kept)
    # normalize: each symbol should start with two tabs inside lib_symbols
    parts = []
    for k in kept:
        if not k.startswith("\t\t"):
            parts.append("\t\t" + k.lstrip())
        else:
            parts.append(k)
    return "\n\t(lib_symbols\n" + "\n".join(parts) + "\n\t)\n"


def build() -> None:
    _patch_measurement_adc_lib()
    saved_new, sch_helpers.new_uid = sch_helpers.new_uid, uid
    saved_sc, scaffold.uid = scaffold.uid, uid
    try:
        mc = sch_import.load(ROOT / "MeasureControl.kicad_sch")

        move_syms = [e for e in mc.elements if e.kind == "symbol" and e.ref in MOVE_REFS]
        found = {e.ref for e in move_syms}
        missing = MOVE_REFS - found
        if missing:
            raise SystemExit(f"MeasureControl に無い参照: {sorted(missing)}")

        tip_set: set[tuple[float, float]] = set()
        for e in move_syms:
            tip_set |= _tips_of(e)

        # LCD 左列の短いスタブ端（ラベル側 194.31）も tip 扱いに含める
        for e in mc.elements:
            if e.kind != "wire":
                continue
            cs = e.coords()
            if len(cs) == 2 and any(_key(c) in tip_set for c in cs):
                for c in cs:
                    tip_set.add(_key(c))

        # U1609 島のワイヤ／ジャンクション（bbox 内に閉じている）
        u_pts = [e.at for e in move_syms if e.ref in {
            "U1609", "R1620", "C1631", "C1633", "C1630", "C1629", "#FLG0702"} and e.at]
        ux = [p[0] for p in u_pts]
        uy = [p[1] for p in u_pts]
        ubox = (min(ux) - 15, min(uy) - 15, max(ux) + 15, max(uy) + 15)

        def in_ubox(p: tuple[float, float] | None) -> bool:
            return bool(p) and ubox[0] <= p[0] <= ubox[2] and ubox[1] <= p[1] <= ubox[3]

        move_extra: list[sch_import.Element] = []
        remain: list[sch_import.Element] = []
        for e in mc.elements:
            if e.kind == "symbol" and e.ref in MOVE_REFS:
                move_extra.append(e)
                continue
            if e.kind in ("label", "no_connect") and e.at and _key(e.at) in tip_set:
                move_extra.append(e)
                continue
            if e.kind == "wire":
                cs = e.coords()
                if cs and all(_key(c) in tip_set or in_ubox(c) for c in cs) and (
                    any(_key(c) in tip_set for c in cs) or all(in_ubox(c) for c in cs)
                ):
                    move_extra.append(e)
                    continue
            if e.kind == "junction" and e.at and (in_ubox(e.at) or _key(e.at) in tip_set):
                move_extra.append(e)
                continue
            remain.append(e)

        # パス書き換え＋平行移動
        moved: list[sch_import.Element] = []
        for e in move_extra:
            t = _rewrite_path(e.text, MC_PATH, FP_PATH)
            ne = sch_import.Element(e.kind, t, e.ref, e.name, e.at)
            moved.append(ne.translated(DX, DY))

        lib_ids = set(_extract_lib_names([e for e in moved if e.kind == "symbol"]))
        lib_ids.add(CONN_LIB)
        lib_ids.add("power:PWR_FLAG")
        # embed missing standard ones; merge with filtered MC libs for custom
        mc_lib_keep = {lid for lid in lib_ids if lid.startswith("MeasurementADC")}
        filtered = _filter_lib_symbols(mc.header, mc_lib_keep) if mc_lib_keep else ""
        std = [lid for lid in sorted(lib_ids) if not lid.startswith("MeasurementADC")]
        lib_block = _merge_lib_symbols([filtered, embed_lib_symbols(std)] if filtered else [embed_lib_symbols(std)])

        fp_els: list[sch_import.Element] = list(moved)

        # J_PNL1602（ピン先に hierarchical_label — 孤立 hier は ERC label_dangling）
        cx, cy = 500.38, 340.36
        fp_els.append(sch_import.Element(
            "symbol",
            symbol_inst_v10(CONN_LIB, "J_PNL1602", "FrontPanel ↔ MeasureControl",
                            cx, cy, 0, FP_PATH, footprint=CONN_FP),
            "J_PNL1602", None, (cx, cy)))
        tips = dict(zip(sch_edit.lib_pins(CONN_LIB).keys(),
                        sch_edit.symbol_tips(fp_els[-1])))
        shape = {n: t for n, t in HIER_PINS}
        for num, net in PNL_NETS.items():
            tx, ty = tips[num]
            if net is None:
                fp_els.append(sch_import.Element("no_connect", _nc(tx, ty), None, None, (tx, ty)))
            else:
                rot = 180 if tx < cx else 0
                fp_els.append(sch_import.Element(
                    "hierarchical_label",
                    hier_label(net, shape[net], tx, ty, rot),
                    None, net, (tx, ty)))

        fp_header = [
            "\n\t(version 20260306)\n",
            '\t(generator "eeschema")\n',
            '\t(generator_version "10.0")\n',
            f'\t(uuid "{FP_FILE_UUID}")\n',
            '\t(paper "A2")\n',
            '\t(title_block\n\t\t(title "FrontPanel")\n\t)\n',
            lib_block if lib_block.startswith("\n") else "\n" + lib_block,
            "\t(embedded_fonts no)\n",
        ]
        fp_sheet = sch_import.Sheet(path=ROOT / "FrontPanel.kicad_sch",
                                    header=fp_header, elements=fp_els, footer=[])
        sch_helpers.write_sch(fp_sheet.path, fp_sheet.render())
        print(f"書き出し: FrontPanel.kicad_sch  elements={len(fp_els)}")

        # --- MeasureControl 側 ---
        mc.elements = remain

        # FrontPanel シート枠
        sx, sy, sw, sh = 400.0, 100.0, 55.88, 55.88
        lefts = [(n, t) for n, t in HIER_PINS]
        blk_pins = []
        for i, (pn, kind) in enumerate(lefts):
            py = sy + 2.54 + i * 2.54
            blk_pins.append((pn, kind, sx, py, 180))
            mc.elements.append(sch_import.Element(
                "label", _label(pn, sx, py, left=True), None, pn, (sx, py)))
        need = sy + 2.54 + (len(lefts) - 1) * 2.54
        if need > sy + sh:
            sh = need - sy + 2.54
        mc.elements.append(sch_import.Element(
            "sheet",
            sheet_block(FP_INST, "FrontPanel", "FrontPanel.kicad_sch",
                        sx, sy, sw, sh, blk_pins, "2",
                        parent_path=MC_PATH),
            None, "FrontPanel", (sx, sy)))

        # J_PNL1601（Pico 表示ピン付近）
        jx, jy = 320.0, 160.0
        mc.elements.append(sch_import.Element(
            "symbol",
            symbol_inst_v10(CONN_LIB, "J_PNL1601", "MeasureControl ↔ FrontPanel",
                            jx, jy, 0, MC_PATH, footprint=CONN_FP),
            "J_PNL1601", None, (jx, jy)))
        tips = dict(zip(sch_edit.lib_pins(CONN_LIB).keys(),
                        sch_edit.symbol_tips(mc.elements[-1])))
        for num, net in PNL_NETS.items():
            tx, ty = tips[num]
            if net is None:
                mc.elements.append(sch_import.Element(
                    "no_connect", _nc(tx, ty), None, None, (tx, ty)))
            else:
                left = tx < jx
                mc.elements.append(sch_import.Element(
                    "label", _label(net, tx, ty, left), None, net, (tx, ty)))

        # lib_symbols にコネクタを足す
        mc_libs = [h for h in mc.header if h.lstrip().startswith("(lib_symbols")]
        merged = _merge_lib_symbols(mc_libs + [embed_lib_symbols([CONN_LIB])])
        new_header = []
        replaced = False
        for h in mc.header:
            if h.lstrip().startswith("(lib_symbols"):
                if not replaced:
                    new_header.append(merged if merged.startswith("\n") else "\n" + merged)
                    replaced = True
                # skip old
            else:
                new_header.append(h)
        mc.header = new_header

        sch_helpers.write_sch(ROOT / "MeasureControl.kicad_sch", mc.render())
        print(f"更新: MeasureControl.kicad_sch  remain={len(remain)} +sheet/conn")

        sch_helpers.canonicalize_sch([
            ROOT / "FrontPanel.kicad_sch",
            ROOT / "MeasureControl.kicad_sch",
        ])
        print("正準化完了")
    finally:
        sch_helpers.new_uid = saved_new
        scaffold.uid = saved_sc


if __name__ == "__main__":
    build()
