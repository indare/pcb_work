# 中国製 DAC 内蔵アンプの音量・EQ・エフェクト・切替 — 製品と部品の調査

- 作成: 2026-09-25（エージェント）。**リポジトリで変えたのは、この記録と [product_board_layout.md](product_board_layout.md) の追加、[README.md](README.md) への一覧の追記だけ**。回路図・スクリプト・DECISIONS・NOW・PARTS・ファームは触っていない
- 目的: 最近多い中国製の DAC 内蔵アンプが、デジタルボリューム・エフェクト・グライコ・アンプの切替をどう実装しているかを、製品と部品の両側から確かめる。v2.1 の未決の材料にする（§6）
- 範囲: スピーカー用 20 機種、ヘッドホン用（据え置き・ドングル・BT）20 機種強、部品 70 品番強。2023〜2026 年の製品を優先し、技術の説明に要る定番機は古くても入れた。**配線（製品基板から学べること）は [product_board_layout.md](product_board_layout.md)**
- 調べ方: 4 つの調査エージェントが製品ページ・マニュアル・データシート・分解記事を読み、内部写真は画像を開いて見た。主要な主張の一部（✔）は、この記録を書いたエージェントが原文で確かめ直した

## 凡例（出典）

| 記号 | 意味 |
|---|---|
| [公式] | メーカーの製品ページ・マニュアル・データシート（製品メーカー・チップメーカーとも） |
| [分解] | 内部写真を実際に開いて確認したもの |
| [第三者] | レビュー・販売店・フォーラム・リバースエンジニアリングの記述（未検証） |
| [推定] | 推論。理由を添える |
| ✔ | この記録を書いたエージェントが原文（DS のページ・製品ページ）で確かめ直したもの |
| [PT2314E pN] | [../datasheets/Princeton_PT2314E.pdf](../datasheets/Princeton_PT2314E.pdf) を開いて読んだもの（p は PDF のページ） |
| [sw] | [../ds_facts/switch_control.md](../ds_facts/switch_control.md)（照合済み） |
| [DEC §n] | [../DECISIONS.md](../DECISIONS.md) の節。`V21-未決-nn` などは §10 の ID |
| [NL] | このセッションで `kicad-cli sch export netlist` した `AudioV2.1/AudioV2Case.kicad_sch`（2026-09-25 の図）のネットリスト |

- 発売年はレビューの日付・基板のシルクから見た目安
- URL は末尾に製品名・品番ごとにまとめた。取れなかった資料（403 など）も末尾に書いた

---

## 0. 結論（先に）

1. **音量はほとんどデジタル。** 置き場所は DAC の内部（ESS / Cirrus の 0.5 dB 刻み＋ソフトランプ）、SoC（アナログ入力も ADC でデジタル化してから）、デジタルアンプのレジスタのどれか
2. **アナログで音量を持つ製品は 3 通り**: 電子ボリューム IC を MCU から制御（NJW1194 / NJW1195A / NJU72315 / PGA2311）、リレーで抵抗を切り替えて粗く・DAC で細かく、ポット（リモコン対応はモーター付き）
3. **EQ・エフェクトは、見つかったものは全部デジタル。** 処理場所は SoC・DSP 内蔵 Class-D・USB ブリッジのファーム・BT SoC の DSP・専用 DSP・DAC 内蔵フィルタの 6 つ。アナログのグライコ IC はほぼ消え、アナログ機は Bass/Treble とトーン無効化（中点デテント・BYPASS スイッチ）止まり
4. **切替は小信号リレー。** Omron G6K-2P-Y を Topping・Fosi の複数機の写真で確認した。安い CMOS マルチプレクサ（CD4052B）は THD 0.12〜0.3 % で Hi-Fi には粗い
5. **オペアンプは DIP-8 ソケットでの手差し替えだけだった（中国ブランドの範囲）。** 電子的に切り替える製品は、v2.1 が参考にしている共立電子 KP-HAMP61（[DEC §2-10]）のほかには見つからなかった
6. **AudioV2.1 に近いのは「DAC ＋ アナログ電子ボリューム IC」型**（SMSL・Loxjie の NJW1194）と「アナログのまま」型（Fosi）。PT2314E は TDA731x と同じ系統の TV・ミニコンポ向けの石で、同じ位置に置く部品として今の製品は NJW1194 を使っている
7. **PT2314E は `LIN`/`RIN` から入れてもマスター音量とスピーカー ATT を通り、DS はリセット後のレジスタ値を書いていない**（§5）。[DEC §10-1] の「PT2314E の POR 直後の音量状態」の材料

---

## 1. 音量

### 1.1 方式の類型

| 方式 | 代表例（部品） | 特徴 |
|---|---|---|
| **A. DAC 内部のデジタル音量** | Moondrop Moonriver 2 Ti（CS43198、「100-level smooth DAC volume」[公式]）、Topping DX5 II（ES9039Q2M×2 [第三者]、DAC 内と [推定]） | ヘッドホン機の多数派。ES9039Q2M は 0〜−127.5 dB を 0.5 dB 刻み＋ソフトランプ、CS43198 は 0.5 dB 刻みで 1/8 dB 刻みのソフトランプ（約 1 dB/ms）[公式]。小音量のノイズはゲインの 2〜5 段で逃がす |
| **B. ADC で全部デジタル化して SoC で** | WiiM Amp / Amp Pro / Amp Ultra、Eversolo Play | ライン入力も ADC（WiiM は PCM1861 [公式]）を通す。音量・EQ・ルーム補正・サブのクロスオーバが全入力に同じように効く |
| **C. デジタルアンプのレジスタ** | Aiyima D03（TAS5548 → TAS5624）、FX-Audio D802C PRO（STA326） | DAC を持たず、アナログ入力は ADC（PCM1808 / WM8782S）[公式]。音量・トーン・ラウドネス・DRC は PWM プロセッサ内 [推定：チップの機能から] |
| **D. アナログ電子ボリューム IC を MCU から** | SMSL AO200 MKII / AO300、Loxjie A30 / A40 → NJW1194。FiiO K11 R2R → NJW1195A。FiiO K7 / K9 Pro → NJU72315×2。xDuoo XD05 Pro → PGA2311 [第三者] | ✔ NJW1194 は 1 チップで 4 入力セレクタ・音量 +31.5〜−95 dB（0.5 dB）・トーン 0〜±10 dB（1 dB）・ゼロクロス検出、電源 ±4.5〜±7.5 V、THD 0.0015 % [公式]。✔ **K9 Pro ESS の仕様表は「Potentiometer+ADC Sampling」。ポットは位置を読むセンサで、減衰は IC** [公式] |
| **E. リレー＋抵抗（粗）＋ DAC（細）** | Topping DX9 15 周年版（G6K-2P-Y×8 [分解]、6 dB ごとにリレー音 [第三者]）、Cayin RU7（抵抗 3 区間をリレーで切替、100 段 [公式]） | DX9 は L/R 各 4 リレーの 2 進重みで粗調・DAC の 0.5 dB で微調と読むと、6 dB ごとのクリックと合う [推定] |
| **F. ポット** | Fosi BT20A Pro（手回し）、Fosi BT20A MAX（モーター付き。リモコンでノブが回る [公式][分解]）、WiiM Vibelink Amp、iBasso DC-Elite（24 段・4 連の段付きアッテネータ [公式]） | ✔ WiiM は Vibelink Amp にリモコンを付けなかった理由を「ノブのモーター化に部品が要る」「簡素さとコスト」と公式ブログで説明 |

### 1.2 スピーカー用（DAC 内蔵プリメイン・ストリーミングアンプ）

| 機種（年） | DAC | パワー段 | SoC・USB・BT・ADC | 音量 | EQ・エフェクト・切替 |
|---|---|---|---|---|---|
| WiiM Amp（2023） | ES9018K2M [公式] | TPA3255（アナログ入力）[公式] | Linkplay A98G（Amlogic A113X）[第三者]、ADC PCM1861 [公式]、サブ出力の DAC PCM5121 [第三者] | デジタル（SoC か DAC かは未確認） | 10 バンド GEQ＋PEQ、ルーム補正、サブのクロスオーバ [公式][第三者] |
| WiiM Amp Pro（2025 頃） | ES9038Q2M [公式] | TPA3255 [公式] | ADC PCM1861、「Line In は ADC でデジタル化」[公式] | デジタル。音量上限・バランス・固定出力 [公式] | 入力ごとに EQ（プリセット 24＋10 バンド GEQ/PEQ）、ルーム補正、Sub Out [公式] |
| WiiM Amp Ultra（2025） | ES9039Q2M [公式] | TPA3255×2＋PFFB、OPA1612×6 [公式] | 未確認 | 未確認 | 入力ごとに 10 バンド GEQ/PEQ、RoomFit（スマホのマイクで 1 点測定）、サブのクロスオーバ 30〜250 Hz を 1 Hz 刻み [第三者] |
| WiiM Vibelink Amp（2025） | ES9039Q2M [公式] | TPA3255、OPA1612×6 [公式] | 配信機能なし。✔ RCA 入力は DAC を通らない [公式] | ✔ 物理ノブのみ [公式] | なし。12 V トリガ [公式] |
| Eversolo Play（2024–25） | AK4493S（AK4493EQ とする記事も）[第三者] | TPA3255 [第三者] | Android ベース。ライン・フォノ（MM/MC）はデジタル化 [第三者] | デジタル [推定：全入力がデジタル化されるので] | PEQ＋GEQ、スイープ測定による自動ルーム補正、サブのレベル・クロスオーバ（40〜500 Hz）・位相・遅延 [第三者] |
| Arylic A50+（2020 頃〜） | 版により STA326 / ES9023＋TPA3116 / NTP8835 [公式：メーカー担当者のフォーラム発言] | 同左 | 未確認 | STA326・NTP8835 の版はアンプ IC 内 [推定] | **部品不足のときにアンプ IC ごと差し替えた 3 版がある**。内蔵 Web ページで版を判別する |
| Arylic Up2Stream Amp V4（DIY 基板） | MVSilicon の DSP チップ内で変換 [第三者] | TPA3116D2 [公式] | 全ソースを 16 bit / 44.1 kHz に再サンプル [第三者] | DSP 内 [推定] | EQ 最大 10 点、Stereo Widen、MV3D、リミッタ／コンプ／エキスパンダ（ACPWorkbench で調整）[第三者] |
| SMSL AO300 / AO300 PRO（2023–25） | CS43131（DAC＋HPA）[公式] | MA5332MS（アナログ入力）[公式] | XU316、BT 5.0（PRO は 5.3）、HDMI ARC（PRO は eARC）[公式] | ✔ NJW1194 [公式]。入力セレクタも同じ IC と公式の説明画像にある | Direct／Tone／SDB／Bass／Super Bass／Rock／Soft／Clear、Bass/Treble ±9 dB、DAC フィルタ 5 種 [公式] |
| SMSL AO200 MKII（2023） | 未確認 | MA5332MS [公式] | BT 5.0 | NJW1194 [公式] | SDB＋Bass/Treble、サブ用プリアウト [公式] |
| SMSL SA300（2020 頃） | 未確認 | MA12070（アナログ入力版）[第三者] | BT 5.0、USB [第三者] | 未確認 | Super Bass など、Bass/Treble ±10 dB [第三者] |
| Loxjie A30（2020–21） | ES9023 [公式] | MA12070、HP 100 mW/32 Ω [公式] | BT 5.0、USB [公式] | NJW1194 [公式] | EQ 7 種、Bass/Treble 1 dB 刻み [公式]（NJW1194 のトーン仕様と一致 [推定]） |
| Loxjie A40（2023–24） | CS43131 [第三者] | MA5332MS [第三者] | QCC5125、XU316、フォノ、HDMI ARC [第三者] | NJW1194 [第三者] | プリセット 8、Bass/Treble ±9 dB、フィルタ 5 [第三者]。主要チップが AO300 と同じ |
| Topping MX3s（2023） | AK4377 [第三者] | Merus Class-D（型番未確認）[第三者] | QCC3040 [第三者] | 未確認。ゲイン 2 段 [第三者] | Bass/Treble ±10 dB [第三者] |
| Aiyima D03（2021–22） | なし | TAS5548 → TAS5624（PWM 入力のパワー段）[公式] | CS8422、QCC3034、SA9123I、ADC PCM1808、DRV603 [公式] | TAS5548 の音量（+18〜−127 dB）[推定：公式のチップ仕様から] | Bass/Treble ±14 dB・ラウドネス [公式]。TAS5548 は 7 BQ/ch・トーン・DRC×2 を持つ [公式] |
| Aiyima T9 Pro（2022–23） | ES9018K2M [公式] | TPA3250 [公式] | QCC3040、USB [公式] | エンコーダ＋リモコン [公式] | Bass/Treble。真空管 JAN5725 を 6AK5 などに差し替え可、OPA1656 [公式] |
| FX-Audio D802C PRO（旧定番） | なし | STA326（I²S 入力の 2.1ch）[公式] | AK4113（S/PDIF）、CM6642（USB）、CSRA64215（BT）、ADC WM8782S [公式] | STA326 内 [推定] | STA326 は 4 BQ/ch＋トーンを持つ [公式] |
| Fosi BT20A Pro（2022–23） | 入力は BT とアナログのみ | TPA3255 [分解] | BT 5.0 | 手回しポット [分解] | Bass/Treble は 2 連ポット、中点でトーン無効 [分解]。NE5532×4 のうち 2 個が DIP-8 ソケット [分解]。RCA 端子の脇に Omron リレー（用途未確認）[分解] |
| Fosi BT20A MAX（2025 末〜26） | CS4398 [第三者] | TPA3255＋PFFB [公式] | QCC3095（BT 6.0）[公式] | モーター付きポット [公式][分解] | TONE/BYPASS スイッチ、メイン出力の 80 Hz HPF／フルレンジ切替 [公式]。G6K-2P-Y（5 V）×3、スピーカー端子側に HKE HRS3FTH-S-DC24V-A×4 [分解]（どれが何を切るかは [推定]） |
| Fosi MC351（2024–25） | 未記載 | TPA3255×2（2.1ch）[公式] | BT 5.3、USB、光・同軸 [公式] | 未確認 | Bass/Treble の中点デテントで「tone defeating」、VU メータ [公式] |
| Douk Audio ST-01 PRO | 未確認 | TPA3250 [公式] | XU316、BT 5.0 [公式] | 未確認 | Treble/Bass ±6 dB、真空管 4BZ6、NE5532×1 を差し替え可 [公式] |
| 参考: Aiyima A07 MAX（DAC なし） | — | TPA3255 | — | — | NE5532 を DIP-8 ソケットで交換 [第三者] |

### 1.3 ヘッドホン用（据え置き・ドングル・BT）

| 機種（年） | DAC | USB・BT | HPA | 音量 | PEQ・切替 |
|---|---|---|---|---|---|
| Topping DX5 II（2025） | ES9039Q2M×2 [第三者] | XU316、QCC5125 [第三者] | ディスクリートとオペアンプの複合（NFCA 系）[第三者] | 0.5 / 1 dB 刻みを選択、バランス 0.5〜9.5 dB [公式]。DAC 内 [推定] | 10 バンド（プリセット 5＋ユーザー 5）、USB 192 kHz・同軸光 192 kHz・BT 96 kHz まで [公式]。処理は XMOS 上 [推定：別 DSP の記載が無い]。フィルタ F-1〜F-8 は ES9039Q2M の 8 プリセット [公式] |
| Topping DX9 15 周年版（2023 末） | AK4499EQ＋SRC AK4137EQ（刻印を確認）[分解] | XU316、AK4118A、QCC5125、CPLD [第三者] | NFCA モジュール 6 枚 [分解] | 表 1.1 の E | XLR 出力・HP 端子の付近にも G6K 系リレー [分解]（出力切替・ミュート用と [推定]） |
| FiiO K7 / K9 Pro ESS（2021 / 2022） | AK4493S×2 / ES9038PRO×2 [公式] | XUF208。K9 Pro は QCC5124 も [公式] | THX AAA 788+×2 [公式] | ✔ ポットを ADC で読み、NJU72315×2（2 dB 刻み・I²C）で減衰 [公式] | ✔ K9 Pro ESS はゲイン L/M/H [公式]（K7 は 2 段）。EQ は BT 使用時のみ [公式] → QCC5124 の DSP [推定] |
| FiiO K11 R2R（2025） | 自社 R2R（FPGA の後）[公式] | SA9312L、MCU GD32F303RE、BT なし [公式] | SGM8262×2、OPA1642×2 [公式] | エンコーダで NJW1195A（4 ch・0.5 dB・ゼロクロス）を制御 [公式]。ゲイン 3 段それぞれに音量カーブ [公式] | ノブの 2 度押しで PO/PRE/LO を切替、モードごとに音量を記憶 [公式] |
| FiiO K13 R2R（2025） | 自社 R2R、FPGA [公式] | XU316、ESP32-S3、BT 5.4 [公式] | OPA1642×2＋TPA6120A×2 [公式] | NJW1195A [第三者] | 10 バンドを XU316 上で処理、192 kHz まで。有効にすると最大サンプルレートが下がる [公式] |
| FiiO K17（2025） | AK4191＋AK4499EX×2 [公式] | XU316、QCC5125、X2000＋ESP32-S3 [公式] | ディスクリート AB 級（MJE243/253）[公式] | 未確認 | 専用 DSP M21586Q で 31 バンド、DRC・リミッタ・コンプ [公式]。ゲイン 5 段 [公式] |
| FiiO K19（2024） | ES9039SPRO×2（原文のまま）[公式] | XU316、QCC5125、HDMI ARC。「quad-core FPGA」がデジタル入力を担う [公式] | THX AAA 788+ 8 回路 [公式] | 未確認 | ✔ ADSP-21565（SHARC+、800 MHz、64 bit 倍精度浮動小数点）で 31 バンド、+12〜−24 dB、Q 0.4〜128 [公式]。✔ 出力 6 モード（PO+PRE / PO / PRE / LO / 同軸 / 光）[公式]。ゲイン 5 段 [公式] |
| FiiO KA17（2024） | ES9069Q×2 [公式] | XU316 [公式] | THX AAA 78+（オペアンプ 8 個並列）[公式] | 60／120 段を選択、ゲインごとにカーブ [公式]。DAC 内 [推定] | 10 バンド、192 kHz まで、UAC1 では不可、アプリとウェブで設定 [公式]。D.Mode でアンプ電源と出力を切替 [公式] |
| FiiO Q15（2024） | AK4191EQ＋AK4499EX [公式] | XU316、QCC5125 [公式] | 非開示 | 未確認 | 7 プリセット＋3 PEQ、BT は 96 kHz まで [公式]。**ゲインと電源電圧を一緒に切り替える**（最上位は外部給電時だけ）[公式] |
| Qudelix T71（2024） | ES9219×4 [公式] | NXP i.MX RT600（ARM＋DSP）[公式] | TI INA1620×2 [公式] | 1 押し ±0.5 dB。**ゲイン切替時に聴感上の音量を自動で合わせる** [公式] | 20 バンド＝ユーザー 10＋機器補正 10、64 bit。飽和表示で全体ゲインを下げる [公式]。ゲイン切替は数秒かかり途中で音が乱れうる [公式] |
| Qudelix 5K（2020、定番） | ES9219C×2 [公式] | QCC5124（Kalimba DSP）[公式] | ES9219C 内蔵 [公式] | 未確認 | 20 バンド PEQ/GEQ、L/R 独立、本体に保存 [公式] |
| Moondrop Moonriver 2 Ti / Moonriver 3（2023 / 2025） | CS43198×2（2 Ti は [公式]、3 は [第三者]） | 非開示 | 2 ch アンプ IC×2 [公式：2 Ti] | DAC 内（2 Ti は「100-level smooth DAC volume」[公式]） | Moonriver 3 はアプリ・ウェブで PEQ [第三者] |
| xDuoo XD05 Pro（2023–24） | DAC カード交換式 [第三者] | XU316 [第三者] | OPA1612 をソケットで交換（±15 V 対応品）[第三者] | PGA2311 [第三者] | ゲイン 3 段 [第三者] |
| iBasso DC-Elite（2023） | BD34301EKV、FPGA [公式] | 非開示 | デュアルオペアンプ×6 [公式] | 24 段・4 連の段付き [公式] | なし |
| Cayin RU7（2023） | 1 bit 抵抗ネットワーク DAC（PCM は全部 DSD に変換）[公式] | 非開示 | 2 アンプ並列の 4 ch 平衡 [公式] | 表 1.1 の E [公式] | なし |
| Shanling UA7（2025） | ES9069 [第三者] | 非開示 | JAN6418×2 の真空管経路／OPA1662＋BUF634 の半導体経路 [第三者] | 100 段 [第三者] | **真空管／半導体をメニューで選ぶ**。素子は非開示 [第三者] |
| Cayin RU9（2025） | AK4493SEQ×2 [第三者] | 非開示 | Nutube 6P1＋JFET、半導体モードは別のオペアンプ回路 [第三者] | 未確認 | **Classic（負帰還オフ）／Modern（負帰還オン）／Solid-State の 3 モード** [第三者] |

- 低価格の PEQ ドングル: KT Micro KT02H20 系はチップ内で 5 バンド（HID で送り、フラッシュ保存のコマンドもある）[第三者]。Savitech SA9312 系は、ホストが計算した BQ 係数を USB HID で送り、ブリッジが I²C で CS43198 の IIR に書く [第三者]

---

## 2. EQ・エフェクト

### 2.1 処理場所（見つかったものは全部デジタル）

| 処理場所 | 例 | 規模・特徴 |
|---|---|---|
| ストリーマーの SoC | WiiM、Eversolo Play | 入力ごとの 10 バンド GEQ/PEQ、ルーム補正、サブのクロスオーバ・遅延 |
| DSP 内蔵 Class-D | TAS5805M、TAS5825M、ACM8625、TAS5548、STA326 | 4〜15 BQ/ch、多帯域 DRC、音量（§4.1） |
| USB ブリッジのファーム | XMOS XU316（FiiO K13 R2R）、NXP i.MX RT600（Qudelix T71）、KT Micro KT02H20 | 5〜20 バンド。XMOS の lib_audio_dsp は BQ・GEQ・コンプ・リミッタ・リバーブ・ディレイまで持つ [公式] |
| BT SoC の DSP | Qualcomm QCC5124 / QCC5125（Kalimba）、杰理 Jieli AC695N / AC696N、炬芯 Actions ATS2853、Beken BK3266 | Jieli は EQ・DRC に加え、**残響・エコー・変声・カラオケ**を SDK に標準で持つ [公式]（§4.3） |
| 専用 DSP | FiiO K19（ADSP-21565）、K17（M21586Q）、中国製 DSP 基板・車載 DSP（ADAU1701 / ADAU1452） | 31 バンド＋DRC など。ADAU1701 は ADC×2・DAC×4 を内蔵し、アナログ入力を直接受ける [公式] |
| DAC 内蔵のフィルタ | Cirrus CS43198 の書き換え可能な IIR（1 次 1 段＋2 次 3 段、係数は I²C）[公式]、ESS の補間フィルタのプリセット | 製品の「フィルタ選択」の多くは、DAC 内蔵フィルタの選択そのもの |

### 2.2 係数の作り方と送り方

- **係数はメーカーの GUI で作る**: TI PurePath Console（PPC3。TAS5805M 用のアプリは申請制）、ADI SigmaStudio、ACME Audio Tuning、Jieli の EQ tool / EffTool、Actions の ASET、Qualcomm の QACT [公式]。GUI が出すレジスタ書き込み列をファームに埋め込む運用 [推定]
- **ユーザー PEQ の転送は USB HID が主流**（ブラウザからは WebHID）。多くは「種類・周波数・ゲイン・Q」を送って機器側で係数にする。Savitech 系はホストが BQ 係数（96 kHz 固定・Q2.30）を計算して送る [第三者：リバースエンジニアリング]
- **全体ゲイン（クリップ防止）を EQ とは別に持つ**（Topping は Q25 の線形値、FiiO は ±12 dB、Qudelix は飽和表示）[公式][第三者]
- **PEQ にはサンプルレートの上限がある**（USB 192 kHz、BT 96 kHz、UAC1 では不可、K17 は 96 kHz まで SRC なし）[公式]

### 2.3 アナログの名残

- グライコ IC の ROHM BA3812L は生産終了 [第三者]。BA3822LS が現行かは未確認。10 バンドはオペアンプ＋ジャイレータの基板が定番 [第三者]
- エコーは PT2399（ADC/DAC＋RAM。遅延は外付け R で約 31〜342 ms、長くするほど歪む）がカラオケ基板の定番 [公式]
- スペクトラム表示は MSGEQ7（7 バンドのピーク値を多重化した DC で出す）か、TDA7419 に内蔵の 7 バンド出力 [公式]
- アナログ機のトーンは、2 連ポットの中点デテントで無効（Fosi BT20A Pro・MC351）か、TONE/BYPASS スイッチ（BT20A MAX）[公式][分解]

---

## 3. 切替

- **入力**: デジタル処理型は、アナログ入力も ADC に通してから SoC で選ぶ（型 B・C）。電子ボリューム型は NJW1194 の 4 入力セレクタで選ぶ
- **出力・ゲイン・モード**:
  - PO/PRE/LO、SE/BAL はメニューで排他に選び、モードごとに音量を記憶する（FiiO K11/K13 R2R）[公式]
  - ゲインは 2〜5 段。FiiO Q15 はゲインと電源電圧を一緒に、Qudelix T71 は切替時に音量を自動で合わせる [公式]
  - 「デスクトップモード」は外部給電で電源電圧を上げ、アンプを並列にする（FiiO BTR17・KA17）[公式]
- **アンプ経路**: 真空管／半導体の切替が 2025 年のドングルで増えている（Shanling UA7、Cayin RU9 は負帰還のオン/オフも）[第三者]。切替素子は非開示
- **オペアンプ**:
  - 交換はどれも DIP-8 ソケットで、メーカーが互換品の一覧を出す形（Fosi BT20A Pro の互換品は LME49720HA / MUSES02 / OPA2134PA / LM4562 / NJM4556AD など [第三者]）
  - **電子的に切り替える製品は、中国ブランドの範囲では見つからなかった。** 共立電子 KP-HAMP61 は選ばないオペアンプを電源ごと切り離し、切替中は約 1 秒音声を GND に落とす（[DEC §2-10] の参考製品、[../datasheets/reference/Kyohritsu_KP-HAMP61_manual.pdf](../datasheets/reference/Kyohritsu_KP-HAMP61_manual.pdf)）
- **素子（写真で確認できたもの）**: 信号リレーの Omron G6K-2P-Y を、Topping DX5 II（HP 端子の横×3）、Topping A90D（入力端子の真後ろに一列）、Topping DX9（音量）、Fosi BT20A MAX（×3）で確認 [分解]。スピーカー端子側は HKE HRS3FTH（BT20A MAX）[分解]。リレーかアナログスイッチかは、ほとんどの機種で非開示

---

## 4. 部品側の表

### 4.1 DSP 内蔵 Class-D（I²S 入力）

| 品番 | メーカー（国） | 音量 | EQ・DRC・効果 | 係数 | 採用例 |
|---|---|---|---|---|---|
| TAS5805M | TI（米） | +24〜−103 dB / 0.5 dB、ランプ付きソフトミュート [公式] | 15 BQ/ch＋サブ用 5 BQ、3 帯域 DRC＋AGL、空間化 [公式] | PPC3（申請制） | Amazon Echo Pop [第三者：分解記事] |
| TAS5825M | TI | 同上 [公式] | 2×15 BQ、3 帯域 DRC＋AGL、Dynamic EQ、バス強調、スピーカー保護 [公式] | PPC3 | 未確認 |
| TAS3251 | TI | — | 最大 15 BQ/ch＋クロスオーバ、3 帯域 DRC＋AGL、SmartBass、SRC [公式] | PurePath Console | 未確認 |
| MA12070P / MA12040P | Infineon（独） | +24〜−144 dB / 0.25 dB、スムージング付き [公式] | **リミッタだけ。BQ（EQ）は無い** [公式：70P の DS V1.0。40P は同系列と推定] | — | RPi 用 HAT [公式] |
| STA350BW / STA333BW | ST（欧） | +42〜−80 dB（350BW）[公式：抜粋] | 8 BQ/ch・2 帯域 DRC（350BW）、5 BQ/ch（333BW）[公式：抜粋] | — | 未確認 |
| **ACM8625P/S/M** | **苏州至盛半导体（ACME Semiconductor、中国）** | −110〜+24 dB [公式] | 前段 2×15 BQ＋後段 2×5 BQ、3 帯域 DRC（遅延バッファ付き）[公式] | ACME Audio Tuning [公式] | 販売店が「TAS5805 / TAS5825 を置換」と宣伝 [第三者] |
| AW88394 / AW88298 | Awinic（上海） | — | PEQ・多帯域 DRC・アンチクリップ・スピーカー保護（394）[公式：抜粋] | SKTune | M5Stack CoreS3（AW88298）[第三者] |
| （参考）MA5332MS | Infineon | — | **アナログ入力で DSP 無し** [第三者] | — | SMSL AO300 / AO200 MKII |

- デジタル入力のアンプなら音量・EQ・DRC は「I²C で書く係数 1 組」で済む。代わりに、アナログ入力には ADC が要る [推定]

### 4.2 音量・トーン IC

**PT23xx の位置づけ**（Princeton Technology、台湾）
- ST の TDA731x と同じ骨格の CMOS の廉価系。PT2313L は DS に「TDA7313 とピン互換」と明記 [公式]。I²C 0x88、音量 1.25 dB 刻み、トーン ±14 dB / 2 dB、トーンの周波数は外付け部品で決まる
- ✔ PT2314E の DS の用途欄は薄型 TV・ホームオーディオ・パワードスピーカー [PT2314E p1]
- 現行の同系は PT2312E / PT2313E / PT2314E / PT2315E（入出力数違い）、高性能版の PT2033、車載の PT12916 系（Q・周波数をプログラム可）[公式]。PT2313L・PT2322・PT2323 は Princeton の現行ページに無い（旧製品と [推定]）
- 中国の互換品に 天微 TM2314 / TM2313 がある [第三者]

| 品番 | メーカー（国） | 中身 | ゼロクロス／ポップ対策 | 電源 | 採用例 |
|---|---|---|---|---|---|
| PT2314E | Princeton（台湾） | 4 入力セレクタ＋入力ゲイン、マスター音量 0〜−78.75 dB / 1.25 dB、スピーカー ATT（ミュート付き）、ラウドネス、Bass/Treble ±14 dB / 2 dB（周波数は外付け）[PT2314E p1–2, p8–9] | **記載なし**。DC 段差は入力ゲイン 3〜10 mV、ATT 0 dB→ミュート 5〜10 mV [sw] | 単電源 4〜10 V（EC 表の min は 5 V。DS 内で食い違う）、最大入出力 2.3 Vrms（min）[sw] | AudioV2.1 |
| NJW1194 | 日清紡（日） | 4 入力セレクタ、音量 +31.5〜−95 dB / 0.5 dB、トーン 0〜±10 dB / 1 dB、3 線シリアル、THD 0.0015 % [公式 ✔] | ゼロクロス検出 [公式 ✔] | ±4.5〜±7.5 V [公式 ✔] | SMSL AO200 MKII / AO300、Loxjie A30 / A40 |
| NJW1195A | 日清紡 | 4 ch の抵抗ラダー音量 +31.5〜−95 dB / 0.5 dB、4 入力 2 出力セレクタ [公式] | ゼロクロス検出 [公式] | 未確認 | FiiO K11 R2R |
| NJU72315 | 日清紡 | 2 ch、0〜−62 dB / 2 dB、I²C [公式] | 未確認 | 未確認 | FiiO K7 / K9 Pro |
| NJU72343 | 日清紡 | 8 ch、+31.5〜−95 dB / 0.5 dB、2 線 [公式] | ゼロクロス [公式] | ±4.5〜±7.5 V または +9〜+15 V [公式] | 未確認 |
| MUSES72320 | 日清紡 | 0〜−111.5 dB / 0.25 dB（＋31.5 dB の利得）、出力は外付けオペアンプ、3 線 [公式] | ゼロクロス [公式] | ±8.5〜±18 V [公式] | リモコン付きプリ基板 [第三者] |
| MUSES72323 | 日清紡 | 0〜−111.75 dB / 0.25 dB、＋21 dB / 3 dB [公式] | ソフトステップ＋ゼロクロス [公式] | ±10〜±18 V [公式] | 未確認 |
| PGA2311 / PGA2320 | TI（米） | +31.5〜−95.5 dB / 0.5 dB。PGA2320 は ±15 V 級で PGA2310 とピン互換 [公式] | ゼロクロス [公式] | ±5 V / ±15 V 級 | xDuoo XD05 Pro（PGA2311）[第三者] |
| CS3318 | Cirrus（米） | 8 ch、−96〜+22 dB / 0.25 dB、I²C/SPI [公式] | ゼロクロス（タイムアウト付き）[公式] | ±8〜±9 V [公式] | 未確認 |
| TDA7439 | ST（欧） | 4 入力、Bass/Mid/Treble ±14 dB / 2 dB（中心周波数・Q は外付け）、音量 0〜−47 dB [公式]。DigiKey で Obsolete [第三者] | ゼロクロスなし（DC 段差の低減をうたう）[公式] | 6〜10.2 V [公式] | DIY が主 |
| TDA7419 | ST | 車載。**Bass/Mid/Treble の周波数と Q を I²C で選べる**（±15 dB / 1 dB）、7 バンドのスペアナ出力 [公式] | ソフトステップ音量・ソフトミュート [公式] | 7.5〜10.5 V [公式] | 未確認 |
| BD37534FV / BD37033FV-M | ROHM（日） | 車載 3 バンド EQ。周波数・Q・ゲインを I²C で（534 は ±20 dB / 1 dB）[公式] | 切替ノイズ低減（Advanced switch）[公式] | 7.0〜9.5 V [公式] | 未確認 |
| M62429 | Renesas（日） | 2 ch、0〜−83 dB / 1 dB、独自 2 線 [公式] | 未確認 | 4.5〜5.5 V [公式] | 未確認 |
| PT2257 / PT2259 / PT2258 | Princeton | 2 ch / 2 ch / 6 ch の電子ボリューム、1 dB 刻み [公式] | 記載なし | 3〜10 V / 4〜10 V / 5〜10 V [公式] | 5.1ch リモコンキット（PT2258）[第三者] |
| リレー式抵抗ラダー | — | 6 リレーで 64 段・1 dB、256 段など [第三者] | 構造上クリックなし [第三者] | — | Khozmo、Benchmark ほか |

### 4.3 BT・USB・SoC 内蔵の DSP

| 品番 | メーカー（国） | EQ・エフェクト | 調整ツール |
|---|---|---|---|
| AC695N / AC696N | 杰理 Jieli（中国） | EQ、DRC、残響、エコー、変声、仮想低音、カラオケ（マイク・残響・伴奏）[公式] | EQ tool / EffTool、「杰理之家」アプリ SDK [公式] |
| ATS2853 | 炬芯 Actions（中国） | CPU＋DSP、PEQ 14 段、リミッタ、2 帯域 DRC [第三者] | ASET [第三者] |
| BK3266 | Beken（中国） | ハードウェア 5 バンド EQ [公式] | 未確認 |
| BES2700ZP | 恒玄 Bestechnic（中国） | Cortex-M55＋HiFi4 DSP（オプション）＋NPU [公式：抜粋] | 未確認 |
| QCC5125 / QCC5181 | Qualcomm（米） | Kalimba DSP 2 コア、User EQ / Speaker EQ（最大 10 段）[公式][第三者] | QACT [公式] |
| KT0231H / KT02H22 | 昆腾微 KT Micro（北京） | EQ・ノイズゲート（02H22 は DRC も）[公式] | — |
| CX31993 | Synaptics（旧 Conexant、米） | EQ・音量 [第三者] | — |
| ALC5686 | Realtek（台湾） | 12 バンド EQ [第三者] | — |
| CT7601 | Comtrue（台湾） | USB→I²S ブリッジ。音量＋フェード、de-pop。EQ の記載なし [公式：抜粋] | — |
| XU316 | XMOS（英） | ソフトの DSP（BQ・FIR・GEQ・コンプ・リミッタ・リバーブ・ディレイ）[公式] | Pipeline Designer [公式] |
| ADAU1701 / ADAU1452 / ADAU1466 | ADI（米） | 単体 DSP。1701 は ADC×2・DAC×4 内蔵で EEPROM から自己ブート [公式：抜粋] | SigmaStudio。Wondom（Sure）JAB4 / JAB5 は 1701 [公式] |

### 4.4 切替・保護

| 品番 | 中身 |
|---|---|
| CD4052B（TI） | ✔ THD 0.3 % / 0.2 % / 0.12 %（電源 5 / 10 / 15 V、1 kHz）[公式]。Hi-Fi には粗い |
| CD74HC4052（TI） | アナログは ±5 V まで、THD 0.01〜0.03 % [公式] |
| TPW4052 / RS2252 | 3PEAK / Runic（中国）の 4052 ピン互換品 [第三者] |
| Omron G6K-2P-Y | SMD の DPDT 信号リレー（ラッチ品もある）[公式]。製品の写真で最も多く見た |
| Hongfa HFD4 / HFD2（中国） | 信号リレー。AgNi＋Au / Ag＋Au 接点 [公式] |
| uPC1237 | スピーカー保護（遅延 ON、DC 検出、AC 断検出）。台湾 UTC が製造を続けている [公式] |
| 2SC2878（東芝） | ミュート用トランジスタ（逆方向 hFE 150 typ、Ron 1 Ω typ）[公式] |
| S/PDIF 受信・SRC | CS8416 / CS8422（ASRC 内蔵）/ WM8805 / AK4118A（量産中）/ DIR9001 [公式]。AK4137 は NRND [公式] |

---

## 5. PT2314E について DS から分かったこと（2026-09-25 の図と照らして）

### 5.1 事実

- ✔ ピン表で `LIN`/`RIN` は "volume controller input"、`LOUT`/`ROUT` は "Input selector output" [PT2314E p4]
- ✔ ブロック図の経路は `LIN` → ラウドネスの切替（"Loud SW"）→ マスター音量 → Bass → Treble → スピーカー ATT（"Speaker Attenuator With Mute"）→ `OUT`。入力セレクタとゲインは `LOUT` へ出る別の枝 [PT2314E p2、画像で確認]
- ✔ 2026-09-25 の図では、入力は `PT_LIN`/`PT_RIN` に入り、`LOUT`/`ROUT` と `LOUD_L`/`LOUD_R` は未接続 [NL]
- ⇒ **インサートで飛ばしているのは入力セレクタと入力ゲインだけで、マスター音量・ラウドネスの切替・スピーカー ATT は経路に残る**〔DS と図から〕
  - [../PARTS.md](../PARTS.md) の生成ブロック（入力端子と PT2314E の行）の「セレクタとボリューム段は…飛ばしている」、[../firmware/tone.py](../firmware/tone.py) の「音量は手回しポットなので触らない」は、これと食い違う
- ✔ 電源を入れるたびに内部レジスタをリセットし、その間は I²C アクセス禁止（推奨 Td 50 ms）[PT2314E p7][sw]。**リセット後のレジスタ値は DS のどこにも書かれていない**（p7〜9 のレジスタ表にも既定値の欄が無い）
- ✔ コード [PT2314E p8–9]:
  - マスター音量 0 dB = `0x00`
  - スピーカー ATT L / R の 0 dB = `0xC0` / `0xE0`
  - Audio switch = `010 G1 G0 LD S1 S0`（`LD=1` でラウドネス OFF、`G1 G0 = 11` で入力ゲイン 0 dB）
  - Bass = `0110 xxxx`、Treble = `0111 xxxx`。`0111` と `1111` がどちらも 0 dB、負側は `0000`=−14 … `0110`=−2、正側は `1110`=+2 … `1000`=+14
- ゼロクロス・ソフトステップの記載は無い。DC 段差は入力ゲイン 3〜10 mV、ATT 0 dB→ミュート 5〜10 mV [sw]

### 5.2 v2.1 に効くところ〔推論〕

- [DEC §10-1] の「確かめる事実: PT2314E の POR 直後の音量状態」は、DS からは決まらない（既定値の記載が無い）。実測で確かめるか、決め打ちで起動時に全レジスタを書くか
- 書くなら、50 ms 待ってから、マスター音量 0 dB・ATT L/R 0 dB・ラウドネス OFF（外付け網が無い）・入力ゲイン 0 dB・Bass/Treble を書く。[DEC §6-2] の「電源投入時」は今は「50 ms は I²C を送らない」だけ
- Pico は USB だけで動き、主電源 OFF でも生きている（[DEC §5-7]）。主電源の入れ直しで PT2314E だけがリセットされるので、±15 V の検知（§5-7）の立ち上がりで初期化し直すのが自然
- 耳で比べている最中にトーンを動かすと、ゼロクロスが無いのでクリックが出うる。同じ位置の現行製品は NJW1194（ゼロクロス付き、ただし ±7.5 V まで）

---

## 6. v2.1 の未決への材料（判断はしない）

| ID | 製品・部品の側で見えたこと |
|---|---|
| V21-未決-01 ミュート | 出力付近の信号リレー（Topping DX9・A90D の G6K 系。用途は [推定]）[分解]。ライン出力のミュート用トランジスタ 2SC2878（Ron 1 Ω typ）[公式]。ES9039Q2M はミュート時に出力を GND へ落とす機能を持つが、DAC の中の話 [公式]。PT2314E の ATT ミュートは `AMP_SEL` の上流にあるので、切替の過渡は消せない（[DEC §2-10] の理由と同じ） |
| V21-未決-14 DIRECT | Fosi BT20A MAX は TONE/BYPASS スイッチ＋G6K-2P-Y×3（どれがバイパスかは [推定]）。Fosi BT20A Pro・MC351 はトーンの中点デテント（経路は通したまま）。SMSL AO300 の「Direct」は EQ モードの 1 つ（IC の中でフラットにしているのか、物理的に飛ばしているのかは未確認）。WiiM Vibelink Amp は RCA 入力が DAC を通らないアナログ経路 [公式] |
| [DEC §10-1] PT2314E の POR 直後 | §5 |
| V21-継-05 トーンは PT2314E | 同じ位置の現行製品は NJW1194。周波数・Q も動かすなら TDA7419 / BD37534FV（9 V 前後の単電源、ソフトステップ系）。±15 V 級で音量だけなら MUSES72323 / PGA2320（§4.2） |
| 切替素子（参考） | 製品の信号リレーは G6K-2P-Y が定番。安い半導体 MUX は THD が悪い（CD4052B は 0.12〜0.3 %）。±15 V で低歪なら高電圧の MUX（TMUX7612 級）か信号リレー |

配線の側の材料（V21-未決-11・15・19・22 など）は [product_board_layout.md](product_board_layout.md) §3。

---

## 出典

### 製品（スピーカー用）
- WiiM Amp / Amp Pro: https://faq.wiimhome.com/en/support/solutions/articles/72000616467-technical-specification-of-the-wiim-amp-and-wiim-amp-pro ／ https://www.wiimhome.com/langPdf/en/WiiM%20Amp%20UM.pdf ／ https://wiimhome.com/langPdf/en/WiiM%20Amp%20Pro%20UM.pdf ／ https://forum.wiimhome.com/threads/what-adc-for-wiim-amp.2544/ ／ https://audioxpress.com/article/fresh-from-the-bench-wiim-amp-integrated-amplifier-and-multiroom-audio-streamer
- WiiM Amp Ultra: https://blog.wiimhome.com/post/wiim-amp-ultra-performance-meets-precision ／ https://www.soundstageaccess.com/index.php/equipment-reviews/1358-wiim-amp-ultra-streaming-integrated-amplifier
- WiiM Vibelink Amp: https://www.wiimhome.com/wiimvibelink/overview ／ https://blog.wiimhome.com/post/wiim-talks-vibelink-amp-continued
- Eversolo Play: https://headfonics.com/eversolo-play-review/ ／ https://www.stereonet.com/reviews/eversolo-play-streaming-amplifier-review ／ https://www.headfonia.com/eversolo-play-review/
- Arylic: https://forum.arylic.com/t/a50-chipset/1814 ／ https://www.arylic.com/pages/benchmark-1 ／ https://audioxpress.com/article/fresh-from-the-bench-arylic-audio-up2stream-amp-v4 ／ https://forum.arylic.com/t/up2stream-amp-v4-used-dac-and-dac-quality/3593
- Fosi BT20A Pro: https://pcper.com/2023/04/rehearsals-refined-the-fosi-audio-bt20a-pro-amplifier/（内部写真 https://pcper.com/wp-content/uploads/2023/04/internals-1.png）
- Fosi BT20A MAX: https://fosiaudio.com/pages/bt20a-max-bluetooth-stereo-power-amp（内部写真・電源図は同ページの画像）／ https://headfonics.com/fosi-audio-bt20a-max-review/2/ ／ https://www.soundphilereview.com/reviews/fosi-audio-bt20a-max-review-51911/
- Fosi MC351: https://fosiaudio.com/products/fosi-audio-mc351-2-1-channel-integrated-amplifier-with-vu-meter
- Fosi（オペアンプ交換）: https://community.fosiaudio.com/threads/op-amp-rolling-rollup.26111/
- SMSL: AO300 PRO https://www.smsl-audio.com/portal/product/detail/id/931.html ／ AO300 マニュアル https://manuals.plus/smsl/ma5332ms-ao300-all-in-one-dac-and-amplifier-manual ／ AO200 MKII https://www.smsl-audio.com/portal/product/detail/id/840.html ／ A300 https://www.smsl-audio.com/portal/product/detail/id/792.html ／ SA300 http://archimago.blogspot.com/2020/11/measurements-smsl-sa300-infineon-merus.html
- Loxjie: A30 http://www.loxjie-audio.com/newsview.asp?id=70 ／ https://www.audiophonics.fr/en/integrated-amplifiers/loxjie-a30-class-d-amplifier-infineon-ma12070-bluetooth-50-2x50w-4-ohm-p-14817.html ／ A40 https://www.audiophonics.fr/en/integrated-amplifiers/loxjie-A40-p-18780.html
- Topping MX3s: https://www.topping.store/products/topping-mx3s-headphone-amplifier-dac ／ https://hifigo.com/products/topping-mx3s
- Aiyima: D03 https://www.aiyima.com/products/aiyima-d03-hifi-bluetooth-5-0-audio-amplifier-2-1-wireless-digital-sound-power-subwoofer-amplificador-usb-dac-stereo-audio150wx2 ／ T9 Pro https://www.aiyima.com/products/aiyima-t9-pro ／ A07 MAX https://www.audiophonics.fr/en/integrated-amplifiers/aiyima-a07-max-stereo-mono-class-d-amplifier-tpa3255-2x225w-4-ohm-1x450w-4-ohm-p-18403.html
- FX-Audio D802C PRO: https://szfxaudio.com/ProductDetail/4596634.html
- Douk Audio ST-01 PRO: https://doukaudio.com/products/douk-audio-st-01-hifi-bluetooth-5-0-tube-amplifier-usb-dac-coax-opt-digital-audio-amp-w-vu-meter

### 製品（ヘッドホン用）
- Topping DX5 II: https://cdn.shopify.com/s/files/1/0153/8863/files/Headphone-zone-Topping-dx5II-user-manual.pdf ／ https://headfonics.com/topping-dx5-ii-review/ ／ HID の記録 https://github.com/gjcourt/toppingctl ・ https://github.com/gjcourt/lab/blob/main/01-audio-midi/_reference/topping-dx5ii-hid-protocol.md
- Topping DX9 15 周年版: http://archimago.blogspot.com/2025/04/part-i-topping-dx9-15th-anniversary.html ／ 分解 https://www.audiosciencereview.com/forum/index.php?threads/topping-dx9-teardown.54777/
- FiiO: K7 https://www.fiio.com/k7 ・ https://www.fiio.com/k7_parameters ／ K9 Pro ESS https://www.fiio.com/k9proess ・ https://www.fiio.com/k9proess_parameters ／ K11 R2R https://www.fiio.com/k11r2r ・ https://www.fiio.com/k11r2r_parameters ／ K13 R2R https://www.fiio.com/k13r2r ・ https://www.fiio.com/k13r2r_parameters ・ https://www.headfonia.com/fiio-k13-r2r-review/ ／ K17 https://www.fiio.com/k17 ・ https://www.fiio.com/k17_parameters ／ K19 https://www.fiio.com/k19 ・ https://www.fiio.com/k19_parameters ・ https://headfonics.com/fiio-k19-review/ ／ KA17 https://www.fiio.com/ka17 ／ BTR17 https://www.fiio.com/btr17 ／ Q15 https://www.fiio.com/q15 ・ https://www.fiio.com/q15_parameters ／ PEQ の説明 https://fiio-file.fiio.net/70%E4%B8%8A%E4%BC%A0%E7%9A%84%E6%96%87%E4%BB%B6/PEQ%20Settings%20Instructions%20for%20FiiO%20Portable%20DAC&AMP.pdf
- Qudelix: T71 https://support-qudelix.github.io/Qudelix_T71_User_Manual.pdf ／ 5K https://www.qudelix.com/products/qudelix-5k
- Moondrop: https://moondroplab.com/en/products/moonriver2-ti ／ https://hifigo.com/products/moondrop-moonriver-3 ／ https://headfonics.com/moondrop-dawn-pro-review/
- HiBy FC6 https://headfonics.com/hiby-fc6-review/ ／ iBasso DC-Elite https://ibassousa.com/ibasso-dc-elite/ ／ DC07PRO https://ibassousa.com/ibasso-dc07pro/ ・ https://www.headfonia.com/ibasso-dc07pro-review/
- Shanling UA4 https://en.shanling.com/article-IntroUA4.html ／ UA7 https://headfonics.com/shanling-ua7-review/
- Cayin RU7 https://en.cayin.cn/features/7/124/603.html ／ RU9 https://headfonics.com/cayin-ru9-review/
- xDuoo XD05 Pro https://headfonics.com/xduoo-xd05-pro-review/ ／ SMSL DO400 https://www.smsl-audio.com/portal/product/detail/id/843.html
- 低価格 PEQ ドングル（リバースエンジニアリング）: https://github.com/ParkWardRR/fiio-ja11-jcally-jm12-moondropkt02-kt02h20-dac-amp-control ／ https://github.com/eyad-elghareeb/kt0231h ／ https://github.com/erikyo/JM98MAX-PEQ ／ https://github.com/jeromeof/devicePEQ

### 部品
- DAC: ES9039Q2M https://www.esstech.com/wp-content/uploads/2026/05/ES9039Q2M_Datasheet_v0.2.3.pdf ／ CS43198 https://statics.cirrus.com/pubs/proDatasheet/CS43198_DS1156F2.pdf
- DSP 内蔵 Class-D: TAS5805M https://www.ti.com/lit/ds/symlink/tas5805m.pdf ／ TAS5825M https://www.ti.com/lit/ds/symlink/tas5825m.pdf ／ TAS3251 https://www.ti.com/lit/ds/symlink/tas3251.pdf ／ TAS5548 https://www.ti.com/product/TAS5548 ／ MA12070P https://www.infineon.com/part/MA12070P ／ STA350BW https://www.st.com/resource/en/datasheet/sta350bw.pdf ／ STA326 https://www.st.com/en/audio-ics/sta326.html ／ ACM8625 https://www.acme-semi.com/productinfo/1165763.html ／ AW88394 https://www.awinic.com/en/productDetail/AW88394CSR ／ Echo Pop の分解 https://www.briandorey.com/post/echo-pop-smart-speaker-teardown
- 音量・トーン: NJW1194 https://www.nisshinbo-microdevices.co.jp/en/products/audio-signal-processing/spec/?product=njw1194 ／ NJU72315 https://www.nisshinbo-microdevices.co.jp/en/products/audio-signal-processing/spec/?product=nju72315 ／ NJW1195A https://www.mouser.com/datasheet/2/294/NJW1195A_E-259014.pdf ／ NJU72343 https://www.nisshinbo-microdevices.co.jp/en/pdf/datasheet/NJU72343_E.pdf ／ MUSES72320 https://www.nisshinbo-microdevices.co.jp/en/pdf/datasheet/MUSES72320_E.pdf ／ MUSES72323 https://www.nisshinbo-microdevices.co.jp/en/pdf/datasheet/MUSES72323_E.pdf ／ PGA2311 https://www.ti.com/lit/ds/symlink/pga2311.pdf ／ PGA2320 https://www.ti.com/lit/ds/symlink/pga2320.pdf ／ CS3318 https://statics.cirrus.com/pubs/proDatasheet/CS3318_F2.pdf ／ TDA7439 https://datasheet.octopart.com/TDA7439-STMicroelectronics-datasheet-156305.pdf ／ TDA7419 https://datasheet.octopart.com/TDA7419TR-STMicroelectronics-datasheet-12536769.pdf ／ BD37534FV https://fscdn.rohm.com/en/products/databook/datasheet/ic/audio_video/audio_processor/bd37534fv-e.pdf ／ M62429 https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/5772/M62429P_FP.pdf ／ Princeton の現行品 https://www.princeton.com.tw/en-us/Products/Multi-Media-Audio/Analog-Audio-Processor-for-Home-Audio ・ https://www.princeton.com.tw/en-us/Products/Multi-Media-Audio/Electronic-Volume-Controller ／ PT2313L https://www.nikom.biz/pdf/PT2313L_PTC.pdf ／ PT2399 https://www.nikom.biz/pdf/PT2399_PTC.pdf ／ TM2313 https://www.lcsc.com/product-detail/Audio-Interface-ICs_TM-Shenzhen-Titan-Micro-Elec-TM2313_C88429.html ／ リレー式ラダー https://khozmo.com/product/64-steps-ladder-type-attenuator-with-remote-relay-based/ ・ https://benchmarkmedia.com/blogs/application_notes/benchmarks-256-step-relay-controlled-attenuator
- BT・USB・SoC・DSP: Jieli https://doc.zh-jieli.com/Apps/iOS/jielihome/zh-cn/master/Development/function.html ／ BK3266 https://www.bekencorp.com/en/goods/detail/cid/27.html ／ BES2700 https://www.bestechnic.com/article/24/42.html ／ ATS2853 https://www.dasenic.com/solutions/consumer_electronics/ats2853 ／ QCC5100 https://www.qualcomm.com/content/dam/qcomm-martech/dm-assets/documents/Qualcomm-QCC5100-Series-Bluetooth-Audio-SoCs.pdf ／ QACT https://www.qualcomm.com/developer/software/qualcomm-audio-calibration-tool ／ KT Micro https://www.ktmicro.com/?usb_104/566.html ／ CT7601 https://www.comtrue-inc.com/doku.php?id=ct7601 ／ XMOS lib_audio_dsp https://github.com/xmos/lib_audio_dsp ／ ADAU1701 https://www.analog.com/en/products/adau1701.html ／ Wondom JAB https://store.sure-electronics.com/product/AA-AP23122
- アナログ: MSGEQ7 https://mix-sig.com/images/datasheets/MSGEQ7.pdf
- 切替・保護: CD4052B https://www.ti.com/lit/ds/symlink/cd4052b.pdf ／ CD74HC4052 https://www.ti.com/lit/ds/symlink/cd74hc4052.pdf ／ G6K https://components.omron.com/us-en/products/relays/G6K ／ HFD4 https://www.hongfa.com/product/signal-relay/HFD4 ／ uPC1237（UTC）https://www.unisonic.com.tw/uploadfiles/836/part_no_pdf/UPC1237.pdf ／ 2SC2878 https://www.edn.com/muting-transistor-attenuator-circuits-2sc2878/ ／ AK4118A https://www.akm.com/global/en/products/audio/ak4118aeq/ ／ AK4137 https://www.akm.com/global/en/products/audio/ak4137eq/
- v2.1 の中の DS: [../datasheets/Princeton_PT2314E.pdf](../datasheets/Princeton_PT2314E.pdf)（p1・p2・p4・p7〜9）

### 取れなかったもの
- Hi-Fi News（WiiM Amp の測定記事）と Stereophile（Eversolo Play）は 403
- ST・ADI・Cirrus のサイトはボット遮断で本体を取れず、検索結果の抜粋だけのものがある（STA350BW / STA333BW / STA326 / ADAU1701 など。「抜粋」と書いた）
- NJW1195 のメーカー DS の URL は 404（NJW1195A は Mouser の写しで読んだ）
