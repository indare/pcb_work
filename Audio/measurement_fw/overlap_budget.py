#!/usr/bin/env python3
"""オーバーラップ FFT の予算モック（CPython ホスト可・実機不要）。

目的:
  - (N, hop) が Pico2 解析予算に収まるかの机上切り分け
  - 連続リングから hop だけ進める読み出しの論理テスト
  - 他チャットが実機前に同じ前提で議論・拡張できるようにする

実 SPI / PIO / MicroPython には依存しない。
計測値のデフォルトは c_fft/README.md の実機 C FFT（n=1024 ≈ 1.91 ms/ch）。

    python3 overlap_budget.py
    python3 overlap_budget.py --n 2048 --hop 512 --fft-ms 4.2
"""

from __future__ import annotations

import argparse
import math
import sys
import unittest


FS_DEFAULT = 48_000.0
# 実機 C fft_q15 @ n=1024（1 ch）。N が違うときは --fft-ms で上書きするか
# scale_fft_ms() の N log N スケールを使う。
FFT_MS_1024 = 1.91
# unpack + バンド dB + IIR など Python 糊の仮置き（要実測で差し替え）。
GLUE_MS_DEFAULT = 2.0


def hop_period_ms(hop: int, fs: float = FS_DEFAULT) -> float:
    return 1000.0 * hop / fs


def delta_f(n: int, fs: float = FS_DEFAULT) -> float:
    return fs / n


def scale_fft_ms(n: int, base_ms: float = FFT_MS_1024, base_n: int = 1024) -> float:
    """粗い N log N スケール。実測があれば --fft-ms を優先。"""
    if n == base_n:
        return base_ms
    return base_ms * (n * math.log2(n)) / (base_n * math.log2(base_n))


def analyze_ms(fft_ms_per_ch: float, glue_ms: float, channels: int = 2) -> float:
    return channels * fft_ms_per_ch + glue_ms


def budget_ok(
    n: int,
    hop: int,
    fft_ms: float | None = None,
    glue_ms: float = GLUE_MS_DEFAULT,
    fs: float = FS_DEFAULT,
    channels: int = 2,
    margin: float = 0.85,
) -> dict:
    """1 ホップ予算に対する解析時間。margin は割り込み・GC 用の使用率上限。"""
    if hop <= 0 or n <= 0 or hop > n:
        raise ValueError("require 0 < hop <= n")
    fft = FFT_MS_1024 if fft_ms is None else fft_ms
    if fft_ms is None:
        fft = scale_fft_ms(n)
    period = hop_period_ms(hop, fs)
    cost = analyze_ms(fft, glue_ms, channels)
    return {
        "n": n,
        "hop": hop,
        "fs": fs,
        "delta_f_hz": delta_f(n, fs),
        "overlap": 1.0 - hop / n,
        "period_ms": period,
        "fft_ms_ch": fft,
        "glue_ms": glue_ms,
        "analyze_ms": cost,
        "fps_cap": 1000.0 / period if period else 0.0,
        "util": cost / period if period else float("inf"),
        "ok": cost <= period * margin,
        "margin": margin,
    }


def format_row(r: dict) -> str:
    flag = "OK " if r["ok"] else "NG "
    return (
        "%s n=%4d hop=%4d  Δf=%5.1fHz  T=%5.2fms  "
        "cost=%5.2fms  util=%5.0f%%  fps≤%.0f  ol=%.0f%%"
        % (
            flag,
            r["n"],
            r["hop"],
            r["delta_f_hz"],
            r["period_ms"],
            r["analyze_ms"],
            100.0 * r["util"],
            r["fps_cap"],
            100.0 * r["overlap"],
        )
    )


class MockI2sRing:
    """連続 DMA 相当のリング。書き込みは ADC クロック相当、読みは hop 単位。

    本番の PIO 張り直しモデル（start_into/wait）の対極として、
    「止めずに hop だけ進める」論理をホストで固定する。
    """

    def __init__(self, capacity_frames: int, channels: int = 2):
        if capacity_frames < 1:
            raise ValueError("capacity")
        self.channels = channels
        self.capacity = capacity_frames
        # L/R 交互ワードを模した単調カウンタ（内容はテスト用）
        self._buf = [0] * (capacity_frames * channels)
        self._write = 0  # フレーム単位
        self._read = 0
        self._total_written = 0

    def push_frames(self, n_frames: int) -> None:
        """ADC が n_frames 進んだことにする。"""
        for _ in range(n_frames):
            base = (self._write % self.capacity) * self.channels
            seq = self._total_written
            for ch in range(self.channels):
                self._buf[base + ch] = seq * self.channels + ch
            self._write += 1
            self._total_written += 1
            # 書きが読みを一周追い越したら読みを落とす（本番はオーバーラン検知）
            if self._write - self._read > self.capacity:
                self._read = self._write - self.capacity

    def available(self) -> int:
        return self._write - self._read

    def take_window(self, n: int, hop: int) -> list[int]:
        """長さ n フレームの窓を返し、読み位置を hop だけ進める。"""
        if hop <= 0 or hop > n:
            raise ValueError("hop")
        if self.available() < n:
            raise RuntimeError("underrun: need %d have %d" % (n, self.available()))
        out = []
        for i in range(n):
            frame = self._read + i
            base = (frame % self.capacity) * self.channels
            out.extend(self._buf[base : base + self.channels])
        self._read += hop
        return out


class MockAnalyzer:
    """固定コストの擬似解析。実 FFT はしない。予算チェック用。"""

    def __init__(self, n: int, hop: int, fft_ms: float | None = None,
                 glue_ms: float = GLUE_MS_DEFAULT):
        self.n = n
        self.hop = hop
        self.row = budget_ok(n, hop, fft_ms=fft_ms, glue_ms=glue_ms)
        self.frames = 0
        self.dropped = 0

    def process_available(self, ring: MockI2sRing) -> int:
        """可能なだけホップ処理。予算超過は『間に合わず drop』と数える机上モデル。"""
        did = 0
        while ring.available() >= self.n:
            ring.take_window(self.n, self.hop)
            self.frames += 1
            did += 1
            # util>1 なら同じ実時間では積み残しが起きる、という印
            if not self.row["ok"]:
                self.dropped += 1
        return did


class OverlapBudgetTests(unittest.TestCase):
    def test_non_overlap_period(self):
        r = budget_ok(1024, 1024, fft_ms=1.91, glue_ms=2.0)
        self.assertAlmostEqual(r["period_ms"], 1024 / 48.0, places=3)
        self.assertTrue(r["ok"])
        self.assertAlmostEqual(r["delta_f_hz"], 48000 / 1024, places=3)

    def test_hop_half_doubles_fps_cap(self):
        a = budget_ok(1024, 1024, fft_ms=1.91, glue_ms=0.0)
        b = budget_ok(1024, 512, fft_ms=1.91, glue_ms=0.0)
        self.assertAlmostEqual(b["fps_cap"], a["fps_cap"] * 2.0, places=3)

    def test_tight_hop_fails_with_heavy_fft(self):
        # 2*3ms + 2ms = 8ms > 5.33ms*0.85
        r = budget_ok(1024, 256, fft_ms=3.0, glue_ms=2.0, margin=0.85)
        self.assertFalse(r["ok"])

    def test_resolution_independent_of_bar_count(self):
        # 30 本でも 15 本でも Δf は N/fs のみ
        self.assertEqual(delta_f(2048), delta_f(2048))

    def test_ring_overlap_reuses_samples(self):
        ring = MockI2sRing(capacity_frames=4096)
        ring.push_frames(2048)
        w0 = ring.take_window(1024, 512)
        w1 = ring.take_window(1024, 512)
        # hop=512 なので、窓0の後半 512 フレーム = 窓1の前半 512 フレーム
        # 1 フレーム = 2 ワード（L/R）
        self.assertEqual(w0[512 * 2 :], w1[: 512 * 2])

    def test_ring_underrun(self):
        ring = MockI2sRing(capacity_frames=256)
        ring.push_frames(100)
        with self.assertRaises(RuntimeError):
            ring.take_window(1024, 256)

    def test_mock_analyzer_counts(self):
        ring = MockI2sRing(capacity_frames=8192)
        an = MockAnalyzer(1024, 512, fft_ms=1.91, glue_ms=1.0)
        ring.push_frames(1024 + 512 * 3)
        n = an.process_available(ring)
        self.assertEqual(n, 4)
        self.assertEqual(an.frames, 4)


def print_table(glue_ms: float, margin: float) -> None:
    print("fs=%.0f  glue=%.2fms/frame  margin=%.0f%%  "
          "(fft scales ~N log N from %.2fms@1024)"
          % (FS_DEFAULT, glue_ms, 100 * margin, FFT_MS_1024))
    print()
    pairs = []
    for n in (1024, 2048, 4096):
        for hop in (n, n // 2, n // 4):
            if hop < 256:
                continue
            pairs.append((n, hop))
    for n, hop in pairs:
        print(format_row(budget_ok(n, hop, glue_ms=glue_ms, margin=margin)))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--n", type=int, default=None)
    p.add_argument("--hop", type=int, default=None)
    p.add_argument("--fft-ms", type=float, default=None,
                   help="1ch FFT 実測 ms。省略時は N log N スケール")
    p.add_argument("--glue-ms", type=float, default=GLUE_MS_DEFAULT)
    p.add_argument("--margin", type=float, default=0.85)
    p.add_argument("--self-test", action="store_true",
                   help="unittest だけ走らせて終了")
    args = p.parse_args(argv)

    if args.self_test or (args.n is None and args.hop is None):
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(OverlapBudgetTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        if args.self_test:
            return 0 if result.wasSuccessful() else 1
        print()
        if not result.wasSuccessful():
            return 1

    if args.n is not None or args.hop is not None:
        if args.n is None or args.hop is None:
            print("--n と --hop はセットで指定", file=sys.stderr)
            return 2
        r = budget_ok(
            args.n, args.hop, fft_ms=args.fft_ms,
            glue_ms=args.glue_ms, margin=args.margin,
        )
        print(format_row(r))
        print("  analyze=%.2f ms  period=%.2f ms  ok=%s"
              % (r["analyze_ms"], r["period_ms"], r["ok"]))
        return 0 if r["ok"] else 1

    print_table(args.glue_ms, args.margin)
    return 0


if __name__ == "__main__":
    sys.exit(main())
