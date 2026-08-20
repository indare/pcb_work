#!/usr/bin/env python3
"""Replace U709/U710 TPS3808 pair with one TPS3307-33D (SO-8)."""
from pathlib import Path
import re
import uuid as uuidlib

ROOT = Path("/Users/masashiarino/workspace/pcb_work")
SCH = ROOT / "Audio/MeasurementADC1804_Module.kicad_sch"
EXTRAS = ROOT / "Audio/MeasurementADC_Extras.kicad_sym"
PATH = "/760b9589-09e7-434e-9ca2-6e4136e3b7a2/6d49c70d-b40d-4b21-ac6e-fba63bdae03e"


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


def insert_before(text, pattern, blob):
    m = re.search(pattern, text, re.M)
    if not m:
        raise SystemExit(f"anchor not found: {pattern}")
    return text[: m.start()] + blob + text[m.start() :]


def drop_instance(text, ref):
    parts = re.split(r"(?=\n\t\(symbol\n)", text)
    kept = []
    n = 0
    for p in parts:
        if re.search(r'\t\t\(property "Reference" "' + re.escape(ref) + r'"\n', p) and p.startswith(
            "\n\t(symbol\n"
        ):
            n += 1
            continue
        kept.append(p)
    if n != 1:
        raise SystemExit(f"instance {ref} matched {n}")
    return "".join(kept)


def drop_label(text, name, x, y):
    pat = (
        r'\t\(label "' + re.escape(name) + r'"\n'
        r"\t\t\(at " + re.escape(fmt(x)) + " " + re.escape(fmt(y)) + r" \d+\)\n"
        r"\t\t\(effects\n\t\t\t\(font\n\t\t\t\t\(size 1\.27 1\.27\)\n\t\t\t\)\n"
        r"\t\t\t\(justify \w+\)\n\t\t\)\n"
        r'\t\t\(uuid "[^"]+"\)\n\t\)\n'
    )
    text, n = re.subn(pat, "", text, count=1)
    if n != 1:
        raise SystemExit(f"label {name} @({x},{y}) matched {n}")
    return text


def extras_to_sch_lib(name):
    src = EXTRAS.read_text()
    start = src.find(f'\t(symbol "{name}"\n')
    end = src.find("\n\t(symbol ", start + 1)
    if end < 0:
        end = src.rfind("\n)")
    block = src[start:end]
    block = block.replace(f'\t(symbol "{name}"', f'\t(symbol "MeasurementADC_Extras:{name}"', 1)
    return "\n".join(("\t" + ln if ln else ln) for ln in block.splitlines()) + "\n"


def make_u709():
    x, y, rot = 412.75, 127.0, 0
    pins = "".join(f'\t\t(pin "{p}"\n\t\t\t(uuid "{uid()}")\n\t\t)\n' for p in "12345678")
    return f'''	(symbol
		(lib_id "MeasurementADC_Extras:TPS3307-33")
		(at {fmt(x)} {fmt(y)} {rot})
		(unit 1)
		(body_style 1)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(in_pos_files yes)
		(dnp no)
		(uuid "{uid()}")
		(property "Reference" "U709"
			(at 415.29 114.3 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left)
			)
		)
		(property "Value" "TPS3307-33D"
			(at 415.29 116.84 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left)
			)
		)
		(property "Footprint" "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"
			(at {fmt(x)} {fmt(y)} 0)
			(hide yes)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Datasheet" "https://www.ti.com/lit/ds/symlink/tps3307.pdf"
			(at {fmt(x)} {fmt(y)} 0)
			(hide yes)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Description" "SO-8 triple supervisor. SENSE1=+5V_A 4.55V, SENSE2=+3V3_A 2.93V, SENSE3 unused to VDD. VDD=+3V3_A so ~RESET is 3.3V push-pull. GP15 -> ~MR. 200ms delay."
			(at {fmt(x)} {fmt(y)} 0)
			(hide yes)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
{pins}		(instances
			(project "AudioCase"
				(path "{PATH}"
					(reference "U709")
					(unit 1)
				)
			)
		)
	)
'''


def make_c745():
    x, y = 419.1, 127.0
    return f'''	(symbol
		(lib_id "Device:C")
		(at {fmt(x)} {fmt(y)} 0)
		(unit 1)
		(body_style 1)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(in_pos_files yes)
		(dnp no)
		(uuid "{uid()}")
		(property "Reference" "C745"
			(at 422.91 125.73 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left)
			)
		)
		(property "Value" "100nF"
			(at 422.91 129.54 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left)
			)
		)
		(property "Footprint" "Capacitor_SMD:C_0603_1608Metric"
			(at {fmt(x)} {fmt(y)} 0)
			(hide yes)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Datasheet" ""
			(at {fmt(x)} {fmt(y)} 0)
			(hide yes)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Description" "TPS3307-33 VDD local 0.1uF"
			(at {fmt(x)} {fmt(y)} 0)
			(hide yes)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(pin "1"
			(uuid "{uid()}")
		)
		(pin "2"
			(uuid "{uid()}")
		)
		(instances
			(project "AudioCase"
				(path "{PATH}"
					(reference "C745")
					(unit 1)
				)
			)
		)
	)
'''


def main():
    text = SCH.read_text()
    if "TPS3307-33D" in text and '(property "Reference" "U710"' not in text:
        raise SystemExit("already converted")

    text = text.replace('(rev "0.3")', '(rev "0.4")', 1)
    text = text.replace(
        "D701 SOD-123 ショットキ +5V_D→VSYS。U708=XC8107 LCD、U709=G33、U710=G50",
        "D701 SOD-123 ショットキ +5V_D→VSYS。U708=XC8107 LCD、U709=TPS3307-33D（3.3V+5V 監視 SO-8）",
    )
    text = text.replace(
        "Y701 ASFL1->R718->ADC_MCLK (TP701; R720 1k to GP9 sense). "
        "U709 G33 / U710 G50 OD wire-AND + GP15 OD -> ADC_nRST (CT 100k to VDD). "
        "U708 XC8107 LCD load-SW (LCD_EN High=ON).",
        "Y701 ASFL1->R718->ADC_MCLK (TP701; R720 1k to GP9 sense). "
        "U709 TPS3307-33D SO-8 watches +5V_A/+3V3_A, ~RESET->ADC_nRST (PP, 200ms), GP15 OD -> ~MR. "
        "U708 XC8107 LCD load-SW (LCD_EN High=ON).",
    )
    text = text.replace(
        "GP15=ADC_nRST (OD, H は駆動しない)",
        "GP15=ADC_nMR (TPS3307 ~MR, OD, H は駆動しない)",
    )
    text = text.replace(
        "U709=TPS3808G33(+3V3_A) U710=TPS3808G50(+5V_A); SENSE=rail + C743/C744 4.7nF local; "
        "CT=R721/R722 100k to VDD (short delay, no pin-1 lift); OD ~RESET wire-AND+R719 + GP15 OD; "
        "VDD 0.1uF local. Larger package: next revision.",
        "U709=TPS3307-33D SO-8: SENSE1=+5V_A (4.55V) SENSE2=+3V3_A (2.93V) SENSE3=VDD; "
        "VDD=+3V3_A C745 100nF; ~RESET PP -> ADC_nRST + R719; GP15 OD -> ~MR (do not drive H); "
        "RESET pin NC; 200ms delay. Replaces TPS3808G33/G50 SOT-23-6.",
    )
    text = text.replace(
        "GP15=ADC_nRST はオープンドレインのみ。H は駆動しない（R719 プルアップのワイヤ AND）。",
        "GP15=ADC_nMR は TPS3307 の ~MR。オープンドレインのみ、H は駆動しない。"
        " ~RESET はプッシュプルなので ADC_nRST には直接ワイヤ AND しない。",
    )

    lib = extras_to_sch_lib("TPS3307-33")
    if '(symbol "MeasurementADC_Extras:TPS3307-33"' not in text:
        text = insert_before(text, r'^\t\t\(symbol "MeasurementADC_Extras:TPS3808G33DBVR"\n', lib)

    for ref in ("R721", "R722", "C743", "C744", "U710", "U709"):
        text = drop_instance(text, ref)

    # Pico GP15 was ADC_nRST; it now drives ~MR only.
    text = drop_label(text, "ADC_nRST", 247.65, 190.5)
    text = drop_label(text, "CT_G33", 396.24, 114.3)
    text = drop_label(text, "CT_G50", 394.97, 147.32)

    # New chip at (412.75, 127):
    # SENSE1 402.59,123.19  SENSE2 402.59,125.73  SENSE3 402.59,128.27  GND 402.59,130.81
    # VDD 422.91,123.19  ~MR 422.91,125.73  RESET 422.91,128.27  ~RESET 422.91,130.81
    # C745 at 419.1,127 pin1 419.1,123.19  pin2 419.1,130.81
    conn = (
        label("+5V_A", 396.24, 123.19, 180, "right")
        + wire(396.24, 123.19, 402.59, 123.19)
        + label("+3V3_A", 396.24, 125.73, 180, "right")
        + wire(396.24, 125.73, 402.59, 125.73)
        + wire(402.59, 125.73, 402.59, 128.27)
        + junction(402.59, 125.73)
        + label("ADC_GND", 396.24, 130.81, 180, "right")
        + wire(396.24, 130.81, 402.59, 130.81)
        + wire(402.59, 130.81, 419.1, 130.81)
        + junction(402.59, 130.81)
        + label("+3V3_A", 428.0, 123.19, 0, "left")
        + wire(422.91, 123.19, 428.0, 123.19)
        + wire(419.1, 123.19, 422.91, 123.19)
        + junction(422.91, 123.19)
        + label("ADC_nMR", 428.0, 125.73, 0, "left")
        + wire(422.91, 125.73, 428.0, 125.73)
        + nc(422.91, 128.27)
        # ~RESET is y=130.81, same as leftover ADC_GND @ 424.18,130.81.
        # Do not draw a label-wire through that point; dogleg onto the R719 bus at y=125.73.
        + label("ADC_nRST", 428.0, 130.81, 0, "left")
        + wire(422.91, 130.81, 429.26, 130.81)
        + wire(429.26, 130.81, 429.26, 125.73)
        + label("ADC_nMR", 247.65, 190.5, 180, "right")
    )
    text = insert_before(text, r"^\t\(wire\n", conn)

    text = text.rstrip()[:-1] + make_u709() + make_c745() + ")\n"

    SCH.write_text(text)
    assert text.count('(property "Reference" "U709"') == 1
    assert '(property "Reference" "U710"' not in text
    print("U709 is TPS3307-33D; U710/R721/R722/C743/C744 removed")


if __name__ == "__main__":
    main()
