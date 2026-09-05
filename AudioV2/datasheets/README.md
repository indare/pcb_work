# AudioV2 予定部品 — データシート

設計判断（[DECISIONS.md](../DECISIONS.md)）で確定・想定している部品の一次資料。オフライン参照用にローカル PDF を置く。

## 電源・PD

| 部品 | 用途 | ローカル | 取得元 |
|---|---|---|---|
| **[50224] CH224** | USB-PD（PowerModule 内蔵） | [StrawberryLinux_CH224K_manual.pdf](StrawberryLinux_CH224K_manual.pdf) 他 | AudioV2 PowerModule **再設計**に統合 |
| **DKMW20F-15** | ±15 V DC-DC（AudioV2 PowerModule） | [MeanWell_SKMW20_DKMW20.pdf](MeanWell_SKMW20_DKMW20.pdf) | [Mean Well SKMW20/DKMW20](https://www.meanwell.com/webapp/product/search.aspx?prod=DKMW20)。F-15 は ±15 V / ±660 mA。2026-09-01 に F-12(±12 V) から変更 |
| **BP5293-50** | 操作板 +5 V（Controll 系） | [ROHM_BP5293-xx.pdf](ROHM_BP5293-xx.pdf) | [ROHM BP5293-xx](https://www.rohm.com/products/power-management/switching-regulators-integrated-fet/bp5293-xx-series) |

### DC-DC の候補（2026-09-05 の再探索。**採否は未決**）

`dcdc_survey.py` で 431 件を引き、±12 V 両レール・MOQ 1・在庫あり・12 V 入力対応の
220 件から実読した分。**選定の決め手になる `Cout`（最大容量負荷）・軽負荷での `Fsw` の
扱い・絶縁容量・最小負荷は、どれも DigiKey API には無くデータシートにしかない。**
だからここに置いてある。経緯と比較は [DECISIONS.md](../DECISIONS.md)。

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
（[DECISIONS.md](../DECISIONS.md) の否定側査読）。**Aimtec 2品は 2000 pF で Recom / Cincon の2倍。**
安いのはこの2品だが、**この設計がいちばん気にしている欄で最下位**にいる。

**`+9V` の三端子レギュレータ**（±12 V 化の障害③に直結）:

| 部品 | ローカル | この設計に効く数字 |
|---|---|---|
| **NJM7809FA**（日清紡マイクロデバイス） | [NJR_NJM7800.pdf](NJR_NJM7800.pdf)（`Ver.1.2`） | **規定入力範囲の下限は 11.5 V**（p3、Line Regulation の試験条件が `VIN=11.5 to 25V, IO=0.5A`）。**ドロップアウト特性のグラフは NJM7805 と NJM7812 にしかなく、7809 には無い**（p8-9）＝ 30 mA 級での規定が無い。`IQ` typ 4.3 / max 6.0 mA、絶対最大入力 35 V |

**⚠ 上の値は2版で照合済み。** 旧 `Ver.2007-05-16`（New JRC 表記）と現行 `Ver.1.2`（日清紡）を
突き合わせたところ、**NJM7809 の行は 19 年間まったく変わっていない** —— 出力 8.65/9.0/9.35 V、
`VIN=11.5 to 25V`、`IQ` 4.3/6.0 mA、絶対最大 35 V、**7809 のドロップアウト曲線が無いことまで同じ**。
違ったのは絶対最大定格のモデル群の括り方（`7805 to 7809` → `7805 to 7810`）と
パッケージ表記（`DL1` → `DL1A`）だけ。**旧版はリポジトリに置かない**（同じ事実を2箇所に
置くと片方が腐る。[SOURCE_OF_TRUTH.md](../../SOURCE_OF_TRUTH.md)）。

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
| `Fsw` | `CCG-D`: **430 kHz**（**負荷条件の記載なし。表に全負荷の見出しも無い**） | カタログ p3 |
| **絶縁容量** | **⚠ 非公表。** あるのは Withstand Voltage（入出力間 1,500 Vdc）と Isolation Resistance だけ | カタログ p3 |
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

| **EC4SBW**（Cincon） | [Cincon_EC4SBW.pdf](Cincon_EC4SBW.pdf) | `24D15`=**650 µF/レール**（p1） | **p1 features に "Fixed Switching Frequency" を明記**。3.3/5V は 270 kHz typ（p2） | **1500 pF typ**（p2） | **0 mA**（p1） | 89 % |

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
| **PT2314 DIP-28** | Bass / Treble（I²C、Amp 前） | [Princeton_PT2314.pdf](Princeton_PT2314.pdf) | Princeton Technology PT2314 v1.1 |
| **Alps RK27112A00CF** ×2 | HP / LINE 手回し音量（A50k Dual） | （メーカーカタログ） | [PARTS.md](../PARTS.md) |
| **C&K 7303SYZQE** | DEST 3PDT ON-OFF-ON | [C&K 7000 Series](https://media.digikey.com/pdf/Data%20Sheets/C&K/7000%20Mini%20Toggle%20Series.pdf) | [PARTS.md](../PARTS.md) |
| ~~PGA2310PA~~ | **不採用**（調査アーカイブ） | [TI_PGA2310.pdf](TI_PGA2310.pdf) | [VOLUME_IC_COMPARISON.md](../VOLUME_IC_COMPARISON.md) |

## アンプ切替（統合1枚基板）

2026-09-01 にアーキテクチャを刷新し、リレー盤とアンプ基板を1枚へ統合した（[DECISIONS.md](../DECISIONS.md) §11.1）。
切替はラッチングリレーからアナログスイッチICへ変更。

| 部品 | 用途 | ローカル | 取得元 |
|---|---|---|---|
| **TMUX7612** | **アンプ入出力の切替**（4回路SPST、1パッケージ=1ch） | [TI_TMUX7612.pdf](TI_TMUX7612.pdf) | [TI TMUX7612](https://www.ti.com/lit/ds/symlink/tmux7612.pdf) |
| **MCP23017** | I²C GPIO 拡張（切替IC の制御、10本） | [Microchip_MCP23017.pdf](Microchip_MCP23017.pdf) | [Microchip DS20001952C](https://ww1.microchip.com/downloads/en/devicedoc/20001952c.pdf) |

### 不採用（調査アーカイブ）

ラッチングリレー方式で検討した部品。経緯は [AGENT_HANDOFF.md](../AGENT_HANDOFF.md) §2.7-3 / §2.9。

| 部品 | 検討内容 | ローカル | 不採用の理由 |
|---|---|---|---|
| ~~AZ850P2-5~~ | ラッチング DPDT（5 V コイル） | [Zettler_AZ850.pdf](Zettler_AZ850.pdf) | 1枚統合でリレーは面積を食いすぎる。コイル 125 Ω / Must Operate 3.75 V の実値は §2.7-3 の検算根拠 |
| ~~ULN2803A~~ | コイル駆動 | [ST_ULN2803A.pdf](ST_ULN2803A.pdf) | ダーリントンの約1 V 降下が 5 V レールの20%を食い、40 ℃ で仕様割れ（§2.7-3） |
| ~~TBD62083A~~ | ULN2803A のドロップイン代替（DMOS） | [Toshiba_TBD62083A.pdf](Toshiba_TBD62083A.pdf) | コイル駆動マージンは解決したが、リレー方式ごと不採用になった。RON 2.0 typ / 3.25 max Ω、ピン配置は ULN2803A と完全一致 |

## UI・MCU

| 部品 | 用途 | ローカル | 取得元 |
|---|---|---|---|
| **SSD1306 / SSD1309** | 制御 OLED 128×64 I²C（**2.42″** 第一） | [Solomon_SSD1306.pdf](Solomon_SSD1306.pdf) | v1 `Control/`。[PARTS.md](../PARTS.md) AliExpress 例 |
| **WAVESHARE-29318** | スペアナ 3.5″ タッチ LCD（ST7796S + FT6336U） | （Wiki） | [スイッチサイエンス 10138](https://www.switch-science.com/products/10138)。`Audio/measurement_fw/` |
| **RP2350** | Pico 2 | [RaspberryPi_RP2350.pdf](RaspberryPi_RP2350.pdf) | [Raspberry Pi RP2350](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf) |
| **ロータリ ENC ×3** | CH / BASS / TREBLE | [RotaryEncoder_EC11_generic.md](RotaryEncoder_EC11_generic.md) | **GPIO 直結**（§10）。押し SW 付き EC11 |

## 計測（独立・参考）

| 部品 | 用途 | ローカル | 取得元 |
|---|---|---|---|
| **PCM1804** | 計測 ADC | [TI_PCM1804.pdf](TI_PCM1804.pdf) | [TI PCM1804](https://www.ti.com/lit/ds/symlink/pcm1804.pdf) |

## AudioV2 に置かないもの（`Audio/` 流用）

- **AmpModule / HeadphoneBuffer** のオペアンプ → [Audio/datasheets/opamps/](../../Audio/datasheets/opamps/README.md)（手持ち在庫のローカル PDF）
- 計測フロントの **OPA1656** も同ディレクトリ（`TI_OPA1656.pdf`）。AudioV2 には複製しない

## 未収録（回路起こし時に追加）

- PD モジュールの差し替え候補（CH224 以外を試す場合）
- 購入 ENC のメーカー寸法図（フットプリント作成時）
- Alps RK27 / C&K 7000 の紙 DS（メーカーページで足りる。必要なら追加）

## 更新

- 2026-08-30: 初回一括取得
- 2026-08-30: CH224 [50224]、ENC 機械仕様、Amp/HP 流用方針。OPA1656 削除
- 2026-08-30: ENC×3 **GPIO 直結**確定（§10）
- 2026-08-30: 表示 — 制御 OLED 2.42″ / スペアナ Waveshare 29318（v1）
- 2026-08-31: Amp/HP OPA DS は `Audio/datasheets/opamps/` を正と明記
- 2026-09-05: ±12 V DC-DC 候補の一次資料7点（Aimtec ×2 / MEAN WELL / Cincon ×2 / Traco ×2）。`Cout`・軽負荷 `Fsw`・絶縁容量は API に無いため
- 2026-09-05: **上の表を訂正。** ブラインド再抽出で 2 件の誤りが出た —— ①Aimtec 2品の絶縁容量を「記載なし」としていたが **2000 pF が明記されている**（AM10TW p2 / AM15CW p3）。②Recom の 350 kHz を「条件の但し書きなし」と書いたが、実際は **Max. 列**で、軽負荷での低下と矛盾しない
- 2026-09-05: **否定側査読で `REC20K-Z` の見落としが出た**（`2415DZ`=±3000 µF / `2412DZ`=±4000 µF）。あわせて `Fsw` 欄の比較が無意味だったこと（全社が全負荷規定。Recom は表の見出しに書いている）を反映
- 2026-09-05: 不採用確定の一次資料3点（Mornsun ×2 / CUI PYBE10）。落選根拠がデータシートの一文なので置く。TDK-Lambda `CCG` は取得不能と確定（実ブラウザでも 403）
- 2026-09-05: `NJM7809FA`（日清紡）。ST 純正 `L7809` は入手不能・`st.com` も不通なので、`+9V` の入力範囲は実際に買える石で評価する
- 2026-09-05: 第2ラウンドの査読で `Cincon EC4SBW` を追加、TDK「取得不能」の記述と `RC` の裏取り経緯を訂正
