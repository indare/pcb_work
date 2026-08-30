# AudioV2 KiCad 素案 — TODO（クラウドエージェント用）

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

## Phase 2 — RelayBoard（5ch テンプレ ×1、§11 Q1-B）

- [ ] **2.1** `RelayBoard.kicad_sch` — `Controll` から **AZ850 + ULN2803 + 端子台** を抜粋（5ch 分のみ素案）
- [ ] **2.2** **MCP23017** + I²C コネクタ J_I2C（SDA/SCL/3V3/GND）+ アドレス 0x20（2 枚目は 0x21 と注記）
- [ ] **2.3** 各 Amp: `AMP{n}_L/R` 入力端子、`AMP{n}_V+` / `AMP{n}_V-` 電源端子（n=1..5）
- [ ] **2.4** **COMMON_LR_OUT** — L/R + `A_GND` 階層ラベル（§11.8）
- [ ] **2.5** 親に **RelayBoard_A** / **RelayBoard_B** の 2 インスタンス（同一 file、sheet name だけ変更）— または 1 インスタンス + 注記「×2 製造」
- [ ] **2.6** 旧 Controll の **子 Pico 削除**（MCP23017 前提）

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

- [ ] Q3 I²C 拓扑（daisy / スター）
- [ ] Q2-B 独立 Output PCB への物理分割
- [ ] GND NetTie 一点の物理位置
- [ ] DEST リレー拓扑の最終本数
- [ ] ERC / ネットリスト整合（`kicad-cli sch export netlist` — 環境に CLI があれば）

---

## 完了条件（素案）

1. `python3 Audio/scripts/check_sexpr.py -q AudioV2` **exit 0**
2. 親 + 子 **5 `.kicad_sch`** + `.kicad_pro` が存在
3. [README.md](README.md) に「KiCad 素案あり」1 行追記
4. PR に「素案・要レビュー」と明記

---

## ブランチ

`cursor/audiov2-kicad-scaffold-2c9e`（`cursor/audiov2-scaffold-2c9e` から分岐可）
