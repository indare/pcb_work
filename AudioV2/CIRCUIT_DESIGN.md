# AudioV2 回路設計メモ

**目的:** ピン番号・部品値をデータシートと突き合わせ、手回し音量構成で ERC/配線を詰める。

**方針（2026-08-30）:** 最終出力ボリュームは **A50k デュアル ×2**、DEST は **トグル + ラダー ADC**。[DECISIONS.md](DECISIONS.md) §2・§3・§10。PGA / digipot は不採用。

**参照 DS:** `datasheets/` ローカル PDF。KiCad シンボルは **標準 lib 優先**。カスタムのみ `AudioV2.kicad_sym`（PT2314 28pin / REC10K-2415DAW / TMUX7612 / CH224_50224）と `Audio/BP5293_ROHM`。

---

## 0. シンボル lib 方針

| 部品 | lib_id | 備考 |
|---|---|---|
| PT2314 | `AudioV2:PT2314` | **28pin DIP**（Princeton DS）。旧 8pin 仮シンボルは廃止 |
| RV601/602 | `Device:R_Potentiometer_Dual` | Value **A50k Dual** |
| SW_DEST 音声 | `Switch:SW_SP3T`×2 | SW601=L / SW602=R。MUTE 投げは NC |
| SW_DEST センス | `Switch:SW_SP3T` | 3PDT の 3 極目。COM→ADC |
| ENC×3 | `Device:RotaryEncoder_Switch` | CH / BASS / TREBLE |
| Pico / OLED / LED / R / C | 各標準 lib | OLED は論理 `SSD1306-128x64`。**実物は 2.42″（[PARTS.md](PARTS.md)）。埋め込み元 0.91″ FP は差し替え予定** |
| ULN2803A / AZ850 | 標準（**RelayBoard のみ**） | DEST ラッチングは廃止 |
| REC10K-2415DAW / CH224 / BP5293 | カスタム / プロジェクト | FP `Library:REC10K-AW_1in_THT`。穴位置は旧 `DKMW20F-15_1in_THT` と同一で、各穴の機能も一致（業界標準 1″ 6ピン）。番号の振り方だけが違う |

---

## 1. ピン照合サマリー（DS vs 図）

| 部品 | DS | AudioV2 図 | 状態 |
|---|---|---|---|
| **PT2314** | 28pin: VDD=1 … REF=28（下表） | `AudioV2:PT2314` 全ピン | ✅ 再作成 |
| **SW_SP3T**×2 | KiCad: COM=3, throws=1(PHONE)/2(MUTE)/4(LINE) | 旧 Audio SW101(DP3T) を L/R 2個に分割 | ✅ |
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

**電源:** VDD typ 9 V（6–10 V）。±15 V 直結不可 → LM7809（PowerModule）。

---

## 3. OutputStage — DEST + 音量（手回し）

```text
AMP_SEL_L ── SW601 (SP3T) / AMP_SEL_R ── SW602 (SP3T)
                 ├─ PHONE (pin1) ── RV601 A50k ── PHONE_L/R → HP Buffer
                 ├─ MUTE  (pin2) ── NC
                 └─ LINE  (pin4) ── RV602 A50k ── LINE_L/R → LINE OUT
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

USB-C → CH224 → PD_12V → PWR SW → F201 → **REC10K-2415DAW/H2** → **±15 V** / A_GND。
（2026-09-01 に ±12 V から変更。理由は [DECISIONS.md](DECISIONS.md) §8。回路図のネット名も `+15V`/`-15V` に改名済み）  
+15 V → LM7809 → VCC_TONE（+9 V）。

### RelayBoard — **廃止**（2026-09-01、`AmpBank` へ統合。AGENT_HANDOFF §2.9）

> **この節は旧アーキテクチャの記録です。** RelayBoard と AmpModule は 10ch 分を載せた
> 1枚の基板 **`AmpBank`** へ統合することが決まりました。入力と出力の両方をアナログスイッチで切り替え、
> 電源は常時給電します。以下は統合前の仕様で、削除済みの `RelayBoard.kicad_sch` の実装内容の記録です。

#### 旧仕様（5ch×2枚）

- 1枚あたり MCP23017×1、ULN2803×2、AZ850×10（audio/power各5）
- `TONE_L/R → audio relay → 選択Amp J701`
- `±12 V → power relay → 選択Amp J703`、A_GNDは常時接続
- 各chのaudio/powerリレーはSET同士・RESET同士を並列駆動し、状態不一致を防止
- ネット名: `CH{n}_SET` / `CH{n}_RST` = コイルパルス、`CH{n}_SET_CMD` / `CH{n}_RST_CMD` = MCP→ULN のロジック
- 図面サイズは **A3**（5ch×リレー20個ぶんのラベルを重ねずに置くため）
- `J_RAIL`: PowerModule `J201` から +12 / A_GND / -12 の3P。`A_GND`は切替せず各 `J_PWR`-2 へ直結
- `J_TONE`: PT2314出力の2P（L/R）。シールドはControl側`A_GND`のみ。Relayのアナログ基準は`J_RAIL`-2
- I²C コネクタ: SDA / SCL / 3V3 / D_GND の **4P**（AmpBank 側 `J_CTRL301`）。**旧 5P の `+5V` は不要になった** — AZ850 のコイル駆動用だったが、アナログスイッチ化で消えた
- JP301=A0、JP302=A1（開=0）。00=0x20 A / 01=0x21 B / 10=0x22 C / 11=0x23 D。A2はGND固定。同じ回路で最大4枚
- `C301`/`C302` は `J_I2C` 直近（3V3 / +5V 入口のパスコン。アナログ端子台ではない）

```text
JP302  JP301   ADDR   BOARD
  開     開    0x20     A
  開     閉    0x21     B
  閉     開    0x22     C
  閉     閉    0x23     D
```
- Amp J702出力は47 Ω＋470 µF後を箱配線で`AMP_SEL_L/R`へ共通化

---

## 5. AmpModule — AudioV2再版（**廃止・記録** — 2026-09-01、`AmpBank` へ統合。AGENT_HANDOFF §2.9）

> **この節は旧アーキテクチャの記録です。** `AmpModule.kicad_sch` は削除済み。現行は §2.9 の
> `AmpBank`（出力カップリング 2.2 µF film、常時給電、TMUX7612 切替）。以下は統合前の仕様。

- 信号経路: `J701 → 100 nF film + 10 µF → 非反転Amp → 47 Ω → 470 µF → J702`
- ゲイン: `1 + 20 kΩ / 20 kΩ = 2`（L/R同一。ソース音量で Loudness、Amp は電気的余裕）
- 入力プルダウン: 220 kΩ、非反転バイアス: 1 kΩ
- 電源: `J703 = +12 V / A_GND / -12 V`
- デカップリング（各レール）: 100 µF polymer + 100 nF X7R + 1 nF C0G
- AMP701: DIP-8ソケット。NE5532Pを基準とし、高速品差し替え時も47 Ω出力アイソレーションを維持
- `AudioV2Case.kicad_sch` は代表1シートのみ。物理PCB/BOMは同一仕様を×10製造し、RelayBoardで入力＋電源を選択

PCB は未設計（2026-09-01 に削除）。着手時は `Audio/split/AudioCase_4_amp.kicad_pcb` の実績配線を参考に、端子・取付穴を維持し、100 µF×2のため上辺のみ15 mm拡張する。要件は [PARTS.md](PARTS.md) §4.2。

---

## 6. 机上検算

| 項目 | 結果 |
|---|---|
| PT2314 @9 V | Is typ 30 mA — `L7809CV` 散逸 **≈0.18 W**（+15 V 入力。旧 ±12 V 前提では 0.12 W と書いていた） |
| DEST ラダー | LINE 3.03 / MUTE 1.65 / PHONE 0.28 V（±5% 間隔 ≈1.3 V） |
| A50k 負荷 | Amp は 50 kΩ を問題なく駆動 |

---

## 7. KiCad 更新チェックリスト

**2026-09-03 の構成刷新で `ControlPanel` / `PowerModule` / `OutputStage` / `AmpBank`（および
それ以前に廃止された `RelayBoard` / `AmpModule`）は解体され、`legacy/` に凍結された。**
それらの基板に対する未完了項目は**もう作業対象ではない**ので、下は現行構成の残りだけ。
現行のシート構成は [CLAUDE.md](../CLAUDE.md)「シートの所有権」が正。

- [ ] OLED KiCad FP — 0.91″ 埋め込みを 2.42″ or 1×4 ヘッダに差し替え
- [ ] ERC 整理（未接続・未使用 PT2314 入力）
- [ ] 未使用 PT2314 入力の AC-GND 実装
- [ ] PCB — 母板・娘基板とも未設計（旧 AmpModule PCB 用にまとめた要件は [PARTS.md](PARTS.md) §4.2 に残る）

### 刷新前に完了していた項目（2026-09-03 までの記録）

- [x] PT2314 シンボル — **28pin DS 一致**
- [x] PGA2310 / DEST ラッチング / ENC_HP·LINE·DEST — **削除**
- [x] OutputStage — SW_DP3T + A50k Dual ×2（→ シートは母板へ統合）
- [x] ControlPanel — ENC×3 + DEST ラダー + LED（→ シート解体。UI は `MeasureControl` へ、PT2314 は母板へ）
- [x] `check_sexpr.py -q AudioV2` — OK
- [x] `kicad-cli sch export netlist` — OK（annotation 警告はドラフト）
- [x] 3PDT / A50k 具体型番 — [PARTS.md](PARTS.md)
- [x] 表示品番 — 制御 OLED 2.42″ / スペアナ Waveshare 29318（v1）
- [x] AmpModule — 代表回路図、バルク/1 nF対応、×10注記（→ 廃止。10ch は娘基板側へ）
- [x] RelayBoard 本配線 — 5ch×2、入力＋電源連動（→ 基板ごと廃止。PCB 用の番地早見表シルクも不要になった）

## 8. 再生成

どのシートを誰が生成するかは [CLAUDE.md](../CLAUDE.md)「シートの所有権」が正。
現行の再生成手段はこの2本で、どちらも冪等（再実行でバイト一致）。`--dry-run` で内訳だけ出る。

```bash
python3 AudioV2/scripts/build_motherboard.py   # 母板 ＋ 親のパッチ
python3 AudioV2/scripts/build_daughter.py      # 娘基板2版（スイッチ / リレー）＋ 親のパッチ
python3 Audio/scripts/check_sexpr.py -q AudioV2
```

`MeasureControl` は生成対象外（KiCad 側が正）。ERC・ネットリストの検証コマンドと
期待値は CLAUDE.md にある。

> **⚠ `wire_circuit_design.py` は再生成の道具ではない。** 旧構成（`PowerModule` /
> `ControlPanel` / `OutputStage` / `AmpBank`）のロジックの記録として残してあるだけで、
> **現行のシートを出力する経路を持たない**（[AGENT_HANDOFF.md](AGENT_HANDOFF.md) §2.8、
> および同「別チャット再開プロンプト」の道具一覧）。
> かつてこの節が案内していた `wire_circuit_design.py all` は再生成にならないので使わない。
> `generate_kicad_scaffold.py` も再実行しない（手回し音量前の素案に戻る）。

---

## 変更履歴

| 日付 | 内容 |
|---|---|
| 2026-08-30 | 初版 — 素案ピン監査 |
| 2026-08-30 | **手回し化** — PGA 削除、PT2314 28pin 再作成、OutputStage ポット+トグル |
| 2026-08-30 | **品番** — SW_DEST=7303SYZQE、RV=RK27112A00CF（[PARTS.md](PARTS.md)） |
| 2026-08-31 | **Amp再版** — ゲイン2（20k/20k）、±12 V、100 µF/100 nF/1 nF、独立PCB |
| 2026-09-03 | §8 の再生成手段を `build_motherboard.py` / `build_daughter.py` に差し替え（`wire_circuit_design.py all` は再生成にならない）。§7 チェックリストから解体済みシートの未完了項目を外し、記録として分離 |
