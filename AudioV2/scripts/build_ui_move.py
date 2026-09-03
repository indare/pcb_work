#!/usr/bin/env python3
"""B4'-1 — UI と I2C マスタを計測/制御基板へ移す（D27 の実装）。

`U401`（操作 Pico）を廃止し、その配下にあったものを `MeasureControl` へ移す。
GPIO は 14 要求 / 11 空きで入らないので、**`MCP23017`(0x22) を1個足して
エンコーダ3個と LED 2個をそこへ逃がす**（D27）。

⚠ 系の `3V3` を駆動していたのは `U401.36` だけ。消すと供給源が無くなるので
  **計測 Pico の `PICO_3V3` を系の `3V3` にする**。`+3V3_A`（LT1763）は
  `PCM1804`・水晶・監視IC の清浄レールなので触らない（D27）。

⚠ NetTie は足さない（D28）。`A_GND`↔`D_GND` の結合は `MeasureControl` の中に
  既に1本ある（`NT1601`→`U1604`→`NT1602`）ので、`D_GND` を統合しても閉路はできない。

一度きりの移行スクリプト。冪等ではない。やり直すなら該当シートを git checkout すること。
"""

from __future__ import annotations

import argparse
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
from generate_kicad_scaffold import PARENT  # noqa: E402
from sch_helpers import embed_lib_symbols, symbol_inst_v10  # noqa: E402

MC_INST = "43e41fda-fe26-43e3-950a-c017f3070bbf"     # 親での MeasureControl シート
CTRL_INST = "a1000006-0006-4006-8006-000000000006"
_NS = uuid.UUID("b2000015-0015-4015-8015-000000000015")
_seq = 0


def uid() -> str:
    global _seq
    _seq += 1
    return str(uuid.uuid5(_NS, f"uimove/{_seq}"))


# --- ControlPanel から外すもの（UI と Pico）-----------------------------
DROP_FROM_CTRL = {
    "U401",                                  # 操作 Pico（D27）
    "ENC401", "ENC402", "ENC403",            # ロータリエンコーダ
    "D401", "D402", "R404", "R408",          # DEST 表示 LED と直列抵抗
    "J_OLED401",                             # OLED
    "R401", "R402",                          # I2C プルアップ（マスタと一緒に動く）
    "SW401", "R403", "R405", "R406", "R409",  # DEST センスラダー
}
# `+3V3` は ControlPanel が出力していたが、供給源の Pico が消えるので階層ピンごと外す
DROP_CTRL_HIER = {"+3V3"}

# --- MeasureControl に足すもの ------------------------------------------
# 0x22 = 0100_010 なので A2=0 / A1=1 / A0=0
MCP = "Interface_Expansion:MCP23017x-x-SP"
MCP_NETS = {
    "21": "ENC1_A", "22": "ENC1_B", "23": "ENC1_SW",     # GPA0-2
    "24": "ENC2_A", "25": "ENC2_B", "26": "ENC2_SW",     # GPA3-5
    "27": "ENC3_A", "28": "ENC3_B", "1": "ENC3_SW",      # GPA6-7, GPB0
    "2": "LED_DEST1", "3": "LED_DEST2",                  # GPB1-2
    "13": "I2C_SDA", "12": "I2C_SCL",
    "15": "D_GND", "16": "3V3", "17": "D_GND",           # A0=0 A1=1 A2=0 -> 0x22
    "18": "3V3", "9": "3V3", "10": "D_GND",              # ~RESET / VDD / VSS
}
MCP_NC = ["4", "5", "6", "7", "8", "11", "14", "19", "20"]

ENCODERS = [("ENC1601", "ENC_CH", 1), ("ENC1602", "ENC_VOL", 2), ("ENC1603", "ENC_TREBLE", 3)]
# 計測 Pico の空きピンに直接付けるもの
PICO_DIRECT = {"26": "I2C_SDA", "27": "I2C_SCL", "31": "DEST_ADC"}   # GPIO20/21/ADC0
PICO_3V3_TIP = (276.86, 129.54)          # A1602 pin36。ここに `3V3` を別名で乗せる
NEW_HIER = [("I2C_SDA", "bidirectional"), ("I2C_SCL", "bidirectional"),
            ("3V3", "output"), ("D_GND", "bidirectional")]


def _label(name: str, x: float, y: float, left: bool = False) -> str:
    rot, just = (180, "right") if left else (0, "left")
    return (f'\t(label "{name}"\n\t\t(at {x} {y} {rot})\n\t\t(effects\n\t\t\t(font\n'
            f'\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify {just} bottom)\n\t\t)\n'
            f'\t\t(uuid "{uid()}")\n\t)\n')


def _nc(x: float, y: float) -> str:
    return f'\t(no_connect\n\t\t(at {x} {y})\n\t\t(uuid "{uid()}")\n\t)\n'


class MC:
    """`MeasureControl` へ部品を足す。既存の手描き配線には触らず、ピン先にラベルを撒く。"""

    def __init__(self) -> None:
        self.s = sch_import.load(ROOT / "MeasureControl.kicad_sch")
        self.path = f"/{PARENT}/{MC_INST}"
        self.libs: list[str] = []

    def place(self, lib: str, ref: str, value: str, x: float, y: float,
              nets: dict[str, str], nc: list[str] | None = None, fp: str = "") -> None:
        el = sch_import.Element(
            "symbol", symbol_inst_v10(lib, ref, value, x, y, 0, self.path, footprint=fp),
            ref, None, (x, y))
        self.s.elements.append(el)
        if lib not in self.libs:
            self.libs.append(lib)
        tips = dict(zip(sch_edit.lib_pins(lib).keys(), sch_edit.symbol_tips(el)))
        for num, net in nets.items():
            tx, ty = tips[str(num)]
            self.s.elements.append(sch_import.Element(
                "label", _label(net, tx, ty, tx < x), None, net, (tx, ty)))
        for num in (nc or []):
            tx, ty = tips[str(num)]
            self.s.elements.append(sch_import.Element("no_connect", _nc(tx, ty), None, None, (tx, ty)))

    def build(self) -> str:
        saved_new, sch_helpers.new_uid = sch_helpers.new_uid, uid
        saved_sc, scaffold.uid = scaffold.uid, uid
        try:
            # ⚠ 元の MeasureControl は **y=315 / x=470 まで**使っている。
            #    要素のアンカーだけ見て y<=233.7 と誤り、既存の配線の上に重ねた（2026-09-03）。
            #    空きを測るときはワイヤの端点も入れること。
            y0 = 340.0
            self.place(MCP, "U1610", "MCP23017 (UI 0x22)", 120.0, y0, MCP_NETS, MCP_NC,
                       fp="Package_DIP:DIP-28_W7.62mm")
            self.place("Device:C", "C1650", "100nF", 170.0, y0, {"1": "3V3", "2": "D_GND"},
                       fp="Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder")
            # エンコーダ3個（パネル実装。ここは電気的な所属だけを表す）
            for i, (ref, val, n) in enumerate(ENCODERS):
                self.place("Device:RotaryEncoder_Switch", ref, val, 220.0 + i * 45.72, y0,
                           {"A": f"ENC{n}_A", "B": f"ENC{n}_B", "C": "D_GND",
                            "S1": f"ENC{n}_SW", "S2": "D_GND"},
                           fp="Rotary_Encoder:RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm")
            # DEST 表示 LED（アノード側に 1k 直列）
            for i, (dref, rref, net) in enumerate((("D1610", "R1651", "LED_DEST1"),
                                                   ("D1611", "R1652", "LED_DEST2"))):
                x = 120.0 + i * 40.64
                self.place("Device:R", rref, "1k", x, y0 + 40.64,
                           {"1": "3V3", "2": f"{net}_A"},
                           fp="Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder")
                self.place("Device:LED", dref, f"DEST {i+1}", x, y0 + 55.88,
                           {"2": f"{net}_A", "1": net},
                           fp="LED_THT:LED_D5.0mm")
            # OLED（パネル実装、I2C）
            self.place("Connector:Conn_01x04_Pin", "J_OLED1601",
                       "2.42 OLED I2C GND/3V3/SCL/SDA", 220.0, y0 + 40.64,
                       {"1": "D_GND", "2": "3V3", "3": "I2C_SCL", "4": "I2C_SDA"},
                       fp="Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical")
            # I2C プルアップ（マスタの直近へ移した）
            for i, (ref, net) in enumerate((("R1653", "I2C_SDA"), ("R1654", "I2C_SCL"))):
                self.place("Device:R", ref, "4.7k", 280.0 + i * 15.24, y0 + 40.64,
                           {"1": "3V3", "2": net},
                           fp="Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder")
            # DEST センスラダー（SW1601 は SW501/SW502 と同じ 3PDT の3極目）
            self.place("Switch:SW_SP3T", "SW1601",
                       "DEST sense (3PDT 3rd pole, same body as SW501/SW502)",
                       360.0, y0, {"1": "DEST_SENSE_PHONE", "2": "DEST_ADC",
                                   "3": "DEST_SENSE_LINE", "4": "DEST_SENSE_MUTE_NC"})
            for ref, val, hi, lo in (("R1655", "1k", "3V3", "DEST_SENSE_LINE"),
                                     ("R1656", "10k", "3V3", "DEST_ADC"),
                                     ("R1657", "10k", "DEST_ADC", "D_GND"),
                                     ("R1658", "1k", "DEST_SENSE_PHONE", "D_GND")):
                x = 360.0 + (("R1655", "R1656", "R1657", "R1658").index(ref)) * 20.32
                self.place("Device:R", ref, val, x, y0 + 40.64, {"1": hi, "2": lo},
                           fp="Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder")

            # 計測 Pico の空きピンへ直付け（GPIO20/21 = I2C、GPIO26/ADC0 = DEST_ADC）
            a = [e for e in self.s.elements if e.ref == "A1602"][0]
            lib = re.search(r'\(lib_id "([^"]+)"\)', a.text).group(1)
            tips = dict(zip(sch_edit.lib_pins(lib).keys(), sch_edit.symbol_tips(a)))
            # ⚠ 空きピンには元から no_connect が打ってある。ラベルを乗せる前に外す
            #    （残すと no_connect_connected になる）。
            used = {(round(tips[n][0], 2), round(tips[n][1], 2)) for n in PICO_DIRECT}
            self.s.elements = [e for e in self.s.elements
                               if not (e.kind == "no_connect" and e.at
                                       and (round(e.at[0], 2), round(e.at[1], 2)) in used)]
            for num, net in PICO_DIRECT.items():
                tx, ty = tips[num]
                self.s.elements.append(sch_import.Element(
                    "label", _label(net, tx, ty), None, net, (tx, ty)))
            # 系の 3V3 = PICO_3V3（別名を重ねるだけ。既存の配線は触らない）
            self.s.elements.append(sch_import.Element(
                "label", _label("3V3", *PICO_3V3_TIP), None, "3V3", PICO_3V3_TIP))

            # 増える階層ピン
            for i, (nm, shape) in enumerate(NEW_HIER):
                hx, hy = 500.0, 340.0 + i * 7.62
                self.s.elements.append(sch_import.Element(
                    "hierarchical_label", scaffold.hier_label(nm, shape, hx, hy, 0),
                    None, nm, (hx, hy)))
                self.s.elements.append(sch_import.Element(
                    "label", _label(nm, hx, hy), None, nm, (hx, hy)))
        finally:
            sch_helpers.new_uid = saved_new
            scaffold.uid = saved_sc

        for i, h in enumerate(self.s.header):
            if h.lstrip().startswith("(lib_symbols"):
                self.s.header[i] = _merge_lib_symbols([h, embed_lib_symbols(self.libs)])
                break
        return self.s.render()


def trim_control_panel() -> tuple[str, list[str]]:
    """`ControlPanel` から UI と Pico を外す。ワイヤが無いシートなので、部品と
    そのピン先のラベルを消すだけで済む。"""
    s = sch_import.load(ROOT / "ControlPanel.kicad_sch")
    tips: set[tuple[float, float]] = set()
    for e in s.elements:
        if e.kind == "symbol" and e.ref in DROP_FROM_CTRL:
            tips |= {(round(x, 2), round(y, 2)) for x, y in sch_edit.symbol_tips(e)}
    gone = sch_edit.remove_symbols(s, DROP_FROM_CTRL)
    kept, dropped_labels = [], []
    for e in s.elements:
        if e.kind in ("label", "hierarchical_label") and e.at:
            k = (round(e.at[0], 2), round(e.at[1], 2))
            if k in tips or (e.kind == "hierarchical_label" and e.name in DROP_CTRL_HIER):
                dropped_labels.append(f"{e.name}@{k}")
                continue
            if e.kind == "label" and e.name in DROP_CTRL_HIER:
                dropped_labels.append(f"{e.name}@{k}")
                continue
        kept.append(e)
    s.elements = kept
    return s.render(), gone + dropped_labels


MC_AT = (238.76, 91.44)
MC_SIZE = (26.67, 30.48)
ORIGINAL_MC_PIN_COUNT = 7   # ユーザーが親で結線済みの本数
MC_PINS = [("+15V_A", "input"), ("-15V_A", "input"),
           ("ADC_GND_IN", "input"), ("ADC_V_IN", "input"),
           ("AUDIO_L_IN", "input"), ("AUDIO_R_IN", "input"),
           ("A_GND", "bidirectional"),
           # B4'-1 で増えた分。I2C マスタと 3V3/D_GND の発生源がここへ移った
           ("I2C_SDA", "bidirectional"), ("I2C_SCL", "bidirectional"),
           ("3V3", "output"), ("D_GND", "bidirectional")]


def patch_parent() -> str:
    """親の `MeasureControl` シートを新しいピン構成へ差し替える（冪等）。"""
    from generate_kicad_scaffold import sheet_block
    s = sch_import.load(ROOT / "AudioV2Case.kicad_sch")
    drop: set[tuple[float, float]] = set()
    kept = []
    for e in s.elements:
        if e.kind == "sheet" and e.name == "MeasureControl":
            for m in re.finditer(r'\(pin "[^"]+" \w+\n\t\t\t\(at (-?[\d.]+) (-?[\d.]+)', e.text):
                drop.add((round(float(m.group(1)), 2), round(float(m.group(2)), 2)))
            continue
        kept.append(e)
    # 元のピン位置にユーザーのラベルは無い（234.95 にあってワイヤで繋がっている）ので、
    # ここで消すものは自分が前回置いたぶんだけ。
    kept = [e for e in kept if not (e.kind == "label" and e.at
                                    and (round(e.at[0], 2), round(e.at[1], 2)) in drop)]
    mx, my = MC_AT
    pins = []
    saved, scaffold.uid = scaffold.uid, uid
    try:
        for i, (nm, shape) in enumerate(MC_PINS):
            px, py = mx, my + 2.54 + i * 2.54
            pins.append((nm, shape, px, py, 180))
            # ⚠ 元からある7本はユーザーが (234.95, y) のラベル＋ワイヤで繋いである。
            #    ここで重ねてラベルを置くと同じネットに2つ名前が付き multiple_net_names になる。
            #    増えた分（I2C_SDA/I2C_SCL/3V3/D_GND）にだけ置く。
            if i >= ORIGINAL_MC_PIN_COUNT:
                kept.append(sch_import.Element("label", _label(nm, px, py, True),
                                               None, nm, (px, py)))
        kept.append(sch_import.Element(
            "sheet",
            sheet_block(MC_INST, "MeasureControl", "MeasureControl.kicad_sch",
                        mx, my, MC_SIZE[0], MC_SIZE[1], pins, "1"),
            None, "MeasureControl", (mx, my)))
    finally:
        scaffold.uid = saved
    s.elements = kept
    return s.render()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parent-only", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.parent_only:
        out = patch_parent()
        (ROOT / "AudioV2Case.kicad_sch").write_text(out, encoding="utf-8")
        print(f"書き換え: AudioV2Case.kicad_sch ({len(out)}) — MeasureControl のピンを {len(MC_PINS)} 本へ")
        return 0
    mc = MC().build()
    ctrl, removed = trim_control_panel()
    print(f"ControlPanel から外した: 部品 {len(DROP_FROM_CTRL)} / ラベル等 {len(removed)-len(DROP_FROM_CTRL)}")
    if a.dry_run:
        return 0
    (ROOT / "MeasureControl.kicad_sch").write_text(mc, encoding="utf-8")
    (ROOT / "ControlPanel.kicad_sch").write_text(ctrl, encoding="utf-8")
    print(f"書き換え: MeasureControl.kicad_sch ({len(mc)}) / ControlPanel.kicad_sch ({len(ctrl)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
