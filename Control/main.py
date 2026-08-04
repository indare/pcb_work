from machine import I2C, Pin
import time

from protocol import (
    APPLY_TIMEOUT_MS,
    CMD_APPLY_MAX,
    CMD_APPLY_MIN,
    CMD_PING,
    CMD_RESET,
    I2C_FREQ,
    LOCAL_CHANNELS,
    MAX_CHANNELS,
    OLED_ADDR,
    REG_CMD,
    REG_DONE,
    REG_STATUS,
    SCL_PIN,
    SDA_PIN,
    SLAVE_ADDR,
    STATUS_OK,
    STATUS_PONG,
)
from relays import RelayBoard
from ssd1306 import SSD1306_I2C


WIDTH = 128
HEIGHT = 64
ENC_A_PIN = 22  # Pico physical pin 29
ENC_B_PIN = 26  # Pico physical pin 31
ENC_SW_PIN = 27  # Pico physical pin 32
RESET_TO_SET_SEC = 0.5
LOOP_DELAY_SEC = 0.01
BUTTON_DEBOUNCE_MS = 250


def draw_status(display, title, line1="", line2="", line3="", line4=""):
    display.fill(0)
    display.rect(0, 0, WIDTH, HEIGHT, 1)
    display.text(title[:15], 4, 4)
    display.text(line1[:15], 4, 16)
    display.text(line2[:15], 4, 28)
    display.text(line3[:15], 4, 40)
    display.text(line4[:15], 4, 52)
    display.show()


def update_display(title, line1="", line2="", line3="", line4=""):
    if oled:
        draw_status(oled, title, line1, line2, line3, line4)


def slave_done_seq():
    return i2c.readfrom_mem(SLAVE_ADDR, REG_DONE, 1)[0]


def slave_send(cmd):
    before = slave_done_seq()
    i2c.writeto_mem(SLAVE_ADDR, REG_CMD, bytes([cmd]))
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < APPLY_TIMEOUT_MS:
        if slave_done_seq() != before:
            status = i2c.readfrom_mem(SLAVE_ADDR, REG_STATUS, 1)[0]
            return status in (STATUS_OK, STATUS_PONG)
        time.sleep_ms(20)
    return False


def ping_slave():
    try:
        return slave_send(CMD_PING)
    except OSError as exc:
        print("slave ping failed:", exc)
        return False


def wait_for_expansion(timeout_ms=3000):
    """Child starts I2CTarget only after its local boot reset, so retry briefly."""
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < timeout_ms:
        try:
            if SLAVE_ADDR in i2c.scan() and ping_slave():
                return True
        except OSError as exc:
            print("expansion probe:", exc)
        time.sleep_ms(100)
    return False


def apply_global_channel(channel):
    if channel <= LOCAL_CHANNELS:
        if has_expansion:
            try:
                if not slave_send(CMD_RESET):
                    update_display("Exp timeout", "reset", "", "", "")
            except OSError as exc:
                print("slave reset failed:", exc)
                update_display("Exp error", "reset failed", str(exc)[:15], "", "")
        board.apply_channel(channel)
        return

    local = channel - LOCAL_CHANNELS
    if local < CMD_APPLY_MIN or local > CMD_APPLY_MAX:
        raise ValueError("expansion channel out of range")

    board.reset_all("Local RESET")
    try:
        if not slave_send(local):
            update_display("Exp timeout", "CH" + str(channel), "slave busy?", "", "")
    except OSError as exc:
        print("slave apply failed:", exc)
        update_display("Exp error", "CH" + str(channel), str(exc)[:15], "", "")


def draw_channel_ui():
    mark = "*" if selected_channel == active_channel else ">"
    update_display(
        "Select CH" + str(selected_channel),
        "Active CH" + str(active_channel),
        mark + " CH" + str(selected_channel),
        "Max CH" + str(channel_count),
        "Push: apply",
    )


led = Pin("LED", Pin.OUT)
led.off()

enc_a = Pin(ENC_A_PIN, Pin.IN, Pin.PULL_UP)
enc_b = Pin(ENC_B_PIN, Pin.IN, Pin.PULL_UP)
enc_sw = Pin(ENC_SW_PIN, Pin.IN, Pin.PULL_UP)

i2c = I2C(0, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN), freq=I2C_FREQ)
devices = i2c.scan()
print("I2C devices:", [hex(device) for device in devices])

oled = None
if OLED_ADDR in devices:
    oled = SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=OLED_ADDR)
elif devices:
    # Fall back to the first non-slave device if address wiring differs.
    for addr in devices:
        if addr != SLAVE_ADDR:
            oled = SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=addr)
            break
else:
    print("No I2C device found on GP20/GP21")

board = RelayBoard(led=led, on_status=update_display)

update_display("Boot", "OLED OK", "Wait exp...", "", "")
has_expansion = wait_for_expansion()
channel_count = MAX_CHANNELS if has_expansion else LOCAL_CHANNELS
print("expansion:", has_expansion, "channels:", channel_count)

if has_expansion:
    update_display("Boot", "OLED OK", "Exp found", "CH1-" + str(channel_count), "")
else:
    update_display("Boot", "OLED OK", "Solo mode", "CH1-" + str(channel_count), "")

board.reset_all("Power-on RESET")
if has_expansion:
    try:
        if not slave_send(CMD_RESET):
            print("slave boot reset timeout")
            has_expansion = False
            channel_count = LOCAL_CHANNELS
    except OSError as exc:
        print("slave boot reset failed:", exc)
        has_expansion = False
        channel_count = LOCAL_CHANNELS

time.sleep(RESET_TO_SET_SEC)

selected_channel = 1
active_channel = 1
apply_global_channel(1)
draw_channel_ui()

last_encoder_state = (enc_a.value() << 1) | enc_b.value()
encoder_direction = 0
last_button_ms = time.ticks_ms()
last_selected_channel = selected_channel
last_active_channel = active_channel

while True:
    encoder_state = (enc_a.value() << 1) | enc_b.value()
    if encoder_state != last_encoder_state:
        if last_encoder_state == 3 and encoder_state == 1:
            encoder_direction = 1
        elif last_encoder_state == 3 and encoder_state == 2:
            encoder_direction = -1
        elif encoder_state == 3 and encoder_direction:
            selected_channel = min(
                channel_count, max(1, selected_channel + encoder_direction)
            )
            encoder_direction = 0

        last_encoder_state = encoder_state

    now_ms = time.ticks_ms()
    if enc_sw.value() == 0 and time.ticks_diff(now_ms, last_button_ms) > BUTTON_DEBOUNCE_MS:
        last_button_ms = now_ms
        if selected_channel != active_channel:
            apply_global_channel(selected_channel)
            active_channel = selected_channel

    if selected_channel != last_selected_channel or active_channel != last_active_channel:
        draw_channel_ui()
        last_selected_channel = selected_channel
        last_active_channel = active_channel

    time.sleep(LOOP_DELAY_SEC)
