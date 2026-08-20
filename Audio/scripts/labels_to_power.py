#!/usr/bin/env python3
"""計測モジュールの電源レール ローカルラベルをパワーシンボルへ置き換える。

    python3 scripts/labels_to_power.py +5V_A [+3V3_A ...]

ラベルは消して、同じ座標にパワーシンボルを置く。ピンは length 0 なので
接続点はラベルが乗っていた点そのまま、つまりネットは変わらない。
検証は scripts/netcmp.py で行う。
"""
import re
import sys
import uuid as uuidlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCH = ROOT / "MeasurementADC1804_Module.kicad_sch"
EXTRAS = ROOT / "MeasurementADC_Extras.kicad_sym"
PATH = "/760b9589-09e7-434e-9ca2-6e4136e3b7a2/6d49c70d-b40d-4b21-ac6e-fba63bdae03e"


def uid():
    return str(uuidlib.uuid4())


def fmt(v):
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return s if s else "0"


def extras_block(name):
    """Extras ライブラリの定義を lib_symbols 用に一段インデントして取り出す。"""
    src = EXTRAS.read_text()
    start = src.find(f'\t(symbol "{name}"\n')
    if start < 0:
        raise SystemExit(f"ライブラリに {name} がない")
    end = src.find('\n\t(symbol "', start + 1)
    block = src[start : end if end > 0 else src.rfind("\n)")]
    block = block.replace(f'\t(symbol "{name}"', f'\t(symbol "MeasurementADC_Extras:{name}"', 1)
    return "\n".join(("\t" + ln if ln else ln) for ln in block.splitlines()) + "\n"


def next_pwr_index(text):
    used = {int(m) for m in re.findall(r'\(property "Reference" "#PWR(\d+)"', text)}
    n = 701
    while n in used:
        n += 1
    return n


def prop(name, value, x, y, hide, extra=""):
    h = "\t\t\t(hide yes)\n" if hide else ""
    return (
        f'\t\t(property "{name}" "{value}"\n'
        f"\t\t\t(at {fmt(x)} {fmt(y)} 0)\n"
        "\t\t\t(show_name no)\n"
        "\t\t\t(do_not_autoplace no)\n"
        f"{h}"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n"
        f"{extra}"
        "\t\t\t)\n"
        "\t\t)\n"
    )


def instance(rail, x, y, ref, is_gnd):
    # 電源は電圧が要るので Value を上に出す。GND は 4 系統を図形で描き分けて
    # あるうえ、文字を下に出すと下の部品や注記に被るので隠す（凡例で補う）。
    vy = y - 3.556 if not is_gnd else y + 3.81
    ry = y - 6.35 if not is_gnd else y + 6.35
    return (
        "\t(symbol\n"
        f'\t\t(lib_id "MeasurementADC_Extras:{rail}")\n'
        f"\t\t(at {fmt(x)} {fmt(y)} 0)\n"
        "\t\t(unit 1)\n"
        "\t\t(body_style 1)\n"
        "\t\t(exclude_from_sim no)\n"
        "\t\t(in_bom no)\n"
        "\t\t(on_board yes)\n"
        "\t\t(in_pos_files no)\n"
        "\t\t(dnp no)\n"
        "\t\t(fields_autoplaced yes)\n"
        f'\t\t(uuid "{uid()}")\n'
        + prop("Reference", ref, x, ry, True)
        + prop("Value", rail, x, vy, is_gnd)
        + prop("Footprint", "", x, y, True)
        + prop("Datasheet", "", x, y, True)
        + prop("Description", "", x, y, True)
        + f'\t\t(pin "1"\n\t\t\t(uuid "{uid()}")\n\t\t)\n'
        "\t\t(instances\n"
        '\t\t\t(project "AudioCase"\n'
        f'\t\t\t\t(path "{PATH}"\n'
        f'\t\t\t\t\t(reference "{ref}")\n'
        "\t\t\t\t\t(unit 1)\n"
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n"
    )


GND_RAILS = {"A_GND", "ADC_GND", "D_GND", "ADC_GND_IN"}

# ラベルがワイヤの途中に乗っている箇所。パワーシンボルのピンは端点でしか
# 繋がらないので、同じワイヤの自由端へ寄せる。
SNAP = {
    ("+3V3_A", 439.42, 121.92): (445.77, 121.92),
}


def wire_endpoints(text):
    ends = set()
    for m in re.finditer(
        r"\(wire\n\t\t\(pts\n\t\t\t\(xy ([0-9.]+) ([0-9.]+)\) \(xy ([0-9.]+) ([0-9.]+)\)", text
    ):
        a, b, c, d = (round(float(v), 2) for v in m.groups())
        ends.add((a, b))
        ends.add((c, d))
    return ends


def convert(text, rail):
    pat = re.compile(
        r'\t\(label "' + re.escape(rail) + r'"\n'
        r"\t\t\(at ([0-9.]+) ([0-9.]+) \d+\)\n"
        r"\t\t\(effects\n\t\t\t\(font\n\t\t\t\t\(size 1\.27 1\.27\)\n\t\t\t\)\n"
        r"(?:\t\t\t\(justify [^)]+\)\n)?"
        r"\t\t\)\n"
        r'\t\t\(uuid "[^"]+"\)\n\t\)\n'
    )
    ends = wire_endpoints(text)
    spots, skipped = [], []
    for m in pat.finditer(text):
        x, y = round(float(m.group(1)), 2), round(float(m.group(2)), 2)
        x, y = SNAP.get((rail, x, y), (x, y))
        (spots if (x, y) in ends else skipped).append((x, y))
    if skipped:
        raise SystemExit(
            f"{rail}: ワイヤ端点でない箇所がある {skipped}。SNAP に寄せ先を書くか対象から外すこと"
        )
    if not spots:
        return text, []
    text = pat.sub("", text)

    if f'\t\t(symbol "MeasurementADC_Extras:{rail}"' not in text:
        blk = extras_block(rail)
        m = re.search(r"^\t\t\(symbol \"", text, re.M)
        text = text[: m.start()] + blk + text[m.start() :]

    idx = next_pwr_index(text)
    blobs = []
    for x, y in spots:
        blobs.append(instance(rail, x, y, f"#PWR{idx}", rail in GND_RAILS))
        idx += 1
    text = re.sub(r"^\t\(symbol\n", "".join(blobs) + "\t(symbol\n", text, count=1, flags=re.M)
    return text, spots


def main():
    text = SCH.read_text()
    for rail in sys.argv[1:]:
        text, spots = convert(text, rail)
        print(f"{rail}: {len(spots)} 個 -> " + ", ".join(f"({x},{y})" for x, y in spots))
    SCH.write_text(text)


if __name__ == "__main__":
    main()
