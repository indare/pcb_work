# MeasurementADC 進捗メモ

最終更新: **2026-07-27**（PCB 配置・VCOM/VIN 幹線の WIP を反映。他 Cursor agent 引き継ぎ用）

Amp 調整用の基準計測モジュール（OPA1656 + 共立 ADC1804_F / PCM1804 + Pico2 + WAVESHARE LCD）。

---

## 他エージェントへの引き継ぎ（2026-07-27）

### いまどこまでか（一言）

回路図・FP・部品調達は概ね完了。**親 PCB `AudioCase.kicad_pcb` で MeasurementADC の OPA×3＋A701 周辺を配置し、VCOM/VIN 幹線を引き始めた WIP。** ADC_GND 星点配線・DRC クリーン・電源/デジタル配線はこれから。

### 触るファイル

| ファイル | 役割 |
|---|---|
| `Audio/AudioCase.kicad_pcb` | **主戦場**（親 PCB） |
| `Audio/MeasurementADC1804_Module.kicad_sch` | 計測モジュール回路図 |
| `Audio/AudioCase.kicad_sch` | 親・階層シート |
| `Audio/route_preview_opamp_adc.png` | OPA→ADC 配線プレビュー（参考） |
| `Audio/MeasurementADC_ORDER.md` | 発注・在庫・FP メモ |
| 本ファイル | 方針・残タスク |

### 最新コミット（main）

- `de87cf0` — wip: OPA 周辺配置と VCOM/VIN 配線を途中保存
- `76ee512` — wip: 配線作業前の状態を退避
- `d404fbb` — 配置＋GND ベタ

### PCB 現状スナップショット（2026-07-27 夜）

**配置（概ね OK）**

```
左: J701/J703(±15V) → U701–U703(OPA) → …
右寄り: R713–716(47Ω) / C719–720(VCOM bypass) → A701(ADC1804)
電源デジ: U704–U710 / Pico / LCD（右側〜上）
```

| 項目 | 状態 |
|---|---|
| C719/C720 ↔ A701 VCOM ピン | 約 **9mm**（A701 側へ寄せ済） |
| R713–716 ↔ A701 VIN ピン | 約 **11mm**（ADC 側へ寄せ済） |
| U701↔U702 | 近接（入力ブロックまとめ済） |
| C705(φ5 Disc) ↔ U701 | ボディ隙間 **+**（干渉解消） |
| **C705 ↔ C707(φ5 電解)** | ボディ **約 −1.3mm 重なり → 要再配置** |
| C706 ↔ R701 | 接近／重なり気味 → 要確認 |

**配線**

| ネット | 銅（目安） | メモ |
|---|---|---|
| `VCOML` | あり（〜40mm 級） | U702 側〜A701 方向。**パッド直結は DRC で要確認** |
| `VCOMR` | あり（〜55mm 級） | 同上（U703） |
| `VINL±` / `VINR±` | 各〜11mm | R713–716↔A701 幹線開始。OPA 出力側の接続も要確認 |
| `ADC_GND` | **ほぼ未配線** | C719/C720 GND 足・A701・NT701 を星点で閉じる必要あり |
| OPA ローカル（帰還・AUDIO・±15V） | U701/U702 中心に進捗 | U703 もローカルは進んでいる |

**VCOM の正しい理解（取り違え注意）**

- VCOM は **ADC（A701）が出す基準** → 2段目 OPA の **＋入力へ入れる**
- U702: pin3=`INA+` と pin5=`INB+` を **同一 `VCOML` で短絡** → A701 pad2（＋ C719）
- U703: 同様に pin3/5 → `VCOMR` → A701 pad5（＋ C720）
- U701 の pin3/5 は **`GND`**（入力インバータ段）。VCOM ではない
- OPA 出力（pin1/7）は VCOM ではなく **VIN± 側**（R713–716 経由）

#### 更新（2026-07-27 深夜・配線追加ぶん）

コミット `de87cf0` ＋以降の手作業。導通は S 式パースで検証済（islands=1 = 当該ネットの全パッドが単一連結）。

| ネット | 状態 |
|---|---|
| `VINL±` / `VINR±` | **完了** R713–716.1 ↔ A701 を F.Cu 0.5mm 直線（各 10.65–10.70mm、スキュー 0.05mm 以内） |
| `VCOML` / `VCOMR` | **完了** U702/U703 の pin3・pin5 ↔ C719/C720 ↔ A701 pad2/pad5 まで導通 |
| OPA 出力 `U70xA/B-OUT` | **完了** R713–716.2 まで導通 |
| `ADC_GND` | ベタ追加（F.Cu/B.Cu、`(420.5,100)–(562,178)`）。A701・C719/C720・Y701 はこれで結合。**x>562 の LDO 群 23 パッドは未接続のまま** |
| `AUDIO_L/R_IN` | 2 島だが正常（J11＝別基板 ↔ J701＝当基板、ハーネス接続のため） |

- **NT701 を (508.8, 166.95) → (421, 150) rot180 に移動。** GND ベタ（B.Cu は x≤419.7）と ADC_GND ベタ（x≥420.5）の境界を pad2=418.4 / pad1=421.0 でまたぐ配置。
- テストポイント TP703–TP710 を `board_only` 属性で追加（各段出力・VCOM・GND/ADC_GND 基準）。TP701/TP702 は削除済。
- ADC_GND ベタの左端 420.5 は暫定。R713–716 の帰路を厳密に ADC_GND に乗せるなら x≈404 まで伸ばし、GND ベタ側を引く。

**既知のクリアランス違反 4 件（すべて上記追加より前から存在）**

| 箇所 | 実測 | 要求 |
|---|---|---|
| `AMP_V-_IN` ↔ C711.1 | **−0.131mm（重なり）** | 0.2 |
| `VCOML` ↔ U702.6 | 0.141mm | 0.2 |
| `Net-(U702B-INB-)` ↔ U702.7 | 0.141mm | 0.2 |
| `Net-(U703A-INA-)` ↔ U703.3 | 0.141mm | 0.2 |

SOIC-8 は隣接パッド間が 0.67mm しかなく、0.5mm 幅＋0.2mm クリアランスでは物理的に通らない。該当区間だけ 0.25mm 幅に落とすか、パッド端から回すこと。

### すぐやる順（PCB）

1. **C705 と C707 を離す**（中心同士 ≥6–7mm 目安、ボディ隙間 ≥0.5mm）
2. ~~**VCOML/R をパッドまで落とす**~~ → **完了**（上記更新を参照）
3. ~~**VIN±**: R713–716 両端（OPA OUT ↔ A701）を閉じる~~ → **完了**
4. **`ADC_GND` 星点**: NT701 移動とベタ追加まで完了。残りは x>562 の LDO 群をベタに載せる（ベタ延長 or 個別配線）
5. 電源デジ配線（MCLK/I2S、±5V_A/+3V3_A、D_GND 太線）→ DRC 全体
6. C707–C710 極性の最終目視（＋＝3.3k／VCOM 側、ネット上は整合済）

### レビューで出た注意（2026-07-27・3視点）

- 47Ω と VCOM バイパスは **A701 ピン近傍が本命**（OPA 側に置かない）— 配置は寄せ済、配線で完成させる
- Disc φ5 は SOIC／電解と干渉しやすい → C705/C707 が残課題
- R701–R712 = **SMD 1206**、THT タクマンは **R713–716**（＋R719）のみ
- NT701/NT702 の **RefDes と役割は下表どおり（古い図と番号が逆だった）**

---

## 目的

- 自作 2ch スペアナ／相対比較用の物差し（L/R 各〜10 バンド程度で十分）
- 絶対校正済み計測器ではない

## 確定した電源アーキテクチャ

```
ADC_V_IN / ADC_GND_IN (PD)
  ├─ U704 BP5293-50 → +5V_D → Pico / LCD（デジ、D_GND）
  └─ U705 MBC2596 (4端子) → ~6.6–6.8V
         ├─ U706 LT1763-3.3 → +3V3_A （先行）
         └─ U707 LT1763-5   → +5V_A  （SHDN=+3V3_A）
±15V_A → OPA1656（U701–U703 等）
U708 TPS3808G33 / U709 TPS3808G50 → OD wire-AND → ADC_nRST（CT 開放 ≈20ms）
A_GND = 音声側アナログ GND（MCW03 二次側）
ADC_GND = U705 以降の ADC アナログ電源戻り
D_GND   = BP5293 戻り（Pico / LCD）
```

補足:

- **U710 XC8107AC20MR-G ロードスイッチ**（旧 Q701 AO3401A を置換, 2026-07-26）。`LCD_EN` **High=ON / Low・Hi-Z=OFF**（Active High）。R717 100k は CE プルダウン。**初号は常時 ON（GP8=High 固定）でも可**
- LCD 接続は Interface2 → 基板側 `PinHeader_1x15_P2.54mm_Vertical`
- **Pico2: VSYS=`+5V_D`、GND=`D_GND`**（`A_GND` には載せない）

## GND 方針（Option A: 非絶縁完成）

計測経路は PD 基準に寄せる。星点は二段。

```
OPA / Amp タップ              A701 / LDO
   A_GND / GND ── NT701 ── ADC_GND   （アナログ星点・A701 近傍）
                              │
                      MBC2596 IN-/OUT-（モジュール内共通）
                              │
   PD 入口 ◄── NT702 ── D_GND / LCD_GND   （デジタルは太く短く）
```

| Ref | Value（PCB） | 役割 | Footprint | おおよその位置 |
|---|---|---|---|---|
| **NT701** | `A_GND-ADC_GND` | アナログ星点（VCOM / OPA / ADC 基準） | `NetTie:NetTie-2_THT_Pad1.0mm` | A701 近傍（例: 421, 150） |
| **NT702** | `ADC_GND_IN-D_GND` | PD 入口での系統合流 | 同上 | 電源入口側（例: 669, 57） |

※ PCB 上 NT701 pad2 は現在グローバル `GND`。回路図の `A_GND` ラベルとの対応は配線時に再確認すること。

PCB では `D_GND` を太く短く、アナログ入力トレース・NT701 から離す。

**捨てるもの**: 計測モジュール上での MCW 二次側絶縁（相対スペアナ用途として許容）。  
**維持するもの**: 本番 Amp/EQ 再生経路の MCW 絶縁（計測タップ以外）。

---

## ChatGPT レビュー（2026-07-14）と対応

レビュー結論: **スペアナ構成としては成立。修正前は PCB 化 NOGO**（実装取り違え）。

### 必須だった指摘 → 対応状況

| # | 指摘 | 判定 | 状態 |
|---|---|---|---|
| 1 | U707/U706 の LDO 型番がレールと逆 | 妥当 | **済** |
| 2 | VCOM が 0.1µF シリーズで OPA＋へ | 妥当・致命 | **済** VCOM→2段目 OPA の＋直結、デカップは VCOM↔ADC_GND（C719/C720） |
| 3 | C707–C710 電解の極性（＋が音側） | 妥当の可能性大 | 要最終目視（＋は 3.3k／VCOM 側） |
| 4 | Q701 AO3401A が 3.3V GPIO で切れない | 既知・妥当 | **済** U710 XC8107（2026-07-26） |

### 追加指摘 → 対応状況

| 指摘 | 状態 |
|---|---|
| `A_GND`─NetTie─`ADC_GND` を 1 点明示 | **済** **NT701**（A701 近傍）※旧文書の NT702 表記は誤り |
| `ADC_GND_IN`─NetTie─`D_GND`（PD 入口） | **済** **NT702** |
| OPA 各電源に ±15V ─100nF─GND | **済** 入口 C701/C702 ＋ 各 OPA パッケージ |
| TPS3808・SV VDD・FMT 注記など | 概ね済／FMT 注記は残 |

### ERC

- MeasurementADC まわり: **ユーザー確認で ERC 違反なし**（2026-07-14）

---

## 終わっていること（要約）

- [x] MeasurementADC 階層を AudioCase に統合
- [x] 電源ツリー・TPS3808・LCD Interface2・VCOM 直結修正
- [x] GND 星点 NT701 / NT702 ＋ FP 割当
- [x] U710 XC8107 置換・注記整理
- [x] MBC2596 / ADC1804 実測 FP、手持ち抵抗・Disc FP 割当
- [x] OPA×3＋入力ブロックの PCB 配置（A701 側へ 47Ω・VCOM bypass 寄せ）
- [x] VCOML/R・VIN± の幹線を引き始め（WIP コミット済）

---

## 終わっていないこと

### PCB（優先）

- [ ] C705↔C707 ボディ干渉の解消
- [ ] VCOM / VIN / ADC_GND をパッドまで接続し DRC 未接続を消す
- [ ] MCLK・I2S・アナログ/デジタル電源・D_GND 太線
- [ ] DRC 全体クリーン（直近 WIP 時点で未接続多数は想定内）
- [ ] C707–C710 極性の最終確認
- [ ] U701 Reference シルク位置・電解「+」シルク（任意だが実装向き）

### レビュー残・仕上げ

- [ ] ジャンパ注記に `FMT1=L FMT0=H`（24bit I²S）を追記

### 検証・ソフト

- [ ] フルスケール／LCD ON/OFF ノイズ比較
- [ ] Pico ファーム（I2S・FFT・10バンド表示・タッチ UI）

---

## 主要ファイル

| ファイル | 役割 |
|---|---|
| `MeasurementADC1804_Module.kicad_sch` | 計測モジュール回路図 |
| `AudioCase.kicad_sch` / `AudioCase.kicad_pcb` | 親 |
| `MeasurementADC1804.kicad_sym` | ADC1804_F + OPA1656 |
| `MeasurementADC_Extras.kicad_sym` | LT1763 / MBC2596 / ASFL1 / LCD / TPS3808… |
| `Library.pretty/` | カスタム FP |
| `sym-lib-table` / `fp-lib-table` | ライブラリ登録 |

参考: [共立 ADC1804_F](https://www.kyohritsu.com/eclib/DIGIT/KIT/adc1804f.pdf) / [TPS3808](https://www.ti.com/lit/ds/symlink/tps3808.pdf)

発注・在庫: [`MeasurementADC_ORDER.md`](MeasurementADC_ORDER.md)

### MBC2596-01 実装メモ（2026-07-23）

- 外形 **43×21mm**。四隅 I/O（上面: 左上 IN+ / 右上 OUT+ / 左下 IN- / 右下 OUT-）。
- パッド中心 = **各辺から 3.5mm** → ピッチ **36.0 × 14.0mm**。
- モジュール穴 ≈ **φ1.3mm**。基板側ドリル **1.0mm**。
- FP: `Library:MBC2596-01_TAEJIN_43x21mm`
- 出力は **6.6–6.8V** にトリマ調整（LT1763 前段）。

### KiCad / MCP（作業環境メモ）

- プロジェクト dir: `Audio/`
- macOS では native `kicad-cli`、KiCad API 有効時は MCP（`kicad-mcp-pro`）利用可
- 古い `~AudioCase.kicad_pcb.lck` が残ると編集阻害 → 実プロセス無しなら削除可
