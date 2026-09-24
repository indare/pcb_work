#!/usr/bin/env python3
"""TMUX7612 の 1 µF デカップ（C315–C318、0603）を AmpBankSwitch の裏面に置く。

DS p34: VDD/VSS それぞれ 0.1 µF と 1 µF。**小さい方をピン直近**なので、既存の 100 nF はそのまま
ピン側に残し、1 µF はその外側に置く。電源パッドは同じレールの B.Cu に短く、GND パッドは裏の A_GND ベタで受ける。

`update_pcb_from_sch.py` は使わない（回路図で基板対象外の部品を PCB から消す作りで、
パッドにネットも付けない）。ここでは足す部品だけを、netlist から読んだネット・KIID パス・シート名つきで置く。

    python3 AudioV2/scripts/place_tmux_1u.py --dry-run   # 衝突だけ見る
    python3 AudioV2/scripts/place_tmux_1u.py
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).resolve().parent))
import amp_sel_hop as hop  # noqa: E402
from pcb_preview import sheet_region  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SCH = ROOT / "AudioV2" / "AudioV2Case.kicad_sch"
PCB = ROOT / "AudioV2" / "AudioV2Case.kicad_pcb"
XML = ROOT / "out" / "place_tmux_1u.xml"

# ref: (x, y, 回転[deg], 電源パッドから既存の同ネット銅への B 折れ線（パッド中心から）)
PLACE: dict[str, tuple[float, float, float, list[tuple[float, float]]]] = {
    # U311 VDD: +15V レール（y=159.85）上、C311 の外側（西）。GND パッドは北へ
    "C315": (548.80, 158.9875, 90, []),
    # U311 VSS: C312 の北に並べ、-15V は C312 の -15V パッドへ 45° で降ろす
    "C316": (549.7175, 166.80, 0, [(551.27, 167.49), (551.27, 168.84)]),
    # U312 VDD: +15V の縦レール（x=504.642）上、C313 の外側（北）。GND パッドは東へ
    "C317": (505.5045, 155.30, 0, []),
    # U312 VSS: -15V レール（y=172.498）上、C314 の外側（東）。GND パッドは南へ
    "C318": (507.80, 173.3605, 90, []),
}


# 新しい 1 µF と隣り合い、参照番号のシルクを置き直すことがある既存の 100 nF
NEIGHBORS = ["C311", "C312", "C313", "C314"]


def fp_dirs() -> list[Path]:
    env = os.environ.get("KICAD10_FOOTPRINT_DIR")
    cands = [Path(env)] if env else []
    cands += [Path("/usr/share/kicad/footprints"),
              Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"),
              Path(r"C:\Program Files\KiCad\10.0\share\kicad\footprints")]
    return [c for c in cands if c.is_dir()]


def load_fp(lib_id: str):
    lib, name = lib_id.split(":", 1)
    for d in fp_dirs():
        pretty = d / f"{lib}.pretty"
        if (pretty / f"{name}.kicad_mod").is_file():
            return pcbnew.PCB_IO_KICAD_SEXPR().FootprintLoad(str(pretty), name, False)
    raise SystemExit(f"フットプリントが見つからない: {lib_id}（KICAD10_FOOTPRINT_DIR で明示）")


def netlist(refs: set[str]) -> dict[str, dict]:
    XML.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([os.environ.get("KICAD_CLI", "kicad-cli"), "sch", "export", "netlist", "--format", "kicadxml",
                    "-o", str(XML), str(SCH)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    root = ET.parse(XML).getroot()
    out: dict[str, dict] = {}
    for c in root.iter("comp"):
        ref = c.get("ref")
        if ref not in refs:
            continue
        sp = c.find("sheetpath")
        out[ref] = {"footprint": c.findtext("footprint"), "value": c.findtext("value"),
                    "path": sp.get("tstamps") + c.findtext("tstamps").strip(),
                    "sheetname": sp.get("names"),
                    "sheetfile": next((p.get("value") for p in c.iter("property") if p.get("name") == "Sheetfile"), ""),
                    "nets": {}}
    for n in root.iter("net"):
        for node in n.iter("node"):
            if node.get("ref") in out:
                out[node.get("ref")]["nets"][node.get("pin")] = n.get("name")
    missing = refs - set(out)
    if missing:
        raise SystemExit(f"回路図に無い: {sorted(missing)}")
    return out


def _silk_boxes(board, skip_ref: str):
    """裏のパッドの外形と、裏シルクの他の線・文字（skip_ref の参照番号そのものは除く）。"""
    out = []
    for f in board.GetFootprints():
        for p in f.Pads():
            if p.IsOnLayer(hop.B):
                out.append(p.GetBoundingBox())
        for g in f.GraphicalItems():
            if g.GetLayer() == pcbnew.B_SilkS:
                out.append(g.GetBoundingBox())
        for fld in (f.Reference(), f.Value()):
            if fld.GetLayer() == pcbnew.B_SilkS and fld.IsVisible():
                if f.GetReference() == skip_ref and fld.GetText() == skip_ref:
                    continue
                out.append(fld.GetBoundingBox())
    return out


def place_ref(board, fp, margin=0.15) -> bool:
    """参照番号の文字を、裏のパッド・他のシルクに重ならない場所へ動かす（部品のまわりを順に試す）。"""
    ref = fp.Reference()
    c = hop.xy(fp.GetPosition())
    boxes = _silk_boxes(board, fp.GetReference())
    m = hop.iu(margin)
    for d in (1.5, 2.1, 2.7, 3.3):
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)):
            ref.SetPosition(hop.P(c[0] + dx * d, c[1] + dy * d))
            bb = ref.GetBoundingBox()
            bb.Inflate(m)
            if not any(bb.Intersects(o) for o in boxes):
                return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    board = pcbnew.LoadBoard(str(PCB))
    info = netlist(set(PLACE))
    clr = hop.design(board)["clr"]
    problems, added = [], []
    for ref, (x, y, rot, stub) in PLACE.items():
        if board.FindFootprintByReference(ref) is not None:
            raise SystemExit(f"{ref} は既に PCB にある")
        c = info[ref]
        fp = load_fp(c["footprint"])
        lib, name = c["footprint"].split(":", 1)
        fp.SetFPID(pcbnew.LIB_ID(lib, name))   # ライブラリ名が無いと DRC の schematic parity が不一致にする
        fp.SetReference(ref)
        fp.SetValue(c["value"])
        fp.SetPath(pcbnew.KIID_PATH(c["path"]))
        fp.SetSheetname(c["sheetname"])
        fp.SetSheetfile(c["sheetfile"])
        board.Add(fp)
        fp.SetPosition(hop.P(x, y))
        fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM if hasattr(pcbnew, "FLIP_DIRECTION_TOP_BOTTOM") else False)
        fp.SetOrientationDegrees(rot)
        for p in fp.Pads():
            netname = c["nets"][p.GetNumber()]
            ni = board.FindNet(netname)
            if ni is None:
                raise SystemExit(f"PCB にネット {netname} が無い")
            p.SetNet(ni)
        added.append(fp)
        # 衝突（他ネットの B 銅）
        for p in fp.Pads():
            obs = hop.Obstacles(board, p.GetNetCode(), layers=(hop.B,))
            pp = hop.xy(p.GetPosition())
            hits = obs.hits(hop.B, p.GetEffectiveShape(hop.B), (pp[0], pp[1], pp[0], pp[1]), clr)
            hits = [h for h in hits if not h.startswith(f"pad {ref}.")]
            problems += [f"{ref}.{p.GetNumber()} {p.GetNetname()} @{pp}: {h}" for h in hits]
        # 電源パッドから既存レールへの短い B
        pwr = next(p for p in fp.Pads() if p.GetNetname() in ("/+15V", "/-15V"))
        pts = [hop.xy(pwr.GetPosition())] + stub
        obs = hop.Obstacles(board, pwr.GetNetCode(), layers=(hop.B,))
        for p, q in zip(pts, pts[1:]):
            problems += [f"{ref} 電源 B {p}->{q}: {h}" for h in obs.seg_hits(hop.B, p, q, 0.5, clr)
                         if not h.startswith(f"pad {ref}.")]
        print(f"{ref} {c['value']} ({x},{y}) rot={rot} 裏: "
              + ", ".join(f"{p.GetNumber()}={p.GetNetname()}@{hop.xy(p.GetPosition())}" for p in fp.Pads())
              + f"  電源 B: {' → '.join(f'({q[0]:.2f},{q[1]:.2f})' for q in pts)}")
    if problems:
        print("衝突あり。保存しない:")
        for pr in problems:
            print("  ", pr)
        return 2
    if a.dry_run:
        print("dry-run: 保存しない")
        return 0
    for ref, (x, y, rot, stub) in PLACE.items():
        fp = board.FindFootprintByReference(ref)
        pwr = next(p for p in fp.Pads() if p.GetNetname() in ("/+15V", "/-15V"))
        pts = [hop.xy(pwr.GetPosition())] + stub
        join = pts[-1]
        # 合流点が既存トラックの途中なら分割して、端点で確実につなぐ
        for t in list(board.GetTracks()):
            if hop.is_via(t) or t.GetNetCode() != pwr.GetNetCode() or t.GetLayer() != hop.B:
                continue
            s, e = hop.xy(t.GetStart()), hop.xy(t.GetEnd())
            if hop.on_segment(join, s, e) and not hop.near(join, s) and not hop.near(join, e):
                w = t.GetWidth()
                board.Remove(t)
                hop.add_track(board, s, join, hop.B, w, pwr.GetNetCode())
                hop.add_track(board, join, e, hop.B, w, pwr.GetNetCode())
                break
        for p, q in zip(pts, pts[1:]):
            hop.add_track(board, p, q, hop.B, hop.iu(0.5), pwr.GetNetCode())
    # 参照番号のシルク: 新しい4個と、それに隣り合う既存の 100 nF を、重ならない場所へ
    for ref in list(PLACE) + NEIGHBORS:
        fp = board.FindFootprintByReference(ref)
        if not place_ref(board, fp):
            print(f"  ⚠ {ref} の参照番号を置ける場所が無い（そのまま）")
    print(f"ゾーン再充填: {hop.refill(board, sheet_region(board, 'AmpBankSwitch'))} 枚")
    board.Save(str(PCB))
    print(f"保存: {PCB}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
