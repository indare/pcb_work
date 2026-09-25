# v2 から持ち越した表（v2.1 では成り立たない v2 の決定・訂正された記録）

> **履歴の記録。** 2026-09-25 まで [../DECISIONS.md](../DECISIONS.md) の §8・§9 にあった表を、本文を変えずにここへ移した（リンク先だけ `review/` からの相対に直した）。
> v2.1 の決定の正は `../DECISIONS.md`。v2 から引き継いだ決定は、そちらの §7（`V21-継-nn`）に v2.1 の項目として書き直してある。

読み方:

- 表の「v2.1 の扱い」の欄などに出る **§n-m は `../DECISIONS.md` の節**、`V21-未決-nn`・`V21-実測-nn` は `../DECISIONS.md` §10 の項目
- 「L28」「v2 L3375」などの**行番号は v2 の決定ログの行**。v2 の本文は読まない（基準は [README.md](README.md)）
- 略記 [NOW]・[pow]・[sw] は `../DECISIONS.md` §0-3 の定義（[pow] = [../ds_facts/power.md](../ds_facts/power.md)、[sw] = [../ds_facts/switch_control.md](../ds_facts/switch_control.md)）

---

## 1. v2.1 では成り立たない v2 の決定（旧 DECISIONS §8）

| v2 の決定（行番号と見出しの語） | 何が崩すか | v2.1 の扱い |
|---|---|---|
| L28 決定ログ「切替方式」: 電源は常時給電、入力はブロードキャスト | 選んだ ch だけ電源と入力を生かす | §1-1、§1-2、§2-8 |
| L2861「11.1 切替アーキテクチャ」の「電源は常時給電」、L4660（L4649「実装への波及」の節の「なぜ電源を切らないか」） | 同上。LDO の EN で切るので接点を通らない | §2-8 |
| L17 決定ログ「CH / 電源 / 音声切替」・L41–42（L37「アクチュエータ」の表）「ラッチングリレーで 1 系統だけ有効（電源もリレー）」 | 考え方は戻る。手段が「娘ごとの電源リレー（1 段目）＋ ch ごとの LDO の EN（2 段目）」に変わる（査読で「無効」から「前提変更」へ） | §1-3、§2-1、§2-8 |
| L3601「出力のみ MUX へ揃える」（v2 の B0）「入力ブロードキャスト＋出力のみ MUX」 | 入力も切る | §2-8 |
| L3569「入力トポロジは A案＋1µF フィルム」（v2 の B1）「入力 220 kΩ を撤去」 | 撤去の主な理由（入力スイッチが無い）が消えた | `TONE` バスに 100 kΩ（§2-11）。ch 側の 220 kΩ を戻すかは未決（V21-未決-13） |
| L4462「リレー版とアナログスイッチ版を別設計として両方起こす」・L4502「別 PCB 2種として起こす」 | ユーザー決定（[NOW] L24–25: 基板は 1 種類、聴き比べはしない）。監査の判定は「維持」だった（決定より前） | §1-4 |
| L3869「娘基板の接続方式 — A（横並び・直結）で確定」、L3884（L3877「接続方式 — 4案のうち3案が落ちた」の表の行）縦積み B は番地衝突で却下 | 番地は v2 で娘のジャンパに移り、却下理由が消えた | 縦積みを採用（§2-1、§2-5）。DIP ソケットへ手が届くこと（L3177）は条件として残る（V21-未決-20） |
| L249「`REC20K-2415DZ` へ差し替え」・L1539「`REC20K-2415DZ` — ±15 V のまま」 | 1 ch 運転で −15 V が DS の範囲から最も遠い、絶縁容量 2000 pF | RS6-1215D（§3-1） |
| L138「電源の要求は『合計 mA』ではなく『ソケット1個あたり何 mA』」（10 個常時通電） | 常時負荷は 1 ch 分。律速は ch の LDO ではなく RS6（査読で訂正） | §3-1 |
| L468「絶縁 DC-DC の絶縁容量 — 探索結果」の「低 Ciso 品は 6 W 上限でこの電力帯に代替が無い」 | 1 ch 通電で ±200 mA 帯に入り、L476 の 6 W 低 Ciso 群（10〜20 pF）も候補になった。RS6（110 pF max）はこの群より 5〜10 倍悪い。**この群を比較に入れなかった理由は記録に無い**（[review/decisions_audit_1_review.md](decisions_audit_1_review.md) 修正の要点 3） | V21-未決-21 |
| L1014「v1 の `MCW03-12D15` は別の軽負荷問題」の節、L1042「AudioV2 はこれを継承しない」 | v2.1 は選んだ ch だけ給電で、軽負荷を継承する | 合計の負荷率で選ぶ（§3-1）、−15 V のプリロード足場（§3-10） |
| L171「非絶縁バック…を削除。ADC の LDO は `+15V` 直結」 | RS6 の +15 V に入らない | PD 12 V から（§4-4） |
| L198（`A_GND`–`D_GND` の NetTie を足した節）の木 | ADC の帰りが PD 側になる | グランドの木の付け替え（§4-4） |
| L226「ADC 枝の PPTC は戻さない」 | 前提（LDO が DC-DC の短絡保護の後ろ）が消えた | PPTC 新設（§4-5） |
| L290「【却下】ADC を絶縁した島にする案」 | 理由②（絶縁容量）は弱まるが、①③と費用対効果は成立 | **却下のまま**（§4-10） |
| L2380「3. 音量方式」〜L2413 PGA2310／digipot の見送り | 理由はすべて成立（±5 V 問題は振幅の上限の話で、専用電源でも解けない） | **却下のまま**（§7） |
| L3965「電源カット…反対理由が入れ替わる」〜L4088（L4076「この構成が要るのは 16ch 以上のときだけ」の節の末尾）「選んでいない ch の電源を切るのは 16 ch 以上のときだけ」 | 構造の反対理由（ESD・入力クランプ）は入出力のスイッチで消えた | **採用**（§1-1）。熱の揃い・整定はファームの問題（§1-2） |
| L3955「結論の候補 — 6ch × 2 = 12ch」・L4076「16ch 以上のときだけ」の 6ch×2・電源カットなし | 入力 TMUX が ch ごとに要る、RS6 の ±200 mA を超える | 採らない |
| L4569「経路ごとの振幅上限」 | 精密／フルレンジ DIRECT は要件外（通常経路の行は残る） | §1-5 |
| L700「±15 V の理由は3つとも消えた…±12 V 側にも重い障害…未決」〜L916 | 生の ±15 V（PT2314E・計測・娘の TMUX）＋ ch の LDO で ±12 V に決着 | §3-3 |
| L4345「`+9V` 三端子が『使わなくなるかもしれない』理由」 | レールは ±15 V のまま、PT2314E は L7809 のまま | §3-4 |
| L4630（L4620「2026-09-01 の『アナログスイッチへ』の判断が不十分だった点」の表の行）TMUX4821 の却下理由「OFF 漏れ」 | OFF 側に信号が無いので不成立。2 mm QFN の理由は成立 | 却下のまま（TMUX7612 を選択） |
| L3492「残る食い違い（A6 とは分けて扱う）」の「`ISO7741`＋ADC の電源を二次側へ」 | ADC の LDO を PD（一次側）から取る決定と逆向き。09-07 の島の却下理由 ①③ も残る | 採らない（§3-9、§4-10） |
| L2329（L2322「C. 3 枚構成」の節の本文）B2-exp（娘の MCP23017）、L4358「I/O エキスパンダも同じ」 | 娘のロジックを親からのレベル線だけにする案が候補 | 未決（V21-未決-03） |
| L1742「懸念と扱い（2026-08-31 に ±12 V へ移したときの記録）」 | ソケットは ±12 V に戻るので、最大出力の低下はソケット側でまた当たる | §3-3 の前提 |

---

## 2. 訂正された記録（旧 DECISIONS §9）

査読・照合で直った記録。v2 の本文や過去の査読を読むときは、この表の読みを使う。

| # | 誤っていた記録 | 正しい読み | 出典 |
|---|---|---|---|
| 1 | 計測側の予備 12 V 入口のヒューズ（記録上の参照 `F1601`）が箱全体の上流・マスターヒューズで、ADC の LDO の上流にある（`rejected_review.md` #7、`rejected_review_review.md` #7、`decisions_audit_1.md`・`_review.md`、NOW の旧記述） | **誤り。** そのヒューズは予備入口（記録上の参照 `J1602`）と `PD_12V_SW` の間だけにある。PD 本線（受け端子 → 主電源スイッチ → `PD_12V_SW`）には枝より手前のヒューズが無い。PPTC を戻す結論は、上流が無保護という別の理由でむしろ強まる | [review/adc_gnd_retree_review.md](adc_gnd_retree_review.md) §2 |
| 2 | RS6 の「200 kHz」は軽負荷でも 200 kHz 以上を DS が保証 | 条件欄「0-100% load」・**Min 列に 1 値だけ**。試験条件も、バースト（間欠）の包絡の有無も書いていない。「DS の字句が候補中で最も強い」が正確 | [pow] §1、[review/main_power_compare_review.md](main_power_compare_review.md) 1-3 |
| 3 | RS6 の「無負荷入力電流 55 mA」 | DS の字句は "Quiescent Current"、**Max 列**、条件欄の印字は "2VDC"（12 V の位置）。負荷の条件は書かれていない | [review/ds_errata_review.md](ds_errata_review.md) P1 |
| 4 | RS6 の UVLO ON 9 V は REC10K と同じ比 | RS6 の 9 V は **Typ**（REC10K の 9 V は max だった） | [review/decisions_audit_1_review.md](decisions_audit_1_review.md) L655 の行 |
| 5 | L7809 の規定入力範囲の下限 11.5 V | **入力範囲の規定項目は無い。** 11.5 V は出力電圧 8.55〜9.45 V を保証する試験条件の下限。実際に出力が落ちるのはドロップアウト（約 1.5〜1.6 V、目読み）＋入口の PPTC の降下を割ったとき | [pow] §5（L7809C）、[review/stack_relay_power_review.md](stack_relay_power_review.md) 2-4 |
| 6 | TMUX7612 の膝は「レールから約 4.2 V 内側」 | DS 本文は "roughly 5 V"、Figure 5-4 の目読みで ±15 V の正側は約 +10.6 V。幅は「どこを膝と呼ぶか」の定義の差 | [review/decisions_audit_1_review.md](decisions_audit_1_review.md) 数値の検証、[sw] §1 |
| 7 | 「1 ch 運転の律速は ch ごとの LDO（150 mA）」 | 律速は RS6（+15 V の残り約 109 mA < 150 mA） | [review/decisions_audit_1_review.md](decisions_audit_1_review.md) 修正の要点 2 |
| 8 | 「8 ch 故障で OLP の 150 % 領域に入る」／「136〜149 % の帯だけ保護が働かない」 | 8 ch の max 積みの全域で、+15 V は定格の 136〜161 % のまま流れ続けうる（OLP が出力ごとか合計かは DS に無い） | [review/rejected_review_review.md](rejected_review_review.md) #5、[review/main_power_compare_review.md](main_power_compare_review.md) 1-5 |
| 9 | ch LDO のソフトスタート電流「8.6 µA」 | **8.6 mA** | [review/main_power_compare_review.md](main_power_compare_review.md) 1-4 |
| 10 | 「1 ch で −15 V は RS6 の約 21 %」 | INA1650 を足す前の数字。足すと typ・無音で約 26.7 % | [review/main_power_compare.md](main_power_compare.md) §1.5 |
| 11 | 記録上のグランド差の除去「約 43 dB」を Q1 の値として Q2 と比べる | 43 dB は `A_GND`↔`ADC_GND` の差で、47 Ω 付きの構成の値らしい（確度 中）。Q2 が落とす ch 側↔計測側の差は、Q1 では 0 dB | [review/tap_compare_review.md](tap_compare_review.md) §2.1 の表・4-4 |
| 12 | `ADC_BCK` は 6.144 MHz（v2 L3375、L3369「ノイズが実際に通る経路」の表の行） | マスター動作で BCK は 64 fS ＝ 3.072 MHz。6.144 MHz は変調器の 128 fS | [review/tap_compare.md](tap_compare.md) §2.4、[_review](tap_compare_review.md) 1-4 |
| 13 | JT-11P-1 の「1 kHz <0.001 %」は上限 | **TYPICAL 列**。+14 dBu・+20 dBu の曲線もある | [review/tap_compare_review.md](tap_compare_review.md) 3-5 |
| 14 | ISO224B の雑音は 3 µV/√Hz で −106 を割らない | 同じ DS の出力雑音から出すと入力換算約 9 µV/√Hz（3 倍の食い違い）。悪い方なら雑音だけで −106 を割る | [review/tap_compare_review.md](tap_compare_review.md) 6-2 |
| 15 | 「今の図では ±15 V と ADC の電源は一緒に来る」 | LT1763 は CBYP 10 nF で起動に 15 ms かかり、v2 の図でも投入時は ADC が遅れる。PD 給電で新しく開くのは**電源断**の窓 | [review/adc_gnd_retree_review.md](adc_gnd_retree_review.md) §9 C5 |
| 16 | 「RCOM 1 MΩ ならセンス線が切れても Q1 相当」「センス線は nA 級」 | RCOM 1 MΩ では断線で −9.5 dB、センス線に約 6.2 µA pk/ch。Q1 相当・nA は RCOM = 0 のとき | [review/adc_gnd_retree_review.md](adc_gnd_retree_review.md) §9 C1・C2 |
| 17 | 「`±15V_AFE` の RC で電流を絞る」「LDO 前の RC でリップルを PD 側で閉じる」 | 前者の 35 dB は電圧の減衰で、渡る電流は ≈ Vripple/R。後者は LDO 足元の MLCC のほうが低インピーダンスで、大半が `ADC_GND` を回る | [review/adc_gnd_retree_review.md](adc_gnd_retree_review.md) §9 C3・C4 |
| 18 | 直列 4.7〜10 Ω は「接点の DS の定格を超える」 | DS の 1 A は抵抗負荷の開閉電流で、メイク時の減衰する突入を規定していない。「DS の保証の外。1 A を代理の物差しにすると超える」 | [review/stack_relay_power_review.md](stack_relay_power_review.md) 1-3 |
| 19 | 「24 mA での LDO の VDO は DS に無い」「ヘッドルーム ≥ 1 V が規定」 | TPS7A49・TPS7A30 とも VDO の典型曲線がある（24 mA で約 0.12〜0.2 V）。≥ 1 V は設計例の "for optimal performance" の目安 | [review/stack_relay_power_review.md](stack_relay_power_review.md) 3-2・3-3 |
| 20 | 「音声 SET を共通 1 本にすれば 2×10 に収まる」「コイルの最悪は 480 mA」 | 24 − 3 ＝ 21 本で 2×10 には入らない。コイルの最悪は L7805C の上限 5.25 V・コイル −10 % で 46.7 mA × 12 ＝ 560 mA | [review/stack_relay_power_review.md](stack_relay_power_review.md) 7-2・7-3 |
| 21 | 「SET/RESET の同時通電は 1 µs 未満」「TPS3808 で 10〜20 ms の遅延」 | 前者はドライバ入力の話で、コイル電流の重なりは L/R で決まり DS から上限が出ない。後者は CT の公差込みで 9.1〜23.4 ms | [review/rail_detect_review.md](rail_detect_review.md) §2-3・§2-4 |
| 22 | `DEST_ADC`（ADC0）は使用中 | 実質空いている（v2 で位置センスラダーを廃止し、ファームも読まない。査読時の確認は [review/rail_detect_review.md](rail_detect_review.md) §7.1）。v2.1 では LM4040 の比率校正に使う（§5-2） | [review/rail_detect_review.md](rail_detect_review.md) §7.1 |
| 23 | `ADC_nRST` は Pico が駆動する | 監視 IC の出力とプルアップだけ。Pico が叩くのは `ADC_nMR` | [review/rejected_review_review.md](rejected_review_review.md) N3 |
| 24 | OPA1652・OPA1612・NJM5532 に入力保護ダイオードの記述は無い（ds_facts の旧版） | **ある**（back-to-back、入力電流 ≤ 10 mA／NJM5532 は投入時の入力ダイオードと V+ 開放時の注意）。ch ごとに電源を落とす構成に直接効く | [review/ds_errata_review.md](ds_errata_review.md) O1〜O3 |
| 25 | PT2314 の入力抵抗 30/40/50 kΩ を PT2314E の DS と食い違うとした（監査） | 30/40/50 は旧 PT2314 の音量入力 `RIV` として正しい。PT2314E で比べる行は `RIN`（VOL = 0 dB）13/20/27 kΩ | [review/decisions_audit_3_review.md](decisions_audit_3_review.md) 覆した点 2 |
| 26 | 「PT2314 のクリップ 2〜2.5 Vrms」は誤記 | 旧 PT2314 の DS の値。PT2314E では VOMAX min 2.3 / typ 2.6 Vrms（部品を替えたことによるずれ） | [review/decisions_audit_3_review.md](decisions_audit_3_review.md) 覆した点 3 |
| 27 | 「KiCad 標準に W5.0 は無い（W4.5 が最大）」 | W7.2 も汎用の W5.0 も標準にある | [review/decisions_audit_3_review.md](decisions_audit_3_review.md) 覆した点 4 |
| 28 | 参考製品の「約 1 秒のミュート・音声回路を GND に落とす」は PDF で確認できない（`arch_zero_base_review.md` §6） | PDF p2 のテキスト層に原文がある（PyMuPDF で抽出して確認）: 「1 秒程度の無音期間（音声回路を安全な GND 信号と接続）」 | [datasheets/reference/Kyohritsu_KP-HAMP61_manual.pdf](../datasheets/reference/Kyohritsu_KP-HAMP61_manual.pdf) p2 |
| 29 | ヘッドホンバッファの「最大」「上限」の負荷の行を定常として扱う | 32 Ω に連続で出すと接合温度が定格を超えるので定常にはならない（DC-DC を大きめに見る上限としてだけ使う） | [review/main_power_compare_review.md](main_power_compare_review.md) 1-2 |
| 30 | TPS7A30 の電流定格 200 mA | 推奨動作条件は 200 mA だが、同じ DS の 8.1 Overview は 150 mA（DS 内の食い違い） | [review/decisions_audit_1_review.md](decisions_audit_1_review.md) 数値の検証 |
| 31 | 「RS6 で ADC を +15 V に載せると 197.7 mA＝98.9 %、余裕が無いだけで入る」 | 197.7 mA は INA1650・入力 TMUX・ch LDO の自己消費を足す前の値。足すと 1 ch・max・無音で約 212 mA（106 %）、HP 最大で約 237 mA（119 %）〔計算〕で、定格に入らない | [review/DECISIONS_v21_review.md](DECISIONS_v21_review.md) B2、[review/main_power_compare.md](main_power_compare.md) §1.5 |
