"""A1 切り分け用の main.py。**LCD スペアナは起動しない。**

使うときは Pico 上で `main.py` をこれに差し替える（元の `main.py` は残しておく）。
SPI 40MHz の LCD を止めた状態で測るのが狙い。詳細は `capture_hold.py` の docstring。
"""
from machine import Pin

Pin("LED", Pin.OUT).on()

import capture_hold

capture_hold.run()
