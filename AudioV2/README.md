# AudioV2（作業中）

`Audio/`（AudioCase）を参考に、操作系を Pico 2 前提で再構成する作業用ディレクトリ。

- **計測 / スペアナ**（`MeasurementADC` + 計測 Pico 2）は現行どおり独立
- **操作 Pico 1 台**＋リレー盤は **I²C GPIO 拡張（MCP23017）**
- **電源: ±12 V** — **PowerModule 再設計**（DKMW20F-12 + **USB-C / CH224 内蔵**）
- **Amp** — AudioV2版を再設計（±12 V、ゲイン2、100 µF/rail + 100 nF + 1 nF、DIP-8）。代表1シート、**×10製造**
- **HP** — `Audio/` 製造済み基板を物理流用
- 音量: **手回しデュアルポット ×2**（HP / LINE）。DEST: 機械 SW + ADC + LED + OLED。トーン: PT2314（I²C、Amp 前）
- **物理 PCB:** Relay **5+5×2**、Control+Output **1 枚**、Power **1 枚**、Amp **×10**（計14枚、設計5種）
- **KiCad 素案** — 手回し音量構成（PT2314 28pin / SW_DP3T / A50k Dual）。[CIRCUIT_DESIGN.md](CIRCUIT_DESIGN.md)
- **品番:** [PARTS.md](PARTS.md) — DEST **C&K 7303SYZQE**、音量 **Alps RK27112A00CF** ×2、制御 OLED **2.42″**、スペアナ **Waveshare 29318**
- **Relay:** 各盤5ch、Amp入力＋電源を連動切替（MCP23017×1 / ULN2803×2 / AZ850×10）
- **次:** ControlPanel ERC整理、OLED FP差し替え、未使用PT2314入力
- **エージェント再開:** [AGENT_HANDOFF.md](AGENT_HANDOFF.md)（クラウド会話の長期記憶）

詳細は [DECISIONS.md](DECISIONS.md)。DEST ラダーは [DEST_SENSE_LADDER.md](DEST_SENSE_LADDER.md)。過去の音量 IC 比較（アーカイブ）は [VOLUME_IC_COMPARISON.md](VOLUME_IC_COMPARISON.md)。データシートは [datasheets/](datasheets/)。

## いまの `Audio/` からの参照元

| 流用・参照 | 内容 |
|---|---|
| Amp | `Audio/AmpModule`を基にAudioV2版へ再設計。`AmpModule.kicad_sch/.kicad_pcb` |
| HP バッファ | **実基板のみ**流用。KiCad には載せない |
| PowerModule | **再設計**の参考（`Audio/PowerModule.kicad_sch` は F-15） |
| リレー＋端子台＋ULN | `Audio/Controll.kicad_sch` |
| 親 UI ファーム（原型） | `Control/` → 新規 `AudioV2/control_fw/` |
| GND 分離の型 | `MeasurementADC` の NetTie |

## このディレクトリの置き方

判断確定済み（main マージ済み）— KiCad は **#19** で回路設計・ピン修正中。`Audio/` 直編集はしない。
