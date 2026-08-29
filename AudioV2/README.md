# AudioV2（作業中）

`Audio/`（AudioCase）を参考に、操作系を Pico 2 前提で再構成する作業用ディレクトリ。

- **計測 / スペアナ**（`MeasurementADC` + 計測 Pico 2）は現行どおり独立のまま想定
- **ラッチングリレーで多系統 Amp のうち 1 つだけ有効**する構成は残す
- **操作 Pico は 1 台**＋リレー盤は **I²C GPIO 拡張**（子 MCU なし）
- 回路図の本起こしは、残りの判断（音量位置など）が固まってから

詳細な選択肢とメリデメは [DECISIONS.md](DECISIONS.md)。

## いまの `Audio/` からの参照元

| 流用したいもの | 参照 |
|---|---|
| リレー＋端子台＋ULN＋PD 5V | `Audio/Controll.kicad_sch` |
| 親 UI ファーム（ENC / OLED / リレー） | `Control/` |
| Amp / HP バッファ / 電源 | `AmpModule` / `HeadphoneBuffer` / `PowerModule` |
| GND 分離の型 | `MeasurementADC` の NetTie（`A_GND`↔`ADC_GND`↔`D_GND`） |
| 現行音量位置 | 親シートの `RV101` / `RV102` |

## このディレクトリの置き方

回路図（`.kicad_sch` / `.kicad_pro`）は未作成。判断が決まったらここに新規プロジェクトとして起こす（`Audio/` 直編集はしない）。
