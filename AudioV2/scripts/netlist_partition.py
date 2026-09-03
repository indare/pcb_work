#!/usr/bin/env python3
"""ネットリストを「ピンの集合の集合」として比べる。

シートを統合するとネット**名**は変わる（`/OutputStage/PHONE_PRE_L` が
`/MotherBoard/PHONE_PRE_L` になる等）が、**どのピンが同じネットに属するかの分割**は
変わってはいけない。名前ではなく分割で比べるのはそのため。

`sch_drift.py` はワイヤもジャンクションも見ないので、配線を持つシートの検証には使えない。
統合・移設の検証はこちらを使うこと。

    python3 AudioV2/scripts/netlist_partition.py before.net after.net
"""

from __future__ import annotations

import re
import sys


def partition(path: str) -> dict[frozenset[str], str]:
    t = open(path, encoding="utf-8").read()
    sec = t[t.index("\t(nets"):]
    out: dict[frozenset[str], str] = {}
    pat = re.compile(r'\(net\n\t+\(code "\d+"\)\n\t+\(name "([^"]+)"\)([\s\S]*?)'
                     r'(?=\n\t\t\(net\n|\n\t\)\n)')
    for m in pat.finditer(sec):
        nodes = re.findall(r'\(ref "([^"]+)"\)\n\s*\(pin "([^"]+)"\)', m.group(2))
        key = frozenset(f"{r}.{p}" for r, p in nodes)
        if key:
            out[key] = m.group(1)
    return out


def main() -> int:
    a, b = partition(sys.argv[1]), partition(sys.argv[2])
    only_a, only_b = set(a) - set(b), set(b) - set(a)
    print(f"前: {len(a)} ネット / 後: {len(b)} ネット")
    renamed = [(a[k], b[k]) for k in set(a) & set(b) if a[k] != b[k]]
    if renamed:
        print(f"同じ分割で名前だけ変わった: {len(renamed)} 件")
        for x, y in sorted(renamed)[:20]:
            print(f"    {x}  ->  {y}")
    if not only_a and not only_b:
        print("✅ 分割は完全に一致（電気的に同じ）")
        return 0
    print(f"❌ 分割が変わった: 前だけ {len(only_a)} / 後だけ {len(only_b)}")
    for k in sorted(only_a, key=lambda s: a[s])[:15]:
        print(f"  前だけ [{a[k]}] {' '.join(sorted(k))[:160]}")
    for k in sorted(only_b, key=lambda s: b[s])[:15]:
        print(f"  後だけ [{b[k]}] {' '.join(sorted(k))[:160]}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
