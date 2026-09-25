#!/usr/bin/env python3
"""TMUX7612 の 100 nF（C311–C314）を 0603 にして、本体直下の裏（ピンの足元）へ寄せる。

いままでは VDD/VSS から外側へ出たファンアウトの先のビアから裏を 5 mm ほど走って 1206 の 100 nF に
届いていた（ピン→パッド中心 4〜6 mm、GND 側 7〜11 mm）。TSSOP は底面パッドが無く本体の下は
表も裏も空いている（表は南北 D の直結だけ）ので、次のようにする:

  - VDD（13）/ VSS（4）からパッド列の**内側**へ短い引き出し → 本体の下にビア
  - 100 nF（0603）を本体直下の裏に縦置き。電源パッドはビアの隣、GND パッドは中央の A_GND ビア側
  - GND（5）からも内側へ引き出して中央の A_GND ビアへ（外側への既存の GND も残す）
  - 外側の既存の電源ファンアウトとビアはそのまま（供給と 1 µF はそちらから）

U312 は本体の下に A_GND ビアがもう1本あり -15V のパッドに重なるので外す
（pin5 からの内側の引き出しと中央ビアが代わりを持つ）。
TMUX の DS §8.5: デカップは 0.1 µF をピン直近・1 µF はその次。1 µF（C315–C318）は据え置き。

    python3 AudioV2.1/scripts/place_tmux_100n_underbody.py --dry-run
    python3 AudioV2.1/scripts/place_tmux_100n_underbody.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).resolve().parent))
import amp_sel_hop as hop  # noqa: E402
import place_tmux_1u as p1u  # noqa: E402
from pcb_preview import sheet_region  # noqa: E402

PCB = Path(__file__).resolve().parents[1] / "AudioV2Case.kicad_pcb"
C0603 = "Capacitor_SMD:C_0603_1608Metric_Pad1.08x0.95mm_HandSolder"
W = 0.25  # 引き出しの幅 [mm]

# TMUX ごと: VDD/VSS ビア、GND の引き出し（pin5 → 折れ点 → 中央ビア）、100 nF の (x, y, 回転, 電源パッド→ビアの B)
SPEC = {
    "U311": {"vdd_via": (555.725, 164.55), "vss_via": (555.725, 167.35),
             "gnd_via": (556.06, 165.95), "gnd_path": [(556.375, 166.265)],
             "C311": (554.95, 165.4125, 270, [(555.725, 164.55)]),
             "C312": (556.5, 166.4875, 270, [(555.725, 167.35)]),
             # C312 が抜けると -15V の B（外側ビア→C316）が C312 のパッド位置で 3 µm 途切れるのでつなぐ
             "joins": [((551.27, 168.84), (551.273, 168.84))]},
    "U312": {"vdd_via": (504.685, 164.12), "vss_via": (504.685, 166.92),
             "gnd_via": (505.01, 165.50), "gnd_path": [(505.335, 165.825)],
             "delete_vias": [(505.96, 167.0)],
             "C313": (503.91, 164.9825, 270, [(504.685, 164.12)]),
             "C314": (505.46, 166.0575, 270, [(504.685, 166.92)])},
}


def swap_to_0603(board, ref, x, y, rot):
    old = board.FindFootprintByReference(ref)
    if old.GetFPIDAsString() == C0603:
        raise SystemExit(f"{ref} は既に 0603（適用済み）")
    nets = {p.GetNumber(): p.GetNetname() for p in old.Pads()}
    path = pcbnew.KIID_PATH(old.GetPath().AsString())
    sn, sf, val = old.GetSheetname(), old.GetSheetfile(), old.GetValue()
    fp = p1u.load_fp(C0603)
    lib, name = C0603.split(":", 1)
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    fp.SetReference(ref)
    fp.SetValue(val)
    fp.SetPath(path)
    fp.SetSheetname(sn)
    fp.SetSheetfile(sf)
    board.Add(fp)
    fp.SetPosition(hop.P(x, y))
    fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
    fp.SetOrientationDegrees(rot)
    for p in fp.Pads():
        p.SetNet(board.FindNet(nets[p.GetNumber()]))
    # Remove() だと外した部品の Python ラッパーが回収されるときに SWIG の型表が壊れ、以後の
    # FOOTPRINT / PADS が 'SwigPyObject' になる（2026-09-24 に切り分け）。Delete() で C++ 側ごと消す
    board.Delete(old)
    return fp


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    board = pcbnew.LoadBoard(str(PCB))
    clr = hop.design(board)["clr"]
    nc = board.GetNetcodeFromNetname
    new_items = []   # (層, 始点, 終点, ネット) — あとで衝突を見る
    for u, s in SPEC.items():
        pads = {p.GetNumber(): hop.xy(p.GetPosition()) for p in board.FindFootprintByReference(u).Pads()}
        for dv in s.get("delete_vias", []):
            v = next(t for t in board.GetTracks() if hop.is_via(t) and hop.near(hop.xy(t.GetPosition()), dv))
            print(f"{u}: 本体下の {v.GetNetname()} ビア {dv} を外す")
            board.Remove(v)
        for pin, net, key in (("13", "/+15V", "vdd_via"), ("4", "/-15V", "vss_via")):
            v = s[key]
            hop.add_track(board, pads[pin], v, hop.F, hop.iu(W), nc(net))
            sample = next(t for t in board.GetTracks() if hop.is_via(t) and t.GetNetname() == net)
            hop.add_via_like(board, v, sample, nc(net))
            new_items += [("F", pads[pin], v, net), ("via", v, v, net)]
        g = [pads["5"]] + s["gnd_path"] + [s["gnd_via"]]
        for p, q in zip(g, g[1:]):
            hop.add_track(board, p, q, hop.F, hop.iu(W), nc("/A_GND"))
            new_items.append(("F", p, q, "/A_GND"))
        for ref in (k for k in s if k.startswith("C")):
            x, y, rot, stub = s[ref]
            fp = swap_to_0603(board, ref, x, y, rot)
            pwr = next(p for p in fp.Pads() if p.GetNetname() in ("/+15V", "/-15V"))
            pts = [hop.xy(pwr.GetPosition())] + stub
            for p, q in zip(pts, pts[1:]):
                hop.add_track(board, p, q, hop.B, hop.iu(W), pwr.GetNetCode())
            print(f"{u} {ref}: " + ", ".join(f"{p.GetNumber()}={p.GetNetname()}@{hop.xy(p.GetPosition())}" for p in fp.Pads()))
        for p, q in s.get("joins", []):
            hop.add_track(board, p, q, hop.B, hop.iu(0.5), nc("/-15V"))
    # 足した銅が他ネットに触れていないか（KiCad の形状で）
    problems = []
    for kind, p, q, net in new_items:
        obs = hop.Obstacles(board, nc(net))
        if kind == "via":
            problems += [f"ビア {p} {net}: {h}" for h in obs.via_hits(p, 0.6, 0.3, clr, 0.25)]
        else:
            problems += [f"F {p}->{q} {net}: {h}" for h in obs.seg_hits(hop.F, p, q, W, clr)]
    if problems:
        print("衝突あり。保存しない:")
        for pr in problems:
            print("  ", pr)
        return 2
    for ref in ("C311", "C312", "C313", "C314", "C315", "C316", "C317", "C318"):
        if not p1u.place_ref(board, board.FindFootprintByReference(ref)):
            print(f"  ⚠ {ref} の参照番号を置ける場所が無い（そのまま）")
    if a.dry_run:
        print("dry-run: 保存しない")
        return 0
    print(f"ゾーン再充填: {hop.refill(board, sheet_region(board, 'AmpBankSwitch'))} 枚")
    board.Save(str(PCB))
    print(f"保存: {PCB}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
