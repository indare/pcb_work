# Audio（AudioCase）

KiCad プロジェクトと関連ドキュメント。

## ドキュメント案内

| ファイル | 内容 |
|---|---|
| [MeasurementADC_STATUS.md](MeasurementADC_STATUS.md) | **現状・次作業・箱内配線方針**（まずここ） |
| [MeasurementADC_BRINGUP.md](MeasurementADC_BRINGUP.md) | 初号機の切り分けログ（履歴） |
| [MeasurementADC_ORDER.md](MeasurementADC_ORDER.md) | 発注・在庫 |
| [measurement_fw/README.md](measurement_fw/README.md) | 計測 Pico2 ファーム |
| [../Control/README.md](../Control/README.md) | Controll 親／子ファーム |
| [../README.md](../README.md) | リポジトリ全体・KiCad MCP |

## 階層シート

| シート | 役割 | いまの扱い |
|---|---|---|
| PowerModule | **TEC 3-1223** ±15 / A_GND（旧 MCW03）。計算メモ: [PowerModule_TEC3_REDESIGN.md](PowerModule_TEC3_REDESIGN.md) | 箱に入れる |
| AmpModule | NE5532 Amp（×10 想定） | ラインアウト（J11）。ADC へは AdcBuffer 経由 |
| AdcBuffer | ゲイン1バッファ（DIP-8 / OPA1652互換） | Amp L/R_OUT → MeasurementADC AUDIO |
| Controll | CH1–10 リレー（親＋子） | 実機では外している |
| MeasurementADC | 計測＋LCD | 初号応急配線で稼働 |
| EQModule | EQ | 今号では使わない |
| RVConvert | RV 変換 | 箱計画に含むかは別途 |

## 分割 Gerber

`split/Gerber/` — `01_main` … `06_measurement_adc`。再生成は `scripts/regenerate_split_gerbers.py`。
