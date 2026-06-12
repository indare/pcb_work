from machine import Pin
import time


ENC_A_PIN = 22
ENC_B_PIN = 26
ENC_SW_PIN = 27

enc_a = Pin(ENC_A_PIN, Pin.IN, Pin.PULL_UP)
enc_b = Pin(ENC_B_PIN, Pin.IN, Pin.PULL_UP)
enc_sw = Pin(ENC_SW_PIN, Pin.IN, Pin.PULL_UP)


def read_state():
    return enc_a.value(), enc_b.value(), enc_sw.value()


last = None
start = time.ticks_ms()
print("encoder debug start: A=GP22 B=GP26 SW=GP27")
print("Turn encoder and press switch for 30 seconds.")

while time.ticks_diff(time.ticks_ms(), start) < 30_000:
    state = read_state()
    if state != last:
        elapsed = time.ticks_diff(time.ticks_ms(), start)
        print(elapsed, "ms", "A", state[0], "B", state[1], "SW", state[2])
        last = state
    time.sleep_ms(10)

print("encoder debug done")
