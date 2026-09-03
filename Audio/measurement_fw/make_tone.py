#!/usr/bin/env python3
"""THD 測定用の試験音 WAV を作る。

## なぜ専用ファイルが要るか

**YouTube 等のストリーミングは測定に使えない**（2026-09-03 に実際にやってしまった）:

- **ラウドネス正規化**で −14 LUFS 前後に絞られる。G8 を最大にしても
  ADC で −16.3 dBFS までしか上がらなかった原因がこれ
- **非可逆圧縮（AAC/Opus）**が心理音響モデルに従ったスプリアスを載せる
- そのアーティファクトは**コーデックのフレームごとに変わる**ので、
  キャプチャのたびに H2/H3 の位相がランダムになる（実際そうなった）

## この生成器の作り

- **24bit PCM**。量子化歪みは −144 dBFS 相当で無視できる
- **TPDF ディザ 1LSB**。量子化による高調波を雑音に置き換える
- **ループ継ぎ目でクリックが出ない長さ**にする。`fs/gcd(f, fs)` サンプルの
  整数倍にすると整数周期で閉じる（1320Hz / 48kHz なら 400 サンプルの倍数）
- 既定は **−1 dBFS**。純音なので intersample over はほぼ出ないが余裕を取る

使い方:
  python3 make_tone.py                      # 1320Hz / 10秒 / -1dBFS
  python3 make_tone.py --freq 1320 --db -1 --sec 10 -o tone.wav
"""

from __future__ import annotations

import argparse
import math
import wave

import numpy as np


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--freq", type=float, default=1320.0)
    ap.add_argument("--fs", type=int, default=48000)
    ap.add_argument("--sec", type=float, default=10.0)
    ap.add_argument("--db", type=float, default=-1.0, help="ピーク dBFS")
    ap.add_argument("--no-dither", action="store_true")
    ap.add_argument("-o", "--out", default="tone_1320.wav")
    a = ap.parse_args()

    # ループが整数周期で閉じる長さに丸める
    period = a.fs // math.gcd(int(round(a.freq)), a.fs)
    n = int(round(a.sec * a.fs / period)) * period
    cycles = a.freq * n / a.fs
    t = np.arange(n, dtype=np.float64) / a.fs
    amp = 10 ** (a.db / 20) * (2 ** 23 - 1)
    x = amp * np.sin(2 * np.pi * a.freq * t)

    if not a.no_dither:
        # TPDF 1LSB。量子化で出る高調波を雑音に均す
        rng = np.random.default_rng(0)
        x = x + rng.random(n) - rng.random(n)

    q = np.clip(np.round(x), -(2 ** 23), 2 ** 23 - 1).astype(np.int32)
    # 24bit little-endian、L/R 同一
    b = q.astype("<i4").tobytes()
    mono24 = bytearray()
    for i in range(0, len(b), 4):
        mono24 += b[i:i + 3]
    frames = bytearray()
    for i in range(0, len(mono24), 3):
        frames += mono24[i:i + 3] * 2      # L と R に同じものを入れる

    with wave.open(a.out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(3)
        w.setframerate(a.fs)
        w.writeframes(bytes(frames))

    print(f"{a.out}: {a.freq}Hz  {a.fs}Hz  24bit stereo  "
          f"{n} サンプル ({n/a.fs:.3f}秒)  ピーク {a.db} dBFS")
    print(f"  整数周期 {cycles:.0f} 周期でちょうど閉じる → ループしてもクリックが出ない")
    print(f"  ディザ: {'なし' if a.no_dither else 'TPDF 1LSB'}")
    print("\n⚠ 再生時の注意:")
    print("  ・ストリーミング（YouTube 等）は不可。ラウドネス正規化と非可逆圧縮が乗る")
    print("  ・プレーヤの音量正規化・イコライザ・アップサンプリングを全部切ること")
    print("  ・OS のミキサも 48kHz / ビットパーフェクトに寄せる")


if __name__ == "__main__":
    main()
