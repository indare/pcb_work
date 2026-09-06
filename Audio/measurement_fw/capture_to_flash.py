"""USB を抜いた状態で捕捉し、**Pico のフラッシュへ書く**。

## なぜ `capture_hold` ではなくこれなのか

`capture_hold` は捕捉結果を RAM に置き、USB を挿し直してから読む設計だった。
**2026-09-07 に実測して、その前提が崩れた** —— **Pico を USB 未接続で起動すると、
後から挿しても USB CDC が列挙されない**（ケーブルを替えても同じ。LED は点いていて
Pico 自体は動いている）。通信を戻すにはリセットが要り、リセットすれば RAM は消える。

そこで**ラッチした時点でフラッシュへ書く**。リセットしても残る。

## 上書き防止のガード

USB を復活させるには「USB を挿した状態で電源再投入」が要る。そのとき `main.py` が
また走るので、**出力ファイルが既にあれば捕捉しない**。これが無いと、読み出す前に
USB 接続状態のデータで上書きしてしまう（それでは切り分けにならない）。

## LED

    点灯 = 捕捉待ち / 消灯 = フラッシュにキャプチャがある

USB が無い状態で進行が分かる唯一の手段なので、消えたら採れている。

## 使い方

    1. 前回のを消す:  mpremote connect COMx rm :cap_hold.txt
    2. USB を抜く → 基板を電源再投入 → トーンを流す → LED が消えたら採れた
    3. USB を挿す → **基板を電源再投入**（ガードが効いて捕捉はスキップ）
    4. mpremote connect COMx cp :cap_hold.txt cap_usbout_1.txt

書式は `capture_raw.py` と同一なので `analyze_thd.py` にそのまま渡せる。
"""

import gc
import os
import time

import ubinascii  # type: ignore

import capture_hold
import i2s_rx

OUT = "/cap_hold.txt"
CHUNK = 3072
NL = bytes([10])


def have():
    try:
        os.stat(OUT)
        return True
    except OSError:
        return False


def _write(buf, rms, tries):
    with open(OUT, "wb") as f:
        f.write(b"# capture v1" + NL)
        f.write(("# n_frames %d" % capture_hold.N_FRAMES).encode() + NL)
        f.write(b"# fs_nominal 48000" + NL)
        f.write(("# source capture_to_flash rms=%.6f tries=%d"
                 % (rms, tries)).encode() + NL)
        mv = memoryview(buf)
        for i in range(0, len(buf), CHUNK):
            f.write(ubinascii.b2a_base64(mv[i:i + CHUNK]))
        f.write(b"# end" + NL)


def run(tries=capture_hold.TRIES, trigger=capture_hold.RMS_TRIGGER):
    if have():
        print("already have", OUT, "- skip")
        return False
    gc.collect()
    words = capture_hold.N_FRAMES * 2
    buf = bytearray(words * 4)
    rx = i2s_rx.I2SReceiver(data_pin=capture_hold.DATA_PIN,
                            reset_pin=capture_hold.RESET_PIN)
    rx.reset()
    rx.open()
    got = None
    try:
        for t in range(tries):
            rx.start_into(buf, timeout_ms=5000, count=words)
            rx.wait()
            r = capture_hold._rms(buf)
            if r >= trigger:
                got = (r, t + 1)
                break
            time.sleep_ms(50)
    finally:
        rx.close()
    if got is None:
        print("no signal after", tries, "tries")
        return False
    _write(buf, got[0], got[1])
    print("wrote", OUT, os.stat(OUT)[6], "bytes rms=%.6f tries=%d" % got)
    return True
