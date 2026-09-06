"""`capture_raw.py` と同じ捕捉を、stdout ではなく Pico のファイルへ書く。

## なぜ分けたか

`capture_raw.py` は base64 を `sys.stdout` へ流す。**USB CDC は書き込みが速すぎると
64 バイト単位で取りこぼす。** 2026-09-07 の実測では 16384 フレームのキャプチャで
毎回 64〜318 文字が欠落し、base64 が復号できなかった（PowerShell / cmd / Git Bash の
どれでも同じだったので、シェルではなく転送そのものの問題）。

**欠けると致命的。** 64 バイト落ちると以降のサンプルが 16 ワードずれて L/R が入れ替わり、
波形に段差が入る。段差は広帯域スプラッタになるので、−78 dBFS のスパーを測る用途では
「少しだけ欠けた」では済まない。

`mpremote cp` は raw REPL の確認応答付きプロトコルなので取りこぼさない。
そこで **一度 Pico のファイルに書いて、cp で回収する。**

使い方:

    mpremote connect COMx run capture_to_file.py
    mpremote connect COMx cp :cap.txt cap_on_1.txt

出力書式は `capture_raw.py` と同一なので `analyze_thd.py` にそのまま渡せる。
"""

import gc
import os

import ubinascii

import i2s_rx

# capture_raw.py と同じ値にすること（書式互換のため）
N_FRAMES = 16384

DATA_PIN = 0     # GP0=DATA, GP1=BCK, GP2=LRCK
RESET_PIN = 15   # GP15 = ADC_nMR（TPS3307 の ~MR）
CHUNK = 3072     # base64 に流す 1 回のバイト数（4 の倍数にする）
OUT = "/cap.txt"

NL = bytes([10])


def main():
    gc.collect()
    words = N_FRAMES * 2                  # L/R 交互
    buf = bytearray(words * 4)

    rx = i2s_rx.I2SReceiver(data_pin=DATA_PIN, reset_pin=RESET_PIN)
    rx.reset()
    rx.open()
    try:
        rx.start_into(buf, timeout_ms=5000, count=words)
        rx.wait()
    finally:
        rx.close()

    with open(OUT, "wb") as f:
        f.write(b"# capture v1" + NL)
        f.write(("# n_frames %d" % N_FRAMES).encode() + NL)
        f.write(b"# fs_nominal 48000" + NL)
        mv = memoryview(buf)
        for i in range(0, len(buf), CHUNK):
            # b2a_base64 は末尾に改行を付ける
            f.write(ubinascii.b2a_base64(mv[i:i + CHUNK]))
        f.write(b"# end" + NL)

    print("wrote", OUT, os.stat(OUT)[6], "bytes")


main()
