#!/usr/bin/env python3
"""AudioV2 の回路図から「機械的に導出できる事実」だけを出す（読み取り専用）。

査読の土台。`SOURCE_OF_TRUTH.md` のとおり、部品数・ネット・ピン接続の正は回路図であって
ドキュメントではない。ドキュメントの数値は書かれた当時のもので、**査読で持ち出す前に
ここへ降ろして確かめる**。実際 2026-09-05 の否定側査読で出た最大の指摘（レール容量が
102 µF ではなく約 250 µF）は、シートが何回インスタンス化されているかを数え直しただけで出た。

    python3 AudioV2/scripts/sch_facts.py all           # 査読の入口。まずこれ
    python3 AudioV2/scripts/sch_facts.py tree          # 階層とインスタンス数（×何枚）
    python3 AudioV2/scripts/sch_facts.py bom           # 部品表（インスタンス展開後）
    python3 AudioV2/scripts/sch_facts.py rails         # レールごとの容量・ピン数の積み上げ
    python3 AudioV2/scripts/sch_facts.py nets --net +15V
    python3 AudioV2/scripts/sch_facts.py iface         # 親のシートピン vs 子の階層ラベル
    python3 AudioV2/scripts/sch_facts.py dangling      # どこにも載っていないピン
    python3 AudioV2/scripts/sch_facts.py aliases       # 1本のネットに別名が複数
    python3 AudioV2/scripts/sch_facts.py pin <REF>     # 部品のピンごとのネット名

`--json` で機械可読。`--root` で別の階層ルートを指定できる（既定 AudioV2/AudioV2Case.kicad_sch）。

**このファイルは何も書かない。** 生成シートにも素材にも触れない。

⚠ これは `kicad-cli` の代わりではない。ERC の正は `docker/kicad-cloud-build/kicad-run.sh erc`。
   ここが出す接続は S 式から組み直した再構成で、2026-09-06 に次を実測して裏を取ってある:

   - **部品数**: instance path を展開したユニーク参照が、CLAUDE.md が載せている
     `kicad-cli` netlist の期待値と一致する。**ここがずれたら再構成が壊れているサイン**。
     ⚠ **期待値の正は CLAUDE.md の表であって、ここではない。**ここに数字を書き写すと
     設計が動いたときに腐り、正常な回路を「壊れている」と誤判定する（2026-09-07 に
     実際そうなった —— 373 と書いたまま設計が 370 に動いていた）
   - **ピン座標**: シンボル配置＋回転＋ミラーから出したピン先が、wire / label / junction /
     no_connect のいずれかに載る。**現状 0 本が浮き**（`dangling` で確認できる）。
     2026-09-06 時点で浮いていた 12 本は `MotherBoard` の PT2314 未使用入力で、
     2026-09-07 に `no_connect` を立てて解消した
   - **ワイヤの結線規則**: 端点同士は結ぶ。ワイヤの途中に**別のワイヤの端点**が来ている箇所は
     junction が無ければ結ばない（KiCad と同じ）。現状 0 件。ラベル・ピン・シートピンは
     ワイヤの途中でも結ぶ（こちらは junction を要求しない）
   - **NetTie は結ばない**（KiCad のネットリストと同じ。銅箔で1点だけ繋ぐのが趣旨）。
     どのネット同士を繋いでいるかは `nets` が一覧に出す

"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

TOL = 1e-3          # 座標一致の許容（mm）。KiCad の格子は 1.27 mm なので十分細かい
NDIG = 3


# --------------------------------------------------------------------------
# S式パーサ（読むだけ。書き戻しには使わない）
# --------------------------------------------------------------------------

def _tokenize(s: str):
    i, n, out = 0, len(s), []
    while i < n:
        c = s[i]
        if c in " \t\r\n":
            i += 1
        elif c == "(" or c == ")":
            out.append(c)
            i += 1
        elif c == '"':
            j, buf = i + 1, []
            while j < n:
                if s[j] == "\\":
                    buf.append(s[j + 1])
                    j += 2
                    continue
                if s[j] == '"':
                    break
                buf.append(s[j])
                j += 1
            out.append(("".join(buf), True))
            i = j + 1
        else:
            j = i
            while j < n and s[j] not in " \t\r\n()":
                j += 1
            out.append((s[i:j], False))
            i = j
    return out


def sexpr(text: str) -> list:
    toks = _tokenize(text)
    pos = 0

    def node():
        nonlocal pos
        pos += 1                       # '('
        items = [toks[pos][0]]
        pos += 1
        while toks[pos] != ")":
            if toks[pos] == "(":
                items.append(node())
            else:
                items.append(toks[pos][0])
                pos += 1
        pos += 1                       # ')'
        return items

    return node()


def kids(n, name: str) -> list:
    return [c for c in n[1:] if isinstance(c, list) and c[0] == name]


def kid(n, name: str):
    k = kids(n, name)
    return k[0] if k else None


def prop(n, name: str, default: str = "") -> str:
    for p in kids(n, "property"):
        if p[1] == name:
            return p[2]
    return default


def pt(x, y) -> tuple[float, float]:
    return (round(float(x), NDIG), round(float(y), NDIG))


# --------------------------------------------------------------------------
# シートファイル
# --------------------------------------------------------------------------

@dataclass
class Sym:
    ref: str                                   # ファイル上の参照（instances で上書きされる）
    lib_id: str
    value: str
    unit: int
    dnp: bool
    at: tuple[float, float, float]
    pins: list[tuple[str, str, tuple[float, float]]] = field(default_factory=list)
    inst: dict[str, str] = field(default_factory=dict)   # instance path -> reference


@dataclass
class ChildRef:
    name: str
    file: str
    uuid: str
    pins: list[tuple[str, tuple[float, float]]]


@dataclass
class SheetFile:
    path: Path
    uuid: str
    syms: list[Sym] = field(default_factory=list)
    children: list[ChildRef] = field(default_factory=list)
    wires: list[tuple[tuple[float, float], tuple[float, float]]] = field(default_factory=list)
    junctions: set = field(default_factory=set)
    labels: list[tuple[str, tuple[float, float]]] = field(default_factory=list)
    hlabels: list[tuple[str, tuple[float, float]]] = field(default_factory=list)
    glabels: list[tuple[str, tuple[float, float]]] = field(default_factory=list)
    ncs: set = field(default_factory=set)

    @property
    def name(self) -> str:
        return self.path.stem


def _lib_pins(root) -> dict[str, list[tuple[str, str, float, float, int]]]:
    """lib_symbols から (ピン番号, ピン名, x, y, ユニット番号) を取る。座標は Y 上向き。"""
    out: dict[str, list] = {}
    ls = kid(root, "lib_symbols")
    if not ls:
        return out
    for sym in kids(ls, "symbol"):
        pins = []
        for sub in kids(sym, "symbol"):
            m = re.match(r"^(.*)_(\d+)_(\d+)$", sub[1])
            unit = int(m.group(2)) if m else 0
            for p in kids(sub, "pin"):
                at = kid(p, "at")
                num = kid(p, "number")
                nm = kid(p, "name")
                pins.append((num[1] if num else "?", nm[1] if nm else "",
                             float(at[1]), float(at[2]), unit))
        out[sym[1]] = pins
    return out


def _place(px: float, py: float, ix: float, iy: float, rot: float,
           mx: bool, my: bool) -> tuple[float, float]:
    """シンボル内座標（Y 上向き）を図面座標（Y 下向き）へ。

    KiCad の実ファイルで検証済み: 全シートのピンが wire / label / junction / no_connect に載る。
    """
    x, y = px, -py
    a = math.radians(rot)
    ca, sa = math.cos(a), math.sin(a)
    dx, dy = x * ca + y * sa, -x * sa + y * ca
    # ⚠ ミラーは回転の**後**に図面座標で掛かる（2026-09-09 に kicad-cli のネットリストで確認:
    #    MeasureControl の J1602 = rot 270 + mirror y は、回転後の dx が反転した位置で結線される）。
    #    回転前に掛けると rot 90/270 で反転する軸が入れ替わる。rot 0/180 では前後どちらでも同じ。
    if my:
        dx = -dx
    if mx:
        dy = -dy
    return pt(ix + dx, iy + dy)


def load_sheet(path: Path) -> SheetFile:
    root = sexpr(path.read_text(encoding="utf-8"))
    lp = _lib_pins(root)
    sh = SheetFile(path=path, uuid=kid(root, "uuid")[1])

    for s in kids(root, "symbol"):
        at = kid(s, "at")
        ix, iy = float(at[1]), float(at[2])
        rot = float(at[3]) if len(at) > 3 else 0.0
        mir = kid(s, "mirror")
        mx = bool(mir and "x" in mir[1:])
        my = bool(mir and "y" in mir[1:])
        unit = int(kid(s, "unit")[1]) if kid(s, "unit") else 1
        lib_id = kid(s, "lib_id")[1]
        sym = Sym(ref=prop(s, "Reference"), lib_id=lib_id, value=prop(s, "Value"),
                  unit=unit, dnp=bool(kid(s, "dnp") and kid(s, "dnp")[1] == "yes"),
                  at=(ix, iy, rot))
        for num, nm, px, py, pu in lp.get(lib_id, []):
            if pu not in (0, unit):
                continue
            sym.pins.append((num, nm, _place(px, py, ix, iy, rot, mx, my)))
        insts = kid(s, "instances")
        if insts:
            for proj in kids(insts, "project"):
                for p in kids(proj, "path"):
                    sym.inst[p[1]] = kid(p, "reference")[1]
        sh.syms.append(sym)

    for c in kids(root, "sheet"):
        pins = [(p[1], pt(kid(p, "at")[1], kid(p, "at")[2])) for p in kids(c, "pin")]
        sh.children.append(ChildRef(name=prop(c, "Sheetname"), file=prop(c, "Sheetfile"),
                                    uuid=kid(c, "uuid")[1], pins=pins))

    for w in kids(root, "wire"):
        xy = kids(kid(w, "pts"), "xy")
        sh.wires.append((pt(xy[0][1], xy[0][2]), pt(xy[1][1], xy[1][2])))
    for j in kids(root, "junction"):
        sh.junctions.add(pt(kid(j, "at")[1], kid(j, "at")[2]))
    for n in kids(root, "no_connect"):
        sh.ncs.add(pt(kid(n, "at")[1], kid(n, "at")[2]))
    for k, dst in (("label", sh.labels), ("hierarchical_label", sh.hlabels),
                   ("global_label", sh.glabels)):
        for l in kids(root, k):
            dst.append((l[1], pt(kid(l, "at")[1], kid(l, "at")[2])))
    return sh


# --------------------------------------------------------------------------
# 階層の展開
# --------------------------------------------------------------------------

@dataclass
class Inst:
    """シートの1インスタンス。同じファイルでも置かれた回数だけ存在する。"""
    key: str                 # "/uuid/uuid/..." — KiCad の instance path と同じ綴り
    label: str               # "MotherBoard/AmpBankSwitch/AmpChannel(a1000020…)"
    sheet: SheetFile
    parent: "Inst | None"
    parent_pins: list[tuple[str, tuple[float, float]]]   # 親側シートピン（親の座標系）


def build_tree(root_path: Path) -> tuple[list[Inst], dict[str, SheetFile]]:
    cache: dict[str, SheetFile] = {}

    def get(p: Path) -> SheetFile:
        if p.name not in cache:
            cache[p.name] = load_sheet(p)
        return cache[p.name]

    root = get(root_path)
    out: list[Inst] = []

    def walk(sheet: SheetFile, key: str, label: str, parent: Inst | None,
             parent_pins: list) -> None:
        inst = Inst(key=key, label=label, sheet=sheet, parent=parent, parent_pins=parent_pins)
        out.append(inst)
        for c in sheet.children:
            child_path = root_path.parent / c.file
            if not child_path.exists():
                continue
            walk(get(child_path), f"{key}/{c.uuid}",
                 f"{label}/{c.name}" if label else c.name, inst, c.pins)

    walk(root, f"/{root.uuid}", root.name, None, [])
    return out, cache


# --------------------------------------------------------------------------
# 接続の再構成
# --------------------------------------------------------------------------

class UF:
    def __init__(self) -> None:
        self.p: dict = {}

    def find(self, a):
        self.p.setdefault(a, a)
        while self.p[a] != a:
            self.p[a] = self.p[self.p[a]]
            a = self.p[a]
        return a

    def union(self, a, b) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[ra] = rb


def _on_seg(p, a, b) -> bool:
    if min(a[0], b[0]) - TOL > p[0] or p[0] > max(a[0], b[0]) + TOL:
        return False
    if min(a[1], b[1]) - TOL > p[1] or p[1] > max(a[1], b[1]) + TOL:
        return False
    cross = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
    return abs(cross) < TOL


NETTIE_RE = re.compile(r"NetTie", re.I)


@dataclass
class Net:
    name: str
    pins: list[str] = field(default_factory=list)          # "R610.1"
    detail: list[tuple[str, str, str, str]] = field(default_factory=list)  # ref,pin,libid,value
    names: set = field(default_factory=set)                 # そのネットに載っていた全ての名前
    sheets: set = field(default_factory=set)


class Design:
    """階層を展開してネットを組み直したもの。"""

    def __init__(self, root_path: Path) -> None:
        self.insts, self.files = build_tree(root_path)
        self.uf = UF()
        self.suspect: list[str] = []      # 黙って結ばなかった接触
        self.dangling: list[tuple[str, str, str, str]] = []
        self._tie_syms: list[tuple] = []
        self.nc_pins: set[str] = set()    # no_connect が置かれているピン（"U402.6"）
        self.ties: list[tuple[str, str, list[str]]] = []   # (インスタンス, 参照, 繋ぐネット名)
        self._connect()
        self._name()

    # -- 1段ぶんの結線 ---------------------------------------------------
    def _connect(self) -> None:
        """KiCad の結線規則を写す。

        - ワイヤの両端は同じノード。端点が一致するワイヤ同士は繋がる
        - ワイヤの途中に**別のワイヤの端点**が来ても、junction が無ければ繋がらない
        - ラベル・ピン・シートピン・no_connect は、ワイヤの途中でも繋がる（junction 不要）
        - 同じシートの中の同名ラベルは同じネット（ローカルスコープ）
        """
        for inst in self.insts:
            sh = inst.sheet
            node = lambda p: (inst.key, p)          # noqa: E731

            for a, b in sh.wires:
                self.uf.union(node(a), node(b))

            def on_wires(p):
                return [(a, b) for a, b in sh.wires if _on_seg(p, a, b)]

            # 端子側（ラベル・ピン・シートピン・NC・junction）はワイヤの途中でも載る
            terminals: list[tuple[tuple[float, float], str]] = []
            for name, p in sh.labels + sh.hlabels + sh.glabels:
                terminals.append((p, f"ラベル {name}"))
            for p in sh.junctions:
                terminals.append((p, "junction"))
            for p in sh.ncs:
                terminals.append((p, "no_connect"))
            for c in sh.children:
                for pin_name, p in c.pins:
                    terminals.append((p, f"シートピン {c.name}:{pin_name}"))
            for s in sh.syms:
                for num, pin_name, p in s.pins:
                    terminals.append((p, f"ピン {s.ref}.{num}"))
            tpoints = {p for p, _ in terminals}
            for p, _what in terminals:
                for a, b in on_wires(p):
                    self.uf.union(node(p), node(a))

            # 同名ラベルはシート内で同じネット。階層ラベルもそのシートではローカルに働く
            byname: dict[str, list] = defaultdict(list)
            for name, p in sh.labels + sh.hlabels + sh.glabels:
                byname[name].append(p)
            for name, pts in byname.items():
                for q in pts[1:]:
                    self.uf.union(node(pts[0]), node(q))

            # ワイヤの端点が別のワイヤの途中に載っているのに junction も端子も無い箇所。
            # KiCad はここを繋がない。**繋がっているつもりの断線**はここに出る
            for a, b in sh.wires:
                for e in (a, b):
                    if e in sh.junctions or e in tpoints:
                        continue
                    for c, dd in sh.wires:
                        if (c, dd) == (a, b) or e in (c, dd):
                            continue
                        if _on_seg(e, c, dd):
                            self.suspect.append(
                                f"{sh.name}: ワイヤの端点 {e} が別のワイヤの途中に載っているが"
                                " junction も端子も無い（KiCad は繋がない）")

            # どこにも載っていないピン
            for s in sh.syms:
                for num, pin_name, p in s.pins:
                    if p in sh.ncs:
                        self.nc_pins.add(f"{self.ref_of(inst, s)}.{num}")
                    if on_wires(p):
                        continue
                    if any(q == p and w != f"ピン {s.ref}.{num}" for q, w in terminals):
                        continue                  # 他のピン・ラベル・NC が同じ点にある
                    self.dangling.append((inst.label, self.ref_of(inst, s), num, pin_name))

        # -- 階層をまたぐ結線: 子の階層ラベル ↔ 親のシートピン（同名）
        for inst in self.insts:
            if inst.parent is None:
                continue
            child_hl = defaultdict(list)
            for nm, p in inst.sheet.hlabels:
                child_hl[nm].append(p)
            for pin_name, ppt in inst.parent_pins:
                for cpt in child_hl.get(pin_name, []):
                    self.uf.union((inst.parent.key, ppt), (inst.key, cpt))

        # -- グローバル: global_label と power シンボル
        for inst in self.insts:
            for nm, p in inst.sheet.glabels:
                self.uf.union((inst.key, p), ("GLOBAL", nm))
            for s in inst.sheet.syms:
                if s.lib_id.startswith("power:") and not s.ref.startswith("#FLG") and s.pins:
                    self.uf.union((inst.key, s.pins[0][2]), ("GLOBAL", s.value))

    # -- ネット名 --------------------------------------------------------
    def ref_of(self, inst: Inst, s: Sym) -> str:
        return s.inst.get(inst.key, s.ref)

    def _name(self) -> None:
        acc: dict[object, Net] = {}
        depth: dict[object, int] = {}
        gname: dict[object, str] = {}

        def net(k) -> Net:
            r = self.uf.find(k)
            if r not in acc:
                acc[r] = Net(name="")
            return acc[r]

        for inst in self.insts:
            d = inst.key.count("/")
            for nm, p in inst.sheet.glabels:
                gname[self.uf.find((inst.key, p))] = nm
            for s in inst.sheet.syms:
                if s.lib_id.startswith("power:") and not s.ref.startswith("#FLG") and s.pins:
                    gname[self.uf.find((inst.key, s.pins[0][2]))] = s.value
            for nm, p in inst.sheet.labels + inst.sheet.hlabels:
                n = net((inst.key, p))
                n.names.add(nm)
                n.sheets.add(inst.sheet.name)
                r = self.uf.find((inst.key, p))
                if r not in depth or d < depth[r]:
                    depth[r] = d
                    n.name = nm

        for inst in self.insts:
            for s in inst.sheet.syms:
                if s.lib_id.startswith("power:"):
                    continue
                ref = self.ref_of(inst, s)
                for num, pin_name, p in s.pins:
                    n = net((inst.key, p))
                    n.sheets.add(inst.sheet.name)
                    n.pins.append(f"{ref}.{num}")
                    n.detail.append((ref, num, s.lib_id, s.value))

        for r, nm in gname.items():
            if r in acc:
                acc[r].name = nm
                acc[r].names.add(nm)

        anon = 0
        self.nets: list[Net] = []
        for r, n in acc.items():
            if not n.pins and not n.names:
                continue
            if not n.name:
                anon += 1
                n.name = f"({sorted(n.pins)[0]})" if n.pins else f"(unnamed-{anon})"
            self.nets.append(n)
        self.nets.sort(key=lambda n: (-len(n.pins), n.name))

        # 部品 → その部品のピンが載っているネット名の集合。
        # 「片側だけ数える」やり方だと、GND 側にピン1が来ているパスコンがレールから漏れる。
        # 参照はインスタンス展開後にユニーク（bom の「参照の重複 0」が前提）。
        self.part: dict[str, tuple[str, str]] = {}
        self.part_nets: dict[str, set] = defaultdict(set)
        for n in self.nets:
            for ref, num, lib, val in n.detail:
                self.part[ref] = (lib, val)
                self.part_nets[ref].add(n.name)

        for inst, s in self._tie_syms:
            ref = self.ref_of(inst, s)
            self.ties.append((inst.label, ref, sorted(self.part_nets.get(ref, set()))))

    # -- 部品表 ----------------------------------------------------------
    def components(self) -> list[tuple[str, str, str, str, bool]]:
        """(ref, lib_id, value, インスタンスのラベル, dnp)。マルチユニットは1件に畳む。"""
        seen: dict[tuple[str, str], tuple] = {}
        for inst in self.insts:
            for s in inst.sheet.syms:
                if s.ref.startswith("#"):
                    continue
                ref = self.ref_of(inst, s)
                seen.setdefault((inst.key, ref), (ref, s.lib_id, s.value, inst.label, s.dnp))
        return sorted(seen.values(), key=lambda c: (c[3], c[0]))


# --------------------------------------------------------------------------
# 値のパース
# --------------------------------------------------------------------------

MULT = {"p": 1e-12, "n": 1e-9, "u": 1e-6, "µ": 1e-6, "μ": 1e-6, "m": 1e-3, "": 1.0}
VAL_RE = re.compile(r"^\s*([0-9]*\.?[0-9]+)\s*([pnuµμm]?)", re.I)


def farads(value: str) -> float | None:
    """'100nF' '0.1u' '2.2uF film' '100uF 35V' → F。読めなければ None。"""
    m = VAL_RE.match(value)
    if not m:
        return None
    unit = m.group(2)
    if unit == "M":                      # 'M' は F では使わない。取り違え防止
        return None
    return float(m.group(1)) * MULT[unit.lower() if unit else ""]


def is_cap(lib_id: str) -> bool:
    return lib_id.startswith("Device:C") and "Coax" not in lib_id


# --------------------------------------------------------------------------
# レポート
# --------------------------------------------------------------------------

def r_tree(d: Design, out: dict) -> None:
    cnt = Counter(i.sheet.name for i in d.insts)
    print("階層（インスタンス数）")
    for i in d.insts:
        indent = "  " * i.key.count("/")
        print(f"{indent}{i.sheet.name}")
    print()
    print("シートファイルごとの枚数（×n が効くのはここ）")
    for name, c in sorted(cnt.items()):
        mark = "  ← 複数枚。1枚ぶんの値を全体の値と取り違えないこと" if c > 1 else ""
        print(f"  {name:18} ×{c}{mark}")
    out["tree"] = {"instances": [i.label for i in d.insts], "per_file": dict(cnt)}


def r_bom(d: Design, out: dict, by: str) -> None:
    comps = d.components()
    print(f"部品（インスタンス展開後・マルチユニットは1件）: {len(comps)} 個")
    dnp = [c for c in comps if c[4]]
    if dnp:
        print(f"  うち DNP: {len(dnp)} — {', '.join(c[0] for c in dnp)}")
    dup = [r for r, c in Counter(c[0] for c in comps).items() if c > 1]
    print(f"  参照の重複: {len(dup)}" + (f" — {', '.join(sorted(dup))}" if dup else ""))
    print()
    if by == "sheet":
        per = Counter(c[3].split("/")[-1] for c in comps)
        for k, v in sorted(per.items()):
            print(f"  {k:18} {v:4}")
    elif by == "value":
        per = Counter((c[1], c[2]) for c in comps)
        for (lib, val), v in sorted(per.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"  {v:4}  {lib:38} {val}")
    else:
        per = Counter(c[1] for c in comps)
        for k, v in sorted(per.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"  {v:4}  {k}")
    out["bom"] = {"total": len(comps), "dnp": [c[0] for c in dnp],
                  "duplicate_refs": sorted(dup),
                  "components": [{"ref": c[0], "lib_id": c[1], "value": c[2],
                                  "instance": c[3], "dnp": c[4]} for c in comps]}


def r_rails(d: Design, out: dict) -> None:
    """ネットに片足でも載っているコンデンサを積む。

    「ピン1側だけ数える」やり方は、GND 側にピン1が向いているパスコンをレールから
    取りこぼす。DC-DC の `Cout` 上限と比べたいのは**そのレールにぶら下がる容量**なので、
    片足が載っていれば数える（両足とも同じネットの部品は数えない）。
    """
    rows = []
    for n in d.nets:
        caps, total, bad = [], 0.0, []
        for ref in sorted({r for r, _, lib, _ in n.detail if is_cap(lib)}):
            if len(d.part_nets[ref]) < 2:
                continue                      # 両足とも同じネット
            val = d.part[ref][1]
            f = farads(val)
            if f is None:
                bad.append(f"{ref}={val!r}")
            else:
                caps.append((ref, val, f))
                total += f
        if caps or bad:
            rows.append((total, n, caps, bad))
    rows.sort(key=lambda r: -r[0])
    print("ネットに片足でも載っているコンデンサの合計（両足が同じネットの部品は数えない）")
    print("⚠ 公称値の和。電解の上振れは含めない。DC-DC の Cout 上限と比べるときは公差を別途積むこと")
    print("⚠ カップリング用も混ざる。レール容量として使うなら中身を見ること\n")
    j = []
    for total, n, caps, bad in rows[:20]:
        agg = Counter(v for _, v, _ in caps)
        parts = ", ".join(f"{v}×{c}" for v, c in sorted(agg.items(), key=lambda kv: -kv[1]))
        print(f"  {n.name:16} {total*1e6:9.2f} µF   ({len(caps)} 個)  {parts}")
        if bad:
            print(f"  {'':16} ⚠ 値を読めなかった: {', '.join(bad)}")
        j.append({"net": n.name, "farads": total, "count": len(caps),
                  "caps": [{"ref": r, "value": v} for r, v, _ in caps], "unreadable": bad})
    out["rails"] = j


def r_nets(d: Design, out: dict, want: str | None, min_pins: int) -> None:
    sel = [n for n in d.nets if (want is None or n.name == want) and len(n.pins) >= min_pins]
    print(f"ネット {len(sel)} 本（全 {len(d.nets)} 本）")
    for n in sel[:200 if want is None else 10000]:
        extra = f"  別名:{sorted(n.names - {n.name})}" if len(n.names) > 1 else ""
        print(f"  {n.name:22} {len(n.pins):4} ピン  {sorted(n.sheets)}{extra}")
        if want is not None:
            for p in sorted(n.pins):
                print(f"        {p}")
    single = [n for n in d.nets if len(n.pins) == 1]
    marked = [n for n in single if n.pins[0] in d.nc_pins]
    free = [n for n in single if n.pins[0] not in d.nc_pins]
    if want is None:
        print(f"\n1ピンしかないネット: {len(single)} 本"
              f"（no_connect あり {len(marked)} / **無し {len(free)}**）")
        print("  no_connect の無いものは「未接続のまま置かれている」。設計意図か確かめること")
        for n in free[:60]:
            print(f"  {n.name:24} {sorted(n.sheets)}")
    if want is None and d.ties:
        print(f"\nnet tie（回路図では別ネットのまま。基板の銅箔で1点だけ繋ぐ）: {len(d.ties)} 個")
        for label, ref, nets in d.ties:
            print(f"  {ref:8} {' ↔ '.join(nets) if nets else '(片側が無名)'}   {label}")
    out["nets"] = [{"name": n.name, "pins": sorted(n.pins), "sheets": sorted(n.sheets),
                    "aliases": sorted(n.names)} for n in sel]
    out["single_pin_nets_without_nc"] = [n.pins[0] for n in free]
    out["net_ties"] = [{"ref": r, "nets": ns, "instance": l} for l, r, ns in d.ties]


def r_iface(d: Design, out: dict) -> None:
    """親の (sheet) が持つピン名 と 子ファイルの階層ラベル名 の食い違い。"""
    bad = []
    for inst in d.insts:
        for c in inst.sheet.children:
            child = d.files.get(Path(c.file).name)
            if child is None:
                continue
            ppins = {n for n, _ in c.pins}
            hl = {n for n, _ in child.hlabels}
            for miss in sorted(ppins - hl):
                bad.append((inst.sheet.name, c.name, miss, "親にピンがあるが子に階層ラベルが無い"))
            for miss in sorted(hl - ppins):
                bad.append((inst.sheet.name, c.name, miss, "子に階層ラベルがあるが親にピンが無い"))
    print(f"親子のシート界面の不一致: {len(bad)} 件"
          + ("（0 = 親子でピンの対応が取れている）" if not bad else ""))
    for parent, child, nm, why in bad:
        print(f"  {parent} → {child}: {nm}  — {why}")
    if bad:
        print("\n  ⚠ CLAUDE.md: MeasureControl にピンを足したら build_motherboard.py の"
              " CHILD_SHEETS にも足すこと")
    out["iface"] = [{"parent": p, "child": c, "pin": n, "why": w} for p, c, n, w in bad]


def r_dangling(d: Design, out: dict) -> None:
    print(f"どこにも載っていないピン: {len(d.dangling)} 本")
    per = defaultdict(list)
    for label, ref, num, name in d.dangling:
        per[(label, ref)].append(f"{num}:{name}")
    for (label, ref), pins in sorted(per.items()):
        print(f"  {label} {ref}  {', '.join(pins)}")
    print(f"\n黙って結ばなかった接触（junction 無しでワイヤの途中）: {len(d.suspect)} 件")
    for s in sorted(set(d.suspect))[:40]:
        print(f"  {s}")
    out["dangling"] = [{"instance": l, "ref": r, "pin": n, "pin_name": nm}
                       for l, r, n, nm in d.dangling]
    out["suspect_contacts"] = sorted(set(d.suspect))


def r_aliases(d: Design, out: dict) -> None:
    rows = [n for n in d.nets if len(n.names) > 1]
    print(f"1本のネットに複数の名前が載っている: {len(rows)} 本")
    print("（階層をまたぐ意図的な別名もここに出る。**意図しない短絡はここに紛れる**ので目視すること）\n")
    for n in rows:
        print(f"  {n.name:20} = {sorted(n.names)}   {len(n.pins)} ピン  {sorted(n.sheets)}")
    out["aliases"] = [{"net": n.name, "names": sorted(n.names), "pins": len(n.pins)}
                      for n in rows]


def r_pin(d: Design, out: dict, ref: str) -> None:
    found = []
    for n in d.nets:
        for r, num, lib, val in n.detail:
            if r == ref:
                found.append((num, n.name, lib, val))
    if not found:
        print(f"{ref} が見つからない。参照は再アノテーションで動く（SOURCE_OF_TRUTH.md §3）ので"
              " 'bom' で現物の参照を確かめること")
    for num, net, lib, val in sorted(found, key=lambda t: (len(t[0]), t[0])):
        print(f"  {ref}.{num:4} → {net:22} [{lib} {val}]")
    out["pin"] = [{"pin": p, "net": n} for p, n, _, _ in found]


# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["all", "tree", "bom", "rails", "nets", "iface",
                                    "dangling", "aliases", "pin"])
    ap.add_argument("arg", nargs="?", help="pin のとき参照（例 C_BULK_P301）")
    ap.add_argument("--root", default="AudioV2/AudioV2Case.kicad_sch")
    ap.add_argument("--by", default="lib", choices=["lib", "value", "sheet"])
    ap.add_argument("--net", default=None)
    ap.add_argument("--min-pins", type=int, default=0)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    root = Path(a.root)
    if not root.exists():
        print(f"error: {root} が無い（リポジトリのルートから実行する）", file=sys.stderr)
        return 2
    d = Design(root)
    out: dict = {}

    if a.json:
        buf, sys.stdout = sys.stdout, open("/dev/null", "w")
    try:
        if a.cmd in ("all", "tree"):
            r_tree(d, out); print()
        if a.cmd in ("all", "bom"):
            r_bom(d, out, a.by); print()
        if a.cmd in ("all", "rails"):
            r_rails(d, out); print()
        if a.cmd in ("all", "iface"):
            r_iface(d, out); print()
        if a.cmd in ("all", "dangling"):
            r_dangling(d, out); print()
        if a.cmd in ("all", "aliases"):
            r_aliases(d, out); print()
        if a.cmd == "nets":
            r_nets(d, out, a.net, a.min_pins)
        if a.cmd == "all":
            r_nets(d, out, None, 12)
        if a.cmd == "pin":
            if not a.arg:
                print("pin は参照が要る: sch_facts.py pin C203", file=sys.stderr)
                return 2
            r_pin(d, out, a.arg)
    finally:
        if a.json:
            sys.stdout.close()
            sys.stdout = buf
    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:            # `| head` で切られたとき
        sys.stderr.close()
        raise SystemExit(0)
