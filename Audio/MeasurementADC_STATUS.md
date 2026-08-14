# MeasurementADC 進捗メモ

最終更新: **2026-08-14**（**I2S 受信まで開通。24bit サンプルを DMA で連続取得**）

Amp 調整用の基準計測モジュール（OPA1656 + 共立 ADC1804_F / PCM1804 + Pico2 + WAVESHARE LCD）。

---

## 残作業

1. **初号実機**（応急構成で動作中・詳細は `MeasurementADC_BRINGUP.md`）
   - `ADC_nRST` は U710 の 1番リフトで解決済み
   - **PCM1804 稼働**: SCKI 12.288MHz / LRCK 48.000kHz / BCK 3.072MHz / DATA 出力
   - SCKI は **Y701**（初号 FP 誤りのため空中配線だが発振確認済み）
   - RST は **Pico GP15** から制御
   - `GP9 → CN3F-1` は測定用に残置。**駆動すると Y701 と衝突するので入力専用**
2. **Pico ファームウェア**（`measurement_fw/`）
   - I2S スレーブ受信は **PIO + DMA で実装済み**。24bit 符号付きサンプルを取りこぼしなく取得
   - **FFT と 10 バンド集計も実装済み**。Q15 固定小数点を viper で回して n=2048 が 22ms
   - GP8 = `LCD_EN` → High 固定
   - LCD / タッチ UI
3. **アナログ入力側**（OPA 電源・VCOM）の立ち上げ ← **次はここ**
   - 入力が浮いているため、両ch とも約 1196Hz の倍音列が −15dBFS で出ている
   - 3 値のカクカクした非正弦波で 16 倍音まで揃う。変調器が入力開放でまともに動いていない
   - 通電して VCOM 基準の信号を入れれば消えるはず。消えなければ別の原因

ハード設計・分割 Gerber は初号として出済み。

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
| `measurement_fw/` | 計測 Pico2 の MicroPython（PIO I2S 受信・確認スクリプト） |
| `scripts/regenerate_split_gerbers.py` | 分割 Gerber（`06_measurement_adc`） |
