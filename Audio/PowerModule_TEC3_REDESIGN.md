# PowerModule リファイン — TEC 3-1223

最終更新: **2026-08-26**

前提:

- Controll リレーで **Amp は常時 1 枚だけ**通電
- Amp 島の電源バッファは **SMD 100µF / 35V 級（高分子）**
- MCW03-12D15 の **Cout 上限 47µF/出力** では Amp 100µF を仕様内に載せられない
- 置き換え候補: **Traco TEC 3-1223**（±15V / ±100mA / Cout **440µF/出力**）

回路図: `PowerModule.kicad_sch`（本メモの値に合わせて更新済み）  
詳細計算の一次ソース: [TEC 3 datasheet](https://www.tracopower.com/sites/default/files/products/datasheets/tec3_datasheet.pdf) / [EMI AN](https://www.tracopower.com/sites/default/files/products/application_notes/tec3_emc_consideration.pdf)

---

## 1. なぜ TEC 3-1223 か

| 項目 | MCW03-12D15 | TEC 3-1223 |
|---|---|---|
| 入出力 | 12V → ±15V ±100mA | **9–18V → ±15V ±100mA** |
| Cout 上限 | **47µF/rail** | **440µF/rail** |
| リップル | （公称弱） | **55 mVp-p max**（20 MHz） |
| 無負荷 | — | **Minimum load 不要** |
| パッケージ | SIP-8 系 | **SIP-8**（pin 1/2/3/5/6/7/8） |
| Remote | あり | pin3（open = ON） |

電流は両方 ±100mA。**1ch Amp + 計測常時**なら同クラスで足りる想定。  
主目的は **Amp SMD 100µF を Cout 仕様内に入れること**。

ピン（dual）:

```text
1 –Vin / 2 +Vin / 3 Remote / 5 NC / 6 +Vout / 7 Common / 8 –Vout
```

旧シンボルも同並びだったが、**実機 MCW03 とピンが逆の系統がある**ので、PCB 差し替え前に DS 突合せ必須。

---

## 2. Cout バジェット（計算）

Amp 1 枚 ON 時の **1 レール**概算:

| 位置 | 容量 | 備考 |
|---|---|---|
| PowerModule 二次（L 後） | **22µF**（C2/C3） | 本改修 |
| HF セラミック | 0.1µF（C4/C5） | 無視してよい |
| MeasurementADC 常時 | **≈47µF** | J703 側（現行） |
| Amp（リレー後） | **100µF SMD** | 方針 |
| **合計** | **≈169µF** | |

- TEC 上限 **440µF** → 余裕 **≈270µF**
- MCW 上限 **47µF** → **約 122µF オーバー**（仕様外）

起動時はリレー OFF なので Amp 100µF は未接続。  
それでも常時分だけで MCW は厳しい。TEC なら常時＋Amp とも余裕。

---

## 3. 二次 LC（L1/L2 + C2/C3）

TEC: スイッチング **≥100 kHz（PFM）**。

選定:

- **L1 = L2 = 10µH**（Isat ≥ 0.3 A、DCR 小さめ）
- **C2 = C3 = 22µF / 35V**（高分子 or OS-CON 相当）

共振:

\[
f_c = \frac{1}{2\pi\sqrt{LC}}
= \frac{1}{2\pi\sqrt{10\times10^{-6}\cdot 22\times10^{-6}}}
\approx 10.7\,\mathrm{kHz}
\]

理想 2 次 LC の減衰（ラフ）:

\[
A(f) \approx 40\log_{10}\!\left(\frac{f}{f_c}\right)
\quad\Rightarrow\quad
A(100\,\mathrm{kHz}) \approx 39\,\mathrm{dB}
\]

狙い:

- モジュールの 100 kHz 級リップルを落とす
- Amp の 100µF を **L の向こう**に置き、切替突入を抑える
- fc を可聴帯に深く入れすぎない（10 kHz 前後）

L を 4.7µH に落とすと \(f_c\approx 15.6\,\mathrm{kHz}\)。PCB で定数実験可。

---

## 4. 一次 EMI（Traco Class A / 12Vin）

公式案（TEC 3-12xx Class A）:

| 記号 | 値 | 役割 |
|---|---|---|
| Cin MLCC | **10µF / 25V** | 入力 |
| C mid | **4.7µF / 25V** | モジュール直近 |
| L_EMI | **4.7µH / 1.15A**（TCK-154 相当） | +Vin 直列 |
| Cy | **150pF / 2kV** | 一次–二次（CM） |

Class B は C を厚くする（同 AN）。  
回路図上の **C1=47µF** はヒューズ後のバルクとして残置。  
**L_EMI + MLCC は PCB レイアウト時に U1 の Vin 直近へ追加**（シート注記済み）。

推奨ヒューズ: **0.8 A slow-blow**（F1 を 800mA に変更済み）。

---

## 5. 目標トポロジ

```text
J4 12V
  → F1 800mA SB
  → C1 47µF bulk
  → [L_EMI 4.7µH] → [10µF + 4.7µF MLCC]   … PCB で追加
  → U1 TEC 3-1223
  → L1/L2 10µH
  → C2/C3 22µF + C4/C5 0.1µF
  → J5 ±15 / A_GND
       ├─ MeasurementADC（常時）
       └─ Controll → リレー → Amp（SMD 100µF）
```

---

## 6. 変更済み（回路図）

| Ref | 旧 | 新 |
|---|---|---|
| U1 | MCW03-12D15 | **TEC 3-1223**（`Library:TEC3-1223_SIP8_THT`） |
| L1/L2 | 値なし / 大 FP | **10µH** / L_1210 |
| C2/C3 | 4.7µF THT | **22µF**（35V 想定） |
| F1 | 1A | **800mA** |
| C1 | 47µF | 47µF（入力バルク、EMI 追記） |

追加ファイル:

- `TEC3.kicad_sym`
- `Library.pretty/TEC3-1223_SIP8_THT.kicad_mod`

---

## 7. まだやっていない（次）

1. **入力 EMI 部品を回路図ネットに正式配線**（L_EMI / MLCC / Cy）
2. `split/AudioCase_3_power` PCB を TEC FP + EMI 配置に追従
3. AmpModule の入口バルクを **SMD 100µF/35V** に揃える（現状 120µF OS-CON THT でも Cout 的には TEC で可）
4. 実機: TEC 単体の ±15 リップルを ZT-703S で A1 再測

---

## 8. リスク短評

| リスク | 見方 |
|---|---|
| 電流 ±100mA | 1ch 前提なら維持。複数 Amp 同時は不可のまま |
| PFM ≥100kHz | リップル形状が変わる。L/C で整える |
| クロスレギュ 5% | ±非対称負荷に注意。1ch Amp なら軽め |
| ピン互換 | SIP-8 同ピッチだが **必ず DS 突合せ** |
'''