# 製品基板と一次資料から学べる配線 — 中国製 DAC 内蔵アンプの内部写真とレイアウト指針

- 作成: 2026-09-25（エージェント）。リポジトリで変えたのは、この記録と [cn_dac_amp_survey.md](cn_dac_amp_survey.md) の追加、[README.md](README.md) への一覧の追記だけ。回路図・PCB・スクリプト・DECISIONS・NOW は触っていない
- 目的: 製品の基板（分解写真・内部写真）と、チップメーカーのレイアウト指針・評価ボードから、配線技術として学べることを拾う。v2.1 の PCB（娘の引き直し、グランドの木、2×12 のスタック）の材料にする（§3）
- 範囲: 内部写真を実際に開いたのは 10 製品・約 35 枚と、TI のレイアウト例図 4 ページ。一次資料は TI / Cirrus / AKM / ESS / XMOS の DS・アプリノート・評価ボードのガイド
- 制約:
  - WiiM Amp / Amp Pro の内部写真は取れなかった（FCC 系のサイトが 403）。代わりに WiiM Ultra（DAC 内蔵ストリーマー）を見た
  - ADI MT-031 と H. Ott の原文も取れなかった。Ott を引いている TI SLYT499 / SLYT512 で代わりにした
  - AKM の DS はログインが要るので、AK4493 の DS（2017/12 版）のミラーを読んだ
  - **層数・内層のベタは、写真から分からないものは「不明」とした**

## 凡例（出典）

| 記号 | 意味 |
|---|---|
| [公式] / [分解] / [第三者] / [推定] / ✔ | [cn_dac_amp_survey.md](cn_dac_amp_survey.md) の凡例と同じ（[分解]＝内部写真を実際に開いて確認、✔＝この記録を書いたエージェントが原文で確かめ直した） |
| [TMUX7612 pN] | [../datasheets/TI_TMUX7612.pdf](../datasheets/TI_TMUX7612.pdf) を開いて読んだもの（p は PDF のページ） |
| [sw] | [../ds_facts/switch_control.md](../ds_facts/switch_control.md)（照合済み） |
| [DEC §n] | [../DECISIONS.md](../DECISIONS.md) の節。`V21-未決-nn` は §10 の ID |
| [NOW] | 2026-09-25 の [../NOW.md](../NOW.md)（「図と PCB の現況」の PCB の節） |

---

## 0. 結論（先に）

1. **グラウンドは「1 枚のベタを区画する」が一次資料の第一。** 分けるなら橋は 1 か所で、区画をまたぐ配線はすべて橋の上を通す（✔ TI SLYT512）。製品も広いベタにビアを多数打った作りで、写真では分割スリットが見えない（内層は不明）
2. **小容量のデカップは、IC と同じ面のピンのすぐ隣。** CS43131 は "must"（✔）、TMUX7612 は「非常に敏感な系では、コンデンサの接続にビアを使わない方がノイズ耐性で勝る場合がある」（✔）。製品写真も同じ面
3. **電源モジュールの後にもう一段入れ、負荷の近くに局所のレギュレータを置く**（WiiM Ultra・Topping A90D・Topping DX5 II・Fosi BT20A MAX）
4. **信号リレーは、切り替える端子のすぐ後ろ。ドライバは一列に並べる**（A90D・DX5 II・Fosi ZA3）
5. **信号の流れを一方向に並べ、敏感な段は出力端子の近くに置く**（Gustard X16、DX5 II の差し込み娘基板）
6. **v2.1 と違うのは、主にグラウンドの分け方とデカップの面**（§3）。一致しているのは、直角交差、TMUX の 0.1 µF＋1 µF、DIP-8 ソケット、SEL とアナログを並走させないこと（§4）

---

## 1. 基板ごとの観察

すべて [分解]（写真を開いて見たもの）。それ以外は行の中に書いた。

| 製品 | 写真の出典 | 見えたこと |
|---|---|---|
| Aiyima A07（TPA3255、2020 年版） | ASR の分解スレッド | **表**: 前面寄りに電源（XL7015 の DC-DC、12 V・3.3 V のレギュレータ）と NE5532×2（ソケット）。中央に TPA3255 と押出しヒートシンク（裏から 2 本のネジで留める）、その真横に大型電解 2 本。右側にトロイダル 4 個（2 列千鳥）と箱形フィルム C。スピーカー端子へはパッドから飛び線。**裏**: 出力経路はマスクを剥いだ銀色の太線（はんだ盛り）。ヒートシンク直下付近に格子状のビア。後面の RCA / 3.5 mm 入力から前面のオペアンプへ、細線 2〜3 本が基板の下縁に沿って走る。熱画像でヒートシンク最高 57 °C。層は両面に配線が見えるだけなので 2 層と [推定] |
| TI TPA3255EVM | SLOU441B の写真・配置図 [公式] | 入力（左）→ IC とヒートシンク（中央）→ トロイダル・フィルム C・バルク（右）→ 出力端子（右端）の一方向。✔ "Double-sided, plated-through, 2-oz. Cu 2-layer PCB layout" |
| Fosi Audio ZA3 | TNT-Audio の内部写真、製品ページの注記画像と区画図 | 後面の辺にスピーカー端子 → フィルム C（2×2）→ リレー（公式の注記では Omron）→ Sumida のインダクタの順。周りに広いマスク開口の銅面があり、両脇を 2200 µF / 63 V が挟む。XLR / RCA 入力はバルクのすぐ隣で、XLR 入力用のオペアンプはその直後。前面に L/R 用・サブ用のオペアンプ（DIP-8 ソケット）とボリューム。TPA3255 は裏面実装で、ヒートシンクは筐体へ [公式：注記]。区画図は出力段を "Digital"、それを三方から囲むプリ・入力部を "Analog" と塗り分ける [公式：販促図。GND を実際に切っているかは不明] |
| SMSL AD18（PWM 変調器内蔵の Class-D＋BT） | HiFiGuides の分解スレッド（原寸画像） | TAS5508C（印字）の直横に 13.500 MHz の水晶。MLCC は同じ面で QFP を囲み、近くに TO-252 のリニアレギュレータ。出力段は櫛形ヒートシンクの下で、バルク 2 本・丸形インダクタ 4 個・箱形フィルム C。フィルタ直近の 4 ピンコネクタから太い 4 芯で後面のスピーカー端子の小基板へ。BT はキャスタレーションのモジュールで、同軸で後面のアンテナへ。**裏**: ほぼ全面ベタでビアが散在、大電流線の端は多数のビアを束ねている |
| Topping DX5 II | ASR の分解スレッド | AC 入口（コモンモードチョーク・Y コン）と AC-DC モジュール ATAZ AD30-B15（15 V）を主基板に直載せ。TPS5430×2 で ±15 V 系。XMOS 周りに 0.9 / 1.8 / 3.3 V の降圧、I/V 付近に ±5.8 V。各レールの試験パッドの脇に電圧をシルク印字。I/V と HP 入力段は SIP ピンで差し込む娘基板で、XLR 出力のすぐ近く。HP 出力の直横に G6K-2P-Y（12 V）×3。表はほぼベタで、微細なビアが全面に散在。XLR 出力寄りに角丸の境界で囲われた区画（用途と層数は不明） |
| Topping A90D | ASR の分解スレッド | Mean Well IRM-20-15×2 を基板に載せ、その直後に 101 のシールドインダクタ×4 と 470 µF（後段の LC と [推定]）。ロジック用に 317D2T×3。G6K-2P-Y を入力 XLR / RCA の真後ろに一列、右側に 2 列×4、出力付近にも。SOT-23 のトランジスタを一列に並べて駆動（記事では SS8050×15 [第三者]）。MCU・Flash は左下の隅に分けて置く。基板と筐体の間に銅の接地点 [第三者] |
| FiiO K11 | FiiO のニュース（AudioTOP の分解写真） | CS43198 の MLCC は同じ面で IC を囲む。DAC 周りなどにシールド缶用フレームのパッド輪郭（缶は未実装）。USB は SA9312L のキャスタレーション小モジュールで、12 MHz 水晶はモジュール上。I²S / SPDIF・SPI の試験点にシルクで信号名。RCA の直横に、裏面から筐体へ当たる金メッキのばねピン（筐体の金属層に接地するという説明は [第三者]） |
| Gustard X16 | AV Mentor の内部写真（低解像度） | デジタル入力側（右上）に XMOS・CPLD・CS8422・BT。49.1520 MHz と 45.1584 MHz の発振器を並べて DAC 寄りに置く。AES 入力にパルストランス（PE-65612NL）。DAC×2 は中央で上下ミラー配置。OPA1612 とフィルム C の出力段はアナログ出力端子のすぐ手前。内部に信号ケーブルが無い。局所のリニアレギュレータは [第三者] |
| WiiM Ultra（DAC 内蔵ストリーマー） | audiocolumn.com の分解（2025/07） | AC 入口（ヒューズ・X コン・コモンモードチョーク）と ATAZ AD20-B12 を主基板の一角に置き、シルク線で囲って区画。モジュールの出力にトロイダルコイル、その先に 4R7 の降圧。Linkplay のモジュールはシールド缶付きで主基板にはんだ付けし、同軸で Wi-Fi アンテナへ。主基板とサブ基板の 2 階建てで、FPC とハーネスでつなぐ。裏は規則的なビア格子。RTL8152B（LAN）・GL852G（USB ハブ）はそれぞれ直近に水晶 |
| soundcore Ace A1（Jieli＋HT8691R） | 52audio の分解記事 | Jieli の SoC の直横に 24 MHz 水晶。基板端に蛇行パターンのアンテナがあり、周りにベタが無い。D 級アンプ HT8691R の直横に昇圧用の 4R7 と SS54、スピーカーのコネクタも隣。外周にビア列（チップの説明は [第三者]） |

---

## 2. テーマ別に学べること

### 2.1 グラウンド

- **1 枚のベタを区画するのが基本で、分割は最後の手段**
  - ✔ TI SLYT512: "A better approach is partitioning. It is always preferable to use only one ground plane, partitioning the PCB…"。分けるなら、橋は 1 か所で、またぐ配線はすべてその上を通す [公式]
  - TI SLYT499: EMC 試験で起きる問題の多くは、スリットや分割をまたぐ配線が原因。リターン電流は配線の直下を流れる [公式]
- **変換器の GND ピンは同じ面へ**
  - ✔ AK4493: "AVSS, DVSS, VSSL and VSSR must be connected to the same analog ground plane."。VSS 間にインピーダンスがあると THD+N が悪くなる [公式]
  - CS43131: GNDA / GNDCP / GNDD を共通のグラウンド領域につなぎ、空いた領域はベタで埋める。ヘッドホンの基準（HPREFA/B）はコネクタの GND ピンまで個別に引き、そこでビアを打って GND 面へ [公式]
- **Class-D**
  - ✔ TPA3255: "Use an unbroken ground plane to have good low impedance and inductance return path to the power supply"。入力は、つながる音源のグランドと一緒に短く引く [公式]
  - TPA3116D2: GND はすべて IC の GND パッドに集め、そこをスター点にする＝星型は IC 単位の局所で使う [公式]
- **製品**: DX5 II（表）、WiiM Ultra（裏）、SMSL AD18（裏）は、広いベタにビアを多数打った作り。写真で分割スリットは見えない（内層は不明）[分解]。ガードトレースは見た範囲に無かった [分解]
- **筐体への接地は入出力端子のそば**: FiiO K11 は RCA の直横にばねピン [分解]、A90D は基板と筐体の間に接地点 [第三者]。SLYT512 は、筐体への接続に食い込みワッシャなどを使い、陽極酸化アルミは絶縁体として扱うよう注意している [公式]
- 補足〔推定〕: 「リターン電流は配線の直下」は高い周波数の話。可聴帯では帰り電流は抵抗の低い方へ広がる。直下の話が効いてくるのは、DC-DC のスイッチング帯とデジタルのエッジ

### 2.2 デカップリング

- ✔ CS43131: "To minimize inductance effects, the low-value ceramic capacitor must be closest to the pin and mounted on the same side of the board as the CS43131." [公式]
- ✔ TMUX7612: 0.1〜10 µF を VDD・VSS に。"For very sensitive systems, or for systems in harsh noise environments, avoiding the use of vias for connecting the capacitors to the device pins may offer superior noise immunity."。並列ビアは GND・電源面への接続に有利 [TMUX7612 p33]。推奨は 0.1 µF と 1 µF で、小さい方をピンの最寄りに [TMUX7612 p34]。✔ レイアウト例図（Figure 8-6）は、コンデンサを IC の隣に置いて "Wide (low inductance) trace for power" でつなぎ、GND 側は "Via to ground plane" [TMUX7612 p34、画像で確認]
- XMOS: 100 nF を少なくとも 8 個、デカップの GND 側は GND ピンまで最短 [公式]
- PCM1804: 0.1 µF セラミック＋10 µF タンタルをピン近くに [sw §6]
- 製品写真: FiiO K11 の CS43198、SMSL AD18 の TAS5508C とも、MLCC を同じ面で IC の周りに置いている [分解]

### 2.3 電源

- **局所レギュレーション**: DX5 II は降圧と LDO を基板全体に散らし、試験パッドの脇に電圧をシルク印字 [分解]。A90D はロジック用に LM317×3 [分解][第三者]。Gustard X16 も局所のリニア [第三者]
- **モジュールの後にもう一段**:
  - WiiM Ultra: AC-DC モジュール（ATAZ AD20-B12）→ トロイダル → 降圧 [分解]
  - A90D: Mean Well IRM-20-15×2 → シールドインダクタ×4＋470 µF [分解]（LC と [推定]）
  - DX5 II: 15 V モジュール（ATAZ AD30-B15）→ TPS5430×2 で ±15 V [分解]
  - Fosi BT20A MAX: オペアンプ用の ±15 V を DC-DC＋LDO で作り、DAC と BT は別々の 3.3 V LDO [公式：電源図]
- **DAC の基準電源は別扱い**: AK4493 の VREF は 0.1 µF＋470 µF をピン直近に、必要なら 10 Ω を足して 17 Hz の LPF。クロックは VREF から離す [公式]。ES9038Q2M の AVCC_L/R は出力段の基準電源で、AGND_L/R は ch ごとに別ピン [公式]
- **Class-D の PVDD**: TPA3255 はバルクをヒートシンクが許す限り近く、太い配線を表層でビアを通さず [公式]。TAS5825M は PVDD のコンデンサが遠いと出力にリンギングが出て、絶対最大を超えうる [公式]

### 2.4 クロック・デジタル線

- **44.1 kHz 系と 48 kHz 系の発振器を 2 個並べ、DAC の近くに置く**: Gustard X16（45.1584 / 49.152 MHz）[分解]、Cirrus CDB43131（22.5792 / 24.576 MHz を選択式）[公式：回路図]
- **発振子は使う IC の真横**: SMSL AD18、soundcore Ace A1、FiiO K11（USB モジュール上）、WiiM Ultra（LAN・USB ハブ）[分解]
- **MCLK はダンピング抵抗越し**: AK4493 の推奨 "It is recommended to input MCLK via a damping resistor" [公式]。製品写真では I²S の直列抵抗は判別できなかった
- **USB**: 90 Ω 差動、D+/D− のスキューは 1 mm 以下、スタブ禁止。途切れない面の上を通し、クロックや磁性部品の近くを通さない（XMOS）[公式]
- **試験点に信号名**: FiiO K11 は I²S・SPI の試験点にシルクで名前 [分解]
- **デジタルアイソレータは、見た 10 枚には無かった**（Gustard X16 の AES 入力のパルストランスだけ）[分解]
- **I²C のレベル変換**: Cirrus CDB43131 は 1.8 V ↔ 3.3 V を TXS0102（プルアップ 3.3 k / 4.7 k）[公式]。標準モードの立ち上がり上限 1000 ns から、プルアップの上限は Rp(max) = tr / (0.8473·Cb)（TI SLVA689）[公式]

### 2.5 リレー・アナログスイッチ

- **信号リレーは、切り替える端子のすぐ後ろ**: A90D は入力 XLR / RCA の真後ろに一列、出力付近にも。DX5 II は HP 出力の直横。Fosi ZA3 はスピーカー端子の脇 [分解][公式：注記]
- **ドライバは一列に並べる**: A90D は SOT-23 のトランジスタを一列 [分解]。フライバックダイオードは写真で確認できなかった。v2.1 のドライバ TBD62083A は各出力にクランプダイオードを内蔵している [sw]
- ✔ **TMUX7612**:
  - "Keep the input lines as short as possible."、"Use a solid ground plane to help reduce electromagnetic interference (EMI) noise pickup." [TMUX7612 p34]
  - "Do not run sensitive analog traces in parallel with digital traces. Avoid crossing digital and analog traces if possible, and only make perpendicular crossings when necessary." [TMUX7612 p34]
  - "Always make sure a solid ground (GND) connection is established before supplies are ramped." [TMUX7612 p33][sw §1]

### 2.6 ゾーニング・基板の分け方・基板間

- **一方向に並べる**: Gustard X16 はデジタル入力（XMOS・CPLD・CS8422・BT）が上、DAC×2 は中央で上下ミラー、出力段は出力端子のすぐ手前。内部に信号ケーブルが無い [分解]
- **敏感な段を差し込み娘基板にして、出力端子の近くへ**: DX5 II の I/V と HP 入力段 [分解]
- **無線・USB はモジュールにする**: WiiM Ultra の Linkplay はシールド缶付きで、同軸でアンテナへ。FiiO K11 は SA9312L のモジュール（水晶もモジュール上）[分解]。K11 はシールド缶のフレームのパッドだけ用意して未実装（後から足せる形）[分解]
- **区画をシルクで示す**: WiiM Ultra は AC 部をシルク線で囲う [分解]。Fosi ZA3 は区画図を公開している [公式]
- **MCU・Flash は隅に分ける**（A90D）[分解]
- **2 階建て**: WiiM Ultra は主基板とサブ基板を FPC とハーネスでつなぐ [分解]
- **基板間（TI SLYT512）**:
  - ✔ "The PCB connector should have at least 30 to 40% of its pins devoted to ground." [公式]
  - 基準面は 1 枚にする（マザーボードを背面板にして連続したグランド面を持たせる）[公式]
  - 電源はデジタル区画から入れ、そこから濾波・安定化してアナログへ回す [公式]

### 2.7 Class-D と熱（v2.1 には無いが、小さなループの考え方は同じ）

- **一方向**: TPA3255 の例図・EVM、TAS5825M の例図は、どれも入力 → IC → LC → 端子の一方向 [公式]。Aiyima A07 と Fosi ZA3 は後面入力 → 前面プリ → 中央の出力段と U ターンするが、A07 は入力の細線を裏面の基板縁に寄せて出力段から離している [分解]
- **ループを小さく**: TPA3116D2 は、出力 → フェライト → 小容量 C → GND のループがアンテナになるので小さくするよう求める。スナバ（例 18 Ω＋330 pF）は IC の GND ピンへ直接戻し、フィルタは出力端子の近くに置く [公式]
- **大電流**: TPA3255 は表層で、ビアを通さずに引く [公式]。製品は、A07 が裏面のマスク開口にはんだを盛り、AD18 が裏面の太線とビアの束で逃がす [分解]
- **インダクタ**: 線形性（Isat）が THD を左右する。Cg を GND へ落とす型は高域のデカップが良い（TI SLAA701B）[公式]。製品はトロイダル（A07・EVM）、角形（ZA3）、丸形シールド（AD18）で、どれもフィルム C と端子を隣接させている [分解]
- **熱**: TPA3255 / TAS5825M は GND ピンから銅を連続させ、熱ビアは放射状、サーマルリリーフ無し、IC は基板端と他の発熱体から離し、ヒートシンクは PCB の GND へ [公式]。A07 はヒートシンクを基板貫通のネジで留め、ZA3 は IC を裏面に実装して筐体へ放熱 [分解][公式]

---

## 3. v2.1 と違うところ（判定ではなく、確かめどころ）

1. **グラウンドの分け方**
   - v2.1 は「ベタ GND は 1 枚にしない。系統ごとに別ゾーンで、NetTie の星で一点接続」[NOW]。ADC のグランドの木は付け替える（[DEC §4-4]）。NetTie 群とグランド選択ヘッダを 1 か所に寄せ、`ADC_GND` の島は 1 か所でしか外とつながらないゾーンにする（V21-未決-19）
   - 一次資料の第一は「1 枚を区画」。分ける場合の条件「橋は 1 か所、またぐ配線は全部その上」から見ると、V21-未決-19 の「1 か所に寄せる」は同じ向き〔推定〕
   - 確かめどころは、系統をまたぐ線（ADC の I²S、PT2314E の I²C、娘への制御線、コイルの駆動）の帰りが、橋の近くを通るか
2. **デカップの面**
   - v2.1 の娘は TMUX の 100 nF・1 µF を本体直下の裏に置き、Amp のデカップの裏置きは「減点しない」[NOW]
   - 製品と一次資料は同じ面（CS43131 は must、TMUX7612 は「ビアを使わない方が有利な場合がある」）。差が出るのは MHz 帯〔推定〕
   - v2.1 は娘を引き直す（[NOW]「PCB」）ので、置き方を選び直せる
3. **±15 V の後段**: 製品はモジュールの後に必ずもう一段入れ、負荷の近くで局所に安定化している。v2.1 は ch ごとの LDO（[DEC §3-3]）、LDO 前のフィルタの形（V21-未決-11）、PD 入口の CMC の足場（[DEC §3-9]）で同じ向き
4. **2×12 のスタックの内訳**（V21-未決-22）
   - SLYT512 の「GND を 30〜40 %」を 24 ピンに当てると 7〜10 本〔計算〕
   - SLYT512 はデジタルの多基板系の話で、電源（±15 V・コイル）を通すスタックにそのまま当てはまるかは別〔推定〕
5. **シャーシの 1 点**（V21-未決-15）: 製品は入出力端子のそばで筐体へ落としている（FiiO K11・A90D）。陽極酸化アルミは絶縁体として扱う（SLYT512）
6. **リレーの置き場所**
   - 製品は、切り替える端子の直後に置く。v2.1 の音声用リレーは娘とバス（スタック）の境目にある（[DEC §2-3]）ので、スタックのコネクタの近くに置くのが製品の並びに当たる〔推定〕
   - 縦積みのリレーは上下・隣とも 5 mm 以上離す（V21-未決-19、DS の制約）
7. **抜き挿し**: TMUX7612 は「電源より先に GND」。v2.1 は活線で抜き挿ししない運用を推奨している（V21-未決-25）ので、コネクタに GND の先行接触を求める必要は薄い〔推定〕

## 4. 一致しているところ

- SEL とアナログ、L と R を並走させず、交差は直角だけにしている（[NOW] の配線の教訓）。TMUX7612 の推奨どおり [TMUX7612 p34]
- TMUX のデカップを DS の推奨どおり 0.1 µF＋1 µF にしている [TMUX7612 p34][NOW]
- DIP-8 ソケット（Aiyima A07・Fosi ZA3・Fosi BT20A Pro も）
- 信号リレー（AZ850 は、製品で多い G6K-2P-Y と同じ小信号のクラス）
- ch ごとの LDO（製品の局所レギュレーションと同じ考え方）

---

## 出典

### 製品の写真
- Aiyima A07: https://www.audiosciencereview.com/forum/index.php?threads/aiyima-a07-tpa3255-tear-down.19020/
- Topping DX5 II: https://www.audiosciencereview.com/forum/index.php?threads/topping-dx5ii-teardown.64527/
- Topping A90D: https://www.audiosciencereview.com/forum/index.php?threads/topping-a90-discrete-a90d-teardown-and-personal-thoughts.48717/
- Fosi Audio ZA3: https://www.tnt-audio.com/ampli/fosi_za3_e.html（写真 https://www.tnt-audio.com/jpg/fosi_za3_inside.jpg）／ 製品ページ https://fosiaudio.com/products/fosi-audio-za3-balanced-dual-mode-class-d-amplifier（注記 https://fosiaudio.com/cdn/shop/files/004_2_60a9f920-bec0-48a8-9654-5ee3f8bd07d5.png、区画図 https://fosiaudio.com/cdn/shop/files/005_4.png）
- SMSL AD18: https://forum.hifiguides.com/t/smsl-ad-18-teardown/12087
- FiiO K11: https://www.fiio.com/newsinfo/875896.html
- Gustard X16: https://avmentor.net/reviews/2021/gustard_dac_x16_1.shtml
- WiiM Ultra: https://audiocolumn.com/linearpower/11743/
- soundcore Ace A1: https://www.52audio.com/archives/153414.html

### 一次資料
- TI: TPA3255 https://www.ti.com/lit/ds/symlink/tpa3255.pdf ／ TPA3255EVM https://www.ti.com/lit/ug/slou441b/slou441b.pdf ／ TPA3116D2 https://www.ti.com/lit/ds/symlink/tpa3116d2.pdf ／ TAS5825M https://www.ti.com/lit/ds/symlink/tas5825m.pdf ／ LC フィルタ（中身は SLAA701B）https://www.ti.com/lit/an/sloa119b/sloa119b.pdf ／ SLYT499 https://www.ti.com/lit/an/slyt499/slyt499.pdf ／ SLYT512 https://www.ti.com/lit/an/slyt512/slyt512.pdf ／ I²C のプルアップ SLVA689 https://www.ti.com/lit/an/slva689/slva689.pdf
- ESS ES9038Q2M: https://www.esstech.com/wp-content/uploads/2022/09/ES9038Q2M-Datasheet-v1.4.pdf
- AKM AK4493（DS のミラー）: https://d.zaix.ru/5cHC.pdf
- Cirrus: CS43131 https://statics.cirrus.com/pubs/proDatasheet/CS43131_DS1155F2.pdf ／ CDB43131 https://statics.cirrus.com/pubs/manual/CDB43131_REV_B_Schematic_Layout.pdf
- XMOS XU316: https://www.xmos.com/documentation/XM-014034-PC/html/rst/XU316-1024-QF60A.html
- v2.1 の中の DS: [../datasheets/TI_TMUX7612.pdf](../datasheets/TI_TMUX7612.pdf)（p33〜34）、[../datasheets/Toshiba_TBD62083A.pdf](../datasheets/Toshiba_TBD62083A.pdf)、[../datasheets/TI_PCM1804.pdf](../datasheets/TI_PCM1804.pdf)（いずれも [sw] に照合済みの行がある）

### 取れなかったもの
- WiiM Amp / Amp Pro の FCC の内部写真（fccid.io・fcc.report・FCC 本体が 403）、WiiM フォーラム（curl を通さない）
- ADI MT-031（analog.com が応答しない）、H. Ott の原文（403）
