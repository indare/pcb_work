# AudioV2.1 — いま（現況）

**更新:** 2026-09-25  
v2.1 は 2026-09-25 に v2 の図・PCB・スクリプトを全部写して始めた。**回路図と PCB はまだ写したときのまま**（下の「図と PCB の現況」はその状態）。
v2.1 の決まりごと・検証の期待値は [CLAUDE.md](CLAUDE.md)。`kicad-run.sh erc` の既定は v2 なので、v2.1 は `kicad-run.sh erc AudioV2.1/AudioV2Case.kicad_sch` と明示する。

**v2.1 の決定（2026-09-25・未実装）** — 一覧・理由・状態（決定／いったんの決め／未決）の正は [DECISIONS.md](DECISIONS.md)。ここは要旨だけ:
- **根本**: 選んだ 1 ch だけ電源と入力を生かす（コールドスタンバイ、同時に生かすのは厳密に 1 ch）。娘は 1 種類・1 枚 4 ch・縦積み — DECISIONS §1
- **制御の木**: 1 段目＝各娘の電源用ラッチングリレー（±15 V を DPDT 1 個、22 Ω ヒューズ抵抗を NO 側）→ レール良好 → 音声用ラッチングリレー（DPDT 2 個）。2 段目＝娘の中は TMUX7612 で ch を選び、選んだ ch の石だけ ch ごとの LDO（±12 V）の EN で給電。EN は娘の切られたレールから作る。音声 SET は全段共通 1 本（全リセットから始まる一続きの手順の中でだけ出す）。スタックのコネクタは 2×12 — §2
- **電源**: DC-DC は `RS6-1215D`（入手できれば）、PD は 12 V 固定、娘のバルクは外す、コイルの 5 V は L7805C。足場（DNP／0 Ω）: HP バッファ電源の RC、PD 入口の CMC、−15 V のプリロード — §3
- **ADC**: タップは今の位置、結合は差動（Q2。Q1 へ戻せる足場）、ADC の LDO は PD 12 V から取りグランドの木を付け替える — §4
- **監視とファーム**: レールは Pico が共通の `MON_P`/`MON_N` で読み `RAIL_OK` を直接出す。精度の要らない後ろ盾 B1/B2。ファームの責務は §6 — §5・§6
- **v2 から引き継いだもの**は DECISIONS §7（`V21-継-01`〜`31`。どれも v2.1 で再考していない）
- **未決・要実測**は DECISIONS §10（`V21-未決-nn`・`V21-実測-nn`）。基板を起こす前に要る実測は RS6 の突入と OLP の形（V21-実測-01）

**2026-09-25**: 未決 16 項目をいったんの決めにしたあと、設計全体を評価した（統合リスト [review/design_eval_review.md](review/design_eval_review.md) §0）。
A2〜A6 はユーザーが受け、DECISIONS に入れた（電源の検知は `PD_12V_SW`＋規則①②③ §5-7、SET/RESET の排他 §5-8、コイル側の論理を `+5V_COIL` で §2-15、`MON` の形と `PG_N` §5-2）。同じ娘の中の ch 替えも毎回全リセットから回す（統合リスト B7 の (B)、§6-2）ので、切替の無音は全リセットの中で作り、ポットの前の GND 落としは切替に使わない（§2-10。電源断のためだけに置くかは未決）。
**査読中**: A1（親の制御線の出どころ。親の MCP23017 か Pico 2 個か、V21-未決-26、[review/a1_two_pico.md](review/a1_two_pico.md)）と DIRECT の迂回の切替（V21-未決-14、[review/direct_bypass.md](review/direct_bypass.md)）— どちらも評価は済み、否定側の査読待ち。
**残る未決**: -20（縦積みの DIP の手の届き、模型）、後回しの -06・-12・-15・-18・-19・-21。B 項目は実装しながら、C 項目は先に測る（統合リスト §3）。
**次にやること**: A1・DIRECT が決まったら、生成スクリプトと回路図へ入れる（娘: 電源用・音声用リレー、ch ごとの電源ゲート一式と入力の切り替え、デコーダ、B1/B2、排他ゲート。親: RS6、ADC の電源とグランドの付け替え、`TONE` のプルダウン、L7805C、`PD_12V_SW` の検知）。
`scripts/` は v2 からの写しで、v2.1 用に新しく書き起こす予定（[CLAUDE.md](CLAUDE.md)）。
**議論中**: Cf の足場、高速娘の網、バイアス（V21-未決-18。材料は [review/opamp_fast_ds_review_v1.md](review/opamp_fast_ds_review_v1.md)）。
ついでに直すもの: ルートの PT2314E まわりの 2.2 µF フィルムの FP が細い W2.5 のまま（`review/decisions_audit_3_review.md` 覆した点 4）
道具: `scripts/rail_budget.py`（±15 V の負荷の積み上げ。`--adc-from-pd`）。根拠データ: `ds_facts/`（照合済み）、査読: `review/`（読み方は [review/README.md](review/README.md)）

## 装置（忘れないこと）

オペアンプを電子的に切り替えて音の差を楽しむ箱。**計測器ではない。**
切替素子の優劣は耳で決める。挿す石の一覧は [OPAMP_STOCK.md](OPAMP_STOCK.md)。

## UI（表示）

- **操作**: ENC×3 / DEST SW / ポット（DECISIONS `V21-継-01`〜`04`）
- **状態表示（CH / DEST / Bass / Treble）は Waveshare LCD**。OLED は図・PCB に無い
- **ファーム置き場:** [`firmware/`](firmware/)（骨格。v2 の形のまま。v2.1 のファームの責務は DECISIONS §6）

## 図と PCB の現況（v2 から写した状態）

**図**
- 階層: `AudioV2Case` → {`MeasureControl`, `FrontPanel`, `AmpBankSwitch`, `AmpBankRelay`}。箱外 I/O はルート上のコネクタで閉じる。
  `FrontPanel` は母板直下（操作系＝ENC/RV/SW/表示）、Pico／計測は `MeasureControl`
- 所有権と禁止事項: [CLAUDE.md](CLAUDE.md)。**ルートは手編集所有**、娘は `build_daughter.py` が回路の正（全面再生成しない、ピンポイントで差し込む）
- 娘は **2 版（Switch / Relay）のまま**、どちらも MCP23017 とジャンパ 6 段の番地（UI の MCP は 0x22、娘は 0x20/0x21/0x23〜0x26）。
  v2.1 では娘は 1 種類で、MCP・I²C・番地ジャンパは外す（DECISIONS §2-12）
- **電源**: DC-DC は `REC20K-2415DZ`（FP `Library:REC20K-Z_1in_THT`）、入口 `F2A` 速断、PPTC 3 個。ADC の LDO は `+15V` 直結で、ADC 枝に PPTC は無い。
  v2.1 ではこれを RS6-1215D・PD 12 V からの ADC 電源・ADC 枝の PPTC へ替える（DECISIONS §3・§4）
- **トーン**: PT2314E（`SOIC-28W`）。外付け網は DS どおり、`DGND` はチップの足元で `A_GND`、I²C 境界は `BSS138` ×2（PT 側 10 k → `VCC_TONE`）。
  UI の MCP23017 の `INTA`/`INTB` は Pico へ（外付け 10 k → `3V3`）
- **箱の I/O**: 入力 `J_IN401`（Phoenix MKDS-1,5）、HP／LINE は JST XH 3P（パネルジャックへケーブル）。3 つとも L / `A_GND` / R。
  HP は DIP-8 ソケットのバッファ越し、LINE はポット直出し
- **パネル**: 操作は FrontPanel 子基板に集約（垂直実装→物理パネルへネジ止め）。DEST=`Cosland 2MD1`、PWR=`Cosland 2MS1`、ENC=EC11E 垂直押し・軸 L=25。
  ポット本体はユニバーサル基板から `JST XH 6P` で FrontPanel へ。母板↔FP の渡りは XH（デジ・音声・電源を分ける）
- 部品調達の PRECISION / MATCH / SPEC は [PARTS.md](PARTS.md) §0c（[issue #38](https://github.com/indare/pcb_work/issues/38)）

**PCB**（v2.1 では娘のコネクタ 2×12・リレー追加で娘は引き直しになる。以下は写したときの状態と、引き直しでも生きる教訓）
- **ゾーン**: 下辺＝パネル、左上＝ルート音声、右上＝ルート電源、中央＝娘タイル、その下＝Out→MeasureControl（`place_pcb_zones.py`）。
  親は Edge.Cuts `(5,5)–(455,455)` のラフ配置のみ、配線・ベタはまだ。FrontPanel は Edge `(15,470)–(165,620)`、FP 済み・配線未着手
- **娘（Switch）**: `TMUX7612` は 270°、DIP-8 は奇数・偶数とも 0°（正は `TMUX_MAP`）。CH1–4 の配置・配線まで済み。
  各 TMUX の D は本体下の F で南北直結＋幹線へは片側 1 本の引き込み（B.Cu）。TMUX の 100 nF・1 µF は 0603 で本体直下の裏
- **娘（Relay）**: リレー列とドライバの間の帯を組み直し、L/R を別の通り道に分けた（`relay_band_rework.py`・`relay_lr_separate.py`）
- **グランド**: ⚠ **ベタ GND は 1 枚にしない。** 4 系統を NetTie の星で一点接続しているので、系統ごとに別ゾーン。
  XH ごとに GND を混ぜない（`A_GND`＝音声 XH、`D_GND`＝デジ XH、`PD_GND`＝電源 XH）
- **娘の外形とコネクタ**: 外形は PCB の Edge が正。pin1 のローカル X・南北の辺・キーイング・M3 四隅（端から 5.0 mm）の規則は維持（本数は v2.1 で 2×12、DECISIONS §2-5）
- **配線の教訓**（v2 の娘の配線で分かったこと）:
  - 無検査の F→B 載せ替えは不可（同じ幾何で層だけ替えると既存 B.Cu と衝突し、DRC が約 180 件出た）。「衝突しない区間だけ移す」も簡易判定では短絡が残る
  - 1 ホップずつ探索配線する。スクリプトで全面を載せ替えない（衝突回避つきの探索か、KiCad の手配線）
  - TMUX7612: SEL とアナログを並走させない（直角交差のみ）、TSSOP のパッド上ビアは禁止
  - 減点しない（意図どおり）: 娘の `A_GND`↔`D_GND` のタイ無し、四隅 M3 の keepout 内置き、Amp のデカップ裏置き
  - GUI 無しの確認は `scripts/pcb_preview.py`

## やらないこと（エージェント）

- 「ゲート」「閉じた」「B5 解放」などの**工程ラベルを新設しない**（ユーザーが言ったときだけ）
- 進捗の報告を **DECISIONS の追記だけ**で終わらせない。正は図・PCB・生成コードの差分
- このファイルを勝手に長くしない。現況が変わったら**短く差し替える**
- `AudioV2/`・`Audio/` の文書を v2.1 の文脈として読まない（[CLAUDE.md](CLAUDE.md)）
