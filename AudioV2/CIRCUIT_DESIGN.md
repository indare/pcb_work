# AudioV2 回路設計メモ

**目的:** ピン番号・部品値をデータシートと突き合わせ、手回し音量構成で ERC/配線を詰める。

**方針（2026-08-30）:** 最終出力ボリュームは **A50k デュアル ×2**、DEST は **トグル + ラダー ADC**。[DECISIONS.md](DECISIONS.md) §2・§3・§10。PGA / digipot は不採用。

**参照 DS:** `datasheets/` ローカル PDF。KiCad シンボルは **標準 lib 優先**。カスタムのみ `AudioV2.kicad_sym`（PT2314 28pin / DKMW20F-12 / CH224_50224）と `Audio/BP5293_ROHM`。

---

## 0. シンボル lib 方針

| 部品 | lib_id | 備考 |
|---|---|---|
| PT2314 | `AudioV2:PT2314` | **28pin DIP**（Princeton DS）。旧 8pin 仮シンボルは廃止 |
| RV101/102 | `Device:R_Potentiometer_Dual` | Value **A50k Dual** |
| SW_DEST 音声 | `Switch:SW_DP3T` | unit1=L / unit2=R。MUTE 投げは NC |
| SW_DEST センス | `Switch:SW_SP3T` | 3PDT の 3 極目。COM→ADC |
| ENC×3 | `Device:RotaryEncoder_Switch` | CH / BASS / TREBLE |
| Pico / OLED / LED / R / C | 各標準 lib | |
| ULN2803A / AZ850 | 標準（**RelayBoard のみ**） | DEST ラッチングは廃止 |
| DKMW20F-12 / CH224 / BP5293 | カスタム / プロジェクト | |

---

## 1. ピン照合サマリー（DS vs 図）

| 部品 | DS | AudioV2 図 | 状態 |
|---|---|---|---|
| **PT2314** | 28pin: VDD=1 … REF=28（下表） | `AudioV2:PT2314` 全ピン | ✅ 再作成 |
| **SW_DP3T** | KiCad: COM=3/7, throws=1/2/4 & 5/6/8 | Audio SW101 と同型 | ✅ |
| **R_Potentiometer_Dual** | 1/3=A, 4/6=B, 2/5=wiper | CW←SW, CCW→A_GND, wiper→OUT | ✅ |
| **DEST ラダー** | [DEST_SENSE_LADDER.md](DEST_SENSE_LADDER.md) | Rh/Rl=10k, Rs=1k | ✅ |
| Pico GPIO | DECISIONS §10 | ENC×3 + DEST_ADC/LED | ✅ ドキュメント一致（配線はドラフト） |
| DKMW / CH224 / 7809 | PowerModule | 既存 | ✅ |

---

## 2. PT2314 — 28pin DIP（Princeton DS）

| Pin | 名前 | AudioV2 接続 |
|:---:|---|---|
| 1 | VDD | **+9 V（VCC_TONE）** |
| 2 | AGND | **A_GND** |
| 3 | TREB_L | C 2.7 nF + R 2.4 kΩ（DS） |
| 4 | TREB_R | 同上 |
| 5 | RIN | **COMMON_R** 経 C 2.2 µF |
| 6–16 | ROUT / LOUD / RINx / LINx … | **未使用** — AC-GND または NC（レイアウト時） |
| 17 | LIN | **COMMON_L** 経 C 2.2 µF |
| 18 | LOUT | 未使用（セレクタ出力） |
| 19–22 | BIN/BOUT L/R | R 2.4 kΩ + C 100 nF（Bass） |
| 23 | OUT_R | C 2.2 µF → **TONE_R** → Amp |
| 24 | OUT_L | C 2.2 µF → **TONE_L** → Amp |
| 25 | DGND | **D_GND** |
| 26 | DATA | Pico I²C SDA 経 4.7 kΩ → 3.3 V |
| 27 | CLK | Pico I²C SCL 経 4.7 kΩ → 3.3 V |
| 28 | REF | R 5.6 kΩ + C 22 µF → AGND |

**電源:** VDD typ 9 V（6–10 V）。±12 V 直結不可 → LM7809（PowerModule）。

---

## 3. OutputStage — DEST + 音量（手回し）

```text
AMP_SEL_L/R ── SW101 (DP3T)
                 ├─ PHONE (1/5) ── RV101 A50k ── PHONE_L/R → HP Buffer
                 ├─ MUTE  (2/6) ── NC
                 └─ LINE  (4/8) ── RV102 A50k ── LINE_L/R → LINE OUT
```

| 項目 | 値 |
|---|---|
| ポット | **Alps RK27112A00CF** ×2（A50k Dual / RK27）。パネル＋ヘッダ |
| DEST SW | **C&K 7303SYZQE**（3PDT ON-OFF-ON）。論理シンボルは DP3T+SP3T |
| 固定パッド | **0 Ω**（§9）。DNP で −10 dB 後付け可 |
| DEST センス | 同一 SW の 3 極目 + 10k/10k/1k |

品番の根拠・代替: [PARTS.md](PARTS.md)。

---

## 4. PowerModule — 部品値（変更なし）

USB-C → CH224 → PD_12V → PWR SW → F1 → DKMW20F-12 → ±12 V / A_GND。  
+12 V → LM7809 → VCC_TONE（+9 V）。

---

## 5. 机上検算

| 項目 | 結果 |
|---|---|
| PT2314 @9 V | Is typ 30 mA — 7809 散逸 ≈0.12 W |
| DEST ラダー | LINE 3.03 / MUTE 1.65 / PHONE 0.28 V（±5% 間隔 ≈1.3 V） |
| A50k 負荷 | Amp は 50 kΩ を問題なく駆動 |

---

## 6. KiCad 更新チェックリスト

- [x] PT2314 シンボル — **28pin DS 一致**
- [x] PGA2310 / DEST ラッチング / ENC_HP·LINE·DEST — **削除**
- [x] OutputStage — SW_DP3T + A50k Dual ×2
- [x] ControlPanel — ENC×3 + DEST ラダー + LED
- [x] `check_sexpr.py -q AudioV2` — OK
- [x] `kicad-cli sch export netlist` — OK（annotation 警告はドラフト）
- [x] 3PDT / A50k 具体型番 — [PARTS.md](PARTS.md)
- [ ] ERC 整理（未接続・未使用 PT2314 入力）
- [ ] RelayBoard 本配線
- [ ] 未使用 PT2314 入力の AC-GND 実装

## 7. 再生成

```bash
python3 AudioV2/scripts/wire_circuit_design.py all
python3 Audio/scripts/check_sexpr.py -q AudioV2
```

---

## 変更履歴

| 日付 | 内容 |
|---|---|
| 2026-08-30 | 初版 — 素案ピン監査 |
| 2026-08-30 | **手回し化** — PGA 削除、PT2314 28pin 再作成、OutputStage ポット+トグル |
| 2026-08-30 | **品番** — SW_DEST=7303SYZQE、RV=RK27112A00CF（[PARTS.md](PARTS.md)） |
