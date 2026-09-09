#!/usr/bin/env python3
"""回路図ネットリストから PCB フットプリントを同期する（空板の初回起こし向け）。

KiCad GUI の「回路図から PCB を更新」に相当する最小実装。
`exclude_from_board` の部品（例: AmpBankRelay シート）は載せない。
既存フットプリントは参照名で突き合わせ、無ければ追加する。配線は触らない。
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCH = ROOT / "AudioV2" / "AudioV2Case.kicad_sch"
PCB = ROOT / "AudioV2" / "AudioV2Case.kicad_pcb"
OUT = ROOT / "out"
KICAD_FP_DIR = Path(r"C:\Program Files\KiCad\10.0\share\kicad\footprints")


def _ensure_pcbnew():
    import os
    os.environ.setdefault("KICAD10_FOOTPRINT_DIR", str(KICAD_FP_DIR))
    try:
        import pcbnew  # noqa: F401
        return
    except ImportError:
        pass
    for ver in ("10.0", "9.0", "8.0"):
        ki = Path(r"C:\Program Files\KiCad") / ver
        if ki.is_dir():
            sys.path.extend([str(ki / "bin"), str(ki / "bin" / "Lib" / "site-packages")])
            break
    import pcbnew  # noqa: F401


def _expand_uri(uri: str, project_dir: Path) -> Path:
    import os
    uri = uri.replace("${KIPRJMOD}", str(project_dir))
    uri = uri.replace("${KICAD10_FOOTPRINT_DIR}", str(KICAD_FP_DIR))
    uri = uri.replace("${KICAD8_FOOTPRINT_DIR}", str(KICAD_FP_DIR))
    uri = uri.replace("${KICAD7_FOOTPRINT_DIR}", str(KICAD_FP_DIR))
    uri = os.path.expandvars(uri)
    return Path(uri)


def _parse_fp_lib_table(path: Path, project_dir: Path, nick_to_pretty: dict[str, Path]) -> None:
    """Minimal (fp_lib_table ...) reader. Nested type=Table は再帰する。"""
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(
        r'\(lib\s*\(name\s+"([^"]+)"\)\s*\(type\s+"([^"]+)"\)\s*\(uri\s+"([^"]+)"\)',
        text,
    ):
        name, typ, uri = m.group(1), m.group(2), m.group(3)
        resolved = _expand_uri(uri, project_dir)
        if typ == "Table":
            _parse_fp_lib_table(resolved, project_dir, nick_to_pretty)
        elif typ == "KiCad":
            nick_to_pretty[name] = resolved


def load_fp_lib_map(project_dir: Path) -> dict[str, Path]:
    nick: dict[str, Path] = {}
    appdata = Path(os.environ.get("APPDATA", "")) / "kicad" / "10.0" / "fp-lib-table"
    _parse_fp_lib_table(appdata, project_dir, nick)
    _parse_fp_lib_table(project_dir / "fp-lib-table", project_dir, nick)
    if KICAD_FP_DIR.is_dir():
        for pretty in KICAD_FP_DIR.glob("*.pretty"):
            nick.setdefault(pretty.stem, pretty)
    return nick


def export_xml(sch: Path, xml_path: Path) -> None:
    xml_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "kicad-cli", "sch", "export", "netlist",
        "--format", "kicadxml",
        "-o", str(xml_path),
        str(sch),
    ]
    subprocess.run(cmd, check=True)


def parse_comps(xml_path: Path) -> list[dict]:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    comps = []
    for comp in root.iter("comp"):
        ref = comp.get("ref") or ""
        if ref.startswith("#"):
            continue  # power flags etc.
        props = {p.get("name"): (p.get("value") or "") for p in comp.findall("property")}
        if "exclude_from_board" in props:
            continue
        fp = ""
        foot = comp.find("footprint")
        if foot is not None and foot.text:
            fp = foot.text.strip()
        if not fp:
            for field in comp.findall("./fields/field"):
                if field.get("name") == "Footprint" and field.text:
                    fp = field.text.strip()
        value = (comp.findtext("value") or "").strip()
        path_el = comp.find("sheetpath")
        sheetpath = path_el.get("names") if path_el is not None else "/"
        tstamps = (comp.findtext("tstamps") or "").strip()
        path_stamp = path_el.get("tstamps") if path_el is not None else ""
        comps.append({
            "ref": ref,
            "footprint": fp,
            "value": value,
            "sheetpath": sheetpath or "/",
            "path": f"{path_stamp}{tstamps}" if path_stamp or tstamps else "",
        })
    return comps


def load_fp_lib_map(project_dir: Path) -> dict[str, Path]:
    nick: dict[str, Path] = {}
    appdata = Path(os.environ.get("APPDATA", "")) / "kicad" / "10.0" / "fp-lib-table"
    _parse_fp_lib_table(appdata, project_dir, nick)
    _parse_fp_lib_table(project_dir / "fp-lib-table", project_dir, nick)
    if KICAD_FP_DIR.is_dir():
        for pretty in KICAD_FP_DIR.glob("*.pretty"):
            nick.setdefault(pretty.stem, pretty)
    return nick


def load_fp(lib_id: str, nick_to_pretty: dict[str, Path]):
    import pcbnew
    if ":" not in lib_id:
        raise ValueError(f"bad footprint id: {lib_id!r}")
    lib, name = lib_id.split(":", 1)
    pretty = nick_to_pretty.get(lib)
    if pretty is None or not pretty.is_dir():
        raise RuntimeError(f"unknown footprint lib {lib!r} (uri={pretty})")
    io = pcbnew.PCB_IO_KICAD_SEXPR()
    fp = io.FootprintLoad(str(pretty), name, False)
    if fp is None:
        raise RuntimeError(f"FootprintLoad failed: {lib_id} in {pretty}")
    return fp


def sync_board(pcb_path: Path, comps: list[dict], nick_to_pretty: dict[str, Path],
               dry_run: bool = False) -> dict:
    import pcbnew

    board = pcbnew.LoadBoard(str(pcb_path))
    existing = {fp.GetReference(): fp for fp in board.GetFootprints()}
    added = []
    skipped_no_fp = []
    skipped_exists = []
    errors = []

    grid_x, grid_y = 10.0, 10.0
    col, row = 0, 0
    pitch = 15.0

    for c in comps:
        ref, fp_id = c["ref"], c["footprint"]
        if not fp_id:
            skipped_no_fp.append(ref)
            continue
        if ref in existing:
            fp = existing[ref]
            if c["value"]:
                fp.SetValue(c["value"])
            skipped_exists.append(ref)
            continue
        try:
            fp = load_fp(fp_id, nick_to_pretty)
        except Exception as e:
            errors.append(f"{ref}: {fp_id}: {e}")
            continue
        fp.SetReference(ref)
        if c["value"]:
            fp.SetValue(c["value"])
        if c["path"]:
            try:
                fp.SetPath(pcbnew.KIID_PATH(c["path"]))
            except Exception:
                pass
        x = pcbnew.FromMM(grid_x + col * pitch)
        y = pcbnew.FromMM(grid_y + row * pitch)
        fp.SetPosition(pcbnew.VECTOR2I(x, y))
        board.Add(fp)
        added.append(ref)
        col += 1
        if col >= 20:
            col = 0
            row += 1

    want = {c["ref"] for c in comps if c["footprint"]}
    removed = []
    for ref, fp in list(existing.items()):
        if ref.startswith("#"):
            continue
        if ref not in want:
            board.Remove(fp)
            removed.append(ref)

    stats = {
        "added": added,
        "already": skipped_exists,
        "no_footprint": skipped_no_fp,
        "removed": removed,
        "errors": errors,
        "on_board_comps": len(comps),
    }
    if dry_run:
        return stats
    board.Save(str(pcb_path))
    return stats


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sch", type=Path, default=SCH)
    ap.add_argument("--pcb", type=Path, default=PCB)
    ap.add_argument("--xml", type=Path, default=OUT / "audiov2_pcb.xml")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-export", action="store_true")
    args = ap.parse_args()

    _ensure_pcbnew()
    if not args.skip_export:
        export_xml(args.sch, args.xml)
    comps = parse_comps(args.xml)
    nick = load_fp_lib_map(args.sch.parent)
    stats = sync_board(args.pcb, comps, nick, dry_run=args.dry_run)
    print(f"on-board comps (excl. exclude_from_board): {stats['on_board_comps']}")
    print(f"added: {len(stats['added'])}")
    print(f"already on board: {len(stats['already'])}")
    print(f"no footprint: {len(stats['no_footprint'])}")
    print(f"removed: {len(stats['removed'])}")
    if stats["no_footprint"]:
        print("  no FP:", ", ".join(stats["no_footprint"][:20]),
              ("..." if len(stats["no_footprint"]) > 20 else ""))
    if stats["errors"]:
        print("errors:")
        for e in stats["errors"][:40]:
            print(" ", e)
        if len(stats["errors"]) > 40:
            print(f"  ... and {len(stats['errors']) - 40} more")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
