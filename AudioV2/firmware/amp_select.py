"""Amp CH 切替 — Switch / Relay 共通入口。

UI（ENC_CH）と LCD 表示はバックエンドを知らない。
裏だけ `backend=\"switch\"|\"relay\"` で差し替える。
"""

import board


class AmpSelect:
    def __init__(self, i2c, backend=None):
        self.i2c = i2c
        self.backend = backend or board.AMP_BACKEND
        self.channel = 1  # 1-based 表示用
        self._impl = _make(self.backend, i2c)

    def apply(self, ch):
        self.channel = int(ch)
        self._impl.apply(self.channel)

    def nudge(self, delta, lo=1, hi=12):
        self.apply(max(lo, min(hi, self.channel + delta)))


def _make(backend, i2c):
    if backend == "relay":
        return _RelayBank(i2c)
    return _SwitchBank(i2c)


class _SwitchBank:
    """AmpBankSwitch — スロット MCP → TMUX SEL。"""

    def __init__(self, i2c):
        self.i2c = i2c

    def apply(self, ch):
        # TODO: スロット番号と局所 CH に分解し、MCP GPIO で SEL を立てる
        _ = (self.i2c, ch)


class _RelayBank:
    """AmpBankRelay — スロット MCP → ラッチング駆動（v1 relays の流れを MCP 越しに）。"""

    def __init__(self, i2c):
        self.i2c = i2c

    def apply(self, ch):
        # TODO: SET/RESET パルス（コイル＋音声の順は v1 Control/relays.py を参照）
        _ = (self.i2c, ch)
