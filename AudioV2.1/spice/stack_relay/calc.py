#!/usr/bin/env python3
"""DC 降下・LDO ヘッドルーム・TMUX 電源・放電・保持時間・直列 R の損失（算術のみ）。

入力の出典（stack_relay_power.md の凡例と同じ）:
  RS6: クロスレギュレーション ±5.0 % typ（25–100 % load）[pow:L64]、ロード・レギュレーション 1.0 % typ [pow:L63] → Ro 0.75 Ω〔計算、BPS と同じ〕
  TPS7A49: VDO 260 mV typ @100 mA、333/600 mV typ/max @150 mA [pow:L187-188]、ヘッドルーム目安 ≥1 V [pow:L231]
  TPS7A30: |VDO| 216 mV typ @100 mA、325/600 mV @200 mA [pow:L314-315]
  TMUX7612: 推奨 VDD–VSS 4.5–50 V [sw:L39]、Ron 平坦域 VSS+5〜VDD−5 V [sw:L82]、±15 V で正側が底から離れ始める約 +10.6 V（目読み）[sw:L96]
"""
import math

V_NOM = 15.0
V_CROSS_LO = V_NOM * 0.95          # クロスレギュレーションの typ ±5 % を最悪に取る〔仮定〕
RO_STATIC = 0.75                   # RS6 の静的出力抵抗〔仮定、BPS 源 C〕
I_TOTAL_RS6 = 0.150                # 設計点の +15 V 合計（max・HP 歪み始め 148.8〜150.3 mA [dcdc_2stage §1.2]）
HOP_R = 0.05                       # 1 段のコネクタ R（最悪）
HOPS = 4
R_CONTACT = 0.1                    # G6K の max 100 mΩ（AZ850 < 50 mΩ）

# 娘の負荷（片レール）: EN 前 / typ / max
TMUX_IDD = (0.435e-3, 0.48e-3)     # 全 ON typ/max [sw:L62]
N_TMUX = 4
I_LOGIC = 1.0e-3                   # 検知・デコーダ・ゲート〔仮定〕
LOADS = {
    "EN 前（TMUX＋ロジック）": N_TMUX * TMUX_IDD[1] + I_LOGIC,
    "typ（NE5532 typ 6 mA）": 6e-3 + 0.4e-3 + N_TMUX * TMUX_IDD[0] + 0.5e-3,
    "max（在庫の最悪 20 mA）": 20e-3 + 1.0e-3 + N_TMUX * TMUX_IDD[1] + I_LOGIC,
}

VDO = {"TPS7A49 typ@100mA": 0.260, "TPS7A49 max@150mA": 0.600, "TPS7A30 typ@100mA": 0.216, "TPS7A30 max@200mA": 0.600}
V_LDO_OUT = 12.0

print("== DC 降下と LDO ヘッドルーム（最悪の源 14.25 V − RS6 0.75 Ω×150 mA − 4 段 × 0.05 Ω − 接点 0.1 Ω − Rser）==")
v_par = V_CROSS_LO - RO_STATIC * I_TOTAL_RS6
print(f"親ノードの最悪 {v_par:.3f} V（typ 源なら {V_NOM - 0.1*I_TOTAL_RS6:.3f} V）")
for R in [1, 2.2, 4.7, 10, 15, 22, 33, 47]:
    row = [f"R={R:>4} Ω"]
    for name, I in LOADS.items():
        drop = I * (R + HOPS * HOP_R + R_CONTACT)
        vin = v_par - drop
        hr_max = vin - V_LDO_OUT - VDO["TPS7A49 max@150mA"]
        hr_typ = vin - V_LDO_OUT - VDO["TPS7A49 typ@100mA"]
        row.append(f"{name}: 降下 {drop*1e3:.0f} mV → VIN {vin:.2f} V, (VIN−12−VDOmax) {hr_max:.2f} V / typ {hr_typ:.2f} V")
    print("  " + "\n           ".join(row))
    I = LOADS["max（在庫の最悪 20 mA）"]
    print(f"           I²R（max）{I*I*R*1e3:.1f} mW, 両レール {2*I*I*R*1e3:.1f} mW")

print("\n== TMUX の電源（D ノード、±対称と仮定）==")
for R in [4.7, 10, 22, 33]:
    for name, I in LOADS.items():
        vdd = V_NOM - I * (R + HOPS * HOP_R + R_CONTACT)
        print(f"  R={R:>4}: {name}: VDD ≈ {vdd:.2f} V、VDD−VSS ≈ {2*vdd:.1f} V（4.5〜50 V の内）、膝の移動 ≈ {-(V_NOM-vdd):+.2f} V（±15 V の約 +10.6 V から）")

print("\n== 突入の概算（源 15 V、R_total = Rser＋接点＋4 段＋ESR）==")
for R in [1, 2.2, 4.7, 10, 15, 22, 33]:
    Rt = R + R_CONTACT + HOPS * 0.01
    ipk = V_NOM / Rt
    for Cb in [4.62e-6, 22.7e-6, 49.6e-6, 85.3e-6]:
        tau = Rt * Cb
        i2t = ipk ** 2 * tau / 2
        E = 0.5 * Cb * V_NOM ** 2
        print(f"  R={R:>4}: Cb={Cb*1e6:5.1f} µF: Ipk {ipk:5.2f} A, τ {tau*1e3:5.2f} ms, I²t {i2t*1e3:.3f} mA²s(=1e-3 A²s), E_R {E*1e3:.1f} mJ, Ppk {ipk**2*R:.1f} W")

print("\n== リセット時の放電（NC → Rdis、Rser 直列）==")
for Rdis in [470, 1000, 2200, 4700]:
    for Cb in [4.62e-6, 49.6e-6, 85.3e-6, 98.8e-6]:
        for R in [10, 22]:
            tau = (Rdis + R) * Cb
            t1 = tau * math.log(15 / 1.0)
            i0 = 15 / (Rdis + R)
            print(f"  Rdis={Rdis:>5}: Cb={Cb*1e6:5.1f} µF, Rser {R}: 接点の電流 {i0*1e3:.1f} mA、Rdis の初期電力 {i0*i0*Rdis:.3f} W、τ {tau*1e3:.0f} ms、1 V まで {t1*1e3:.0f} ms、E {0.5*Cb*225*1e3:.1f} mJ")

print("\n== NO が開いてから LDO が落ちるまでの保持（娘の C だけ、負荷は max 24 mA、NC の Rdis は無視）==")
for Cb in [4.62e-6, 22.7e-6, 49.6e-6, 85.3e-6]:
    for I in [LOADS["typ（NE5532 typ 6 mA）"], LOADS["max（在庫の最悪 20 mA）"]]:
        for vstart in [14.9, 14.5]:
            t_rg = Cb * (vstart - 13.5) / I
            t_do = Cb * (vstart - (V_LDO_OUT + 0.6)) / I
            print(f"  Cb={Cb*1e6:5.1f} µF, I={I*1e3:4.1f} mA, V0={vstart}: 13.5 V まで {t_rg*1e3:5.2f} ms、12.6 V（LDO が落ち始める）まで {t_do*1e3:5.2f} ms")

print("\n== コイル電流（5 V、同時に通電するコイルの数）==")
coil = {"AZ850P2-5（125 Ω）": 5 / 125, "TQ2-L2-5V PC（40 mA）": 0.040, "TQ2SA-L2-5V SMD（28.1 mA）": 0.0281, "G6KU-2 5V（21.1 mA、単巻線）": 0.0211}
for name, i in coil.items():
    print(f"  {name}: 1 枚 3 個同時 {3*i*1e3:.0f} mA / 4 枚の音声リセット 8 個 {8*i*1e3:.0f} mA / 4 枚の全リセット 12 個 {12*i*1e3:.0f} mA")
