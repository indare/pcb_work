"""USB を抜いた状態で捕まえて RAM に保持する — A1（USB グラウンドループ）の切り分け用。

**なぜ RAM に残すのか。** 1205〜1212Hz の自走スプリアスは
`PC → G8 → アナログ → ADC → Pico → PC` のループ由来という仮説がある
（`../MeasurementADC_BRINGUP.md`）。USB を挿し直すとその環が閉じ直るので、
**挿してから採ったのでは意味が無い**。抜いている間に採って、挿してから読む。

`mpremote` は接続時に Ctrl-C を送るだけで Pico をリセットしないので、
モジュールのグローバルに置いておけば再接続後も生きている。

⚠⚠ **ただし `mpremote exec` は既定でソフトリセットを送る。** 読み出しに使うと
   **RAM を消してから読みに行く**ので、この用途では必ず `resume` を挟むこと。

       mpremote connect <dev> resume exec "import capture_hold; capture_hold.dump()"

   `mpremote --help` の `resume` に「will not auto soft-reset」とある＝既定はリセットする。
   既知の「`mpremote` で繋ぐとスペアナが止まる」と同じ系統の罠。

**電源は USB に依存しない。** Pico の VSYS は `D701`（ショットキ）経由で
基板の `+5V_D` から来ている（`../MeasurementADC_STATUS.md`）。USB を抜いても動く。

使い方:

    # 1. USB を抜く
    # 2. 基板の電源を入れ直す（main.py がこれを呼ぶ）
    # 3. 1320Hz を流す  → 音が来たら自動でラッチして停止する
    # 4. USB を挿して mpremote で繋ぐ
    # 5. 読み出す。**必ず `resume` を挟むこと**:
    #      mpremote connect <dev> resume exec "import capture_hold; capture_hold.dump()"
    #    出力は capture_raw.py と同じ書式なので analyze_thd.py にそのまま渡せる

⚠ **LCD スペアナは起動しないこと。** SPI 40MHz は系で最も騒がしいデジタル源で、
   止めた状態で測る（前回の測定も `mpremote` 接続でスペアナが止まっていたので条件が揃う）。
   `main.py` を `main_capture.py` に差し替えて使う。
"""

import gc
import sys
import time

import ubinascii  # type: ignore

import i2s_rx

N_FRAMES = 16384
N_HOLD = 2          # RAM に残す本数。1本 128KB。足りなければ 1 にする
DATA_PIN = 0        # GP0=DATA, GP1=BCK, GP2=LRCK
RESET_PIN = 15      # GP15 = ADC_nMR
CHUNK = 3072        # base64 に流す 1 回のバイト数（4 の倍数）

# 無音とトーンを分ける閾値。前回の実測は基本波 −16.3 dBFS、無音床は −120 dBFS 級
# なので、間のどこでも効く。24bit フルスケール 0x7FFFFF に対する比。
RMS_TRIGGER = 0.003            # ≒ −50 dBFS
TRIES = 200                    # 音が来るまでの試行回数（1回あたり約 0.35 s）

# --- Ctrl-C しても消えないように、モジュールのグローバルに置く ---------
HOLD = []            # list[bytearray]
INFO = {"tries": 0, "mem_free": 0, "rms": [], "hold_rms": []}


def _rms(buf):
    """24bit 符号付きサンプルの RMS（フルスケール比）。間引いて概算する。"""
    mv = memoryview(buf)
    n = len(buf) // 4
    step = max(1, n // 2048)
    acc = 0
    cnt = 0
    for i in range(0, n, step):
        o = i * 4
        w = mv[o] | (mv[o + 1] << 8) | (mv[o + 2] << 16)
        if w & 0x800000:
            w -= 0x1000000
        acc += w * w
        cnt += 1
    return (acc / cnt) ** 0.5 / 0x7FFFFF if cnt else 0.0


def run(n_hold=N_HOLD, tries=TRIES, trigger=RMS_TRIGGER):
    """音が来るまで採り直し、来たら `HOLD` に保持して止まる。"""
    global HOLD
    HOLD = []
    INFO["rms"] = []
    INFO["hold_rms"] = []
    gc.collect()
    words = N_FRAMES * 2
    scratch = bytearray(words * 4)
    INFO["mem_free"] = gc.mem_free()

    rx = i2s_rx.I2SReceiver(data_pin=DATA_PIN, reset_pin=RESET_PIN)
    rx.reset()
    rx.open()
    try:
        for t in range(tries):
            INFO["tries"] = t + 1
            rx.start_into(scratch, timeout_ms=5000, count=words)
            rx.wait()
            r = _rms(scratch)
            INFO["rms"].append(r)
            if r >= trigger:
                HOLD.append(scratch)
                INFO["hold_rms"].append(r)
                if len(HOLD) >= n_hold:
                    break
                # 次の1本ぶんを新しく確保する（採れなければここで止まる）
                gc.collect()
                try:
                    scratch = bytearray(words * 4)
                except MemoryError:
                    break
            time.sleep_ms(50)
    finally:
        rx.close()

    # ここで止める。連続で採り続けると、USB を挿した瞬間の汚れたデータで
    # 上書きしてしまう（それでは切り分けにならない）。
    while True:
        time.sleep(1)


def dump(index=0):
    """`capture_raw.py` と同じ書式で吐く。`analyze_thd.py` にそのまま渡せる。"""
    if index >= len(HOLD):
        sys.stdout.write("# no capture (tries=%d)\n" % INFO.get("tries", 0))
        return
    buf = HOLD[index]
    sys.stdout.write("# capture v1\n")
    sys.stdout.write("# n_frames %d\n" % N_FRAMES)
    sys.stdout.write("# fs_nominal 48000\n")
    sys.stdout.write("# source capture_hold index=%d rms=%.6f\n"
                     % (index, INFO["hold_rms"][index]
                        if index < len(INFO["hold_rms"]) else 0.0))
    mv = memoryview(buf)
    for i in range(0, len(buf), CHUNK):
        sys.stdout.write(ubinascii.b2a_base64(mv[i:i + CHUNK]))
    sys.stdout.write("# end\n")


def status():
    sys.stdout.write("held=%d tries=%d mem_free=%d rms=%s\n"
                     % (len(HOLD), INFO.get("tries", 0), INFO.get("mem_free", 0),
                        [round(x, 5) for x in INFO.get("rms", [])[-5:]]))
