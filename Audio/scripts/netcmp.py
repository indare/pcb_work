#!/usr/bin/env python3
"""回路図編集の前後でネット構成が変わっていないか比べる。

    python3 scripts/netcmp.py save  <tag>   # 現状を基準として保存
    python3 scripts/netcmp.py check <tag>   # 保存した基準と比較

ネット名は KiCad が自動採番する `Net-(...)` を含むため、名前ではなく
「ピンの集合」で突き合わせる。名前だけが変わった場合は rename として出す。
"""
import json
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCH = ROOT / "AudioCase.kicad_sch"
STORE = ROOT / "scripts" / ".netcmp"


def netlist():
    with tempfile.TemporaryDirectory() as td:
        xml = Path(td) / "n.xml"
        subprocess.run(
            ["kicad-cli", "sch", "export", "netlist", "--format", "kicadxml",
             "--output", str(xml), str(SCH)],
            check=True, capture_output=True,
        )
        root = ET.parse(xml).getroot()
    nets = {}
    for net in root.iter("net"):
        pins = sorted(f"{n.get('ref')}.{n.get('pin')}" for n in net.findall("node"))
        if pins:
            nets[net.get("name") or ""] = pins
    return nets


def save(tag):
    STORE.mkdir(exist_ok=True)
    nets = netlist()
    (STORE / f"{tag}.json").write_text(json.dumps(nets, indent=1, sort_keys=True))
    print(f"保存 {tag}: {len(nets)} ネット / {sum(len(v) for v in nets.values())} ピン")


def check(tag):
    old = json.loads((STORE / f"{tag}.json").read_text())
    new = netlist()
    o = {tuple(v): k for k, v in old.items()}
    n = {tuple(v): k for k, v in new.items()}

    removed = [(o[p], p) for p in o if p not in n]
    added = [(n[p], p) for p in n if p not in o]
    renamed = [(o[p], n[p]) for p in o if p in n and o[p] != n[p]]

    for name, pins in sorted(removed):
        print(f"  消えた   {name}: {', '.join(pins)}")
    for name, pins in sorted(added):
        print(f"  増えた   {name}: {', '.join(pins)}")
    for a, b in sorted(renamed):
        print(f"  改名     {a} -> {b}")
    if not (removed or added or renamed):
        print(f"一致（{len(new)} ネット）")
        return 0
    print(f"差分あり: 消えた {len(removed)} / 増えた {len(added)} / 改名 {len(renamed)}")
    return 1


if __name__ == "__main__":
    cmd, tag = sys.argv[1], sys.argv[2]
    sys.exit(save(tag) if cmd == "save" else check(tag))
