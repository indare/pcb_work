"""Amp CH 切替 — Switch / Relay 共通入口。

UI（ENC_CH）と LCD 表示はバックエンドを知らない。
裏だけ `backend=\"switch\"|\"relay\"` で差し替える。

## Switch SEL（実装時の必須）

回路に SEL→D_GND の外付けプルは置かない（TMUX7612 に SEL 内蔵プルダウンあり）。
その代わりファームで次を守る:

1. I²C が通ったら**すぐ**各スロット MCP の SEL 担当 GPIO（GPB0–3＝SEL_CH1–4）を
   **出力**にし、全 ch Low、または既定 ch だけ High の既知値を書く
2. `main` は UI MCP 初期化のあと、早めに `AmpSelect.apply(既定ch)` を呼ぶ
   （I²C 前の数百 ms は TMUX 内蔵 PD に任せる）
3. MCP の該当ピンに内部プルアップを付けない
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
        # TODO: 検出した娘 MCP それぞれについて IODIR を出力・SEL を既知値へ
        # （モジュール先頭の「Switch SEL」を参照）

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
