"""A1 切り分け用の main.py（フラッシュ書き込み版）。LCD スペアナは起動しない。

LED 点灯 = 捕捉待ち / 消灯 = フラッシュにキャプチャがある。
詳細は capture_to_flash.py の docstring。
"""
import time

from machine import Pin

led = Pin("LED", Pin.OUT)
led.on()

# ⚠ 起動直後に捕捉へ入ってはいけない（2026-09-07 実測）。
#
# USB の列挙はホストとの数百 ms のやり取りで完了する。その間 MicroPython は
# USB タスクを回し続ける必要があるが、`capture_to_flash.run()` は
# `rx.wait()` でブロックするので応答できない。**電源投入後に COM ポートが
# 一切現れなくなり、BOOTSEL から UF2 を焼き直すまで復旧しなかった。**
#
# ソフトリセット（mpremote reset）では USB の列挙が維持されるので、この罠は
# 完全な電源断のときだけ出る。切り分けの本番はまさにそれなので必ず踏む。
#
# USB を挿さずに使うときも、5 秒待つだけで害は無い。
time.sleep(5)

import capture_to_flash

capture_to_flash.run()
led.value(0 if capture_to_flash.have() else 1)
