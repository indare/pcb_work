# NJW1194 の代替 — 広く探した記録

| 候補 | T トーン | S スルー | F フェード | A 2.3 Vrms | C 制御 | P パッケージ | 在庫（2026-09-26） | 一言 |
|---|---|---|---|---|---|---|---|---|
| NJW1194（基準） | ○ ±10 dB／1 dB | ○ `TSW` | ○ 0.5 dB（ゼロクロスの効きは不明） | ○ VOM 3.6 min（±7 V） | 3 線 | SSOP32 | JLC 0・LCSC API 0／Digi-Key Active・最小 2,000・12 週 | 基準（前の調査） |
| **BD3814FV**（ROHM） | ○ ±14 dB／2 dB（FL/FR だけ）〔DS p3〕 | ○ "Tone: By-pass"・D8 "Tone"〔DS p2・p5・p6〕。**0/1 の意味は DS に無い** | △ 1 dB 刻み・ゼロクロスの記載なし。MUTE 端子あり〔DS p1・p6〕 | ○ Vomax 3.6 min（±7 V）〔DS p2〕 | ○ 2 線、VIH 2.2 V〔DS p4〕 | SSOP-B40 | JLC 10・LCSC 10／**Digi-Key Obsolete** | **機能は NJW1194 とほぼ同じ並び**。ただし製造終了・残り 10 個・符号表なし |
| BD3813KS（ROHM） | ○ ±14／2 dB | ○ "Tone Bypass"〔DS p1・p3〕 | △ 同上 | ○ 3.4 min | ○ 2 線 | **SQFP56** | 0 | 兄弟品。QFP・在庫 0 で除外 |
| 組 C1: PT2314E＋DIRECT リレー＋**NJU72343** | ○（PT2314E） | リレー | ○ **0.5 dB＋ゼロクロス、POR で MUTE**〔NJU72343 p1・p10・p13〕 | トーン経由は PT2314E の 2.3 min のまま／DIRECT は ○ 3.6 min | I²C 形式の 2 線、VIH 2.5 V〔p4・p9〕 | SSOP32 | NJU72343: **Digi-Key Active・在庫 14,697・最小 1**、LCSC 29 | **次善の本命**。±7 V が要る（NJW1194 と同じ） |
| 組 C2: PT2314E＋DIRECT リレー＋**PGA2320／PGA2310** | ○（PT2314E） | リレー | ○ 0.5 dB＋ゼロクロス（16 ms で打ち切り）、POR で MUTE〔PGA2320 p7・p10〕 | ○ ±15 V で約 ±14 V まで〔p3、計算〕 | 3 線 SPI＋5 V の VD+〔p3〕 | SOIC-16 | PGA2320 LCSC 6（TI Active・在庫切れ）、PGA2310 LCSC 76（TI Active） | ±15 V のまま動く。雑音 10.5 µV typ は大きめ |
| 組 C3: 自作トーン（±15 V）＋リレーのスルー＋NJU72343 か PGA2310 | ○（自作） | リレー（自作の中） | ○（C1・C2 と同じ） | ○ | — | — | 部品はどれもある | トーンの頭の天井も消えるが、設計と部品が最も多い |
| PT7313E・TM2348・TDA7718N・TDA7418・BD3702FV ほか | ○ | × | — | ×〜△（PT7313E は 2.3 min で PT2314E と同じ） | I²C | SOP/SSOP | 在庫あり | バイパス無し・振幅は PT2314E 以下（BD3702FV は DS のフォント欠けで読めず、確かめられず） |

**NJW1194 と同等以上の単体の石は、見られた範囲では「無い」。** 機能がいちばん近いのは ROHM **BD3814FV**（音量→トーン＋スルーのスイッチ→バッファの並び、±7 V、3.6 Vrms min、2 線で 3.3 V 可、バイパスの雑音に max がある）だが、**Digi-Key で Obsolete、流通は LCSC/JLC の 10 個だけ**、トーンのバイパスがどの符号かが DS に書かれていない。量産の少ない 1 台物なら「10 個を今押さえる」手はあるが、壊したときの替えが効かない〔推論〕。
**次善は組 C1（PT2314E＋DIRECT のリレー＋NJU72343）**: NJU72343 は現行（Digi-Key 在庫 14,697、最小 1）で、±7 V・VOM 3.6 min・0.5 dB・ゼロクロス・POR で MUTE。`TONE` バスの手前（トーンと DIRECT の切替の後ろ）に置けば、NJW1194 の「どの経路でも音量で段階に絞れる」を 2 個で作れる〔推論〕。NJW1194 に負けるのは、トーン経由の振幅が PT2314E の 2.3 Vrms min のまま残ることと、DIRECT のリレーが要ること。±7 V を作る手間は NJW1194 と同じ。±7 V を作りたくなければ組 C2（PGA2310/PGA2320、±15 V 直、ただし雑音が大きく 5 V も要る）。
- 外れる条件: BD3814FV の符号表が ROHM から取れて在庫が 10 個以上確保できる／1 台物で替えが要らない → BD3814FV が 1 位。NJU72343 を置く位置の雑音・歪み（1.41 µV typ、0.0004 % typ〔p3〕）が許せない、または聴く経路に石を 1 段足すこと自体を嫌う → 組 C1・C2 は崩れ、PT2314E＋リレー（前の査読の P）か NJW1194 を待つ

- 作成: 2026-09-26（部品調査のエージェント）。書いたのはこのファイルと `datasheets/tone/`・`datasheets/README.md` の行だけ
- 状態: 調査済み（査読前）。ユーザーの判断の材料
- 前の調査: [tone_chip_bypass.md](tone_chip_bypass.md)・[tone_chip_bypass_review.md](tone_chip_bypass_review.md)（末尾の在庫の追記を含む）・[tone_chip_newer.md](tone_chip_newer.md)・[tone_options_compare.md](tone_options_compare.md)。そこで見た品番は「既出」として並べるだけで、DS を読み直さない
- 凡例: 〔DS 品名 p.n〕＝`datasheets/tone/` の PDF（`pdftotext -layout`、ブロック図と制御語は `pdftoppm` の画像で確かめた）。〔推論〕〔仮定〕〔計算〕。「確かめられず」＝DS を取れなかったか、DS に書かれていない。在庫は JLCPCB の部品検索 API（`selectSmtComponentList`）と LCSC の製品 API で 2026-09-26 に取った値。[DEC] §n = `AudioV2.1/DECISIONS.md`
- `AudioV2/`・`Audio/` の文書は読んでいない

## 求める機能（NJW1194 が満たしていること）

| 記号 | 中身 |
|---|---|
| T | Bass/Treble の 2 バンド以上のトーン |
| S | トーン段を通さない経路（バイパス／ディフィート／ダイレクト）。無い品は「リレーを足せば使える」組として別枠 |
| F | 切替の前後に信号をなめらかに絞れる音量段（ゼロクロス・ソフトミュートで加点） |
| A | ライン入力 2.3 Vrms 以上（最大入力・最大出力の min） |
| C | 3.3 V の Pico から I²C／SPI／3 線（UI の MCP23017 の空き 5 本でも可） |
| P | 手はんだできるパッケージ（SOP/SSOP/TSSOP/DIP。QFN は減点） |
| B | 入手できる |

## 既出の品（前の調査のまま。DS は読み直していない）

- トーン付き: NJW1119A・NJU7391A・NJW1192・NJW1201A・PT2314E・PT2033・PT2322・BD37033FV-M・BD37512FS・BD3490FV・BD3491FS・BD375xx・BD37034FV-M・TDA7439・TDA7468・TDA7719・TDA7419・TM2313・TM2314
- 音量だけ・別の道: BD347xx・BD34602FS-M・BD37068/69・MCP41HV51・AD5292・NJU72322・MUSES72323・NJU72344・NJU72315・PCM1863＋PCM5122・ADAU1701・CS42L52・LM1036
- このうち NJU72343 は前の調査で名前だけ出ていた（Nisshinbo の一覧）。今回 DS を読んだのは新しい事実として下に書いた

## 組み合わせの注意〔推論〕

- 組 C1・C2 の音量 IC は、NJW1194 と同じく**聴く経路に常に居る**（スルーでも通る点は NJW1194 と変わらない）。0 dB で使えば EC の条件どおり
- NJU72343 を UI の I²C バスに載せると、今の PT2314E と同じく、UI の MCP を読むたびに SCL/SDA のエッジが音声チップの足に来る（[DEC] §2-12 の考えとは逆向き）。UI の MCP の空きピンで別の 2 線を bit-bang する手もある〔推論、未検討〕
- NJU72343 の注意書きは NJW1194 と同じ形（電源投入前の信号で初期状態がおかしくなりうる、切る前に MUTE）〔NJU72343 p10〕
- BD3814FV を採るなら: 電源は **VEE を先に（または同時に）**〔DS p1・p8〕。D8 の意味・POR の状態は実物で確かめる。トーンの切替は「セット側で MUTE」〔DS p8〕（NJW1194 と同じ注。前の査読 M5 の読みがそのまま当たる）

## 作業ログ

### JLCPCB の網（2026-09-26）

- 汎用の語（"tone control"・"bass treble"・"sound processor"・"audio processor"・"音调"・"音效处理"）は keyword 検索では当たらない（語が分かち書きされて別分類の品が出るか、0 件）。**当たるのは JLCPCB の説明文の語 "Volume Control"（Audio Interface ICs の 59 件）**
- JLCPCB の分類 "Audio Interface ICs" に出る品を、説明文の語（"Volume Control"・"Attenuator"）と品番の頭（PT23/PT22/PT20・TM23・AiP・LC753/754/757・M624/M615/M622・BD34/37/38/39・BH35・BA38・NJW11/12・NJU72/73・NJM21・TDA73/74/77/84/15・TEA63・TC94・TA20・SC73/SC23・CD23・HT23・HS23・WS23・CS23・FM23・PGA23/21/43・MAS91・LM197・LMC199・DS180・THAT21・MUSES・R2A15/R2S15・YDA/YSS・SSM21・GR62・MX23・JL23 ほか、"2313"・"2314"・"2322"・"2348"・"7313"・"7439"・"7440"）で網を掛けた。Audio Interface ICs に出た約 300 件を見た
- **在庫が 1 以上で、トーンか音量を持つ品**（2026-09-26）: PT2314E 116・PT7313E 250・PT2033 1・PT2258-S 936・PT2259-S 217・TM2313 1001（SSOP 版 39）・TM2312 103・TM2314 1・**TM2348 1523**・**BD3814FV 10**・**BD3702FV 100**・BD37534FV 10・BD34602FS-M 5・**TDA7718N 45**・**TDA7418 20**・TDA7440D 20・**NJU72343 33**・**NJU72342 55**・NJW1195A 12（C42855428、JRC 名義、説明なし）・AiP2358 91・M62429（Wuxi I-core）221／L 3261・LM1971 18・PGA2311UA/1K 105・PGA2311U/1K 86・**PGA2310UA/1K 76**・**PGA2320IDWR 7**・PGA4311U 1・DS1882Z-050+ 4・R2S15902FP(LX)（lingxingic、LQFP-44）318
- 在庫 0 で目を引いたもの: NJW1111／NJW1112／NJW1110（Nisshinbo、SSOP32。NJW1111・NJW1110 は DS で **9 入力 3 出力のセレクタ**＝トーン無し〔LCSC の DS p1〕）、LC75341〜LC75386・LC75412（onsemi/Sanyo、多くが "no longer manufactured"）、M615xx・M624xx・R2A15xxx・R2S15xxx（Renesas、ほぼ全部 "no longer manufactured"）、TDA73xx〜TDA74xx の旧品、CS3310/CS3318/CS3308、SSM2160、MUSES72320・MUSES72323・NJU72322

### ROHM BD3814FV — **バイパスあり・±7 V・3.6 Vrms min**。`datasheets/tone/ROHM_BD3814FV.pdf`（Technical Note No.10081EAT05、2010.06 Rev.A、本文 10 頁＋注意書き、LCSC の写し。rohm.com の元の URL は 404）

- 構成: 6 ch の電子ボリューム（0〜−95 dB／1 dB、MUTE、ch ごと独立）、**FL/FR だけに Bass/Treble**、別に汎用オペアンプ 2 個〔DS p1・p6〕
- **バイパス**: 応用回路（ブロック図を兼ねる）で、FL/FR は 入力 → 音量（Ri 20 kΩ のラダー）→ **2 接点のスイッチ（ワイパ直／BASS→TREBLE の戻り）** → バッファ → OUTFL/OUTFR と描かれている〔DS p6 画像〕。NJW1194 と同じ並び（音量が前、トーン＋スルーのスイッチが後ろ）。制御語 ① の D8 が "Tone"（1 bit）〔DS p5 画像〕。EC の条件に "Tone: By-pass" と "Tone: ON" の行がある〔DS p2・p3〕。注意書き 10 "Tone bypath switching — For tone bypath switching, use MUTE on the set."〔DS p8〕
  - **D8 の 0/1 のどちらがバイパスか、Bass/Treble・音量の符号表は、この DS に無い**（制御語の枠だけ）→ 確かめられず。電源投入時の既定も無い（"At power-on sequence, initialize all data."〔DS p5〕）
- 性能（EC の共通条件: ±7 V、1 kHz、Vin 1 Vrms、RL 10 kΩ、Rg 600 Ω、音量 0 dB、Bass/Treble 0 dB）〔DS p2〕:
  - 最大出力 Vomax1 **3.6 min / 4.3 typ Vrms**（THD 1 %）。どの条件（バイパスか ON か）かは行に書かれていない〔DS p2〕
  - THD1 **0.001 typ / 0.03 max %**（BW 400 Hz–30 kHz）。行に Tone の指定が無く、共通条件は "Bass and Treble=0dB"（＝トーン ON のフラットと読める〔推論〕）
  - 出力雑音 Vno1（FL/FR）**バイパス 1.0 typ / 6.0 max µVrms**、ON 1.7 typ / 10 max µVrms（Rg 0、IHF-A）。残留雑音 Vnom1 もバイパスで 1.0 / 6.0 µVrms〔DS p2・p3〕→ **バイパスの雑音に max がある**（NJW1194 の TONE=OFF の雑音は typ だけ）
  - ch 間クロストーク −95 typ / −80 max dB（Rg 0）〔DS p2〕
  - 音量の誤差 ±1.5 dB（0〜−53 dB）・±2.5 dB（−54〜−95 dB）、最大減衰 −115 typ / −105 max dB、**音量の試験は Vin 3 Vrms**〔DS p3〕
  - 入力インピーダンス 14 / 20 / 26 kΩ〔DS p3〕
  - Bass/Treble **±14 dB／2 dB**（100 Hz／15 kHz）、外付けの C・R（Bass 0.1 µ×2・4.7 k、Treble 4700 p）〔DS p3・p6〕
- 電源: 動作 **±5〜±7.3 V（typ ±7 V）**、絶対最大 ±7.5 V。電流 7 typ / 17 max mA（各レール）。**「VEE を先に、または同時に。VCC だけ先に上げると VCC→VEE に過電流」**〔DS p1・p8〕
- 入力の絶対最大: VCC+0.3〜VEE−0.3 V〔DS p1〕。±7 V なら 2.3 Vrms（3.25 Vpk）は内側〔計算〕
- 制御: **2 線シリアル（CL・DA。ラッチは DA 線で送る）**、"for both 3.3V and 5V"。VIH min 2.2 V・VIL max 1.0 V、IIH/IIL max 5 µA、各幅 min 2 µs〔DS p1・p2・p4〕。応用回路で CL/DA/MUTE に 10 kΩ の直列〔DS p6〕。**外付けの MUTE 端子（35 番）がある**〔DS p6〕が、MUTE の働き（何を落とすか・速さ）の説明は無い → 確かめられず
- なめらかさ: ゼロクロス・ソフトステップの語は DS に無い（"zero"・"soft" は出ない）。電源 ON/OFF は "a shock sound will be generated. Therefore, use MUTE on the set."〔DS p8〕
- パッケージ: SSOP-B40（JLCPCB の表記 SSOP-40-B）
- 入手性: JLCPCB `BD3814FV-E2` C2662555 **在庫 10**、最小 1（2026-09-26）。LCSC の製品 API（`wmsc.lcsc.com/ftps/wm/product/detail`）でも在庫 10（`productCycle` normal）。**Digi-Key（digikey.ca の製品頁、2026-09-26）は "Obsolete — This product is no longer manufactured."** → 流通在庫の 10 個が残りと読むのが安全〔推論〕
- 読み〔推論〕: 機能の並び（音量→トーン＋スルー→バッファ）、±7 V、3.6 Vrms min は NJW1194 とほぼ同じ。**NJW1194 より良い点**: 制御が 2 本、バイパスの雑音に max、在庫がある。**悪い点**: トーンが ±14 dB／2 dB（NJW1194 は ±10 dB／1 dB）、音量は 1 dB 刻み（NJW1194 は 0.5 dB）、ゼロクロスの記載なし、**符号表が DS に無い**（どの値でバイパスかを実物で確かめる必要）、DS は 2010 年の Technical Note で現行品かは確かめられず（rohm.com の頁は取れず）、SSOP-B40 は 6 ch 分の足があって大きい

### ROHM の同じ家族（"Sound Processors for Home Theater Systems"、±7 V・2 線）

- **BD3813KS／BD3815KS** — `datasheets/tone/ROHM_BD3813KS.pdf`（No.10081EAT04、2010.06 Rev.A、LCSC の写し）。5.1 ch、入力利得＋6 ch 音量（0〜−95 dB／1 dB）＋FL/FR の Bass/Treble ±14 dB／2 dB、**"Tone Bypass"**（特長 1)、EC の "Tone: By-pass" の行、制御語 2 の D8 が "TONE"）〔DS p1・p3・p6〕。Vomax1 **3.4 min / 4.2 typ Vrms**〔p3〕。±7 V、VEE を先に〔p2〕。2 線（3.3/5 V）〔p1〕。音量は「抵抗ラダーで残留雑音と切替のショック音を減らす」〔p1〕。"For functions except the Master Volume, Treble and Bass controls, use of the MUTE function is recommended."〔p15〕。**パッケージ SQFP56**〔p1・p17〕。符号表（D8 の 0/1 の意味）は**この DS にも無い**。JLCPCB `BD3813KS-E2` C2662580 在庫 0（2026-09-26）→ BD3814FV の兄弟として記録するだけ（QFP・在庫 0）
- **BD3812F** — 2 ch の音量だけ（0〜−103 dB／1 dB、出力利得、MUTE 端子）、Vomax 3.4 min / 4.2 typ Vrms、±7 V、2 線〔LCSC の DS p1・p2〕。**トーン無し**。SOP-14。JLCPCB C213438 在庫 0。(c)「フェード専用の音量 IC」の型だが在庫が無い
- **BD3816K1／BD3817KS** — 6.1 ch、"Volume Direct Mode"〔LCSC の DS p1〕、QFP、JLCPCB は "no longer manufactured"・在庫 0 → 読み込んでいない
- BD3811K1・BD3818KS（QFP、在庫 0、DS 取れず）→ 見ていない

### ほかに在庫のあった品（どれも除外。理由だけ）

| 品番 | DS（取った写し） | T | S | A（最大入力／出力の min） | 除外の理由 |
|---|---|---|---|---|---|
| BD3702FV（ROHM、SSOP-28、在庫 100） | LCSC の写し（10 頁）は**日本語フォントが欠けて読めず** | 3 バンド ±20 dB／1 dB（検索の要約。DS で確かめられず） | 確かめられず | 確かめられず | 車載の 7〜9.5 V 単電源の系統〔JLCPCB の説明〕で、既出の BD375xx と同じ形と読む〔推論〕 |
| PT7313E（Princeton、SOP-28、在庫 250） | LCSC の写し 16 頁 | ±14 dB／2 dB | **無い**（"bypass" は I²C の ACK の説明だけ〔DS p6〕） | VCL **2.3 min / 2.6 typ Vrms**〔DS p11〕 | PT2314E と同じ振幅・バイパス無し。PT2314E の代わりにはなるが改善ではない |
| TM2348（Titan Micro、SSOP36、在庫 1523） | LCSC の写し（中国語） | ±15 dB／1 dB（低音・高音）〔DS p1〕 | 語が無い（"旁路"・"直通" は出ない） | Vcl **2 min / 2.5 typ Vrms**〔DS p3〕 | 振幅不足（PT2348 の同構成品〔推論〕） |
| TDA7718N（ST、TSSOP28、在庫 45） | LCSC の写し（Doc ID 16502 Rev 2、40 頁） | 3 バンド | "Off (bypass)" は Anti-alias filter の設定〔DS p30〕。トーンを飛ばす設定は見当たらない | VCL **2 min Vrms**〔DS p9〕 | 振幅不足・バイパス無し |
| TDA7418（ST、SO20、在庫 20） | LCSC の写し 29 頁 | 3 バンド | 見当たらない（MUX ピンは "mono signal output (before tone filters)"〔DS p19〕） | VCL **1.8 min / 2 typ Vrms**〔DS p8〕 | 振幅不足 |
| NJW1110・NJW1111（Nisshinbo、SSOP32、在庫 0） | LCSC の写し | — | — | — | 9 入力 3 出力の**セレクタ**（トーン・音量無し）〔各 DS p1〕 |

### フェード専用の音量 IC（組み合わせ (c) の部品。トーンは持たない）

| 品番 | DS | 電源 | 振幅 | なめらかさ | 制御 | パッケージ | JLC 在庫（2026-09-26） |
|---|---|---|---|---|---|---|---|
| **PGA2320**（TI） | `datasheets/tone/TI_PGA2320.pdf`（SBOS312B、2004-12、LCSC の写し 22 頁） | **±15 V**（±4.5〜±15.5 V）＋VD+ 5 V〔p3〕 | 入出力の範囲 (VA−)+0.86〜(VA+)−0.86 V〔p3〕（±15 V で約 ±14 V〔計算〕）。THD+N 0.0003 typ / 0.001 max %（10 Vpp）、出力雑音 10.5 typ / 17.5 max µVrms〔p3〕 | **ゼロクロス**（ZCEN 端子で有効。2 回のゼロクロスか **16 ms のタイムアウト**で新しい利得を掛ける）〔p10〕、+31.5〜−95.5 dB／0.5 dB、MUTE 端子、**電源投入時は MUTE**（00h）〔p1・p7〕 | 3 線（SPI）、VIH min 2.0 V（VD+ 5 V）〔p3〕 | SOL-16〔p1〕 | `PGA2320IDWR` C2662546 **7**（`IDW` 0） |
| PGA2310（TI） | 既に `datasheets/TI_PGA2310.pdf`（v2 から写した DS。この調査では読み直していない） | ±15 V〔JLCPCB の説明〕 | — | ゼロクロス〔JLCPCB の説明 "Automatic mute/no-noise switch"〕 | 3 線 | SOIC-16 | `PGA2310UA/1K` C2651274 **76** |
| **NJU72343**（Nisshinbo） | `datasheets/tone/NJR_NJU72343.pdf`（Ver.2.6E、16 頁、Nisshinbo） | ±4.5〜±7.5 V（単電源 9〜15 V も可）〔p1〕 | **VOM 3.6 min / 4.2 typ Vrms**（±7 V、VOL 0 dB）、VIM 4.7 min Vrms（VOL −20 dB）〔p3〕 | **ゼロクロス**（09h の Z/C ビットで ON/OFF）〔p1・p13〕、+31.5〜−95 dB／0.5 dB、MUTE。**電源投入時は MUTE**（全レジスタ 0）〔p10〕。タイムアウトの記述は見ていない。THD 0.0004 typ / 0.01 max %（1 Vrms）、出力雑音 1.41 typ / 6.3 max µVrms（Rg 0、A 重み）〔p3〕 | **2 線だが形は I²C と同じ**（S・チップアドレス 80h/82h・各バイトの後に 1 bit・P。タイミングも I²C の記号）〔p8・p9〕、VIH min 2.5 V〔p4〕 | SSOP32（8 ch） | `NJU72343V-TE1` C5185453 **33** |
| **NJW1195A**（Nisshinbo） | `datasheets/tone/NJR_NJW1195A.pdf`（20 頁、Nisshinbo） | ±3.5〜±7.5 V（単電源 7〜15 V も可）〔p1・p3〕 | **VOM 3.6 min / 4.2 typ Vrms**（VOL 0 dB）〔p3〕 | "Zero Cross Detection"〔p1〕（効かせ方は読み込んでいない）、+31.5〜−95 dB／0.5 dB、MUTE、抵抗ラダー〔p1〕 | 3 線（NJW1194 と同じ形式〔推論〕）、VIH min 2.5 V〔p4〕 | SSOP32（4 ch＋4 入力 2 出力のセレクタ） | C42855428（JRC 名義）**12**、C22400328 0 |
| NJU72342（Nisshinbo） | 作業場で読んだ（Ver.0.8E）。`datasheets/` には置かない | 単電源 4.5〜14.5 V | **VOM 2.2 min / 2.6 typ Vrms**（V+ 9 V）〔p2〕→ 9 V では 2.3 Vrms を min で満たさない | ゼロクロス〔p1〕 | I²C | SSOP14 | C17554014 **55** |
| BD3812F（ROHM） | 上の ROHM の節 | ±7 V | Vomax 3.4 min | 記載なし（MUTE 端子あり） | 2 線 | SOP-14 | 0 |

- 置き方〔推論〕: トーンの段（PT2314E、または自作）と DIRECT の切替の**後ろ**、`TONE` バスの手前にこの音量を 1 段置けば、DIRECT でも通常でも「絞る → 全リセット → … → 戻す」を同じ手順でできる（NJW1194 が 1 個でやっていることを 2 個で）。代わりに**聴く経路に能動の段が 1 つ増える**
- PGA2320 は ±15 V のまま動くので ±7 V を作らずに済む〔推論〕が、出力雑音 10.5 µV typ は NJW1194 のバイパス（1.41 µV typ）や NJU72343 系より大きい。VD+ の 5 V が別に要る

### 入手性の追加（2026-09-26）

| 品番 | LCSC（製品 API `wmsc.lcsc.com/ftps/wm/product/detail`） | Digi-Key／メーカー | 読み |
|---|---|---|---|
| NJW1194V-TE1 | C5184872 **在庫 0**（国内・海外とも 0、`productCycle` normal、リール 2,000） | Digi-Key: **Active、在庫を持たない、最小 2,000 個、12 週**（digikey.com の検索頁） | ユーザーが LCSC の頁で見た「在庫あり・リードタイムつき」は、この API の在庫の数には出ていない（取り寄せの扱いと読む〔推論〕。こちらからは頁を読めず確かめられず） |
| BD3814FV-E2 | C2662555 **10** | Digi-Key: **Obsolete**（"no longer manufactured"） | 流通在庫だけ |
| BD3813KS-E2 | C2662580 0 | — | — |
| **NJU72343V-TE1** | C5185453 **29** | **Digi-Key: Active、在庫 14,697、最小 1、$3.96（1 個）** | 少量で正規に買える |
| NJW1195AV-TE1 | C42855428 **12**（JRC 名義） | Digi-Key の頁は取れず。Mouser は 503 | 確かめられず |
| NJU72342V-TE2 | C17554014 55 | — | — |
| PGA2320IDWR | C2662546 **6** | TI: **ACTIVE、TI の在庫は切れ**（ti.com の部品頁） | 少量はある |
| PGA2310UA/1K | C2651274 **76** | TI: **Active**、SOIC-16／PDIP-16、ゼロクロスあり（ti.com の製品頁） | 在庫あり |
| PT2314E | C90034 95（JLCPCB は 116） | — | 今の石 |
