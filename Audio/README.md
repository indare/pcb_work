# Audio（AudioCase）

KiCad プロジェクトと関連ドキュメント。

## ドキュメント案内

| ファイル | 内容 |
|---|---|
| [MeasurementADC_STATUS.md](MeasurementADC_STATUS.md) | **現状・次作業・箱内配線方針**（まずここ） |
| [MeasurementADC_BRINGUP.md](MeasurementADC_BRINGUP.md) | 初号機の切り分けログ（履歴） |
| [MeasurementADC_ORDER.md](MeasurementADC_ORDER.md) | 発注・在庫 |
| [measurement_fw/README.md](measurement_fw/README.md) | 計測 Pico2 ファーム |
| [measurement_fw/OVERLAP_FFT_NOTES.md](measurement_fw/OVERLAP_FFT_NOTES.md) | スペアナ分解能／fps（オーバーラップ）方針メモ |
| [../Control/README.md](../Control/README.md) | Controll 親／子ファーム |
| [../README.md](../README.md) | リポジトリ全体・KiCad MCP |

## 階層シート

| シート | 役割 | いまの扱い |
|---|---|---|
| PowerModule | MCW03 ±15 / A_GND | 箱に入れる |
| AmpModule | NE5532 Amp（×10 想定） | Amp→スペアナ接続中 |
| Controll | CH1–10 リレー（親＋子） | 実機では外している |
| MeasurementADC | 計測＋LCD | 初号応急配線で稼働 |
| EQModule | EQ | 今号では使わない |
| RVConvert | RV 変換 | 箱計画に含むかは別途 |

## 分割 Gerber

`split/Gerber/` — `01_main` … `06_measurement_adc`。再生成は `scripts/regenerate_split_gerbers.py`。
