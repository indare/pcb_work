# PowerModule リファイン — TEC 3-1223 → TMR 6-1223

最終更新: **2026-08-28**

前提:

- Controll リレーで **Amp は常時 1 枚だけ**通電、というのが元の箱計画
- **実機は Controll を外している**（`MeasurementADC_STATUS.md`）。±15 が Amp に直結だと枚数分が同時通電になる
- Amp 島の電源バッファは **SMD 100µF / 35V 級（高分子）**
- MCW03-12D15 の **Cout 上限 47µF/出力** では Amp 100µF を仕様内に載せられない
- Cout のために入れた **TEC 3-1223（±100mA）は電流が足りない**。U1 は同じ SIP-8 Dual の **TMR 6-1223（±200mA）** にする

回路図: `PowerModule.kicad_sch`（本メモの値に合わせて更新済み）  
一次ソース: [TMR 6 datasheet](https://www.tracopower.com/sites/default/files/products/datasheets/tmr6_datasheet.pdf)（ローカル `datasheets/TMR6_Datasheet.pdf`） / [TEC 3 datasheet](https://www.tracopower.com/sites/default/files/products/datasheets/tec3_datasheet.pdf) / [EMI AN](https://www.tracopower.com/sites/default/files/products/application_notes/tec3_emc_consideration.pdf)

---

## 1. なぜ TEC 3 では電流が足りず、TMR 6 にするか

最初の置き換え目的は Cout（MCW 47µF → TEC 440µF）だった。電流は MCW も TEC 3 も **±100mA のまま**。

| 項目 | MCW03-12D15 | TEC 3-1223 | **TMR 6-1223（採用）** |
|---|---|---|---|
| 入出力 | 12V → ±15V ±100mA | 9–18V → ±15V **±100mA** | 9–18V → ±15V **±200mA** |
| Cout 上限 | **47µF/rail** | 440µF/rail | **660µF/rail** |
| リップル | （公称弱） | 55 mVp-p max | 50 mVp-p max |
| 推奨ヒューズ（12Vin） | — | **0.8 A SB** | **1.6 A SB** |
| 無負荷 | — | Minimum load 不要 | 不要（12Vin 無負荷入力 **55 mA typ**） |
| 外形 | SIP-8 | 21.8×9.1×11.2 SIP-8 | **同じ** |
| Dual ピン | 1=−Vin … 8=−Vout | 同じ | **同じ**（FP `TEC3-1223_SIP8_THT` 流用） |

TEC 3 は **Cout だけ**見れば正解。電流は下記で危険側。

### 1.1 ±15 の電流バジェット（typ、1 レールあたり ≈ パッケージ Icc）

オペアンプの Icc は +Vs から引き −Vs へ戻るので、**両レールともほぼ同じ mA** を見る。信号電流（2 Vrms / 1.4 kΩ ≈ 1.4 mA）は Icc より小さい。

| 負荷 | 石 | Iq typ | 備考 |
|---|---|---|---|
| MeasurementADC 常時 | OPA1656 ×3 | **≈23 mA** | 3.9 mA/ch × 6 |
| AdcBuffer | NE5532 ×1 | **8 mA** | Amp 側レール（現状） |
| Amp ×1 | NE5532 | **8 mA** | |
| Amp ×2 | NE5532 | 16 mA | Controll なしの今号 |
| Amp ×10 | NE5532 | 80 mA | 箱の最終枚数。リレー無しだと全部乗る |
| HP バッファ（予定） | NE5532 級 | ≈8 mA | 未製 |

| シナリオ | 合計 typ | TEC 3 ±100 mA | TMR 6 ±200 mA |
|---|---|---|---|
| 計測のみ | 23 mA | 余裕 | 余裕 |
| **計画どおり 1ch + 計測 + Buffer** | **39 mA** | 39%。アナログならギリギリ許容 | 余裕 |
| **Controll 外・Amp×2 + 計測 + Buffer** | **47 mA** | 半分近く。差し替えですぐ逼迫 | 余裕 |
| Controll 外・Amp×10 + 計測 + Buffer | **111 mA** | **超過** | 56% |
| Amp 1 枚が AK05/LC5 の 150 mA 説 | ≥150 mA + 計測 | **超過** | **超過** |
| Amp 2 枚が AD797×2（≈16 mA/枚） | ≈63 mA +… | きつい | 余裕 |

アナログ電源は定格の半分を常用上限にしたい。**TEC 3 単体は「1ch・5532・Controll あり」専用**で、今号の使い方（Controll なし、Amp 複数、DIP 差し替え、将来 10 枚）には足りない。

TMR 6 でも **Amp×10 同時 + 大電流 DIP** は厳しい。10 枚同時は Controll で 1 枚だけ通電するか、Amp 専用にもう 1 台（計測は TEC 3 のまま分ける）が次の手。

### 1.2 TMR 6 の上（9 W / 12 W）— 電流は増えるが Cout が減る

同じ Traco TMR 系で ±15 / 12Vin Dual の一段上:

| | TMR 6-1223（採用） | TMR 9-1223 | TMR 12-1223WI |
|---|---|---|---|
| 電力 | 6 W | 9 W | 12 W（4:1 入力） |
| ±15 電流 | **±200 mA** | **±300 mA** | **±400 mA** |
| Cout 上限（±15 Dual） | **660 µF/rail** | **200 µF/rail** | **300 µF/rail** |
| 推奨ヒューズ 12Vin | 1.6 A SB | 3.15 A SB | 5 A SB |
| 外形 | 21.8×9.1×11.2 樹脂 SIP-8 | 21.8×**9.6**×11.2 **金属** SIP-8 | 22.0×9.6×**12.0** 金属 |
| ピン | 1/2/3/5/6/7/8（pin4 欠） | 1/2/3/6/7/8 + **ケース 9–12**（pin5 なし） | 同様にケースピンあり |
| 本 FP に直挿し | **可** | **不可**（ケースピン・幅・pin5） | **不可** |

この基板の Cout 概算は 1 Amp ON で **≈170 µF**。TMR 9 の 200 µF は余裕 30 µF しかなく、Amp を 2 枚同時や島バルクを厚くすると **即仕様外**。TMR 12WI の 300 µF も Amp×2（100+100+計測47+局所22 ≈ 270 µF）でほぼ上限。

**電流だけ見て TMR 9 / 12 に上げると、Cout のために TEC 3 へ替えた意味が消える。**  
6 W より上が必要なら、同じ穴に無理に載せ替えず **Amp 用ともう 1 台**（計測は TEC 3 や TMR 6 のまま）が筋。DIP-24 の TEN 8-1223（±267 mA）は Cout が **100 µF/rail** でさらに向かない。

### 1.3 基板を作り直してよい場合（SIP-8 互換を捨てる）

TMR 6 の次を SIP 穴に無理に載せると Cout が減る（§1.2）。**PowerModule の再設計が可**なら、電流と Cout を同時に取れるのは Mean Well 1″×1″ の DKMW か、2″×1″ の REC15 / DKA15。

| 候補 | ±15 | Cout | 外形 | メモ |
|---|---|---|---|---|
| **Mean Well DKMW20F-15** | **±660 mA** | **650 µF**（各レール） | **1″×1″** | 9–36Vin。小ささと Cout の両立が一番良い |
| **Mean Well DKMW30F-15** | **±1000 mA** | **1000 µF** | 1″×1″ | 余裕最大。入力電流も大きい |
| **Recom REC15-1215D/H2/M** | ±500 mA | **±1000 µF** | 2″×1″ / DIP-24 相当 | Cout は厚い。突入 150% 可 |
| Mean Well **DKA15A-15** | ±500 mA | 680 µF | 50.8×25.4×10.2 | **A = 9–18Vin**（B は 18–36V なので 12V 系では使わない）。内蔵 EMI Class A |
| XP JCA1012D03 | ±330 mA | 470 µF | 1″×0.8″ | 電流は Amp×10 には足りるが差し替え余裕は薄い |
| Traco THN 20-1223 | ±667 mA | 350 µF | 1″×1″ | Cout 不足（400 µF 基準）。1 Amp 構成（≈170 µF）なら可 |
| Traco THN 15-1223N | ±500 mA | 250 µF | 1″×1″ | THN 15 無印は NRND |
| Traco TEN 15-1223 | ±500 mA | **165 µF** | 2″×1″ | 今の 170 µF 概算で **仕様外** |

Amp×10 を 5532 のまま同時通電しても ≈111 mA。DKMW20 なら定格の 17%。AK05 150 mA 説でも 1 枚なら入る。

ピンは SIP-8 と違う。二次 LC・F1（DKMW20 は 12Vin フルで約 1 A 入力 → **2 A SB 前後**、DKMW30 はそれ以上）・FP を取り直す。

**再設計するなら DKMW20F-15（小さい）か REC15 / DKA15A-15（2″×1″）。** THN 20 は Cout が薄いので次点。

SIP-8 のまま 6 W にするなら TMR 6 以外に **RS6-1215D / AM6G-1215DZ / PDL06-12D15**（Cout ±660 µF）。国内は秋月に 6 W SIP は無く、**Cosel MGW61215**（ピンは同じ、Remote は L=ON）が近い。千石・共立の CCG6-12-15DF は DIP でピン非互換。**Mean Well DPB09A-15** は SIP-8 で ±300 mA だが Cout **47 µF** なのでこの島バルクでは使わない。

---

### ピン配置（2026-08-26 DS 突合せ済み）

出典: `datasheets/TEC3_Datasheet.pdf`（Traco TEC 3 Series Rev. 2026-07-02）Pinout Dual 列。  
秋月 MCW03 DS も **同じ SIP-8 並び**（1=–Vin … 8=–Vout）。

| Pin | TEC Dual（DS） | 本シンボル | PowerModule 配線 |
|---|---|---|---|
| 1 | –Vin (GND) | –Vin | PD_GND / Vin− |
| 2 | +Vin (Vcc) | +Vin | F1/C1 側 +Vin |
| 3 | Remote On/Off | Remote | **N.C.（open = ON）** ※DS: passive on |
| 5 | NC | NC | N.C. |
| 6 | +Vout | +Vout | L1 → +15 |
| 7 | Common | Common | A_GND |
| 8 | –Vout | –Vout | L2 → −15 |

回路図 Datasheet プロパティ:

- URL: `https://www.tracopower.com/sites/default/files/products/datasheets/tec3_datasheet.pdf`
- ローカル: `Audio/datasheets/TEC3_Datasheet.pdf`
- EMI AN: `Audio/datasheets/TEC3_EMC_Consideration.pdf`

### フットプリント寸法（DS Outline vs `TEC3-1223_SIP8_THT`）

| 項目 | データシート | 本 FP（修正後） | 旧 MCW03 FP |
|---|---|---|---|
| パッド Y（pin1=0） | 0 / 2.54 / 5.08 / **(skip)** / 10.16 / 12.7 / 15.24 / 17.78 | **一致** | **一致**（ピッチ互換） |
| 本体 L×W×H | 21.8 × 9.1 × 11.2 | Silk/Fab 21.8×9.1 | 21.8×9.3（MCW） |
| pin1〜端 | **2.0** | Silk Y **-2.0 … 19.8** | -2.01 … 19.79 |
| ピン断面 | **0.5 × 0.25** | drill **0.8** / pad 1.7 | drill 0.85 / pad 1.85 |
| ピン〜長辺 | **3.5**（片側） | 本体 X **-5.6 … +3.5**（pin 寄り +X） | -6.6 … +2.7 |
| 基板下ピン長 | 4.1 | （3D 未） | — |
| 配線注意 | **本体下にトレース禁止** | CrtYd + Cmts 注記 | — |

**結論:** パッド中心列は MCW03 と同一ピッチで差し替え可能。初期 TEC FP は本体をピン列中心に置いていたので、**長辺オフセット 3.5mm と Y はみ出し 2.0mm に合わせて修正済み**。

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

- TMR 6 上限 **660µF** → 余裕 **≈490µF**（TEC 3 なら 440µF で余裕 ≈270µF）
- MCW 上限 **47µF** → **約 122µF オーバー**（仕様外）

起動時はリレー OFF なので Amp 100µF は未接続。  
それでも常時分だけで MCW は厳しい。TEC なら常時＋Amp とも余裕。

---

## 3. 二次 LC（L1/L2 + C2/C3）

TMR 6 / TEC 3 ともスイッチング **≥100 kHz（PFM）**。二次 LC はそのまま。

選定:

- **L1 = L2 = 10µH シールド**
  - 指定: **秋月 114977 / Murata DFE322512F-100M**
  - メタルコンポジット、ΔT **1.1 A** / ΔL 1.7 A、DCR **324 mΩ max**
  - FP: `Library:L_Murata_DFE322512F`（本体 3.2×2.5×1.2、推奨ランド pad 1.05×2.70 / ギャップ 1.10）
  - DCR は 0.1 A で約 32 mV。二次 LC の Q を抑える方向で、115628（127 mΩ）よりこちらを採用
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

推奨ヒューズ: TMR 6-12xx は **1.6 A slow-blow**（F1 を 1.6A に変更済み）。TEC 3 だけ載せる場合は DS どおり 0.8 A。

---

## 5. 目標トポロジ

```text
J4 12V
  → F1 1.6A SB
  → C1 47µF bulk（TMR 6 の surge 試験は 220µF KY。PCB で増やす候補）
  → [L_EMI 4.7µH] → [10µF + 4.7µF MLCC]   … PCB で追加
  → U1 TMR 6-1223（SIP-8 Dual、TEC 3 とピン互換）
  → L1/L2 10µH（DFE322512F-100M / 秋月 114977）
  → C2/C3 22µF + C4/C5 0.1µF
  → J5 ±15 / A_GND
       ├─ MeasurementADC（常時）
       └─ Controll → リレー → Amp（SMD 100µF）
```

---

## 6. 変更済み（回路図）

| Ref | 旧 | 新 |
|---|---|---|
| U1 | MCW03-12D15 → TEC 3-1223 | **TMR 6-1223**（同じ `Library:TEC3-1223_SIP8_THT`） |
| L1/L2 | 値なし / 大 FP | **10µH DFE322512F-100M**（秋月 114977）/ `Library:L_Murata_DFE322512F` |
| C2/C3 | 4.7µF THT | **22µF**（35V 想定） |
| F1 | 1A → 800mA（TEC 3） | **1.6A SB**（TMR 6-12xx） |
| C1 | 47µF | 47µF（入力バルク、EMI 追記） |

追加ファイル:

- `TEC3.kicad_sym`（表示値は TMR 6-1223。lib_id / FP 名は TEC3 のままピン互換）
- `datasheets/TMR6_Datasheet.pdf`
- `Library.pretty/TEC3-1223_SIP8_THT.kicad_mod`
- `Library.pretty/L_Murata_DFE322512F.kicad_mod`

---

## 7. まだやっていない（次）

1. **入力 EMI 部品を回路図ネットに正式配線**（L_EMI / MLCC / Cy）
2. `split/AudioCase_3_power` PCB を TEC FP + EMI 配置に追従
3. AmpModule の入口バルクを **SMD 100µF/35V** に揃える（現状 120µF OS-CON THT でも Cout 的には TEC で可）
4. 実機: TMR 6 単体の ±15 リップルを ZT-703S で A1 再測
5. 基板再設計可なら **DKMW20F-15**（1″×1″）または **REC15 / DKA15A-15**（2″×1″）。SIP の TMR 9/12 は Cout が減るので使わない（§1.2）
6. **計測 / Amp の 2 台分け・Single×2・ポストレギュ**の具体 MPN・Cout・面積: [`PowerModule_TWO_MODULE_SPLITS.md`](PowerModule_TWO_MODULE_SPLITS.md)

---

## 8. リスク短評

| リスク | 見方 |
|---|---|
| 電流 | TEC 3 ±100mA は 1ch・5532 専用。TMR 6 ±200mA なら Amp×10 同時（5532）まで。AK05 150mA 説はどちらでも不可 |
| Amp×10 | Controll なしでは TMR 6 でも差し替え次第で逼迫。リレー復帰が本命 |
| PFM ≥100kHz | リップル形状が変わる。L/C で整える |
| クロスレギュ 5% | ±非対称負荷に注意。1ch Amp なら軽め |
| ピン互換 | **DS Dual と一致を確認済み**（上表）。FP ピッチ 2.54 / skip4 も DS 寸法どおり |
