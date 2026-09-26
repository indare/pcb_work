# トーンチップの候補 — バイパス（スルー）を持つもの（調査の記録）

| 順位 | 品番 | バイパスの中身 | バイパス時の DS 値 | DIRECT のリレー | 主な弱み |
|---|---|---|---|---|---|
| 1 | **NJW1194**（Nisshinbo） | `TSW` でトーンだけ飛ばす。セレクタ・音量・出力バッファは残る〔DS p1・p17〕 | **表にある**（EC の共通条件が TONE=OFF）: VOM min 3.6 Vrms、雑音 1.41 µV typ、CT/CS −120 dB typ。THD はグラフだけ（2 Vrms 1 kHz で約 0.0015 %） | 要らなくなる。音量が経路に残るので、DIRECT でも段階で絞れる〔推論〕 | 3 線シリアル（I²C ではない）、±7 V が要る、TSW の切替は MUTE しろと DS に書いてある、少量では買いにくい（Digi-Key は最小 2,000 個） |
| 2 | **NJW1119A**（Nisshinbo） | トーン専用。ch ごとの `TSW`。音量もセレクタも無い〔DS p1・p9〕 | **表にある**: THD 0.0002 % typ（2 Vrms）、雑音 1.0 typ / 3.2 max µV、VOM min 3.0 Vrms、CS −100 typ / −90 max dB。周波数特性のグラフは無い | 要らなくなる | 音量が無いので、今 PT2314E の音量でやっている切替の絞り（DECISIONS §2-10・§6-2）ができない。入手性は 1 位と同じ |
| 3 | **PT2314E のまま**＋形 1／形 2 のリレー | チップにバイパスは無い〔DS PT2314E p7・p9〕 | 無い（あるのはトーン 0 dB＝フラットの値だけ: VOMAX min 2.3 Vrms、THD 0.03 typ / 0.07 max %） | 要る | 振幅の余裕が 0 dB（min 2.3 Vrms）。DIRECT の経路には絞れる素子が無い（§2-10 の「硬い端」が残る） |
| 参考 | PT2322（Princeton） | "Tone Defeat" あり〔抜粋 p1〕 | DS が 3 頁の抜粋しか取れず、**確かめられず** | — | Princeton の今のホーム用の一覧に載っていない |
| 除外 | ROHM BD37033FV-M・BD37512FS・BD3490FV・BD3491FS、ST TDA7439・TDA7468、NJW1192・NJW1201A、PT2033 | どの DS にもバイパスは見当たらない | フラットの値だけ | 要る | 最大入力の min が 2.0〜2.1 Vrms（PT2033 だけは min 2.5 Vrms） |
| 保留 | NJU7391A | EC 表の条件に「TONE=OFF」とあるが、制御表でどう設定するか定義されていない〔p3・p7〕 | 確かめられず | — | 単電源 9 V、最大入力は typ しか書かれていない |

**要旨**: DS を読んで「トーンを通さない経路」を確かめられたのは Nisshinbo の **NJW1194** と **NJW1119A** だけだった。どちらも**バイパスの条件で**性能の表値があり、フラットの PT2314E より、振幅の余裕（+3.9 dB／+2.3 dB〔計算〕）・歪み・雑音のどれでもはっきり上。
ただしどちらでも**信号はチップの中を通る**（「チップと電気的に無縁」にはならない）。NJW1194 は音量が経路に残るので、DIRECT の「絞れない」問題も一緒に消える見込み〔推論〕。そのため 1 位にした。
どちらも **I²C ではなく 3 線シリアル・±7 V の両電源**で、少量で買える正規ルートが見つからなかった。ここが採用の前に解くべき問題になる。

- 作成: 2026-09-26（部品調査のエージェント）。書いたのはこのファイルと `datasheets/tone/`・`datasheets/README.md` の行だけ
- 状態: 調査済み（査読前）。ユーザーの判断の材料
- 凡例: 〔DS 品名 p.n〕＝`datasheets/tone/` の PDF（`pdftotext -layout`。グラフと表の並びは `pdftoppm` の画像で確かめた）。〔推論〕〔仮定〕〔計算〕。「確かめられず」＝DS を取れなかったか、DS に書かれていない
- 比べる相手 PT2314E の事実は `ds_facts/switch_control.md` §5（以下 [sw]）
- `AudioV2/`・`Audio/` の文書は読んでいない

## 1. バイパス時の性能（ユーザーの追加の軸）

**バイパスの条件（トーン段を通さない）で書かれた値**と、**トーン ON・0 dB（フラット）の値**を分けて並べる。フラットの値はバイパスの値として扱わない。

| 項目 | NJW1194 **TONE=OFF** | NJW1194 TONE=ON（Bass=Treble=0 dB） | NJW1119A **Tone=OFF** | NJW1119A Tone=ON（全 0 dB） | PT2314E（フラット。バイパスは無い） |
|---|---|---|---|---|---|
| 条件（電源・負荷） | ±7 V、RL 47 kΩ、VOL 0 dB〔p3〕 | 同左 | ±7 V、RL 47 kΩ〔p3〕 | 同左 | VDD 9 V、RL 10 kΩ、all controls flat〔[sw] §5、p12〕 |
| 最大出力（THD 1 %） | **3.6 min / 4.2 typ Vrms**（表）〔p3〕 | 表に無い。グラフでは TONE=OFF と同程度（約 4.3 Vrms、目読み）〔p20〕 | **3.0 min / 4.0 typ Vrms**（表）〔p3〕 | 表に無い。グラフで約 4.4 Vrms（目読み）〔p15〕 | 2.3 min / 2.6 typ Vrms |
| 2.3 Vrms からの余裕 | +3.9 dB〔計算、min 基準〕 | — | +2.3 dB〔計算〕 | — | 0 dB |
| THD+N | **表に無い**。グラフ（2 Vrms、BW 10–80 kHz）: 1 kHz で約 0.0015 %、10 kHz で約 0.004 %（目読み）〔p22〕 | 表: 0.0015 % typ（2 Vrms、1 kHz）、0.005 %（10 kHz）、max は THD7（2 Vrms、VOL −18 dB）の 0.02 % だけ〔p4〕 | **表: 0.0002 % typ（2 Vrms、1 kHz、BW 400 Hz–30 kHz）、0.002 %（20 kHz）**。max は無い〔p4〕。グラフでは約 0.0003〜0.0005 %（目読み）〔p17〕 | 表: 0.002 typ / 0.02 max %（1 kHz）、0.005 %（20 kHz）〔p4〕 | 0.03 typ / 0.07 max %（Vin 1 Vrms） |
| 出力雑音 | **1.41 µVrms typ（−117 dBV）**、A-weight、Rg 0。max は無い〔p4〕 | 2.2 typ / 10 max µVrms（−113 / −100 dBV）〔p4〕 | **1.0 typ / 3.2 max µVrms（−120 / −110 dBV）**、A-weight〔p3〕 | 3.2 typ / 6.3 max µVrms〔p3〕 | S/N 100 dBV typ（A-weight）。残留雑音はグラフで約 7 µV（A-weight、目読み） |
| 周波数特性 | **表に無い**。グラフ「Volume Gain output vs Frequency」（TONE=OFF）で 10 Hz〜100 kHz ほぼ平ら。目盛が 20 dB 刻みで細かくは読めない〔p20〕 | 同じ形のグラフ（TONE=ON）〔p20〕 | **無い**（利得の温度特性の 1 kHz と 10 kHz の点だけ。TONE=OFF・ON とも約 0 dB）〔p16〕 | トーンの周波数特性のグラフ〔p18〕 | [sw] §5 に無い（確かめられず） |
| 利得 | 0 ± 0.5 dB（Vin 2 Vrms）〔p3〕 | トーンのフラット: ±2 dB〔p5〕 | 0 ± 0.5 dB（Vin 2 Vrms）〔p3〕 | フラット: ±1.5 dB〔p4〕 | 音量段とスピーカ減衰の和で 0 ± 2 dB（`review/direct_bypass_review.md` §0.1 #5） |
| L↔R の分離 | CS1 **−120 typ / −90 max dB**（1 kHz、A-weight）、CS2 −100 dB typ（20 kHz）〔p3〕 | CS3 −110 / −90 dB（1 kHz）、CS4 −90 dB（20 kHz）〔p3〕 | CS1 **−100 typ / −90 max dB**（1 kHz、A-weight）〔p3〕。20 kHz は TONE=OFF の値が無い | CS2 −100 / −90 dB、CS3 −80 dB（20 kHz）〔p3〕 | 90 min / 100 typ dB |
| 入力間のクロストーク | CT1 −120 dB typ（1 kHz）、CT2 −100 dB typ（20 kHz）〔p3〕 | — | 入力は 1 系統だけ（該当なし） | — | 入力の分離 90 min / 100 typ dB（20 Hz〜20 kHz） |

- NJW1194 の THD の表の行は、**8 行とも「TONE=ON (Bass=Treble=0dB)」**と条件に書いてある〔p4〕。バイパスの THD はグラフでしか分からない
- 3 品とも測定の条件（電源・負荷・帯域）がそろっていない。上の表は「DS がどの条件で何を保証しているか」の比較で、同じ条件での性能の比較ではない
- 今回除外した品（ROHM・ST・PT2033・NJW1192・NJW1201A）の EC は、どれもトーン 0 dB（フラット）の条件（各品のログを参照）。バイパスの値は、そもそも存在しない

## 2. 比べる軸（候補ごと）

| 軸 | NJW1194 | NJW1119A | PT2314E（今） |
|---|---|---|---|
| バイパスで何を飛ばすか | トーンだけ〔p17〕。セレクタ（MUTE あり）・音量（+31.5〜−95 dB／0.5 dB、MUTE）・出力は経路に残る〔p1・p8。TSW で飛ぶ範囲の図は無く、ブロック図から読んだ〔推論〕〕 | トーンだけ（ch ごと）。残るのは入力の段と出力バッファ（50 Ω）・ch ごとの MUTE〔p5・p9〕 | 無い |
| バイパスでもチップを通るか | 通る。電源が無ければ信号は通らない〔推論〕 | 通る〔推論〕 | — |
| 切替のポップ・ミュート | 「TSW を切り替えるときは MUTE を使え」と応用回路の注にある〔p8〕。特長にゼロクロス検出〔p1〕とあるが、**何の切替に効くかは書かれていない**。スイッチングノイズ用のコンデンサの端子 `DCCAP`〔p2〕 | 切替のノイズ用のコンデンサの端子 `SWC`〔p2〕。**ポップの値もゼロクロスも MUTE の注も書かれていない** | ソフトミュート・ゼロクロスは無い（DECISIONS §2-10） |
| 電源 | ±4.5〜±7.5 V（typ ±7 V）、絶対最大 ±8 V、12 mA typ／17 mA max（各レール）〔p3〕 | ±4.5〜±7.5 V、14 typ／21 max mA〔p3〕 | 単電源 5〜10 V（今は L7809 の 9 V）、30 typ／40 max mA |
| 入力の最大・絶対最大 | 絶対最大 VIM＝V+/V−〔p3〕。±7 V なら 2.3 Vrms（3.25 Vpk）は内側〔計算〕 | 同じ（"Be careful to use in power supply voltage range"）〔p3〕 | −0.3 V〜VDD+0.3 V。VOMAX 2.3 Vrms min |
| 入力抵抗 | 15 min / 20 typ kΩ〔p3〕 | 等価回路に 50 kΩ（表値は無い）〔p5〕 | 音量段 13 / 20 / 27 kΩ |
| 電源が無いときの入力 | **規定が無い**。「電源投入の前に信号が入っていると初期状態がおかしくなりうる。電源を切る前に MUTE にせよ」という注だけ〔p11〕 | **規定が無い**。"Any signal must not be inputted on the power “off”. It may affect initial condition of DATA CONTROL."〔p3〕 | 絶対最大が −0.3 V〜VDD+0.3 V（電源が無ければ ±0.3 V 付近で頭を打つ〔推論〕）。Iin ±100 mA（ラッチアップ）は `review/direct_bypass_review.md` §0.1 #7 |
| Bass/Treble | 0〜±10 dB／1 dB〔p1〕。Bass は外付けの C1・C2・R3 で f0 と Q、Treble は外付けの C で f0 が決まる（式と内部抵抗の表あり）〔p9・p10〕 | 3 バンド 0〜±12 dB／1 dB（100 Hz／1 kHz／10 kHz）〔p1〕。どのバンドも外付けの C・R で決まる〔p11・p12〕 | ±14 dB／2 dB。Bass・Treble の容量は外付け（DS p10 のグラフ） |
| 制御 | **3 線シリアル**（DATA/CLOCK/LATCH、16 bit）、チップアドレスは 4 通り。VIH min 2.5 V・VIL max 1.5 V〔p5・p11〕→ 3.3 V でそのまま駆動できる〔推論〕 | 同じ〔p4・p8〕 | I²C。VIH min 3.0 V なので BSS138 のレベルシフタを入れている（V21-継-05） |
| パッケージ | SSOP32（NJW1194V）、0.65 mm ピッチ、11 × 7.6 mm（Nisshinbo の SSOP32 の頁） | SSOP32（NJW1119AV）〔p1〕 | SOIC-28W |
| 入手性（2026-09-26） | Digi-Key `NJW1194V-TE1`: "Active"、在庫無しの取り寄せ、**最小 2,000 個**、リードタイム 12 週。秋月: 扱い無し（検索で出ない）。少量は AliExpress に出品がある（本物かどうか分からない） | Digi-Key `NJW1119AV-TE1`: "Active"、在庫無しの取り寄せ、最小 2,000 個、12 週。秋月: 扱い無し。Mouser は頁を取れず | [sw] には無い（DECISIONS V21-継-05 では「無印は買えない、E は買える」） |

- マルツは Digi-Key の取次なので、Digi-Key と同じ条件になると考えられる〔推論〕。LCSC・Mouser・チップワンストップは、自動の取得を拒否されるか在庫を読めず、**確かめられず**
- NJW1194・NJW1119A の DS に「EOL」「NRND」の記載は無い。Nisshinbo の製品頁は Digi-Key と同じく現行品として出している（製品頁と Digi-Key の "Active" による）

## 3. DIRECT（`review/direct_bypass.md`・`_review.md`）との関係

**DIRECT の要件が「トーン回路を通さない」なら、NJW1194（または NJW1119A）のバイパスで足りる。形 1・形 2 のリレーは要らなくなる**〔推論〕。要らなくなるもの: DIRECT のリレー（AZ850 1 個）、その制御線 2 本（制御 MCP、DECISIONS §2-16）、親の TBD62083A 2 ch と AHCT、DIRECT の側の 2.2 µF と 220 kΩ。ほかに、`review/direct_bypass_review.md` の次の論点が消えるか、形が変わる〔推論〕:

| review の論点 | チップのバイパスにしたとき |
|---|---|
| §5.3・DECISIONS §2-10「DIRECT には絞れる素子が無く、生きた信号の硬い端が残る（ch 替えで 2、DIRECT の切替で 1）」 | **NJW1194 なら消える見込み**: 音量が経路に残るので、DIRECT のままでも PT2314E のときと同じ「音量を段階で絞る → 全リセット → … → 戻す」の手順が使える〔推論〕。0.5 dB 刻みで、ゼロクロス検出もある（効く範囲は確かめられず）。**NJW1119A では消えない**（音量が無い。ch ごとの MUTE はあるが、硬さは確かめられず） |
| DIRECT ↔ 通常の切替 | TSW の書き込みになる。DS の注にしたがって、MUTE（音量を段階で絞る）→ TSW → 戻す〔p8〕 |
| §0.1 #8・#13「T-a では並列の PT の入力の保護ダイオードが源の頭を丸める。PT から電気的には切れない」 | 並列の枝は無くなる。代わりに**信号はチップの中を直列に通る**（「無縁」からはさらに遠くなる） |
| §0.1 #24・§7.2「DIRECT のまま電源を切ると、SET のまま残った音声リレー越しに、源の信号が電源の無い TMUX のクランプへ行く」 | 源とバスの間に、電源の無いチップが入る。源の信号がどこまでバスへ漏れるかは、電源が無いときの入力・出力の規定が無いので**確かめられず**（要実測） |
| 振幅の天井（§0.2-5） | チップの VOM が天井になる（NJW1194 は min 3.6 Vrms）。それより先に ADC の頭（2.73 Vrms、§0.1 #9）が来る |

**足りないところ**:
- **「DIRECT＝チップと電気的に無縁」を要件にするなら、どの候補でも足りない**。形 1（入口と出口の両方で切る）が要る（`review/direct_bypass_review.md` §0.3 の 3 行目と同じ）
- バイパスでも、チップの入力段・音量の抵抗ラダー・出力バッファを通る。チップに電源が無いと信号は通らない〔推論〕。親のトーンは常時通電なので（DECISIONS §1-1 の前提）、聴いている間は問題にならない
- 電源投入の前から源が鳴っていると、初期状態がおかしくなりうる〔NJW1194 p11、NJW1119A p3〕。箱の電源断は制御できない（PD を抜かれる）ので、DS の手当て（切る前に MUTE にする）は当てにできない。起動のたびに全レジスタを書き直す〔推論。今の PT2314E の初期化（DECISIONS §6）と同じ場所で〕

## 4. PT2314E を続ける場合との比較

| | PT2314E のまま＋DIRECT のリレー | NJW1194 に替える |
|---|---|---|
| DIRECT の置き方 | 形 1／形 2 のリレーが要る（査読済み・ユーザーの判断待ち、V21-未決-14） | TSW でバイパス。リレーは要らない |
| DIRECT の間の絞り | できない（硬い端が残る、DECISIONS §2-10） | 音量でできる〔推論〕 |
| 通常の経路の振幅の余裕 | 0 dB（min 2.3 Vrms、THD 1 %） | +3.9 dB（min 3.6 Vrms、±7 V、TONE=OFF。TONE=ON の表値は無い） |
| 電源 | +15 V → L7809 の 9 V（DECISIONS §3-4） | ±7 V を 2 本作る（±15 V からレギュレータで〔推論〕）。−15 V 側にも負荷が増える（17 mA max〔p3〕） |
| 制御 | I²C＋BSS138 ×2（V21-継-05） | 3 線シリアル、3.3 V で直接〔推論〕。BSS138 は要らなくなる。**線が 3 本要る**。Pico の空きは 1 本（DECISIONS §2-16）なので、どこから出すかを決める必要がある（下の「外れる条件」） |
| 定数の決め直し | 無し | ADC 前段の 6.19 k（V21-継-08 は PT2314E の VOMAX で決めた）、トーンの外付けの網、入出力の結合 C（DS の応用回路は 10 µF〔p8〕）。I/O の DC は 0 V〔p6〕 |
| 入手性 | 今の図で使っている | 少量の正規ルートが見つからない（Digi-Key は最小 2,000 個） |
| 図・PCB への影響 | リレー 1 個と周辺 | ルートのトーンまわりを描き直す（SOIC-28W → SSOP32、電源、制御線） |

## 5. 結論

1. **NJW1194**: 「バイパスでもチップを通ることは受け入れ、バイパス時の性能が十分なものを選ぶ」という選び方なら 1 位。DS がバイパスの条件で振幅・雑音・分離を保証しており（THD だけはグラフ）、どの値もフラットの PT2314E より上。音量が残るので、DIRECT の「絞れない」問題（§2-10）も一緒に片づく〔推論〕
2. **NJW1119A**: バイパスの数値はいちばん良い（THD 0.0002 % typ、雑音 1.0 µV typ）。ただし音量が無いので、切替の絞りを別の素子で作り直す必要がある。音量はポットで手で回す装置なので、チップに音量が要るのは切替の絞りのためだけ。それを別に持つなら 1 位と入れ替わる
3. **PT2314E を続ける**: DIRECT を「チップと無縁」にしたいとき、または NJW1194 を少量で手に入れられないとき。この場合、DIRECT は今の査読どおり（形 1／形 2）
4. **PT2033**（バイパス無し）: DIRECT をリレーで作る前提のまま、PT2314E の振幅の余裕だけを改善したいときの候補（min 2.5 Vrms、+0.7 dB〔計算〕。VIH min 3 V は同じ）

**外れる条件**
- ユーザーが「DIRECT＝チップと電気的に無縁」を求める → 3 位（または形 1 を足す）
- NJW1194 を少量で正規に買えない → 1・2 位は崩れる（AliExpress の品は本物かどうか分からない）
- 3 線の線を出す場所が無い → 1・2 位の費用が上がる。候補〔推論、どれも未検討〕: DIRECT のリレーを無くせば制御 MCP の 2 本が空く（ただしこの MCP は「スタック制御専用」の決め〔DECISIONS §2-16〕なので、音声チップを載せるのはその決めの見直しになる）。UI の MCP の空きピン（数は図から数えていない）。Pico の既存の SPI と共用する（DS の "Set CLOCK in High to prevent incorrect operation during a standby period"〔p11〕と、聴いている間にエッジが音声チップへ来ること（DECISIONS §2-12 で娘の I²C を外した理由と同じ形）の 2 点で要検討）
- TSW の切替のポップが MUTE でも消えない → DIRECT の切替の手順を見直す

**要実測**
- NJW1194 の TSW の切替のポップ（MUTE あり・なし）と、ゼロクロス検出が音量の段に効くか
- バイパスの THD+N と雑音（DS はグラフと typ だけ）。後段（オペアンプ ch のゲイン 2 → ADC）を通した実物で
- 箱の電源が無い間に源が鳴っているとき、チップの入力の電流と、出力へ漏れる量
- 電源投入の前から信号があるときの初期状態（DS p11 の注）と、起動時に全部書き直せば戻るか

## 6. 作業ログ（候補ごと、見つけた順）

### NJW1194（Nisshinbo／旧 NJR）— `datasheets/tone/NJR_NJW1194.pdf`（Ver.7.4、25 頁、Nisshinbo の製品頁から 2026-09-26 取得）

- 構成: 4 入力セレクタ → 音量（+31.5〜−95 dB／0.5 dB、MUTE）→ トーン（Bass/Treble、0〜±10 dB／1 dB）→ 出力、2 ch〔DS NJW1194 p1〕
- **バイパス**: 制御語 Treble の D10 が `TSW : Tone Control By-pass Switch`、0＝Tone Control OFF（**初期値**）、1＝ON〔DS p17〕。飛ぶのは**トーンだけ**。セレクタと音量は経路に残る（ブロック図・応用回路で、TONE はセレクタ・音量の後ろ〔DS p1・p8〕。TSW で飛ぶ範囲の図は無く、ブロック図からの読み〔推論〕）
- **切替のポップ**: 応用回路の注 "When switching TSW(Tone Control By-pass Switch), use MUTE on the set."〔DS p8〕→ TSW の切替自体は無音ではない、とメーカーが言っている
- ゼロクロス: 特長に "Zero Cross Detection"、ブロック図に Zero Cross Detection のブロック〔DS p1・p8〕。**何の切替に効くか（音量だけか、TSW にも効くか）は DS に書かれていない**（確かめられず）
- 電源: **±4.5〜±7.5 V（typ ±7.0 V）両電源**、絶対最大 ±8 V〔DS p3〕。±15 V からなら ±7 V の LDO が要る〔推論〕
- **EC 表の共通条件が `TONE=OFF`**（"Ta=25°C, V+/V-=±7V, RL=47kΩ, Volume=0dB, TONE=OFF"）〔DS p3〜p5 の見出し〕。行ごとに TONE=ON と書いてあるものだけが ON:
  - バイパス（TONE=OFF）の値: VOM min 3.6 / typ 4.2 Vrms（THD 1 %, VOL 0 dB）、GV1 −0.5/0/+0.5 dB（Vin 2 Vrms）、CT1 −120 dB typ（1 kHz, A-weight, Rg 0）、CT2 −100 dB typ（20 kHz）、CS1 −120 typ/−90 max dB（1 kHz）、CS2 −100 dB typ（20 kHz）、**VNO2 −117 dBV typ（1.41 µVrms、A-weight, Rg 0, TONE=OFF）**〔DS p3・p4〕
  - トーン ON（Bass=Treble=0 dB）の値: VNO1 −113 typ / −100 max dBV（2.2 / 10 µVrms）、CS3 −110/−90 dB、CS4 −90 dB、THD1〜8 はすべて TONE=ON（例 THD3 0.0015 % typ @1 kHz 2 Vrms、THD4 0.005 % @10 kHz 2 Vrms、THD7 max 0.02 %）〔DS p3・p4〕
  - **THD の表値に TONE=OFF の行は無い**。TONE=OFF の THD+N はグラフだけ: p22「THD+N vs Frequency」Vin 2 Vrms, BW 10–80 kHz で TONE=OFF 約 0.0015 %（1 kHz）・約 0.004 %（10 kHz）、TONE=ON 約 0.002 %・約 0.006 %〔DS p22、画像で目読み〕。p21「THD+N vs Input Voltage」TONE=OFF で 1 kHz は約 3〜4 Vrms で急増〔DS p21、目読み〕
  - 周波数特性: TONE=OFF の「Volume Gain output vs Frequency」で VOL 0 dB は 10 Hz〜100 kHz でほぼ平ら（目盛 20 dB、細かい値は読めない）〔DS p20、目読み〕。表値は無い
- 入力: 入力インピーダンス min 15 / typ 20 kΩ〔DS p3〕、最大入力電圧 VIM = V+/V−（絶対最大）〔DS p3〕。**電源が無いときの入力の扱い・保護の規定は無い**。注に "If any audio signal is inputted in input signal terminal before power “ON”, it may cause initial condition abnormality … it prevents that abnormality by setting MUTE before power “OFF”"〔DS p11〕
- 起動は MUTE（音量 2 本とも MUTE、セレクタも MUTE、TSW＝OFF）〔DS p11 INITIAL CONDITION、p17〕
- 制御: **I²C ではなく 3 線シリアル（DATA/CLOCK/LATCH、16 bit、MSB first）**、チップアドレスはピン 2 本で 4 通り〔DS p1・p11〕。VIH min 2.5 V／VIL max 1.5 V〔DS p5〕→ 3.3 V ロジックで直接つなげる〔推論〕。タイミングは µs 級（t1 min 4 µs）〔DS p11〕
- トーンの外付け: Bass は外付け C1・C2・R3 で f0 と Q が決まる（式と内部抵抗表あり、例 C1 100 nF・C2 4.7 µF・R3 4.7 kΩ）、Treble は外付け C1（3.3 nF）で決まる〔DS p9・p10〕
- パッケージ: SSOP32（NJW1194V）〔DS p1、製品頁〕。Nisshinbo の SSOP32 の頁でピッチ 0.65 mm・11 × 7.6 mm（外形図は DS に無く、別の資料）
- 入手性: Digi-Key の `NJW1194V-TE1` は "Active"、在庫なし・メーカー取り寄せ、**最小注文 2,000 個**、標準リードタイム 12 週（2026-09-26 に製品頁で確認）。秋月・マルツの取り扱いは確かめられず（マルツは Digi-Key の取り次ぎ）。LCSC は自動取得を拒否され確かめられず

### NJW1119A（Nisshinbo／旧 NJR）— `datasheets/tone/NJR_NJW1119A.pdf`（Ver 2.1、19 頁、Nisshinbo から 2026-09-26 取得）

- 構成: **トーン専用**（3 バンド: Bass/Middle/Treble、0〜±12 dB／1 dB、100 Hz/1 kHz/10 kHz）＋ ch ごとの MUTE、**入力セレクタも音量も無い**。入力 1 本・出力 1 本／ch〔DS NJW1119A p1・p2〕
- **バイパス**: `TSWa`/`TSWb : Tone Control By-pass Switch for each channel`（L/R 別）、D10＝0 で Tone Control OFF（**初期値**）〔DS p9〕。MUTE も ch ごと（`Mutea`/`Muteb`、初期値 Mute ON）〔DS p9〕。バイパスでも信号は入力（200 Ω・50 kΩ の等価回路）→ 出力バッファ（50 Ω）を通る〔DS p5 等価回路。内部の段の数は DS に無い〕
- 切替のポップ: 端子 SWCA/SWCB "Switching noise rejection capacitor"（応用回路で 10 µF）〔DS p2・p11〕。DC 電圧欄に "V-(sub)+0.7V (TONE=OFF)"〔DS p5〕。**TSW 切替のポップの値・ゼロクロスの記述は無い**（確かめられず）。NJW1194 のような「TSW 切替では MUTE を使え」の注も**この DS には無い**（無いことは安全の保証ではない〔推論〕）
- 電源: **±4.5〜±7.5 V（typ ±7 V）両電源**、絶対最大 ±8 V〔DS p3〕
- バイパス（Tone=OFF）の値（表）: VOM min 9.5 / typ 12.0 dBV（**3.0 / 4.0 Vrms**、f 1 kHz, THD 1 %）、GV −0.5/0/+0.5 dB（Vin 2 Vrms）、**VNO1 −120 typ / −110 max dBV（1.0 / 3.2 µVrms、A-weight, Rg 0）**、CS1 −100 typ / −90 max dB（1 kHz, A-weight）、**THD1 0.0002 % typ（2 Vrms, 1 kHz, BW 400 Hz–30 kHz）**、THD2 0.002 % typ（2 Vrms, 20 kHz）〔DS p3・p4〕
- トーン ON（全 0 dB）の値（表）: VNO2 −110 / −104 dBV（3.2 / 6.3 µVrms）、CS2 −100 / −90 dB、CS3 −80 dB typ（20 kHz）、THD3 0.002 typ / 0.02 max %（1 kHz）、THD4 0.005 %（20 kHz）、フラットの利得 ±1.5 dB〔DS p3・p4〕
- グラフ（目読み）: THD+N vs Frequency（Vin 2 Vrms, BW 10–80 kHz）TONE=OFF は約 0.0003〜0.0005 %、高域で約 0.003 % まで上がる／TONE=ON は約 0.002〜0.005 %〔DS p17〕。THD+N vs Input Voltage TONE=OFF は約 3〜4 Vrms で急増〔DS p16・p17〕。最大出力 vs 周波数 TONE=OFF 約 4.5 Vrms〔DS p15〕。**周波数特性（利得 vs 周波数）の TONE=OFF のグラフは無い**（1 kHz と 10 kHz の利得の温度特性だけ、TONE=OFF,ON とも約 0 dB〔DS p16〕）。チャンネル分離 vs 周波数（TONE=OFF）はあるが目盛の数字が埋め込みフォントの欠けで読めない〔DS p16〕
- 入力: 最大入力電圧 VIM = V+/V−（"Be careful to use in power supply voltage range"）〔DS p3〕。**"Any signal must not be inputted on the power “off”. It may affect initial condition of DATA CONTROL."**〔DS p3〕— 電源断のときの入力の保護・耐量は書かれていない
- 制御: 3 線シリアル（NJW1194 と同じ形式・タイミング）、チップアドレス 4 通り、VIH min 2.5 V／VIL max 1.5 V〔DS p4・p8〕→ 3.3 V で直接〔推論〕
- 外付け: Bass・Middle は外付けの C・R で f0 が決まる（式と表: Bass は C 100 nF・R 3.9 kΩ、Middle は 33 nF・4.7 nF・4.7 kΩ）、Treble は外付け C（2.2 nF）〔DS p11・p12〕
- パッケージ: SSOP32（NJW1119AV）〔DS p1〕
- 入手性: Mouser の `NJW1119AV-TE2` 頁は取得できず（503）。検索結果の要約では "non-stocked"〔確かめられず〕。Digi-Key は確かめられず

### NJW1192・NJW1201A（Nisshinbo、I²C）— 除外。`datasheets/tone/NJR_NJW1192.pdf`・`NJR_NJW1201A.pdf`

- どちらも I²C の音量＋トーン（NJW1192 は Bass/Treble、NJW1201A は 3 バンド）。**トーンのバイパスの制御ビットは DS に見当たらない**（"by-pass"/"bypass"/"TONE=OFF" の語が無い。トーンの「フラット」設定だけ）〔DS NJW1192 p1・p4、NJW1201A p1・p3〕
- 単電源（NJW1192 7.5〜13 V、NJW1201A 7.5〜10 V）で、**最大入力 VIM min 2.0 / typ 2.4 Vrms（V+ 9 V）**〔DS NJW1192 p3、NJW1201A p3〕→ 2.3 Vrms の上限を min で満たさない
- NJW1201A には `RecOut`・`MonOut` の出力がある〔DS p2 ピン表〕が、EC 表にこれらの出力の項目は無い（確かめられず）。パッケージ LQFP52〔DS p1〕
- NJW1192 の EC の条件は "all controls flat(Gv=0dB)"（トーン 0 dB）〔DS p3〕

### ROHM BD37033FV-M・BD37512FS・BD3490FV・BD3491FS（I²C のサウンドプロセッサ）— 除外

- 4 品とも DS に**トーンを飛ばすモードは見当たらない**（"bypass"/"through" の語なし。トーン 0 dB の設定だけ）〔各 DS の機能説明 p1・制御表〕。EC の共通条件はどれも**トーン 0 dB**（BD37033FV-M "Tone control 0dB" VCC 8.5 V〔p4〕、BD37512FS VCC 8.5 V〔p4〕、BD3490FV・BD3491FS "Bass 0dB, Treble 0dB" VCC 9.0 V〔p4・p3〕）
- 最大入力 VIM（min / typ）: BD37033FV-M 2.0 / 2.1 Vrms〔p4〕、BD37512FS 2.1 / 2.3 Vrms〔p4〕、BD3490FV・BD3491FS 2.1 / 2.4 Vrms〔p4〕→ **どれも 2.3 Vrms を min で満たさない**
- 単電源（BD37xxx 7.0〜9.5 V、BD349x 4.75〜9.5 V）〔p3・p4〕。入力の絶対最大 VCC+0.3〜GND−0.3 V（BD37512FS〔p4〕）
- I²C は 3.3 V でつなげる: BD37033FV-M・BD37512FS は "It is possible to control by 3.3V / 5V for I2C BUS"〔p1〕、BD349x は VIH min 2.3 V〔p7〕
- 目を引く機能: BD37xxx の "Advanced switch"（音量・MUTE・Bass/Treble の段の切替の雑音を減らす）〔BD37033FV-M p1、BD37512FS p1・p9 Figure 14/15〕。**バイパスではない**が、ソフトに絞る機能としては PT2314E に無いもの
- 自動取得: ROHM の製品頁（rohm.com）は 403 で取れず、入手性は確かめられず。DS は fscdn.rohm.com から取得（2026-09-26）
- 取得した DS: `ROHM_BD37033FV-M.pdf`・`ROHM_BD37512FS.pdf`・`ROHM_BD3490FV.pdf`・`ROHM_BD3491FS.pdf`

### NJU7391A（Nisshinbo、3 線）— 保留（トーンの OFF が制御表で定義されていない）。`datasheets/tone/NJR_NJU7391A.pdf`（18 頁）

- 5 入力セレクタ・入力利得・音量・2 バンドトーン・surround〔DS NJU7391A p1〕。単電源 4.7〜9.7 V〔p3〕
- EC 表の共通条件に "TONE=OFF" とある〔p3〕が、トーンの制御表には Bass/Treble とも 0 dB の符号が 2 つ（`1000` と `0000`＝初期値）あるだけで、**「OFF／BYPASS」の名の付いた設定は無い**〔p7〕。"BYPASS" は surround（`SUR`=00）と入力利得（`GVIN`=000）の設定名〔p8〕。→ 0000 が内部でトーン段を飛ばすのかは**確かめられず**
- 最大入力 VIM **typ 3.0 Vrms（min の記載なし）**、VOM typ 3.0 Vrms〔p3〕。THD+N2 0.01 % typ（Vo 2 Vrms）、VNO −110 typ / −97 max dBV（A-weight）、CT・CS は max −80 dB だけ〔p3〕（いずれも TONE=OFF, SUR=OFF の共通条件）
- 入力の絶対最大 0〜V+（"Don’t apply the input voltage that exceeds supply voltage."）〔p3〕。VIH min 2.6 V／VIL max 1.0 V〔p4〕

### Princeton PT2033（I²C）— バイパス無し。PT2314E の後継候補としてだけ記録。`datasheets/tone/Princeton_PT2033.pdf`（V1.4 September 2010、15 頁、princeton.com.tw から取得）

- 3 入力セレクタ＋音量＋Bass/Treble（±14 dB／2 dB）＋サブウーファ出力〔DS PT2033 p1〕。**トーンを飛ばすモードは DS に無い**（"bypass" は I²C の ACK の説明の中だけ〔p5〕）
- EC の共通条件 "Ta=25℃, VDD=9V, RL=100KΩ, Rg=600Ω, **all controls flat (G=0)**, f=1KHz"〔p12〕
- 最大入力 VCL min 2.5 / typ 2.7 Vrms（THD 0.3 %）、出力 VOCL min 2.5 / typ 2.7 Vrms〔p11・p12〕— **PT2314E（min 2.3 Vrms、THD 1 %）より余裕がある**。THD typ 0.003 / max 0.01 %（1 Vrms）、S/N typ 105 dB〔p11〕、チャンネル分離 min 85 / typ 95 dB〔p12〕
- 電源 4〜10 V（EC 表は 4〜9.7 V）〔p11・p12〕、VIH min 3 V〔p12〕（PT2314E と同じく 3.3 V では余裕が薄い〔推論〕）
- Princeton の現行の「Analog Audio Processor for Home Audio」一覧は **PT2312E・PT2313E・PT2314E・PT2315E・PT2033** の 5 品（princeton.com.tw、2026-09-26 閲覧）。一覧の "Special Feature" 欄にバイパスを挙げた品は無い。車載の一覧（PT12313・PT12913・PT12916・PT12919・PT2347・PT2348・PT12917）の特長欄は "Soft Step/Soft Mute, Direct Mute" 等で、バイパスは挙げられていない（**DS は読んでいない**）

### Princeton PT2322（I²C、6 ch）— "Tone Defeat" を持つが DS は抜粋しか取れず。`datasheets/tone/Princeton_PT2322_excerpt.pdf`（v1.0 November 2002、**3 頁の抜粋**、nikom.biz のミラー）

- 特長に **"Tone Defeat Function"**、説明に "3-band tone control (treble, middle, and bass), mute function, 3D effect function, tone defeat function"〔DS PT2322 抜粋 p1〕
- **EC 表・制御表・電源条件の頁が無い**。Tone Defeat で何を飛ばすか、最大入力、THD、ポップは**確かめられず**。検索要約に「J1=1 で TONE DEFEAT」とあるが一次資料で見ていない
- Princeton の現行のホームオーディオ一覧に**載っていない**（上）→ 現行品ではない可能性が高い〔推論〕。入手性は確かめられず

### ST TDA7439・TDA7468（I²C）— バイパス無し。`datasheets/tone/ST_TDA7439.pdf`（Rev.10 June 2004、ampslab.com のミラー）・`ST_TDA7468.pdf`（Rev.4 April 2010、mikroe のミラー）

- st.com からの取得は接続を切られて失敗（2026-09-26）。**ミラーの版が ST の最新版かは確かめられず**（検索結果に TDA7439 の Rev.11 March 2008 の存在が見える）
- どちらも **トーンを飛ばすモードは DS に無い**（"bypass"/"through" の語が無い）。どちらもセレクタの出口 `MUXOUT`/`MUX` ピンがあり、音量・トーンを通らない出力になっている〔DS TDA7439 p1 ブロック図・p2 ピン、TDA7468 p1 ピン〕
- EC の共通条件は "all controls flat (G = 0dB)"（VS 9 V）〔TDA7439 p3、TDA7468 p4〕
- 最大入力: TDA7439 "Max. input signal handling" 2 Vrms（Quick Reference）、入力のクリップ VCL min 2 / typ 2.5 Vrms（THD 0.3 %）、出力 VCLIP min 2.1 / typ 2.6 Vrms〔TDA7439 p2・p3・p4〕。TDA7468 VCL min 2 / typ 2.5 Vrms〔p4〕→ **2.3 Vrms を min で満たさない**
- TDA7439 の THD typ 0.01 / max 0.08 %（1 Vrms）、ENO typ 5 / max 15 µV（All gains 0 dB）、VIH min 3 V〔p4〕。電源 6〜10.2 V 単電源〔p2〕。パッケージ SDIP30（TDA7439）、SO28（TDA7468D）〔各 p1〕

### PT2314E（今の石、比較の相手）— バイパス無し

- 制御表は Bass/Treble の段（−14〜+14 dB）だけで、飛ばすモードは無い（"bypass" は I²C の ACK の説明だけ）〔DS PT2314E p6・p7・p9〕
- トーンを通らない出力としては、セレクタの出口 `LOUT`/`ROUT`（最小負荷 5 kΩ）がある〔[sw] §5、DS p12〕。今の図はセレクタを使っていない（`review/direct_bypass_review.md` §1）
- EC の共通条件は "all controls flat"（[sw] §5 の表の条件列）
