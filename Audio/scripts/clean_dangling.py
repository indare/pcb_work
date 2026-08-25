#!/usr/bin/env python3
"""指定ネットの宙に浮いた配線を、末端から繰り返し剥がして消す。

1 本ずつ「両端が何かに触れているか」を見るだけだと、
スタブが数本つながっている場合に互いを支えあって残ってしまう。
そこで「自由端を持つ配線を消す」を、消えるものが無くなるまで繰り返す。

  確認: kicad-python clean_dangling.py board.kicad_pcb
  適用: kicad-python clean_dangling.py board.kicad_pcb --apply
"""
import argparse
import math

import pcbnew

MM = pcbnew.ToMM

NETS = {"Net-(AMP1A--)", "Net-(AMP1-Pad1)", "Net-(AMP1B--)", "Net-(AMP1-Pad7)"}
ISLAND = (219.0, 71.0, 287.0, 121.0)
EPS = 0.01


def prad(p):
    s = p.GetSize()
    return math.hypot(MM(s.x), MM(s.y)) / 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pcb")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    board = pcbnew.LoadBoard(args.pcb)
    x0, y0, x1, y1 = ISLAND

    # 固定端（パッドとビア）
    anchors = {}
    for f in board.GetFootprints():
        for pd in f.Pads():
            n = pd.GetNetname()
            if n in NETS:
                q = pd.GetPosition()
                anchors.setdefault(n, []).append((MM(q.x), MM(q.y), prad(pd)))
    for t in board.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() in NETS:
            q = t.GetPosition()
            anchors.setdefault(t.GetNetname(), []).append((MM(q.x), MM(q.y), 0.3))

    # 対象の配線を (uuid, net, 両端, 長さ, 層) で持つ
    items = []
    for t in board.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T or t.GetNetname() not in NETS:
            continue
        s, e = t.GetStart(), t.GetEnd()
        if not (x0 < MM(s.x) < x1 and y0 < MM(s.y) < y1):
            continue
        items.append(dict(uuid=t.m_Uuid.AsString(), net=t.GetNetname(),
                          a=(MM(s.x), MM(s.y)), b=(MM(e.x), MM(e.y)),
                          L=MM(t.GetLength()), layer=board.GetLayerName(t.GetLayer())))

    alive = {i["uuid"]: i for i in items}
    doomed = []
    while True:
        drop = []
        for uid, it in alive.items():
            for end in (it["a"], it["b"]):
                held = any(math.hypot(end[0] - ax, end[1] - ay) <= ar
                           for ax, ay, ar in anchors.get(it["net"], []))
                if not held:
                    held = any(o is not it and o["net"] == it["net"]
                               and (math.hypot(end[0] - o["a"][0], end[1] - o["a"][1]) < EPS
                                    or math.hypot(end[0] - o["b"][0], end[1] - o["b"][1]) < EPS)
                               for o in alive.values())
                if not held:
                    drop.append(uid)
                    break
        if not drop:
            break
        for uid in drop:
            doomed.append(alive.pop(uid))

    if not doomed:
        print("宙に浮いた配線なし。")
        return
    print(f"宙に浮いた配線 {len(doomed)} 本 / 計 {sum(d['L'] for d in doomed):.2f} mm")
    for d in doomed:
        print(f"   {d['layer']:5s} {d['L']:6.2f} mm  {d['net']}  "
              f"({d['a'][0]:.2f},{d['a'][1]:.2f})→({d['b'][0]:.2f},{d['b'][1]:.2f})")
    if not args.apply:
        print("\n[dry-run] --apply で削除する。")
        return

    kill = {d["uuid"] for d in doomed}
    for t in list(board.GetTracks()):
        if t.m_Uuid.AsString() in kill:
            board.Remove(t)
    board.Save(args.pcb)
    print(f"\n{len(kill)} 本を削除して保存した。")


if __name__ == "__main__":
    main()
