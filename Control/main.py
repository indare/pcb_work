from machine import I2C, Pin
import time

from ssd1306 import SSD1306_I2C


WIDTH = 128
HEIGHT = 64
SDA_PIN = 20  # Pico physical pin 26
SCL_PIN = 21  # Pico physical pin 27
ENC_A_PIN = 22  # Pico physical pin 29
ENC_B_PIN = 26  # Pico physical pin 31
ENC_SW_PIN = 27  # Pico physical pin 32
PULSE_SEC = 0.1
RESET_TO_SET_SEC = 0.5
LOOP_DELAY_SEC = 0.01
BUTTON_DEBOUNCE_MS = 250

ENCODER_STEPS = {
    (0, 1): 1,
    (1, 3): 1,
    (3, 2): 1,
    (2, 0): 1,
    (0, 2): -1,
    (2, 3): -1,
    (3, 1): -1,
    (1, 0): -1,
}

CHANNELS = (
    {
        "number": 1,
        "audio": {"name": "K4 AUDIO", "reset_pin": 5, "set_pin": 4},
        "pwr": {"name": "K3 PWR", "reset_pin": 7, "set_pin": 6},
    },
    {
        "number": 2,
        "audio": {"name": "K2 AUDIO", "reset_pin": 1, "set_pin": 0},
        "pwr": {"name": "K1 PWR", "reset_pin": 3, "set_pin": 2},
    },
    {
        "number": 3,
        "audio": {"name": "K8 AUDIO", "reset_pin": 9, "set_pin": 8},
        "pwr": {"name": "K5 PWR", "reset_pin": 11, "set_pin": 10},
    },
    {
        "number": 4,
        "audio": {"name": "K9 AUDIO", "reset_pin": 13, "set_pin": 12},
        "pwr": {"name": "K6 PWR", "reset_pin": 15, "set_pin": 14},
    },
    {
        "number": 5,
        "audio": {"name": "K10 AUDIO", "reset_pin": 18, "set_pin": 19},
        "pwr": {"name": "K7 PWR", "reset_pin": 16, "set_pin": 17},
    },
)


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


def pulse(outputs, coil_name):
    for output in outputs:
        output[coil_name].on()
    time.sleep(PULSE_SEC)
    for output in outputs:
        output[coil_name].off()


def reset_all(title):
    led.off()
    for output in relay_outputs:
        output["state"] = "RESET"
    update_display(title, "All channels", "RESET pulse", "Coils 0.1 sec")
    pulse(relay_outputs, "reset")


def apply_channel(channel):
    target_outputs = [
        output for output in relay_outputs if output["channel"] == channel["number"]
    ]
    for output in relay_outputs:
        output["state"] = "SET" if output in target_outputs else "RESET"

    led.on()
    update_display(
        "Apply CH" + str(channel["number"]),
        channel["audio"]["name"],
        channel["pwr"]["name"],
        "RESET all",
        "then SET",
    )
    pulse(relay_outputs, "reset")
    time.sleep(RESET_TO_SET_SEC)
    pulse(target_outputs, "set")


def draw_channel_ui():
    mark = "*" if selected_channel == active_channel else ">"
    update_display(
        "Select CH" + str(selected_channel),
        "Active CH" + str(active_channel),
        mark + " CH" + str(selected_channel),
        "Turn: select",
        "Push: apply",
    )


led = Pin("LED", Pin.OUT)
led.off()

enc_a = Pin(ENC_A_PIN, Pin.IN, Pin.PULL_UP)
enc_b = Pin(ENC_B_PIN, Pin.IN, Pin.PULL_UP)
enc_sw = Pin(ENC_SW_PIN, Pin.IN, Pin.PULL_UP)

relay_outputs = []
for channel in CHANNELS:
    for role in ("audio", "pwr"):
        relay = channel[role]
        reset_output = Pin(relay["reset_pin"], Pin.OUT)
        set_output = Pin(relay["set_pin"], Pin.OUT)
        reset_output.off()
        set_output.off()
        relay_outputs.append(
            {
                "channel": channel["number"],
                "name": relay["name"],
                "reset": reset_output,
                "set": set_output,
                "state": "OFF",
            }
        )

i2c = I2C(0, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN), freq=400_000)

devices = i2c.scan()
print("I2C devices:", [hex(device) for device in devices])

oled = None
if devices:
    oled = SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=devices[0])
    draw_status(oled, "Encoder UI", "OLED OK", "Ready", "CH1-5")
else:
    print("No I2C device found on GP20/GP21")

reset_all("Power-on RESET")
time.sleep(RESET_TO_SET_SEC)

selected_channel = 1
active_channel = 1
apply_channel(CHANNELS[0])
draw_channel_ui()

last_encoder_state = (enc_a.value() << 1) | enc_b.value()
encoder_accum = 0
last_button_ms = time.ticks_ms()
last_selected_channel = selected_channel
last_active_channel = active_channel

while True:
    encoder_state = (enc_a.value() << 1) | enc_b.value()
    if encoder_state != last_encoder_state:
        encoder_accum += ENCODER_STEPS.get((last_encoder_state, encoder_state), 0)
        last_encoder_state = encoder_state

        if encoder_accum >= 4:
            selected_channel = min(len(CHANNELS), selected_channel + 1)
            encoder_accum = 0
        elif encoder_accum <= -4:
            selected_channel = max(1, selected_channel - 1)
            encoder_accum = 0

    now_ms = time.ticks_ms()
    if enc_sw.value() == 0 and time.ticks_diff(now_ms, last_button_ms) > BUTTON_DEBOUNCE_MS:
        last_button_ms = now_ms
        if selected_channel != active_channel:
            apply_channel(CHANNELS[selected_channel - 1])
            active_channel = selected_channel

    if selected_channel != last_selected_channel or active_channel != last_active_channel:
        draw_channel_ui()
        last_selected_channel = selected_channel
        last_active_channel = active_channel

    time.sleep(LOOP_DELAY_SEC)
