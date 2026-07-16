# MeasurementADC 進捗メモ

最終更新: 2026-07-16（GND 星点 NT702・注記・FP 反映）

Amp 調整用の基準計測モジュール（OPA1656 + 共立 ADC1804_F / PCM1804 + Pico2 + WAVESHARE LCD）。

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

- 高精度計測時は LCD OFF 想定（Q701）。3.3V GPIO では PMOS 切れ切りが甘い → 要改善または常時 ON で相対測定
- LCD 接続は Interface2（GH 付属ケーブルのメス端）→ 基板側 `PinHeader_1x15_P2.54mm_Vertical`
- **Pico2: VSYS=`+5V_D`、GND=`D_GND`**（`A_GND` には載せない）

## GND 方針（Option A: 非絶縁完成）

MCW03 による音声側ガルバニック絶縁は、**計測経路では PD 基準に寄せる**方針で確定。星点は二段。

```
OPA / Amp タップ          A701 / LDO
   A_GND ── NT702 ── ADC_GND     （アナログ星点・A701 近傍）
                      │
              MBC2596 IN-/OUT-（実モジュール内共通）
                      │
   PD 入口 ◄── NT701 ── D_GND / LCD_GND   （デジタルは太く短く）
```

| Ref | Value | 役割 | Footprint |
|---|---|---|---|
| **NT702** | `A_GND-ADC_GND` | アナログ星点（VCOM / OPA / ADC 基準を揃える） | `NetTie:NetTie-2_THT_Pad1.0mm` |
| **NT701** | `ADC_GND_IN-D_GND` | PD 入口での系統合流 | 同上 |

PCB では `D_GND` を太く短く、アナログ入力トレース・NT702 から離す。

**捨てるもの**: 計測モジュール上での MCW 二次側絶縁（相対スペアナ用途として許容）。  
**維持するもの**: 本番 Amp/EQ 再生経路の MCW 絶縁（計測タップ以外）。

---

## ChatGPT レビュー（2026-07-14）と対応

レビュー結論: **スペアナ構成としては成立。修正前は PCB 化 NOGO**（実装取り違え）。

### 必須だった指摘 → 対応状況

| # | 指摘 | 判定 | 状態 |
|---|---|---|---|
| 1 | U707/U706 の LDO 型番がレールと逆 | 妥当 | **済** U706=`LT1763-3.3`→`+3V3_A` / U707=`LT1763-5`→`+5V_A`（SHDN=`+3V3_A`） |
| 2 | VCOM が 0.1µF シリーズで OPA＋へ（DC経路なし） | 妥当・致命 | **済** VCOM→2段目 OPA の＋直結、デカップは VCOM↔`A_GND` |
| 3 | C707–C710 電解の極性（＋が音側） | 妥当の可能性大 | 要最終目視（＋は 3.3k／VCOM 側） |
| 4 | Q701 AO3401A が 3.3V GPIO で切れない | 既知・妥当 | **未**（常時 ON 試験可／ロード SW 置換は任意） |

### 追加指摘 → 対応状況

| 指摘 | 状態 |
|---|---|
| `A_GND`─NetTie─`ADC_GND` を 1 点明示 | **済** NT702（A701 近傍） |
| `ADC_GND_IN`─NetTie─`D_GND`（PD 入口） | **済** NT701 |
| OPA 各電源に `±15V_A`─100nF─`A_GND` | **済** 入口 C701/C702 ＋ 各 OPA パッケージ |
| TPS3808 `~RESET` を Open Collector、G33/G50 明記、CT≈20ms | **済**（プロジェクト用シンボル、CT 開放） |
| SV VDD に 0.1µF | **済**（VDD–GND 直近） |
| 監視 IC の VDD をレールから分離 | **任意**（初号スキップ可） |
| ジャンパに FMT（24bit I²S）明記 | 推奨（シート注記拡充） |

### レビューが「できている」とした点（維持）

- ADC1804 → Pico I²S（DATA/BCK/LRCK、GP0–2）
- ASFL1 12.288MHz ＋シリーズ R、ADC マスタ 48k/256fs
- TPS3808 OD wire-AND ＋ R53 10k、CT 開放
- LCD SPI／タッチ I²C、BP5293→Pico VSYS

### ERC

- MeasurementADC まわり: **ユーザー確認で ERC 違反なし**（2026-07-14）

---

## 終わっていること（要約）

- [x] MeasurementADC 階層を AudioCase に統合
- [x] 電源ツリー（MBC2596 → LT1763×2、BP5293→デジ）
- [x] `TPS3808G33DBVR` / `TPS3808G50DBVR`（`~RESET`=open_collector）
- [x] WAVESHARE-29318 = Interface2・15pin ヘッダ FP
- [x] VCOM 直結＋デカップ修正
- [x] OPA ±15V 100nF（共通＋各パッケージ）
- [x] GND 星点 NT701 / NT702 ＋ FP 割当
- [x] Pico GND=`D_GND` 注記修正
- [x] ERC クリア（ユーザー確認）

---

## 終わっていないこと

### レビュー残・仕上げ

- [ ] C707–C710 極性の最終確認（＋＝3.3k／VCOM 側）
- [ ] Q701: 確実 OFF（TPS22919 等）または相対測定は常時 ON
- [ ] ジャンパ注記に `FMT1=L FMT0=H`（24bit I²S）を追記
- [ ] 古い注記の整理（POWER/DIGITAL ブロックの旧 Ref・CT 0.57s 表記など）

### フットプリント・基板

- [ ] `ADC1804_F_MODULE` FP
- [ ] `MBC2596-01` FP（ピンヘッダ想定）
- [ ] 残パッシブ FP 割当
- [ ] PCB 配置・配線・DRC（D_GND 太線・NT702 近傍レイアウト）

### 検証・ソフト

- [ ] フルスケール／LCD ON/OFF ノイズ比較
- [ ] Pico ファーム（I2S・FFT・10バンド表示・タッチ UI）

---

## 主要ファイル

| ファイル | 役割 |
|---|---|
| `MeasurementADC1804_Module.kicad_sch` | 計測モジュール回路図 |
| `AudioCase.kicad_sch` | 親（階層シート） |
| `MeasurementADC1804.kicad_sym` | ADC1804_F + OPA1656 |
| `MeasurementADC_Extras.kicad_sym` | LT1763 / MBC2596 / ASFL1 / LCD / TPS3808G33/G50 |
| `Library.pretty/` | カスタム FP |
| `sym-lib-table` / `fp-lib-table` | ライブラリ登録 |

参考: [共立 ADC1804_F](https://www.kyohritsu.com/eclib/DIGIT/KIT/adc1804f.pdf) / [TPS3808](https://www.ti.com/lit/ds/symlink/tps3808.pdf)

発注・在庫: [`MeasurementADC_ORDER.md`](MeasurementADC_ORDER.md)（秋月 / 共立エレショップ・2026-07-16 調査）

---

## 次にやるとよい順

1. [`MeasurementADC_ORDER.md`](MeasurementADC_ORDER.md) に沿って ADC1804 / MBC2596 / OPA1656 を先行発注（FP 計測用）
2. C707–C710 極性確認
3. Q701 方針決定（置換 or 常時 ON）
4. 残 FP 割当 → PCB（D_GND 太線・星点配置）
5. Pico ファーム（簡易スペアナ）
