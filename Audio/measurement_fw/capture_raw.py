"""PCM1804 の生サンプルを USB シリアルへ base64 で吐くだけのスクリプト。

## なぜ生で出すのか

`spectrum.py` 経由の測定は使えない。ブリングアップ実測より:

    固定小数点 FFT の演算ノイズはピークから約 65dB 下

`NORM_BITS = 15` で 24bit ADC の 9bit を捨て、各段で `>>1` するため、
**基本波から 65dB 下が限界**。−100dB 級の高調波は丸め誤差に埋もれて見えない。
`power()` が `re²+im²` に潰すので**位相も捨てられている**。

なので Pico 側では一切解析せず、生の 24bit をそのまま PC へ渡し、
PC 側 numpy（float64）で FFT する。

## 使い方

    mpremote connect COMx cp i2s_rx.py : + run capture_raw.py > cap.txt

    # 繰り返し取る（再現性の床を測るとき）
    for i in 1 2 3 4 5; do
        mpremote connect COMx run capture_raw.py > cap_$i.txt
    done

出力は `analyze_thd.py` に食わせる。

## 出力形式

    # capture v1
    # n_frames <1フレームあたりの L+R ペア数>
    # fs_nominal 48000
    <base64 行が続く>
    # end

base64 の中身は DMA が書いた生の 32bit ワード列（リトルエンディアン）で、
**L, R, L, R, ... の順**。各ワードの下位 24bit が符号付きサンプル。
"""

import gc
import sys
import time

import ubinascii

import i2s_rx

# 1ch あたりのフレーム数。48kHz なので 16384 で約 0.34 秒、Δf ≈ 2.93 Hz。
# L+R 分で 4*2*N バイト要る（16384 なら 128 KB）。Pico 2 の RAM は 520 KB。
N_FRAMES = 16384

DATA_PIN = 0     # GP0=DATA, GP1=BCK, GP2=LRCK
RESET_PIN = 15   # GP15 = ADC_nMR（TPS3307 の ~MR）
CHUNK = 3072     # base64 に流す 1 回のバイト数（4 の倍数にする）


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

    sys.stdout.write("# capture v1\n")
    sys.stdout.write("# n_frames %d\n" % N_FRAMES)
    sys.stdout.write("# fs_nominal 48000\n")
    mv = memoryview(buf)
    for i in range(0, len(buf), CHUNK):
        # b2a_base64 は末尾に改行を付ける
        sys.stdout.write(ubinascii.b2a_base64(mv[i:i + CHUNK]))
    sys.stdout.write("# end\n")


main()
