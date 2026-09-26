# AudioV2.1 — データシート

v2.1 の設計・査読で引いている部品の一次資料。オフライン参照用にローカル PDF を置く。
DS から読んだ事実（照合済み）は [../ds_facts/](../ds_facts/)、決定は [../DECISIONS.md](../DECISIONS.md)。
2026-09-25 に、v1 の置き場から引いていた手持ちオペアンプの DS と Traco `TMR9`・`TMR6` をここへ写した（v2.1 はここだけを読む）。

## サブディレクトリ

| | 中身 |
|---|---|
| [opamps/](opamps/) | 手持ちオペアンプ 16 石＋ NE5532 本家の DS。石と PDF の対応は [../OPAMP_STOCK.md](../OPAMP_STOCK.md) |
| [boundary/](boundary/) | 境目の切替素子の候補（照合は [../ds_facts/verify_boundary.md](../ds_facts/verify_boundary.md)） |
| [detect/](detect/README.md) | 娘のレール検知の候補 |
| [relay4/](relay4/) | 4 回路リレーの候補（`ds_facts/relay4.md` は未照合） |
| [tap/](tap/) | 計測タップの結合・絶縁の候補 |
| [arch/](arch/) | 制御の木（デコーダ・ロードスイッチ・監視）の候補 |
| [reference/](reference/) | 参考製品の取説 |
| [tone/](tone/) | トーンチップの候補（バイパスを持つもの。調査は [../review/tone_chip_bypass.md](../review/tone_chip_bypass.md)） |

## 電源・PD

| 部品 | 用途 | ローカル | 取得元 |
|---|---|---|---|
| **RS6-1215D**（Recom） | ±15 V DC-DC（v2.1 の主電源、DECISIONS §3-1） | [Recom_RS6.pdf](Recom_RS6.pdf) | Recom |
| **REC20K-2415DZ**（Recom） | ±15 V DC-DC（今の図。v2 から） | [Recom_REC20K-Z_Rev3-2025.pdf](Recom_REC20K-Z_Rev3-2025.pdf) | Recom |
| **TMR 9 / TMR 6**（Traco） | 主電源の比較の候補 | [TMR9_Datasheet.pdf](TMR9_Datasheet.pdf)・[TMR6_Datasheet.pdf](TMR6_Datasheet.pdf) | Traco |
| **[50224] CH224** | USB-PD（外付けモジュール、板上は受け端子） | [StrawberryLinux_CH224K_manual.pdf](StrawberryLinux_CH224K_manual.pdf) 他 | ストロベリーリナックス |
| **DKMW20F-15** | ±15 V DC-DC（v2 の初期に使った。今の図には無い） | [MeanWell_SKMW20_DKMW20.pdf](MeanWell_SKMW20_DKMW20.pdf) | [Mean Well SKMW20/DKMW20](https://www.meanwell.com/webapp/product/search.aspx?prod=DKMW20) |
| **BP5293-50** | +5 V（コイル・デジ） | [ROHM_BP5293-xx.pdf](ROHM_BP5293-xx.pdf) | [ROHM BP5293-xx](https://www.rohm.com/products/power-management/switching-regulators-integrated-fet/bp5293-xx-series) |
| **L7805C / L7809** | コイルの 5 V（v2.1）／PT2314E の 9 V | [ST_L78.pdf](ST_L78.pdf) | ST |
| **TPS7A49 / TPS7A30** | ch ごとの LDO（v2.1） | [TI_TPS7A49.pdf](TI_TPS7A49.pdf)・[TI_TPS7A30.pdf](TI_TPS7A30.pdf) | TI |

### DC-DC の候補（2026-09-05 の再探索。**採否は未決**）

`dcdc_survey.py` で 431 件を引き、±12 V 両レール・MOQ 1・在庫あり・12 V 入力対応の
220 件から実読した分。**選定の決め手になる `Cout`（最大容量負荷）・軽負荷での `Fsw` の
扱い・絶縁容量・最小負荷は、どれも DigiKey API には無くデータシートにしかない。**
だからここに置いてある（以下は v2 のときの探索の記録。v2.1 の比較は `../review/main_power_compare.md` ほか）。

**⚠ この表の数値は ±12 V 両出力版のもの。** 同じ系列でも単出力版・±15 V 版では `Cout` が
まるで違う（TEL 10WI は単出力 12 V が 560 µF、±12 V dual は 390 µF。EC7AW は単出力 24S12 が
833 µF、±12 V dual は 417 µF）。**モデル行を取り違えると倍以上ずれる。**

**⚠⚠ `Fsw` の欄で候補を比べてはいけない。** 「Aimtec は @100% load と条件付き、Recom は
条件が書いていない」という差は**見せかけ**だった —— Recom は同じ条件を**表の見出し**に
書いている（`REC10K-AW.pdf` p2 *"BASIC CHARACTERISTICS (measured @ TAMB= 25°C, nom. VIN,
**full load** and after warm-up unless otherwise stated)"*）。Cincon も Traco も同様の全負荷注記が
あり、**下の候補は9品すべて全負荷規定**。しかも Recom の 350 kHz は **Max. 列**（Min./Typ. 欄は空）で、
軽負荷で下がることと矛盾しない。

**この欄で意味があるのは次の2つだけ:**
- **Mornsun `URA_ZP-10WR3` / `URA_LD-20WR3` は「軽負荷（50%以下）で周波数を下げる」と明記**（不採用の根拠。この箱が追っている 1.2 kHz スパーの第一容疑者と同系統の挙動）
- **Traco `TEL`/`TMR` は "(PWM)" と明記**（PFM／バーストではない、という積極的な主張）

それ以外の「書いていない」は**全部同じ**で、優劣を付ける材料にならない。

| 部品 | ローカル | `Cout`（±12V dual） | `Fsw` の書かれ方 | 絶縁容量 | 最小負荷 | 効率 |
|---|---|---|---|---|---|---|
| **REC20K-Z**（Recom） | [Recom_REC20K-Z_Rev3-2025.pdf](Recom_REC20K-Z_Rev3-2025.pdf) | `2415DZ`=**±3000 µF** / `2412DZ`=**±4000 µF**（p1） | "Internal Operating Frequency" 265 kHz、Max. 列（p2） | **2000 pF** typ（p6） | **0 %**（p2） | 88 % |
| **REC10K-AW**（Recom） | [Recom_REC10K-AW_Rev2-2025.pdf](Recom_REC10K-AW_Rev2-2025.pdf) | `2412DAW`=**±470 µF** / `2415DAW`=±270 µF（p1） | "Internal Operating Frequency" 350 kHz、**Max. 列**・条件欄空（p2） | 1000 pF typ（p6） | **0 %**（p2、Min. 列） | 85 % |
| **AM10TW-LPZ**（Aimtec） | [Aimtec_AM10TW-LPZ.pdf](Aimtec_AM10TW-LPZ.pdf) | `2412DLPZ`=**470 µF**（± 表記なし、p2） | 300 kHz、条件 **"100% load"**、Min./Max. 欄空（p3） | **2000 pF**（p2） | 項目なし | 87 % |
| **AM15CW-LPZ**（Aimtec） | [Aimtec_AM15CW-LPZ.pdf](Aimtec_AM15CW-LPZ.pdf) | `2412DLPZ`=**±470 µF**、±625 mA（p2） | 300 kHz、条件 **"100% load"**（p3） | **2000 pF**（p3） | 項目なし | 90 % |
| **NSD10-D**（MEAN WELL） | [MeanWell_NSD10-D.pdf](MeanWell_NSD10-D.pdf) | **±1000 µF** と最大。ただし**6モデル横断の1セル**でモデル別値ではない（p1） | 仕様表に**記載なし**。p2 ブロック図に "fosc : 350KHz" とあるだけ | **記載なし** | 項目なし（`CURRENT RANGE` 下限が 0.02 A） | **77 %** |
| **EC7AW**（Cincon） | [Cincon_EC7AW.pdf](Cincon_EC7AW.pdf) | **417 µF**（± 表記なし、p1） | **"Fixed Switching Frequency"**（p1 Features、**文書内ここ1箇所のみ**）。特性表は 477/530/**583** kHz ≒ ±10 % の幅で、**両者を結ぶ注記は無い**（p3） | 1000 pF typ（p3） | 項目なし（`OUTPUT CURRENT MIN.` が 0 mA） | 88.5 % |
| **EC2SBW**（Cincon） | [Cincon_EC2SBW.pdf](Cincon_EC2SBW.pdf) | **470 µF**（± 表記なし、p1） | **"100 kHz min."**（p2、条件記載なし。**下限表記＝可変を示唆**） | 1000 pF typ（p2） | 項目なし（`OUTPUT CURRENT MIN.` が 0 mA） | 86 % |
| **TEL 10WI**（Traco） | [Traco_TEL10WI.pdf](Traco_TEL10WI.pdf) | **390 / 390 µF**（p2） | 355-485 kHz (PWM) / 420 kHz typ（p3） | **1'500 pF max**（p3、候補中で最大） | **"Not required"**（p2） | 87 % |
| **TMR 10WI**（Traco） | [Traco_TMR10WI.pdf](Traco_TMR10WI.pdf) | **390 / 390 µF**（p2） | 390-450 kHz (PWM) / 420 kHz typ（p3） | 1'000 pF typ / **1'500 pF max**（p4） | **"Not required"**（p2） | 88 % |

**⚠ 絶縁容量は候補ごとに桁ではなく倍で違う。** この設計の絶縁は `PD_GND` と `A_GND` を
分ける構造そのもので、効くのは耐電圧（functional）ではなく**絶縁容量**の方
（v2 のときの否定側査読）。**Aimtec 2品は 2000 pF で Recom / Cincon の2倍。**
安いのはこの2品だが、**この設計がいちばん気にしている欄で最下位**にいる。

**`U1604` の下流 LDO**（置き換え候補の足切りを決める）:

| 部品 | ローカル | この設計に効く数字 |
|---|---|---|
| **LT1763**（ADI） | [ADI_LT1763.pdf](ADI_LT1763.pdf)（`1763fh`） | **⚠ `LT1763-5` の実負荷での規定は `6V < VIN < 20V, 1mA < ILOAD < 500mA`**（p4）。`VIN=5.5V` の行は `ILOAD=1mA` のときだけ。**これで固定 6 V の三端子が全部落ちる**（DECISIONS `V21-継-13`）。Ripple Rejection **50 min / 65 typ dB**（p5、条件に `CBYP` は入っていない）。Figure 3（p16）が「容量を増やせば最小 ESR は 0 に近づく」を示す |

⚠ `analog.com` はこの環境から不通（接続自体が落ちる）。**DigiKey API の `DatasheetUrl` で正しい版（`1763fh`）を特定し、`bdtic.com` のミラーから取得**した。

**`+9V` の三端子レギュレータ**（±12 V 化の障害③に直結）:

| 部品 | ローカル | この設計に効く数字 |
|---|---|---|
| **NJM7809FA**（日清紡マイクロデバイス） | [NJR_NJM7800.pdf](NJR_NJM7800.pdf)（`Ver.1.2`） | **規定入力範囲の下限は 11.5 V**（p3、Line Regulation の試験条件が `VIN=11.5 to 25V, IO=0.5A`）。**ドロップアウト特性のグラフは NJM7805 と NJM7812 にしかなく、7809 には無い**（p8-9）＝ 30 mA 級での規定が無い。`IQ` typ 4.3 / max 6.0 mA、絶対最大入力 35 V |

**⚠ 上の値は2版で照合済み。** 旧 `Ver.2007-05-16`（New JRC 表記）と現行 `Ver.1.2`（日清紡）を
突き合わせたところ、**NJM7809 の行は 19 年間まったく変わっていない** —— 出力 8.65/9.0/9.35 V、
`VIN=11.5 to 25V`、`IQ` 4.3/6.0 mA、絶対最大 35 V、**7809 のドロップアウト曲線が無いことまで同じ**。
違ったのは絶対最大定格のモデル群の括り方（`7805 to 7809` → `7805 to 7810`）と
パッケージ表記（`DL1` → `DL1A`）だけ。**旧版はリポジトリに置かない**（同じ事実を2箇所に
置くと片方が腐る）。

**⚠ `L7809CV` は ST 純正が DigiKey に存在しない**（UMW / Lumimax / EVVO のセカンドソースのみ。
2026-09-05 に API で確認）。**なので入力範囲の議論は ST 版ではなく、実際に買える石で
やること。** 手持ちの `NJM7809FA`（在庫 9263・アクティブ）は**同じ 11.5 V 下限**なので、
**障害③は石を替えても消えない。** ⚠ `NJM7809FA` は TO-220F なのでフットプリントが別。

**不採用が確定した候補の一次資料**（落選根拠がデータシートの一文にあるので置く）:

| 部品 | ローカル | 落選根拠（原文） |
|---|---|---|
| **URA_ZP-10WR3**（Mornsun） | [Mornsun_URA_ZP-10WR3.pdf](Mornsun_URA_ZP-10WR3.pdf) | **p3 注①** *"Switching frequency is measured at full load. **The module reduces the switching frequency for light load (below 50%) efficiency improvement.**"* —— この箱が追っている 1.2 kHz スパーと同系統の挙動を自分で作りに行くことになる。`Cout` 470 µF（**注③「Vo1 と Vo2 の値は同一」＝片レール**）・絶縁容量 **2000 pF** |
| **URA_LD-20WR3**（Mornsun） | [Mornsun_URA_LD-20WR3.pdf](Mornsun_URA_LD-20WR3.pdf) | **p3 Note \*** に同一文。加えて 2"×1" で面積が倍 |
| **PYBE10**（CUI / Bel） | [CUI_PYBE10.pdf](CUI_PYBE10.pdf) | **p3 note 9** *"Value is based on full load. **At loads <50%, the switching frequency decreases with decreasing load**"* —— Mornsun と同じ。`Cout` 470 µF・絶縁容量 2000 pF・350 kHz PWM・±416 mA と**数値が全部一致**する。DigiKey では **NFND**。⚠ `belfuse.com` のリンクは製品ナビの HTML を返す。**実体は CUI 側**（`cui.com/product/resource/pybe10.pdf`） |

**TDK-Lambda `CCG15-30W`**（2026-09-05）。`product.tdk.com` は TDK 自身の Akamai が 403 を返し、
`curl`・`WebFetch`・実 Chromium すべて不可。**⚠ ただし「取得不能」と結論したのは誤りだった** ——
**公開ミラーで取れる**（`docs.rs-online.com/b44f/A700000006915758.pdf` が取説、
`4donline.ihs.com` にカタログ。どちらも認証なしで 200）。**4つ試して諦めたのが早すぎた。**
Farnell と Octopart のミラーが単出力のみだったのは事実だが、**それは短縮版を引いていただけ**:

| ローカル | 中身 |
|---|---|
| [TDK-Lambda_CCG15-30.pdf](TDK-Lambda_CCG15-30.pdf) | カタログ。p1 モデル表、p3 仕様表 |
| [TDK-Lambda_CCG15-30_manual.pdf](TDK-Lambda_CCG15-30_manual.pdf) | 取説。**p8 Table 5-1 が最大外部出力容量** |

| 項目 | 値 | 出典 |
|---|---|---|
| **最大外部出力容量** | **±12V: ±1,200 µF / ±15V: ±1,000 µF** | 取説 p8 Table 5-1・カタログ p3 |
| **その容量はどこに繋ぐ値か** | **`CCG-D` は「+Vout と COM の間」「−Vout と COM の間」＝ 片レール**（取説 p8 に明記） | 取説 p8 |
| 最小負荷 | **"No minimum load required"** | カタログ p3 |
| `Fsw` | `CCG-D`: **430 kHz**。**取説 p4 のブロック図が `Switching Frequency(fixed) : 430kHz` と "fixed" を明記**（⚠ 当初「記載なし」としたのは誤り。同上） | カタログ p3 / 取説 p4 |
| **絶縁容量** | **1000 pF**（取説 p17 §6-19 *"This product has internal capacitor connected between input and output. Capacitance of input - output : 1000pF"*）。**⚠ 当初「非公表」と記録したのは誤り —— カタログ p3 にしか無いと思い込み、同時に持っていた取説を見ていなかった。** この欄では `EC4SBW`(1500 pF) より良く、`REC20K`(2000 pF) の半分 | 取説 p17 |
| **`RC` ピン** | **⚠ サフィックス無しは負論理 —— *"ON when pin is shorted, OFF when open"*。`REC10K` の「開放 = ON」と逆で、ON にするのに `−Vin` へのショートが要る**（取説 §6-7 Note 1）。`/P` サフィックスが正論理（開放 = ON）だが、**`/P` 品は DigiKey に無い**（`CCG15-24-12D/P` / `-15D/P` / `CCG30-24-15D/P` すべて 0 件）。**⚠ この事実は Farnell / Octopart の短縮版 p1 にも書かれていた**（*"Standard: Low = ON, Open = OFF"*）。**欄の名前だけ見て行を読まなかったせいで「DigiKey 属性は信用できないので裏取り待ち」と誤って記録した** | カタログ p2・p3、取説 §6-7 |
| OCP | **hiccup mode, >105 %**（`REC10K` の 150 % に比べてかなり狭い） | カタログ p3 |
| 寸法 | 25.4×25.4×9.9（1"×1"） | カタログ p3 |
| 該当品 | `CCG15-24-12D` ±12V ±650 mA 89 % ¥5,082 在庫 80 ／ `CCG15-24-15D` ±15V ±500 mA 90 % ¥5,082 在庫 108 | カタログ p1・API |

**⚠⚠ 記録が「`Cout` ≥ 102 µF の足切りで TDK-Lambda `CC`/`CCG` 系が落ちた」としていたのは誤り。**
`CCG` の `Cout` は **1,000〜1,200 µF** で、その足切りの10倍以上ある。**落ちる理由が無かった。**

**不採用が確定した候補の一次資料**（落選根拠がデータシートの一文にあるので置く）:

| 部品 | ローカル | 落選根拠（原文） |
|---|---|---|
| **URA_ZP-10WR3**（Mornsun） | [Mornsun_URA_ZP-10WR3.pdf](Mornsun_URA_ZP-10WR3.pdf) | **p3 注①** *"Switching frequency is measured at full load. **The module reduces the switching frequency for light load (below 50%) efficiency improvement.**"* —— この箱が追っている 1.2 kHz スパーと同系統の挙動を自分で作りに行くことになる。`Cout` 470 µF（**注③「Vo1 と Vo2 の値は同一」＝片レール**）・絶縁容量 **2000 pF** |
| **URA_LD-20WR3**（Mornsun） | [Mornsun_URA_LD-20WR3.pdf](Mornsun_URA_LD-20WR3.pdf) | **p3 Note \*** に同一文。加えて 2"×1" で面積が倍 |
| **PYBE10**（CUI / Bel） | [CUI_PYBE10.pdf](CUI_PYBE10.pdf) | **p3 note 9** *"Value is based on full load. **At loads <50%, the switching frequency decreases with decreasing load**"* —— Mornsun と同じ。`Cout` 470 µF・絶縁容量 2000 pF・350 kHz PWM・±416 mA と**数値が全部一致**する。DigiKey では **NFND**。⚠ `belfuse.com` のリンクは製品ナビの HTML を返す。**実体は CUI 側**（`cui.com/product/resource/pybe10.pdf`） |

**⚠ TDK-Lambda `CC`/`CCG` 系はこの環境から取得できない。** `product.tdk.com` は
**TDK 自身の Akamai** が 403 を返す（本文に `errors.edgesuite.net` の参照番号）。
`curl`・`WebFetch`・**プリインストールの実 Chromium** すべて 403 で、
**クライアント指紋ではなく IP レピュテーションでの遮断**。代理店ミラー
（Farnell / Octopart）は本物の TDK 文書だが**単出力のみ・`Cout` 欄そのものが無い**短縮版。
`Cout` は `ccg_e.pdf`（カタログ）と `ccg_apl.pdf`（取説 Table 5-1）にしかなく、
どちらも `product.tdk.com` のみ。**`CCG15-24-12D`（¥5,082・在庫 80・±650 mA・1"×1"）は
`Cout` 不明のまま未評価。** 判断するには通常回線からの人手が要る。

| **EC4SBW**（Cincon） | [Cincon_EC4SBW.pdf](Cincon_EC4SBW.pdf) | `24D15`=**650 µF/レール**（p1） | **p1 features に "Fixed Switching Frequency" を明記**。`Others` は **330 kHz typ**、3.3/5V のみ 270 kHz（p2） | **1500 pF typ**（p2） | **0 mA**（p1） | 89 % |

**⚠ `REC20K-2415DZ` にはメーカーの EMC フィルタ推奨が無い。** `Recom_REC20K-Z_Rev3-2025.pdf` p8
**Note8: *"Filter suggestions are valid for `REC20K-2405SZ` only."*** —— `REC10K` 側の
「Dual 用推奨に `2415DAW` が入っていない」より穴が広い（`REC20K` は単出力1品にしか無い）。

**⚠⚠ `REC20K-Z` は ±15 V のままで `Cout` の宿題を閉じられる。** 現行 `REC10K-2415DAW/H2` の
`Cout ±270 µF` はレール総容量に対して余裕が無いが、**同じ Recom・同じ 1"×1"・同じピン配置**
（Dual: 1 +Vin / 2 −Vin / 3 CTRL / 4 −Vout / 5 COM / 6 +Vout。`REC20K-Z` p9）の
`REC20K-2415DZ` は **±3000 µF**・±667 mA・88 %・絶縁 2 kVDC（**grade basic**、`REC10K` は
functional）で、差額は **+¥1,216**（¥3,620 / 在庫 162 / MOQ1）。
**`TMUX7612` の膝も `L7809` の入力下限もネット名の改名も、一切触らずに済む。**
代償は絶縁容量が 1000 → **2000 pF** に悪化することと、ピン径が Ø1.0→**Ø1.4 mm**（穴径が別。PCB 未設計なので実害なし）。
**この選択肢は 2026-09-05 の否定側査読で出た。それまでの記録は ±15 V 側を「逃げ道が乏しい」と
誤って結論していた（REC10K 系列しか見ていなかった）。**

**⚠ Recom の EMC フィルタ推奨は `2412DAW` にあって `2415DAW` に無い。**
`Recom_REC10K-AW_Rev2-2025.pdf` **p8** の EN55032 Class B / Dual Output の Component List に
挙がっているのは `REC10K-2412DAW/H2` / `REC10K-2405DAW/H2` / `REC10K-4824DAW/H2` の3つで、
**現行採用の `2415DAW/H2` は入っていない**。Note7: *"Filter suggestions are valid for indicated
part numbers only. For other part numbers, please contact RECOM for advice."*
なお部品表に載っているのは**定数だけ**（C 10 µF / L1 10 µH / CMC1 5 µH / C4,C5 4.7 nF）で、
フィルタ部品のメーカ型番は書かれていない。単出力版は L1 が 33 µH で Dual と違う。

## 音量・トーン

| 部品 | 用途 | ローカル | 取得元 |
|---|---|---|---|
| **PT2314E SOP-28** | Bass / Treble（I²C、Amp 前） | **[Princeton_PT2314E.pdf](Princeton_PT2314E.pdf)** | PT2314E V1.0 / 2010-01 / **15ページ完全版**。ELECTRICAL CHARACTERISTICS あり（`VIH` min 3 V・`RL` 5 kΩ・THD 0.03 % 等 → DECISIONS `V21-継-05`） |
| ~~PT2314 DIP-28~~ | 無印（**不採用**。参考） | [Princeton_PT2314.pdf](Princeton_PT2314.pdf) | v1.1 の**3ページ抜粋**。ピン配置とアプリケーション回路のみで**電気的特性が無い**。ピン配置は E と同一 |
| NJW1194（候補） | 音量＋トーン、`TSW` でトーンを飛ばす（3 線シリアル、±7 V） | [tone/NJR_NJW1194.pdf](tone/NJR_NJW1194.pdf) | Nisshinbo 製品頁、Ver.7.4（25 頁）、2026-09-26 取得 |
| NJW1119A（候補） | トーン専用 3 バンド、ch ごとの `TSW`（3 線シリアル、±7 V） | [tone/NJR_NJW1119A.pdf](tone/NJR_NJW1119A.pdf) | Nisshinbo、Ver 2.1（19 頁）、2026-09-26 取得 |
| NJU7391A（参考） | 音量＋トーン、トーンの OFF の定義が制御表に無い | [tone/NJR_NJU7391A.pdf](tone/NJR_NJU7391A.pdf) | Nisshinbo、18 頁、2026-09-26 取得 |
| NJW1192 / NJW1201A（除外） | I²C の音量＋トーン、バイパス無し | [tone/NJR_NJW1192.pdf](tone/NJR_NJW1192.pdf)・[tone/NJR_NJW1201A.pdf](tone/NJR_NJW1201A.pdf) | Nisshinbo、2026-09-26 取得 |
| BD37033FV-M / BD37512FS / BD3490FV / BD3491FS（除外） | I²C のサウンドプロセッサ、バイパス無し | [tone/ROHM_BD37033FV-M.pdf](tone/ROHM_BD37033FV-M.pdf)・[tone/ROHM_BD37512FS.pdf](tone/ROHM_BD37512FS.pdf)・[tone/ROHM_BD3490FV.pdf](tone/ROHM_BD3490FV.pdf)・[tone/ROHM_BD3491FS.pdf](tone/ROHM_BD3491FS.pdf) | fscdn.rohm.com、2026-09-26 取得 |
| PT2033（参考） | I²C の音量＋トーン、バイパス無し（PT2314E より振幅の余裕） | [tone/Princeton_PT2033.pdf](tone/Princeton_PT2033.pdf) | princeton.com.tw、V1.4 2010-09（15 頁） |
| PT2322（参考） | 6 ch、"Tone Defeat" | [tone/Princeton_PT2322_excerpt.pdf](tone/Princeton_PT2322_excerpt.pdf) | nikom.biz のミラー、v1.0 2002-11 の **3 頁抜粋**（EC 無し） |
| TDA7439 / TDA7468（除外） | I²C の音量＋トーン、バイパス無し | [tone/ST_TDA7439.pdf](tone/ST_TDA7439.pdf)・[tone/ST_TDA7468.pdf](tone/ST_TDA7468.pdf) | **ミラー**（ampslab.com Rev.10 2004-06／mikroe Rev.4 2010-04）。st.com は取得失敗 |
| BD37534FV（除外、BD375xx 家族の代表） | 車載 I²C の 3 バンド、バイパス無し（調査は [../review/tone_chip_newer.md](../review/tone_chip_newer.md)） | [tone/ROHM_BD37534FV.pdf](tone/ROHM_BD37534FV.pdf) | fscdn.rohm.com、16.Dec.2015 Rev.001、2026-09-26 取得 |
| TDA7719（除外、参考） | 車載 I²C の 3 バンド、"Direct path"（フィルタと音量を飛ばす） | [tone/ST_TDA7719.pdf](tone/ST_TDA7719.pdf) | **ミラー**（rlocman.ru）、Doc ID 13698 Rev 4 2009-04。st.com は取得失敗 |
| PCM1863（別の道 (b)） | ADC、単端 2.1 Vrms FS、TSSOP-30 | [tone/TI_PCM186x.pdf](tone/TI_PCM186x.pdf) | ti.com、SLAS831D（2018-03 改訂）、2026-09-26 取得 |
| PCM5122（別の道 (b)） | DAC、2.1 Vrms 出力、内蔵の biquad、TSSOP-28 | [tone/TI_PCM512x.pdf](tone/TI_PCM512x.pdf) | ti.com、SLAS763C（2018-10 改訂）、2026-09-26 取得 |
| ADAU1701（別の道 (b)） | SigmaDSP（ADC 2・DAC 4）、LQFP-48 | [tone/ADI_ADAU1701_Rev0.pdf](tone/ADI_ADAU1701_Rev0.pdf) | **Digi-Key のミラー、Rev. 0（2006-10）＝旧版**。analog.com は取得失敗 |
| MCP41HV51（別の道 (a)） | ±18 V のデジタルポテンショメータ（7/8 bit、SPI）、TSSOP-14 | [tone/Microchip_MCP41HVX1.pdf](tone/Microchip_MCP41HVX1.pdf) | ww1.microchip.com、DS20005207B（2013–2015）、2026-09-26 取得 |
| **Alps RK27112A00CF** ×2 | HP / LINE 手回し音量（A50k Dual） | （メーカーカタログ） | [PARTS.md](../PARTS.md) |
| **Cosland 2MD1 / 2MS1** | DEST（DPDT ON–ON）／PWR | （秋月の商品ページ） | [PARTS.md](../PARTS.md) §2.1 |
| ~~PGA2310PA~~ | **不採用**（DECISIONS `V21-継-02`） | [TI_PGA2310.pdf](TI_PGA2310.pdf) | TI |

## アンプ切替

v2.1 は娘ごとの電源用・音声用ラッチングリレー（1 段目）と、娘の中の TMUX7612（2 段目）の 2 段（DECISIONS §2）。

| 部品 | 用途 | ローカル | 取得元 |
|---|---|---|---|
| **TMUX7612** | 娘の中で ch を選ぶ（4回路SPST） | [TI_TMUX7612.pdf](TI_TMUX7612.pdf) | [TI TMUX7612](https://www.ti.com/lit/ds/symlink/tmux7612.pdf) |
| **AZ850P2-5** | ラッチング DPDT（5 V コイル）。娘の電源用・音声用（DECISIONS §2-2） | [Zettler_AZ850.pdf](Zettler_AZ850.pdf)（[detect/AmericanZettler_AZ850.pdf](detect/AmericanZettler_AZ850.pdf) も） | Zettler |
| **TBD62083A** | コイル駆動（DMOS。ULN2803A とピン互換） | [Toshiba_TBD62083A.pdf](Toshiba_TBD62083A.pdf) | Toshiba |
| **MCP23017** | I²C GPIO 拡張（UI・娘。娘に残すかは V21-未決-03） | [Microchip_MCP23017.pdf](Microchip_MCP23017.pdf) | [Microchip DS20001952C](https://ww1.microchip.com/downloads/en/devicedoc/20001952c.pdf) |
| ~~ULN2803A~~ | コイル駆動（**不採用**） | [ST_ULN2803A.pdf](ST_ULN2803A.pdf) | ダーリントンの約 1 V 降下が 5 V レールの 20 % を食い、40 ℃ で仕様割れ |

## UI・MCU

| 部品 | 用途 | ローカル | 取得元 |
|---|---|---|---|
| ~~SSD1306 / SSD1309~~ | 制御 OLED（**廃止**。図・PCB に無い） | [Solomon_SSD1306.pdf](Solomon_SSD1306.pdf) | — |
| **WAVESHARE-29318** | スペアナ 3.5″ タッチ LCD（ST7796S + FT6336U） | （Wiki） | [スイッチサイエンス 10138](https://www.switch-science.com/products/10138)。状態表示もここ |
| **RP2350** | Pico 2 | [RaspberryPi_RP2350.pdf](RaspberryPi_RP2350.pdf) | [Raspberry Pi RP2350](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf) |
| **ロータリ ENC ×3** | CH / BASS / TREBLE | [RotaryEncoder_EC11_generic.md](RotaryEncoder_EC11_generic.md) | 押し SW 付き EC11（DECISIONS `V21-継-01`） |

## 計測

| 部品 | 用途 | ローカル | 取得元 |
|---|---|---|---|
| **PCM1804** | 計測 ADC | [TI_PCM1804.pdf](TI_PCM1804.pdf) | [TI PCM1804](https://www.ti.com/lit/ds/symlink/pcm1804.pdf) |

## 未収録（回路起こし時に追加）

- PD モジュールの差し替え候補（CH224 以外を試す場合）
- 購入 ENC のメーカー寸法図（フットプリント作成時）
- Alps RK27 の紙 DS（メーカーページで足りる。必要なら追加）

## 更新

- 2026-09-25: v2.1 の索引に書き直した。手持ちオペアンプの DS（`opamps/`）と `TMR9`・`TMR6` を v1 の置き場から写した。v2 の決定ログへのリンクを外した
- それより前の更新履歴は v2 のもの（git の履歴にある）
