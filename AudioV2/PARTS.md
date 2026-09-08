# AudioV2 品番（回路から決めた第一候補）

**目的:** 回路が要求する電気・機械条件から、まだ空欄だった型番を埋める。在庫は変動するので **機能等価の代替** を併記する。

**実装の型（既存 `Audio/` と同じ）:** RV / SW_DEST / ENC / PWR SW は **パネル実装**。基板はヘッダ＋リード。RK27 を Control PCB に直付けしない。

参照: [DECISIONS.md](DECISIONS.md) §0・§3・§9・§10、[CIRCUIT_DESIGN.md](CIRCUIT_DESIGN.md)、[DEST_SENSE_LADDER.md](DEST_SENSE_LADDER.md)。

> **この文書の読み方 — どこが生成で、どこが手書きか**
>
> `<!-- BEGIN GENERATED: ... -->` 〜 `<!-- END GENERATED: ... -->` で囲まれたブロックは
> **回路図から自動生成**したもの（現在は §4.1 の AmpBank 部品表）。
> **手で編集しても次の再生成で消える。** 直すときは KiCad の回路図側を直して再生成する。
>
> それ以外はすべて**手書きで、こちらが正**。調達先・代替品・選定理由・C&K の現物端子対応・
> パネル/箱配線など、**回路図から導出できない情報**を置く場所。方針は
> [SOURCE_OF_TRUTH.md](../SOURCE_OF_TRUTH.md)。
>
> ```bash
> python3 AudioV2/scripts/gen_parts_bom.py          # 再生成して埋め込み直す
> python3 AudioV2/scripts/gen_parts_bom.py --check  # 実図とズレていれば非ゼロ終了（検査のみ）
> ```

---

## 0. 回路が課す制約（品番を決める前に）

| ブロック | 電気 | 機械 |
|---|---|---|
| **RV_HP / RV_LINE** | A カーブ 50 kΩ デュアル。Amp 後 ~7 Vrms → 素子 0.05 W で十分（7²/50k ≈ 1 mW） | **目立つノブ**。6 ピン（1/3=A, 4/6=B, 2/5=wiper）。基板はヘッダ |
| **SW_DEST** | 3 極 × ON-OFF-ON。音声 L/R + センス 1 極。電流 ≈ 7 V / 50 kΩ = **0.14 mA**（信号級で足りる） | パネル φ6.35 mm 級。はんだラグ → ヘッダ |
| **PWR SW** | DC-DC 一次 ≈ **1 A @ 12 V**（`REC10K` は 10 W / η 87 % → 11.5 W ÷ 12 V）+ パネル LED ~10–15 mA | 3 A 以上。信号用ミニスイッチは不可。**旧 `DKMW20`（20 W）時代は約 2 A だったので余裕が増えた** |
| **ENC×3** | A/B/SW、Pico 内部プルアップ | EC11、押し SW、D カット、固定足東西 |
| **DEST LED** | GP14/15、3.3 V、直列 1 kΩ | パネル 3–5 mm |
| **12 V LED** | SW 後 12 V、内蔵抵抗 ~10–15 mA | パネル 5 mm |
| **PT2314E** | VDD 4–10 V、I²C、28 pin | **SOP-28 300 mil**（表面実装。DIP 版は無い） |
| **AZ850** | コイルは**母板の `BP5293-50` が作る +5 V**。娘基板へは**スタッキングヘッダ経由**で渡る（旧: ControlPanel から RelayBoard へ 5P 配線） | 2コイル・ラッチDPDT。audio/power を同時駆動 |
| **OLED 制御** | I²C 0x3C、128×64、3.3 V、**SSD1306 互換**（実機は SSD1309 可） | 4 線（VCC/GND/SCL/SDA）。パネル or ヘッダ |
| **LCD スペアナ** | SPI（ST7796S）+ I²C タッチ（FT6336U）、5 V 可 | Waveshare **29318**。計測盤のみ |

### 0a. 何を繋ぐか（**2026-09-06 確定。バッファの設計はここで決まる**）

**出力段の設計は「先に何を繋ぐか」で決まる**のに、それがどこにも書かれていなかった。ユーザー確定分:

| 出口 | 繋ぐもの | 公称仕様 | 出典 |
|---|---|---|---|
| **PHONE** | **Sennheiser HD 560S** | **120 Ω** / 110 dB SPL/V @1 kHz | メーカー公称（**二次情報**。データシート PDF ではない） |
| **PHONE** | **HyperX Cloud III** | **64 Ω** / 100 dB SPL/mW @1 kHz | 同上 |
| **LINE** | **IK Multimedia iLoud Micro Monitor** | RCA 不平衡 ＋ TRS 1/8" 平衡。**⚠ 入力インピーダンスと入力感度はメーカーが公表していない**（仕様ページは出力特性のみ） | メーカー仕様ページ |

**⚠ 32 Ω 級は無い。** 「32 Ω の低能率を駆動する」という前提で部品を選ばないこと
（v1 の `NJM4556A` 70 mA 級はその前提で選ばれたと思われる）。

**⚠ `iLoud` の入力インピーダンスが不明なのは、ライン出力バッファの要否に直結する。**
`A50k` ポットのワイパーは電気的中点で `Zout` 最大 12.5 kΩ。負荷による追加損失は
**10 kΩ で −7.0 dB / 20 kΩ で −4.2 dB / 47 kΩ で −2.1 dB**（`600 Ω` なら −26.8 dB）。
**アクティブモニタの RCA は 10〜47 kΩ 級が普通**なので、**この範囲なら「損失」ではなく
「A カーブが崩れてつまみの位置が変わる」だけ**で、上に 10 dB 以上の余裕がある以上、実害は小さい。
**測定用途で「つまみを動かすと 20 kHz の応答が動く」ことを嫌うなら、バッファを入れる理由になる。**

---

---

## 0b. ベンダのデータを読むときの罠（実際に踏んだもの）

価格・在庫は変動するので**スナップショットは残さない**。代わりに読み方を残す。
すべて 2026-09-02 の DC-DC 選定で実際に踏んだもので、根拠と実数は
[AGENT_HANDOFF.md](AGENT_HANDOFF.md) §2.10 にある。

| 罠 | どうする |
|---|---|
| **通貨単位** | §2.10 の価格表が **¥ と $ を取り違えていた**（`¥9.98` と書かれた値の実体は **¥1,581**）。桁が3つ違っても表の中では気づかない。**通貨を明示していない数字を比較に使わない** |
| **MOQ（最小注文数量）** | `UnitPrice` だけで並べると**順位を間違える**。MOQ 19（チューブ）の品は単価最安でも実際に払うのは 19 個分。**「最低購入額 = 単価 × MOQ」で並べる**。API では `ProductVariations[].MinimumOrderQuantity` |
| **包装で品番が分かれる** | 同じ石でもカットテープ / テープ&リール / Digi-Reel で別品番になり、**テープ&リールは MOQ 3000・在庫0**、Digi-Reel は別途リール手数料。**買うのはカットテープ（`...CT-ND`）** |
| **入手性フィールド** | **DigiKey API の入手性フィールドは信用できない**（`AM10TW` で判明。正規ルートから消えているのに在庫ありに見えた）。在庫の判断は実ページで確認する。**⚠ ただし実ページが見られない環境では下の「販売元」を使う** |
| **販売元（Marketplace か直販か）** | **`ProductUrl` のスラグが `Manufacturer.Name` と食い違ったら Marketplace 出品**。DigiKey の商品 URL は `/products/detail/<メーカのスラグ>/<型番>/<id>` なので、両者は普通一致する。**2026-09-05 に 1023 件で試したら不一致は `aimtec → dcomponents` の 25 件だけで、うち 22 件が `BackOrderNotAllowed=True`。** 記録にある `AM10TW` の在庫誤認はこれ —— **在庫を持っていたのは DigiKey ではなく出品者**だった。`MarketPlace` フィールド自体は `None` を返すので役に立たない。**`www.digikey.com` が塞がっている環境でも、この判別は API だけでできる** |
| **`ProductStatus`** | **「新規設計向けに不適合」(NFND) は候補から即落とす。** 性能で比べる前に見ること。2026-09-05 の再探索では `URA2412ZP-10WR3`（Mornsun）と `PYBE10-Q24-D12`（Bel）がこれで、**どちらも `NormallyStocking=False` かつ `BackOrderNotAllowed=True`**。データシートを読む手間ごと省ける |
| **属性 vs データシート** | DigiKey の属性が**データシートと矛盾する**ことがある（`REC10K` の絶縁は属性 3 kV / DS は **1.6 kVDC**）。**データシートを正とする** |
| **足切りは価格ではない** | DC-DC の決め手は価格ではなく **最大容量負荷 Cout** だった。**回路が課す制約（§0）で先に落とす**、価格で並べるのはその後 |

探索そのものは [`scripts/dcdc_survey.py`](scripts/dcdc_survey.py) / [`scripts/digikey_search.py`](scripts/digikey_search.py) で再実行できる。
**ライブ API を叩くので結果は当時と変わる** — 変わってよい。固定したいのは上の読み方だけ。

---

## 1. 表示デバイス（v1 実装あり・確定）

AudioV2 は **表示が 2 系統**。DECISIONS の「OLED×2」は言い方が粗い — 実体は次。

| 役割 | 部品 | v1 実装 | AudioV2 での置き場 |
|---|---|---|---|
| **操作 UI** | **2.42″ OLED 128×64 I²C** | `Control/ssd1306.py` + `main.py`（`WIDTH=128 HEIGHT=64`、addr 0x3C、I2C0 GP20/21） | **ControlPanel** |
| **スペアナ** | **Waveshare 3.5″ タッチ LCD 320×480** | `Audio/measurement_fw/`（`lcd.py` ST7796S / `touch.py` FT6336U） | **MeasurementADC（`Audio/` 流用）**。AudioV2 KiCad には載せない |

### 1.0a 制御 OLED — AliExpress 2.42″（SSD1309 / SSD1306 互換）

| | |
|---|---|
| 例リンク | [a.aliexpress.com/_c3yp3JiX](https://a.aliexpress.com/_c3yp3JiX) → item **4000002579405** |
| 解像度 | **128×64**（v1 ファームと一致。**128×32 / 0.91″ は不可**） |
| コントローラ | 表記は **SSD1309** が多い。コマンドは SSD1306 と同系 → **既存 `ssd1306.py` のまま** |
| 配線 | Controll J17 と同型: **GND / 3V3 / SCL / SDA** → Pico GP21 / GP20 |
| バス | I²C0 **400 kHz**（100 kHz だと 1 KB フレームがタイムアウト — `Control/README.md`） |
| 表示内容 | CH / DEST / Bass / Treble。**音量は出さない** |

**代替:** 同ピン配列の **0.96″ SSD1306 128×64 I²C**（4 ピン）。ソフト変更なし。パネル穴・見た目だけ変わる。

**KiCad 注意:** 素案の `Display_Graphic:SSD1306-128x64` は埋め込み元が **ER_OLEDM0.91（128×32）** になっている。ピンは 4 本で足りるが **FP・寸法は 2.42″ 用に差し替え**（当面は `PinHeader_1x04` + 注記で可）。

### 1.0b スペアナ LCD — Waveshare **29318**（スイッチサイエンス）

| | |
|---|---|
| 販売 | [スイッチサイエンス 10138](https://www.switch-science.com/products/10138) / メーカー SKU **29318** |
| 表示 | 3.5″ IPS **320×480**、ST7796S、**4 線 SPI** |
| タッチ | FT6336U、**I²C**（静電容量） |
| 接続 | GH1.25 15P 付属 → 基板側 **1×15 ピンヘッダ**（`Audio/MeasurementADC_Extras:WAVESHARE-29318`） |
| 電源 | 3.3 / 5 V（オンボード LDO・レベルシフタ）。計測盤では `LCD_EN` で VCC 切 |

AudioV2 では **計測 Pico 配下のまま**。操作 Pico の I²C0 / SPI には載せない（DECISIONS §6・独立計測）。

---

## 2. 今回決めた第一候補（未定だったパネル部品）

### 2.1 SW_DEST — **C&K 7303SYZQE**

| | |
|---|---|
| 機能 | **3PDT ON-OFF-ON**（中央オープン＝MUTE） |
| 端子 | はんだラグ、パネル 1/4-40（穴 **φ6.35 mm**） |
| 定格 | 5 A / 120 VAC — 音声 0.14 mA に対し余裕。銀接点（QE）で可 |
| 並び（DECISIONS） | **上 LINE / 中 MUTE / 下 PHONE** |
| KiCad | 論理は `SW_DP3T`（L/R）+ `SW_SP3T`（センス）。**1 個の現物** |

**C&K 端子 → AudioV2 ネット**（DS: Pos1=2-3/5-6/8-9、Pos3=2-1/5-4/8-7、COM=2/5/8）

取り付けで「下＝PHONE」になるよう、レバー下向きで Pos1 が PHONE 側端子に来る向きにする。

| 現物端子 | 役割 | 基板ヘッダ（音声 2×4 + センス 1×3） |
|---|---|---|
| 2 | L COM | SW601-3 `AMP_SEL_L` |
| 3 | L PHONE（Pos1） | SW601-1 → RV601 |
| 1 | L LINE（Pos3） | SW601-4 → RV602 |
| （L MUTE） | 開放 | SW601-2 NC |
| 5 | R COM | SW602-3 `AMP_SEL_R` |
| 6 | R PHONE | SW602-1 → RV601 |
| 4 | R LINE | SW602-4 → RV602 |
| 8 | センス COM | → DEST_ADC（GP26） |
| 9 | センス PHONE | → Rs=1 kΩ → GND |
| 7 | センス LINE | → Rs=1 kΩ → 3V3 |
| （センス MUTE） | 開放 | ラダー中点のまま |

**代替**

| 状況 | 型番 | 備考 |
|---|---|---|
| 7303 欠品 | **NKK S38** | 同じく 3PDT ON-OFF-ON。穴 **φ12.5 mm**・大きい。RS 流通 |
| ミニ 3PDT 全滅 | **C&K 7203SYZQE**（音声 DPDT）+ **7103SYZQE**（センス SPDT） | 穴 2 個。UX は劣るが両方とも流通が多い |
| NKK ミニ | M2033SSxxW01 | 機能は同じだが **一部 suffix が EOL**。在庫確認必須 |

4PDT（C&K 7403）は余 1 極を NC にして使ってよい（将来アース切等）。

### 2.2 RV_HP / RV_LINE — **Alps RK27112A00CF** ×2

| | |
|---|---|
| 機能 | **A（対数）50 kΩ デュアル**、カーボン、1 回転 |
| 外形 | RK27 **27 mm**、軸 φ6 × 20 mm、取付 M9 |
| 電力 | 0.05 W — 本回路の ~1 mW に対し十分 |
| ギャング誤差 | DS 目安 2 dB（-60〜0 dB）— ステレオ音量として実用 |
| 実装 | **パネル**。基板は 6P ヘッダ（`Device:R_Potentiometer_Dual` ピン番号のまま） |
| なぜ RK097 でないか | 現行 Audio は RK097 水平実装。AudioV2 は **ノブを主操作子**にするので 27 mm を第一にする |

**代替**

| 状況 | 内容 |
|---|---|
| RK27 欠品・高い | パネル用 **A50k デュアル**ならピン互換で可（台湾 Alpha RD901 系など）。カーブが **A** であること |
| 現行機と見た目を揃える | Alps **RK097 デュアル A50k**（水平ピン）。9 mm で「目立たない」。回路は同一 |
| A100k | 可（DECISIONS）。中点 Zout が上がるので **A50k 優先** |

RK097 のカタログ現役は 10 kΩ デュアルが多く、**A50k デュアルは RK27 の方が型番が取りやすい**。

### 2.3 その他・回路上まだ曖昧だったもの

| 用途 | 第一候補 | 理由 |
|---|---|---|
| **ENC×3** | 秋月 **EC11 系・押し SW 付き**（D カット、固定足東西） | DECISIONS どおり。PPR は CH/Bass/Treble では何周でも可。購入品の寸法で FP を切る |
| **操作 Pico** | **Raspberry Pi Pico 2**（RP2350、**W なし**、SC0915 相当） | Wi-Fi 不要。ヘッダ後付け可 |
| **OLED（制御）** | **2.42″ 128×64 I²C**（SSD1309、SSD1306 互換）— [AliExpress 例](https://a.aliexpress.com/_c3yp3JiX) / item `4000002579405` | v1 `Control/` と同じ。`WIDTH=128 HEIGHT=64`、addr **0x3C**、GP20/21。**0.96″ でも動くが、現行機は 2.42″** |
| **LCD（スペアナ）** | **Waveshare 29318**（スイッチサイエンス [10138](https://www.switch-science.com/products/10138)） | v1 `Audio/measurement_fw/`。ST7796S SPI + FT6336U I²C。**MeasurementADC 流用**（AudioV2 Control には載せない） |
| **PWR SW** | **C&K 7101SYZQE**（SPDT ON-ON、5 A、ラグ）を SPST として使用 | 12 V / **~1 A**（`REC10K` 10 W。旧 `DKMW20` 20 W では ~2 A）。5 A 品なので余裕は十分。ミニ信号 SW 禁止 |
| **12 V LED** | **12 V 内蔵抵抗付き 5 mm**（緑または青、~10 mA） | DECISIONS §9。素 LED なら 680 Ω–1 kΩ |
| **DEST LED×2** | 3 mm 通常 LED（Vf≈2 V）+ 既存 **1 kΩ** | 3.3 V で ~1.3 mA。暗ければ 330 Ω に落とす |
| **AZ850** | **AZ850P2-5**（秋月 118017） | コイル **5 V** / 125 Ω / ~40 mA。`TBD62083APG` + BP5293-50 と一致。**12 V コイルは使わない**。電源は母板の `BP5293-50` が `PD_12V_SW` から作る **`+5V_COIL`** で、帰路は専用の `GND_COIL`（`NT101` で1点結合）。娘基板側に 100 µF + 100 nF のローカルバイパスがあるので、パルスとフライバックは娘基板内で閉じる |
| **MCP23017** | **`MCP23017-E/SP`**（DIP-28） | JP A1/A0 で 0x20–0x23（最大4枚）。A2=0。UI 側は 0x22。**個数は回路図から導出できるので §4.1 の部品表を見る** |
| **DIP-28 ソケット** | **板バネ（dual-wipe）型**、28 pos / 行間隔 0.300"（7.62 mm） | 挿さるのは `MCP23017` だけ＝ I²C のデジタルなので接触抵抗も歪みも効かない。品番は発注時（[DECISIONS.md](DECISIONS.md)「DIP-28 ソケット」） |
| **リレードライバ** | **`TBD62083APG`**（DIP-18。`ULN2803` とピン互換） | **`ULN2803` は不採用**（D24）。ダーリントンの約 1 V 降下では 40 ℃ 超で `AZ850` の Must Operate を満たさない。DMOS なら 40 mA で 0.13 V。**1枚に2個要る**（5ch×2コイル=10本 > 8ch。D25 — 4ch/枚なら1個で済んだ分のコスト） |
| **PT2314E** | **PT2314E SOP-28 300 mil**（回路値 `PT2314E`） | 無印 DIP は入手不可。2026-09-07 に E へ確定（[DECISIONS.md](DECISIONS.md)「トーン」） |
| **+9 V LDO** | **ST `L7809CV`**（TO-220） | 入力は **+15 V**（`U202.1 → /+15V`）。PT2314 typ 30 mA → 散逸 **(15−9)×30 mA ≈ 0.18 W**。TO-220 なら放熱器なしで余裕。⚠ TI の `LM78xx` は廃番系なので**回路図の Value も `L7809CV` に揃えてある**（KiCad のシンボル名 `Regulator_Linear:LM7809_TO220` は 78xx 共通の型で、そのまま使える）。**⚠ 2026-09-05 に予備として `NJM7809FA`（Nisshinbo/JRC）を購入。これは `TO-220F`（フルモールド）で `L7809CV` の `TO-220` とは別パッケージ。** ピン配置は同じ（1=IN / 2=GND / 3=OUT）だが、**フットプリントは `TO-220F-3_Vertical` に差し替えが要る**。タブが絶縁されているのでシャーシへ直付けするなら絶縁ワッシャが不要という利点はある。散逸 0.18 W なので放熱はどちらでも問題にならない。**実装に使うと決めるまで回路図は `L7809CV` のまま置く** |
| **一次ヒューズ**（PD 入力〜DC-DC 間） | **5×20 mm `T1.6 A` スローブロー**（ガラス管＋ホルダ）**確定 2026-09-04** | 定常 0.96 A に対し 60 %。3 A で数秒・5 A で瞬時に切れる。旧 `T3.15 A` は PD ポートの供給能力（12 V/3〜5 A 級）の全域で切れず実質「保護なし」だった。突入は 47 µF ぶんで I²t ≈ 0.03 A²s、溶断 I²t の2桁下なので効かない。導出は [DECISIONS.md](DECISIONS.md) §8 |
| **各コンバータ手前のリセッタブル** | **PPTC** — `+5V_D` に **0.5 A** / `+5V_COIL` に **0.35 A** / `+9V` に **0.1 A**（I_hold）**確定 2026-09-04** | 立ち上げ中はプローブを当てるので自己復帰品にする（一発品だと外して交換になる）。**2026-09-06 に全枝が回路図へ入った**（最後まで残っていた `+9V` 枝 = D-f）。詳細と根拠は [DECISIONS.md](DECISIONS.md) §8 |
| **BP5293** | **BP5293-50**（秋月 111188） | 現行 Audio と同じ +5 V |
| **DC-DC** | **`REC10K-2415DAW/H2`**（Recom、±15 V / ±333 mA、1″×1″ 6-DIP） | **2026-09-02 に `DKMW20F-15` から変更**（[DECISIONS.md](DECISIONS.md) §8）。穴位置は旧品と同一で差し替え可。DigiKey `945-REC10K-2415DAW/H2-ND` |
| **PD 給電モジュール** | **ストロベリーリナックス `50224`**（CH224K。DS: [`datasheets/StrawberryLinux_CH224K_manual.pdf`](datasheets/StrawberryLinux_CH224K_manual.pdf)） | **外付けモジュールとして使う。** 板上に USB-C / CH224K チップは載せず、受けの端子（`PD module in`）で 12 V を受ける。**部品は当初と同じで、変わったのは実装形態だけ**（基板内蔵 → 外付け、2026-09-04 訂正）。12 V/15 V のジャンパはモジュール側 |
| **PD 供給元（AC アダプタ）** | **UGREEN 卓上急速充電器 200 W Type-C 6C2A 8ポート PPS** | 手持ちの実機。⚠ **多ポート充電器は総出力を分配する**ので、他ポートに何を挿すかでネゴシエートされるプロファイルが変わりうる。**12 V 固定が出るかは実機で確認する**（多ポート品は 5/9/15/20 V のみで 12 V を持たない機種がある）。出ない場合のフォールバックは **15 V 一本**（**⚠ 9 V を選んではいけない** —— `REC10K` の UVLO 起動閾値の上限が 9 V で、境界そのもの。2026-09-04 にデータシートで確認。[DECISIONS.md](DECISIONS.md)「PD 入力 — どの電圧で受けるか」）。**15 V で確定させるならこのパネル LED も直すこと**（12 V 品なので 30 % 過電流になる）。**実機はいま 15 V が入っている**（2026-09-04 実測） |
| **USB-C** | USB2.0 16P レセプタクル（KiCad `USB_C_Receptacle_USB2.0_16P`） | CC はモジュール側。基板は VBUS/GND が主 |
| **ラダー R** | 10 k / 10 k / 1 k **1%**（1206 可） | ±5% でも間隔は足りるが、初号は 1% |
| **J_I2C（旧 ControlPanel↔RelayBoard 5P。⚠ 両シートは解体済みで、基板間はヘッダのスタックへ変更。この行は v1 の実績の記録）** | **Phoenix Contact MKDS-1,5シリーズ**（5.08 mmピッチ、ネジ式）互換品または同一品。KiCad FP: `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-N-5.08_1xNN_P5.08mm_Horizontal`（Nはピン数、5Pなら`5`/`05`） | `Audio/Controll.kicad_sch`（v1の「リレー＋端子台＋ULN」原型）で13箇所使用実績あり。フェルール対応で、スター配線をControlPanel側1コネクタ＋箱内フェルール束ね/スプリッタで実現する方針（WIRING.md）と合う |

---

## 3. ピン・配線メモ（購入後に間違えないため）

```text
Amp 選択後 L/R
    → 7303 極1/極2 COM
         下 PHONE → RK27 (RV601) CW ← wiper → HP Buffer
         中 MUTE  → NC
         上 LINE  → RK27 (RV602) CW ← wiper → LINE OUT
    → 7303 極3 COM → ADC
         下 → Rs → GND     = PHONE
         上 → Rs → 3V3     = LINE
```

ポット: **CW（時計回りで音量大）= SW 側（HOT）**、CCW = `A_GND`、ワイパー = 出力。A カーブは CCW 側が急に落ちる。

---

## 4. 部品表と実装メモ（娘基板 5ch×2枚、§2.9）

### 4.1 部品表（回路図から自動生成）

> **1つ目の表が発注数の正。** 階層ルートの `AudioV2Case.kicad_sch` から取っているので、
> `AmpChannel` ×10 のインスタンス別参照上書き（ch2=8xx, ch3=9xx…）まで解決されている。
>
> **娘基板シートを単体で export してはいけない。** `AmpBankSwitch` / `AmpBankRelay` を
> ルートとして渡すと kicad-cli は上書きを解決できず、**1ch 分の値しか出ない**
> （解体前の `AmpBank.kicad_sch` でも同じだった）。2つ目の表は「1ch に何が要るか」を
> 見るためのテンプレートで、**発注数の根拠にはならない**。
>
> 1つ目の表の部品総数がネットリストの部品数より少ないのは、NetTie が BOM 対象外
> だから（差は NetTie の個数ぶん）。NetTie は基板上の銅箔で、買う部品ではない。
> KiCad 標準 `Device:NetTie_2` の既定も `in_bom=no`。

<!-- BEGIN GENERATED: case-bom -->
**AudioV2 全体部品表（母板 + 娘基板 + 計測 + 親）** — 下の表は `AudioV2/AudioV2Case.kicad_sch` から自動生成しています。
**手で編集しないでください**（次の再生成で消えます）。値・フットプリント・役割を直すときは KiCad の回路図側を直し、
`python3 AudioV2/scripts/gen_parts_bom.py` で再生成します。

行数 98 / 部品総数 385。

> `Refs` 列と `Value` / `Role` 列に**位置の対応はありません**。kicad-cli はグループ内の値を重複除去してアルファベット順に並べるため、「n 番目の参照 = n 番目の役割」とは読めません。

| Refs | Value | Footprint | Qty | Role |
|---|---|---|---|---|
| A1601 | ADC1804_F_MODULE | `Library:ADC1804_F_KYOHRITSU_56x33mm` | 1 | 共立 ADC1804_F PCM1804 module — Library:ADC1804_F_KYOHRITSU_56x33mm (measured) |
| A1602 | Pico2 | `Module:RaspberryPi_Pico_Common_THT` | 1 |  |
| AMP601,AMP701,AMP801,AMP901,AMP1001,AMP1101,AMP1201,AMP1301,AMP1401,AMP1501 | NE5532 / DIP-8 compatible | `Package_DIP:DIP-8_W7.62mm_Socket` | 10 | Socketed dual op amp under test |
| C201,C205,C207 | 47u | `Capacitor_THT:CP_Radial_D8.0mm_P3.50mm` | 3 |  |
| C202,C204,C206,C208,C402 | 0.1u | `Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder` | 5 |  |
| C203 | 10u | `Capacitor_THT:CP_Radial_D5.0mm_P2.00mm` | 1 |  |
| C311,C312,C313,C314,C315,C316,C322,C505,C506,C607,C608,C609,C610,C707,C708,C709,C710,C807,C808,C809,C810,C907,C908,C909,C910,C1007,C1008,C1009,C1010,C1107,C1108,C1109,C1110,C1207,C1208,C1209,C1210,C1307,C1308,C1309,C1310,C1407,C1408,C1409,C1410,C1507,C1508,C1509,C1510,C1604,C1605,C1607,C1612,C1614,C1615,C1617,C1618,C1622,C1624,C1625,C1629,C1634,C1636,C1637,C1638,C1639,C1641,C1642,C1643,C1646,C1647,C1650,C_IO301,C_IO302 | 100nF | `Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder` | 74 | A701 +3V3_A local bypass 100nF / 1206 / A701 +5V_A local bypass 100nF / 1206 / U1611 の +15V_A デカップリング / U1611 の -15V_A デカップリング / U501 の +15V デカップリング / U501 の -15V デカップリング（v1 C906） / U704/U705 VIN HF bypass 100nF / return ADC_GND_IN. / U709 VDD bypass 100nF / VCOML bypass to ADC_GND / VCOMR bypass to ADC_GND / op amp V+ local decoupling / op amp V- local decoupling / switch VDD local decoupling / switch VSS local decoupling |
| C321 | 100uF 25V | `Capacitor_SMD:CP_Elec_10x12.6` | 1 |  |
| C401 | 22u | `Capacitor_THT:CP_Radial_D6.3mm_P2.50mm` | 1 |  |
| C403,C404,C410,C411 | 100n | `Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder` | 4 |  |
| C405,C406,C407,C409 | 2.2u | `Capacitor_THT:C_Rect_L7.2mm_W2.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2` | 4 |  |
| C408,C412 | 2.7n | `Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder` | 2 |  |
| C501,C502 | 470uF 25V NP | `Capacitor_THT:CP_Radial_D10.0mm_P5.00mm` | 2 | HP 出力の DC ブロック（v1 C901）。無極性電解。役目はオフセットではなく素子故障時の保護（DECISIONS） / HP 出力の DC ブロック（v1 C902）。無極性電解 |
| C503,C504 | 10uF 25V X7R | `Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder` | 2 | U501 の +15V ローカルバルク（v1 C903） / U501 の -15V ローカルバルク（v1 C905 相当） |
| C601,C604,C701,C704,C801,C804,C901,C904,C1001,C1004,C1101,C1104,C1201,C1204,C1301,C1304,C1401,C1404,C1501,C1504 | 2.2uF film | `Capacitor_THT:C_Rect_L7.2mm_W2.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2` | 20 | L output coupling (before switch) / R output coupling (before switch) |
| C602,C605,C702,C705,C802,C805,C902,C905,C1002,C1005,C1102,C1105,C1202,C1205,C1302,C1305,C1402,C1405,C1502,C1505 | 1uF film | `Capacitor_THT:C_Rect_L11.0mm_W4.2mm_P10.00mm_MKT` | 20 | L input film coupling / R input film coupling |
| C1601,C1608,C1623 | 10nF | `Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder` | 3 | Y701 VDD bypass 10nF (ASFL1 データシート指定: pin2-pin4 間) |
| C1602,C1613,C1626,C1628 | 10uF 25V NP | `Capacitor_THT:C_Radial_D5.0mm_H7.0mm_P2.00mm` | 4 | AC couple unpolarized 10uF 25V (not polar electrolytic) |
| C1603 | 10uF 10V X7R | `Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder` | 1 | LT1763-3.3 OUT bulk, >=10V X7R 1206 |
| C1606,C1619 | 10uF 50V X7R | `Capacitor_SMD:C_1210_3225Metric_Pad1.33x2.70mm_HandSolder` | 2 | LT1763 IN bulk / 16V X7R 1206 (6.7V rail) |
| C1609,C1620,C1627,C1632 | 1.8nF C0G | `Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder` | 4 | LPF C0G/NP0 ceramic |
| C1610 | 47uF 35V | `Capacitor_THT:CP_Radial_D8.0mm_P3.50mm` | 1 | BP5293/MBC2596 input bulk. 15V rail -> 35V rating. Return on ADC_GND_IN. |
| C1611,C1631,C1633 | 10uF | `Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder` | 3 | U704/U705 VIN mid-freq ceramic 10uF (unpolarized), return ADC_GND_IN. Parallel with C723 bulk and C725 100nF.,積セラ 10uF50V 3216（秋月 117338・購入済）。U708(XC8107) 入力コンデンサ CIN。データシート推奨 1.0uF 以上、VIN-VSS 間を最短で。,積セラ 10uF50V 3216（秋月 117338・購入済）。U708(XC8107) 出力コンデンサ CL。データシート推奨 1.0uF 以上、IC 直近に配置。 |
| C1616 | 10uF 16V X7R | `Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder` | 1 | LT1763-5 OUT bulk, 10V or 16V X7R 1206 |
| C1621 | 47uF | `Capacitor_THT:CP_Radial_D8.0mm_P3.50mm` | 1 | 導電性高分子アルミ固体電解コンデンサー OS-CON相当 47uF16V以上 +5V_D |
| C1630 | 22uF | `Capacitor_THT:CP_Radial_D6.3mm_P2.50mm` | 1 | 導電性高分子アルミ固体電解コンデンサー OS-CON相当 22uF16V以上 LCD_VCC |
| C1635,C1640 | 10uF 50V | `Capacitor_THT:CP_Radial_D5.0mm_P2.00mm` | 2 | 導電性高分子アルミ固体電解コンデンサー ハイブリッド相当 10μF50V +15V_A / 導電性高分子アルミ固体電解コンデンサー ハイブリッド相当 10μF50V -15V_A |
| C1645 | 10uF 50V | `Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder` | 1 | U1607(BP5293-50) の入力コンデンサ CIN。DS p.2 推奨 10uF。帰り先は D_GND（U1607 の GND と同じ）。PD_GND に落とすと入力の脈流ループが NT1602 を通ってしまう。 |
| C_BULK_N301,C_BULK_N302,C_BULK_P301,C_BULK_P302 | 100uF 35V | `Capacitor_SMD:CP_Elec_10x12.6` | 4 |  |
| D403 | 12V panel LED | `LED_THT:LED_D5.0mm` | 1 |  |
| D1601 | RB160M-30 | `Diode_SMD:D_SOD-123` | 1 | SOD-123 Schottky, +5V_D anode -> Pico VSYS cathode. Blocks USB backfeed into +5V_D. |
| D1610 | DEST 1 | `LED_THT:LED_D5.0mm` | 1 |  |
| D1611 | DEST 2 | `LED_THT:LED_D5.0mm` | 1 |  |
| ENC1601 | ENC_CH | `Rotary_Encoder:RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm` | 1 |  |
| ENC1602 | ENC_BASS | `Rotary_Encoder:RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm` | 1 |  |
| ENC1603 | ENC_TREBLE | `Rotary_Encoder:RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm` | 1 |  |
| F201 | T1.6A slow 5x20 | `Resistor_THT:R_Axial_DIN0411_L9.9mm_D3.6mm_P12.70mm_Horizontal` | 1 |  |
| F202 | PPTC 0.35A hold | `Resistor_THT:R_Axial_DIN0411_L9.9mm_D3.6mm_P12.70mm_Horizontal` | 1 |  |
| F203 | PPTC 0.1A hold | `Resistor_THT:R_Axial_DIN0411_L9.9mm_D3.6mm_P12.70mm_Horizontal` | 1 |  |
| F1601 | T1A slow | `Resistor_THT:R_Axial_DIN0411_L9.9mm_D3.6mm_P12.70mm_Horizontal` | 1 | Fuse |
| F1602 | PPTC 0.5A hold | `Resistor_THT:R_Axial_DIN0411_L9.9mm_D3.6mm_P12.70mm_Horizontal` | 1 | Fuse |
| J201 | +15/-15/A_GND out | `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal` | 1 |  |
| J202 | PD module in (1=GND 2=+12V) | `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal` | 1 |  |
| J1601 | AUDIO | `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal` | 1 | Generic screw terminal, single row, 01x02, script generated (kicad-library-utils/schlib/autogen/connector/) |
| J1602 | V_IN | `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal` | 1 | Generic screw terminal, single row, 01x02, script generated (kicad-library-utils/schlib/autogen/connector/) |
| J1603 | 15_V_IN | `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal` | 1 | Generic screw terminal, single row, 01x03, script generated (kicad-library-utils/schlib/autogen/connector/) |
| J_ANA101 | SLOT1 ANA (D18) | `Connector_PinSocket_2.54mm:PinSocket_2x05_P2.54mm_Vertical` | 1 |  |
| J_ANA102 | SLOT2 ANA (D18) | `Connector_PinSocket_2.54mm:PinSocket_2x05_P2.54mm_Vertical` | 1 |  |
| J_ANA301,J_ANA302 | SLOT ANA (D18) | `Connector_PinHeader_2.54mm:PinHeader_2x05_P2.54mm_Vertical` | 2 |  |
| J_HP501 | HP OUT | `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal` | 1 | ヘッドホン出力端子（箱のパネルのジャックへ）。1=PHONE_L / 2=A_GND / 3=PHONE_R。U501 バッファの出力（10Ω・470µF NP 経由）。2026-09-08 に 2P→3P（帰路を入れた。J_IN401/J_RAIL501 と同じ流儀）。旧 Value「to Audio HP Buffer」= 図の外の v1 バッファは同日 U501 として取り込んだ |
| J_IN401 | AUDIO IN L/R | `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal` | 1 | 箱の外部音声入力。1=L / 2=A_GND / 3=R。ここから結合C経由で PT2314E の LIN/RIN へ入る（セレクタとボリューム段は LOUT/ROUT->LIN/RIN のインサートで飛ばしている）。L と R の間に GND を挟むため 3P にした。 |
| J_LINE501 | LINE OUT | `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal` | 1 | ライン出力端子（箱のパネルへ）。1=LINE_L / 2=A_GND / 3=LINE_R。RV502 直出し（バッファ無し）。2026-09-08 に 2P→3P（帰路を入れた） |
| J_OLED1601 | 2.42 OLED I2C GND/3V3/SCL/SDA | `Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical` | 1 |  |
| J_PWR101 | SLOT1 PWR/CTRL (D18) | `Connector_PinSocket_2.54mm:PinSocket_2x06_P2.54mm_Vertical` | 1 |  |
| J_PWR102 | SLOT2 PWR/CTRL (D18) | `Connector_PinSocket_2.54mm:PinSocket_2x06_P2.54mm_Vertical` | 1 |  |
| J_PWR301,J_PWR302 | SLOT PWR/CTRL (D18) | `Connector_PinHeader_2.54mm:PinHeader_2x06_P2.54mm_Vertical` | 2 |  |
| J_RAIL501 | AMP_SEL OUT | `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal` | 1 | 選択された Amp 出力の取り出し端子。1=AMP_SEL_L / 2=A_GND / 3=AMP_SEL_R で、DEST スイッチ(SW501/SW502)の手前。旧 Value の RAIL IN と旧記述の +12V/A_GND/-12V は、娘基板がスロット直結(J_PWR/J_ANA)になる前の名残で電源ではない。A_GND 極を持つ唯一の音声取り出し口。 |
| K301,K302,K303,K304,K305 | AZ850P2-5 | `Relay_THT:Relay_DPDT_FRT5` | 5 |  |
| LCDDisplay1601 | WAVESHARE-29318 | `Connector_PinHeader_2.54mm:PinHeader_1x15_P2.54mm_Vertical` | 1 | Waveshare 29318 Interface2 host side: 2.54mm 1x15 pin header for included GH-to-Dupont cable (ST7796S SPI + FT6336U I2C) |
| Q401,Q402 | BSS138 | `Package_TO_SOT_SMD:SOT-23` | 2 | I²C SCL 側の双方向レベルシフタ。役目・理由は Q401（SDA 側）と同じ / I²C 双方向レベルシフタ（2026-09-08）。S=Pico 側 3V3 バス、D=PT2314E 側 9V バス、G=3V3。PT2314E の VIH min 3.0 V に対し 3.3 V プルアップでは余裕 0.3 V しか無いので、PT 側を VCC_TONE(9V) で釣る。P82B96 を使わないのは Sx 側 VOL 0.8–1.0 V が PT2314E VIL max 1.0 V / RP2350 VIL 0.8 V を食い切るため（DECISIONS）。 SDA。 |
| R401 | 2.2k | `Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder` | 1 | D403(12V パネル LED)の直列抵抗。素の LED でも 12V 直結で壊れないようにする。(12-Vf2)/2.2k = 約 4.5mA。抵抗内蔵の 12V LED を挿しても点く（やや暗い）。 |
| R410,R411 | 5.6k | `Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder` | 2 |  |
| R412,R413,R1611,R1656,R1657 | 10k | `Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder` | 5 | ADC_nRST pull-up 10k / 1206 / PT2314E 側 I²C SCL のプルアップ（9V=VCC_TONE） / PT2314E 側 I²C SDA のプルアップ（9V=VCC_TONE）。10k: 0.9 mA / 立ち上がり ~0.3 µs（100 kbit/s） |
| R501,R502 | 10R | `Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder` | 2 | HP 出力の直列抵抗（v1 R901）。ケーブル容量からの分離 / HP 出力の直列抵抗（v1 R903） |
| R503,R504,R601,R607,R701,R707,R801,R807,R901,R907,R1001,R1007,R1101,R1107,R1201,R1207,R1301,R1307,R1401,R1407,R1501,R1507,R1620,R1659,R1660 | 100k | `Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder` | 25 | HP ジャック側ノードのブリード（v1 R902）。未接続時に C501 の DC を落とす / HP ジャック側ノードのブリード（v1 R904） / L non-inverting bias / R non-inverting bias / U1611 L バッファの入力バイアス（v1 R805 相当）。J1601 を抜いても入力が浮かない / U1611 R バッファの入力バイアス（v1 R810 相当） / U708(XC8107) CE プルダウン。Active High なので Pico GPIO が Hi-Z の間は LCD OFF がデフォルト。CE に内部プルダウンは無いため必須。 |
| R602,R608,R702,R708,R802,R808,R902,R908,R1002,R1008,R1102,R1108,R1202,R1208,R1302,R1308,R1402,R1408,R1502,R1508 | 47R | `Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder` | 20 | L output isolation / R output isolation |
| R603,R609,R703,R709,R803,R809,R903,R909,R1003,R1009,R1103,R1109,R1203,R1209,R1303,R1309,R1403,R1409,R1503,R1509 | 220k | `Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder` | 20 | L output pulldown (before switch) / R output pulldown (before switch) |
| R604,R606,R610,R612,R704,R706,R710,R712,R804,R806,R810,R812,R904,R906,R910,R912,R1004,R1006,R1010,R1012,R1104,R1106,R1110,R1112,R1204,R1206,R1210,R1212,R1304,R1306,R1310,R1312,R1404,R1406,R1410,R1412,R1504,R1506,R1510,R1512 | 20k | `Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder` | 40 | L feedback Rf; default 20k = GAIN 2 / L gain resistor Rg; GAIN=1+Rf/Rg / R feedback Rf; default 20k = GAIN 2 / R gain resistor Rg; GAIN=1+Rf/Rg |
| R1601,R1606,R1612,R1615 | 4.7k 0.1% | `Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder` | 4 |  |
| R1602,R1608,R1613,R1617 | 47 | `Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder` | 4 | OPA to ADC VIN series 47 / 1206 |
| R1603,R1609,R1614,R1618 | 6.19k 0.1% | `Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder` | 4 |  |
| R1604 | 33 | `Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder` | 1 | Y701 MCLK series 33, 1206 |
| R1607,R1610,R1616,R1619 | 1k 0.1% | `Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder` | 4 |  |
| R1651,R1652,R1655,R1658 | 1k | `Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder` | 4 |  |
| R1653,R1654 | 4.7k | `Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder` | 2 |  |
| RV501 | A50k Dual HP | `Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical` | 1 |  |
| RV502 | A50k Dual LINE | `Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical` | 1 |  |
| SW402 | PWR SW | `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` | 1 |  |
| SW501 | DEST L (PHONE/MUTE/LINE) | `Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical` | 1 |  |
| SW502 | DEST R (PHONE/MUTE/LINE) | `Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical` | 1 |  |
| SW1601 | DEST sense (3PDT 3rd pole, same body as SW501/SW502) | `Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical` | 1 |  |
| TP1601 | ADC_MCLK | `TestPoint:TestPoint_Pad_D1.5mm` | 1 | ADC_MCLK probe pad after R718. |
| U201 | REC20K-2415DZ | `Library:REC20K-Z_1in_THT` | 1 | Recom REC20K-2415DZ isolated DC/DC, 9-36Vin, ±15V/±667mA (20W), eff 88% typ, DIP 1in x 1in, Cout ±3000uF/rail, pin3=CTRL open=ON。REC10K-2415DAW/H2（±333mA・Cout ±270uF）から 2026-09-07 に差し替えた。理由は独立に3つ: ①ソケット10個が常時通電なので ±333mA だと 1ソケットあたり 27mA しか使えず、在庫の MUSES03（20mA）で既に窮屈 ②実レール容量 259.8uF が Cout ±270uF の 96% ③計測系の電源を +15V へ寄せる余地。ピン配置は REC10K と同一で、推奨穴が Ø1.0 -> Ø1.4 になるのでフットプリントも替えた（Ø1.4 なら REC10K も挿さる） |
| U202 | L7809CV +9V | `Package_TO_SOT_THT:TO-220-3_Vertical` | 1 |  |
| U311,U312,U313 | TMUX7612 | `Package_SO:TSSOP-16_4.4x5mm_P0.65mm` | 3 |  |
| U321,U322 | TBD62083APG | `Package_DIP:DIP-18_W7.62mm` | 2 |  |
| U402 | PT2314E | `Package_SO:SOIC-28W_7.5x17.9mm_P1.27mm` | 1 | SOP-28 300 mil（表面実装。無印 PT2314 の DIP 版は入手不可）。LCSC C90034。トーン段だけ使う — 入力セレクタとボリューム段は LOUT/ROUT -> LIN/RIN の インサート点で飛ばしていて、未使用12ピンには no_connect を立ててある。 DGND(25) は 2026-09-08 にチップの足元で A_GND へ（旧 D_GND）。I²C は Q401/Q402 レベルシフタ越しに 9V（VCC_TONE）プルアップの I2C_SDA_9V/I2C_SCL_9V で受ける。 |
| U403 | BP5293-50 +5V | `Library:BP5293-50_ROHM_SIP-3` | 1 |  |
| U501 | OPA1652 | `Package_DIP:DIP-8_W7.62mm_Socket` | 1 | HP バッファ（v1 HeadphoneBufferModule AMP901 の移設・2026-09-08）。ユニティフォロワ ×2（A=L, B=R）。DIP-8 ソケットで AmpChannel と同じ。標準実装は OPA1652（DIP 化モジュール、出力 ±30 mA）。入力は RV501 ワイパー（PHONE_BUF_L/R）、出力は 10Ω→470µF NP→PHONE_L/R。⚠ 比較セッション中は差し替えない（10 石すべてに共通に掛かる）。 |
| U1601,U1602,U1608,U1611 | OPA1656 | `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` | 4 | 計測タップの「+」側バッファ（v1 の AdcBuffer を復元）。ユニティフォロワ、入力 100k→A_GND。音声バスから見た負荷を 1.87k→約30k（RV501 50k ∥ R603 220k ∥ R1659 100k）に戻し、両ブランチが 10µF を見る源インピーダンスを揃える（Vg 除去 20Hz 10.5→43dB、TMUX7612 の H3 −94.9→−115.5dB（spice/switch_thd.py --rload 30.4e3 実測）、低域 39→17Hz）。v1 の出力 47Ω は対称性のため付けない（負荷は R1612/R1614 系の抵抗で容量性ではなく、OPA1656 は CL 100 pF まで規定内。DS Electrical Characteristics）。2026-09-07 |
| U1603 | LT1763-3.3 | `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` | 1 | ADI LT1763 3.3V fixed LDO, SO-8, low noise |
| U1605 | TPS3307-33 | `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` | 1 | Triple supervisor SO-8: SENSE1=5V (4.55V), SENSE2=3.3V (2.93V), SENSE3=adj 1.25V. Push-pull RESET / ~RESET, 200ms delay, ~MR. VDD from +3V3_A so ~RESET is 3.3V. |
| U1606 | LT1763-5 | `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` | 1 | ADI LT1763 5V fixed LDO, SO-8, low noise |
| U1607 | BP5293-50 | `Library:BP5293-50_ROHM_SIP-3` | 1 |  |
| U1609 | XC8107AC20MR-G | `Package_TO_SOT_SMD:SOT-23-5_HandSoldering` | 1 | LCD/タッチ用ロードスイッチ。秋月 131334。CE=LCD_EN は Active High（VCEH 1.5V min なので Pico 3.3V で直接ON）。R717 100k で CE プルダウン＝起動時 OFF。ソフトスタート 0.6ms typ で LCD_VCC バルクへの突入電流を抑制。C740(CIN)/C739(CL) は 10uF 3216 を IC 直近に。FLG 未使用。 |
| U1610 | MCP23017 (UI 0x22) | `Package_DIP:DIP-28_W7.62mm` | 1 |  |
| U_IO301,U_IO302 | MCP23017 | `Package_DIP:DIP-28_W7.62mm` | 2 |  |
| Y1601 | ASFL1-12.288MHZ-EC-T | `Library:Oscillator_SMD_Abracon_ASFL-4Pin_5.0x3.2mm_HandSoldering` | 1 | Abracon ASFL1 12.288MHz CMOS osc, 3.3V. pin1=Tri-State (H/open=発振), pin4=Vdd. データシート指定: pin2-pin4 間に 0.01uF バイパス |
<!-- END GENERATED: case-bom -->

<!-- BEGIN GENERATED: ampchannel-bom -->
**AmpChannel 1ch テンプレート（×10 される中身）** — 下の表は `AudioV2/AmpChannel.kicad_sch` から自動生成しています。
**手で編集しないでください**（次の再生成で消えます）。値・フットプリント・役割を直すときは KiCad の回路図側を直し、
`python3 AudioV2/scripts/gen_parts_bom.py` で再生成します。

行数 8 / 部品総数 19。

> `Refs` 列と `Value` / `Role` 列に**位置の対応はありません**。kicad-cli はグループ内の値を重複除去してアルファベット順に並べるため、「n 番目の参照 = n 番目の役割」とは読めません。

| Refs | Value | Footprint | Qty | Role |
|---|---|---|---|---|
| AMP601 | NE5532 / DIP-8 compatible | `Package_DIP:DIP-8_W7.62mm_Socket` | 1 | Socketed dual op amp under test |
| C601,C604 | 2.2uF film | `Capacitor_THT:C_Rect_L7.2mm_W2.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2` | 2 | L output coupling (before switch) / R output coupling (before switch) |
| C602,C605 | 1uF film | `Capacitor_THT:C_Rect_L11.0mm_W4.2mm_P10.00mm_MKT` | 2 | L input film coupling / R input film coupling |
| C607,C608,C609,C610 | 100nF | `Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder` | 4 | op amp V+ local decoupling / op amp V- local decoupling / switch VDD local decoupling / switch VSS local decoupling |
| R601,R607 | 100k | `Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder` | 2 | L non-inverting bias / R non-inverting bias |
| R602,R608 | 47R | `Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder` | 2 | L output isolation / R output isolation |
| R603,R609 | 220k | `Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder` | 2 | L output pulldown (before switch) / R output pulldown (before switch) |
| R604,R606,R610,R612 | 20k | `Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder` | 4 | L feedback Rf; default 20k = GAIN 2 / L gain resistor Rg; GAIN=1+Rf/Rg / R feedback Rf; default 20k = GAIN 2 / R gain resistor Rg; GAIN=1+Rf/Rg |
<!-- END GENERATED: ampchannel-bom -->

### 4.2 選定・実装メモ（回路図から導出できない＝ここが正）

> **TODO（§2.9 移行に伴う要更新）:** 以下は旧 AmpModule（×10 独立基板）時代の記述が残っている。
> AmpBank（1 枚統合、TMUX7612 切替、出力カップリング 2.2 µF フィルム、入口バルクのみ）の実態と
> 一部合っていない。書き換えは未着手。デカップリング寸法・OpAmp 差し替え条件はおおむね有効。

| 項目 | 内容 |
|---|---|
| **`TMUX7612` の発注型番** | 回路図の Value は基本型番の `TMUX7612`。**発注は `TMUX7612PWR`**（16-TSSOP。DS の orderable は他に WQFN の `TMUX7612RUMR`）。DigiKey は包装で品番が分かれ、**`296-TMUX7612PWRCT-ND`（カットテープ・MOQ 1）を使う** — `...TR-ND`（テープ&リール）は **MOQ 3000 / 在庫0**、`...DKR-ND`（Digi-Reel）は別途リール手数料 $7。2026-09-02 実ページ確認: 正規在庫 1,772 個、qty1 $7.59 / **qty10 $5.86**（10ch で約 $59）。WQFN 版は ¥806 と安いがテープ&リール MOQ 3000 のみで実用にならない |
| **OpAmp の差し替え条件** | 基準は **NE5532P**。DIP-8 **ソケット**実装なので現物差し替えで聴き比べできる。他の DIP-8 互換デュアルに替えるときは **±15 V 動作・ユニティゲイン安定・容量負荷耐性** を DS で確認する（手持ち在庫は [`Audio/OPAMP_INVENTORY.md`](../Audio/OPAMP_INVENTORY.md)） |
| **SMD バイパスコンデンサの寸法** | `100nF` は **1206 が既定**（回路図の Footprint も 1206）。ハンドはんだ前提のため大きめを選んでいる。**レイアウト都合で 0603 まで下げるのは可**。下げる場合は回路図の Footprint も合わせて変更すること |
| **PCB 外形（未設計）** | AmpBank の PCB はまだ設計していない。基板サイズは 150×100 mm 見込み（DIP-8 ソケット10個が面積の支配要因、[AGENT_HANDOFF.md §2.9](AGENT_HANDOFF.md)）。旧 AmpModule 用の `Audio/split/AudioCase_4_amp.kicad_pcb` 流用方針は§2.9の刷新で無効 |

## 4.3 MCU の在庫と選択肢（2026-09-03）

**Arduino Nano が在庫にある**が、置き換え先は限られる。

| 用途 | 現行 | Nano で代替できるか |
|---|---|---|
| **計測用**（`MeasurementADC`） | **Pico 2 (RP2350)** | **不可**。ハード要求が RP2350 固有 |
| 制御用（`ControlPanel`） | Pico | 可能だが**利点が無い**（下記） |

**計測用が替えられない理由**（`Audio/measurement_fw/README.md`）:

- **I²S スレーブ受信を PIO で実装**している（PCM1804 がマスタなので `machine.I2S` が使えない）。
  Nano に PIO 相当が無い
- 24bit×2ch を **DMA** で連続取得
- **第2コア**で FFT、core0 で LCD 描画を並行
- キャプチャに **128 KB** のバッファ（Nano の SRAM は 2 KB）

**制御用を Nano にしない理由:**

- **Nano は 5V、この系の I²C は 3.3V**（`MCP23017` が 3V3、プルアップも `3V3` へ）。
  レベル変換か再設計が要る
- `ControlPanel` は Pico のフットプリントとピン割当で組んであり、`VSYS` 給電もその前提
- **Pico は安価で入手性に問題が無い**ので、リレーと違い「在庫がある」ことの価値が小さい
- GPIO は 12 本余っており、性能上の不足は無い

**Nano の使い道として残るもの:**

- **USB アイソレーションの切り分け治具**（`DECISIONS.md` の USB グラウンドループ仮説の検証）
- 将来 `ControlPanel` を作り直すときの選択肢

> **MCU を1個に統合する案は「あり」**（2026-09-03 に見解を訂正）。
> 一度「計測基板を隔離したいのに UI を集めるのは逆行」と書いたが、**根拠が弱かった**。
> 詳細と理由は [`DECISIONS.md`](DECISIONS.md)「MCU 統合は成立する」。

## 5. まだ買わなくてよい / レイアウト時

| 項目 | 状態 |
|---|---|
| ENC 正確な秋月コード | 在庫を見て同一外形を 3 個 |
| PT2314E 入手先 | **LCSC `C90034` / JLCPCB（Extended part）**。無印 PT2314 は DigiKey に無く、モデレータ自身が調達困難と回答している。SOP なのでソケットは無い |
| ノブ（φ6 D カット） | RK27 用に大きめ。ENC 用は小さめ |
| AmpBank シルク | 帰還抵抗の倍率表（GAIN = 1 + Rf/Rg）を基板隅に印刷（§2.9） |
| ~~Footprint 未設定の部品~~ | **2026-09-07 に 0 個**（現在の個数は §4.1 の生成値が正。数値をここに書き写すと腐るので置かない）。`legacy/` 由来の電源・トーン・出力段・パネル部品も埋めた。⚠ パネル部品は2種類ある — **ヘッダ**（`RV501/502`・`SW402`・`SW501/502`・`SW1601`。現物は箱配線なので品番が変わっても基板は動かない）と、**基板実装**（`ENC1601-1603` は EC11 垂直・軸20mm の本体、`D1610/D1611/D403` は 5mm LED 本体、`A1602` は Pico 本体）。後者は基板の物理位置をパネルに縛るので、品番変更が基板に効く。`U202` の立て方と F201-203 のヒューズ外形はレイアウトで見直す前提 |

---

## 変更履歴

| 日付 | 内容 |
|---|---|
| 2026-08-30 | 初版 — 回路制約から SW_DEST / RV / 周辺の第一候補を固定 |
| 2026-08-30 | 表示 — 制御 OLED=2.42″ SSD1309（AliExpress）、スペアナ=Waveshare 29318（v1 実装） |
| 2026-08-31 | AmpModule再版 — ゲイン2（20k/20k）、バルク/高速バイパス、出力C小型化 |
| 2026-08-31 | J_I2C端子台をPhoenix MKDS-1,5シリーズ（v1 `Audio/Controll.kicad_sch`と同一/互換）に確定。§11 Q3（JST-XH vs 2.54）は解消 |
| 2026-09-01 | AmpModule 部品表を回路図からの**自動生成**に切替（§4.1）。手書きの designator 表を廃止し、非導出情報だけを §4.2 に残した。生成: `AudioV2/scripts/gen_parts_bom.py` |
