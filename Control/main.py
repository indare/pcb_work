from machine import I2C, Pin
import time

from ssd1306 import SSD1306_I2C


WIDTH = 128
HEIGHT = 64
SDA_PIN = 20  # Pico physical pin 26
SCL_PIN = 21  # Pico physical pin 27
PULSE_SEC = 0.1
RESET_TO_SET_SEC = 0.5
CHANNEL_HOLD_SEC = 20.0

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


def reset_channel(channel):
    target_outputs = [
        output for output in relay_outputs if output["channel"] == channel["number"]
    ]
    for output in target_outputs:
        output["state"] = "RESET"
    update_display(
        "Reset CH" + str(channel["number"]),
        channel["audio"]["name"],
        channel["pwr"]["name"],
        "RESET pulse",
        "Next in 0.5 sec",
    )
    pulse(target_outputs, "reset")


def set_channel(channel):
    target_outputs = [
        output for output in relay_outputs if output["channel"] == channel["number"]
    ]
    for output in relay_outputs:
        output["state"] = "SET" if output in target_outputs else "RESET"

    led.on()
    update_display(
        "CH" + str(channel["number"]) + " SET",
        channel["audio"]["name"],
        channel["pwr"]["name"],
        "Others RESET",
        "Hold 20 sec",
    )
    pulse(target_outputs, "set")


led = Pin("LED", Pin.OUT)
led.off()

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
    draw_status(oled, "Relay test", "OLED OK", "Ready", "CH1-5")
else:
    print("No I2C device found on GP20/GP21")

reset_all("Power-on RESET")
time.sleep(RESET_TO_SET_SEC)

current_channel = None
for channel in CHANNELS:
    if current_channel:
        reset_channel(current_channel)
        time.sleep(RESET_TO_SET_SEC)
    set_channel(channel)
    current_channel = channel
    time.sleep(CHANNEL_HOLD_SEC)

update_display("Final state", "CH5 SET", "K10 AUDIO", "K7 PWR", "Others RESET")
