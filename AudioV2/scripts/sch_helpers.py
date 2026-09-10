"""KiCad schematic helpers — grid snap, pin coords, lib_symbols embed."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import uuid
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# --- KiCad 標準シンボルライブラリの探索 --------------------------------------
# macOS / Windows / Linux のどれでも動くようにする。以前は macOS のパスが直書きで、
# Windows は `C:\tmp\kicad-symbols` にジャンクションを張って凌いでいた（§2.9 の記録）。
# 順に見て、最初に見つかったものを使う。**見つからないときは試した場所を全部出す。**

_EXPLICIT_ENV = "KICAD_SYMBOL_DIR"          # このリポジトリ独自。最優先
_KICAD_ENV = ("KICAD10_SYMBOL_DIR", "KICAD9_SYMBOL_DIR",
              "KICAD8_SYMBOL_DIR", "KICAD7_SYMBOL_DIR")


def _ver_key(d: Path) -> tuple[bool, tuple[int, ...]]:
    """バージョン名を数値で比較する。

    辞書順だと "9.0" > "10.0" になり、KiCad 9 と 10 が同居している Windows で
    古い方を掴む。数字を取り出して数値のタプルで比べる。数字を含まない
    ディレクトリは (False, ()) になり、reverse=True では最後に回る。
    """
    nums = tuple(int(n) for n in re.findall(r"\d+", d.name))
    return bool(nums), nums


def _symbol_root_candidates():
    """(パス, どこ由来か) を優先順に返す。存在確認はしない。"""
    for var in (_EXPLICIT_ENV, *_KICAD_ENV):
        val = os.environ.get(var)
        if val:
            yield Path(val), f"環境変数 {var}"

    # 旧来の逃げ道。Windows では カレントドライブの \tmp\kicad-symbols に解決される
    yield Path("/tmp/kicad-symbols"), "旧来の逃げ道 /tmp/kicad-symbols"

    # macOS
    yield (Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"),
           "macOS 既定")

    # Windows: Program Files\KiCad\<version>\share\kicad\symbols
    seen = set()
    for base in (os.environ.get("ProgramW6432"), os.environ.get("ProgramFiles"),
                 r"C:\Program Files"):
        if not base or base in seen:
            continue
        seen.add(base)
        kicad = Path(base) / "KiCad"
        try:
            vers = sorted((d for d in kicad.iterdir() if d.is_dir()),
                          key=_ver_key, reverse=True)
        except OSError:
            continue
        for ver in vers:
            yield ver / "share" / "kicad" / "symbols", f"Windows KiCad {ver.name}"

    # Linux（ディストリ配布・Flatpak）
    yield Path("/usr/share/kicad/symbols"), "Linux 既定"
    yield (Path("/var/lib/flatpak/app/org.kicad.KiCad/current/active/files/"
                "share/kicad/symbols"), "Flatpak")


@lru_cache(maxsize=1)
def symbol_root() -> Path:
    """KiCad 標準シンボルライブラリの場所。見つからなければ試した場所を添えて落とす。"""
    tried = []
    for path, why in _symbol_root_candidates():
        if path.is_dir():
            return path
        tried.append(f"    {why}: {path}")
    raise FileNotFoundError(
        "KiCad の標準シンボルライブラリが見つかりません。\n"
        "  探した場所（この順）:\n" + "\n".join(tried) + "\n\n"
        f"  KiCad を入れるか、{_EXPLICIT_ENV} で明示してください:\n"
        f"    macOS/Linux:  export {_EXPLICIT_ENV}=/path/to/kicad/symbols\n"
        f"    Windows:      set {_EXPLICIT_ENV}=C:\\Program Files\\KiCad\\9.0\\share\\kicad\\symbols\n"
        "  自己診断:  python3 AudioV2/scripts/sch_helpers.py"
    )


def write_sch(path: Path, text: str) -> None:
    r"""KiCad ファイルを書き出す。改行は必ず LF。

    Windows の Python はテキストモードで ``\n`` を ``\r\n`` に変換する。
    素の ``write_text`` で書くと生成物が CRLF になり、内容が同一でも再生成の
    たびに全ファイルが変更扱いになって本物の差分が埋もれる（``.gitattributes``
    の ``*.kicad_sch text eol=lf`` がコミット時に戻すのでリポジトリは汚れないが、
    作業ツリーは汚れる）。**生成物の書き出しは必ずここを通すこと。**
    """
    path.write_text(text, encoding="utf-8", newline="\n")


# --- KiCad の正準形へ揃える --------------------------------------------------
# このスクリプト群は `.kicad_sym` から抜いたシンボル本体をそのまま貼って
# `lib_symbols` を組み立てる。ところが `.kicad_sym` と `.kicad_sch` の中の
# `lib_symbols` は方言が違う（シンボルごとの embedded_fonts / exclude_from_sim /
# in_bom / on_board / in_pos_files / duplicate_pin_numbers_are_jumpers、
# プロパティごとの show_name / do_not_autoplace が `.kicad_sym` には無い。
# インデントも一段深い）。KiCad は読むときは寛容だが、**保存すると自分の正準形へ
# 書き戻す**。放っておくと「KiCad で開いて保存 → 3万行の差分 → 再生成 → 元に戻る」
# を永久に往復する（2026-09-10 に実測）。
#
# 正準形を Python で書き起こすと KiCad の版に追随できないので、KiCad 自身に
# 揃えさせる。`kicad-cli sch upgrade` は冪等（2回目はバイト一致）。

_CLI_ENV = "KICAD_CLI"                      # このリポジトリ独自。最優先


def _kicad_cli_candidates():
    """(パス, どこ由来か) を優先順に返す。存在確認はしない。"""
    val = os.environ.get(_CLI_ENV)
    if val:
        yield Path(val), f"環境変数 {_CLI_ENV}"

    which = shutil.which("kicad-cli")
    if which:
        yield Path(which), "PATH"

    yield (Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"),
           "macOS 既定")

    seen = set()
    for base in (os.environ.get("ProgramW6432"), os.environ.get("ProgramFiles"),
                 r"C:\Program Files"):
        if not base or base in seen:
            continue
        seen.add(base)
        kicad = Path(base) / "KiCad"
        try:
            vers = sorted((d for d in kicad.iterdir() if d.is_dir()),
                          key=_ver_key, reverse=True)
        except OSError:
            continue
        for ver in vers:
            yield ver / "bin" / "kicad-cli.exe", f"Windows KiCad {ver.name}"

    yield Path("/usr/bin/kicad-cli"), "Linux 既定"


@lru_cache(maxsize=1)
def kicad_cli() -> Path:
    """`kicad-cli` の場所。見つからなければ試した場所を添えて落とす。"""
    tried = []
    for path, why in _kicad_cli_candidates():
        if path.is_file():
            return path
        tried.append(f"    {why}: {path}")
    raise FileNotFoundError(
        "kicad-cli が見つかりません。生成物を KiCad の正準形へ揃えるのに要ります。\n"
        "  探した場所（この順）:\n" + "\n".join(tried) + "\n\n"
        f"  KiCad を入れるか、{_CLI_ENV} で明示してください:\n"
        f"    macOS/Linux:  export {_CLI_ENV}=/path/to/kicad-cli\n"
        "  自己診断:  python3 AudioV2/scripts/sch_helpers.py"
    )


def canonicalize_sch(paths: list[Path]) -> None:
    """書き出した `.kicad_sch` を KiCad 自身に正準形へ書き直させる。

    **生成の最後に必ず通すこと。** 通さないと KiCad で開いて保存しただけで
    数万行の差分が出る。`sch upgrade` は階層を辿らないので、シートは1枚ずつ渡す。
    """
    cli = kicad_cli()
    for path in paths:
        before = path.read_text(encoding="utf-8")
        proc = subprocess.run(
            [str(cli), "sch", "upgrade", "--force", str(path)],
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"kicad-cli sch upgrade に失敗しました: {path}\n{proc.stderr.strip()}"
            )
        text = path.read_text(encoding="utf-8")
        # `sch upgrade` はルートの (embedded_fonts no) を落とすが、KiCad の GUI は
        # 保存時に必ず書く。落としたままだと開いて保存しただけで差分が出るので戻す。
        # 深さで見分けること — シンボル定義の中にも同じ行があり、素朴な部分文字列
        # 検索だとそちらに当たって「有る」と誤判定する。
        top = "\t(embedded_fonts no)"

        def has_top(s: str) -> bool:
            return any(ln == top for ln in s.splitlines())

        if has_top(before) and not has_top(text):
            text = text.rstrip()[:-1].rstrip() + "\n" + top + "\n)\n"
        # kicad-cli の改行に依存しない。write_sch と同じ LF の保証をここでも掛ける。
        write_sch(path, text)


def new_uid() -> str:
    return str(uuid.uuid4())


def grid(x: float, step: float = 2.54) -> float:
    return round(x / step) * step


def _rotate_point(ox: float, oy: float, rot: int) -> tuple[float, float]:
    if rot == 0:
        return ox, oy
    # KiCad の回転は y 下向きの図面座標で反時計回り。lib 座標 (px, py) は
    # 呼び出し側で py の符号を反転して渡される（ox=px, oy=-py）。
    #   90:  (x, y) -> ( y, -x)      270: (x, y) -> (-y,  x)
    # 2026-09-09 まで 90 と 270 の式が入れ替わっていた。対称な 2 ピン部品では
    # ピン先の集合が同じになるので気づかず、非対称な部品（例 MeasureControl の
    # J1602、rot 270）で実図のワイヤ端と食い違って発覚。実図 5 枚の rot 90/270
    # 全ピンに対する命中率で検証済み（scratch の rot_check）。
    if rot == 90:
        return oy, -ox
    if rot == 180:
        return -ox, -oy
    if rot == 270:
        return -oy, ox
    return ox, oy


def pin_connect(
    sx: float,
    sy: float,
    sym_rot: int,
    px: float,
    py: float,
    pin_angle: int = 0,
    length: float = 0.0,
) -> tuple[float, float]:
    """Absolute electrical tip of a schematic pin.

    In KiCad, lib pin ``(at x y rot)`` is the **connection tip** (wires / labels
    attach here).  ``length`` draws the pin body *inward* toward the symbol and
    must not be added to the tip.  Instance placement flips library Y:
    global = rotate(px, -py, sym_rot) + (sx, sy).

    ``pin_angle`` / ``length`` are kept for call-site compatibility but ignored.
    """
    del pin_angle, length
    rx, ry = _rotate_point(px, -py, sym_rot)
    return sx + rx, sy + ry


def _pins(
    sx: float,
    sy: float,
    sym_rot: int,
    defs: list[tuple[float, float, int, float]],
) -> list[tuple[float, float]]:
    return [pin_connect(sx, sy, sym_rot, px, py, ang, ln) for px, py, ang, ln in defs]


def cap_pins(cx: float, cy: float, rot: int = 0) -> tuple[tuple[float, float], tuple[float, float]]:
    p1, p2 = _pins(
        cx,
        cy,
        rot,
        [(0, 3.81, 270, 2.794), (0, -3.81, 90, 2.794)],
    )
    return p1, p2


def fuse_pins(fx: float, fy: float, rot: int = 90) -> tuple[tuple[float, float], tuple[float, float]]:
    p1, p2 = _pins(
        fx,
        fy,
        rot,
        [(0, 3.81, 270, 1.27), (0, -3.81, 90, 1.27)],
    )
    return p1, p2


def lm7809_pins(ux: float, uy: float, rot: int = 0) -> dict[str, tuple[float, float]]:
    vi, gnd, vo = _pins(
        ux,
        uy,
        rot,
        [(-7.62, 0, 0, 2.54), (0, -7.62, 90, 2.54), (7.62, 0, 180, 2.54)],
    )
    return {"VI": vi, "GND": gnd, "VO": vo}


def dkmw_pins(sx: float, sy: float, rot: int = 0) -> dict[str, tuple[float, float]]:
    keys = ("1", "2", "3", "4", "5", "6")
    defs = [
        (-12.7, -8.89, 0, 2.54),
        (-12.7, -5.08, 0, 2.54),
        (12.7, -6.35, 180, 2.54),
        (12.7, -8.89, 180, 2.54),
        (12.7, -11.43, 180, 2.54),
        (-12.7, -13.97, 0, 2.54),
    ]
    pts = _pins(sx, sy, rot, defs)
    return dict(zip(keys, pts, strict=True))


def ch224_pins(sx: float, sy: float, rot: int = 0) -> dict[str, tuple[float, float]]:
    keys = ("VBUS", "GND", "12V", "PG")
    defs = [
        (-12.7, 5.08, 0, 2.54),
        (-12.7, 2.54, 0, 2.54),
        (12.7, 5.08, 180, 2.54),
        (12.7, 2.54, 180, 2.54),
    ]
    pts = _pins(sx, sy, rot, defs)
    return dict(zip(keys, pts, strict=True))


def usb16_pins(jx: float, jy: float, rot: int = 0) -> dict[str, tuple[float, float]]:
    vbus, gnd = _pins(
        jx,
        jy,
        rot,
        [(15.24, 15.24, 180, 5.08), (0, -22.86, 90, 5.08)],
    )
    return {"VBUS": vbus, "GND": gnd}


def conn02_pins(cx: float, cy: float, rot: int = 0) -> tuple[tuple[float, float], tuple[float, float]]:
    p1, p2 = _pins(
        cx,
        cy,
        rot,
        [(5.08, 0, 180, 3.81), (5.08, -2.54, 180, 3.81)],
    )
    return p1, p2


def conn03_pins(
    cx: float, cy: float, rot: int = 0
) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
    p1, p2, p3 = _pins(
        cx,
        cy,
        rot,
        [(5.08, 2.54, 180, 3.81), (5.08, 0, 180, 3.81), (5.08, -2.54, 180, 3.81)],
    )
    return p1, p2, p3


def pin_uuid_block(numbers: list[str]) -> str:
    lines = []
    for n in numbers:
        lines.append(
            f'\t\t(pin "{n}"\n\t\t\t(uuid "{new_uid()}")\n\t\t)'
        )
    return "\n".join(lines)


PIN_COUNTS: dict[str, list[str]] = {
    "Device:C": ["1", "2"],
    "Device:R": ["1", "2"],
    "Device:Fuse": ["1", "2"],
    "Device:LED": ["1", "2"],
    "Device:RotaryEncoder_Switch": ["A", "B", "C", "S1", "S2"],
    "Device:R_Potentiometer_Dual": ["1", "2", "3", "4", "5", "6"],
    "Switch:SW_SPST": ["1", "2"],
    "Switch:SW_DP3T": ["1", "2", "3", "4", "5", "6", "7", "8"],
    "Switch:SW_SP3T": ["1", "2", "3", "4"],
    "Regulator_Linear:LM7809_TO220": ["1", "2", "3"],
    "Connector:USB_C_Receptacle_USB2.0_16P": [
        "A1", "A4", "A5", "A6", "A7", "A8", "A9", "A12",
        "B1", "B4", "B5", "B6", "B7", "B8", "B9", "B12", "SH",
    ],
    "Connector:Conn_01x02_Pin": ["1", "2"],
    "Connector:Conn_01x03_Pin": ["1", "2", "3"],
    "Connector:Conn_01x04_Pin": ["1", "2", "3", "4"],
    "Connector:Conn_01x06_Pin": ["1", "2", "3", "4", "5", "6"],
    "Connector:Screw_Terminal_01x02": ["1", "2"],
    "AudioV2:CH224_50224": ["1", "2", "3", "4"],
    "power:PWR_FLAG": ["1"],
    "AudioV2:DKMW20F-12": ["1", "2", "3", "4", "5", "6"],
    "AudioV2:DKMW20F-15": ["1", "2", "3", "4", "5", "6"],
    "AudioV2:REC10K-2415DAW": ["1", "2", "3", "4", "5", "6"],
    "AudioV2:PT2314": [str(i) for i in range(1, 29)],
    "AudioV2:TMUX7612": [str(i) for i in range(1, 17)],
    "Interface_Expansion:MCP23017x-x-SP": [str(i) for i in range(1, 29)],
    "BP5293_ROHM:BP5293-50": ["1", "2", "3"],
    "Relay:AZ850P2-x": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
    "Transistor_Array:ULN2803A": [str(i) for i in range(1, 19)],
}

# Schematic lib_id -> (source_lib, source_sym, extends chain base-first)
# OLED: do NOT map SSD1306/ER_OLEDM0.91 (128×32). Control uses Conn_01x04 header.
SYMBOL_SOURCES: dict[str, tuple[str, str, list[tuple[str, str]]]] = {
    "Amplifier_Operational:NE5532": (
        "Amplifier_Operational",
        "NE5532",
        [("Amplifier_Operational", "LM2904")],
    ),
    "Interface_Expansion:MCP23017-E/SP": (
        "Interface_Expansion",
        "MCP23017x-x-SP",
        [("Interface_Expansion", "MCP23017x-x-SO")],
    ),
    # KiCad 10 の正しい名前。旧 "MCP23017-E/SP" は現行 lib に存在しないので
    # 新規シートではこちらを使う（AGENT_HANDOFF §2.9）。
    "Interface_Expansion:MCP23017x-x-SP": (
        "Interface_Expansion",
        "MCP23017x-x-SP",
        [("Interface_Expansion", "MCP23017x-x-SO")],
    ),
    "MCU_Module:Raspberry_Pi_Pico": ("MCU_Module", "RaspberryPi_Pico", []),
    "MCU_Module:RaspberryPi_Pico": ("MCU_Module", "RaspberryPi_Pico", []),
    "Audio:PGA2310PA": ("Audio", "PGA2310PA", [("Audio", "PGA2310UA")]),
    "Regulator_Linear:LM7809_TO220": (
        "Regulator_Linear",
        "LM7809_TO220",
        [("Regulator_Linear", "LM7805_TO220")],
    ),
    "BP5293_ROHM:BP5293-50": ("BP5293_ROHM", "BP5293-50", []),
}


def _read_symbol_text(lib: str, name: str) -> str:
    if lib == "AudioV2":
        return (ROOT / "AudioV2.kicad_sym").read_text(encoding="utf-8")
    if lib == "BP5293_ROHM":
        return (ROOT.parent / "Audio" / "BP5293_ROHM.kicad_sym").read_text(encoding="utf-8")
    return _read_packed_or_dir(lib, name)


def _pin_numbers_from_sym_text(text: str, sym_name: str) -> list[str]:
    m = re.search(rf'\(symbol "{re.escape(sym_name)}"', text)
    if not m:
        return []
    start = m.start()
    depth = 0
    end = start
    for i in range(start, len(text)):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    chunk = text[start:end]
    nums = re.findall(r'\(number "([^"]+)"', chunk)
    seen: set[str] = set()
    out: list[str] = []
    for n in nums:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def pin_numbers_for(lib_id: str) -> list[str]:
    if lib_id in PIN_COUNTS:
        return PIN_COUNTS[lib_id]
    _, embed_name = lib_id.split(":", 1)
    if lib_id in SYMBOL_SOURCES:
        file_lib, file_name, extends = SYMBOL_SOURCES[lib_id]
    else:
        file_lib, file_name = lib_id.split(":", 1)
        extends = []
    merged: list[str] = []
    seen: set[str] = set()
    for elib, ename in extends:
        for p in _pin_numbers_from_sym_text(_read_symbol_text(elib, ename), ename):
            if p not in seen:
                seen.add(p)
                merged.append(p)
    for p in _pin_numbers_from_sym_text(_read_symbol_text(file_lib, file_name), file_name):
        if p not in seen:
            seen.add(p)
            merged.append(p)
    return merged or ["1"]


def _extract_symbol_body(
    kicad_sym_text: str,
    lib_name: str,
    embed_name: str,
    file_name: str | None = None,
) -> str:
    """Turn (symbol \"FILE\" ...) into embeddable (symbol \"Lib:EMBED\" ...)."""
    src = file_name or embed_name
    m = re.search(rf'\(symbol "{re.escape(src)}"', kicad_sym_text)
    if not m:
        raise ValueError(f"symbol {src} not found")
    start = m.start()
    depth = 0
    for i in range(start, len(kicad_sym_text)):
        if kicad_sym_text[i] == "(":
            depth += 1
        elif kicad_sym_text[i] == ")":
            depth -= 1
            if depth == 0:
                body = kicad_sym_text[start : i + 1]
                body = body.replace(f'(symbol "{src}"', f'(symbol "{lib_name}:{embed_name}"', 1)
                if src != embed_name:
                    body = body.replace(f'"{src}_', f'"{embed_name}_')
                return body
    raise ValueError(f"unbalanced symbol {src}")


def _read_packed_or_dir(lib: str, sym_name: str) -> str:
    root = symbol_root()
    symdir = root / f"{lib}.kicad_symdir" / f"{sym_name}.kicad_sym"
    if symdir.is_file():
        return symdir.read_text(encoding="utf-8")
    packed = root / f"{lib}.kicad_sym"
    if packed.is_file():
        return packed.read_text(encoding="utf-8")
    raise FileNotFoundError(
        f"シンボル {lib}:{sym_name} が見つかりません。\n"
        f"  探した場所: {symdir}\n"
        f"              {packed}\n"
        f"  シンボルライブラリの場所: {root}"
    )


def _sanitize_embed_body(body: str) -> str:
    """KiCad 10 sch rejects some legacy symbol stroke types."""
    return body.replace("(type solid)", "(type default)")


def _indent_symbol_body(body: str) -> str:
    return "\n".join(("\t" + ln if ln.strip() else ln) for ln in body.splitlines())


def _extract_raw_symbol(kicad_sym_text: str, sym_name: str) -> str:
    """Extract raw (symbol \"NAME\" ...) including extends-only stubs."""
    m = re.search(rf'\(symbol "{re.escape(sym_name)}"', kicad_sym_text)
    if not m:
        raise ValueError(f"symbol {sym_name} not found")
    start = m.start()
    depth = 0
    for i in range(start, len(kicad_sym_text)):
        if kicad_sym_text[i] == "(":
            depth += 1
        elif kicad_sym_text[i] == ")":
            depth -= 1
            if depth == 0:
                return kicad_sym_text[start : i + 1]
    raise ValueError(f"unbalanced symbol {sym_name}")


def _property_blocks(sym_body: str) -> dict[str, str]:
    """Map property name -> full (property \"Name\" ...) s-expr."""
    out: dict[str, str] = {}
    for m in re.finditer(r'\(property "', sym_body):
        start = m.start()
        depth = 0
        for i in range(start, len(sym_body)):
            if sym_body[i] == "(":
                depth += 1
            elif sym_body[i] == ")":
                depth -= 1
                if depth == 0:
                    block = sym_body[start : i + 1]
                    nm = re.match(r'\(property "([^"]+)"', block)
                    if nm:
                        out[nm.group(1)] = block
                    break
    return out


def _replace_or_insert_properties(body: str, props: dict[str, str]) -> str:
    """Replace existing properties by name; append any missing before unit symbols."""
    for name, block in props.items():
        pat = re.compile(
            rf'\(property "{re.escape(name)}"(?:\s|(?:.|\n)*?\n\t\t\))',
            re.MULTILINE,
        )
        # Match balanced property via scan
        m = re.search(rf'\(property "{re.escape(name)}"', body)
        if m:
            start = m.start()
            depth = 0
            end = start
            for i in range(start, len(body)):
                if body[i] == "(":
                    depth += 1
                elif body[i] == ")":
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break
            body = body[:start] + block + body[end:]
        else:
            # Insert before first nested (symbol "…_ or (embedded_fonts
            ins = re.search(r'\n(\t+)\(symbol "[^"]+_\d', body)
            if not ins:
                ins = re.search(r'\n(\t+)\(embedded_fonts', body)
            if ins:
                indent = ins.group(1)
                # normalize block indent to match sibling properties (two tabs inside symbol)
                blk = block
                body = body[: ins.start()] + "\n" + blk + body[ins.start() :]
            else:
                # before final closing paren
                body = body.rstrip()
                if body.endswith(")"):
                    body = body[:-1] + block + "\n)"
    return body


def _flatten_extends_symbol(
    file_lib: str,
    file_name: str,
    embed_lib: str,
    embed_name: str,
    extends: list[tuple[str, str]],
) -> str:
    """Merge pin-bearing parent into child; emit one (symbol \"Lib:Name\" ...) without extends."""
    if not extends:
        text = _read_symbol_text(file_lib, file_name)
        return _extract_symbol_body(text, embed_lib, embed_name, file_name)

    # Base of chain is the pin-bearing definition (extends listed base-first).
    base_lib, base_name = extends[0]
    parent_text = _read_symbol_text(base_lib, base_name)
    parent_body = _extract_raw_symbol(parent_text, base_name)

    child_text = _read_symbol_text(file_lib, file_name)
    child_body = _extract_raw_symbol(child_text, file_name)
    child_props = _property_blocks(child_body)

    # Start from parent; drop extends if any; rename to embed id.
    body = parent_body
    body = re.sub(r"\n\t*\(extends \"[^\"]+\"\)", "", body)
    body = body.replace(f'(symbol "{base_name}"', f'(symbol "{embed_lib}:{embed_name}"', 1)
    body = body.replace(f'"{base_name}_', f'"{embed_name}_')

    # Intermediate extends (rare): overlay their property overrides too.
    for elib, ename in extends[1:]:
        mid = _extract_raw_symbol(_read_symbol_text(elib, ename), ename)
        body = _replace_or_insert_properties(body, _property_blocks(mid))

    body = _replace_or_insert_properties(body, child_props)

    # Ensure no leftover extends and Value defaults to embed name if still base.
    body = re.sub(r"\n\t*\(extends \"[^\"]+\"\)", "", body)
    if f'(property "Value" "{base_name}"' in body and embed_name != base_name:
        body = body.replace(
            f'(property "Value" "{base_name}"',
            f'(property "Value" "{embed_name}"',
            1,
        )
    return body


# ピンを持たないのが正常な型。ここに書いたものだけ下のピン検査を免除する。
PINLESS_OK = {"Mechanical:MountingHole"}


def embed_lib_symbols(lib_ids: list[str]) -> str:
    """Build (lib_symbols ...) with pin-complete definitions (extends flattened)."""
    chunks: list[str] = ["\t(lib_symbols"]
    seen: set[str] = set()

    for lib_id in lib_ids:
        if lib_id in seen:
            continue
        seen.add(lib_id)
        lib, embed_name = lib_id.split(":", 1)
        if lib_id in SYMBOL_SOURCES:
            file_lib, file_name, extends = SYMBOL_SOURCES[lib_id]
        else:
            file_lib, file_name = lib, embed_name
            extends = []
        if extends:
            body = _flatten_extends_symbol(file_lib, file_name, lib, embed_name, extends)
        else:
            text = _read_symbol_text(file_lib, file_name)
            body = _extract_symbol_body(text, lib, embed_name, file_name)
        # Flattened body must contain pins for netlist/BOM.
        # 例外は PINLESS_OK だけ。このガードは extends の展開が失敗した body を
        # 捕まえるためのもので、機構部品のように本当にピンが無い型と区別がつかない。
        if lib_id not in PINLESS_OK:
            if "(pin " not in body and "(pin\n" not in body and "(pin\t" not in body:
                # also match "(pin power_in" etc.
                if not re.search(r"\(pin\s+\w+", body):
                    raise ValueError(f"embed {lib_id}: flattened body has no pins")
        chunks.append(_indent_symbol_body(_sanitize_embed_body(body)))

    chunks.append("\t)")
    return "\n".join(chunks)


def symbol_inst_v10(
    lib_id: str,
    ref: str,
    value: str,
    x: float,
    y: float,
    rot: int,
    parent_path: str,
    project: str = "AudioV2Case",
    extra_props: list[tuple[str, str]] | None = None,
    unit: int = 1,
    footprint: str = "",
    datasheet: str = "",
    description: str = "",
    instance_refs: list[tuple[str, str]] | None = None,
    prop_dx: float = 0.0,
    grid_step: float = 2.54,
    # NetTie のように「基板上の銅箔で、買う部品ではない」ものは False。
    # KiCad 標準ライブラリの Device:NetTie_2 の既定も in_bom=no。
    in_bom: bool = True,
) -> str:
    from generate_kicad_scaffold import sym_prop  # noqa: WPS433

    props = [
        sym_prop("Reference", ref, x + prop_dx, y - 2.54),
        sym_prop("Value", value, x + prop_dx, y + 2.54),
        sym_prop("Footprint", footprint, 0, 0, hide=True),
        sym_prop("Datasheet", datasheet, 0, 0, hide=True),
        sym_prop("Description", description, 0, 0, hide=True),
    ]
    if extra_props:
        for n, v in extra_props:
            props.append(sym_prop(n, v, 0, 0, hide=True))
    # Multi-unit: only emit pin UUIDs for pins belonging to this unit when known
    nums = pin_numbers_for(lib_id)
    if lib_id == "Switch:SW_DP3T":
        nums = ["1", "2", "3", "4"] if unit == 1 else ["5", "6", "7", "8"]
    pin_block = pin_uuid_block(nums)
    props_str = "\n".join(props)
    paths = instance_refs or [(parent_path, ref)]
    path_blocks = "\n".join(
        f"""\t\t\t\t(path "{path}"
\t\t\t\t\t(reference "{instance_ref}")
\t\t\t\t\t(unit {unit})
\t\t\t\t)"""
        for path, instance_ref in paths
    )
    return f"""\t(symbol
\t\t(lib_id "{lib_id}")
\t\t(at {grid(x, grid_step)} {grid(y, grid_step)} {rot})
\t\t(unit {unit})
\t\t(body_style 1)
\t\t(exclude_from_sim no)
\t\t(in_bom {'yes' if in_bom else 'no'})
\t\t(on_board yes)
\t\t(in_pos_files yes)
\t\t(dnp no)
\t\t(fields_autoplaced yes)
\t\t(uuid "{new_uid()}")
{props_str}
{pin_block}
\t\t(instances
\t\t\t(project "{project}"
{path_blocks}
\t\t\t)
\t\t)
\t)
"""


# --- 配線要素（2026-09-03 追加） ------------------------------------------
#
# 生成コードは長らく「ピン先にラベルを置く」方式だけで、ワイヤを1本も出せなかった。
# 一方 KiCad 側の実図は 572 本のワイヤと 181 個のジャンクションを持つ。
# 手編集所有からスクリプト所有へ戻すにも、新構成の母板・娘基板を起こすにも、
# ここが無いと実図を再現できない。
#
# ⚠ `sch_drift.py` はワイヤもジャンクションも比較しない。これらを使ったシートの
#    検証は drift ではなく **ネットリストの同値** で行うこと。

def wire(x1: float, y1: float, x2: float, y2: float, width: float = 0, style: str = "default") -> str:
    """1本のワイヤ。端点はピン先／他のワイヤ端／ジャンクションに乗せる。"""
    return f"""\t(wire
\t\t(pts
\t\t\t(xy {x1} {y1}) (xy {x2} {y2})
\t\t)
\t\t(stroke
\t\t\t(width {width})
\t\t\t(type {style})
\t\t)
\t\t(uuid "{new_uid()}")
\t)
"""


def wire_path(points: list[tuple[float, float]], **kw: object) -> str:
    """折れ線を線分に展開する。`[(x0,y0), (x1,y1), ...]`。"""
    return "".join(
        wire(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1], **kw)  # type: ignore[arg-type]
        for i in range(len(points) - 1)
    )


def junction(x: float, y: float, diameter: float = 0) -> str:
    """3本以上が集まる点に打つ。2本の突き合わせには要らない。"""
    return f"""\t(junction
\t\t(at {x} {y})
\t\t(diameter {diameter})
\t\t(color 0 0 0 0)
\t\t(uuid "{new_uid()}")
\t)
"""


if __name__ == "__main__":
    # 自己診断: このマシンでシンボルライブラリが見つかるか
    print("KiCad シンボルライブラリの探索\n")
    found = None
    for path, why in _symbol_root_candidates():
        ok = path.is_dir()
        mark = "✅" if ok else "  "
        print(f"  {mark} {why}\n       {path}")
        if ok and found is None:
            found = path
    print()
    if found:
        n = len(list(found.glob("*.kicad_sym"))) + len(list(found.glob("*.kicad_symdir")))
        print(f"→ 使うのは {found}（ライブラリ {n} 件）")
    else:
        print(f"→ 見つかりません。{_EXPLICIT_ENV} で明示してください。")
        sys.exit(1)
