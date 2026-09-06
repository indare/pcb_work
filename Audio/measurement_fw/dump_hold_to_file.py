"""`capture_hold` が RAM に保持したキャプチャを、Pico のファイルへ書き出す。

## なぜ要るか

`capture_hold.dump()` は base64 を `sys.stdout` へ流す。**USB CDC は 64 バイト単位で
取りこぼす**（2026-09-07 実測。`capture_raw.py` でも毎回 64〜318 文字欠落した）。
USB を抜いて苦労して採ったデータを、読み出しで壊しては意味が無い。

`mpremote cp` は raw REPL の確認応答付きプロトコルなので取りこぼさない。

## 使い方

    # ⚠ 必ず resume を挟むこと。exec/run は既定でソフトリセットし、
    #   HOLD（モジュールのグローバル）を消してから読みに行く
    mpremote connect COMx resume run dump_hold_to_file.py
    mpremote connect COMx cp :cap.txt cap_usbout_1.txt

書式は `capture_raw.py` と同一なので `analyze_thd.py` にそのまま渡せる。
"""

import os

import ubinascii  # type: ignore

import capture_hold

OUT = "/cap.txt"
CHUNK = 3072
NL = bytes([10])


def dump(index=0, out=OUT):
    if index >= len(capture_hold.HOLD):
        print("no capture: held=%d tries=%d"
              % (len(capture_hold.HOLD), capture_hold.INFO.get("tries", 0)))
        return
    buf = capture_hold.HOLD[index]
    rms = (capture_hold.INFO["hold_rms"][index]
           if index < len(capture_hold.INFO["hold_rms"]) else 0.0)
    with open(out, "wb") as f:
        f.write(b"# capture v1" + NL)
        f.write(("# n_frames %d" % capture_hold.N_FRAMES).encode() + NL)
        f.write(b"# fs_nominal 48000" + NL)
        f.write(("# source capture_hold index=%d rms=%.6f" % (index, rms)).encode() + NL)
        mv = memoryview(buf)
        for i in range(0, len(buf), CHUNK):
            f.write(ubinascii.b2a_base64(mv[i:i + CHUNK]))
        f.write(b"# end" + NL)
    print("wrote", out, os.stat(out)[6], "bytes  index=%d rms=%.6f" % (index, rms))


print("held=%d tries=%d rms(last5)=%s"
      % (len(capture_hold.HOLD), capture_hold.INFO.get("tries", 0),
         [round(x, 5) for x in capture_hold.INFO.get("rms", [])[-5:]]))
dump(0)
