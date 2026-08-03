# Shared I2C expansion protocol (parent master <-> child slave).

SLAVE_ADDR = 0x42
OLED_ADDR = 0x3C
# 100kHz makes the 1KB SSD1306 frame write exceed the I2C transfer timeout.
I2C_FREQ = 400_000

SDA_PIN = 20  # Pico physical pin 26
SCL_PIN = 21  # Pico physical pin 27

# Parent writes command to register 0.
# Child publishes status in register 1 and increments register 2 on completion.
REG_CMD = 0
REG_STATUS = 1
REG_DONE = 2

CMD_RESET = 0x00
CMD_APPLY_MIN = 0x01  # local CH1
CMD_APPLY_MAX = 0x05  # local CH5
CMD_PING = 0x10

STATUS_IDLE = 0x00
STATUS_BUSY = 0x01
STATUS_OK = 0x02
STATUS_ERR = 0xFF
STATUS_PONG = 0xA5

LOCAL_CHANNELS = 5
MAX_CHANNELS = 10
APPLY_TIMEOUT_MS = 2000
