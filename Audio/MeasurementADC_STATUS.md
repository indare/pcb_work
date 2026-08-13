# MeasurementADC 進捗メモ

最終更新: **2026-08-14**（初号ブリングアップ継続中）

Amp 調整用の基準計測モジュール（OPA1656 + 共立 ADC1804_F / PCM1804 + Pico2 + WAVESHARE LCD）。

---

## 残作業

1. **初号実機**
   - `ADC_nRST` は応急構成で H まで確認済み（詳細は `MeasurementADC_BRINGUP.md`）
   - **PCM1804 が BCK/LRCK を出さない** → 予備モジュール載せ替えが次手
   - 出たら Pico から I2S / FFT / LCD
2. **Pico ファームウェア**（クロック確認後）
   - GP8 = `LCD_EN` → High 固定
   - I2S 受信（FMT = 24bit I²S）
   - FFT → おおよそ 10 バンド表示
   - LCD / タッチ UI

ハード設計・分割 Gerber は初号として出済み。実機は上記で停止中。

---

## 発注・分割 Gerber

```bash
cd Audio
python3 scripts/regenerate_split_gerbers.py --only 06_measurement_adc
```

出力:

- `split/AudioCase_6_measurement_adc.kicad_pcb`
- `split/Gerber/06_measurement_adc.zip`

外形 Edge.Cuts: `(339.87, 85.32)–(522.47, 169.02)` mm

---

## 初号で無視するもの

- `PICO_3V3` 未配線（基板他部品未使用）
- A1 Pico `lib_footprint_mismatch`
- 島またぎ未接続（設置時ワイヤ想定）
- Controll と同一ネジピッチ（現状高さ不足・今はやらない）

---

## 確定方針（要約）

- GND 案A（非絶縁）: NT701 `A_GND↔ADC_GND` / NT702 `ADC_GND_IN↔D_GND`
- Pico: VSYS=`+5V_D`、GND=`D_GND`
- LCD: U708 XC8107、ソフト制御（CE↔VIN ハードショートしない）
- VCOM: ADC → 2段目 OPA の＋、デカップは `VCOM↔ADC_GND`
- 電源デジの一括オートルートは再禁止

詳細な設計経緯・レビュー対応は git 履歴と `MeasurementADC_BRINGUP.md` を参照。

---

## 主要ファイル

| ファイル | 役割 |
|---|---|
| `MeasurementADC1804_Module.kicad_sch` | 計測モジュール回路図 |
| `AudioCase.kicad_pcb` | 親 PCB（MeasurementADC 島含む） |
| `MeasurementADC_ORDER.md` | 発注・在庫メモ |
| `MeasurementADC_BRINGUP.md` | 初号機ブリングアップ記録（現状の停止要因と次手順） |
| `scripts/regenerate_split_gerbers.py` | 分割 Gerber（`06_measurement_adc`） |
