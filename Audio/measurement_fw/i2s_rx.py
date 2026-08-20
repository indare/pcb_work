"""PCM1804（共立 ADC1804_F モジュール）からの I2S 受信。

ADC 側がマスタで BCK / LRCK を出すため `machine.I2S` は使えない。
rp2 の実装はクロックを自分で生成するマスタ専用で、ADC と衝突する。
そのため PIO で LRCK に同期し、BCK の立ち上がりごとに DATA を 1 ビット取り込む。

ピンは DATA / BCK / LRCK が連番である必要がある（PIO の `wait` が
in_base からの相対インデックスでピンを見るため）。初号機では GP0/1/2。
"""

import array
import machine
import rp2
import time
from machine import Pin

PIO0_RXF0 = 0x50200020
DREQ_PIO0_RX0 = 4
FULL_SCALE = 1 << 23


@rp2.asm_pio(in_shiftdir=rp2.PIO.SHIFT_LEFT, autopush=True, push_thresh=24)
def _i2s_slave_rx():
    wrap_target()

    wait(1, pin, 2)
    wait(0, pin, 2)
    wait(0, pin, 1)
    wait(1, pin, 1)            # I2S は LRCK 遷移の 1BCK 後が MSB。ここは捨てる
    set(x, 23)
    label("lbit")
    wait(0, pin, 1)
    wait(1, pin, 1)
    in_(pins, 1)
    jmp(x_dec, "lbit")

    wait(1, pin, 2)
    wait(0, pin, 1)
    wait(1, pin, 1)
    set(x, 23)
    label("rbit")
    wait(0, pin, 1)
    wait(1, pin, 1)
    in_(pins, 1)
    jmp(x_dec, "rbit")

    wrap()


def to_signed(word):
    v = word & 0xFFFFFF
    return v - 0x1000000 if v & 0x800000 else v


class I2SReceiver:
    """PCM1804 が出す 24bit I2S を DMA で連続取得する。

    `data_pin` から連番で BCK / LRCK が並んでいること。
    `reset_pin` を渡すと `reset()` で TPS3307 の ~MR を L にして ADC を落とす。
    H は駆動せず IC 内部プルアップに任せる（~RESET はプッシュプルなのでワイヤ AND しない）。
    """

    def __init__(self, data_pin=0, reset_pin=None, sm_id=0):
        self._data = data_pin
        self._reset = reset_pin
        self._sm_id = sm_id
        self._sm = None
        self._dma = None
        for offset in range(3):
            Pin(data_pin + offset, Pin.IN, None)
        if reset_pin is not None:
            Pin(reset_pin, Pin.IN, None)

    def reset(self, low_ms=50, settle_ms=300):
        if self._reset is None:
            return
        p = Pin(self._reset, Pin.OUT)
        p.value(0)
        time.sleep_ms(low_ms)
        p.init(Pin.IN, None)
        time.sleep_ms(settle_ms)

    def open(self):
        """PIO と DMA を確保する。連続描画では毎フレーム作り直さない。"""
        if self._sm is None:
            self._sm = rp2.StateMachine(self._sm_id, _i2s_slave_rx,
                                        freq=machine.freq(),
                                        in_base=Pin(self._data))
            self._dma = rp2.DMA()
        return self

    def close(self):
        if self._sm is None:
            return
        self._sm.active(0)
        self._dma.close()
        rp2.PIO(0).remove_program(_i2s_slave_rx)
        self._sm = None
        self._dma = None

    def start_into(self, buf, timeout_ms=1000, count=None):
        """DMA を起動して戻る。完了は `wait()`。先頭は必ず L。

        count は 32bit ワード数。省略時はバッファ全体。2k 確保のまま
        1k だけ取りたいときに使う。
        """
        self.open()
        sm = self._sm
        dma = self._dma
        sm.active(0)
        while sm.rx_fifo():
            sm.get()
        sm.restart()
        if count is None:
            count = len(buf)
        ctrl = dma.pack_ctrl(size=2, inc_read=False, inc_write=True,
                             treq_sel=DREQ_PIO0_RX0)
        dma.config(read=PIO0_RXF0, write=buf, count=count, ctrl=ctrl,
                   trigger=True)
        sm.active(1)
        self._t0 = time.ticks_ms()
        self._timeout_ms = timeout_ms
        return buf

    def wait(self):
        """`start_into` の DMA 完了を待つ。"""
        dma = self._dma
        sm = self._sm
        t0 = self._t0
        timeout_ms = self._timeout_ms
        while dma.active():
            if time.ticks_diff(time.ticks_ms(), t0) > timeout_ms:
                sm.active(0)
                raise RuntimeError("I2S DMA タイムアウト（BCK/LRCK が出ていない）")
            # ビジーループだと GIL を握ったままになり、他コアの描画が止まる。
            time.sleep_us(50)
        sm.active(0)

    def read_into(self, buf, timeout_ms=1000, count=None):
        """buf を L/R 交互の生 32bit ワードで埋める。先頭は必ず L。

        毎回ステートマシンを止めて再スタートするので、フレーム境界が
        バッファ先頭に揃う。連続録音ではなくスナップショット用。
        FFT と重ねる場合は `start_into` / `wait` を使う。
        """
        self.start_into(buf, timeout_ms, count)
        self.wait()
        return buf

    def capture(self, nframe, timeout_ms=1000):
        """L/R 交互に nframe*2 ワードを取得して生の 32bit 配列で返す。"""
        buf = array.array('I', bytearray(8 * nframe))
        try:
            return self.read_into(buf, timeout_ms)
        finally:
            self.close()

    def capture_channels(self, nframe, timeout_ms=1000):
        """L/R を分離した符号付き整数のリストを返す。"""
        vals = [to_signed(w) for w in self.capture(nframe, timeout_ms)]
        return vals[0::2], vals[1::2]
