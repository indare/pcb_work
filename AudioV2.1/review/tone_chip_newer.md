# トーンチップの候補 — 新しめの品と別の道（調査の記録）

| 候補 | 新しさ（DS の版） | トーンを通さない経路 | 2.3 Vrms を通せるか | JLCPCB 在庫（2026-09-26） | 判定 |
|---|---|---|---|---|---|
| **NJW1194**（比べる基準、前の調査） | Ver.7.4。メーカー一覧で "Standard" | `TSW`〔前の調査〕 | VOM min 3.6 Vrms（±7 V） | **0**（LCSC はリードタイムつきで在庫あり、ユーザー確認） | 基準 |
| ROHM BD37531/32/33/34FV・BD37543/44FS・BD37034FV-M | 2013〜2015 の DS | **無い**〔各 DS のレジスタ表〕 | **否**: VIM min 2.0〜2.1 Vrms | BD37534FV 10、ほか 0 | 除外 |
| ROHM BD347xx・BD34602FS-M、Nisshinbo NJU723xx・MUSES7232x | 2014〜2020 | —（**トーンが無い**。音量だけ） | — | — | 対象外 |
| ST TDA7719 | 2007 初版、Rev 4 2009 | **ある**（"Direct path"、フィルタと音量を飛ばす）〔DS p15〕 | 否: VCL typ 2 Vrms（min 無し） | 0 | 除外（古い・振幅） |
| ST TDA7419、Titan Micro TM2314/TM2313 | 2004／2011 | 無い | 否: min 1.8／2 Vrms | TM2313 1001、TM2314 1 | 除外 |
| (a) 自作トーン＋**MCP41HV51**（±18 V デジポット） | DS 2013–2015、現行 | 自分でリレーを置く | ±15 V のオペアンプで余裕〔推論〕 | 11〜108（抵抗値で違う） | 条件つき（THD の規定が DS に無い、切替の絞りが別に要る） |
| (b) **PCM1863＋PCM5122**（DAC 内蔵の biquad） | 2014／2012 初版、2018 改訂、現行 | デジタルを通らないリレー（前提） | FS 2.1 Vrms → 入口で絞り出口で戻す | **916／1476** | 条件つき（聴く経路が ADC/DAC、箱にクロックが走る） |
| (b) ADAU1701 | 2006（取れたのは Rev. 0） | 同上 | FS 2 Vrms（入力抵抗で合わせる）、DAC 0.9 Vrms → 利得段 | 6863 | (b) の次点 |

**結論: NJW1194 より良い（新しい・手に入る・バイパスがある・性能）トーンチップは、見られた範囲では「無い」。**
2012 年以降の DS を持つアナログのトーン IC は ROHM の車載の BD375xx の家族と BD37034FV-M だけで（DS の版の年で、品の発売年は確かめられず）、どれも単電源 7〜9.5 V・最大入力 min 2.0〜2.1 Vrms・バイパス無し（PT2314E より振幅が足りない）。Nisshinbo は 2020 年ごろの新製品が音量 IC だけで、トーン付きの品番は前の調査の 5 品のまま。チップの中で「トーンを飛ばす」を DS で確かめられた新しい品は、ここでは ST の TDA7719（2007 年、振幅不足）しか増えなかった。
NJW1194 が手に入らない・待てないときの道は、(1) 前の査読どおり PT2314E＋DIRECT のリレー、(2) (b) の PCM1863＋PCM5122（現行・在庫が多い・TSSOP。ただし聴く経路がデジタルになり、2.3 Vrms を 0 dB で通すには前後に段が要る）、(3) (a) の自作（部品は手に入るが、デジポットの歪みは実測しないと分からない）。どれも NJW1194 の「バイパスあり＋音量で段階に絞れる」を 1 個で置き換えるものではない〔推論〕。

- **外れる条件**: st.com・analog.com・rohm.com の製品一覧に届かなかった（ST の 2012 年以降の品番、ROHM の一覧にしか無い品番を見落としている可能性）。LCSC は読めず、JLCPCB の在庫だけで入手性を書いている

- 作成: 2026-09-26（部品調査のエージェント）。書いたのはこのファイルと `datasheets/tone/`・`datasheets/README.md` の行だけ
- 状態: 調査済み（査読前）。ユーザーの判断の材料
- 前の調査: [tone_chip_bypass.md](tone_chip_bypass.md)・査読 [tone_chip_bypass_review.md](tone_chip_bypass_review.md)。そこで見た品番（NJW1194・NJW1119A・PT2322・NJU7391A・BD37033FV-M・BD37512FS・BD3490FV・BD3491FS・TDA7439・TDA7468・NJW1192・NJW1201A・PT2033・PT2314E）は調べ直さない
- 凡例: 〔DS 品名 p.n〕＝`datasheets/tone/` の PDF（`pdftotext -layout`）。〔推論〕〔仮定〕〔計算〕。「確かめられず」＝DS を取れなかったか、DS に書かれていない
- `AudioV2/`・`Audio/` の文書は読んでいない

## 作業ログ（見つけた順）

### ROHM — fscdn.rohm.com から DS を取得（2026-09-26。rohm.com の製品頁・一覧は 403 で読めず）

DS を取った品（`datasheets/tone/` には、トーンを持つ代表だけ置く。ほかは下の読みの根拠として作業場で読んだ）:

| 品番 | DS の版（頁の脚注） | トーン | バイパス | 最大入力 VIM（min/typ） | 電源 | 読み |
|---|---|---|---|---|---|---|
| BD37534FV（SSOP-B28〔DS〕） | 16.Dec.2015 Rev.001（PDF の更新 2024-04） | 3 バンド P-EQ ±20 dB／1 dB | **無い**。レジスタ表は Bass/Middle/Treble の setup（f0・Q）と gain だけ〔DS p15〕。01h の "Advanced switch ON/OFF … Tone/Fader/Loudness/Mixing" は**段の切替を柔らかくする機能の時間の設定**で、経路の切替ではない〔DS p16〕 | **2.1 / 2.3 Vrms**（THD+N 1 %、BW 400 Hz–30 kHz）〔DS p4〕 | 単電源 7.0〜9.5 V〔DS p1〕 | 除外（2.3 Vrms を min で満たさない、バイパス無し） |
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

### その他のメーカー

- **TI**: アナログのトーン IC は見つからなかった。LM1036（DC 制御のトーン）は ti.com の DS の URL が 404（2026-09-26）で **DS を取れず**、JLCPCB の検索でも出ない（"no hit"）→ 確かめられず。TI のトーンはデジタル側（PCM512x の biquad、TLV320AIC3204 の処理ブロック）にある → (b) で扱う
- **Cirrus Logic**: CS42L52 など低電圧コーデックのトーン（Bass/Treble）はデジタル。CS42L52 の ADC の最大入力は **0.769·VA Vpp typ**（VA 2.5 V で約 1.9 Vpp ≈ 0.68 Vrms〔計算〕）、40 ピン QFN〔CS42L52 DS、Digi-Key のミラー。`datasheets/` には置かない〕→ 2.3 Vrms のライン入力に合わない。除外
- **Princeton**: 前の調査で一覧（PT2312E〜PT2315E・PT2033）を見ている。新しい品は無い（前の調査 §6）
- **Titan Micro（深圳天微）TM2314／TM2313**: PT2314／PT2313 と同じ構成（4 入力・音量・Bass/Treble・スピーカ減衰・ラウドネス、SOP28）の中国製〔TM2314 DS p1。PT2314 との互換は DS に書かれておらず、品番と構成からの読み〔推論〕〕（TM2314 の DS は中国語、**Ver2.0 2011-09-24**〔TM2314 DS p12〕、LCSC の DS の写し。`datasheets/` には置かない）。音量 1.25 dB 刻み・Bass/Treble・ラウドネス、**バイパスに当たる語（"bypass"・旁路・直通）が DS に無い**。制御表の Bass/Treble は −14〜+14 dB の 2 dB 段と 0 dB の 2 符号だけ〔TM2314 DS p9〕。電源 6〜10 V、**入力のクリップ Vcl min 2 / typ 2.5 Vrms**〔TM2314 DS p3〕→ 2.3 Vrms を min で満たさず、PT2314E（min 2.3 Vrms）より悪い。JLCPCB（2026-09-26）: `TM2314` C5250045 在庫 1、`TM2313` C88429 在庫 1001。除外
- 検索で出たほかの品（TDA7440D・TDA7318・BA3880S・Sony CXA2021・Panasonic AN5295NK）は 1990〜2000 年代の品で、「新しめ」に当たらないので DS を読んでいない
- 検索で出た PT2314 系の話題（Arduino ライブラリなど）は PT2314 の使い方で、新しい品番ではない

## 別の道

### (a) トーン回路を自作し、デジタルポテンショメータ／アナログスイッチで切り替える

- **±15 V でそのまま使えるデジタルポテンショメータ**: Microchip **MCP41HV51**（MCP41HVX1 家族）
  - 端子電圧 ±18 V（V+−V− 最大 36 V、端子は V−−0.3 V〜V++0.3 V）〔DS p1・p3〕、8 bit（256 タップ）または 7 bit、R_AB 5/10/50/100 kΩ（±20 %）〔DS p1・p5〕、ワイパ抵抗 75 Ω typ〔DS p1〕、SPI、ロジック電源 VL 2.7〜5.5 V（DGND 基準。3.3 V の Pico で直接）〔DS p1・p4〕、帯域 480 kHz（5 kΩ）／240 kHz（10 kΩ）〔DS p10〕、**POR のワイパは中点（8 bit で 7Fh）**〔DS p14〕、TSSOP-14〔DS p1〕、DS20005207B（2013–2015）
  - **THD・雑音の規定は DS に無い**（"THD"/"Distortion" の語が無い）→ 音声の性能は**確かめられず（要実測）**
  - 入手性: JLCPCB で `MCP41HV51-503E/ST`（50 kΩ）C637064 在庫 29、`-103E/ST` C637062 在庫 108、`-104E/ST` C148046 在庫 11（2026-09-26）
- ADI **AD5292**（±15 V、1024 段と記憶。**DS は analog.com に届かず取れず → 性能は確かめられず**）: JLCPCB `AD5292BRUZ-20` C208566 在庫 21、`-50` 在庫 0（2026-09-26）
- 形の読み〔推論〕: ±15 V のオペアンプ（Baxandall などの帰還型）の Bass/Treble の可変抵抗を、ch あたり 2 個のデジタルポテンショメータで置き換える。L/R で 4 個、SPI の CS が 4 本（または数珠つなぎ）。中点の POR はほぼフラットの位置になる（回路しだい）
- 良い点〔推論〕: ±15 V で振れるので**振幅の天井はオペアンプの振幅（2.3 Vrms の数倍）**。ブースト時の頭打ちも起きにくい。部品はどれも現行で JLCPCB に在庫がある。トーン段を自分で描くので、**バイパス（トーン段の前後をリレーで短絡）も自分で置ける**
- 弱い点: (1) デジポットの歪みが DS で分からない（線形の抵抗ラダー＋CMOS スイッチなので、ワイパの電圧が大きいと歪むことが考えられる〔推論〕。要実測）。(2) **段の切替にゼロクロスもソフトステップも無い**（DS に記述なし）→ 1 dB 相当ずつ動かしてもジッパー音が出うる〔推論〕。(3) 切替の絞り（[DEC] §2-10・§6-2）に使える音量の素子が無い — 別に電子ボリュームが要る。±15 V で動く Nisshinbo の NJU72322・MUSES72323（一覧の電源欄 ±10〜±18 V、SSOP32）は JLCPCB で**どちらも在庫 0**（`NJU72322V-TE1` C17338971、`MUSES72323V-TE1` C17565270、2026-09-26）。(4) 部品が増える（デジポット 4、オペアンプ、C・R の網、デジの線 4〜6 本）、定数の設計と検証を自分でやる
- アナログスイッチで抵抗を切り替える形（TMUX7612 はすでに娘にある）: 段の数だけスイッチと抵抗が要り、1 dB 刻み ±10 dB を 2 バンド×2 ch で作ると部品が大きく増える〔推論〕。細かくは評価していない
- **DIRECT への効き**: トーン段を自作すれば、DIRECT は「トーン段を通らないリレー」を自分の回路の中に置く形になり、今の形 1／形 2（`review/direct_bypass_review.md`）と同じ類になる。**PT2314E を置き換える意味での新しさは無い**が、PT2314E の 2.3 Vrms の天井は消える〔推論〕

### (b) ADC＋DSP＋DAC でトーンを作る（DIRECT はデジタルを通らないリレー）

2 つの組み方を見た。

| | TI **PCM1863（ADC）＋PCM5122（DAC、内蔵 biquad）** | ADI **ADAU1701**（SigmaDSP、ADC 2・DAC 4 を内蔵） |
|---|---|---|
| DS | SLAS831D（2014-03 初版、2018-03 改訂）／SLAS763C（2012-08 初版、2018-10 改訂） | **Rev. 0（2006-10）**を Digi-Key のミラーで。今の版は取れず（analog.com に届かず） |
| 入力の最大 | 単端 **2.1 Vrms**（FS）、差動 4.2 Vrms〔PCM186x p13〕→ 2.3 Vrms は単端では頭を打つ。入口で約 −1.5 dB 以上絞るか差動で入れる〔計算〕 | 電流入力、FS 100 µArms＝**2 Vrms（18 kΩ 外付け＋2 kΩ 内部）**〔ADAU1701 p3〕→ 2.3 Vrms なら外付けを約 21 kΩ に〔計算〕 |
| 出力の最大 | **2.1 Vrms**（グランド中心、10 kΩ で 2 Vrms）〔PCM512x p33〕→ 2.3 Vrms の源は −1.5 dB 以上低く出る。0 dB を保つには後ろに利得段が要る〔推論〕 | DAC の FS **0.9 Vrms**〔ADAU1701 p3〕→ 約 ×2.6 の利得段が要る〔計算〕 |
| THD+N | ADC 単端 **−87 dB typ**（0.0045 %〔計算〕、−1 dBFS、min/max 無し）、差動 −93 typ／−85 min dB〔PCM186x p13〕。DAC **−93 typ／−83 max dB**（0.0022 %／0.0071 %〔計算〕）〔PCM512x p8〕 | ADC **−83 dB typ**（−3 dBFS）、DAC **−90 dB typ**（−1 dBFS）。どちらも max 無し〔ADAU1701 p3〕 |
| 雑音 | ADC SNR 単端 106 dB typ・差動 110 typ／97 min dB〔PCM186x p13〕。DAC DR 112 typ／108 min dB〔PCM512x p8〕 | ADC DR 100 typ／95 min dB、DAC DR 104 typ／99 min dB〔ADAU1701 p3〕 |
| トーンの作り方 | PCM5122 の固定の処理フロー（Program 5）に biquad・DRC・ミキサ・音量〔PCM512x p34〕。**48 kHz まで**〔同 p34〕。係数メモリは A/B の 2 面で、"adaptive mode" なら動作中に片面を書いて切り替えられる〔PCM512x p103〕→ Pico がシェルビングの係数を計算して I²C で書く〔推論〕 | SigmaStudio で組んだ処理を EEPROM から自己起動、または I²C/SPI で書く〔ADAU1701 p1・p14〕。動作中の係数の書き換えは "safeload"（Safeload Data/Address Registers）〔ADAU1701 p14・p35〕 |
| 電源 | 3.3 V 単電源（どちらも）〔各 p1〕 | AVDD 3.3 V・DVDD 1.8 V（内蔵レギュレータで 3.3 V だけでも可）〔ADAU1701 p3・p14〕 |
| パッケージ | TSSOP-30／TSSOP-28〔各 p1〕 | LQFP-48（7×7、0.5 mm）〔JLCPCB の表記〕 |
| 入手性（JLCPCB、2026-09-26） | `PCM1863DBTR` C529569 **916**、`PCM5122PWR` C962071 **1476**（`PCM5122PW` 194） | `ADAU1701JSTZ-RL` C389590 **6863**、`ADAU1701JSTZ` C3001875 220 |

- 良い点: **どれも現行で在庫が多い**。トーンの形（周波数・Q・段）を自由に決められる。PCM5122 は QFN でなく TSSOP
- 弱い点〔推論〕: (1) 聴く経路に ADC と DAC が入る。歪みの DS 値（typ −87〜−93 dB）は PT2314E（0.03 % typ ≈ −70 dB〔計算〕）より良いが、NJW1194 のバイパス（グラフで約 0.0015 %≈−96 dB、前の調査）と同じ程度かそれより下。(2) **2.3 Vrms を 0 dB で通せない**（入力 2.1 Vrms FS／出力 2.1 Vrms）。入口で絞って出口で戻す段が要り、そのぶん雑音が増える。(3) 箱の中に 3.3 V のデジタル・クロック（I²S、PLL）が常に走る。[DEC] §2-12 で「聴いている間に音声チップの足へデジタルのエッジを来させない」とした考えと正面から当たる。(4) 部品と設計が増える（クロック、3.3 V のアナログ電源、入力の減衰・出力の利得段・出力の RC、ファームで係数計算）。(5) 電源が無いときの入力の扱い・起動時のポップは DS を読み込んでいない（確かめられず）
- **DIRECT への効き**: 前提どおり、DIRECT はデジタルを通らないリレーで取る → 今の形 1／形 2 と同じ（リレーの切替の硬い端は残る）。DSP 側の MUTE（PCM5122 の soft mute、アナログ mute〔PCM512x p1〕）で「通常」側の切替は静かにできる見込み〔推論〕が、DIRECT 側には効かない
- この装置（オペアンプの差を耳で比べる箱）で、比べる石の手前に ADC/DAC を入れてよいかはユーザーの判断〔推論〕

