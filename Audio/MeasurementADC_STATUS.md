# MeasurementADC 進捗メモ

最終更新: **2026-07-28**（ムラタ RDE FP 実寸化。壊れた自動配線は破棄済み）

Amp 調整用の基準計測モジュール（OPA1656 + 共立 ADC1804_F / PCM1804 + Pico2 + WAVESHARE LCD）。

---

## 他エージェントへの引き継ぎ（2026-07-28）

### いまどこまでか（一言）

VCOM/VIN・OPA ローカルは導通済みの WIP ベース（`ab554d5` 系）。**ムラタ RDE（100nF/10nF）の FP を実寸に差し替え済み。**  
自動投入した電源デジ幹線は品質が悪く **破棄**（`ab554d5` に戻したうえで RDE のみ載せ直し）。次は ADC_GND 延長とデジ配線を人手／慎重に。

### 触るファイル

| ファイル | 役割 |
|---|---|
| `Audio/AudioCase.kicad_pcb` | **主戦場**（親 PCB） |
| `Audio/MeasurementADC1804_Module.kicad_sch` | 計測モジュール回路図 |
| `Audio/Library.pretty/C_Murata_RDE_L4.0mm_W3.5mm_T2.5mm_P5.00mm.kicad_mod` | RDE 実寸 FP |
| `Audio/MeasurementADC_ORDER.md` | 発注・在庫・FP メモ |
| `Audio/route_preview_opamp_adc.png` | OPA→ADC 配線プレビュー（参考） |
| 本ファイル | 方針・残タスク |

### PCB / FP スナップショット（2026-07-28）

**ゾーン（維持）**

```
OPA/音声: 〜x346–423 → ADCフロント: 〜x412–544 → 電源デジ: 〜x560–684
```

| 項目 | 状態 |
|---|---|
| `VINL±` / `VINR±` | **完了**（R713–716↔A701、並走ピッチ≈5mm） |
| `VCOML` / `VCOMR` | **完了**（U702/U703 pin3/5 ↔ C719/C720 ↔ A701） |
| OPA 出力→47Ω | **完了** |
| `AUDIO_L/R_IN`・`AMP_V±` | OPA 島内は繋がっている。基板またぎ未接続は想定どおり |
| `ADC_GND` ベタ | `(420.5,100)–(562,178)`。**x>562 の LDO 群は未接続** |
| GND ベタ | OPA 周りは未完（パスコン GND はベタ待ち） |

**ムラタ RDE FP（2026-07-28）**

- 発注品: `RDER71H104K0K1H03B`（100nF）/ `RDER71H103K0K1H03B`（10nF）
- 実寸: **L4.0 × W3.5 × T2.5 mm max**、F=5.0±0.8mm（丸 Disc φ5 ではない）
- 新 FP: `Library:C_Murata_RDE_L4.0mm_W3.5mm_T2.5mm_P5.00mm`（パッド 0/5mm は旧 Disc と互換）
- 適用: **C701 C702 C705 C706 C711 C712 C717 C718 C719 C720 C722 C724 C725 C728 C730 C731 C735 C736 C737 C738**（20個）

**C705 ↔ C707**

- 旧 Disc φ5 FP だとボディ重なりに見えたが、**実部品＋画面上は約 2mm 空いている**（FP 過大が主因）
- C707–C710: 回路 `10uF 25V` / FP `CP_Radial_D5.0mm_P2.00mm`。手持ち候補はルビコン PX 10µF50V（φ5/P2）。ORDER 上 PX は C703/C704 向け表記で、カップリング4本への明示割当は薄い
- **無理に離す優先度は下げた**

**やってはいけないこと（教訓）**

- MeasurementADC へ電源デジの Manhattan 幹線を一括自動投入 → 短絡・交差・マスク橋が大量発生。破棄済み

**VCOM の正しい理解（取り違え注意）**

- VCOM は **ADC（A701）が出す基準** → 2段目 OPA の **＋入力へ入れる**
- U702: pin3/5 = `VCOML` → A701 pad2（＋ C719）
- U703: pin3/5 = `VCOMR` → A701 pad5（＋ C720）
- U701 の pin3/5 は **`GND`**。OPA 出力は **VIN±**（R713–716）

**既知のクリアランス（SOIC 近傍）**

SOIC-8 は隣接パッド間 ≈0.67mm。0.5mm 幅＋0.2mm クリアランスは物理的に通らない区間あり → **0.25mm ネックダウン**またはパッド端から回す。

### すぐやる順（PCB）

1. **`ADC_GND` ベタ延長**（東へ LDO 群を載せる。必要なら西≈404 まで）
2. 電源デジ幹線（`+5V_D` / `+3V3_A` / `+5V_A` / `D_GND`、続けて MCLK/I2S）— **短く・層分け・既存配線を踏まない**
3. SOIC 近傍のクリアランス詰め（必要区間のみ 0.25mm）
4. C707–C710 極性の最終目視（＋＝3.3k／VCOM 側）
5. DRC（MeasurementADC 領域）で short/crossing を潰す

### レビュー注意（継続）

- 47Ω・VCOM bypass は A701 近傍（寄せ済）
- R701–R712 = SMD 1206、THT タクマンは R713–716（＋R719）
- NT701 = A_GND/GND↔ADC_GND、NT702 = ADC_GND_IN↔D_GND（旧文書の番号逆に注意）

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
- [x] VCOML/R・VIN± 導通（WIP）
- [x] ムラタ RDE（100nF/10nF×20）FP 実寸化

---

## 終わっていないこと

### PCB（優先）

- [x] ムラタ RDE FP を実寸に更新（Disc φ5 → `C_Murata_RDE_…_P5.00mm`）
- [x] VCOM / VIN をパッドまで接続（WIP 時点）
- [ ] `ADC_GND` ベタ延長（LDO 群）と OPA 側 GND ベタ
- [ ] MCLK・I2S・アナログ/デジタル電源・D_GND 太線（自動一括配線は禁止／破棄済）
- [ ] SOIC 近傍クリアランス（必要区間 0.25mm）
- [ ] DRC 全体クリーン（基板またぎ未接続は想定内）
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
