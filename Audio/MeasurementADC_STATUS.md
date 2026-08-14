# MeasurementADC 進捗メモ

最終更新: **2026-08-15**

Amp 調整用の基準計測モジュール（OPA1656 + 共立 ADC1804_F / PCM1804 + Pico2 + WAVESHARE-29318）。

ブリングアップの詳細ログは `MeasurementADC_BRINGUP.md`。ファームは `measurement_fw/`。

---

## いまの実機状態

| 項目 | 状態 |
|---|---|
| PCM1804 | 稼働（SCKI 12.288 MHz / LRCK 48 kHz / BCK 3.072 MHz） |
| アナログ FE | J703 ±15V 通電済み。開放時の 1196 Hz 過負荷は解消 |
| 残差 | 約 1175 Hz 系の弱い混入（実用上は許容） |
| LCD | ST7796S、MADCTL `0xE8`、480×320。バックライトは GP8=`LCD_EN` |
| タッチ | FT6336U（I2C1 GP10/11）。下端メニューでレンジ／L+R／色／ピーク |
| スペアナ FW | 10 バンド（低域 IIR）＋棒表示。DMA と FFT を重ねて約 18–20 fps |
| 接続 | **Amp → スペアナ**。Controll 2 段は外している。EQ は今号では使わない |

### 初号の応急配線（残置・次号で解消）

| 箇所 | 内容 |
|---|---|
| U710 1番 | リフト（RESET 出力 L 固定のため） |
| Y701 ASFL | 初号 FP 誤りのため空中配線（発振確認済み） |
| LCD SCK/MOSI | ヘッダ GP3/4 ではなく **GP18/GP19（SPI0）へ飛ばし** |
| GP9 → CN3F-1 | SCKI センス専用。**駆動禁止** |
| GP15 → `ADC_nRST` | オープンドレイン制御（H は駆動しない） |

---

## 次の作業（優先順）

1. **MeasurementADC 次号基板**（ジャンパ解消）
   - ASFL FP の GND/VDD
   - LCD SCK/MOSI をハード SPI 正規ピンへ
   - U710 リセット周りを応急なしで動く回路に
   - JP1F／Pico 向きなどの注記・その他洗い出し
   - 分割 Gerber `06_measurement_adc` 再生成
2. **親シート**にボリューム＋手前端子台（L/R/`A_GND`）とタップ注記
3. **箱内配線方針の図面化**（下記）とケース編成

---

## AudioCase 箱内配線方針（合意）

```text
PD(+15/PD_GND) ──直──► Power / Controll×2 / 計測デジ入口のみ

Power MCW03 二次
  ├─ A_GND ──分配器並列──► Amp×10 / 計測 A_GND / 端子台 0V
  └─ ±15  ──分配器──────► Controll AMP_PWR_IN / 計測 ±15V_A
                              └─(リレー)──► 選択中の Amp だけ

入力 L/R ──分配──►【ボリューム手前端子台】──► ボリューム ──► Controll ──► Amp
                      ├─ スペアナ（ハイZ）
                      └─ HP バッファ（ハイZ・将来）
```

- Controll 2 段＋Amp 10 枚（2 段×5、5 cm 樹脂スペーサ）を想定
- Controll／Amp の中身は回路図に複製しない。ボリュームと端子台は親シートへ追加する
- EQ は一旦諦め方向
- 専用ヘッドフォンアンプ基板は未製（ゲイン 1 倍バッファで足りる、という整理）

---

## 発注・分割 Gerber

```bash
cd Audio
python3 scripts/regenerate_split_gerbers.py --only 06_measurement_adc
```

- `split/AudioCase_6_measurement_adc.kicad_pcb`
- `split/Gerber/06_measurement_adc.zip`
- 外形 Edge.Cuts: `(339.87, 85.32)–(522.47, 169.02)` mm（約 183×84 mm）

---

## 確定方針（要約）

- GND 案A（非絶縁）: 板上で `A_GND↔ADC_GND` / `ADC_GND_IN↔D_GND`
- Pico: VSYS=`+5V_D`、GND=`D_GND`
- LCD: U708 XC8107、`LCD_EN`=GP8（Active High）
- VCOM: ADC → 2 段目 OPA の＋、デカップは `VCOM↔ADC_GND`
- 電源デジの一括オートルートは再禁止

---

## 主要ファイル

| ファイル | 役割 |
|---|---|
| `MeasurementADC1804_Module.kicad_sch` | 計測モジュール回路図 |
| `AudioCase.kicad_pcb` / `.kicad_sch` | 親 PCB・階層シート |
| `MeasurementADC_ORDER.md` | 発注・在庫メモ |
| `MeasurementADC_BRINGUP.md` | 初号ブリングアップ記録（履歴） |
| `measurement_fw/` | Pico2 MicroPython（I2S / FFT / LCD スペアナ） |
| `scripts/regenerate_split_gerbers.py` | 分割 Gerber |
| `../Control/` | Controll 用ファーム（親／子） |
