"""電源投入で LCD スペアナを起動する。"""
from machine import Pin

Pin("LED", Pin.OUT).on()

import spectrum_lcd

spectrum_lcd.main()
