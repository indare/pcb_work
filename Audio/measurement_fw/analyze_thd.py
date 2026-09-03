#!/usr/bin/env python3
"""`capture_raw.py` の生サンプルから基本波・H2/H3/H5 を取り出す（PC 側、float64）。

## 何を出すか

各高調波について **振幅（dBc）と「基本波に対する相対位相」**。
複数キャプチャを渡すと**平均とばらつき**を出す。そのばらつきが
**「どこまでの THD 差を再現性よく比較できるか」の答え**になる。

## 非同期クロックへの対処（重要）

G8（USB DAC）の 48kHz と PCM1804 のローカル 12.288MHz は独立なので、
再生した音の周波数は**ビン中心に乗らないし、ドリフトもする**。

- **振幅**: FFT のビンを読むと窓の走査損失で誤差が出る。
  → **基本波の実周波数 f0 を放物線補間で求め、そこで DTFT を直接評価する。**
     ビン中心に依存しないので走査損失が消える。
- **位相**: 絶対位相はキャプチャごとに無意味（時間原点がずれる）。
  → **相対位相 `φn - n·φ1` を使う。** 時間シフト Δt は φ1 を 2πf0Δt、
     φn を n·2πf0Δt 動かすので、この差はシフト不変。
     周波数ドリフトも f0 を毎回測り直すので追従する。

## 使い方

    python3 analyze_thd.py cap.txt                    # 1回分
    python3 analyze_thd.py cap_*.txt                  # 複数 → 平均とばらつき
    python3 analyze_thd.py --ch R cap.txt             # R を見る（既定は L）
    python3 analyze_thd.py --self-test                # 合成波で自己検証

**L チャンネルを使うこと。** ブリングアップ実測で R は L より全倍音で一貫して 14dB 悪い。

## 既知の妨害

1174.8 Hz の倍音列（自走の非同期源、L −84.4 / R −70.0 dBFS、未解決）がある。
**試験周波数はこれと重ならないよう選ぶ。** 例えば基本波 1 kHz なら
H2=2k / H3=3k / H5=5k に対し妨害は 1175/2350/3525 Hz で衝突しない。
`--show-interferer` で妨害の位置も一緒に出す。
"""

from __future__ import annotations

import argparse
import base64
import sys

import numpy as np

FULL_SCALE = float(1 << 23)
INTERFERER_HZ = 1174.8          # 既知の妨害（BRINGUP 実測）
HARMONICS = (2, 3, 5)


def load(path: str):
    """capture_raw.py の出力を (L, R, fs_nominal) にする。"""
    n_frames = None
    fs = 48000.0
    payload = []
    with open(path, "r") as fp:
        for line in fp:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                tok = line.split()
                if len(tok) >= 3 and tok[1] == "n_frames":
                    n_frames = int(tok[2])
                elif len(tok) >= 3 and tok[1] == "fs_nominal":
                    fs = float(tok[2])
                continue
            payload.append(line)
    if n_frames is None:
        raise ValueError(f"{path}: ヘッダに n_frames が無い（キャプチャ失敗？）")
    raw = base64.b64decode("".join(payload))
    words = np.frombuffer(raw, dtype="<u4")
    got = len(words) // 2
    if got < n_frames:
        raise ValueError(f"{path}: {n_frames} フレーム宣言だが {got} しか無い")
    words = words[: n_frames * 2]
    # 下位 24bit が符号付きサンプル
    v = (words & 0xFFFFFF).astype(np.int64)
    v = np.where(v & 0x800000, v - 0x1000000, v).astype(np.float64)
    return v[0::2], v[1::2], fs


def dtft(x: np.ndarray, w: np.ndarray, freq: float, fs: float) -> complex:
    """窓を掛けた信号の、任意周波数における DTFT。ビン中心に縛られない。"""
    n = np.arange(len(x), dtype=np.float64)
    return np.sum(x * w * np.exp(-2j * np.pi * freq * n / fs))


def refine_peak(mag: np.ndarray, k: int) -> float:
    """対数振幅の放物線補間でビン間の真のピーク位置を返す。"""
    if k <= 0 or k >= len(mag) - 1:
        return float(k)
    a, b, c = (np.log(max(mag[k + d], 1e-300)) for d in (-1, 0, 1))
    denom = a - 2 * b + c
    if denom == 0:
        return float(k)
    return k + 0.5 * (a - c) / denom


def analyze(x: np.ndarray, fs: float, f_lo: float, f_hi: float):
    """基本波を見つけ、各高調波の振幅(dBc)と相対位相(deg)を返す。"""
    x = x - x.mean()
    n = len(x)
    w = np.hanning(n)
    wsum = w.sum()                       # Hann のコヒーレントゲイン = n/2
    sp = np.fft.rfft(x * w)
    freqs = np.fft.rfftfreq(n, 1.0 / fs)

    band = (freqs >= f_lo) & (freqs <= f_hi)
    if not band.any():
        raise ValueError("探索帯域にビンが無い")
    k = int(np.argmax(np.abs(sp) * band))
    f0 = refine_peak(np.abs(sp), k) * fs / n

    out = {"f0": f0, "n": n, "fs": fs}
    x1 = dtft(x, w, f0, fs)
    a1 = 2.0 * abs(x1) / wsum            # 正弦波振幅（LSB）
    out["fund_dbfs"] = 20 * np.log10(max(a1, 1e-300) / FULL_SCALE)
    phi1 = np.angle(x1)

    for h in HARMONICS:
        fh = f0 * h
        if fh >= fs / 2:
            out[f"h{h}"] = None
            continue
        xh = dtft(x, w, fh, fs)
        ah = 2.0 * abs(xh) / wsum
        # 相対位相。φh - h·φ1 が時間シフト不変（Δt は φ1 を 2πf0Δt、φh を
        # その h 倍だけ動かすので差し引きゼロ）。
        # さらに (h-1)·90° を引いて、正弦波表記 x = Σ Ah·sin(hωt + θh) の
        # θh - h·θ1 になるよう直す。DTFT は sin に対し angle = θ - π/2 を返すので
        # φh - h·φ1 = (θh - h·θ1) + (h-1)·π/2 という定数ずれが入るため。
        # 定数なので再現性の測定には影響しないが、値を解釈しやすくしておく。
        rel = np.angle(xh) - h * phi1 - (h - 1) * np.pi / 2
        rel = (np.degrees(rel) + 180.0) % 360.0 - 180.0
        out[f"h{h}"] = {
            "f": fh,
            "dbc": 20 * np.log10(max(ah, 1e-300) / max(a1, 1e-300)),
            "dbfs": 20 * np.log10(max(ah, 1e-300) / FULL_SCALE),
            "rel_deg": rel,
        }

    # THD（拾った次数の RSS）
    amps = [10 ** (out[f"h{h}"]["dbc"] / 20) for h in HARMONICS if out[f"h{h}"]]
    out["thd_dbc"] = 20 * np.log10(np.sqrt(sum(a * a for a in amps))) if amps else None

    # 雑音床の目安: 基本波と高調波の近傍を除いたビンの中央値
    mask = np.ones(len(freqs), dtype=bool)
    for h in [1] + list(HARMONICS):
        mask &= np.abs(freqs - f0 * h) > 5 * fs / n
    amp_bins = 2.0 * np.abs(sp[mask]) / wsum
    out["floor_dbfs"] = 20 * np.log10(np.median(amp_bins) / FULL_SCALE)
    return out


def circ_stats(deg: list[float]):
    """位相の平均と広がり（±180 をまたいでも壊れない）。"""
    r = np.exp(1j * np.radians(deg))
    m = np.degrees(np.angle(r.mean()))
    spread = np.degrees(np.sqrt(max(-2 * np.log(min(abs(r.mean()), 1.0)), 0.0)))
    return m, spread


def self_test() -> None:
    """既知の合成波で振幅・相対位相の抽出が正しいか確かめる。"""
    fs, n = 48000.0, 16384
    t = np.arange(n) / fs
    f0 = 1000.37                      # わざとビン中心から外す（非同期を模す）
    truth = {2: (-95.0, 30.0), 3: (-110.0, -75.0), 5: (-120.0, 150.0)}
    x = np.sin(2 * np.pi * f0 * t)
    for h, (dbc, deg) in truth.items():
        x += 10 ** (dbc / 20) * np.sin(2 * np.pi * f0 * h * t + np.radians(deg))
    x *= 0.5 * FULL_SCALE
    r = analyze(x, fs, 500, 2000)
    print("自己検証（合成波、基本波をビン中心から 0.37Hz ずらしてある）")
    print(f"  f0        期待 {f0:.2f} Hz   →  {r['f0']:.2f} Hz")
    ok = abs(r["f0"] - f0) < 0.05
    for h, (dbc, deg) in truth.items():
        got = r[f"h{h}"]
        # 補正後の相対位相は θh - h·θ1。合成波は θ1=0 なので真値は deg そのもの
        d_amp = got["dbc"] - dbc
        d_ph = (got["rel_deg"] - deg + 180) % 360 - 180
        print(f"  H{h}  振幅 期待 {dbc:7.1f} dBc → {got['dbc']:7.1f}  (誤差 {d_amp:+.2f} dB)"
              f"   相対位相 期待 {deg:7.1f}° → {got['rel_deg']:7.1f}°  (誤差 {d_ph:+.2f}°)")
        ok &= abs(d_amp) < 0.1 and abs(d_ph) < 1.0
    print(f"  雑音床（合成波なので数値誤差のみ）: {r['floor_dbfs']:.1f} dBFS")
    print("  → " + ("OK" if ok else "**NG: 抽出が合っていない**"))
    sys.exit(0 if ok else 1)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", help="capture_raw.py の出力")
    ap.add_argument("--ch", choices=["L", "R"], default="L",
                    help="既定 L（R は実測で全倍音 14dB 悪い）")
    ap.add_argument("--f-lo", type=float, default=500.0, help="基本波の探索下限")
    ap.add_argument("--f-hi", type=float, default=2000.0, help="基本波の探索上限")
    ap.add_argument("--show-interferer", action="store_true",
                    help="既知の 1174.8Hz 妨害の位置も出す")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    if a.self_test:
        self_test()
    if not a.files:
        ap.error("ファイルを指定するか --self-test")

    runs = []
    for path in a.files:
        left, right, fs = load(path)
        x = left if a.ch == "L" else right
        r = analyze(x, fs, a.f_lo, a.f_hi)
        r["path"] = path
        runs.append(r)

    print(f"ch={a.ch}  N={runs[0]['n']}  fs={runs[0]['fs']:.0f}Hz  "
          f"Δf={runs[0]['fs']/runs[0]['n']:.2f}Hz  {len(runs)} 回\n")
    print(f"{'file':22s}{'f0':>10s}{'基本波':>11s}{'床':>10s}"
          + "".join(f"{f'H{h} dBc':>10s}{f'H{h} 位相':>10s}" for h in HARMONICS))
    for r in runs:
        cells = ""
        for h in HARMONICS:
            g = r[f"h{h}"]
            cells += f"{g['dbc']:10.1f}{g['rel_deg']:10.1f}" if g else f"{'—':>10s}{'—':>10s}"
        print(f"{r['path'][-22:]:22s}{r['f0']:9.2f}H{r['fund_dbfs']:10.2f}"
              f"{r['floor_dbfs']:10.1f}{cells}")

    if len(runs) > 1:
        print("\n=== 再現性（これが分解能の床）===")
        print(f"{'量':12s}{'平均':>12s}{'ばらつき(1σ)':>14s}{'最大-最小':>12s}")
        for h in HARMONICS:
            vals = [r[f"h{h}"]["dbc"] for r in runs if r[f"h{h}"]]
            if not vals:
                continue
            v = np.array(vals)
            print(f"H{h} 振幅     {v.mean():11.2f}dB{v.std(ddof=1):12.3f}dB"
                  f"{np.ptp(v):11.3f}dB")
            phs = [r[f"h{h}"]["rel_deg"] for r in runs if r[f"h{h}"]]
            m, sp = circ_stats(phs)
            print(f"H{h} 相対位相 {m:11.1f}° {sp:12.3f}° "
                  f"{max(phs)-min(phs):11.3f}°")
        f0s = np.array([r["f0"] for r in runs])
        print(f"\n  f0 のドリフト: {f0s.min():.3f} 〜 {f0s.max():.3f} Hz "
              f"({np.ptp(f0s)*1e6/f0s.mean():.0f} ppm)")
        print("  → 振幅のばらつき(1σ)より小さい石の差は見分けられない。")

    if a.show_interferer:
        print(f"\n既知の妨害 {INTERFERER_HZ}Hz とその倍音の位置:")
        r = runs[0]
        for k in (1, 2, 3):
            f = INTERFERER_HZ * k
            near = [h for h in HARMONICS if abs(r[f"h{h}"]["f"] - f) < 20] if r["h2"] else []
            warn = f"  ⚠ H{near[0]} と {abs(r[f'h{near[0]}']['f']-f):.1f}Hz しか離れていない" if near else ""
            print(f"  {f:8.1f} Hz{warn}")


if __name__ == "__main__":
    main()
