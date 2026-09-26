# トーンチップの候補 — 新しめの品と別の道（調査の記録）

（結論の表は調査の最後に書く。途中で切れたときは §作業ログが正）

- 作成: 2026-09-26（部品調査のエージェント）。書いたのはこのファイルと `datasheets/tone/`・`datasheets/README.md` の行だけ
- 状態: 調査中
- 前の調査: [tone_chip_bypass.md](tone_chip_bypass.md)・査読 [tone_chip_bypass_review.md](tone_chip_bypass_review.md)。そこで見た品番（NJW1194・NJW1119A・PT2322・NJU7391A・BD37033FV-M・BD37512FS・BD3490FV・BD3491FS・TDA7439・TDA7468・NJW1192・NJW1201A・PT2033・PT2314E）は調べ直さない
- 凡例: 〔DS 品名 p.n〕＝`datasheets/tone/` の PDF（`pdftotext -layout`）。〔推論〕〔仮定〕〔計算〕。「確かめられず」＝DS を取れなかったか、DS に書かれていない
- `AudioV2/`・`Audio/` の文書は読んでいない

## 作業ログ（見つけた順）

### ROHM — fscdn.rohm.com から DS を取得（2026-09-26。rohm.com の製品頁・一覧は 403 で読めず）

DS を取った品（`datasheets/tone/` には、トーンを持つ代表だけ置く。ほかは下の読みの根拠として作業場で読んだ）:

| 品番 | DS の版（頁の脚注） | トーン | バイパス | 最大入力 VIM（min/typ） | 電源 | 読み |
|---|---|---|---|---|---|---|
| BD37534FV（SSOP-B28〔DS〕） | 16.Dec.2015 Rev.001（PDF の更新 2024-04） | 3 バンド P-EQ ±20 dB／1 dB | **無い**。レジスタ表は Bass/Middle/Treble の setup（f0・Q）と gain だけ〔DS p15 付近の表〕。01h の "Advanced switch ON/OFF … Tone/Fader/Loudness/Mixing" は**段の切替を柔らかくする機能の時間の設定**で、経路の切替ではない〔DS 01h の説明〕 | **2.1 / 2.3 Vrms**（THD+N 1 %、BW 400 Hz–30 kHz）〔DS EC 表〕 | 単電源 7.0〜9.5 V〔DS p1〕 | 除外（2.3 Vrms を min で満たさない、バイパス無し） |
| BD37531FV・BD37532FV・BD37533FV（SSOP-B28）・BD37543FS・BD37544FS（SSOP-A32） | どれも 16.Dec.2015 Rev.001 | 同じ 3 バンド | **無い**（同じ形のレジスタ表。"Tone/Fader/Loudness" は Advanced switch の時間の設定だけ） | どれも **2.1 / 2.3 Vrms** | 7.0〜9.5 V | 除外（BD37534FV と同じ家族。前の調査の BD37512FS・BD37033FV-M と同じ形） |
| BD37034FV-M | 4.Oct.2013 Rev.002 | 3 バンド | **無い**（"passes through 0dB" は Bass/Middle/Treble の利得を段で動かすとき 0 dB を経由する、という Advanced switch の説明） | **2.0 / 2.1 Vrms** | 車載 | 除外 |
| BD34602FS-M・BD34700FV・BD34704KS2・BD34705KS2 | 2014〜2015 | **無い**（音量だけ。"Bass"/"Treble" の語がほぼ無い） | — | BD34700FV・BD3470x は VOM typ 4.2 Vrms（±電源） | ±電源（BD34700FV は Vcc/Vee の立ち上げ順の注あり） | トーンが無いので対象外。**ただし (a) 自作トーンの「音量＋切替の絞り」の相方にはなりうる**（下の (a)） |
| BD37068FV-M・BD37069FV-M | 2016 | **無い**（セレクタ＋6 ch 音量＋ポストフィルタ） | "INSIDE THROUGH" はセレクタの設定名 | 2.2 / 2.1 typ | 車載 | 対象外 |

- ROHM の新しめ（2013〜2016 の DS）のトーン付きは **BD375xx の家族と BD37034FV-M で、どれも車載の単電源 7〜9.5 V・最大入力 min 2.0〜2.1 Vrms・バイパス無し**〔各 DS〕。前の調査の BD37033FV-M・BD37512FS と同じ設計の系統〔推論〕
- ホーム向けの新しめ（BD347xx・BD34602FS-M）は**音量だけでトーンが無い**〔各 DS p1〕

### ST — st.com は接続を切られて取れず（2026-09-26、前の調査と同じ）。rlocman.ru のミラーから取得

| 品番 | DS の版 | バイパス | 最大入力 | 電源 | 読み |
|---|---|---|---|---|---|
| TDA7719（TSSOP28） | Doc ID 13698 **Rev 4, April 2009**（初版 2007-07）〔DS 改訂履歴 p45〕 | **ある**: "Direct path" — "In direct path mode the input pins are connected to dedicated mono fader directly, all the filters and volume are bypassed"。Byte1 の Bit5〜7、QD2（Front）・QD3（Rear）・QD4（Sub）ごとに on/off〔DS §4.1.2 p15、Table 12 p32〕。**専用の入力ピン（QD2L/R など）→ スピーカの fader（0〜−79 dB、ソフトステップ）へ直結**。注 3 に "Inputs in direct path mode are also selectable with front and rear selector" とあり、同じピンをトーンの経路の源にも選べる〔DS p15〕。direct path を QD2 だけ on にすれば Front 出力だけが直結になる読み〔推論〕 | 入力のクリップ VCL **typ 2 Vrms（min は無い）**〔DS Table 5 p9〕 | 単電源 7.5〜10 V（typ 8.5 V）〔DS p9〕 | **除外**: 2007 年の品で「新しめ」ではなく、2 Vrms typ は 2.3 Vrms に届かない。ただし「チップの中でトーンも音量も飛ばし、ソフトステップの fader だけ残す」は NJW1194 の TSW と同じ考えで、メーカー（ST）にもある形として記録 |
| TDA7419（SO-28） | **Rev 6, Feb 2009**（初版 2004-11）〔DS 改訂履歴 p39〕 | "off (bypass)" は Smoothing filter の設定だけ〔DS p35〕。トーンを飛ばすモードは見当たらない | VCL **min 1.8 / typ 2 Vrms**〔DS p10〕 | 8.0〜10 V〔DS〕 | 除外（古い・振幅が足りない） |
| TDA7418・TDA7718・TDA7729 ほか | — | DS を取れず | — | — | **確かめられず**（st.com に届かず、ミラーも 404） |

- ST のアナログのオーディオプロセッサ（TDA74xx/77xx）は**車載の 8.5 V 単電源・入力 2 Vrms 級**の系統で、2012 年以降の新しい品番を DS で確かめることはできなかった（確かめられず）

### Nisshinbo — 製品一覧（Audio Signal Processing）を 2026-09-26 に取得（nisshinbo-microdevices.co.jp/en/products/audio-signal-processing/）

- 一覧の「Tone Control」列に値がある品は **NJU7391A・NJW1119A・NJW1192・NJW1194・NJW1201A の 5 品だけ**で、どれも前の調査で見た品〔メーカー一覧〕。**Nisshinbo にトーン付きの新しい品番は無い**
- 一覧の Note 欄はどれも "-"、区分はどれも "Standard"（NJW1194・NJW1119A を含む）〔メーカー一覧〕。製造中止・非推奨の印は付いていない（JLCPCB が NJW1119A を「製造終了」と出していることとは食い違う — 前の調査の追記。どちらが正しいかは確かめられず）
- 新しめの品（2020 年の新製品ニュースに NJU72315・NJU72322〔Nisshinbo ニュース 2020-04-09、検索結果の見出し〕）は**音量だけ**: NJU72315（±3〜±5.5 V、I²C、WCSP16）、NJU72322（±10〜±18 V、0〜−111.5 dB／0.5 dB、3 線、SSOP32）、MUSES72320・MUSES72323（±8.5/±10〜±18 V、3 線、SSOP32）、NJU72343（±4.5〜±7.5 V、8 ch、2 線、SSOP32）、NJU72344（2 ch、2 線、SSOP14）〔メーカー一覧の電源・制御・パッケージ欄〕
  - → トーンの IC ではないが、**±15 V でそのまま動く音量 IC（NJU72322・MUSES72323 は ±18 V まで）**は (a) の「自作トーン＋切替の絞り」の部品候補になる（下の §別の道 (a)）

### 入手性 — JLCPCB 部品検索 API（`selectSmtComponentList`、keyword 検索、2026-09-26 10 時台 UTC 取得）その 1

| keyword | 品番（JLCPCB の表記） | JLCPCB 番号 | 在庫 `stockCount` | `noBuyReason` | 最小 |
|---|---|---|---:|---|---:|
| NJW1194 | NJW1194V-TE1（SSOP-32、JRC） | C5184872 | **0** | なし（買える扱い） | 4 |
| PT2314E | PT2314E（SOP-28-300mil） | C90034 | 116 | なし | 1 |
| BD37534FV | BD37534FV-E2（SSOP-28） | C111704 | 10 | なし | 1 |
| BD37544FS | BD37544FS-E2 | C2651264 | 0 | なし | 3 |
| BD37543FS | BD37543FS-E2 | C17187488 | 0 | なし | 3 |
| TDA7719 | TDA7719（TSSOP-28） | C1235396 | 0 | なし | 2 |
| 〃 | TDA7719TR | C2651278 | 0 | "This product is no longer manufactured." | 4 |
| PCM1863 | PCM1863DBTR（TSSOP-30） | C529569 | **916** | なし | 1 |
| PCM5122 | PCM5122PWR（TSSOP-28） | C962071 | **1476** | なし | 1 |
| 〃 | PCM5122PW | C1540085 | 194 | なし | 1 |
| ADAU1701 | ADAU1701JSTZ-RL（LQFP-48 7×7） | C389590 | **6863** | なし | 1 |
| 〃 | ADAU1701JSTZ | C3001875 | 220 | なし | 1 |
| 〃 | ADAU1701（"JLCPCB Assembly" の出品） | C9900207170 | 0 | "This product is no longer manufactured." | 445 |

- **読みの注意**〔推論〕: 「JLCPCB Assembly」名義の `C99…` の番号は、現行品の ADAU1701 にも "no longer manufactured" と付いている（上）。前の調査の追記で NJW1119A が「製造終了」と出たのも `C9900305081`（同じ名義）だった。**`C99…` の出品の `noBuyReason` はメーカーの製造状況の根拠にならない**と読むのが安全（NJW1119A は Nisshinbo の一覧で "Standard"、上）

