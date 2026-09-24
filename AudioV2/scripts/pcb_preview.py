#!/usr/bin/env python3
"""PCB の一部を PNG に描く（読み取り専用）。GUI の無いクラウドで配線を目で見るための道具。

層ごとの配線・パッド・ビアを SVG に描き、headless Chromium で PNG にする。
`AMP_SEL_*` と `SEL_CH*` は強調する（配線方針: AMP_SEL は B.Cu、SEL とは並走させない）。

    python3 AudioV2/scripts/pcb_preview.py 543 153 571 178 -o out/u311.png --scale 40
    python3 AudioV2/scripts/pcb_preview.py --region AmpBankSwitch -o out/sw.png

Chromium は `PCB_PREVIEW_CHROME` → Playwright 同梱（`/opt/pw-browsers`）→ PATH の順に探す。
見つからなければ SVG だけ書く。
"""
from __future__ import annotations

import argparse
import glob
import html
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pcbnew

PCB = Path(__file__).resolve().parents[1] / "AudioV2Case.kicad_pcb"
F, B = pcbnew.F_Cu, pcbnew.B_Cu
mm = pcbnew.ToMM


def board_outlines(board):
    """Edge.Cuts の矩形（複数基板を1ファイルに同居させているので、娘ごとに1枚ある）。"""
    out = []
    for d in board.GetDrawings():
        if d.GetLayer() == pcbnew.Edge_Cuts and d.GetShape() == pcbnew.SHAPE_T_RECT:
            bb = d.GetBoundingBox()
            out.append((mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())))
    return out


def sheet_region(board, sheet: str):
    """シート名（例 AmpBankSwitch）の部品を最も多く含む Edge 矩形。"""
    best, best_n = None, 0
    fps = [f for f in board.GetFootprints() if f.GetSheetname().startswith(f"/{sheet}/")]
    for r in board_outlines(board):
        n = sum(1 for f in fps if r[0] <= mm(f.GetPosition().x) <= r[2] and r[1] <= mm(f.GetPosition().y) <= r[3])
        if n > best_n:
            best, best_n = r, n
    if best is None:
        raise SystemExit(f"{sheet} の部品を含む Edge.Cuts 矩形が無い")
    return best


def style(net: str, layer: int):
    """(色, 強調幅 or None, 破線)。"""
    if "AMP_SEL_L" in net:
        return ("#d00000" if layer == F else "#0040ff"), 0.45, ""
    if "AMP_SEL_R" in net:
        return ("#ff8000" if layer == F else "#00a0a0"), 0.45, ""
    if "SEL_CH" in net:
        return ("#ff40c0" if layer == F else "#8000c0"), 0.3, "0.6,0.3"
    if net in ("/+15V", "/-15V"):
        return ("#e0a060" if layer == F else "#80a0c0"), None, ""
    return ("#f2bcbc" if layer == F else "#b4ccec"), None, ""


def render_svg(board, x0, y0, x1, y1, pxmm) -> tuple[str, int, int]:
    W, H = round((x1 - x0) * pxmm), round((y1 - y0) * pxmm)
    fs = max(0.6, 11 / pxmm)

    def inr(x, y, m=2.0):
        return x0 - m <= x <= x1 + m and y0 - m <= y <= y1 + m

    s = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="{x0} {y0} {x1 - x0} {y1 - y0}">',
        f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="white"/>',
    ]
    step = 5 if pxmm < 30 else 1
    for gx in range(math.ceil(x0 / step) * step, int(x1) + 1, step):
        s.append(f'<line x1="{gx}" y1="{y0}" x2="{gx}" y2="{y1}" stroke="#eee" stroke-width="{0.6 / pxmm}"/>')
        if gx % 5 == 0:
            s.append(f'<text x="{gx + 0.2}" y="{y0 + fs}" font-size="{fs * 0.8}" fill="#999">{gx}</text>')
    for gy in range(math.ceil(y0 / step) * step, int(y1) + 1, step):
        s.append(f'<line x1="{x0}" y1="{gy}" x2="{x1}" y2="{gy}" stroke="#eee" stroke-width="{0.6 / pxmm}"/>')
        if gy % 5 == 0:
            s.append(f'<text x="{x0 + 0.2}" y="{gy - 0.2}" font-size="{fs * 0.8}" fill="#999">{gy}</text>')
    for r in board_outlines(board):
        s.append(f'<rect x="{r[0]}" y="{r[1]}" width="{r[2] - r[0]}" height="{r[3] - r[1]}" fill="none" stroke="#bb0" stroke-width="0.15"/>')

    tracks = [t for t in board.GetTracks() if t.Type() != pcbnew.PCB_VIA_T]

    def seg(t, highlighted):
        net = t.GetNetname()
        col, hw, dash = style(net, t.GetLayer())
        if (hw is not None) != highlighted:
            return
        a, b = t.GetStart(), t.GetEnd()
        if not (inr(mm(a.x), mm(a.y)) or inr(mm(b.x), mm(b.y))):
            return
        w = max(mm(t.GetWidth()), hw or 0)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        s.append(
            f'<line x1="{mm(a.x):.3f}" y1="{mm(a.y):.3f}" x2="{mm(b.x):.3f}" y2="{mm(b.y):.3f}" '
            f'stroke="{col}" stroke-width="{w:.3f}" stroke-linecap="round"{da}/>'
        )

    for lay in (B, F):
        for t in tracks:
            if t.GetLayer() == lay:
                seg(t, False)
    for fp in board.GetFootprints():
        for p in fp.Pads():
            px, py = mm(p.GetPosition().x), mm(p.GetPosition().y)
            if not inr(px, py):
                continue
            bb = p.GetBoundingBox()
            smd = p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD
            fill = "#b8b8b8" if (smd and p.IsOnLayer(F)) else ("#9ab0c8" if smd else "#909090")
            stroke = ' stroke="black" stroke-width="0.12"' if "AMP_SEL" in p.GetNetname() else ""
            if not smd and p.GetShape() in (pcbnew.PAD_SHAPE_CIRCLE, pcbnew.PAD_SHAPE_OVAL):
                s.append(f'<ellipse cx="{px:.3f}" cy="{py:.3f}" rx="{mm(bb.GetWidth()) / 2:.3f}" ry="{mm(bb.GetHeight()) / 2:.3f}" fill="{fill}" opacity="0.8"{stroke}/>')
            else:
                s.append(f'<rect x="{mm(bb.GetLeft()):.3f}" y="{mm(bb.GetTop()):.3f}" width="{mm(bb.GetWidth()):.3f}" height="{mm(bb.GetHeight()):.3f}" fill="{fill}" opacity="0.8"{stroke}/>')
            if not smd:
                s.append(f'<circle cx="{px:.3f}" cy="{py:.3f}" r="{mm(p.GetDrillSizeX()) / 2:.3f}" fill="white"/>')
    for lay in (B, F):
        for t in tracks:
            if t.GetLayer() == lay:
                seg(t, True)
    for v in board.GetTracks():
        if v.Type() != pcbnew.PCB_VIA_T:
            continue
        vx, vy = mm(v.GetX()), mm(v.GetY())
        if not inr(vx, vy):
            continue
        net = v.GetNetname()
        col = "black" if "AMP_SEL" in net else ("#8000c0" if "SEL_CH" in net else "#607060")
        s.append(f'<circle cx="{vx:.3f}" cy="{vy:.3f}" r="{mm(v.GetWidth(F)) / 2:.3f}" fill="{col}"/>')
        s.append(f'<circle cx="{vx:.3f}" cy="{vy:.3f}" r="{mm(v.GetDrill()) / 2:.3f}" fill="white"/>')
    for fp in board.GetFootprints():
        px, py = mm(fp.GetPosition().x), mm(fp.GetPosition().y)
        if not inr(px, py, 0):
            continue
        ref = fp.GetReference()
        big = ref[0] in "UJ" or ref.startswith("AMP")
        if not big and pxmm < 20:
            continue
        s.append(f'<text x="{px:.2f}" y="{py:.2f}" font-size="{fs * (1.3 if big else 0.8):.2f}" fill="#004000" font-family="sans-serif" text-anchor="middle" opacity="0.85">{html.escape(ref)}</text>')
        for p in fp.Pads():
            if "AMP_SEL" in p.GetNetname():
                qx, qy = mm(p.GetPosition().x), mm(p.GetPosition().y)
                s.append(f'<text x="{qx + 0.4:.2f}" y="{qy - 0.4:.2f}" font-size="{fs:.2f}" font-family="sans-serif">{ref}.{p.GetNumber()} {html.escape(p.GetNetname().lstrip("/").replace("AMP_SEL_", ""))}</text>')
    lg = [("#d00000", "AMP_SEL_L F"), ("#0040ff", "AMP_SEL_L B"), ("#ff8000", "AMP_SEL_R F"),
          ("#00a0a0", "AMP_SEL_R B"), ("#ff40c0", "SEL_CH F"), ("#8000c0", "SEL_CH B")]
    lx, ly = x1 - fs * 9, y1 - fs * (len(lg) * 1.3 + 2.2)
    s.append(f'<rect x="{lx - fs * 0.5}" y="{ly - fs * 1.2}" width="{fs * 9.5}" height="{fs * (len(lg) * 1.3 + 3)}" fill="white" opacity="0.9"/>')
    for i, (c, t) in enumerate(lg):
        s.append(f'<text x="{lx}" y="{ly + i * fs * 1.3}" font-size="{fs}" font-family="sans-serif" fill="{c}">{t}</text>')
    s.append(f'<text x="{lx}" y="{ly + len(lg) * fs * 1.3}" font-size="{fs * 0.8}" font-family="sans-serif" fill="#888">淡赤=F 淡青=B 黒丸=AMP_SEL ビア</text>')
    s.append("</svg>")
    return "\n".join(s), W, H


def find_chrome() -> str | None:
    env = os.environ.get("PCB_PREVIEW_CHROME")
    if env:
        return env
    for pat in ("/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell",
                "/opt/pw-browsers/chromium-*/chrome-linux/chrome"):
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[-1]
    for name in ("chromium", "chromium-browser", "google-chrome"):
        if shutil.which(name):
            return shutil.which(name)
    return None


def to_png(svg_path: Path, png_path: Path, w: int, h: int) -> bool:
    chrome = find_chrome()
    if not chrome:
        print("Chromium が無いので SVG だけ書いた", file=sys.stderr)
        return False
    subprocess.run(
        [chrome, "--no-sandbox", "--disable-gpu", "--hide-scrollbars", f"--screenshot={png_path}",
         f"--window-size={w},{h}", svg_path.resolve().as_uri()],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return png_path.exists()


def preview(board, x0, y0, x1, y1, out: Path, pxmm: float) -> Path:
    svg, w, h = render_svg(board, x0, y0, x1, y1, pxmm)
    out.parent.mkdir(parents=True, exist_ok=True)
    svg_path = out.with_suffix(".svg")
    svg_path.write_text(svg, encoding="utf-8")
    if out.suffix.lower() == ".png" and to_png(svg_path, out, w, h):
        return out
    return svg_path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("box", nargs="*", type=float, help="x0 y0 x1 y1 [mm]")
    ap.add_argument("--region", help="シート名の Edge 矩形を丸ごと描く（例 AmpBankSwitch）")
    ap.add_argument("-o", "--out", type=Path, required=True, help=".png（Chromium が無ければ .svg）")
    ap.add_argument("--scale", type=float, default=12.0, help="px/mm")
    ap.add_argument("--board", type=Path, default=PCB)
    a = ap.parse_args()
    board = pcbnew.LoadBoard(str(a.board))
    if a.region:
        x0, y0, x1, y1 = sheet_region(board, a.region)
        x0, y0, x1, y1 = x0 - 1, y0 - 1, x1 + 1, y1 + 1
    elif len(a.box) == 4:
        x0, y0, x1, y1 = a.box
    else:
        ap.error("x0 y0 x1 y1 か --region を渡す")
    print(preview(board, x0, y0, x1, y1, a.out, a.scale))
    return 0


if __name__ == "__main__":
    sys.exit(main())
