# AudioV2.1 決定ログ（DECISIONS）— 下書き

- 作成: 2026-09-25（エージェントの下書き。ユーザーの査読前）。置き場所は `AudioV2.1/DECISIONS.md` を想定し、**リンクはすべて `AudioV2.1/` からの相対パス**で書いた
- 現況（いま何待ちか）の正は [NOW.md](NOW.md)。この文書は「何を決めたか・なぜか・何を捨てたか」だけを持つ
- 回路図から導出できる事実（ネットリスト・参照・部品数・部品値）は書かない（[../SOURCE_OF_TRUTH.md](../SOURCE_OF_TRUTH.md)）。部品は機能名かネット名で書く。**選定として決めた型番**（RS6-1215D など）と、決定を支える DS の数値は書き、出典を付ける
- v2 の決定ログ（4,890 行）は [../AudioV2/DECISIONS.md](../AudioV2/DECISIONS.md)。本文を写さず、行番号と見出しでリンクする（v2 の行番号は凍結された v2 のもの。`AudioV2.1/DECISIONS.md` の旧版はこれとバイト一致だった）

---

## 0. v2.1 とは

### 0-1 目的

オペアンプを電子的に切り替えて、音の差を耳で楽しむ箱。**計測器ではない。** 切替素子の優劣も耳で決める（[NOW.md](NOW.md)「装置」）。
計測系（ADC・スペアナ）は表示と簡易分析のためにあり、**本線（聴く経路）を汚さないことが計測の精度より優先**する（§4-2）。

### 0-2 v2 との関係

- `AudioV2.1/` は 2026-09-25 に `AudioV2/` を**全部コピー**して作った。v2 は残す（[../CLAUDE.md](../CLAUDE.md)、[NOW.md](NOW.md) 冒頭）
- 目的は「選んだ ch だけ電源と入力を生かす」構成の検討。v2 は「全ソケット常時通電・入力はブロードキャスト」だった（v2 [L28 決定ログ「切替方式」](../AudioV2/DECISIONS.md)）
- v2 の決定のうち、v2.1 でもそのまま効くものは §7、成り立たなくなったものは §8 に表で置いた（棚卸し: [review/decisions_audit_1.md](review/decisions_audit_1.md)・[_2](review/decisions_audit_2.md)・[_3](review/decisions_audit_3.md) とそれぞれの `_review`。**査読が監査を直したところは査読を採った**）

### 0-3 読み方

各項目は次の形で書く。

| 欄 | 中身 |
|---|---|
| **決定** | 1〜3 行 |
| **理由** | いちばん強い理由 1 つ |
| **根拠** | `ds_facts/`・`review/`・`spice/`・`scripts/`・DS へのリンク |
| **前提・外れる条件** | これが崩れたら見直す |
| **却下した案** | 1 案 1 行、理由とリンク |
| **状態** | **決定**（ユーザーが決めた）／**いったんの決め**（推奨をユーザーが受けた。査読で出た値を仮に採ったもの）／**未決**／**要実測** |

略記: [NOW] = [NOW.md](NOW.md)、[pow] = [ds_facts/power.md](ds_facts/power.md)、[sw] = [ds_facts/switch_control.md](ds_facts/switch_control.md)、[op] = [ds_facts/opamps.md](ds_facts/opamps.md)、[tap] = [ds_facts/tap.md](ds_facts/tap.md)、[bnd] = [ds_facts/boundary.md](ds_facts/boundary.md)（照合 [verify_boundary.md](ds_facts/verify_boundary.md)）。`ds_facts/relay4.md` は**未照合**なので根拠に使っていない。

---

## 1. 設計の根本

### 1-1 コールドスタンバイ — 電源要求の違う回路を切り替える

- **決定**: 解く問題を「電源要求の違う回路を同じバスへ切り替えること」と置く。非選択の回路は**電源ごと落とし**、バスとの境目には「電源が無いときにも切れている素子」を置く（コールドスタンバイ）。回路ごとに自分の電源（LDO で電圧を選ぶ）を持たせて同じバスに混ぜる
- **理由**: v2 の形では、非選択の回路が境目の素子（TMUX7612）を生かすために通電していた（ホットスタンバイ）。TMUX7612 の DS には**電源を切ったときの漏れ・高インピーダンスの規定が無く**、端子はレールへダイオードでクランプされている
- **根拠**: [NOW] L22「設計の根本」／[bnd] §1.1（TMUX7612: 電源断時の規定なし、"Pins are diode-clamped to the power-supply rails."、電源シーケンスは任意）
- **前提・外れる条件**: 境目の素子が電源断でも切れていること（§2-1 のラッチングリレー）。境目の外にある素子（TMUX、計測、トーン）は常時通電のまま
- **却下した案**: v2 の「全 ch 常時通電・入力ブロードキャスト」— 選んだ ch だけを生かす目的と逆（v2 [L28](../AudioV2/DECISIONS.md)、[L2861 §11.1](../AudioV2/DECISIONS.md)）
- **状態**: 決定（ユーザー判断 2026-09-25）

### 1-2 同時に生かすのは厳密に 1 ch

- **決定**: 電源と入力を生かすのは**選んだ 1 ch だけ**。ファームは全 OFF → 1 ch ON。温めておく ch は作らない。ハードは ch ごとに独立して切れる。ヘッドホンは 32 Ω を想定
- **理由**: 主電源（RS6-1215D、±200 mA）の予算がこの前提で成り立つ（§3-1）。温めておく ch を許すと、同時に通電できる数が DC-DC の型番で決まってしまう（最悪の石で 5 ch、80 % で使うなら 3 ch という見積もりがあった）
- **根拠**: [NOW] L9／[review/rejected_review.md](review/rejected_review.md) #5・[rejected_review_review.md](review/rejected_review_review.md) #5（温める数の見積もりと訂正）
- **前提・外れる条件**: 石の熱の整定（通電してから音が落ち着くまで）が許せる長さであること。v2 の反対理由「今つけた石と、ずっとついていた石を比べる」（v2 [L3965](../AudioV2/DECISIONS.md)）はハードでは解けず、切り替えてから聴くまでの待ち時間の問題として残る（[rejected_review_review.md](review/rejected_review_review.md) §6 U2）
- **却下した案**: 「最低 1 ch、温める数はファームが決める」— 同上（DC-DC の余裕を食う）
- **状態**: 決定（ユーザー判断 2026-09-25）

### 1-3 制御の木は 2 段

- **決定**: 1 段目＝**基板（娘）1 枚だけ ON**、2 段目＝**その基板の中で 1 ch だけ**。どちらも「全リセット → 1 つだけセット」のブレーク・ビフォア・メイク
- **理由**: 選んだ 1 ch だけ給電する形なら、1 段目の故障（別の基板にも電源が入る）でも ch の EN が 2 つ目の関門になる（[review/dcdc_2stage_review.md](review/dcdc_2stage_review.md) 要約 3）。逆に基板をまたぐ排他が無いと、娘 4 枚が 1 ch ずつ ON の最悪で RS6 の +15 V が定格の 110 % になり、過負荷保護（150 %）は働かない
- **根拠**: [NOW] L24／[review/bulk_parent_sim.md](review/bulk_parent_sim.md) §0.3（4 枚 110 %、2 枚以下なら 89 %）／[review/dcdc_2stage.md](review/dcdc_2stage.md)・[_review](review/dcdc_2stage_review.md)
- **前提・外れる条件**: 1 段目・2 段目の中身は §2
- **却下した案**: 親のスロットごとの電源スイッチ（eFuse 等）で 1 段目を作る案 — §2-1 の縦積みリレーで不要になった（[NOW] L24「旧 N1/N2 は不要」）
- **状態**: 決定（ユーザー判断 2026-09-25）

### 1-4 基板は 1 種類、1 枚 4 ch、切替素子の聴き比べはしない

- **決定**: 娘は 1 種類だけ（中は TMUX7612 で ch を選ぶ）、1 枚 4 ch。ch ごとのリレーの基板と、切替素子の聴き比べは v2.1 ではやらない
- **理由**: ユーザーの判断（[NOW] L24–25）
- **根拠**: [NOW] L24「決定（2026-09-25、差し替え）: DC-DC は RS6、1 枚 4 ch、基板は 1 種類だけ」、L25
- **前提・外れる条件**: —
- **却下した案**: v2 の「リレー版とスイッチ版を別 PCB 2 種で起こし、実機で比べる」（v2 [L4462](../AudioV2/DECISIONS.md)・[L4502](../AudioV2/DECISIONS.md)）— v2.1 の目的から外した／ch ごとにラッチングリレーを置く娘（[review/arch_zero_base.md](review/arch_zero_base.md) §0.1 #11）— 同上
- **状態**: 決定（ユーザー判断 2026-09-25）

### 1-5 DIRECT（PT2314E を飛ばす経路）は聴くためのライン入力用

- **決定**: DIRECT はライン入力を聴くための経路とする。v2 の「経路ごとの振幅上限」のうち**精密 DIRECT・フルレンジ DIRECT は要件から外す**。PT2314E を通る通常経路の上限の考え方は残る
- **理由**: 装置は計測器ではない（§0-1）。精密 DIRECT は TMUX の膝の近くまで振る運用のためのもので、耳で比べる用途には要らない
- **根拠**: [NOW] L18／[review/decisions_audit_3_review.md](review/decisions_audit_3_review.md)（v2 L4569 は「無効」ではなく「前提変更」。無効なのは DIRECT の 2 行だけ）
- **前提・外れる条件**: DIRECT の置き場所・切替の形は**未決**（[NOW] L27）。ライン入力の振幅の定義（2 Vrms か、それ以上か）も未決（[review/rejected_review.md](review/rejected_review.md) §3.4）
- **却下した案**: —
- **状態**: 決定（ユーザー判断 2026-09-25）。置き方は未決

---

## 2. 制御の木

### 2-1 1 段目: 縦積みの各娘に電源用ラッチングリレー → レールがそろってから音声用

- **決定**: ±15 V は全段に常時通す。各娘で **電源用ラッチングリレー（DPDT 1 個、+15 V と −15 V に 1 極ずつ）** をセット → 両レールがそろってから **音声用ラッチングリレー（DPDT 2 個、`TONE_L/R` と `AMP_SEL_L/R` の 4 本）** をセット。リセット（NC 側）は切り離し
- **理由**: ラッチングなら聴取中に音声の近くを制御電流が流れない（ユーザーの好み）
- **根拠**: [NOW] L24／[review/arch_zero_base.md](review/arch_zero_base.md) §1.1「ユーザーはラッチングリレーを好む」／[review/stack_relay_power.md](review/stack_relay_power.md)・[_review](review/stack_relay_power_review.md)
- **前提・外れる条件**: ラッチングリレーは衝撃・前歴で状態が変わりうる（G6K・TQ の DS が「リセット位置で出荷、衝撃で変わりうる、初期化せよ」と明記 [bnd] §3、[verify_boundary.md](ds_facts/verify_boundary.md) 要約）。**電源投入時とすべての切替で全リセットから始める**こと（§6）
- **却下した案**:
  - 親のスロットごとの電源 IC（TPS26600 eFuse）— 内部にチャージポンプがあり周波数も DS に無い（電源経路に発振器・チャージポンプを置かない要件に反する）（[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §0.1）
  - 境目を非ラッチングリレー／電源断保護つきアナログ SW／PhotoMOS にする案 — [NOW] L22 の候補で、L24 でラッチングリレーに決めた。**個別の却下理由の記録は無い**（DS 事実は [bnd]）
- **状態**: 決定（ユーザー判断 2026-09-25）

### 2-2 リレーの品種 — AZ850P2-5 を電源・音声の両方に

- **決定**: 電源用・音声用とも `AZ850P2-5`（v1/v2 と同じ石）を使う方向
- **理由**: 直列 R を 15 Ω 以上にすれば電源の役でも突入のピークが抵抗負荷の開閉電流 1 A の内に入り（22 Ω で 0.68 A）、音声の役は最小開閉 10 mV / 10 µA・AgPd 金クラッド。2 コイル型なので今のシンク型ドライバ（TBD62083A）で SET/RESET とも駆動でき、FP・BOM・駆動が 1 種で済む
- **根拠**: [review/stack_relay_power.md](review/stack_relay_power.md) §0.1-5・§1.4／[sw] §2（AZ850）／v2 [NOW] の旧記述「リレーは AZ850P2-5 に固定（2026-09-09）」
- **前提・外れる条件**: 容量負荷のメイクは DS の規定の外（1 A は抵抗負荷）。**実機のメイク回数試験**が最終的な根拠（[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 1-3・1-4）。直列 R を 15 Ω 未満にするなら電源用だけ 2 A 級（TQ2SA-L2）
- **却下した案**: Omron G6KU・Fujitsu FTR-B3 — 単巻線ラッチで極性反転の駆動が要り、シンク型ドライバでは組めない（[review/stack_relay_power.md](review/stack_relay_power.md) §1.1）／`TQ2-L2` を AZ850 の FP に挿す — COM/NC/NO のピン番号が違い SET/RESET が反転する（v2 の注意、[NOW] 旧記述）
- **状態**: 未決（推奨。ユーザーの明示の決定は記録に無い）

### 2-3 配線: COM＝娘側、NO＝バス（スタック）、NC＝抵抗越しに GND

- **決定**: 音声・電源とも、接点の COM を娘側、NO をバス側、NC を抵抗越しに GND へ。リセット状態で娘側の音声の節とレールが抵抗で放電される
- **理由**: この向きなら NC の抵抗はセット・リセットのどちらの状態でもバスに載らない（バスに見えるのは開いた NO 接点だけ）。逆にするとバスを抵抗で負荷する
- **根拠**: [review/stack_relay_power.md](review/stack_relay_power.md) §0.1-6・§5.1／[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 5-1・5-2（AZ850 p2 の図と v1 のピンの使い方で確認）
- **前提・外れる条件**: 抵抗値は推奨どまり（音声 10 kΩ、レール 2.2 kΩ）で**未決**
- **却下した案**: 逆向きの配線 — NC の抵抗が並列でバスを負荷する（[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 5-2）
- **状態**: いったんの決め（配線の向き）／未決（抵抗値）

### 2-4 電源接点に直列 22 Ω（ヒューズ抵抗）、NO（スタック）側

- **決定**: 電源接点の後ろに各レール **22 Ω**。品種は**ヒューズ抵抗**（突入パルスには耐え、2 W 連続で開く）。**±15 V は DPDT 1 個で切り、22 Ω は NO（スタック）側へ置く**
- **理由**: 22 Ω で突入のピークが 0.68 A（接点の開閉電流 1 A の 68 %）。NO 側に置けば、リレーの中でどこの極間が短絡しても ±15 V の間に 44 Ω 以上が入る
- **根拠**: [NOW] L25／[review/stack_relay_power.md](review/stack_relay_power.md) §1.3（4.7 Ω で 3.10 A、10 Ω で 1.48 A、22 Ω で 0.68 A）／[review/rail_detect.md](review/rail_detect.md) §0.4／[review/rail_detect_review.md](review/rail_detect_review.md) §6（極間短絡で各 22 Ω に最大 11.5 W、RS6 が 0.3 A で頭打ちなら各 2 W 連続。**耐パルスの 1206 では焼けるので溶断型が要る**）／[spice/stack_relay/](spice/stack_relay/)
- **前提・外れる条件**: 最悪の角で LDO の入力が 13.60 V、ヘッドルーム（VIN − VOUT − VDO）は VDO の typ 曲線（約 0.2 V）で約 1.4 V〔計算〕（目安「≥ 1 V」は DS の設計例の "for optimal performance"）（[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 3-2〜3-4）。**ヒューズ抵抗の品番の単発パルス曲線は未収集**
- **却下した案**: 4.7〜10 Ω — 突入が接点の 1 A を超え、RS6 が突入を出せない場合に親の +15 V が 7〜11 V まで落ちる（[review/stack_relay_power.md](review/stack_relay_power.md) §0.1-1・2）／33 Ω — ヘッドルームの目安に近づき、レール検知の窓を狭める（同 §3、[_review](review/stack_relay_power_review.md) 3-4）／22 Ω を COM 側 — 極間短絡が ±15 V の直結になる（[review/rail_detect.md](review/rail_detect.md) §0.4）／±15 V を DPDT 2 個に分ける — ユーザーが 1 個のままを選んだ（D9）
- **状態**: 決定（DPDT 1 個・NO 側: ユーザー判断 2026-09-25、D9）／いったんの決め（22 Ω・ヒューズ抵抗）

### 2-5 制御線は全段共通、各娘はジャンパで自分の段を選ぶ

- **決定**: 制御線は全段に同じ番号で素通しする。電源用 SET は段ごと（4 本）で、各娘はジャンパで 1 本を選ぶ。RESET は共通。ch 選択線は共通。音声用 SET は共通 1 本（§2-6）。スタックの制御・電源のコネクタは **2×12**（24 本: 音声 SET 共通で 21 本 ＋ `MON_P`・`MON_N`・`RAIL_OK`）
- **理由**: 縦積みで各娘が同じピンを見るので、段ごとに違う線を通すなら番号をずらす仕掛けが要る。全段共通＋ジャンパなら娘の基板は 1 種類のまま
- **根拠**: [NOW] L24／[review/stack_relay_power.md](review/stack_relay_power.md) §7／[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 7-2（音声 SET を共通にしても 21 本で 2×10 には入らない）／本数はユーザー判断（2026-09-25）
- **前提・外れる条件**: 娘の MCP23017 を残して I²C を通すなら 2 本増える（[review/stack_relay_power.md](review/stack_relay_power.md) §7.2）。娘の MCP を残すかは未決（§10）。電源用 SET と音声用 SET で選ぶ段を食い違えない配置が要る（同 §7.2）
- **却下した案**: 今の 2×8 のまま — 本数が足りない（同 §7）／親にスロット 4 口を横に並べるバックプレーン — 縦積みに決めた（[review/arch_zero_base.md](review/arch_zero_base.md) §0.1 #15 は横並びを推していた）
- **状態**: 決定（ユーザー判断 2026-09-25）

### 2-6 D10: 音声用 SET は全段共通の 1 本

- **決定**: 音声用リレーの SET は**スタック全段に共通の 1 本**。条件: 壊れないこと（下の前提をファームが守ること）
- **理由**: B1（§5-4）で、レールの無い娘は音声 SET のコイルに電源が来ないので**セットできない**。衝撃でラッチした音声リレーは、段ごとの SET でも共通の SET でも防げない。共通線だけの弱点は「選んでいない娘の**電源**リレーが衝撃でラッチした場合、その娘のレールで B1 が導通し、共通 SET でその娘もつながる」ことで、これは §6 のファームの規則で防ぐ
- **根拠**: ユーザー判断（2026-09-25。親エージェントの確認を理由として記録）／[review/stack_relay_power.md](review/stack_relay_power.md) §7.2（共通案の弱点）／[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 7-4（段ごとの SET も衝撃でセットされた音声リレーは消せない）／[review/rail_detect_review.md](review/rail_detect_review.md) §3.3（B1）
- **前提・外れる条件**: **音声 SET は「全リセット（全娘の電源リレーと音声リレー）→ 選んだ娘の電源 SET → レール良好 → 共通の音声 SET」の 1 つの手順の中でだけ出す**（§6）。聴取中に衝撃で別の娘の電源リレーがラッチしても、その娘は電源が入るだけで（音声リレーはリセットのまま＝バスに出ない）、RS6 の負荷は最悪でも約 2 ch 分＝89 %（[review/bulk_parent_sim.md](review/bulk_parent_sim.md) §0.3）。次の切替の手順でリセットされる。ジャンパの重複で 2 枚が同じ段を選んだ場合は [review/stack_relay_power.md](review/stack_relay_power.md) §7.2 が挙げた弱点として残る
- **却下した案**: 段ごとの音声 SET（4 本）— 衝撃でラッチした音声リレーはどちらでも防げず、残る弱点はファームの手順で消せるので、ピンを 3 本使う理由が弱い（上の根拠）
- **状態**: 決定（ユーザー判断 2026-09-25、上の条件つき）

### 2-7 全リセット → 1 つだけセット。リセットの順番はファーム

- **決定**: 切替はいつも全リセットから。リセットの順番（音声を先・電源を後）は**ファームで守り、ハードは足場だけ**置く。パルス幅もファーム（§6）
- **理由**: 娘のバルクを外したので、電源接点が開いてから LDO が落ち始めるまで 0.4〜3.8 ms しかなく、リセット時間と同じ桁。同時に切るとバスに制御されない過渡が出うる。ただし**壊れはしない**ので、ハードで保証するのは必須ではなく保険
- **根拠**: [NOW] L25／[review/stack_relay_power.md](review/stack_relay_power.md) §0.1-7・§5.3／[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 6-1（ファームの ARST → 20 ms → PRST で足りる）
- **前提・外れる条件**: ハードで順序を保証する（PRST が音声のリセットも叩き、電源だけ 10 ms 遅らせる）かは未決（[review/rail_detect.md](review/rail_detect.md) §0.5 D6）
- **却下した案**: —
- **状態**: いったんの決め

### 2-8 2 段目: 娘の中は TMUX7612 で ch を選び、選んだ ch の石だけ LDO の EN で給電

- **決定**: 娘の中の ch 選択は TMUX7612。ch の**出力だけでなく入力も**切る（入出力 L/R＝ch あたり 1 パッケージ）。選んだ ch のソケットだけ、ch ごとの正負 LDO（TPS7A49／TPS7A30）の EN で給電する。TMUX は LDO の前の ±15 V で常時通電
- **理由**: 電源を落とした石の入力が共有の `TONE` バスにつながったままだと、どの石でも入力の絶対最大を越え、入力保護ダイオード越しにバスを低いインピーダンスで負荷する（PT2314E の最小負荷 5 kΩ を大きく割る）。アナログスイッチ自身は常時通電にしないと、スイッチがクランプになる
- **根拠**: [NOW] L9・L17・L25／[review/pm12_judgement.md](review/pm12_judgement.md) §5・[_review](review/pm12_judgement_review.md) §E／[review/ds_errata_review.md](review/ds_errata_review.md) O1〜O3（OPA1652・OPA1612・NJM5532 の入力保護ダイオード）／[review/dcdc_2stage_review.md](review/dcdc_2stage_review.md) 1.1（ch に 1 パッケージ）／v2 [L3999「入力クランプ」](../AudioV2/DECISIONS.md)・[L4048「アナログスイッチ自身は常時通電」](../AudioV2/DECISIONS.md)
- **前提・外れる条件**: 電源を切った石の出力も ESD 構造でレールにつながるので、出力も切る（v2 [L2871](../AudioV2/DECISIONS.md)）。正側 LDO だけが切れて負側が残る状態は NJM5532 の DS が注意する形（[review/pm12_judgement.md](review/pm12_judgement.md) §5.3-2）
- **却下した案**: 出力だけ切る（v2 の図）— 電源の無い石の入力に信号がかかる（[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6.3-2）／ch ごとの絶縁 DC-DC — 同時に生きる ch が 1 つなら守る相手が無い（[review/rejected_review.md](review/rejected_review.md) N1）
- **状態**: 決定（ユーザー判断 2026-09-25）

### 2-9 EN は娘の切られたレールから作る。1 ch だけ ON のデコーダは既定 OFF

- **決定**: ch の LDO の EN の論理は娘の切られたレール（電源リレーの後ろ）から給電し、**EN が LDO の IN を超えない形にする**。娘ごとに「1 ch だけ ON できる」デコーダを置き、有効化の既定は OFF。レールが落ちたら EN も切る（§5-5）
- **理由**: TPS7A49 の絶対最大は「EN – IN −36 / +0.3 V」。`3V3` が生きていて ±15 V が無いとき（主電源スイッチ OFF で Pico が USB だけで動く場合、RS6 が保護で止まっている間）に 3.3 V の EN を出すと定格を破る。起動の順序では防げず、DC-DC の型番でも直らない
- **根拠**: [NOW] L15・L25／[pow] §2（TPS7A49 絶対最大 EN–IN、VEN(high) 2.1 V、VEN ≤ VIN）・§3（TPS7A30 EN–IN −0.3/+36 V）／[review/main_power_compare_review.md](review/main_power_compare_review.md) 1-6・§3.3／[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6.2・§6.3-1
- **前提・外れる条件**: デコーダを娘に置くか親に置くか、娘の 3.3 V を何で作るか（発振器・チャージポンプの無いもの）は**未決**（[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6.4 A1）。[NOW] L15 の「直列抵抗＋EN→IN ショットキー＋プルダウン」は、EN をレールから作る形では要らなくなる（同 §6.2）。どちらの形にするかは未決。**1 ch だけ**をハードで守るのは娘の中だけで、娘をまたぐ排他は §2-6・§6 に残る
- **却下した案**: ファームの規約だけで排他する — MCP23017 の POR 後は全ピンが入力で、プルダウンが守るのはリセット中だけ。ファームのバグ（ポートに全ビット 1 を書く等）には効かない（[review/main_power_compare_review.md](review/main_power_compare_review.md) 1-5）
- **状態**: いったんの決め（EN はレールから・デコーダ既定 OFF）／未決（素子と置き場所）

### 2-10 切替の間は音声を GND へ落とすミュート

- **決定**: 切替の間は、音声を GND へ落として無音にする
- **理由**: 過渡の出どころ（TMUX と境目のリレーの切替、LDO の立ち上がり、出力結合の整定、娘のレールの切替）は全部 `AMP_SEL` バスに出るので、バスより上流の PT2314E のミュートでは消せない
- **根拠**: [NOW] L25／[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6.3-5／参考製品 [datasheets/reference/Kyohritsu_KP-HAMP61_manual.pdf](datasheets/reference/Kyohritsu_KP-HAMP61_manual.pdf) — PDF p2（本文テキスト層）「切り替え時はオペアンプの電源の切り替えと音声回路の切り替えを行いますが、…1 秒程度の無音期間（音声回路を安全な GND 信号と接続）が取られる構造」、PDF p3（画像、[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6 で読んだもの）「選択されていないオペアンプが、電源も含めて回路から完全に切り離されている」。操作子はスイッチ 1 個、音声の検出にマイコンを使う（PDF p1・p2）
- **前提・外れる条件**: `AMP_SEL` を直接 GND に落とすと、選んだ石の出力を結合コンデンサ越しに交流短絡するので避ける（[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6.3-5）
- **却下した案**: —
- **状態**: 決定（方針）／**未決**: 場所（ポットの前／HP 入力と LINE 出力／HP 出力の後ろ）、素子（常開・常閉・ラッチング・半導体）、時間（約 1 s＝2τ か 1.5 s＝3τ）（同 §6.4 M1〜M3）

### 2-11 `TONE` バスに 100 kΩ のプルダウン

- **決定**: 親の `TONE_L/R` に 100 kΩ で GND への DC の基準を置く
- **理由**: 今の `TONE` バスは直列のコンデンサに挟まれて DC が浮いている。音声リレーをセットした瞬間に娘側（NC 抵抗で 0 V）とバスの DC の段差が入りうる
- **根拠**: [NOW] L25／[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 5-4／[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6.1（20 Hz で約 −0.08 dB、PT2314E の最小負荷 5 kΩ の内側）
- **前提・外れる条件**: —
- **却下した案**: —
- **状態**: いったんの決め

---

## 3. 電源

### 3-1 主電源の DC-DC は RS6-1215D

- **決定**: ±15 V の絶縁 DC-DC は `RS6-1215D`（入手できれば）。SIP8 の新しいフットプリント（推奨穴 Ø1.00 +0.15/−0 mm）を作る
- **理由**: 1 ch の設計点で出力の合計が定格の **36〜63 %** で、候補の中で軽負荷の領域からいちばん遠い（軽負荷の振る舞いを決めるのは片側ではなく合計の電力）。あわせて最大容量性負荷 ±660 µF（出力ごと）、絶縁容量 110 pF max
- **根拠**: [NOW] L14／[review/main_power_compare.md](review/main_power_compare.md)・[_review](review/main_power_compare_review.md) §3.1（理由の順番を直した）／[pow] §1（±200 mA、9–18 V、±660 µF、110 pF max、内部動作周波数「0-100% load」Min 200 kHz、起動 2 ms、UVLO ON 9 V typ、OLP 150 %、SIP8 のピン配置と穴径）／[scripts/rail_budget.py](scripts/rail_budget.py)（`--adc-from-pd`）／[scripts/dcdc2/](scripts/dcdc2/)
- **前提・外れる条件**: ADC の LDO を ±15 V に載せない（§4-4。載せると +15 V は max 積みで 197.7 mA＝98.9 %）。8 ch が同時に入る故障では +15 V が定格の 136〜161 % のまま流れ続けうる（OLP が出力ごとか合計かは DS に無い、過熱保護の記載も無い）→ §2-9 のデコーダと §6 の手順で防ぐ。**突入をどこまで出せるか・OLP の形（定電流かヒカップか）は要実測**（§10）。今のフットプリント（1″×1″）には挿さらない。リポジトリにある SIP8 の FP は穴 Ø0.8 で合わない。CTRL を開放にしておけば ON（low は不可）（[review/main_power_compare.md](review/main_power_compare.md) §2.1）
- **却下した案**:
  - `TMR 9-1223` — Cout ±200 µF でレールの見込みの上側を超えうる、500 kHz は全負荷の値で軽負荷の記載が無い、金属ケース（[review/main_power_compare.md](review/main_power_compare.md) §2.1、[_review](review/main_power_compare_review.md) 1-3）
  - `TMR 10-1223WI` — Cout ±220 µF、絶縁容量 1000 pF typ、4.1〜4.5 V で起動するので PD が交渉する前の 5 V で動いてしまう（同上）
  - `REC20K-2415DZ`（v2 の石）— 1 ch では −15 V が定格の約 8 % で DS の Note4（10 % 未満は仕様を満たさないことがある）より下、絶縁容量 2000 pF typ（同上、[review/dcdc_2stage_review.md](review/dcdc_2stage_review.md) 1.2）
  - Mornsun `URA` — v2 と同じく NFND（v2 [L1674](../AudioV2/DECISIONS.md)）。「軽負荷で周波数を下げる」は決め手ではない（[review/rejected_review_review.md](review/rejected_review_review.md) #12）
  - ±15 V を 2 台に分ける（ソケット用と常時系）— HP バッファの電流は分けても共有側に残る（[review/rejected_review_review.md](review/rejected_review_review.md) N4）
- **状態**: 決定（ユーザー判断 2026-09-25、入手できれば）

### 3-2 PD は 12 V 固定

- **決定**: PD の受け電圧は 12 V に固定する（他の設定にしない）
- **理由**: ADC の LDO（LT1763）を PD 12 V から直接取るので、IN の絶対最大 ±20 V に対して 20 V 設定は許容差の分だけ超えうる。RS6 の入力範囲も 9〜18 V（サージ 25 V は 1 秒まで）
- **根拠**: [NOW] L11／[review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) 1 表（LT1763 の IN 絶対最大）・§7.4／[pow] §1（RS6 入力範囲）
- **前提・外れる条件**: PD モジュールは交渉前に 5 V を出す。主電源スイッチを入れたまま USB-C を挿すと、その間 ADC 側だけが立つ（[review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) §7.4「PD の 5 V の窓」）。RS6 は UVLO で止まっている
- **却下した案**: 15 V／20 V — 上の理由（v2 [L594](../AudioV2/DECISIONS.md)・[L662](../AudioV2/DECISIONS.md) の「12 V が出なければ 15 V」は RS6 の範囲内だが、固定にした）
- **状態**: いったんの決め

### 3-3 TMUX・PT2314E・計測は生の ±15 V、ソケットは ch ごとの LDO で ±12 V

- **決定**: ±15 V は常時系（TMUX7612、PT2314E の 9 V レギュレータ、計測系）にそのまま使う。ソケットは ch ごとの正負 LDO（TPS7A49／TPS7A30）で ±12 V。LDO の出力電圧は帰還の分圧で決まるので、ch ごとに選べる
- **理由**: ±12 V を DC-DC で直に作ると TMUX7612 の平坦域の膝がレールに追従して下がる（DS 本文: 平坦域は「概ね VSS+5 V〜VDD−5 V」。Figure 5-4 の目読みで Ron が底から離れ始めるのは ±15 V で約 +10.6 V、±12 V で約 +7.6 V）。ソケットだけを LDO の後ろで ±12 V にすれば膝は動かず、ch ごとの EN（§2-8）と PSRR も LDO が持つ
- **根拠**: [NOW] L17・L22／[sw] §1（平坦域の本文、Figure 5-4）／[pow] §2（TPS7A49 の出力電圧の式 R1 = R2 (VOUT/VFB − 1)、PSRR 72 dB @120 Hz）・§3（TPS7A30）／[review/rejected_review.md](review/rejected_review.md) #9／[review/pm12_judgement.md](review/pm12_judgement.md)・[_review](review/pm12_judgement_review.md)
- **前提・外れる条件**: ±12 V で電源範囲から外れる石は無い。ただし ±12 V の振幅を保証しているのは OPA1612・OPA2140 だけで、MUSES01（2 kΩ 基準）・OPA2604・OPA627 は推定で余裕が薄い。LDO の総合精度 ±2.5 % で全石が −0.3 V 動く（[review/pm12_judgement_review.md](review/pm12_judgement_review.md) 要約 5・6）。TPS7A49 の IOUT は 150 mA まで（[pow] §2）
- **却下した案**:
  - ±12 V の DC-DC で系全体を ±12 V（v2 [L700–916](../AudioV2/DECISIONS.md)、`REC10K-2412DAW/H2` ほか）— TMUX の膝が下がる。PT2314E の 9 V レギュレータ（L7809）の入力も 11.5 V（出力の許容差を保証する試験条件の下限）を割る（v2 [L855](../AudioV2/DECISIONS.md)。11.5 V の読みは §9）
  - `NSD10-12D12` — 2″×1″ で新しいフットプリント、最小負荷 20 mA/レール（1 ch 運転と合わない）、±12 V 出力（v2 [L1609](../AudioV2/DECISIONS.md)、[review/decisions_audit_1.md](review/decisions_audit_1.md)）
- **状態**: 決定（ユーザー判断 2026-09-25）

### 3-4 PT2314E は +15 V → L7809 のまま

- **決定**: PT2314E の電源は今までどおり +15 V から L7809 で 9 V
- **理由**: 電源だけ一次側（PD）へ移すと、PT2314E の帰り電流がグランドの木の中の唯一の橋を通る（v2 で一度潰したバグの再導入）
- **根拠**: v2 [L1456「`+9V` 枝を `+15V` から外すのは再導入」](../AudioV2/DECISIONS.md)／[review/decisions_audit_1_review.md](review/decisions_audit_1_review.md) 修正の要点 1（L1456 は「却下の再検討」ではなく維持）／[review/rejected_review_review.md](review/rejected_review_review.md) #8
- **前提・外れる条件**: +15 V の負荷を非対称にする唯一の塊がこれ（+15 V だけに 35〜48 mA）で、動かせない（[review/main_power_compare.md](review/main_power_compare.md) §3.2）
- **却下した案**: PT2314E を PD 12 V 側へ — 上の理由
- **状態**: 決定（ユーザー判断 2026-09-25。[review/decisions_audit_1.md](review/decisions_audit_1.md) の決定⑤）

### 3-5 娘のダンパのバルクは外す

- **決定**: 娘の ±15 V のバルク（ダンパ）を外す
- **理由**: 直列 R が 1 Ω 以上なら、どの角でも親→娘の伝達に共振の山が無い。バルクを残すと突入の電荷が増えて親の落ち込みを大きくするだけになる
- **根拠**: [NOW] L25／[review/stack_relay_power.md](review/stack_relay_power.md) §0.1-3・§4（1 Ω 以上で 144/144 組とも山なし、22 Ω・バルク無しで fsw 帯 −42.7 dB 以下）／[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 4-1（安定性の懸念なし）／[spice/stack_relay/](spice/stack_relay/)
- **前提・外れる条件**: ch LDO の CIN は 10 µF（DS の強い推奨、[pow] §2）。リセット時に電源接点が開いてから LDO が落ちるまでの余裕は小さくなる（§2-7）
- **却下した案**: 娘ごとに RC ダンパ（35〜45 µF・0.1〜0.2 Ω）— [NOW] L19–20 の旧方針。直列 22 Ω を入れた後は突入を増やすだけ（上の根拠）／親だけにバルク（直列 R なし）— 共振が娘の側に残り、親を盛っても直らない（[review/bulk_parent_sim.md](review/bulk_parent_sim.md) §0.2）
- **状態**: いったんの決め（[NOW] L19 の「残す」を L25 で差し替え）

### 3-6 親の +15 V/−15 V に +100 µF は任意

- **決定**: 親のバルク +100 µF は足場として置けるようにし、**要否は RS6 の突入を実測して決める**。実測は基板を起こす前に
- **理由**: 22 Ω・娘のバルク無しなら、RS6 が 300 mA で頭打ちでも親の最低は約 12.25 V で、PT2314E の 9 V は動かない。+100 µF が効くのは RS6 の OLP がヒカップ型か 300 mA 以下で頭打ちするときの保険だけ
- **根拠**: [NOW] L25／[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 2-5・2-6（L7809 の挙動モデル）・2-3（どの R でも RS6 の電流は 300 mA を超える）
- **前提・外れる条件**: RS6 の出力インピーダンスと電流制限の形は DS に無く、シミュレーションは〔仮定〕の上（[review/stack_relay_power.md](review/stack_relay_power.md) §8）
- **却下した案**: 必須にする（[review/stack_relay_power.md](review/stack_relay_power.md) §0.2 の推奨）— 査読で任意に格下げ
- **状態**: 要実測

### 3-7 ch LDO: CNR/SS は必須、後ろの容量は合計 22 µF 以下

- **決定**: ch の LDO には CNR/SS（10 nF）を付ける。LDO の出力側の容量は合計 22 µF 以下
- **理由**: CNR 無しだと立ち上がりが電流制限になり、娘のレールが 8.6〜12.6 V まで落ちる。DS 上は安定に必須ではないが、この構成では必須
- **根拠**: [NOW] L25／[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 4-4・2.4（自作の LDO 起動モデル）／[pow] §2（tSS = 1.4 × CNR[nF] ms）
- **前提・外れる条件**: **22 µF の上限は、レール良好のしきい値を 13.0 V に置いていたときの制約**。しきい値を約 10.5 V に下げた（§5-1）後は、100 µF でも立ち下がりのしきい値を割らないので制約は消える、と査読が支持している（[review/rail_detect.md](review/rail_detect.md) §0.2、[review/rail_detect_review.md](review/rail_detect_review.md) 要約 5）。NOW にはまだ上限が残っている → 整理は未決
- **却下した案**: —
- **状態**: いったんの決め（CNR/SS）／未決（容量の上限を残すか）

### 3-8 コイル電源は L7805C（PD 12 V からのリニア）

- **決定**: `+5V_COIL` は `BP5293-50` をやめて `L7805C`。入力側の PPTC は、コイルの最悪の同時通電（約 560 mA・30 ms）で切れない値にする
- **理由**: `+5V_COIL` は全娘へ配られ、娘の上でリレーの間を音声の近くに通る。BP5293 は 570 kHz の内部発振器を持ち、軽負荷で間欠動作に入る。聴取中はコイル電流が 0 なので、スイッチングの無いリニアで足りる
- **根拠**: [NOW] L25／[review/arch_zero_base.md](review/arch_zero_base.md) §0.1 #9／[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §0.1（BP5293 の発振器）・§6.1／[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 7-3（最悪 46.7 mA × 12 ＝ 560 mA、リニアでは入力電流＝出力電流で、今の PPTC 0.4 A 保持をパルスの間超える）
- **前提・外れる条件**: PPTC のトリップ曲線は未照合
- **却下した案**: BP5293 のまま — 発振器（上の理由）
- **状態**: いったんの決め

### 3-9 電源系統の独立は b-1、PD 入口に CMC の足場

- **決定**: 「電源系統の独立」は **b-1**（系統ごとに自分のレギュレータ、グランドは 1 点で結ぶ木）と読む。PD の受け端子の直後にコモンモードチョークの足場（0 Ω で素通し）を置く
- **理由**: ADC のグランドの付け替え（§4-4）で ADC の LDO の直流が `A_GND` を通らなくなり、b-1 が成り立つ形になった。ガルバニックに切る読み（b-2・b-3）が効くかは、PD 充電器が音に出ているかで決まり、誰も測っていない
- **根拠**: [NOW] L16／[review/rejected_review.md](review/rejected_review.md) §0（b-1/b-2 の定義）／[review/rejected_review_review.md](review/rejected_review_review.md) §2（b-3〜b-6）／[review/main_power_compare.md](review/main_power_compare.md) §4／[_review](review/main_power_compare_review.md) 1-7（「字義どおり」なのは ADC の LDO の直流についてだけ。AFE は ±15 V から取って `ADC_GND` へ帰る）
- **前提・外れる条件**: PD 充電器の A-B-A（§10）で差が高域なら CMC を実装、音声帯なら b-3（PD だけを絶縁）を検討。木が成り立つのはシャーシを 1 点で落とすときだけ（パネル部品の金属部・ジャックのスリーブ・PD モジュールのシェルがパネルに触れる閉路）（[review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) §3.2・§8-1）
- **却下した案**: b-2（一次と音声側を電気的に切る）— ADC の LDO を PD から取る決定と両立しない（帰り道が無くなる）（[review/rejected_review.md](review/rejected_review.md) §3.1-4）
- **状態**: いったんの決め（読み）／要実測（CMC を実装するか）

### 3-10 −15 V のプリロード抵抗は足場（DNP、3.0 kΩ）

- **決定**: DC-DC の −Vout と COM の足元に 3.0 kΩ の足場を置き、実装しない
- **理由**: RS6 のクロスレギュレーションは「25 % to 100 % load」で typ だけ規定。1 ch・typ・無音の −15 V は 26.2〜26.7 % で、INA1650 が min 側に振れるか軽い石を挿すと 25 % を割る（軽い端 23.6 %）。3.0 kΩ（5 mA、75 mW）を入れれば軽い端でも 26 % を超える
- **根拠**: [NOW] L16／[review/main_power_compare.md](review/main_power_compare.md) §3.4／[review/dcdc_2stage_review.md](review/dcdc_2stage_review.md) 要約 5・1.2
- **前提・外れる条件**: −15 V が軽いときに電圧がどちらへ振れるかは DS に無い。電圧の偏り自体は、±15 V に直結の負荷をどれも止めない（[review/main_power_compare.md](review/main_power_compare.md) §3.3）。実装は実測で決める（§10）
- **却下した案**: —
- **状態**: いったんの決め（足場）／要実測（実装）

### 3-11 ヘッドホンバッファの電源に RC の足場

- **決定**: ヘッドホンバッファ（OPA1652）の電源に自前の RC を入れられる足場を置く
- **理由**: 32 Ω を鳴らす信号電流（各レール平均 5〜25 mA、瞬時 16〜80 mA）は音声帯で変わる負荷として共有の ±15 V に載る。加えて 32 Ω に連続で出すとバッファの接合温度が定格を超える
- **根拠**: [NOW] L16／[review/main_power_compare.md](review/main_power_compare.md) §1.4・§4（b-5）／[review/main_power_compare_review.md](review/main_power_compare_review.md) 1-2・§3.5（連続正弦で約 0.82 W・+117 °C）
- **前提・外れる条件**: LINE 出力に HP と相関する成分が出るかは未測定（§10）。HP の帰りをバッファのデカップの GND へ寄せる配線と組にしないと効きが半分（同 1-7）
- **却下した案**: —
- **状態**: いったんの決め（足場）

---

## 4. ADC 経路

### 4-1 タップは今の位置（`AMP_SEL_L/R`、ポットの前）

- **決定**: 計測のタップは `AMP_SEL_L/R`（ch 選択の直後、DEST スイッチ・音量ポット・HP バッファの手前）のまま
- **理由**: ユーザーの判断
- **根拠**: [NOW] L12／[review/tap_facts.md](review/tap_facts.md) §1.1（v1 もポットの前で取っていた）
- **前提・外れる条件**: 本線に直接触るのは計測タップのバッファ（OPA1656 フォロワ）だけ。バス負荷は v2 と同じ
- **却下した案**: —
- **状態**: 決定（ユーザー判断 2026-09-25）

### 4-2 ADC 経路に絶対の品質は求めない。優先は本線を汚さないこと

- **決定**: ADC 経路は LCD のスペアナ・VU メーター・USB で Pico 経由の簡易分析ができれば足りる。**本線を汚さないことを優先**する
- **理由**: 装置は計測器ではない（§0-1）
- **根拠**: [NOW] L13・L33／参考値: ソケットの抜き差しで再現できる範囲は記録上 −106 dBc（H3 の差の検出限界、v1 仮配線、n=1）（[review/tap_facts.md](review/tap_facts.md) §4.1）
- **前提・外れる条件**: −106 dBc は「差の再現性」で、鎖の絶対歪みではない。v1 は鎖のベースライン −76 dBc のまま −106 の差を出した（[review/tap_compare_review.md](review/tap_compare_review.md) 2-2・2-3）
- **却下した案**: 分解能を上げること自体を目的にする — v2 [L4122](../AudioV2/DECISIONS.md)「そもそも」と同じ
- **状態**: 決定（ユーザー判断 2026-09-25）

### 4-3 結合は差動（INA1650 をタップのバッファの後ろ）、片側（今の形）に戻せる足場

- **決定**: タップのバッファの後ろに INA1650 を置き、− 入力を GND センス線へ、REF を `ADC_GND` へ。逆相を作る反転段は残し、その基準を `ADC_GND` へ移す。ジャンパ／0 Ω で今の片側（Q1）へ戻せる形にする
- **理由**: ch 側のグランドと計測側の `A_GND` の差は、今の片側では信号と直列に乗る（除去 0 dB）。差動なら DS の CMRR（85 dB min、±18 V 条件）で落ち、REF を `ADC_GND` に取れば ADC の電源・グランドの置き場が自由になる（§4-4 の付け替えの前提）
- **根拠**: [NOW] L12／[review/tap_compare.md](review/tap_compare.md) §2.2・[_review](review/tap_compare_review.md) §2.1（「43 dB」は別の Vg の値で、Q1 の ch↔MC の差は 0 dB）／[review/adc_gnd_retree.md](review/adc_gnd_retree.md) §2・[_review](review/adc_gnd_retree_review.md) §4／[tap] Q2-2（INA1650: CMRR 85/91 dB、IQ 10.5/12 mA、入力バッファ内蔵）
- **前提・外れる条件**: **その Vg が実際に効いているかは測っていない**。効いていなければ Q2 は保険で、実績があるのは Q1（v1 の同じ形で −106 を出した）だけ（[review/tap_compare_review.md](review/tap_compare_review.md) §3）。±15 V での CMRR の規定値は無い。GND を拾う点（センス点）と切り替えの形は**未決**
- **却下した案**: INA1620・SSM2141・SSM2143・AD8274・INA134/137・THAT1200 — 入力インピーダンスが低く両脚にバッファが要る、差動アンプとしての CMRR の規定が無い、個別高調波の規定が無い、など（[review/tap_compare.md](review/tap_compare.md) §2.2）／絶縁系の結合は §4-9
- **状態**: 決定（Q2・Q1 に戻せる足場: ユーザー判断 2026-09-25）／未決（センス点・切替の形。REF を `ADC_GND`・反転段の基準を `ADC_GND` へ、は提案で査読が支持したもの）

### 4-4 ADC の LDO は PD 12 V（主電源スイッチの後ろ）から。ADC のグランドの木を付け替える

- **決定**: 計測系の LDO（`+3V3_A` / `+5V_A`）は PD 12 V（ネット `PD_12V_SW`、主電源スイッチの後ろ）から取る。`ADC_GND`–`A_GND` の NetTie をやめ、**グランド選択の 1×3 ヘッダ**で Q2 は `ADC_GND` を `D_GND` 側の葉に、Q1 へ戻すときは `A_GND` 側へ結ぶ
- **理由**: RS6 で ADC を +15 V に載せると、1 ch・最悪の石・ADC max 積みで +15 V が 197.7 mA（定格の 98.9 %）で余裕が無い。付け替え後は ADC の直流の帰り（LDO 入力で typ 60.9 / max 86.9 mA）が `ADC_GND` → ヘッダ → `D_GND` → `PD_GND` と帰り、`A_GND` を通らない
- **根拠**: [NOW] L10／[review/adc_gnd_retree.md](review/adc_gnd_retree.md) §0.1・§3・[_review](review/adc_gnd_retree_review.md) §0・§3（骨格は覆らなかった）／[review/rejected_review.md](review/rejected_review.md) §3.1-1・[rejected_review_review.md](review/rejected_review_review.md) §5（98.9 % は「入らない」ではなく「余裕が無い」）／[scripts/rail_budget.py](scripts/rail_budget.py) `--adc-from-pd`
- **前提・外れる条件**: 1×3 ヘッダ＋シャント 1 個なら、Q1・Q2 を同時に結ぶ閉路は物理的に起きない（[review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) §3.1）。「木」はガルバニックな話で、DC-DC の絶縁容量の輪・`±15V_AFE` の R・筐体の閉路は別（同 C8）。Q1 では ADC の帰りが `A_GND` を横切る長さが PCB の置き方で決まる（同 C9）。PD 給電で電源断のたびに「±15 V はあるが ADC の電源が無い」窓が 15〜40 ms 開く（§4-6）
- **却下した案**:
  - ADC の LDO を +15 V のまま（v2 [L171](../AudioV2/DECISIONS.md)）— 上の理由（RS6 の余裕）
  - `ADC_GND` を `PD_GND` へ結ぶ — 木にはなるが I²S の帰りが 2 ホップになる（[review/adc_gnd_retree.md](review/adc_gnd_retree.md) §3.1）
  - ADC 枝の電源に絶縁 DC-DC（v2 [L1293](../AudioV2/DECISIONS.md)・[L2107](../AudioV2/DECISIONS.md)）— b-1 の読み（§3-9）では要らない。スイッチング源が 1 つ増える（[review/rejected_review.md](review/rejected_review.md) #2）
- **状態**: 決定（PD 12 V から・付け替えの方向: ユーザー判断 2026-09-25）

### 4-5 ADC の枝に PPTC を新設

- **決定**: PD 12 V から ADC の LDO へ行く枝に PPTC を置く
- **理由**: PD 本線（受け端子 → 主電源スイッチ → `PD_12V_SW`）には枝より手前のヒューズが無く、他の枝はそれぞれ自分の保護を持つ。ADC の枝だけが無保護になる。v2 の「戻さない」は LDO が +15 V（DC-DC の短絡保護の後ろ）にあることが前提だった
- **根拠**: [NOW] L10–11／[review/adc_gnd_retree.md](review/adc_gnd_retree.md) §6.1・[_review](review/adc_gnd_retree_review.md) §2・§7.4／v2 [L226「ADC 枝の PPTC は戻さない」](../AudioV2/DECISIONS.md)
- **前提・外れる条件**: 定格は PPTC の DS（温度ディレーティング）を取ってから（hold 0.25 A 級が候補、未照合）。LDO 前の直列 R はフォールト電流を受けるのでパルス定格のある品（[review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) §6.2）
- **却下した案**: `+5V_D` の枝（既存 PPTC の後ろ）から取る — PPTC は増えないが、ADC の枝の短絡で Pico も落ちる（同 §7.4）
- **状態**: いったんの決め

### 4-6 ADC 前の直列 47 Ω → 100 Ω（電源断ごとの窓は許す）

- **決定**: ADC を直接駆動するドライバと ADC 入力の間の直列抵抗を 47 Ω から 100 Ω にする。電源を切るたびに開く窓は許す
- **理由**: PD 給電では電源断のとき ADC の電源が ±15 V より先に落ち、その間（約 15〜40 ms）ドライバの出力が ADC 入力のクランプへ流れる。フルスケールで 14〜16 mA pk と PCM1804 の絶対最大 ±10 mA を超えるが、100 Ω なら 6.5 mA
- **根拠**: [NOW] L11／[review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) §7.1・§7.4（代償は ADC 入力 10 kΩ との分圧 −0.09 dB と DS の値からの逸脱）
- **前提・外れる条件**: この構成では 47 Ω はドライバの帰還ループの外にあるので電流を制限できる（DS の図はループの中）（同 C10）
- **却下した案**: ドライバを `+5V_A` の単電源にする — 構造で解けるが `+5V_A` の負荷と ADC の VCC への信号電流が増え、過剰（同 §7.4 (b)）／何もしない — 窓は「事故のときだけ」ではなく電源を切るたびに開く（同 (c)）
- **状態**: いったんの決め／未決: VCOM とドライバ +IN の間の 1 kΩ（逆向きの窓の保険。RS6 なら故障時だけの保険）（同 (d)）

### 4-7 `±15V_AFE` の直列は 22〜33 Ω

- **決定**: ADC 側のオペアンプ（INA1650・反転段・ドライバ）の ±15 V デカップを `ADC_GND` に揃え、その手前に各レール 22〜33 Ω の直列抵抗（`±15V_AFE`）
- **理由**: デカップを `ADC_GND` に置くと、±15 V のリップル電流が `ADC_GND` → `D_GND` → `A_GND` と渡り、その大きさはほぼ Vripple / R。4.7 Ω だと 265 kHz で最大 10〜21 mA p-p を `A_GND` の星点へ入れるが、22〜33 Ω なら 1.5〜4.5 mA p-p
- **根拠**: [NOW] L11／[review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) §6.1（表）・C3
- **前提・外れる条件**: 33 Ω で V+ が約 13.7 V まで下がっても、INA1650 の同相の上限（V+ − 2 V）はフルスケール 7.74 Vpk の上（同 1 表）。ADC の HF の電流（ドライバのキックバック）は `ADC_GND` の中で閉じる（[review/adc_gnd_retree.md](review/adc_gnd_retree.md) §4）
- **却下した案**: 4.7 Ω — 上の理由／フェライトビーズ — 265 kHz ではほとんど効かない（[review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) §6.1）
- **状態**: いったんの決め

### 4-8 INA1650 の RCOM は 0 Ω（1 MΩ に替えられる足場）

- **決定**: INA1650 の COM は 0 Ω で `ADC_GND` へ。1 MΩ に替えられるフットプリントにする
- **理由**: RCOM = 0 ならセンス線が切れても Q1 相当に落ちるだけで、センス線の電流は nA 級。1 MΩ だと断線で −9.5 dB になり、センス線に約 6 µA pk/ch の信号電流が出る
- **根拠**: [NOW] L11／[review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) §4・C1・C2・§10-6／[tap] Q2-2（20 Ω の不整合で 83.7 dB、RCOM 1 MΩ で 89.6 dB）
- **前提・外れる条件**: 源インピーダンスの不整合は 1 Ω 未満の見込みで、RCOM の差は小さい（同 1 表）
- **却下した案**: 1 MΩ（[review/adc_gnd_retree.md](review/adc_gnd_retree.md) の推奨）— 上の理由で仮置きは 0 Ω
- **状態**: いったんの決め（仮置き）

### 4-9 計測側の予備 12 V 入口は残し、主電源スイッチを迂回する旨を注記

- **決定**: 計測側の予備 12 V 入口とそのヒューズは残し、「ここから給電すると主電源スイッチを迂回する（受け端子から給電しているときはスイッチ後の 12 V が出ている端子になる）」と図に注記する
- **理由**: 予備入口は今の図ではスイッチ後の `PD_12V_SW` につながっている
- **根拠**: [NOW] L11／[review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) §2（副作用）・§10-7
- **前提・外れる条件**: 両方から同時に給電すると電源が並列になる（同 §2）
- **却下した案**: —
- **状態**: いったんの決め（仮置き）

### 4-10 却下した結合・絶縁の案（v2.1 でも採らない）

- **決定**: 計測タップの経路は、絶縁アンプ・信号トランス・デジタル絶縁・ADC の絶縁島のどれも採らない
- **理由**: どれも −106 dBc（差の検出）を良くする根拠が記録に無く、ADC の電源の置き場を先に決めてしまうか、ADC の隣に新しい高周波源を置く
- **根拠**: [review/tap_compare.md](review/tap_compare.md) §2.3〜§2.5・[_review](review/tap_compare_review.md) §2・§3／[review/rejected_review.md](review/rejected_review.md) #1・[_review](review/rejected_review_review.md) #1
- **前提・外れる条件**: b-2（ガルバニックに切る）を採るなら見直す（§3-9）
- **却下した案**:
  - 絶縁アンプ（ISO224B・AMC3330 ほか）— DS の THD は −84 dB（10 kHz）で 1 kHz 未満の規定が無い。ISO224 の雑音は DS の中で 3 倍食い違い、悪い方なら雑音だけで −106 を割る。内部の ΔΣ・搬送波・DC-DC が ADC の隣に来る（[review/tap_compare_review.md](review/tap_compare_review.md) 6-1・6-2）
  - ライン・トランス（JT-11P-1）— 1 kHz の「<0.001 %」は typ 列で、1320 Hz の H3 とその安定性は DS に無い。二次側にバッファが要り、寸法も不明（同 3-5・6-3）
  - デジタル絶縁（ISO7741 を I²S に）— −106 に効く筋が記録から立たず（「本命」の記録は ADC 自身の床の話）、ADC の電源を ±15 V 側に固定する。部品代ほぼゼロの比較相手（ADC 出力への直列抵抗）がある（同 5-4〜5-6、§3「別枠」）
  - ADC を絶縁した島（v2 [L290](../AudioV2/DECISIONS.md)）— 却下のまま。島が動かすのは測定床の実用律速より下の部分で、装置は計測器ではない（[review/rejected_review.md](review/rejected_review.md) #1）。RS6 で絶縁容量が下がっても「島の性能は DC-DC の絶縁容量で決まる」構図は残る（[review/decisions_audit_1_review.md](review/decisions_audit_1_review.md) 修正の要点 4）
  - PT2314E 境界の絶縁 I²C（`ADuM1250` 級、v2 [L2474](../AudioV2/DECISIONS.md)）— b-1 なら理由（`D_GND` はどのみち娘へ引く）は成り立ち、むしろ強まる（[review/decisions_audit_2_review.md](review/decisions_audit_2_review.md) 3.3）
  - USB アイソレータ（`ADuM3160`）— USB を抜いた A/B で床の差 2.9 dB（n=1）（[review/rejected_review_review.md](review/rejected_review_review.md) #10）
- **状態**: いったんの決め（ユーザーは Q2 を選んだ。ここの案を個別に却下した記録は無く、査読の順位と v2 からの却下による）

---

## 5. 監視と連動

### 5-1 レール検知はしきい値つき、しきい値は下げる

- **決定**: 娘の ±レールの検知はしきい値で行い、**立ち上がり 約 ±12 V（遅延つき、10〜20 ms）で音声 SET を許し、立ち下がり 約 ±10.5 V（即時）で音声を自動リセット**。+ と − の両方。検知の分圧は **0.1 %**、ただし他の公差・不良にも耐える作りにする
- **理由**: 立ち下がりのしきい値を約 10.5 V まで下げると、ch LDO の起動時の落ち込み（最悪 13.44 V）から離れて迷惑トリップしない。分圧 1 % だと立ち下がり帯の下端が約 10 V を割る
- **根拠**: [NOW] L25／[review/rail_detect.md](review/rail_detect.md) §0.2（0.1 % で帯 10.24〜10.79 V / 11.68〜12.22 V（+））／[review/rail_detect_review.md](review/rail_detect_review.md) 要約 3・§2（帯の重なりの判定は不要な条件、1 % の弱点は下端だけ）
- **前提・外れる条件**: 13.0 V のしきい値（[review/stack_relay_power.md](review/stack_relay_power.md) §0.2）は公差込みで窓の上端に張り付いていた（[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 3-7）。EN の保護（EN ≤ IN + 0.3 V）だけなら、しきい値を高く置く必要は DS 上は無い
- **却下した案**: 13.0 V — 上の理由
- **状態**: 決定（しきい値つき・下げる・0.1 %: ユーザー判断 2026-09-25）

### 5-2 レールは Pico が読む（共通の `MON_P`/`MON_N`、LM4040 で比率校正）

- **決定**: 各娘の分圧したレールをダイオード OR でスタック共通の `MON_P`/`MON_N` に載せ、Pico の ADC で読む。**ADC0 の `DEST_ADC` を解放**して LM4040-2.5 を読み、比率で校正する。しきい値・遅延・読みの妥当性の判定はファーム
- **理由**: 娘の部品が監視 IC 案の約半分で、しきい値をファームで変えられ、読みの妥当性（張り付き・片側だけ等）を見て誤「良」の多くを検出できる
- **根拠**: [NOW] L25／[review/rail_detect_review.md](review/rail_detect_review.md) §7・§8-1（(c) を第一候補）
- **前提・外れる条件**: RP2350 の ADC はオフセット・利得・INL の規定が無く、比率校正が前提。Pico の 3V3 の公差はどの DS にも無い。`DEST_ADC` は今は `D_GND` へのプルダウンだけで、ファームは無視している（[NOW] L208 旧記述）。Pico 2 の `AGND` の扱いは Pico 2 の DS で確かめる（リポジトリに無い）（同 §7.1・§10）
- **却下した案**:
  - (a) 娘ごとに窓型の監視 IC（TPS3701 ＋ TPS3808 ＋ LM4040）— 単一の不良（オープンドレインの配線の開放、基準側の抵抗の開放、LM4040 の短絡など）で誤「良」になる経路が 4 つ以上あり、TPS3808 の遅延は CT の公差込みで 9.1〜23.4 ms と 10〜20 ms に入らない。娘 1 枚で IC 約 10 個（[review/rail_detect_review.md](review/rail_detect_review.md) §3.2・§2-3・§1 表）
  - (b) Pico だけ（I²C 経由で切る）— 突然の断では EN が切れる前にレールが割れる（I²C の書き込み 0.29 ms ＋ 待ち 最大約 0.9 ms に対し 0.20 ms）。ファームが止まると何も守られない（同 §7.4・§7.5）
  - ディスクリート（ツェナー＋トランジスタ）だけで精度の層を作る — ツェナーの公差で下端 10 V を守れない（[review/rail_detect.md](review/rail_detect.md) §2.2）
- **状態**: いったんの決め

### 5-3 `RAIL_OK` を Pico から直接（Pico が High を出している間だけ「良」）

- **決定**: Pico の空き GPIO から直接 `RAIL_OK` をスタックへ出す。**Pico が能動的に High を出している間だけ「良」**（外付けプルダウン）。娘の上で EN の許可と音声 SET のゲートに AND し、立ち下がりで音声リレーをリセット。Pico のリセット・停止で全段の音声がリセットされる
- **理由**: I²C（100 kbit/s・共用）経由では突然の断に間に合わない。直結の GPIO なら EN が 0.1〜0.2 ms で切れる。既定が「不良」なのでフェイルセーフの向き
- **根拠**: [NOW] L25／[review/rail_detect_review.md](review/rail_detect_review.md) §7.4・§7.5・§9 R3
- **前提・外れる条件**: ファームがハングして High を出し続ける形は残る → §5-4 の後ろ盾で塞ぐ。BOOTSEL・デバッガの停止・起動中はウォッチドッグも助けない（同 §7.5）
- **却下した案**: 娘がオープンドレインで引き下げる PG 線 — 電源の無い娘が線を放すと既定が「良」になる向き（[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6.3-3）
- **状態**: いったんの決め

### 5-4 精度の要らない後ろ盾（B1・B2）

- **決定**: **B1**: 音声 SET のコイル電源を、娘の ±レールがおおむねある（約 ±7 V を越える）ときだけ ON になる PMOS 越しにする（ツェナー＋トランジスタ）。どこが開放しても SET 不可に倒れる。RESET のコイル電源は常時の `+5V_COIL` のまま。**B2**: その「レールがある」信号の立ち下がりでもリセットの単安定を撃つ
- **理由**: 精度の層（§5-2）が誤「良」で固まっても、電源の無い娘の音声がバスにつながる形をハードで消せる。AZ850P2 は SET と RESET のコイルの＋端子が別ピンなので、SET 側だけをゲートできる
- **根拠**: [NOW] L25／[review/rail_detect_review.md](review/rail_detect_review.md) §3.3・§8-2／[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6.3-6
- **前提・外れる条件**: 部品の DS は未収集。TBD62083A のクランプの COMMON をどちらへ繋ぐかは要整理（同上）。B1 は §2-6（D10）の理由そのもの
- **却下した案**: —
- **状態**: いったんの決め

### 5-5 レールが落ちたら音声を自動リセット、EN も切る

- **決定**: レールが落ちたら音声リレーをハードで自動リセットする。同じ信号で ch の LDO の EN も切る
- **理由**: 接点の瞬断や衝撃で電源が切れても、音声がバスにつながったまま・ミュートも掛かっていない状態が残る。EN を切らないと EN が IN を超えうる（§2-9）
- **根拠**: [NOW] L25／[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 6-3（自動リセットの経路が無いという指摘）／[review/rail_detect.md](review/rail_detect.md) §0.3／[review/rail_detect_review.md](review/rail_detect_review.md) §8-1
- **前提・外れる条件**: 律速はリレーの復帰時間（AZ850 は 1 ms typ、max は DS に無い）。SET と RESET のコイル電流の重なりは µs ではなく sub-ms〜ms になりうるが、リセットパルスが長いので最後はリセットで終わる（[review/rail_detect_review.md](review/rail_detect_review.md) 2-4）。電源リレーまで自動で切るか（D5）は未決
- **却下した案**: —
- **状態**: いったんの決め

### 5-6 TBD62083A は 5 V 振幅で駆動（`+5V_COIL` の AHCT を 1 段）

- **決定**: コイルドライバ TBD62083A の入力を、`+5V_COIL` で動く AHCT 系を 1 段通して 5 V 振幅にする
- **理由**: TBD62083A の出力電圧（VDS）は VIN = 5 V の条件でしか規定されていない。3.3 V 駆動で保証されるのは「100 mA で VOUT = 2 V」だけで、コイル端の電圧が感動電圧に届く保証が無い。自動リセットという安全機能がこの保証外に乗っていた
- **根拠**: [NOW] L25／[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §0.2-5／[review/rail_detect_review.md](review/rail_detect_review.md) §5-1・§8-3／[sw] §3（TBD62083A）
- **前提・外れる条件**: AHCT の DS は未収集。LVC を 5 V で動かすと 3.3 V の信号を受けられない（同 §5-1）。TBD62083A は VCC ピンが無く入力電圧だけで動くので、電源の無い娘にもリセットが届く（[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6.1）
- **却下した案**: 3.3 V で直接駆動 — 上の理由（v1/v2 で動いた実績はありうるが DS の保証ではない）
- **状態**: いったんの決め

---

## 6. ファームの責務

ハードが保証することと、ファームが守ることを分けて置く。ハードの後ろ盾は「ファームが間違えたときに壊さない・つながない」ためのもので、手順そのものはファームが持つ。

### 6-1 ハードが保証すること（ファームに依らない）

| 何を | どうやって | 項目 |
|---|---|---|
| レールの無い娘は音声 SET できない | B1（音声 SET のコイル電源をレールでゲート） | §5-4 |
| レールが落ちたら音声リセット、EN 切り | B2 と `RAIL_OK` の立ち下がりで単安定 → RESET コイル。EN の許可にも AND | §5-4・§5-5 |
| Pico が止まったら全段の音声リセット | `RAIL_OK` は Pico が High を出している間だけ良 | §5-3 |
| 電源の無い娘にもリセットが届く | コイル電源は常時系統、TBD62083A は VCC 無し | §5-6 |
| EN が LDO の IN を超えない | EN の論理を娘の切られたレールから | §2-9 |
| 娘の中で同時に ON は 1 ch まで、既定 OFF | デコーダ | §2-9 |
| 切ったノードが浮かない | NC 抵抗 → GND、`TONE` バスに 100 kΩ | §2-3・§2-11 |
| 極間短絡で ±15 V を直結しない | 22 Ω を NO 側、溶断型 | §2-4 |

### 6-2 ファームが守ること

- **厳密に 1 ch**: 全 OFF → 1 ch ON。温めておく ch は作らない（§1-2）
- **切替の手順（娘をまたぐとき）**: ミュート → **全リセット（全娘の音声リレーと電源リレー。音声が先・電源が後、例: ARST → 20 ms → PRST）** → 選んだ娘の電源 SET → レール良好（立ち上がりのしきい値 ＋ 遅延 10〜20 ms）→ ch 選択 → 整定待ち → **共通の音声 SET** → ミュート解除（[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6.3-9、[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 6-1）
- **D10 の規則**: 音声 SET は、上の「全リセット → 電源 SET → レール良好 → 共通の音声 SET」の 1 つの手順の中でだけ出す。それ以外で音声 SET を出さない（§2-6。ユーザー判断 2026-09-25）
- **同じ娘の中で ch を変えるとき**: ミュート → ch を全 OFF → 番地 → ch を ON（TMUX と LDO の EN が同時に切り替わる）→ LDO の立ち上がり（CNR 10 nF で 14 ms）＋整定待ち → ミュート解除。境目のリレーは動かさない（[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6.3-9）
- **パルス幅**: コイルのパルスは 20 ms 以上（Panasonic の「セット・リセット時間の 5 倍以上」、AZ850 の typ 2 ms の 10 倍）。SET と RESET のコイルに同時に電圧を加えない（[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 8-1、[bnd] §3.3 TQ）
- **EN を上げる条件**: ±15 V があることを確かめてから（主電源スイッチ OFF で Pico が USB だけで動いているときに EN を上げない）（§2-9、[review/main_power_compare_review.md](review/main_power_compare_review.md) 1-6）
- **レール監視**: `MON_P`/`MON_N` を読み、LM4040 を ADC0 で読んで比率校正。しきい値（約 ±12 V / 約 ±10.5 V）と遅延をファームで持つ。張り付き・片側だけなどの妥当性を見る。`RAIL_OK` は能動的に High を出し、異常では落とす（§5-2・§5-3）
- **迷惑トリップを無限に再試行しない**（誤「不良」で EN 切り → 回復 → 良 → EN → 落ち込み…を繰り返しうる）（[review/rail_detect_review.md](review/rail_detect_review.md) §3.1）
- **電源投入時**: 全リセットから始める（ラッチングリレーは停電前・衝撃の状態を保持しうる）。PT2314E には電源投入後 50 ms は I²C を送らない（v2 [L2592](../AudioV2/DECISIONS.md)、[sw] §5）。PT2314E の I²C は 100 kbit/s（3.3 V ロジック × VDD 9 V で Standard）
- **待ち時間の目安**: ch の入力結合の整定は 5τ で 0.5 s 級、ミュートの長さは 2τ（約 1 s）か 3τ（1.5 s）で未決（§2-10）

---

## 7. v2 から引き継ぐもの

本文は v2 のまま。行番号は [../AudioV2/DECISIONS.md](../AudioV2/DECISIONS.md)。判定は棚卸し（[audit_1](review/decisions_audit_1.md)・[_review](review/decisions_audit_1_review.md)／[audit_2](review/decisions_audit_2.md)・[_review](review/decisions_audit_2_review.md)／[audit_3](review/decisions_audit_3.md)・[_review](review/decisions_audit_3_review.md)）の「維持」。

**UI・操作（v2.1 でも変わらない）**
- ENC×3（CH / BASS / TREBLE）、回して候補・押して確定 — L25、L2137、L2648。確定で入るのが入力切替と LDO の EN になるだけ
- 音量は Amp の後の手回し A50k デュアル ×2、IC にしない — L2334（§2 確定）、L2380〜2413（PGA2310／digipot の見送り。理由は UI・コスト・SNR で v2.1 でも成立）
- 出力段: PHONE はバッファ、LINE は直結、ゲインなし／バッファも DIP-8 ソケット — L1077、L1123、L1167（OPA1652）
- DEST は機械スイッチ、リレーは要らない — L93
- トーンは PT2314E、`DGND` はチップの足元で `A_GND` へ、I²C 境界は `BSS138` のレベルシフタ — L2415、L2426、L2444、L2499（`P82B96`・`PCA9306` 等の見送りも成立）
- HP 固定パッドは廃止、DNP で後付け — L2180（ソケット ±12 V でむしろ当時の条件どおり）

**計測（v2.1 の Q1 の土台）**
- タップの「+」側バッファを戻した — L354
- 前段入力抵抗 6.19k（PT2314E 経路について）— L404、L417
- `MCLK_SENSE` を落とした — L448

**部品選定の理屈**
- 2.2 µF フィルムは公差ではなく耐圧で選ぶ — L4374〜4411
- 受動部品は回路が固まってから DigiKey API でまとめて選ぶ — L4302
- DIP-28 ソケットは 0.300"、板バネ型 — L4211、L4243
- 却下のまま: 7806（6 V の壁）L1381、Aimtec L1622、CCG／PYBE10 L1632、`T3.15 A` L1877、`NSD10-12D12` L1609、Mornsun L1674（NFND）

**回路の原則**
- 電源を切るなら出力も切る（ESD でレールにつながる）— L2871
- 電源を切るなら入力も切る（入力クランプ）— L3986、L3999
- アナログスイッチ自身は常時通電 — L4048
- 出力側スイッチは 47 Ω の後ろ — L4720
- ブレーク・ビフォア・メイクはファームで — L4724
- グランドの結合は木（2 箇所目は閉路）、同居は結合ではない — L3433、L3449、L3463、L3478（査読で「却下の再検討」から維持へ直した）
- シャーシアースは 1 点 — L3415
- I²S の帰り・クロック結合の注意 — L3213、L3369、L3384、L3396
- 基板間はワイヤでなくヘッダのスタック、DIP ソケットに手が届くこと — L3159、L3177
- ヘッダの電流・接触抵抗・挿抜寿命は制約にならない — L3810〜3858

**道具・手順の警告**
- 同じ仕様でも絶縁容量が桁で違う、サフィックス違いに注意 — L502
- レール容量は `sch_facts.py rails` で毎回数え直す（数値を書かない）— L1464、L1592
- Recom の表の Fsw 欄で比べない（見出しは full load）— L1573
- 同じ前提を渡した並列の一致は独立の裏付けにならない、探索範囲の指定が盲点になる — L1518、L1725
- 「USB で 23 dB」を DC-DC 不要の論拠にしない（再現は 2.9 dB）— L1510
- 参照番号は「最大値＋1」で採らない、PPTC 下流の PWR_FLAG — L1840
- 買ったことを採用の根拠にしない — L4333、L4358
- TMUX7612 の DS は表を取り違えやすい（±15 V 表と ±20 V 表、平坦度の条件は VS ±10 V）— L4694

---

## 8. v2.1 では成り立たない v2 の決定

| v2 の決定（リンク） | 何が崩すか | v2.1 の扱い |
|---|---|---|
| [L28](../AudioV2/DECISIONS.md) 決定ログ「切替方式」: 電源は常時給電、入力はブロードキャスト | 選んだ ch だけ電源と入力を生かす | §1-1、§1-2、§2-8 |
| [L2861](../AudioV2/DECISIONS.md) §11.1「電源は常時給電」、[L4660](../AudioV2/DECISIONS.md)「なぜ電源を切らないか」 | 同上。LDO の EN で切るので接点を通らない | §2-8 |
| [L17](../AudioV2/DECISIONS.md)・[L37](../AudioV2/DECISIONS.md)「ラッチングリレーで 1 系統だけ有効（電源もリレー）」 | 考え方は戻る。手段が「娘ごとの電源リレー（1 段目）＋ ch ごとの LDO の EN（2 段目）」に変わる（査読で「無効」から「前提変更」へ） | §1-3、§2-1、§2-8 |
| [L3601](../AudioV2/DECISIONS.md) B0「入力ブロードキャスト＋出力のみ MUX」 | 入力も切る | §2-8 |
| [L3569](../AudioV2/DECISIONS.md) B1「入力 220 kΩ を撤去」 | 撤去の主な理由（入力スイッチが無い）が消えた | `TONE` バスに 100 kΩ（§2-11）。ch 側の 220 kΩ を戻すかは未決（§10） |
| [L4462](../AudioV2/DECISIONS.md)・[L4502](../AudioV2/DECISIONS.md) リレー版とスイッチ版を別 PCB 2 種 | 娘は 1 種類、聴き比べはしない | §1-4 |
| [L3869](../AudioV2/DECISIONS.md) 娘は横並び・直結、[L3884](../AudioV2/DECISIONS.md) 縦積み B は番地衝突で却下 | 番地は v2 で娘のジャンパに移り、却下理由が消えた | 縦積みを採用（§2-1、§2-5）。DIP ソケットへ手が届くこと（L3177）は条件として残る |
| [L249](../AudioV2/DECISIONS.md)・[L1539](../AudioV2/DECISIONS.md) `REC20K-2415DZ` | 1 ch 運転で −15 V が DS の範囲から最も遠い、絶縁容量 2000 pF | RS6-1215D（§3-1） |
| [L138](../AudioV2/DECISIONS.md)「ソケット 1 個あたり何 mA」（10 個常時通電） | 常時負荷は 1 ch 分。律速は ch の LDO ではなく RS6（査読で訂正） | §3-1 |
| [L468](../AudioV2/DECISIONS.md)「低 Ciso 品は 6 W 上限でこの電力帯に代替が無い」 | 1 ch 通電で電力帯そのものが下がった | RS6 がその電力帯の石（§3-1） |
| [L1014](../AudioV2/DECISIONS.md)「AudioV2 は v1 の軽負荷問題を継承しない」 | v2.1 は選んだ ch だけ給電で、軽負荷を継承する | 合計の負荷率で選ぶ（§3-1）、−15 V のプリロード足場（§3-10） |
| [L171](../AudioV2/DECISIONS.md)「ADC の LDO は `+15V` 直結」 | RS6 の +15 V に余裕が無い | PD 12 V から（§4-4） |
| [L198](../AudioV2/DECISIONS.md)「`A_GND`–`D_GND` の NetTie」の木 | ADC の帰りが PD 側になる | グランドの木の付け替え（§4-4） |
| [L226](../AudioV2/DECISIONS.md)「ADC 枝の PPTC は戻さない」 | 前提（LDO が DC-DC の短絡保護の後ろ）が消えた | PPTC 新設（§4-5） |
| [L290](../AudioV2/DECISIONS.md)【却下】ADC の絶縁島 | 理由②（絶縁容量）は弱まるが、①③と費用対効果は成立 | **却下のまま**（§4-10） |
| [L2380](../AudioV2/DECISIONS.md)〜[L2413](../AudioV2/DECISIONS.md) PGA2310／digipot の見送り | 5 つの理由とも成立（±5 V 問題は振幅の上限の話で、専用電源でも解けない） | **却下のまま**（§7） |
| [L3965](../AudioV2/DECISIONS.md)〜[L4089](../AudioV2/DECISIONS.md)「選んでいない ch の電源を切るのは 16 ch 以上のときだけ」 | 構造の反対理由（ESD・入力クランプ）は入出力のスイッチで消えた | **採用**（§1-1）。熱の揃い・整定はファームの問題（§1-2） |
| [L3955](../AudioV2/DECISIONS.md)・[L4076](../AudioV2/DECISIONS.md) 6ch×2・電源カットなし | 入力 TMUX が ch ごとに要る、RS6 の ±200 mA を超える | 採らない |
| [L4569](../AudioV2/DECISIONS.md) 経路ごとの振幅上限 | 精密／フルレンジ DIRECT は要件外（通常経路の行は残る） | §1-5 |
| [L700](../AudioV2/DECISIONS.md)〜[L916](../AudioV2/DECISIONS.md) ±15 V か ±12 V か（未決） | 生の ±15 V（TMUX・PT2314E・計測）＋ ch の LDO で ±12 V に決着 | §3-3 |
| [L4345](../AudioV2/DECISIONS.md)「`+9V` 三端子を使わなくなる理由」 | レールは ±15 V のまま、PT2314E は L7809 のまま | §3-4 |
| [L4630](../AudioV2/DECISIONS.md) TMUX4821 の却下理由「OFF 漏れ」 | OFF 側に信号が無いので不成立。2 mm QFN の理由は成立 | 却下のまま（TMUX7612 を選択） |
| [L3492](../AudioV2/DECISIONS.md)「`ISO7741`＋ADC の電源を二次側へ」 | ADC の LDO を PD（一次側）から取る決定と逆向き。09-07 の島の却下理由 ①③ も残る | 採らない（§3-9、§4-10） |
| [L2329](../AudioV2/DECISIONS.md) B2-exp（娘の MCP23017）、[L4358](../AudioV2/DECISIONS.md) | 娘のロジックを親からのレベル線だけにする案が候補 | 未決（§10） |
| [L1742](../AudioV2/DECISIONS.md) 2026-08-31 の ±12 V の記録 | ソケットは ±12 V に戻るので、最大出力の低下はソケット側でまた当たる | §3-3 の前提 |

---

## 9. 訂正された記録

査読・照合で直った記録。v2 の本文や過去の査読を読むときは、この表の読みを使う。

| # | 誤っていた記録 | 正しい読み | 出典 |
|---|---|---|---|
| 1 | 計測側の予備 12 V 入口のヒューズ（記録上 `F1601`）が箱全体の上流・マスターヒューズで、ADC の LDO の上流にある（`rejected_review.md` #7、`rejected_review_review.md` #7、`decisions_audit_1.md`・`_review.md`、NOW の旧記述） | **誤り。** そのヒューズは予備入口（記録上 `J1602`）と `PD_12V_SW` の間だけにある。PD 本線（受け端子 → 主電源スイッチ → `PD_12V_SW`）には枝より手前のヒューズが無い。PPTC を戻す結論は、上流が無保護という別の理由でむしろ強まる | [review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) §2 |
| 2 | RS6 の「200 kHz」は軽負荷でも 200 kHz 以上を DS が保証 | 条件欄「0-100% load」・**Min 列に 1 値だけ**。試験条件も、バースト（間欠）の包絡の有無も書いていない。「DS の字句が候補中で最も強い」が正確 | [pow] §1、[review/main_power_compare_review.md](review/main_power_compare_review.md) 1-3 |
| 3 | RS6 の「無負荷入力電流 55 mA」 | DS の字句は "Quiescent Current"、**Max 列**、条件欄の印字は "2VDC"（12 V の位置）。負荷の条件は書かれていない | [review/ds_errata_review.md](review/ds_errata_review.md) P1 |
| 4 | RS6 の UVLO ON 9 V は REC10K と同じ比 | RS6 の 9 V は **Typ**（REC10K の 9 V は max だった） | [review/decisions_audit_1_review.md](review/decisions_audit_1_review.md) L655 |
| 5 | L7809 の規定入力範囲の下限 11.5 V | **入力範囲の規定項目は無い。** 11.5 V は出力電圧 8.55〜9.45 V を保証する試験条件の下限。実際に出力が落ちるのはドロップアウト（約 1.5〜1.6 V、目読み）＋入口の PPTC の降下を割ったとき | [pow] §5（L7809C）、[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 2-4 |
| 6 | TMUX7612 の膝は「レールから約 4.2 V 内側」 | DS 本文は "roughly 5 V"、Figure 5-4 の目読みで ±15 V の正側は約 +10.6 V。幅は「どこを膝と呼ぶか」の定義の差 | [review/decisions_audit_1_review.md](review/decisions_audit_1_review.md) 数値の検証、[sw] §1 |
| 7 | 「1 ch 運転の律速は ch ごとの LDO（150 mA）」 | 律速は RS6（+15 V の残り約 109 mA < 150 mA） | [review/decisions_audit_1_review.md](review/decisions_audit_1_review.md) 修正の要点 2 |
| 8 | 「8 ch 故障で OLP の 150 % 領域に入る」／「136〜149 % の帯だけ保護が働かない」 | 8 ch の max 積みの全域で、+15 V は定格の 136〜161 % のまま流れ続けうる（OLP が出力ごとか合計かは DS に無い） | [review/rejected_review_review.md](review/rejected_review_review.md) #5、[review/main_power_compare_review.md](review/main_power_compare_review.md) 1-5 |
| 9 | ch LDO のソフトスタート電流「8.6 µA」 | **8.6 mA** | [review/main_power_compare_review.md](review/main_power_compare_review.md) 1-4 |
| 10 | 「1 ch で −15 V は RS6 の約 21 %」 | INA1650 を足す前の数字。足すと typ・無音で約 26.7 % | [review/main_power_compare.md](review/main_power_compare.md) §1.5 |
| 11 | 記録上のグランド差の除去「約 43 dB」を Q1 の値として Q2 と比べる | 43 dB は `A_GND`↔`ADC_GND` の差で、しかも 47 Ω 付きの構成の値。Q2 が落とす ch 側↔計測側の差は、Q1 では 0 dB | [review/tap_compare_review.md](review/tap_compare_review.md) 4-4 |
| 12 | `ADC_BCK` は 6.144 MHz（v2 L3375） | マスター動作で BCK は 64 fS ＝ 3.072 MHz。6.144 MHz は変調器の 128 fS | [review/tap_compare.md](review/tap_compare.md) §2.4、[_review](review/tap_compare_review.md) 1-4 |
| 13 | JT-11P-1 の「1 kHz <0.001 %」は上限 | **TYPICAL 列**。+14 dBu・+20 dBu の曲線もある | [review/tap_compare_review.md](review/tap_compare_review.md) 3-5 |
| 14 | ISO224B の雑音は 3 µV/√Hz で −106 を割らない | 同じ DS の出力雑音から出すと入力換算約 9 µV/√Hz（3 倍の食い違い）。悪い方なら雑音だけで −106 を割る | [review/tap_compare_review.md](review/tap_compare_review.md) 6-2 |
| 15 | 「今の図では ±15 V と ADC の電源は一緒に来る」 | LT1763 は CBYP 10 nF で起動に 15 ms かかり、今の図でも投入時は ADC が遅れる。PD 給電で新しく開くのは**電源断**の窓 | [review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) C5 |
| 16 | 「RCOM 1 MΩ ならセンス線が切れても Q1 相当」「センス線は nA 級」 | RCOM 1 MΩ では断線で −9.5 dB、センス線に約 6.2 µA pk/ch。Q1 相当・nA は RCOM = 0 のとき | [review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) C1・C2 |
| 17 | 「`±15V_AFE` の RC で電流を絞る」「LDO 前の RC でリップルを PD 側で閉じる」 | 前者の 35 dB は電圧の減衰で、渡る電流は ≈ Vripple/R。後者は LDO 足元の MLCC のほうが低インピーダンスで、大半が `ADC_GND` を回る | [review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) C3・C4 |
| 18 | 直列 4.7〜10 Ω は「接点の DS の定格を超える」 | DS の 1 A は抵抗負荷の開閉電流で、メイク時の減衰する突入を規定していない。「DS の保証の外。1 A を代理の物差しにすると超える」 | [review/stack_relay_power_review.md](review/stack_relay_power_review.md) 1-3 |
| 19 | 「24 mA での LDO の VDO は DS に無い」「ヘッドルーム ≥ 1 V が規定」 | TPS7A49・TPS7A30 とも VDO の典型曲線がある（24 mA で約 0.12〜0.2 V）。≥ 1 V は設計例の "for optimal performance" の目安 | [review/stack_relay_power_review.md](review/stack_relay_power_review.md) 3-2・3-3 |
| 20 | 「音声 SET を共通 1 本にすれば 2×10 に収まる」「コイルの最悪は 480 mA」 | 24 − 3 ＝ 21 本で 2×10 には入らない。コイルの最悪は L7805C の上限 5.25 V・コイル −10 % で 46.7 mA × 12 ＝ 560 mA | [review/stack_relay_power_review.md](review/stack_relay_power_review.md) 7-2・7-3 |
| 21 | 「SET/RESET の同時通電は 1 µs 未満」「TPS3808 で 10〜20 ms の遅延」 | 前者はドライバ入力の話で、コイル電流の重なりは L/R で決まり DS から上限が出ない。後者は CT の公差込みで 9.1〜23.4 ms | [review/rail_detect_review.md](review/rail_detect_review.md) §2-3・§2-4 |
| 22 | `DEST_ADC`（ADC0）は使用中 | 回路図では 10 kΩ で `D_GND` へ引いてあるだけで、NOW でもファームは無視。実質空いている | [review/rail_detect_review.md](review/rail_detect_review.md) §7.1 |
| 23 | `ADC_nRST` は Pico が駆動する | 監視 IC の出力とプルアップだけ。Pico が叩くのは `ADC_nMR` | [review/rejected_review_review.md](review/rejected_review_review.md) N3 |
| 24 | OPA1652・OPA1612・NJM5532 に入力保護ダイオードの記述は無い（ds_facts の旧版） | **ある**（back-to-back、入力電流 ≤ 10 mA／NJM5532 は投入時の入力ダイオードと V+ 開放時の注意）。ch ごとに電源を落とす構成に直接効く | [review/ds_errata_review.md](review/ds_errata_review.md) O1〜O3 |
| 25 | PT2314 の入力抵抗 30/40/50 kΩ を PT2314E の DS と食い違うとした（監査） | 30/40/50 は旧 PT2314 の音量入力 `RIV` として正しい。PT2314E で比べる行は `RIN`（VOL = 0 dB）13/20/27 kΩ | [review/decisions_audit_3_review.md](review/decisions_audit_3_review.md) 覆した点 2 |
| 26 | 「PT2314 のクリップ 2〜2.5 Vrms」は誤記 | 旧 PT2314 の DS の値。PT2314E では VOMAX min 2.3 / typ 2.6 Vrms（部品を替えたことによるずれ） | [review/decisions_audit_3_review.md](review/decisions_audit_3_review.md) 覆した点 3 |
| 27 | 「KiCad 標準に W5.0 は無い（W4.5 が最大）」、フットプリントの幅の問題は解決済み | W7.2 も汎用の W5.0 も標準にある。AmpChannel は差し替え済みだが、PT2314E まわりの 2.2 µF フィルムの FP は W2.5 のまま | [review/decisions_audit_3_review.md](review/decisions_audit_3_review.md) 覆した点 4 |
| 28 | 参考製品の「約 1 秒のミュート・音声回路を GND に落とす」は PDF で確認できない（`arch_zero_base_review.md` §6） | PDF p2 のテキスト層に原文がある（PyMuPDF で抽出して確認）: 「1 秒程度の無音期間（音声回路を安全な GND 信号と接続）」 | [datasheets/reference/Kyohritsu_KP-HAMP61_manual.pdf](datasheets/reference/Kyohritsu_KP-HAMP61_manual.pdf) p2 |
| 29 | ヘッドホンバッファの「最大」「上限」の負荷の行を定常として扱う | 32 Ω に連続で出すと接合温度が定格を超えるので定常にはならない（DC-DC を大きめに見る上限としてだけ使う） | [review/main_power_compare_review.md](review/main_power_compare_review.md) 1-2 |
| 30 | TPS7A30 の電流定格 200 mA | 推奨動作条件は 200 mA だが、同じ DS の 8.1 Overview は 150 mA（DS 内の食い違い） | [review/decisions_audit_1_review.md](review/decisions_audit_1_review.md) 数値の検証 |

---

## 10. 未決・要実測

### 10-1 実測するもの（安い順・基板を起こす前に要るものを先に）

| # | 何を | 決まるもの | 出典 |
|---|---|---|---|
| M1 | **RS6 の突入**（娘の電源リレーのメイクでどこまで出すか）と **OLP の形**（出力ごとか合計か、定電流かヒカップか） | 親 +100 µF の要否（§3-6）、22 Ω での親の落ち込み、極間短絡時の 22 Ω の電力（§2-4）。**基板を起こす前に** | [NOW] L25、[review/stack_relay_power.md](review/stack_relay_power.md) §8、[review/rail_detect_review.md](review/rail_detect_review.md) §10-5 |
| M2 | **RS6 の軽負荷での −15 V**（1 ch・無音・軽い石）の電圧と波形、周波数（バーストの有無） | プリロードの実装（§3-10） | [review/rejected_review.md](review/rejected_review.md) §4 D4、[review/main_power_compare_review.md](review/main_power_compare_review.md) §4-1 |
| M3 | **PD 充電器 ↔ 12 V のリニア電源／電池の A-B-A（最低 2 回）**、音声出力の床とスパーを外の機材で。差の周波数 | CMC の実装（§3-9）、b-3 の要否 | [review/rejected_review_review.md](review/rejected_review_review.md) §6、[review/main_power_compare.md](review/main_power_compare.md) §4 |
| M4 | **Pico の 3V3 の公差**（Pico 2 基板の DS がリポジトリに無い） | 比率校正の前提、監視のしきい値の誤差 | [review/rail_detect.md](review/rail_detect.md) §0.5 D8、[review/rail_detect_review.md](review/rail_detect_review.md) §10-1 |
| M5 | **AZ850 のコイルのインダクタンスと最大リセット時間** | SET/RESET の重なり、自動リセットの時間予算 | [review/rail_detect_review.md](review/rail_detect_review.md) §10-3 |
| M6 | ADC のデジタル動作が音声出力に漏れているか（I²S の 3 本を Pico 側で外す A-B-A。**リセット保持の形は使わない**: 1.37 s でパワーダウンに入る） | デジタル絶縁・直列抵抗の要否 | [review/tap_compare_review.md](review/tap_compare_review.md) 6-6・§4-D |
| M7 | ch 側グランドと計測側 `A_GND` の差（タップ入力の短絡点を変えた無信号キャプチャ 2 通り） | Q2 が保険か実益か（§4-3）。v1 での負の結果だけが強い | [review/tap_compare_review.md](review/tap_compare_review.md) 6-5 |
| M8 | HP 32 Ω を鳴らす／外すで LINE 出力の A-B-A、TMUX・L7809 のピンの ±15 V の AC | HP バッファの RC の実装（§3-11） | [review/main_power_compare.md](review/main_power_compare.md) §4 (b-5) |
| M9 | 石の熱の整定（通電してから何秒で H3・音が落ち着くか） | 切り替えてから聴くまでの待ち（§1-2） | [review/rejected_review_review.md](review/rejected_review_review.md) §6 U2 |
| M10 | ADC 系の実電流（電流計を直列に 1 回） | ADC 枝の PPTC・LDO 前の R の定格 | [review/rejected_review_review.md](review/rejected_review_review.md) §6 |
| M11 | 容量負荷のメイク回数試験（22 Ω・AZ850） | 電源用リレーの品種（§2-2） | [review/stack_relay_power_review.md](review/stack_relay_power_review.md) 1-4 |
| M12 | ch を ON してからの出力 DC の整定 | ミュートの長さ（§2-10） | [review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6.4 M3 |

DS を取るもの（リポジトリに無い）: 22 Ω ヒューズ抵抗の品番（単発パルス曲線）、PPTC（RXEF 系）の温度別 hold 電流、AHCT 系、PMOS・ツェナー（B1）、RB160M-30、TPS3307 の MR、Pico 2 基板、5×20 F2A の溶断 I²t、娘の 3.3 V を作る素子（発振器なし）。確かめる事実: PT2314E の POR 直後の音量状態、PCM1804 の VCOM の駆動能力、RS6 の入手性（[review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) §10-11、[review/rail_detect_review.md](review/rail_detect_review.md) §10、[review/main_power_compare_review.md](review/main_power_compare_review.md) §5）。

### 10-2 決めること

| # | 決めること | 選択肢 | 出典 |
|---|---|---|---|
| U1 | ミュートの場所・素子・時間 | ポットの前／HP 入力と LINE 出力／HP 出力の後ろ、常開・常閉・ラッチング・半導体、約 1 s／1.5 s | §2-10、[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6.4 |
| U2 | ch のデコーダの置き場所と EN の形、娘の 3.3 V | 娘（2→4 デコーダ＋FET、レールから 3.3 V）／親。直列 R＋ショットキーを残すか | §2-9、[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6.4 A1 |
| U3 | 娘の MCP23017 を残すか（I²C をスタックに通すか） | 残す（コネクタ +2 本）／親からのレベル線だけ | [NOW] L25、[review/arch_zero_base.md](review/arch_zero_base.md) §0.1 #1、[review/stack_relay_power.md](review/stack_relay_power.md) §7.2 |
| U4 | NC 側の抵抗値 | 音声 10 kΩ（4.7〜22 kΩ）、レール 2.2 kΩ（1〜4.7 kΩ） | §2-3、[review/stack_relay_power.md](review/stack_relay_power.md) §0.2 |
| U5 | 電源リレーの品種（AZ850P2-5 で両役か） | 1 品種／電源だけ 2 A 級 | §2-2 |
| U6 | リセットの順序をハードでも保証するか、PRST を音声リセットの OR に入れるか、自動リセットを電源リレーにも入れるか | — | [review/rail_detect.md](review/rail_detect.md) §0.5 D5・D6 |
| U7 | ch LDO の後ろの容量の上限（22 µF）を残すか | しきい値を下げたので制約は消えた、という査読の読みを採るか | §3-7 |
| U8 | GND センス点と Q1/Q2 の切替の形 | 娘→母板のコネクタの `A_GND` ピン際 1 点（推奨）／外部取り出し端子の GND／娘に専用ピン。1×3 ヘッダ＋シャント／スライドスイッチ | §4-3、[review/adc_gnd_retree.md](review/adc_gnd_retree.md) §5・§7.4 |
| U9 | 計測側の予備の音声端子（2P、GND 極なし）を 3P にするか外すか | — | [review/adc_gnd_retree.md](review/adc_gnd_retree.md) §7.4-10 |
| U10 | ADC 入力の逆向きの窓の保険（VCOM–ドライバ +IN に 1 kΩ）、I²S の直列抵抗（0 Ω の足場） | — | §4-6、[review/adc_gnd_retree.md](review/adc_gnd_retree.md) §6.4 |
| U11 | LDO 前のフィルタの形 | 入口の電解を低 ESR に／足元を 1 µF に／2 段 | [review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) §6.2・§10-2 |
| U12 | v2.1 の試験レベル | バス 3.70 Vrms（−3.4 dBFS、DUT は v1 より +5.5 dB）／v1 と同じ DUT 振幅（−8.9 dBFS、平均を増やす） | [review/tap_compare_review.md](review/tap_compare_review.md) §2.3・§4-A |
| U13 | ch 側の入力 220 kΩ を戻すか | 入力スイッチを先に閉じ 5τ 待てば聴こえるバスに出る前に吸収される。安い保険 | [review/rejected_review.md](review/rejected_review.md) #6、[_review](review/rejected_review_review.md) #6 |
| U14 | DIRECT の置き方と切替、ライン入力の振幅の定義 | — | §1-5、[NOW] L27 |
| U15 | シャーシを 1 点で落とす先（パネル部品の金属部のグランドの扱いを含む） | — | [review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) §8-1・§10-8 |
| U16 | 入力ヒューズ（今の F2A 速断のままか）と DC-DC 入口の電解の耐圧・ESR | 突入の I²t は 0.007〜0.034 A²s の見積もり。RS6 の DS に推奨ヒューズは無い | [review/main_power_compare_review.md](review/main_power_compare_review.md) 1-6・§4-7 |
| U17 | 娘の最終枚数 | 固定側・レール容量・故障時の ch 数が枚数に比例（電源 SET は 4 本＝4 枚まで） | [review/main_power_compare_review.md](review/main_power_compare_review.md) §4-8、§2-5 |
| U18 | 議論中の回路: Cf の足場、高速娘の網、バイアス | — | [NOW] L28 |
| U19 | PCB: グランドの NetTie 群とグランド選択ヘッダを 1 か所に寄せる、`ADC_GND` の島は 1 か所でしか外とつながらないゾーンに | — | [review/adc_gnd_retree.md](review/adc_gnd_retree.md) §7.4-13 |
| U20 | 縦積みで下の段の DIP ソケットに手が届くか（v2 L3177「最大の制約」） | 積み方・段の数・挿し替えの手順 | [review/decisions_audit_3_review.md](review/decisions_audit_3_review.md)（3884 の補足） |
