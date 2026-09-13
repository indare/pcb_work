# AudioV2 PCB — メーカー資料索引

一次資料へのリンク集。エージェントは必要な節だけ開く。

---

## 1. メーカー横断ガイド（部品非依存）

### Texas Instruments

| 資料 | URL |
|---|---|
| High-Speed Layout Guidelines (SCAA082) | https://www.ti.com/lit/an/scaa082a/scaa082a.pdf |
| High-Speed Interface Layout Guidelines (SPRAAR7) | https://www.ti.com/lit/an/spraar7j/spraar7j.pdf |
| High-Speed DSP Systems Design Reference (SPRU889) | https://www.ti.com/lit/ug/spru889/spru889.pdf |
| Mixed-signal grounding Part 1 (SLYT499) | https://www.ti.com/lit/pdf/SLYT499 |
| Mixed-signal grounding Part 2 (SLYT512) | https://www.ti.com/lit/an/slyt512/slyt512.pdf |
| How (Not) to Decouple HS Op Amps (SLOA069) | https://www.ti.com/lit/an/sloa069/sloa069.pdf |
| High-Speed Op Amp Layout (SLOA046) | https://www.ti.com/lit/an/sloa046/sloa046.pdf |
| Op amp layout basics (Precision Hub) | https://e2e.ti.com/blogs_/archives/b/precisionhub/posts/the-basics-how-to-layout-a-pcb-for-an-op-amp |

### Analog Devices

| 資料 | URL |
|---|---|
| MT-031 Grounding Data Converters (AGND/DGND) | https://www.analog.com/media/en/training-seminars/tutorials/mt-031.pdf |
| Staying Well Grounded | https://www.analog.com/en/resources/analog-dialogue/articles/staying-well-grounded.html |
| Successful PCB Grounding (path of least impedance) | https://www.analog.com/en/resources/technical-articles/successful-pcb-grounding-with-mixedsignal-chips--follow-the-path-of-least-impedance.html |
| AN-1142 High Speed ADC PCB Layout | https://www.analog.com/en/resources/app-notes/an-1142.html |
| LT1763 datasheet (IN/OUT/BYP layout) | https://www.analog.com/media/en/technical-documentation/data-sheets/1763fh.pdf |

### Microchip

| 資料 | URL |
|---|---|
| AN1258 Op Amp Precision Design: PCB Layout | https://ww1.microchip.com/downloads/en/AppNotes/01258B.pdf |
| AN688 Layout Tips for 12-Bit A/D | https://ww1.microchip.com/downloads/aemDocuments/documents/MCU08/ApplicationNotes/ApplicationNotes/00688b.pdf |
| MCP23017 address/reset/I²C pitfalls (support article) | https://support.microchip.com/s/article/Troubleshooting-Excessive-Current-Draw-and-I2C-Address-Instability-in-MCP23017-Based-Designs |

### ST / NXP

| 資料 | URL |
|---|---|
| ST AN1709 EMC design guide (MCU) | https://www.st.com/resource/en/application_note/an1709-emc-design-guide-for-stm8-stm32-and-legacy-mcus-stmicroelectronics.pdf |
| NXP AN10441 I²C level shifting (BSS138 型) | https://www.nxp.com/docs/en/application-note/AN10441.pdf |

---

## 2. AudioV2 主要部品（DS の Layout / Power）

| 部品 | 役割（概略） | 一次資料 |
|---|---|---|
| TMUX7612 | AmpBank アナログ SW | https://www.ti.com/lit/ds/symlink/tmux7612.pdf — §8.4 Power, §8.5 Layout（図 8-5, 8-6） |
| OPA1656 / OPA1652 | オーディオ OP | https://www.ti.com/lit/ds/symlink/opa1656.pdf — §8.4 Layout |
| MCP23017 | SEL / UI I²C GPIO | https://ww1.microchip.com/downloads/en/DeviceDoc/20001952c.pdf |
| LT1763 | LDO | https://www.analog.com/media/en/technical-documentation/data-sheets/1763fh.pdf |
| BSS138 | I²C レベル変換 | AN10441（上表）＋素子 DS |

### TMUX7612 Layout で特に見る項目

- VDD/VSS→GND: 0.1µF（＋推奨 1µF）。小さい方をピン直近。耐圧に注意
- 敏感系: デカップのピン接続はビア回避を検討。平面接続は複数ビア可
- アナログとデジタル（SEL）並走禁止。交差は直角のみ
- 直角トレース回避（幅一定のアール／45°）
- 入力短く、電源トレースは幅広、ベタ GND
- WQFN 露出パッドは VSS（本設計は TSSOP だが DS 記載として把握）

### OPA165x Layout で特に見る項目

- 各電源ピンに低 ESR 0.1µF をピン直近
- ピンとデカップのあいだにビアを入れない
- 入力は短く、電源／出力と離す
- A/D グラウンドは電流の流れを見て分ける

### MCP23017 で特に見る項目

- VDD–VSS 100nF 直近
- A0–A2 / RESET を浮かせない
- SDA/SCL プルアップ（バス条件に合わせる）

---

## 3. プロジェクト既決との対応（文献の使い方）

| 既決（NOW 等） | 文献側の言い方 |
|---|---|
| A↔D は親 NetTie 一点。娘に安易に足さない | MT-031 / Staying Well Grounded / 帰りの最短。二重結合＝ループ |
| AMP_SEL は B.Cu、TSSOP パッド上ビア禁止 | TMUX §8.5（敏感経路・ビア注意）と整合しやすい |
| 電源 100nF を DIP 裏 | OPA「ピン直近」理想より遠い。ソケット都合の妥協として明示する |
| 娘 SEL 帰りの遠回りを v0.1 で許容 | SLYT 多基板＋共有インピーダンス。自己 L だけでは結論しない |

文献だけで既決を覆さない。覆すならユーザー確認。

---

## 4. 更新メモ

- リンク切れしたらメーカー lit 番号（SCAA082, MT-031, AN1258 等）で再検索する
- 新チップを採用したら §2 の表に DS Layout 節だけ足す（数値の複製はしない）
