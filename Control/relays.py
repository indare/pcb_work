from machine import Pin
import time

from protocol import LOCAL_CHANNELS


PULSE_SEC = 0.1
AUDIO_BREAK_SEC = 0.1
POWER_SETTLE_SEC = 0.3

# Local board channel map (same GPIO assignment on parent and expansion).
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


class RelayBoard:
    def __init__(self, led=None, on_status=None):
        self.led = led
        self.on_status = on_status
        self.outputs = []
        for channel in CHANNELS:
            for role in ("audio", "pwr"):
                relay = channel[role]
                reset_output = Pin(relay["reset_pin"], Pin.OUT)
                set_output = Pin(relay["set_pin"], Pin.OUT)
                reset_output.off()
                set_output.off()
                self.outputs.append(
                    {
                        "channel": channel["number"],
                        "role": role,
                        "name": relay["name"],
                        "reset": reset_output,
                        "set": set_output,
                        "state": "OFF",
                    }
                )

    def _status(self, title, line1="", line2="", line3="", line4=""):
        if self.on_status:
            self.on_status(title, line1, line2, line3, line4)

    def _pulse(self, outputs, coil_name):
        for output in outputs:
            output[coil_name].on()
        time.sleep(PULSE_SEC)
        for output in outputs:
            output[coil_name].off()

    def _outputs_by_role(self, role):
        return [output for output in self.outputs if output["role"] == role]

    def _outputs_by_channel_and_role(self, channel_number, role):
        return [
            output
            for output in self.outputs
            if output["channel"] == channel_number and output["role"] == role
        ]

    def reset_all(self, title="RESET"):
        if self.led:
            self.led.off()
        for output in self.outputs:
            output["state"] = "RESET"
        self._status(title, "All channels", "AUDIO RESET", "PWR RESET", "Split pulses")
        self._pulse(self._outputs_by_role("audio"), "reset")
        time.sleep(AUDIO_BREAK_SEC)
        self._pulse(self._outputs_by_role("pwr"), "reset")

    def apply_channel(self, channel_number):
        if channel_number < 1 or channel_number > LOCAL_CHANNELS:
            raise ValueError("local channel out of range")

        if self.led:
            self.led.on()
        self._status(
            "Apply CH" + str(channel_number),
            "AUDIO off",
            "PWR switch",
            "PWR settle",
            "AUDIO on",
        )
        self._pulse(self._outputs_by_role("audio"), "reset")
        time.sleep(AUDIO_BREAK_SEC)
        self._pulse(self._outputs_by_role("pwr"), "reset")
        self._pulse(self._outputs_by_channel_and_role(channel_number, "pwr"), "set")
        time.sleep(POWER_SETTLE_SEC)
        self._pulse(self._outputs_by_channel_and_role(channel_number, "audio"), "set")

        for output in self.outputs:
            output["state"] = "SET" if output["channel"] == channel_number else "RESET"
