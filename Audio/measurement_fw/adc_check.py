"""MeasurementADC のブリングアップ確認。

クロックの実測と I2S 受信を一度に行い、期待値と突き合わせる。

    mpremote connect <port> run adc_check.py

GP9 は CN3F-1 への飛ばし配線が残っているが、**駆動してはいけない**。
Y701 と R718(33Ω) を挟んで衝突し SCKI が化ける。ここでは入力として読むだけ。
"""

import machine
import rp2
import time
from machine import Pin

from i2s_rx import I2SReceiver, FULL_SCALE

SCKI_PROBE = 9
RESET_PIN = 15
DATA_PIN = 0
FSAMP = 48000.0

EXPECT = (
    ("SCKI", SCKI_PROBE, 12_288_000, 32768),
    ("BCK", DATA_PIN + 1, 3_072_000, 1024),
    ("LRCK", DATA_PIN + 2, 48_000, 32),
)


@rp2.asm_pio()
def _edge_count():
    pull(block)
    label("restart")
    mov(y, osr)
    label("outer")
    set(x, 31)
    label("inner")
    wait(0, pin, 0)
    wait(1, pin, 0)
    jmp(x_dec, "inner")
    jmp(y_dec, "outer")
    in_(null, 32)
    push()
    jmp("restart")


def frequency(gpio, per_push=1024, gate_ms=400, timeout_ms=1000):
    """最初と最後の push の時刻だけで割るので端数切り捨て誤差が出ない。"""
    sm = rp2.StateMachine(0, _edge_count, freq=machine.freq(),
                          in_base=Pin(gpio, Pin.IN, None))
    try:
        sm.active(1)
        sm.put(per_push // 32 - 1)
        t0 = time.ticks_ms()
        while not sm.rx_fifo():
            if time.ticks_diff(time.ticks_ms(), t0) > timeout_ms:
                return 0.0
        sm.get()
        t_first = time.ticks_us()
        n = 0
        t_last = t_first
        while time.ticks_diff(time.ticks_us(), t_first) < gate_ms * 1000:
            if sm.rx_fifo():
                sm.get()
                t_last = time.ticks_us()
                n += 1
        if n == 0:
            return 0.0
        return n * per_push / (time.ticks_diff(t_last, t_first) / 1e6)
    finally:
        sm.active(0)
        rp2.PIO(0).remove_program(_edge_count)


def check_clocks():
    print("クロック実測")
    print("  %-6s %14s %14s %8s" % ("信号", "実測[Hz]", "期待[Hz]", "誤差"))
    results = {}
    ok = True
    for name, gpio, want, per_push in EXPECT:
        got = frequency(gpio, per_push=per_push)
        results[name] = got
        err = (got - want) / want * 100 if got else -100.0
        print("  %-6s %14.1f %14d %7.2f%%" % (name, got, want, err))
        if abs(err) > 1.0:
            ok = False
    if results.get("LRCK"):
        print("  SCKI/LRCK = %.3f （256 が正常）" % (results["SCKI"] / results["LRCK"]))
        print("  BCK/LRCK  = %.3f （64 が正常）" % (results["BCK"] / results["LRCK"]))
    if not ok:
        print("  ★期待値から外れている。標準にない分周比なら SCKI の衝突を疑う★")
    return ok


def describe(name, ch):
    n = len(ch)
    dc = sum(ch) / n
    ac = [v - dc for v in ch]
    rms = (sum(v * v for v in ac) / n) ** 0.5
    peak = max(max(ac), -min(ac))
    print("  %s  DC=%9.0f  RMS=%7.3f %%FS  peak=%7.3f %%FS"
          % (name, dc, rms / FULL_SCALE * 100, peak / FULL_SCALE * 100))


def main():
    Pin(SCKI_PROBE, Pin.IN, None)
    rx = I2SReceiver(data_pin=DATA_PIN, reset_pin=RESET_PIN)
    rx.reset()

    print("=" * 70)
    ok = check_clocks()
    print("=" * 70)
    if not ok:
        return

    nframe = 512
    left, right = rx.capture_channels(nframe)
    print("I2S 受信 %d フレーム（%.1f ms）" % (nframe, nframe / FSAMP * 1000))
    describe("L", left)
    describe("R", right)
    print("  L 先頭: %s" % left[:6])
    print("  R 先頭: %s" % right[:6])
    print("=" * 70)


main()
