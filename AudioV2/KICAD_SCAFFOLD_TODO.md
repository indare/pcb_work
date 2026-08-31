# AudioV2 KiCad 素案 — TODO（クラウドエージェント用）

> **警告（2026-08-30）:** 手回し音量確定後は **`generate_kicad_scaffold.py` を再実行しない**（PGA / ENC×6 / DEST リレーに戻る）。  
> 再生成は `python3 AudioV2/scripts/wire_circuit_design.py all`。  
> シンボル修正: [SYMBOL_FIX_TODO.md](SYMBOL_FIX_TODO.md) / レビュー: [SYMBOL_REVIEW_SUMMARY.md](SYMBOL_REVIEW_SUMMARY.md)。

**目的:** 回路の完全性・ピンアサインの正確性は **後レビュー**。まず **開ける・階層が繋がる・net 名が DECISIONS と一致**する素案を作る。

**参照:** [DECISIONS.md](DECISIONS.md) §6.9 / §8 / §9 / §10 / §11、`Audio/Controll.kicad_sch`、`Audio/PowerModule.kicad_sch`

**検証（必須）:**

```bash
python3 Audio/scripts/check_sexpr.py -q AudioV2
```

`kicad-cli` が無い環境でも上記は通すこと。編集後は毎回。

**禁止:** `Audio/` 直下の既存 `.kicad_sch` を改変しない。

---

## Phase 0 — プロジェクト骨格

- [ ] **0.1** `AudioV2/AudioV2Case.kicad_pro` 新規（`Audio/AudioCase.kicad_pro` を雛形。`sheets` UUID は子シートと一致）
- [ ] **0.2** `AudioV2/sym-lib-table` / `fp-lib-table` — `../Audio` の `Library` / カスタム sym を参照（相対パス）
- [ ] **0.3** 親 `AudioV2Case.kicad_sch` — 4 子シート + 箱配線用テキスト（Amp/HP/計測は **載せない**）
- [ ] **0.4** `check_sexpr.py -q AudioV2` パス

---

## Phase 1 — PowerModule（§6.3 着手順 1）

- [ ] **1.1** `PowerModule.kicad_sch` — `Audio/PowerModule.kicad_sch` を **参考に新規**（コピペ改変可）。U1 = **DKMW20F-12**（F-15 から差替）
- [ ] **1.2** USB-C + **CH224K / 50224 枠** を板上に配置（素案: 50224 モジュール + 周辺 F1/PD_12V 端子）
- [ ] **1.3** 階層ラベル: `+12V_IN` / `-12V_IN` / `A_GND` / `PD_12V` / `PD_GND` / `PD_12V_SW`（§9）
- [ ] **1.4** PT2314 用 **+9V または +5V 派生** — 暫定 LDO 1 個 + ラベル `VCC_TONE`（値は TODO コメント）
- [ ] **1.5** 親シートとの sheet pin 接続

---

## Phase 2 — RelayBoard（5chテンプレ×2インスタンス、完了）

- [x] **2.1** `RelayBoard.kicad_sch` — AZ850×10 + ULN2803×2 + 端子台
- [x] **2.2** **MCP23017** + J_I2C 5P（SDA/SCL/3V3/+5V/GND）、JP301/JP302で0x20–0x23
- [x] **2.3** 各Amp: `J_AUD{n}`入力2P、`J_PWR{n}`電源3P（+12/A_GND/-12）
- [x] **2.4** `TONE_L/R`を選択Amp入力へ接続し、電源リレーと同じSET/RESETで連動
- [x] **2.5** 親に **RelayBoard_A** / **RelayBoard_B** の2インスタンス。参照番号も300/400番台で分離
- [x] **2.6** 子Picoなし。MCP23017×1/盤で駆動
- [ ] **2.7 PCBレイアウト時** JP301/JP302 横の F.Silk に番地早見表（0x20 A … 0x23 D）

---

## Phase 3 — ControlPanel（§10 ピン表）

- [ ] **3.1** `ControlPanel.kicad_sch` — **Raspberry Pi Pico 2**（RP2350 モジュール or 汎用 Pico sym）
- [ ] **3.2** ENC×6 — 各 1×3 ヘッダ + GP 番号ラベル（§10 表どおり）
- [ ] **3.3** **SSD1306** OLED（I²C0）
- [ ] **3.4** **PT2314** + 外部 C/R プレースホルダ（DS 参照、値は `DNP` 可）
- [ ] **3.5** **PGA2310PA ×2** SPI デイジーチェーン（§10 / VOLUME_IC_COMPARISON §4）
- [ ] **3.6** **BP5293-50** +5 V（Controll 流用）
- [ ] **3.7** PWR SW + 12 V LED 回路（§9）
- [ ] **3.8** 階層ラベル: `COMMON_LR_IN`、`I2C_BUS`、`+12V`、`-12V`、`A_GND`、`D_GND`

---

## Phase 4 — OutputStage（論理シート、§11 Q2-A 既定）

- [ ] **4.1** `OutputStage.kicad_sch` — DEST 用 **AZ850 ×2〜3** 素案（PHONE / LINE / MUTE）
- [ ] **4.2** ULN2803 + MCP23017 ビット共有 or Control 側 ULN から配線 — **素案は Control 上 ULN の余裕 port から注記**
- [ ] **4.3** 入力: `PGA_HP_L/R`、`PGA_LINE_L/R` — 出力: `PHONE_L/R`、`LINE_L/R`、`MUTE`（開放）
- [ ] **4.4** 親・ControlPanel との sheet / 階層リンク

---

## Phase 5 — 親シート配線（箱配線 IF）

- [ ] **5.1** PowerModule → 星型 ±12V / A_GND バス（グローバルラベル）
- [ ] **5.2** Relay COMMON_LR → Control PT2314 入力（シート間 pin）
- [ ] **5.3** Control PGA 出力 → OutputStage → **J_HP** / **J_LINE** 端子（Audio HP Buffer / LINE 流用先）
- [ ] **5.4** テキストボックス: 「Amp×10 / HP / 計測 = Audio/ 製造済み・図外」
- [ ] **5.5** `MeasurementADC_STATUS.md` 型の **箱配線一覧** を `AudioV2/WIRING.md` に 1 ページ素案

---

## Phase 6 — シンボル（不足分）

| 部品 | 方針 |
|---|---|
| PGA2310PA | KiCad 標準 or `AudioV2/Library.pretty` 同梱 sym 新規 |
| PT2314 | 新規 sym（TSSOP） |
| MCP23017 | 標準 `Interface_Expansion:MCP23017-*` |
| CH224 / 50224 | 50224 はモジュール枠 + `StrawberryLinux` メモ参照 |
| RP2350 / Pico2 | `MCU_Module:Raspberry_Pi_Pico` または Pico 2 相当 |

- [ ] **6.1** 上記のうち repo に無いものを `AudioV2/*.kicad_sym` または親シート `lib_symbols` に追加

---

## Phase 7 — レビュー待ち（素案では埋めなくてよい）

- [x] Q3 I²C トポロジー（daisy / スター）→ **スター確定**（2026-08-31、WIRING.md）
- [ ] Q2-B 独立 Output PCB への物理分割
- [ ] GND NetTie 一点の物理位置
- [ ] DEST リレートポロジーの最終本数
- [ ] ERC / ネットリスト整合（`kicad-cli sch export netlist` — 環境に CLI があれば）

---

## 完了条件（素案）

1. `python3 Audio/scripts/check_sexpr.py -q AudioV2` **exit 0**
2. 親 + 子 **5 `.kicad_sch`** + `.kicad_pro` が存在
3. [README.md](README.md) に「KiCad 素案あり」1 行追記
4. PR に「素案・要レビュー」と明記

---

## ブランチ

素案は `main` にマージ済み。以降は `main` から（歴史ブランチは使わない）。再開: [AGENT_HANDOFF.md](AGENT_HANDOFF.md)。
