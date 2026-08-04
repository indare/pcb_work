from machine import I2CTarget, Pin
import time

from protocol import (
    CMD_APPLY_MAX,
    CMD_APPLY_MIN,
    CMD_PING,
    CMD_RESET,
    REG_CMD,
    REG_DONE,
    REG_STATUS,
    SCL_PIN,
    SDA_PIN,
    SLAVE_ADDR,
    STATUS_BUSY,
    STATUS_ERR,
    STATUS_IDLE,
    STATUS_OK,
    STATUS_PONG,
)
from relays import RelayBoard


# mem[0]=command, mem[1]=status, mem[2]=completion counter.
mem = bytearray([0x00, STATUS_IDLE, 0x00])
pending_cmd = None


def bump_done():
    mem[REG_DONE] = (mem[REG_DONE] + 1) & 0xFF


def irq_handler(target):
    global pending_cmd
    flags = target.irq().flags()
    if flags & I2CTarget.IRQ_END_WRITE and target.memaddr == REG_CMD:
        pending_cmd = mem[REG_CMD]


def handle_command(cmd):
    mem[REG_STATUS] = STATUS_BUSY
    led.on()

    try:
        if cmd == CMD_PING:
            mem[REG_STATUS] = STATUS_PONG
            return

        if cmd == CMD_RESET:
            board.reset_all("Slave RESET")
            mem[REG_STATUS] = STATUS_OK
            return

        if CMD_APPLY_MIN <= cmd <= CMD_APPLY_MAX:
            board.apply_channel(cmd)
            mem[REG_STATUS] = STATUS_OK
            return

        print("unknown cmd", cmd)
        mem[REG_STATUS] = STATUS_ERR
    except Exception as exc:
        print("command failed:", cmd, exc)
        mem[REG_STATUS] = STATUS_ERR
    finally:
        bump_done()
        led.off()


led = Pin("LED", Pin.OUT)
led.off()

board = RelayBoard(led=None)

# Advertise on the bus before the local boot reset so the parent can find us.
target = I2CTarget(
    0,
    SLAVE_ADDR,
    mem=mem,
    mem_addrsize=8,
    scl=Pin(SCL_PIN),
    sda=Pin(SDA_PIN),
)
target.irq(irq_handler)
mem[REG_STATUS] = STATUS_PONG
print("expansion slave ready at", hex(SLAVE_ADDR))

board.reset_all("Slave boot")
mem[REG_STATUS] = STATUS_PONG

while True:
    cmd = pending_cmd
    if cmd is not None:
        pending_cmd = None
        handle_command(cmd)
    time.sleep_ms(5)
