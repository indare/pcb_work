# NJW1194 の代替 — 広く探した記録（調査中）

（結論の表は調べ終わってからここに置く）

- 作成: 2026-09-26（部品調査のエージェント）。書いたのはこのファイルと `datasheets/tone/`・`datasheets/README.md` の行だけ
- 状態: **調査中**（書きながら埋めている）
- 前の調査: [tone_chip_bypass.md](tone_chip_bypass.md)・[tone_chip_bypass_review.md](tone_chip_bypass_review.md)（末尾の在庫の追記を含む）・[tone_chip_newer.md](tone_chip_newer.md)・[tone_options_compare.md](tone_options_compare.md)。そこで見た品番は「既出」として並べるだけで、DS を読み直さない
- 凡例: 〔DS 品名 p.n〕＝`datasheets/tone/` の PDF（`pdftotext -layout`）。〔推論〕〔仮定〕〔計算〕。「確かめられず」＝DS を取れなかったか、DS に書かれていない。在庫は JLCPCB の部品検索 API（`selectSmtComponentList`、keyword 検索）で 2026-09-26 に取った値
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

## 候補の一覧（調べる順。1 品調べるたびに行を埋める）

| 候補 | 出どころ | 状態 | T | S | F | A | C | P | JLC 在庫（2026-09-26） | 一言 |
|---|---|---|---|---|---|---|---|---|---|---|
| NJW1194 | 既出（基準） | 既出 | ○ | ○ TSW | ○ 0.5 dB | ○ 3.6 min | 3 線 | SSOP32 | 0（C5184872、min 4） | 基準 |
| NJW1119A・NJU7391A・NJW1192・NJW1201A | 既出 | 既出 | | | | | | | | 前の調査のまま |
| PT2314E・PT2033・PT2322 | 既出 | 既出 | | | | | | | | |
| BD37033FV-M・BD37512FS・BD3490FV・BD3491FS・BD375xx・BD37034FV-M・BD347xx・BD34602FS-M・BD37068/69 | 既出 | 既出 | | | | | | | | |
| TDA7439・TDA7468・TDA7719・TDA7419 | 既出 | 既出 | | | | | | | | |
| TM2313・TM2314 | 既出 | 既出 | | | | | | | | |
| MCP41HV51・AD5292・NJU72322・MUSES72323・NJU72343・NJU72344・NJU72315 | 既出（(a) の部品） | 既出 | | | | | | | | |
| PCM1863＋PCM5122・ADAU1701・CS42L52・LM1036 | 既出（(b)・除外） | 既出 | | | | | | | | |

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
- 入手性: JLCPCB `BD3814FV-E2` C2662555 **在庫 10**、最小 1（2026-09-26）
- 読み〔推論〕: 機能の並び（音量→トーン＋スルー→バッファ）、±7 V、3.6 Vrms min は NJW1194 とほぼ同じ。**NJW1194 より良い点**: 制御が 2 本、バイパスの雑音に max、在庫がある。**悪い点**: トーンが ±14 dB／2 dB（NJW1194 は ±10 dB／1 dB）、音量は 1 dB 刻み（NJW1194 は 0.5 dB）、ゼロクロスの記載なし、**符号表が DS に無い**（どの値でバイパスかを実物で確かめる必要）、DS は 2010 年の Technical Note で現行品かは確かめられず（rohm.com の頁は取れず）、SSOP-B40 は 6 ch 分の足があって大きい
