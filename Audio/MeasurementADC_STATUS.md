# MeasurementADC 進捗メモ

最終更新: **2026-08-24**

Amp 調整用の基準計測モジュール（OPA1656 + 共立 ADC1804_F / PCM1804 + Pico2 + WAVESHARE-29318）。

ブリングアップの詳細ログは `MeasurementADC_BRINGUP.md`。ファームは `measurement_fw/`。  
**いまの実機ノイズ切り分け**は `MeasurementADC_ZT703S_NOISE.md`（ZT-703S 2ch）。

---

## いまの実機状態

| 項目 | 状態 |
|---|---|
| PCM1804 | 稼働（SCKI 12.288 MHz / LRCK 48 kHz / BCK 3.072 MHz） |
| アナログ FE | J703 ±15V 通電済み。開放時の 1196 Hz 過負荷は解消 |
| 残差 | 約 1175 Hz 系の弱い混入（実用上は許容）。**ZT-703S で電源／VCOM／GND を計測中** |
| 計測機材 | ZT-703S ＋プローブ 2 本 到着済み（2026-08-24） |
| LCD | ST7796S、MADCTL `0xE8`、480×320。バックライトは GP8=`LCD_EN` |
| タッチ | FT6336U（I2C1 GP10/11）。下端メニューでレンジ／L+R／色／ピーク |
| スペアナ FW | 10 バンド（低域 IIR）＋棒表示。DMA と FFT を重ねて約 18–20 fps |
| 接続 | **Amp → スペアナ**。Controll 2 段は外している。EQ は今号では使わない |

### 初号の応急配線（実機は残置。回路図 rev 0.4 で解消済み）

| 箇所 | 内容 | 回路図 rev 0.4 |
|---|---|---|
| U710 1番 | リフト（RESET 出力 L 固定のため） | U710 廃止。U709 を TPS3307-33D 1 個に置換 |
| Y701 ASFL | 初号 FP 誤りのため空中配線（発振確認済み） | FP は `ef9d6d4` で修正済み。PCB 側の銅箔直しが残り |
| LCD SCK/MOSI | ヘッダ GP3/4 ではなく **GP18/GP19（SPI0）へ飛ばし** | GP18/GP19 に正規配線。GP3/GP4 は NC |
| GP9 → CN3F-1 | SCKI センス専用。**駆動禁止** | `MCLK_SENSE` として R720 1k 経由で `ADC_MCLK` へ |
| GP15 → `ADC_nRST` | オープンドレイン制御（H は駆動しない） | GP15=`ADC_nMR`（TPS3307 の ~MR）。`~RESET` は PP で `ADC_nRST` へ |
| （新規） | USB 挿すと `+5V_D` へ逆流 | D701 SOD-123 ショットキ `+5V_D`→VSYS で阻止 |

---

## 次の作業（優先順）

0. **ZT-703S で 1175 Hz 残差を計測** ← **いまここ**（手順: `MeasurementADC_ZT703S_NOISE.md`）
   - A1 1回目: 50 ms/div・40 mV/div で ±15 に約 40 mVpp の帯。1175 Hz は未分解
   - A1 2回目（GND 変更）: 1 V/div で 2〜3 Vpp・1 kHz 同位相 → **ループ拾い。不採用**
   - A1 4回目: 20 mV / 200 µs で帯が画面を埋める → **HF スイッチング。1175 Hz は未分解**
   - A1 6回目: 10 µs でも帯、1 ms で 1175 Hz 包絡なし。J703 は **100–250 mVpp の HF**。仮説1（1.17 kHz が ±15 に大きい）はオシロでは非支持
   - A2 1回目: どちらも CH1。VCOMR/L とも約 250 mVpp。**GND は J703 0V** なので星点間 HF が乗っている
   - A2-local: CH2 GND を C719 → 青約 100 mVpp、黄（J703 GND）約 250 mVpp。2ch GND 共通なので J703–C719 が短絡しうる
   - A2-local 2: 黄が細く青が太い。**青先端は未接続（アンテナ拾い）。無視**
   - A2-local 3: **CH1 のみ** VCOMR×C719 でも 150–250 mVpp HF。局所 GND では消えず
   - A2-cap: C719 両端でも 100–150 mVpp。配線ループだけでは非説明
   - 短絡テスト: **帯消滅。** 測定有効。VCOM×C719 の 100–150 mVpp は実電圧
   - 再現確認: C719 両端で帯復帰 → **VCOM HF 実電圧 確定**
   - 任意: 10–20 µs で周期 / A4 星点間 / スペアナで 1175 Hz 再記録
1. ~~**MeasurementADC 次号 回路図**~~ → **完了（rev 0.4, 2026-08-20）**
   - 追加部品: D701（RB160M-30 / SOD-123）、R720 1k、TP701、U709=TPS3307-33D（SO-8）
   - 廃止: U710 / R721 / R722（TPS3808 対）。C743 100nF・C744 10nF は U709 の
     `+3V3_A` デカップとして残置（C745 は使わない）
   - ERC の error は `A702 pin39 VSYS: Input Power pin not driven` のみ
     （D701 直列のため。この図は元から PWR_FLAG を使っていない）
   - ネットリストで確認済み: `VSYS` と `+5V_D` は別ネット、`LCD_SCK`=GP18 / `LCD_MOSI`=GP19、
     `ADC_nRST`=U709.~RESET + R719 + A701、`ADC_nMR`=GP15、`MCLK_SENSE`=GP9、GP3/GP4 は NC
   - **U709 の VDD が `~MR` に短絡していたのを修正**（VDD→`+3V3_A`）。
     短絡したままだと監視 IC が動かず、GP15 を L に引くと IC の電源ごと落ちる
   - 電源レールはローカルラベルのまま。U705→U706/U707 までは線で追えるが、その先の分配順は基板設計時の課題
2. **MeasurementADC 次号 PCB**（回路図に追従。計測結果で星点／電源を反映）
   - ASFL FP の GND/VDD を銅箔へ反映
   - LCD SCK/MOSI を GP18/GP19 のパターンへ
   - D701・R720・C745・TP701・TPS3307-33D（SO-8）の配置。旧 G33/G50 ランドは削除
   - 分割 Gerber `06_measurement_adc` 再生成
3. **親シート**にボリューム＋手前端子台（L/R/`A_GND`）とタップ注記
4. **箱内配線方針の図面化**（下記）とケース編成

---

## AudioCase 箱内配線方針（合意）

```text
PD(+15/PD_GND) ──直──► Power / Controll×2 / 計測デジ入口のみ

Power MCW03 二次
  ├─ A_GND ──分配器並列──► Amp×10 / 計測 A_GND / 端子台 0V
  └─ ±15  ──分配器──────► Controll AMP_PWR_IN / 計測 ±15V_A
                              └─(リレー)──► 選択中の Amp だけ

入力 L/R ──分配──►【ボリューム手前端子台】──► ボリューム ──► Controll ──► Amp
                      ├─ スペアナ（ハイZ）
                      └─ HP バッファ（ハイZ・将来）
```

- Controll 2 段＋Amp 10 枚（2 段×5、5 cm 樹脂スペーサ）を想定
- Controll／Amp の中身は回路図に複製しない。ボリュームと端子台は親シートへ追加する
- EQ は一旦諦め方向
- 専用ヘッドフォンアンプ基板は未製（ゲイン 1 倍バッファで足りる、という整理）

---

## 発注・分割 Gerber

```bash
cd Audio
python3 scripts/regenerate_split_gerbers.py --only 06_measurement_adc
```

- `split/AudioCase_6_measurement_adc.kicad_pcb`
- `split/Gerber/06_measurement_adc.zip`
- 外形 Edge.Cuts: `(339.87, 85.32)–(522.47, 169.02)` mm（約 183×84 mm）

---

## 回路図の電源表記（2026-08-20 時点）

電源レールはすべてローカルラベル（パワーシンボルは未使用）。
U705→U706/U707 までは線で追えるが、その先はラベルで飛ぶので分配順は読み取れない。
基板の電源レーンを引くときの課題として残っている。

一度パワーシンボル化とアナログ分配バスの明示配線を試したが、rev 0.4 に巻き戻した。
再挑戦する場合は `scripts/make_power_symbols.py` と `scripts/labels_to_power.py` を使う。

ネット構成は 235 ネット / 808 ピン。ERC の error は VSYS のダイオード直列のみ。

---

## 確定方針（要約）

- GND 案A（非絶縁）: 板上で `A_GND↔ADC_GND` / `ADC_GND_IN↔D_GND`
- Pico: VSYS は D701 ショットキ経由で `+5V_D` から。VBUS(pin40) は NC、GND=`D_GND`
  - USB だけ挿すと Pico は動くが LCD は消える（`+5V_D` へは逆流しない）
- LCD: U708 XC8107、`LCD_EN`=GP8（Active High）。SPI は SPI0（GP18/GP19）
- 監視 IC: U709=TPS3307-33D（SO-8）。SENSE1=`+5V_A`（4.55 V）、SENSE2/SENSE3/VDD=`+3V3_A`、
  `~RESET` PP → `ADC_nRST`+R719、GP15 OD → `~MR`（H は駆動しない）。RESET ピンは NC
- VCOM: ADC → 2 段目 OPA の＋、デカップは `VCOM↔ADC_GND`
- 電源デジの一括オートルートは再禁止

---

## 主要ファイル

| ファイル | 役割 |
|---|---|
| `MeasurementADC1804_Module.kicad_sch` | 計測モジュール回路図 |
| `AudioCase.kicad_pcb` / `.kicad_sch` | 親 PCB・階層シート |
| `MeasurementADC_ORDER.md` | 発注・在庫メモ |
| `MeasurementADC_BRINGUP.md` | 初号ブリングアップ記録（履歴） |
| `MeasurementADC_ZT703S_NOISE.md` | ZT-703S 2ch による 1175 Hz 残差の計測手順・結果欄 |
| `measurement_fw/` | Pico2 MicroPython（I2S / FFT / LCD スペアナ） |
| `scripts/regenerate_split_gerbers.py` | 分割 Gerber |
| `scripts/netcmp.py` | 回路図編集の前後でネット構成を照合 |
| `scripts/make_power_symbols.py` | 電源レール用パワーシンボルの生成（現在未使用） |
| `scripts/labels_to_power.py` | 電源ラベル → パワーシンボル置換（現在未使用） |
| `../Control/` | Controll 用ファーム（親／子） |
