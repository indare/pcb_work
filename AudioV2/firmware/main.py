"""AudioV2 起動入口。

聴きモード: ENC で操作、LCD に状態。Amp は board.AMP_BACKEND。
計測モード（スペアナ／capture）は後続。
"""

import board
import encoders
import tone
import amp_select
import ui_status


def main():
    i2c = encoders.open_bus()
    print("I2C scan", [hex(a) for a in i2c.scan()])

    ui_mcp = encoders.UiMcp(i2c)
    tn = tone.Tone(i2c)
    amps = amp_select.AmpSelect(i2c)
    status = ui_status.StatusUi()

    dest = "PHONE"  # DEST は機械 SW。センスは廃止済み — 表示は仮／将来 GPIO で
    status.show(
        ch=amps.channel, dest=dest,
        bass=tn.bass, treble=tn.treble,
        backend=amps.backend,
    )
    amps.apply(amps.channel)

    # 骨格: INT が落ちたら GPIO を読んで差分処理（クアドラチャ実装は次）
    while True:
        if ui_mcp.irq_pending():
            a, b = ui_mcp.raw()
            print("mcp", hex(a), hex(b))
            # TODO: ENC デコード → amps.nudge / tn.nudge_* → status.show
            status.show(
                ch=amps.channel, dest=dest,
                bass=tn.bass, treble=tn.treble,
                backend=amps.backend,
            )


if __name__ == "__main__":
    main()
