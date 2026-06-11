from machine import I2C, Pin

from ssd1306 import SSD1306_I2C


WIDTH = 128
HEIGHT = 64
SDA_PIN = 20  # Pico physical pin 26
SCL_PIN = 21  # Pico physical pin 27


def draw_border(display):
    display.fill(0)
    display.rect(0, 0, WIDTH, HEIGHT, 1)
    display.show()


led = Pin("LED", Pin.OUT)
led.off()

i2c = I2C(0, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN), freq=400_000)

devices = i2c.scan()
print("I2C devices:", [hex(device) for device in devices])

oled = None
if devices:
    oled = SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=devices[0])
    draw_border(oled)
else:
    print("No I2C device found on GP20/GP21")
