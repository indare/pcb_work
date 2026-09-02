#!/usr/bin/env python3
"""10ch セレクタで「OFF の9ch から何が漏れてくるか」を周波数ごとに解く。

## なぜ要るか

これまでは ON になったスイッチの THD だけを追っていた。しかし 10ch セレクタでは
**非選択9ch の OFF 経路からの漏れ**が別の律速になりうる。特に TMUX4821 は
OISO が −50dB（@100kHz, RL=50Ω）で、TMUX7612 の −105dB より 55dB 悪い。

`CS(off)` の比（70pF 対 24pF）で見ると3倍程度に見えるが、それはソース対グランド容量。
**ソース→ドレインの貫通は OISO 規格が捉えている**ので、そちらから実効直列容量を逆算する:

    OISO = RL / |RL + 1/(jωC)|  →  C = 1 / (2π f · (RL/OISO))

    TMUX7612  OISO −105dB @100kHz, RL=50Ω  →  C_off ≈ 0.18 pF
    TMUX4821  OISO  −50dB @100kHz, RL=50Ω  →  C_off ≈ 100.6 pF   （562倍）

## モデル

    TONE ─┬─[SW1_on  Ron ]─ A1 ─ Rbias ─ GND      選択ch
          │                    └ Amp1 ─ Riso ─[SW2_on  Ron ]─┐
          │                                                   ├─ BUS ─ RL
          ├─[SW1_off Coff]─ Ak ─ Rbias ─ GND      非選択ch ×9 │
          │                    └ Ampk ─ Riso ─[SW2_off Coff]─┘
          ⋮

OFF は2段（入力側と出力側）通るので、単純に「OISO が −50dB だから駄目」とは言えない。
各周波数でフェーザとして節点方程式を解き、**選択chのみの場合との差**を漏れ量とする。

漏れは信号の同相コピーなので、効果は THD ではなく**周波数特性の誤差**になる。
非選択アンプ自身の歪みも一緒に漏れてくるが、二重減衰を受けるので普通は無視できる。
それも一緒に出す。

使い方:
  python3 AudioV2/spice/switch_offiso.py
  python3 AudioV2/spice/switch_offiso.py --rbias 100e3 --nch 10
"""

from __future__ import annotations

import argparse

import numpy as np

# (OISO dB, 測定周波数 Hz, 測定 RL Ω, Ron Ω, 部品名)
PARTS = {
    "tmux7612": (-105.0, 100e3, 50.0, 1.35, "TMUX7612 (16-TSSOP)"),
    "tmux4821": (-50.0, 100e3, 50.0, 0.25, "TMUX4821 (2ch/pkg)"),
    # 以下2026-09-02追加。OISOはデータシート記載値をそのまま外挿（測定周波数が違う点に注意）。
    # Ronはswitch_thd.py用に抽出したRon(V)カーブのVS≈0点（代表値、フルカーブではない）
    "adg1407": (-73.0, 1e6, 50.0, 7.79, "ADG1407 (dual 8:1, 25C typ)"),
    "dg507b": (-84.0, 1e6, 50.0, 170.0, "DG507B (dual 8:1)"),
    # OISO は MIN 保証値なので、そこから逆算した C_off は実力より悲観側（安全側）になる。
    # MAX14753 は IN-OUT 容量が別途 <1pF と明記されており、実力はもっと良いはず
    "max14753": (-65.0, 100e3, 50.0, 60.0, "MAX14753 (dual 4:1, 72V)"),
    "max14778": (-80.0, 100e3, 50.0, 0.84, "MAX14778 (dual 4:1, +-25V)"),
}
GAIN = 2.0
R_ISO = 47.0          # 出力直列抵抗
DUT_THD_DB = -94.0    # 被試験オペアンプ自身の THD（NE5532 0.002%）


def coff_from_oiso(oiso_db: float, f: float, rl: float) -> float:
    """OISO 規格から OFF 経路の実効直列容量を逆算する。"""
    a = 10 ** (oiso_db / 20)          # 電圧比
    # a = RL / sqrt(RL^2 + X^2) → X = RL * sqrt(1/a^2 - 1)
    x = rl * np.sqrt(1 / a**2 - 1)
    return 1 / (2 * np.pi * f * x)


def solve(part: str, f: float, rbias: float, rload: float, nch: int, rsrc: float):
    oiso_db, f0, rl0, ron, _ = PARTS[part]
    coff = coff_from_oiso(oiso_db, f0, rl0)
    zc = 1 / (1j * 2 * np.pi * f * coff)

    # --- 入力側: TONE から各ch のアンプ入力へ ---
    v_on = rbias / (rbias + rsrc + ron)              # 選択ch
    v_off = rbias / (rbias + rsrc + zc)              # 非選択ch（容量結合）

    # --- 出力側: 各アンプ出力 → BUS ---
    z_on = R_ISO + ron
    z_off = R_ISO + zc
    b_on = GAIN * v_on
    b_off = GAIN * v_off

    def bus(include_off: bool):
        num = b_on / z_on
        den = 1 / z_on + 1 / rload
        if include_off:
            num += nch_off * b_off / z_off
            den += nch_off / z_off
        return num / den

    nch_off = nch - 1
    v_all = bus(True)
    v_sel = bus(False)
    leak = abs(v_all - v_sel) / abs(v_sel)

    # 非選択アンプ自身の歪みが漏れてくる分（各アンプ出力の DUT_THD 分が OFF 経路を通る）
    dut = 10 ** (DUT_THD_DB / 20)
    d_leak = nch_off * abs(b_off) * dut * abs((1 / z_off) / (1 / z_on + nch_off / z_off + 1 / rload))
    d_leak /= abs(v_sel)

    return abs(v_off), leak, d_leak, coff


def solve_broadcast(part: str, f: float, rload: float, nch: int,
                     mismatch: list[tuple[float, float, float | None]] | None = None,
                     coherent: bool = False):
    """入力ブロードキャスト構成（全DUT入力ON、出力だけ1 ON/9 OFF）の BUS 誤差を解く。

    `solve()` の2段OFFモデルとは前提が違う: 非選択chも選択chと**同じ強さの信号**を
    増幅している（入力側に減衰が無い）。漏れは「弱い幽霊信号」ではなく、
    「ほぼ同じ信号を出す9台が Coff 経由で BUS に相乗りして起きる合成誤差」になる。

    mismatch: 非選択9ch 分の (gain_ratio, phase_deg, thd_db) のリスト。
      省略時は「9chとも選択chと完全に同一」（=素子のOFF特性のみが誤差要因）。
    coherent: 非選択ch の歪み成分の足し方。
      False（既定）= 二乗和（RSS、各chの高調波位相がランダムという前提）。
      True = 振幅の単純和（coherent worst case）。全DUTは同一正弦波を受けているので
      同じ次数の高調波が同相で揃う可能性があり、そのとき n ch では RSS の √n 倍
      （9ch なら +9.5dB）になる。**どちらが実態かは石の揃い方次第なので両方見る。**
    戻り値: v_bus_all（全ch込みのBUS電圧）, gain_err（複素数。絶対値=振幅誤差比、
      角度=位相誤差 deg）, dist_leak（非選択9ch自身の歪みが漏れてくる分、dB用の比）
    """
    oiso_db, f0, rl0, ron, _ = PARTS[part]
    coff = coff_from_oiso(oiso_db, f0, rl0)
    zc = 1 / (1j * 2 * np.pi * f * coff)

    z_on = R_ISO + ron
    z_off = R_ISO + zc
    b_on = GAIN + 0j

    nch_off = nch - 1
    if mismatch is None:
        mismatch = [(1.0, 0.0, None)] * nch_off

    num = b_on / z_on
    den = 1 / z_on + 1 / rload
    dist_sq = 0.0      # RSS 用
    dist_lin = 0.0     # coherent 用
    for gain_ratio, phase_deg, thd_db in mismatch:
        b_k = GAIN * gain_ratio * np.exp(1j * np.radians(phase_deg))
        num += b_k / z_off
        den += 1 / z_off
        if thd_db is not None:
            dut = 10 ** (thd_db / 20)
            contrib = abs(b_k) * dut * abs(1 / z_off)
            dist_sq += contrib ** 2
            dist_lin += contrib

    v_bus_all = num / den
    v_bus_sel = (b_on / z_on) / (1 / z_on + 1 / rload)  # 理想: 選択chのみが駆動した場合
    gain_err = v_bus_all / v_bus_sel
    dist_num = dist_lin if coherent else np.sqrt(dist_sq)
    dist_leak = dist_num / abs(1 / z_on + nch_off / z_off + 1 / rload) / abs(v_bus_sel)
    return v_bus_all, gain_err, dist_leak, coff


def db(x: float) -> float:
    return 20 * np.log10(max(abs(x), 1e-30))


def broadcast_report(rload: float = 50e3, nch: int = 10,
                      gain_pct: float = 0.0, phase_deg: float = 0.0,
                      dut_thd_db: float | None = None) -> None:
    """入力ブロードキャスト構成のBUS誤差レポート。gain_pct/phase_degを与えると
    非選択9chすべてに同方向（最悪ケース）でその誤差を持たせた感度分析になる。"""
    nch_off = nch - 1
    mismatch = [(1.0 + gain_pct / 100, phase_deg, dut_thd_db)] * nch_off
    tag = ""
    if gain_pct or phase_deg:
        tag = f"  [感度分析: 非選択9ch に gain{gain_pct:+.1f}% / phase{phase_deg:+.2f}deg を最悪ケースで付与]"
    print(f"=== ブロードキャスト構成（全ch入力ON、出力のみ1 ON/{nch_off} OFF）"
          f" 負荷{rload/1e3:.0f}k{tag} ===\n")
    if dut_thd_db:
        print(f"   漏れ歪みは非選択chの THD を {dut_thd_db:.0f}dB として、"
              f"RSS（位相ランダム）と coherent（{nch_off}ch同相・最悪）の両方を出す\n")
    for part, (oiso, f0, rl0, ron, name) in PARTS.items():
        c = coff_from_oiso(oiso, f0, rl0)
        print(f"■ {name}   OISO {oiso:.0f}dB@{f0/1e3:.0f}kHz → C_off {c*1e12:.2f} pF   Ron {ron}Ω")
        print(f"   {'周波数':>9s}{'振幅誤差':>11s}{'位相誤差':>11s}"
              f"{'漏れ歪みRSS':>13s}{'同 coherent':>13s}")
        for f in (20.0, 1e3, 10e3, 20e3):
            _, gerr, dleak, _ = solve_broadcast(part, f, rload, nch, mismatch)
            _, _, dcoh, _ = solve_broadcast(part, f, rload, nch, mismatch, coherent=True)
            cells = (f"{db(dleak):11.1f}dB{db(dcoh):11.1f}dB"
                     if dut_thd_db else f"{'—':>13s}{'—':>13s}")
            print(f"   {f:8.0f}Hz{db(abs(gerr)):10.4f}dB"
                  f"{np.degrees(np.angle(gerr)):10.3f}deg{cells}")
        print()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rbias", type=float, default=47e3)
    ap.add_argument("--rload", type=float, default=50e3)
    ap.add_argument("--rsrc", type=float, default=1e3, help="TONE 側の出力インピーダンス")
    ap.add_argument("--nch", type=int, default=10)
    ap.add_argument("--broadcast", action="store_true",
                     help="入力ブロードキャスト構成（全ch入力ON、出力のみ切替）で解く")
    ap.add_argument("--gain-pct", type=float, default=0.0,
                     help="[--broadcast] 非選択9chに与える最悪ケースのゲイン誤差(%%)")
    ap.add_argument("--phase-deg", type=float, default=0.0,
                     help="[--broadcast] 非選択9chに与える最悪ケースの位相誤差(deg)")
    ap.add_argument("--dut-thd", type=float, default=None,
                     help="[--broadcast] 非選択chのDUT自身のTHD(dB)。指定時のみ漏れ歪み列を出す")
    a = ap.parse_args()

    if a.broadcast:
        broadcast_report(a.rload, a.nch, a.gain_pct, a.phase_deg, a.dut_thd)
        return

    print(f"Rbias {a.rbias/1e3:.0f}k / 負荷 {a.rload/1e3:.0f}k / 源 {a.rsrc:.0f}Ω / "
          f"{a.nch}ch（1 ON, {a.nch-1} OFF）/ ゲイン {GAIN:g}\n")
    for part, (oiso, f0, rl0, ron, name) in PARTS.items():
        c = coff_from_oiso(oiso, f0, rl0)
        print(f"■ {name}   OISO {oiso:.0f}dB@{f0/1e3:.0f}kHz → C_off {c*1e12:.2f} pF   Ron {ron}Ω")
        print(f"   {'周波数':>9s}{'非選択入力':>12s}{'BUS漏れ計':>12s}{'漏れ歪み':>11s}")
        for f in (20.0, 100.0, 1e3, 10e3, 20e3):
            voff, leak, dleak, _ = solve(part, f, a.rbias, a.rload, a.nch, a.rsrc)
            print(f"   {f:8.0f}Hz{db(voff):10.1f}dB{db(leak):11.1f}dB{db(dleak):10.1f}dB")
        print()
    print(f"判定の目安: BUS漏れ計は信号の同相コピー = 周波数特性の誤差。")
    print(f"  −60dB で 0.009dB、−40dB で 0.09dB、−20dB で 0.9dB の誤差。")
    print(f"  漏れ歪みは被試験石（{DUT_THD_DB:.0f}dB 相当）より十分下にあるべき。")


if __name__ == "__main__":
    main()
