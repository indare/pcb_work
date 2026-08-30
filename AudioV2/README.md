# AudioV2（作業中）

`Audio/`（AudioCase）を参考に、操作系を Pico 2 前提で再構成する作業用ディレクトリ。

- **計測 / スペアナ**（`MeasurementADC` + 計測 Pico 2）は現行どおり独立
- **操作 Pico 1 台**＋リレー盤は **I²C GPIO 拡張（MCP23017）**
- **電源: ±12 V** — **PowerModule 再設計**（DKMW20F-12 + **USB-C / CH224 内蔵**）
- **Amp / HP** — `Audio/` 製造済み基板を **物理流用**（電源電圧にほぼ非依存。AudioV2 回路図には載せない）
- 音量: PGA2310PA ×2（SPI）、トーン: PT2314（I²C、Amp 前）
- **物理 PCB:** Relay **5+5×2**、Control+Output **1 枚**、Power **1 枚**（§11）
- **次:** KiCad 起こし（Q3 I²C はレイアウト時）

詳細は [DECISIONS.md](DECISIONS.md)。音量 IC 比較は [VOLUME_IC_COMPARISON.md](VOLUME_IC_COMPARISON.md)。データシートは [datasheets/](datasheets/)。

## いまの `Audio/` からの参照元

| 流用・参照 | 内容 |
|---|---|
| Amp / HP バッファ | **実基板のみ**流用。KiCad には載せない |
| PowerModule | **再設計**の参考（`Audio/PowerModule.kicad_sch` は F-15） |
| リレー＋端子台＋ULN | `Audio/Controll.kicad_sch` |
| 親 UI ファーム（原型） | `Control/` → 新規 `AudioV2/control_fw/` |
| GND 分離の型 | `MeasurementADC` の NetTie |

## このディレクトリの置き方

回路図（`.kicad_sch` / `.kicad_pro`）は未作成。判断確定済み — ここに新規プロジェクトとして起こす（`Audio/` 直編集はしない）。
