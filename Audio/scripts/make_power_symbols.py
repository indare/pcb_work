#!/usr/bin/env python3
"""MeasurementADC の電源レール用パワーシンボルを Extras ライブラリに作る。

このシートのレールはすべてローカルラベルなので、`(power local)` を使う。
`global` にすると階層をまたいで同名ネットと勝手に繋がるため使わない。

形状は KiCad 標準 power ライブラリから借りている。GND が 4 系統あるので、
文字を読まなくても見分けが付くよう系統ごとに違う図形を割り当てる。
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXTRAS = ROOT / "MeasurementADC_Extras.kicad_sym"

ARROW = """\t\t\t(polyline
\t\t\t\t(pts
\t\t\t\t\t(xy -0.762 1.27) (xy 0 2.54)
\t\t\t\t)
\t\t\t\t(stroke
\t\t\t\t\t(width 0)
\t\t\t\t\t(type default)
\t\t\t\t)
\t\t\t\t(fill
\t\t\t\t\t(type none)
\t\t\t\t)
\t\t\t)
\t\t\t(polyline
\t\t\t\t(pts
\t\t\t\t\t(xy 0 2.54) (xy 0.762 1.27)
\t\t\t\t)
\t\t\t\t(stroke
\t\t\t\t\t(width 0)
\t\t\t\t\t(type default)
\t\t\t\t)
\t\t\t\t(fill
\t\t\t\t\t(type none)
\t\t\t\t)
\t\t\t)
\t\t\t(polyline
\t\t\t\t(pts
\t\t\t\t\t(xy 0 0) (xy 0 2.54)
\t\t\t\t)
\t\t\t\t(stroke
\t\t\t\t\t(width 0)
\t\t\t\t\t(type default)
\t\t\t\t)
\t\t\t\t(fill
\t\t\t\t\t(type none)
\t\t\t\t)
\t\t\t)"""

NEG = """\t\t\t(polyline
\t\t\t\t(pts
\t\t\t\t\t(xy 0 0) (xy 0 1.27) (xy 0.762 1.27) (xy 0 2.54) (xy -0.762 1.27) (xy 0 1.27)
\t\t\t\t)
\t\t\t\t(stroke
\t\t\t\t\t(width 0)
\t\t\t\t\t(type default)
\t\t\t\t)
\t\t\t\t(fill
\t\t\t\t\t(type none)
\t\t\t\t)
\t\t\t)"""

TRI = """\t\t\t(polyline
\t\t\t\t(pts
\t\t\t\t\t(xy 0 0) (xy 0 -1.27) (xy 1.27 -1.27) (xy 0 -2.54) (xy -1.27 -1.27) (xy 0 -1.27)
\t\t\t\t)
\t\t\t\t(stroke
\t\t\t\t\t(width 0)
\t\t\t\t\t(type default)
\t\t\t\t)
\t\t\t\t(fill
\t\t\t\t\t(type none)
\t\t\t\t)
\t\t\t)"""

BAR = """\t\t\t(rectangle
\t\t\t\t(start -1.27 -1.524)
\t\t\t\t(end 1.27 -2.032)
\t\t\t\t(stroke
\t\t\t\t\t(width 0.254)
\t\t\t\t\t(type default)
\t\t\t\t)
\t\t\t\t(fill
\t\t\t\t\t(type outline)
\t\t\t\t)
\t\t\t)
\t\t\t(polyline
\t\t\t\t(pts
\t\t\t\t\t(xy 0 0) (xy 0 -1.524)
\t\t\t\t)
\t\t\t\t(stroke
\t\t\t\t\t(width 0)
\t\t\t\t\t(type default)
\t\t\t\t)
\t\t\t\t(fill
\t\t\t\t\t(type none)
\t\t\t\t)
\t\t\t)"""

REF = """\t\t\t(polyline
\t\t\t\t(pts
\t\t\t\t\t(xy -0.635 -1.905) (xy 0.635 -1.905)
\t\t\t\t)
\t\t\t\t(stroke
\t\t\t\t\t(width 0)
\t\t\t\t\t(type default)
\t\t\t\t)
\t\t\t\t(fill
\t\t\t\t\t(type none)
\t\t\t\t)
\t\t\t)
\t\t\t(polyline
\t\t\t\t(pts
\t\t\t\t\t(xy -0.127 -2.54) (xy 0.127 -2.54)
\t\t\t\t)
\t\t\t\t(stroke
\t\t\t\t\t(width 0)
\t\t\t\t\t(type default)
\t\t\t\t)
\t\t\t\t(fill
\t\t\t\t\t(type none)
\t\t\t\t)
\t\t\t)
\t\t\t(polyline
\t\t\t\t(pts
\t\t\t\t\t(xy 0 -1.27) (xy 0 0)
\t\t\t\t)
\t\t\t\t(stroke
\t\t\t\t\t(width 0)
\t\t\t\t\t(type default)
\t\t\t\t)
\t\t\t\t(fill
\t\t\t\t\t(type none)
\t\t\t\t)
\t\t\t)
\t\t\t(polyline
\t\t\t\t(pts
\t\t\t\t\t(xy 1.27 -1.27) (xy -1.27 -1.27)
\t\t\t\t)
\t\t\t\t(stroke
\t\t\t\t\t(width 0)
\t\t\t\t\t(type default)
\t\t\t\t)
\t\t\t\t(fill
\t\t\t\t\t(type none)
\t\t\t\t)
\t\t\t)"""

HATCH = """\t\t\t(polyline
\t\t\t\t(pts
\t\t\t\t\t(xy -1.016 -1.27) (xy -1.27 -2.032)
\t\t\t\t)
\t\t\t\t(stroke
\t\t\t\t\t(width 0.2032)
\t\t\t\t\t(type default)
\t\t\t\t)
\t\t\t\t(fill
\t\t\t\t\t(type none)
\t\t\t\t)
\t\t\t)
\t\t\t(polyline
\t\t\t\t(pts
\t\t\t\t\t(xy -0.508 -1.27) (xy -0.762 -2.032)
\t\t\t\t)
\t\t\t\t(stroke
\t\t\t\t\t(width 0.2032)
\t\t\t\t\t(type default)
\t\t\t\t)
\t\t\t\t(fill
\t\t\t\t\t(type none)
\t\t\t\t)
\t\t\t)
\t\t\t(polyline
\t\t\t\t(pts
\t\t\t\t\t(xy 0 -1.27) (xy 0 0)
\t\t\t\t)
\t\t\t\t(stroke
\t\t\t\t\t(width 0)
\t\t\t\t\t(type default)
\t\t\t\t)
\t\t\t\t(fill
\t\t\t\t\t(type none)
\t\t\t\t)
\t\t\t)
\t\t\t(polyline
\t\t\t\t(pts
\t\t\t\t\t(xy 0 -1.27) (xy -0.254 -2.032)
\t\t\t\t)
\t\t\t\t(stroke
\t\t\t\t\t(width 0.2032)
\t\t\t\t\t(type default)
\t\t\t\t)
\t\t\t\t(fill
\t\t\t\t\t(type none)
\t\t\t\t)
\t\t\t)
\t\t\t(polyline
\t\t\t\t(pts
\t\t\t\t\t(xy 0.508 -1.27) (xy 0.254 -2.032)
\t\t\t\t)
\t\t\t\t(stroke
\t\t\t\t\t(width 0.2032)
\t\t\t\t\t(type default)
\t\t\t\t)
\t\t\t\t(fill
\t\t\t\t\t(type none)
\t\t\t\t)
\t\t\t)
\t\t\t(polyline
\t\t\t\t(pts
\t\t\t\t\t(xy 1.016 -1.27) (xy -1.016 -1.27)
\t\t\t\t)
\t\t\t\t(stroke
\t\t\t\t\t(width 0.2032)
\t\t\t\t\t(type default)
\t\t\t\t)
\t\t\t\t(fill
\t\t\t\t\t(type none)
\t\t\t\t)
\t\t\t)
\t\t\t(polyline
\t\t\t\t(pts
\t\t\t\t\t(xy 1.016 -1.27) (xy 0.762 -2.032)
\t\t\t\t)
\t\t\t\t(stroke
\t\t\t\t\t(width 0.2032)
\t\t\t\t\t(type default)
\t\t\t\t)
\t\t\t\t(fill
\t\t\t\t\t(type none)
\t\t\t\t)
\t\t\t)"""

# name -> (図形, ピン角度, Value の y, 説明)
UP, DOWN = 90, 270
RAILS = {
    "+3V3_A":     (ARROW, UP,   3.556,  "アナログ側 3.3V（U706 LT1763-3.3 出力）"),
    "+5V_A":      (ARROW, UP,   3.556,  "アナログ側 5V（U707 LT1763-5 出力）"),
    "+5V_D":      (ARROW, UP,   3.556,  "デジタル側 5V（U704 BP5293-50 出力）"),
    "PICO_3V3":   (ARROW, UP,   3.556,  "Pico2 内蔵 LDO の 3V3OUT"),
    "LCD_VCC":    (ARROW, UP,   3.556,  "U708 XC8107 が切る LCD 電源"),
    "VSYS":       (ARROW, UP,   3.556,  "Pico2 VSYS（D701 ショットキ経由）"),
    "ADC_V_IN":   (ARROW, UP,   3.556,  "計測モジュール入口の未整流入力"),
    "+15V_A":     (ARROW, UP,   3.556,  "アナログ FE 正電源"),
    "-15V_A":     (NEG,   UP,   3.556,  "アナログ FE 負電源"),
    "A_GND":      (TRI,   DOWN, -3.81,  "アナログ GND（三角）"),
    "ADC_GND":    (HATCH, DOWN, -3.81,  "ADC / レギュレータ GND（ハッチ）"),
    "D_GND":      (BAR,   DOWN, -3.81,  "デジタル GND（太バー）"),
    "ADC_GND_IN": (REF,   DOWN, -3.81,  "計測モジュール入口 GND（基準線）"),
}


def prop(name, value, x, y, hide):
    h = "\t\t\t(hide yes)\n" if hide else ""
    v = value.replace('"', '\\"')
    return (
        f'\t\t(property "{name}" "{v}"\n'
        f"\t\t\t(at {x} {y} 0)\n"
        "\t\t\t(show_name no)\n"
        "\t\t\t(do_not_autoplace no)\n"
        f"{h}"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n"
        "\t\t)\n"
    )


def build(name, shape, pin_angle, value_y, desc):
    ref_y = -3.81 if pin_angle == UP else -6.35
    return (
        f'\t(symbol "{name}"\n'
        "\t\t(power local)\n"
        "\t\t(pin_numbers\n\t\t\t(hide yes)\n\t\t)\n"
        "\t\t(pin_names\n\t\t\t(offset 0)\n\t\t\t(hide yes)\n\t\t)\n"
        "\t\t(exclude_from_sim no)\n"
        "\t\t(in_bom no)\n"
        "\t\t(on_board yes)\n"
        "\t\t(in_pos_files no)\n"
        "\t\t(duplicate_pin_numbers_are_jumpers no)\n"
        + prop("Reference", "#PWR", 0, ref_y, True)
        + prop("Value", name, 0, value_y, False)
        + prop("Footprint", "", 0, 0, True)
        + prop("Datasheet", "", 0, 0, True)
        + prop("Description", desc, 0, 0, True)
        + prop("ki_keywords", "power local rail", 0, 0, True)
        + f'\t\t(symbol "{name}_0_1"\n{shape}\n\t\t)\n'
        + f'\t\t(symbol "{name}_1_1"\n'
        "\t\t\t(pin power_in line\n"
        f"\t\t\t\t(at 0 0 {pin_angle})\n"
        "\t\t\t\t(length 0)\n"
        '\t\t\t\t(name ""\n\t\t\t\t\t(effects\n\t\t\t\t\t\t(font\n\t\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t\t)\n\t\t\t\t\t)\n\t\t\t\t)\n'
        '\t\t\t\t(number "1"\n\t\t\t\t\t(effects\n\t\t\t\t\t\t(font\n\t\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t\t)\n\t\t\t\t\t)\n\t\t\t\t)\n'
        "\t\t\t)\n\t\t)\n"
        "\t\t(embedded_fonts no)\n"
        "\t)\n"
    )


def main():
    text = EXTRAS.read_text()
    added = []
    for name, (shape, ang, vy, desc) in RAILS.items():
        if f'\t(symbol "{name}"\n' in text:
            continue
        text = text.rstrip()[:-1].rstrip("\n") + "\n" + build(name, shape, ang, vy, desc) + ")\n"
        added.append(name)
    EXTRAS.write_text(text)
    print("追加:", ", ".join(added) if added else "なし（すでに存在）")


if __name__ == "__main__":
    main()
