#!/usr/bin/env python3
"""Patch MeasurementADC1804_Module.kicad_sch to rev 0.3 (next-rev schematic).

Geometry note: A702 (RaspberryPi_Pico) sits at (271.78, 167.64) rot 0, so a
library pin at local (lx, ly) lands on the sheet at (271.78 + lx, 167.64 - ly).
Every coordinate below is derived from that transform, not guessed.
"""
from pathlib import Path
import re
import uuid as uuidlib

ROOT = Path("/Users/masashiarino/workspace/pcb_work")
SCH = ROOT / "Audio/MeasurementADC1804_Module.kicad_sch"
KICAD_SYMS = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols")
PATH = "/760b9589-09e7-434e-9ca2-6e4136e3b7a2/6d49c70d-b40d-4b21-ac6e-fba63bdae03e"

# Pico pins we touch, sheet coordinates
GP3 = 160.02
GP4 = 162.56
GP9 = 175.26
GP15 = 190.5
GP18 = 160.02
GP19 = 162.56
X_LEFT = 248.92
X_LEFT_LBL = 247.65
X_RIGHT = 294.64
X_RIGHT_LBL = 295.91
VSYS = (266.7, 129.54)


def uid():
    return str(uuidlib.uuid4())


def fmt(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def wire(x1, y1, x2, y2):
    return (
        "\t(wire\n\t\t(pts\n"
        f"\t\t\t(xy {fmt(x1)} {fmt(y1)}) (xy {fmt(x2)} {fmt(y2)})\n"
        "\t\t)\n\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)\n"
        f'\t\t(uuid "{uid()}")\n\t)\n'
    )


def label(name, x, y, ang, just):
    return (
        f'\t(label "{name}"\n\t\t(at {fmt(x)} {fmt(y)} {ang})\n'
        "\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n"
        f"\t\t\t(justify {just})\n\t\t)\n"
        f'\t\t(uuid "{uid()}")\n\t)\n'
    )


def nc(x, y):
    return f"\t(no_connect\n\t\t(at {fmt(x)} {fmt(y)})\n\t\t(uuid \"{uid()}\")\n\t)\n"


def junction(x, y):
    return (
        f"\t(junction\n\t\t(at {fmt(x)} {fmt(y)})\n\t\t(diameter 0)\n"
        f'\t\t(color 0 0 0 0)\n\t\t(uuid "{uid()}")\n\t)\n'
    )


def note(body, x, y):
    return (
        f'\t(text "{body}"\n\t\t(exclude_from_sim no)\n'
        f"\t\t(at {fmt(x)} {fmt(y)} 0)\n"
        "\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n"
        "\t\t\t(justify left bottom)\n\t\t)\n"
        f'\t\t(uuid "{uid()}")\n\t)\n'
    )


def symbol(lib_id, ref, value, footprint, x, y, rot, desc, pins=("1", "2"),
           ref_at=None, val_at=None, hide_value=False):
    """ref_at / val_at are (x, y, justify) so text clears the symbol body."""
    pin_block = "".join(f'\t\t(pin "{p}"\n\t\t\t(uuid "{uid()}")\n\t\t)\n' for p in pins)
    ref_at = ref_at or (x, y + 5.08, "")
    val_at = val_at or (x, y - 5.08, "")

    def prop(name, val, hide):
        h = "\t\t\t(hide yes)\n" if hide else ""
        return (
            f'\t\t(property "{name}" "{val}"\n\t\t\t(at {fmt(x)} {fmt(y)} 0)\n{h}'
            "\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n"
            "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        )

    # Property text inherits the symbol rotation, so cancel it to keep text level.
    text_ang = (360 - int(rot)) % 360

    def placed(name, val, at, hide=False):
        px, py, just = at
        j = f"\t\t\t\t(justify {just})\n" if just else ""
        h = "\t\t\t(hide yes)\n" if hide else ""
        return (
            f'\t\t(property "{name}" "{val}"\n\t\t\t(at {fmt(px)} {fmt(py)} {text_ang})\n{h}'
            "\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n"
            f"\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n{j}\t\t\t)\n\t\t)\n"
        )

    head = (
        f'\t(symbol\n\t\t(lib_id "{lib_id}")\n\t\t(at {fmt(x)} {fmt(y)} {rot})\n'
        "\t\t(unit 1)\n\t\t(body_style 1)\n\t\t(exclude_from_sim no)\n"
        "\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(in_pos_files yes)\n\t\t(dnp no)\n"
        f'\t\t(uuid "{uid()}")\n'
    )
    ref_prop = placed("Reference", ref, ref_at)
    val_prop = placed("Value", value, val_at, hide_value)
    tail = (
        f'\t\t(instances\n\t\t\t(project "AudioCase"\n\t\t\t\t(path "{PATH}"\n'
        f'\t\t\t\t\t(reference "{ref}")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n'
    )
    return (
        head
        + ref_prop
        + val_prop
        + prop("Footprint", footprint, True)
        + prop("Datasheet", "", True)
        + prop("Description", desc, True)
        + pin_block
        + tail
    )


def drop_label(text, name, x, y):
    pat = (
        r'\t\(label "' + re.escape(name) + r'"\n'
        r"\t\t\(at " + re.escape(fmt(x)) + " " + re.escape(fmt(y)) + r" \d+\)\n"
        r"\t\t\(effects\n\t\t\t\(font\n\t\t\t\t\(size 1\.27 1\.27\)\n\t\t\t\)\n"
        r"\t\t\t\(justify \w+\)\n\t\t\)\n"
        r'\t\t\(uuid "[^"]+"\)\n\t\)\n'
    )
    text, n = re.subn(pat, "", text)
    if not n:
        raise SystemExit(f"label {name} @({x},{y}) not found")
    return text


def drop_nc(text, x, y):
    pat = (
        r"\t\(no_connect\n\t\t\(at "
        + re.escape(fmt(x)) + " " + re.escape(fmt(y))
        + r'\)\n\t\t\(uuid "[^"]+"\)\n\t\)\n'
    )
    text, n = re.subn(pat, "", text)
    if n != 1:
        raise SystemExit(f"no_connect @({x},{y}) matched {n} times")
    return text


def drop_wire(text, x1, y1, x2, y2):
    pat = (
        r"\t\(wire\n\t\t\(pts\n\t\t\t\(xy "
        + re.escape(fmt(x1)) + " " + re.escape(fmt(y1)) + r"\) \(xy "
        + re.escape(fmt(x2)) + " " + re.escape(fmt(y2)) + r"\)\n"
        r"\t\t\)\n\t\t\(stroke\n\t\t\t\(width 0\)\n\t\t\t\(type default\)\n\t\t\)\n"
        r'\t\t\(uuid "[^"]+"\)\n\t\)\n'
    )
    text, n = re.subn(pat, "", text)
    if n != 1:
        raise SystemExit(f"wire ({x1},{y1})-({x2},{y2}) matched {n} times")
    return text


def insert_before(text, pattern, blob):
    m = re.search(pattern, text, re.M)
    if not m:
        raise SystemExit(f"anchor not found: {pattern}")
    return text[: m.start()] + blob + text[m.start():]


def take_lib_symbol(lib_file, name, next_name, prefix):
    src = (KICAD_SYMS / lib_file).read_text()
    start = src.find(f'\t(symbol "{name}"\n')
    end = src.find(f'\n\t(symbol "{next_name}"', start)
    if start < 0 or end < 0:
        raise SystemExit(f"{name} not found in {lib_file}")
    block = src[start:end].replace(f'\t(symbol "{name}"', f'\t(symbol "{prefix}:{name}"', 1)
    return "\n".join(("\t" + ln if ln else ln) for ln in block.splitlines()) + "\n"


def replace_once(text, old, new, what):
    if old not in text:
        raise SystemExit(f"text not found: {what}")
    return text.replace(old, new, 1)


def main():
    text = SCH.read_text()
    if '(rev "0.3")' in text:
        raise SystemExit("already rev 0.3 -- restore from git first")

    # ---------- title block / notes ----------
    text = replace_once(text, '(rev "0.2")', '(rev "0.3")', "rev")
    text = replace_once(text, '(date "2026-07-12")', '(date "2026-08-20")', "date")
    text = replace_once(
        text,
        "電源: ADC_VIN→MBC2596(6.6-6.8V)→LT1763×2(+3V3_A先行/+5V_A)。+5V_D=BP5293。"
        "U710 XC8107 LCD_EN High=ON（初号は常時ON可）",
        "電源: ADC_VIN→MBC2596→LT1763×2(+3V3_A先行/+5V_A)。+5V_D=BP5293。"
        "D701 SOD-123 ショットキ +5V_D→VSYS。U708=XC8107 LCD、U709=G33、U710=G50",
        "comment 4",
    )
    text = replace_once(
        text,
        "A3 Pico2: VSYS=+5V_D GND=D_GND | GP0=ADC_DATA GP1=ADC_BCK GP2=ADC_LRCK | "
        "GP3=LCD_SCK GP4=LCD_MOSI GP5=LCD_CS GP6=LCD_DC GP7=LCD_RST GP8=LCD_EN | "
        "GP10=TP_SDA GP11=TP_SCL GP12=TP_INT GP13=TP_RST. Wire labels to pins in EESchema.",
        "A3 Pico2 横置き: 南列 1-20 西→東 / 北列 21-40 東→西。VSYS=+5V_D via D701 ショットキ, GND=D_GND | "
        "GP0=ADC_DATA GP1=ADC_BCK GP2=ADC_LRCK | GP3/GP4=NC(旧 LCD SPI) | "
        "GP5=LCD_CS GP6=LCD_DC GP7=LCD_RST GP8=LCD_EN | GP9=MCLK_SENSE (R720 1k, 入力専用) | "
        "GP10=TP_SDA GP11=TP_SCL GP12=TP_INT GP13=TP_RST | GP15=ADC_nRST (OD, H は駆動しない) | "
        "GP18=LCD_SCK GP19=LCD_MOSI (SPI0)",
        "A3 pin table",
    )
    text = replace_once(
        text,
        "POWER/DIGITAL: ADC_VIN->U705(MBC2596 6.6-6.8V)->U706(+3V3_A) then U707(+5V_A EN=+3V3_A). "
        "U704=+5V_D. Y701 ASFL1->R718->ADC_MCLK. U708/U709 OD wire-AND->ADC_nRST (CT open≈20ms). "
        "U710 XC8107 LCD load-SW (LCD_EN High=ON); precision mode can leave LCD on.",
        "POWER/DIGITAL: ADC_VIN->U705(MBC2596 6.6-6.8V)->U706(+3V3_A) then U707(+5V_A EN=+3V3_A). "
        "U704=+5V_D; D701 Schottky +5V_D->VSYS so USB cannot backfeed +5V_D. "
        "Y701 ASFL1->R718->ADC_MCLK (TP701; R720 1k to GP9 sense). "
        "U709 G33 / U710 G50 OD wire-AND + GP15 OD -> ADC_nRST (CT 100k to VDD). "
        "U708 XC8107 LCD load-SW (LCD_EN High=ON).",
        "POWER/DIGITAL note",
    )
    text = replace_once(
        text,
        "U708=G33(+3V3_A) U709=G50(+5V_A); SENSE=rail; CT open≈20ms (0.1uF≈0.57s if fitted); "
        "OD ~RESET wire-AND+R719; VDD 0.1uF local.",
        "U709=TPS3808G33(+3V3_A) U710=TPS3808G50(+5V_A); SENSE=rail + C743/C744 4.7nF local; "
        "CT=R721/R722 100k to VDD (short delay, no pin-1 lift); OD ~RESET wire-AND+R719 + GP15 OD; "
        "VDD 0.1uF local. Larger package: next revision.",
        "supervisor note",
    )
    text = replace_once(
        text,
        "U710 XC8107AC20MR-G ロードスイッチ:",
        "U708 XC8107AC20MR-G ロードスイッチ:",
        "XC8107 note ref",
    )
    text = text.replace("U710(XC8107)", "U708(XC8107)")
    text = replace_once(
        text,
        "JP1F: ショート=H / 開放=L。本設計は 24bit I²S → FMT1=L（開放）FMT0=H（ショート）。"
        "マスタ/スレーブ・OSR・HPF はモジュールマニュアルに従う。",
        "JP1F: ショート=H / 開放=L。本設計は S/M=L, OSR2=L OSR1=H OSR0=H（ADCマスタ 48k/256fs）、"
        "24bit I²S → FMT1=L（開放）FMT0=H（ショート）。HPF はモジュールマニュアルに従う。",
        "JP1F note",
    )

    # ---------- 1. VSYS: cut +5V_D, insert D701 ----------
    text = drop_wire(text, 266.7, 127.0, 266.7, 129.54)
    text = drop_label(text, "+5V_D", 266.7, 127.0)
    power = (
        wire(266.7, 129.54, 266.7, 121.92)         # VSYS pin -> D701 K
        + label("VSYS", 266.7, 128.27, 90, "left")
        + wire(266.7, 114.3, 266.7, 111.76)        # D701 A -> +5V_D
        + label("+5V_D", 266.7, 111.76, 90, "left")
    )

    # ---------- 2. LCD SPI: GP3/GP4 -> GP18/GP19 ----------
    text = drop_label(text, "LCD_SCK", X_LEFT_LBL, GP3)
    text = drop_label(text, "LCD_MOSI", X_LEFT_LBL, GP4)
    text = drop_wire(text, X_LEFT, GP3, X_LEFT_LBL, GP3)
    text = drop_wire(text, X_LEFT, GP4, X_LEFT_LBL, GP4)
    text = drop_nc(text, X_RIGHT, GP18)
    text = drop_nc(text, X_RIGHT, GP19)
    spi = (
        nc(X_LEFT, GP3)
        + nc(X_LEFT, GP4)
        + wire(X_RIGHT, GP18, X_RIGHT_LBL, GP18)
        + label("LCD_SCK", X_RIGHT_LBL, GP18, 0, "left")
        + wire(X_RIGHT, GP19, X_RIGHT_LBL, GP19)
        + label("LCD_MOSI", X_RIGHT_LBL, GP19, 0, "left")
    )

    # ---------- 3. GP15 -> ADC_nRST, GP9 -> MCLK_SENSE, TP701 ----------
    text = drop_nc(text, X_LEFT, GP15)
    text = drop_nc(text, X_LEFT, GP9)
    jumpers = (
        wire(X_LEFT, GP15, X_LEFT_LBL, GP15)
        + label("ADC_nRST", X_LEFT_LBL, GP15, 180, "right")
        + wire(X_LEFT, GP9, X_LEFT_LBL, GP9)
        + label("MCLK_SENSE", X_LEFT_LBL, GP9, 180, "right")
    )
    # R720 hangs off the ADC_MCLK net next to Y701/R718; TP701 taps R718 pin 2.
    mclk = (
        junction(430.53, 77.47)
        + wire(430.53, 77.47, 430.53, 71.12)
        + wire(433.07, 77.47, 433.07, 86.36)
        + wire(433.07, 93.98, 433.07, 96.52)
        + label("MCLK_SENSE", 433.07, 96.52, 90, "left")
    )

    # ---------- 4. supervisors: CT 100k to VDD, SENSE caps ----------
    text = drop_nc(text, 402.59, 114.3)   # U709 CT
    text = drop_nc(text, 402.59, 144.78)  # U710 CT
    sup = (
        # U709 (G33 on +3V3_A)
        wire(391.16, 114.3, 402.59, 114.3)
        + label("CT_G33", 396.24, 114.3, 0, "left")
        + wire(383.54, 114.3, 381.0, 114.3)
        + label("+3V3_A", 381.0, 114.3, 180, "right")
        + wire(389.89, 109.22, 402.59, 109.22)
        + junction(402.59, 109.22)
        + wire(389.89, 101.6, 389.89, 99.06)
        + label("ADC_GND", 389.89, 99.06, 90, "left")
        # U710 (G50 on +5V_A)
        + wire(391.16, 144.78, 402.59, 144.78)
        + label("CT_G50", 396.24, 144.78, 0, "left")
        + wire(383.54, 144.78, 381.0, 144.78)
        + label("+5V_A", 381.0, 144.78, 180, "right")
        + wire(389.89, 139.7, 402.59, 139.7)
        + junction(402.59, 139.7)
        + wire(389.89, 132.08, 389.89, 129.54)
        + label("ADC_GND", 389.89, 129.54, 90, "left")
    )

    text = insert_before(text, r"^\t\(wire\n", power + spi + jumpers + mclk + sup)

    # ---------- 5. sheet notes ----------
    notes = (
        note(
            "電源: USB VBUS → Pico 内部ショットキ → VSYS。D701 が +5V_D への逆流を止めるので、"
            "USB だけ挿すと Pico は動き LCD は消える。VBUS(pin40) は NC。",
            171.45,
            219.71,
        )
        + note(
            "GP9=MCLK_SENSE は R720 1k 経由の入力専用。出力にすると Y701 と衝突して SCKI が化ける。",
            171.45,
            223.52,
        )
        + note(
            "GP15=ADC_nRST はオープンドレインのみ。H は駆動しない（R719 プルアップのワイヤ AND）。",
            171.45,
            227.33,
        )
    )
    text = insert_before(text, r'^\t\(text "ADC1804_F には', notes)

    # ---------- new symbols ----------
    if '(symbol "Device:D_Schottky"' not in text:
        text = insert_before(
            text,
            r'^\t\t\(symbol "BP5293_ROHM:BP5293-50"\n',
            take_lib_symbol("Device.kicad_sym", "D_Schottky", "D_Schottky_AAK", "Device"),
        )
    if '(symbol "Connector:TestPoint"' not in text:
        text = insert_before(
            text,
            r'^\t\t\(symbol "BP5293_ROHM:BP5293-50"\n',
            take_lib_symbol("Connector.kicad_sym", "TestPoint", "TestPoint_2Pole", "Connector"),
        )

    fp_r = "Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder"
    fp_c = "Capacitor_SMD:C_0603_1608Metric"
    parts = (
        symbol(
            "Device:D_Schottky", "D701", "RB160M-30", "Diode_SMD:D_SOD-123",
            266.7, 118.11, 90,
            "SOD-123 Schottky, +5V_D anode -> Pico VSYS cathode. Blocks USB backfeed into +5V_D.",
            ref_at=(262.89, 116.84, "right"), val_at=(262.89, 120.65, "right"),
        )
        + symbol(
            "Device:R", "R720", "1k", fp_r, 433.07, 90.17, 0,
            "ADC_MCLK -> GP9 sense series resistor. GP9 is input only.",
            ref_at=(436.88, 88.9, "left"), val_at=(436.88, 92.71, "left"),
        )
        + symbol(
            "Device:R", "R721", "100k", fp_r, 387.35, 114.3, 90,
            "U709 TPS3808G33 CT to VDD: shortest reset delay, replaces the pin-1 lift.",
            ref_at=(387.35, 111.76, ""), val_at=(387.35, 118.11, ""),
        )
        + symbol(
            "Device:R", "R722", "100k", fp_r, 387.35, 144.78, 90,
            "U710 TPS3808G50 CT to VDD: shortest reset delay, replaces the pin-1 lift.",
            ref_at=(387.35, 142.24, ""), val_at=(387.35, 148.59, ""),
        )
        + symbol(
            "Device:C", "C743", "4.7nF", fp_c, 389.89, 105.41, 0,
            "U709 SENSE local decoupling (1-10nF), place at the pin.",
            ref_at=(386.08, 104.14, "right"), val_at=(386.08, 107.95, "right"),
        )
        + symbol(
            "Device:C", "C744", "4.7nF", fp_c, 389.89, 135.89, 0,
            "U710 SENSE local decoupling (1-10nF), place at the pin.",
            ref_at=(386.08, 134.62, "right"), val_at=(386.08, 138.43, "right"),
        )
        + symbol(
            "Connector:TestPoint", "TP701", "ADC_MCLK", "TestPoint:TestPoint_Pad_D1.5mm",
            430.53, 71.12, 0, "ADC_MCLK probe pad after R718.", pins=("1",),
            ref_at=(433.07, 68.58, "left"), val_at=(433.07, 66.04, "left"),
            hide_value=True,
        )
    )
    text = text.rstrip()[:-1] + parts + ")\n"

    # ---------- sanity ----------
    bp = text.find('(symbol "BP5293-50_0_1"')
    if "DC/DC" not in text[bp: bp + 600]:
        raise SystemExit("lib_symbols corrupted: BP5293 graphic lost")

    SCH.write_text(text)
    for ref in ("D701", "R720", "R721", "R722", "C743", "C744", "TP701"):
        assert text.count(f'(property "Reference" "{ref}"') == 1, ref
    print("patched ok; added D701 R720 R721 R722 C743 C744 TP701")


if __name__ == "__main__":
    main()
