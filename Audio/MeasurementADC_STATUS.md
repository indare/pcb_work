# MeasurementADC 進捗メモ

最終更新: 2026-07-13（ERC 再実行 01:56）

Amp 調整用の基準計測モジュール（OPA1656 + 共立 ADC1804_F / PCM1804 + Pico2 + WAVESHARE LCD）。

## 目的

- 自作 2ch スペアナ／相対比較用の物差し
- 絶対校正済み計測器ではない（「それなりの精度」で十分という前提）

## 確定した電源アーキテクチャ

```
ADC_V_IN / ADC_GND_IN (PD)
  ├─ BP5293-50 → +5V_D → Pico / LCD（デジ、D_GND）
  └─ MBC2596 (4端子) → ~6.6–6.8V
         ├─ LT1763-5   → +5V_A  （ADC AVDD）
         └─ LT1763-3.3 → +3V3_A （ADC DVDD、+5V_A より先行）
±15V_A → OPA1656
A_GND = 音声側アナログ GND
ADC_GND = 6.6V 以降のアナログ電源戻り（デカップもここ）
A_GND ↔ ADC_GND は星点一点結合
```

補足:

- TPS7A4901（HVSSOP）は LT1763 SOIC-8 に置換（手はんだ・秋月入手性）
- BP5293-33 を ADC 電源に使わない（ノイズ）
- 高精度計測時は LCD OFF 想定（Q1 ロードスイッチ）

---

## ERC スナップショット（`audiocase_erc.txt`）

| 項目 | 前回 (01:20) | 今回 (01:56) |
|---|---|---|
| 合計 | 71 | **69** |
| Errors | 30 | **28** |
| Warnings | 41 | 41 |

シート別（今回）:

- `/`（親）: dangling ラベル・未接続配線端・off-grid など
- `/MeasurementADC/`: エラー中心（電源ピン・未接続パスシブ・pin_to_pin）
- `/PowerModule/`: Power output 同士接続 1 件
- 他シート: 違反なし

### 直近で解消したもの

- [x] **Q1（AO3401A）ピン未接続** — G=`LCD_EN`（R51 経由）、S=`+5V_D`、D=`LCD_VCC` で ERC から消えた
- [x] 以前出ていた `ADC_GND_IN` / `LCD_VCC` / `ADC_GND` / `+5V_A` などの dangling の一部も減少

### 残っている主な Errors（MeasurementADC）

- A2（ADC1804）`+3V3` / `GND` 未接続・未駆動
- `LCDDisplay1` VCC 未駆動（FET D は passive のため power_pin_not_driven は残り得る）
- C64 / C65 / C68 / C69 未接続
- U13（MBC2596）OUT+/OUT- の pin_to_pin（Power output 同士）
- U14 / U16（LT1763）GND・BYP 未接続、OUT 同士の誤接続疑い
- U15 / U17（スーパーバイザ）`~{RESET}` 出力同士接続（ワイヤ AND 要ダイオード等の見直し）

### 残っている主な Warnings

- 親シート: dangling（`+3V3_A`, `+6V7_PRE`, `+5V_D`, `A_GND`, `U13_FB`）
- `multiple_net_names`（`+3V3_A`/`+5V_A`、`+6V7_PRE`/`ADC_GND`、`ADC_GND_IN`/`D_GND`、`ADC_nRST`/`U17_CT`）→ **短絡配線の可能性大**
- LT1763 GND がグランドネット扱いになっていない
- off-grid / 未接続配線端（自動配線の名残）

### Q1（AO3401A）現状と間違い

**合っている点（ネット割り当て）**

| ピン | 名前 | 現状の接続 | 判定 |
|---|---|---|---|
| 1 | G | R51 → `LCD_EN` | 行き先の意図は OK |
| 2 | S | `+5V_D` | OK（ハイサイド電源側） |
| 3 | D | `LCD_VCC` | OK（負荷側） |

ERC 上の Q1 ピン未接続は解消済み。

**間違い・不十分（要修正）**

1. **R51 の使い方が違う**  
   いまは `LCD_EN`—100k—G の**直列**。100k はゲート直列としては大きすぎる。  
   正しくは **G ↔ `+5V_D` のプルアップ（100k）**。必要ならゲート直列は別途数 10〜100Ω 程度。

2. **Pico 3.3V では P-FET を切れきれない**  
   Source=`+5V_D` なのに Gate High=3.3V だと Vgs≈−1.7V のまま → **OFF 不完全**（高精度モードの LCD 切断が成立しない）。  
   対策: G を `+5V_D` プルアップし、`LCD_EN` は **Low で G を落とす（OD／プッシュプル Low のみ有効）**。High は Hi-Z か、ゲートを 5V まで上げない駆動にしない。

3. **シート注記と実回路が矛盾**  
   注記「`LCD_EN` high で切断」は、上記プルアップ構成＋OD 相当なら成立。  
   **現状の直列 100k＋3.3V プッシュプルでは注記どおりに動かない。**

4. **ERC に残る LCD VCC**  
   `LCDDisplay1` の `power_pin_not_driven` は、Q1 の D が passive 扱いのため**残り得る**（結線ミスとは限らない）。電源フラグ／PWR_FLAG 検討は別途。

**望ましい結線（修正目標）**

```
+5V_D ──┬── Q1.S
        └── R51 100k ── Q1.G ── LCD_EN（Pico GP8、Low=ON / Hi-Z or 開放でOFF）
Q1.D ────── LCD_VCC → LCD / タッチ VCC
```

---

## 終わっていること

### 回路図・プロジェクト統合

- [x] レガシー `.sch` を KiCad 10 用 `MeasurementADC1804_Module.kicad_sch` へ移植
- [x] `AudioCase.kicad_sch` に MeasurementADC 階層シート追加
- [x] 親シート階層ピン方針: `ADC_V_IN` / `ADC_GND_IN` / ±15V / AUDIO / `A_GND`
- [x] シートタイトル・電源ツリー注記・ADC ジャンパ方針（マスタ 48k / 256fs、ASFL1 12.288 MHz）

### シンボル・ライブラリ

- [x] `MeasurementADC1804.kicad_sym`（ADC1804_F_MODULE + OPA1656）を `sym-lib-table` 登録
- [x] `MeasurementADC_Extras.kicad_sym`（LT1763-3.3 / LT1763-5 / MBC2596-01 / ASFL1 / WAVESHARE-29318）追加・登録
- [x] MBC2596 を PDF どおり 4 端子（IN+/IN-/OUT+/OUT-）に修正
- [x] 不要な `MCW03_1.kicad_sym` / `.bak` 類の整理
- [x] ASFL1 用 FP を `Library.pretty` に追加（通常 + HandSoldering）

### 回路方針（設計として決定済み）

- [x] 電源ツリー（上記）
- [x] VCOM は ADC の `VCOML` / `VCOMR`（VIN± のマイナスではない）
- [x] C58–C61 デカップ戻りを `ADC_GND` 側にする方針
- [x] Pico ピン割り当て方針（I2S / LCD SPI / タッチ）をシート注記に記載
- [x] ADC nRST は SV ワイヤ AND、≥20 ms 想定
- [x] Q1 LCD ロードSW の基本結線（S=`+5V_D`, D=`LCD_VCC`, G=`LCD_EN`）

---

## 終わっていないこと

### 回路図の仕上げ（最優先）

- [ ] MeasurementADC 電源ブロックの **配線確認・掃除**（上記 ERC Errors／`multiple_net_names`）
- [ ] Q1: R51 を G→`+5V_D` プルアップへ直し、3.3V GPIO で確実に OFF できる駆動にする（上記「Q1 間違い」参照）
- [ ] LT1763 `BYP`: 使わないなら開放（no-connect）、使うなら 10 nF → `ADC_GND`
- [ ] A2（ADC）`+3V3` / `GND` と電源ネットの実接続
- [ ] デカップ C64/C65/C68/C69 の接続
- [ ] SV `~{RESET}` ワイヤ AND の正しい実装
- [ ] 親シート dangling ラベル掃除
- [ ] Pico / LCD / ADC デジタル線のラベル↔ピン実配線確認

### フットプリント・基板

- [ ] `ADC1804_F_MODULE` のフットプリント未設定
- [ ] `MBC2596-01` / `WAVESHARE-29318` の FP 未設定
- [ ] パスシブ多数の FP 未割当
- [ ] PCB 配置・配線
- [ ] DRC

### 検証・試作

- [ ] ERC クリーン（現状 **28 errors / 41 warnings**）
- [ ] フルスケール・レベル確認
- [ ] 電源ノイズ・LCD ON/OFF ノイズフロア比較
- [ ] Pico ファーム（I2S・FFT・表示）
- [ ] ジャンパ実機確認

### ドキュメント／リポジトリ

- [ ] BOM / 接続図の整理（必要なら）
- [ ] 変更の git commit（依頼があれば）

---

## 主要ファイル

| ファイル | 役割 |
|---|---|
| `MeasurementADC1804_Module.kicad_sch` | 計測モジュール回路図 |
| `AudioCase.kicad_sch` | 親（階層シート） |
| `MeasurementADC1804.kicad_sym` | ADC モジュール + OPA1656 |
| `MeasurementADC_Extras.kicad_sym` | LT1763 / MBC2596 / ASFL1 / LCD |
| `Library.pretty/` | カスタム FP |
| `sym-lib-table` / `fp-lib-table` | ライブラリ登録 |
| `audiocase_erc.txt` | 直近 ERC（2026-07-13 01:56） |

参考 PDF: [共立 ADC1804_F](https://www.kyohritsu.com/eclib/DIGIT/KIT/adc1804f.pdf)

---

## 次にやるとよい順

1. `multiple_net_names`（電源短絡疑い）を先に潰す
2. LT1763 GND/BYP・デカップ C・A2 電源ピンを接続
3. Q1: R51 をプルアップ化し、3.3V で OFF 不完全な点を直す（ステータス「Q1 間違い」）
4. SV RST ワイヤ AND を見直し
5. 親 dangling / off-grid 掃除 → ERC 再実行
6. FP 割当 → PCB
