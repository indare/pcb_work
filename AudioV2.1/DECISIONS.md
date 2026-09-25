# AudioV2.1 決定ログ（DECISIONS）

> **これは v2.1 自身の決定ログ（2026-09-25 から）。** v2 から引き継いだ決定は §7 に v2.1 の項目（`V21-継-nn`）として書き直してある。v2 の決定ログは読まない。
> このファイルは、v2 の全コピーのときにできた v2 の決定ログの写し（バイト一致）を置き換えたもの。

- 2026-09-25: エージェントの下書き（[review/DECISIONS_v21_draft.md](review/DECISIONS_v21_draft.md)）に、否定側査読（[review/DECISIONS_v21_review.md](review/DECISIONS_v21_review.md)）とユーザーの回答を反映して置いた
- 現況（いま何待ちか・次の一手）の正は [NOW.md](NOW.md)。この文書は「何を決めたか・なぜか・何を捨てたか」だけを持つ
- 回路図から導出できる事実（ネットリスト・参照・部品数・部品値）は書かない（[../SOURCE_OF_TRUTH.md](../SOURCE_OF_TRUTH.md)）。部品は機能名かネット名で書く。**選定として決めた型番**（RS6-1215D など）と、決定を支える DS の数値は書き、出典を付ける
- v2 から引き継いだものは §7、v2.1 では成り立たない v2 の決定と訂正された記録の表は [review/v2_carryover.md](review/v2_carryover.md)。本文で「v2 の『…』」と書くのは v2 でそう決めていたことの呼び名で、v2 の本文は引かない
- **`[NOW] Lnn` はコミット `a63caac` の NOW.md の行番号**（`git show a63caac:AudioV2.1/NOW.md`）。この文書を置いたときに NOW の「v2.1 で決まったこと」を短い要旨へ差し替えたので、今の NOW.md とは行が合わない

---

## 0. v2.1 とは

### 0-1 目的

オペアンプを電子的に切り替えて、音の差を耳で楽しむ箱。**計測器ではない。** 切替素子の優劣も耳で決める（[NOW.md](NOW.md)「装置」）。
計測系（ADC・スペアナ）は表示と簡易分析のためにあり、**本線（聴く経路）を汚さないことが計測の精度より優先**する（§4-2）。

### 0-2 v2 との関係

- v2.1 は 2026-09-25 に v2 の図・スクリプトを**全部写して**始めた（[NOW.md](NOW.md) 冒頭）
- 目的は「選んだ ch だけ電源と入力を生かす」構成の検討。v2 は「全ソケット常時通電・入力はブロードキャスト」だった
- v2 の決定のうち、v2.1 でもそのまま効くものは §7、成り立たなくなったものは [review/v2_carryover.md](review/v2_carryover.md) に表で置いた（棚卸し: [review/decisions_audit_1.md](review/decisions_audit_1.md)・[_2](review/decisions_audit_2.md)・[_3](review/decisions_audit_3.md) とそれぞれの `_review`。**査読が監査を直したところは査読を採った**）

### 0-3 読み方

各項目は次の形で書く。

| 欄 | 中身 |
|---|---|
| **決定** | 1〜3 行 |
| **理由** | いちばん強い理由 1 つ |
| **根拠** | `ds_facts/`・`review/`・`spice/`・`scripts/`・DS へのリンク |
| **前提・外れる条件** | これが崩れたら見直す |
| **却下した案** | 1 案 1 行、理由とリンク |
| **状態** | 下の表のどれか。1 項目に複数あるときは箇条に割る |

| 状態 | 意味 |
|---|---|
| **決定** | ユーザーが決めた。条件つきのものは条件を書く |
| **いったんの決め** | 推奨をユーザーが受けた（「よい」「おすすめで」「良さそう」）もの、査読で出た値を仮に採ったもの |
| **未決（推奨）** | 推奨はあるが、ユーザーは決めていない |
| **未決** | 推奨もまだ無い |
| **要実測** | 実測の結果で決める |
| **v2 の却下を引き継ぐ** | v2 で却下され、v2.1 で個別の判断はしていない |
| **v2 から引き継ぎ（v2.1 で再考していない）** | v2 で決め、v2.1 の前提で見直さずに持っている（§7） |
| **DS の制約** | DS が求めること。判断ではない |

略記: [NOW] = 上の注のとおり（コミット `a63caac` の [NOW.md](NOW.md)）、[pow] = [ds_facts/power.md](ds_facts/power.md)、[sw] = [ds_facts/switch_control.md](ds_facts/switch_control.md)、[op] = [ds_facts/opamps.md](ds_facts/opamps.md)、[tap] = [ds_facts/tap.md](ds_facts/tap.md)、[bnd] = [ds_facts/boundary.md](ds_facts/boundary.md)（照合 [verify_boundary.md](ds_facts/verify_boundary.md)）。`ds_facts/relay4.md` は**未照合**なので根拠に使っていない。
§10 の未決・実測は `V21-未決-nn`・`V21-実測-nn` で呼ぶ（他の査読ファイルの記号と衝突させないため）。

---

## 1. 設計の根本

### 1-1 コールドスタンバイ — 電源要求の違う回路を切り替える

- **決定**: 解く問題を「電源要求の違う回路を同じバスへ切り替えること」と置く。非選択の回路は**電源ごと落とし**、バスとの境目には「電源が無いときにも切れている素子」を置く（コールドスタンバイ）。回路ごとに自分の電源（LDO で電圧を選ぶ）を持たせて同じバスに混ぜる
- **理由**: v2 の形では、非選択の回路が境目の素子（TMUX7612）を生かすために通電していた（ホットスタンバイ）。TMUX7612 の DS には**電源を切ったときの漏れ・高インピーダンスの規定が無く**、端子はレールへダイオードでクランプされている
- **根拠**: [NOW] L22「設計の根本」／[bnd] §1.1（TMUX7612: 電源断時の規定なし、"Pins are diode-clamped to the power-supply rails."、電源シーケンスは任意）。[NOW] L22 は「議論中」と書いているが、境目の素子（ラッチングリレー）と 1 枚の ch 数（4）は L24 で決まった
- **前提・外れる条件**: 境目の素子が電源断でも切れていること（§2-1 のラッチングリレー）。境目の外（親）の PT2314E と計測系は常時通電。TMUX7612 は娘の上で電源リレーの後ろにあり、**選んだ娘の中では ch の EN で切らずに通電したまま**、選んでいない娘では電源ごと落ち、境目のリレーでバスから切られる
- **却下した案**: v2 の「全 ch 常時通電・入力ブロードキャスト」— 選んだ ch だけを生かす目的と逆
- **状態**: 決定（ユーザー判断 2026-09-25）

### 1-2 同時に生かすのは厳密に 1 ch

- **決定**: 電源と入力を生かすのは**選んだ 1 ch だけ**。ファームは全 OFF → 1 ch ON。温めておく ch は作らない。ハードは ch ごとに独立して切れる。ヘッドホンは 32 Ω を想定
- **理由**: 主電源（RS6-1215D、±200 mA）の予算がこの前提で成り立つ（§3-1）。温めておく ch を許すと、同時に通電できる数が DC-DC の型番で決まってしまう（最悪の石で 5 ch、80 % で使うなら 3 ch という見積もりがあった）
- **根拠**: [NOW] L9／[review/rejected_review.md](review/rejected_review.md) #5・[rejected_review_review.md](review/rejected_review_review.md) #5（温める数の見積もりと訂正）
- **前提・外れる条件**: 石の熱の整定（通電してから音が落ち着くまで）が許せる長さであること。v2 の反対理由「今つけた石と、ずっとついていた石を比べる」はハードでは解けず、切り替えてから聴くまでの待ち時間の問題として残る（[rejected_review_review.md](review/rejected_review_review.md) §6 U2、V21-実測-09）
- **却下した案**: 「最低 1 ch、温める数はファームが決める」— 同上（DC-DC の余裕を食う）
- **状態**: 決定（ユーザー判断 2026-09-25）

### 1-3 制御の木は 2 段

- **決定**: 1 段目＝**基板（娘）1 枚だけ ON**、2 段目＝**その基板の中で 1 ch だけ**。どちらも「全リセット → 1 つだけセット」のブレーク・ビフォア・メイク
- **理由**: 選んだ 1 ch だけ給電する形なら、1 段目の故障（別の基板にも電源が入る）でも ch の EN が 2 つ目の関門になる（[review/dcdc_2stage_review.md](review/dcdc_2stage_review.md) 要約 3）。逆に基板をまたぐ排他が無いと、娘 4 枚が 1 ch ずつ ON の最悪で RS6 の +15 V が定格の 110 % になり、過負荷保護（150 %）は働かない
- **根拠**: [NOW] L24／[review/bulk_parent_sim.md](review/bulk_parent_sim.md) §0.3（4 枚 110 %、2 枚以下なら 89 %）／[review/dcdc_2stage.md](review/dcdc_2stage.md)・[_review](review/dcdc_2stage_review.md)
- **前提・外れる条件**: 1 段目・2 段目の中身は §2
- **却下した案**: 親のスロットごとの電源スイッチで 1 段目を作る案 — §2-1 の縦積みリレーに差し替えた（[NOW] L24「旧 N1/N2 は不要」、§2-1 の却下欄）
- **状態**: 決定（ユーザー判断 2026-09-25）

### 1-4 基板は 1 種類、1 枚 4 ch、切替素子の聴き比べはしない

- **決定**: 娘は 1 種類だけ（中は TMUX7612 で ch を選ぶ）、1 枚 4 ch。ch ごとのリレーの基板と、切替素子の聴き比べは v2.1 ではやらない
- **理由**: ユーザーの判断（[NOW] L24–25）
- **根拠**: [NOW] L24「決定（2026-09-25、差し替え）: DC-DC は RS6、1 枚 4 ch、基板は 1 種類だけ」、L25
- **前提・外れる条件**: —
- **却下した案**: v2 の「リレー版とスイッチ版を別 PCB 2 種で起こし、実機で比べる」— v2.1 の目的から外した／ch ごとにラッチングリレーを置く娘（[review/arch_zero_base.md](review/arch_zero_base.md) §0.1 #11）— 同上
- **状態**: 決定（ユーザー判断 2026-09-25）

### 1-5 DIRECT（PT2314E を飛ばす経路）は聴くためのライン入力用

- **決定**: DIRECT はライン入力を聴くための経路とする。v2 の「経路ごとの振幅上限」のうち**精密 DIRECT・フルレンジ DIRECT は要件から外す**。PT2314E を通る通常経路の上限の考え方は残る
- **理由**: 装置は計測器ではない（§0-1）。精密 DIRECT は TMUX の膝の近くまで振る運用のためのもので、耳で比べる用途には要らない
- **根拠**: [NOW] L18／[review/decisions_audit_3_review.md](review/decisions_audit_3_review.md)（v2 の「経路ごとの振幅上限」は「無効」ではなく「前提変更」。無効なのは DIRECT の 2 行だけ）
- **前提・外れる条件**: DIRECT の置き場所・切替の形、ライン入力の振幅の定義（2 Vrms か、それ以上か）は未決（V21-未決-14、[NOW] L27、[review/rejected_review.md](review/rejected_review.md) §3.4）
- **却下した案**: —
- **状態**:
  - 決定: DIRECT は聴くためのライン入力用、精密／フルレンジ DIRECT は要件外（ユーザー判断 2026-09-25）
  - 未決: 置き方（V21-未決-14）

---

## 2. 制御の木

### 2-1 1 段目: 縦積みの各娘に電源用ラッチングリレー → レールがそろってから音声用

- **決定**: ±15 V は全段に常時通す。各娘で **電源用ラッチングリレー（DPDT 1 個、+15 V と −15 V に 1 極ずつ）** をセット → 両レールがそろってから **音声用ラッチングリレー（DPDT 2 個、`TONE_L/R` と `AMP_SEL_L/R` の 4 本）** をセット。リセット（NC 側）は切り離し。**コイルの電源（`+5V_COIL`）と全リセットは常時系統から出す**（電源の無い娘にもリセットが届く）
- **理由**: ラッチングなら聴取中に音声の近くを制御電流が流れない（ユーザーの好み）
- **根拠**: [NOW] L24／[review/arch_zero_base.md](review/arch_zero_base.md) §1.1「ユーザーはラッチングリレーを好む」／[review/stack_relay_power.md](review/stack_relay_power.md)・[_review](review/stack_relay_power_review.md)
- **前提・外れる条件**:
  - ラッチングリレーは衝撃・前歴で状態が変わりうる（G6K・TQ の DS が「リセット位置で出荷、衝撃で変わりうる、初期化せよ」と明記 [bnd] §3、[verify_boundary.md](ds_facts/verify_boundary.md) 要約）。**電源投入時とすべての切替で全リセットから始める**こと（§6）
  - 縦積みで上下・隣のリレーは **5 mm 以上離す**（AZ850 p2 が隣接 5.0 mm を推奨、Panasonic・Omron も近接の影響を明記。[review/stack_relay_power_review.md](review/stack_relay_power_review.md) §3 (c)、[review/rail_detect_review.md](review/rail_detect_review.md) §1 の表）。PCB を起こすときの制約
- **却下した案**:
  - 親のスロットごとの電源 IC（TPS26600 eFuse）— 内部にチャージポンプがあり周波数も DS に無い（電源経路に発振器・チャージポンプを置かない要件に反する）（[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §0.1）
  - スロットごとの ±15 V スイッチ（LM5067／ディスクリート、発振器なしで合格。[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6 冒頭・§6.1）— [NOW] L24 で電源リレーに差し替えた。**差し替えの理由の記録は無い**
  - 境目を非ラッチングリレー／電源断保護つきアナログ SW／PhotoMOS にする案 — [NOW] L22 の候補で、L24 でラッチングリレーに決めた。**個別の却下理由の記録は無い**（DS 事実は [bnd]）
- **状態**:
  - 決定: 電源用 → 音声用の縦積みラッチングリレー、コイル電源と全リセットは常時系統から（ユーザー判断 2026-09-25、[NOW] L24）
  - DS の制約: リレーの間隔 5 mm 以上

### 2-2 リレーの品種 — 音声用は AZ850P2-5（v2 から）、電源用も同じ石を推奨

- **決定**: 音声用は `AZ850P2-5`（v1/v2 と同じ石）。電源用にも同じ石を使う方向（推奨）
- **理由**: 直列 R を 15 Ω 以上にすれば電源の役でも突入のピークが抵抗負荷の開閉電流 1 A の内に入り（22 Ω で 0.68 A）、音声の役は最小開閉 10 mV / 10 µA・AgPd 金クラッド。2 コイル型なので今のシンク型ドライバ（TBD62083A）で SET/RESET とも駆動でき、FP・BOM・駆動が 1 種で済む
- **根拠**: [review/stack_relay_power.md](review/stack_relay_power.md) §0.1-5・§1.4／[sw] §2（AZ850）／[NOW] L222（v2 から引き継いだ「リレーは AZ850P2-5 に固定（2026-09-09）」）
- **前提・外れる条件**: 容量負荷のメイクは DS の規定の外（1 A は抵抗負荷）。**実機のメイク回数試験**が最終的な根拠（[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 1-3・1-4、V21-実測-11）。直列 R を 15 Ω 未満にするなら電源用だけ 2 A 級（TQ2SA-L2）
- **却下した案**: Omron G6KU・Fujitsu FTR-B3 — 単巻線ラッチで極性反転の駆動が要り、シンク型ドライバでは組めない（[review/stack_relay_power.md](review/stack_relay_power.md) §1.1）／`TQ2-L2` を AZ850 の FP に挿す — COM/NC/NO のピン番号が違い SET/RESET が反転する（[NOW] L222）
- **状態**:
  - 決定: 音声用は AZ850P2-5（v2 の確定 2026-09-09 を引き継ぐ、[NOW] L222）
  - 未決（推奨）: 電源用にも AZ850P2-5。推奨は両役、容量負荷のメイク試験で決める（V21-未決-05、V21-実測-11）

### 2-3 配線: COM＝娘側、NO＝バス（スタック）、NC＝抵抗越しに GND

- **決定**: 音声・電源とも、接点の COM を娘側、NO をバス側、NC を抵抗越しに GND へ。リセット状態で娘側の音声の節とレールが抵抗で放電される
- **理由**: この向きなら NC の抵抗はセット・リセットのどちらの状態でもバスに載らない（バスに見えるのは開いた NO 接点だけ）。逆にするとバスを抵抗で負荷する
- **根拠**: [review/stack_relay_power.md](review/stack_relay_power.md) §0.1-6・§5.1／[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 5-1・5-2（AZ850 p2 の図と v1 のピンの使い方で確認）
- **前提・外れる条件**: 抵抗値は推奨どまり（音声 10 kΩ、レール 2.2 kΩ）
- **却下した案**: 逆向きの配線 — NC の抵抗が並列でバスを負荷する（[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 5-2）
- **状態**:
  - いったんの決め: 配線の向き
  - 未決: 抵抗値（V21-未決-04）

### 2-4 電源接点に直列 22 Ω（ヒューズ抵抗）、NO（スタック）側

- **決定**: 電源接点の後ろに各レール **22 Ω**。品種は**ヒューズ抵抗**（突入パルスには耐え、2 W 連続で開く）。**±15 V は DPDT 1 個で切り、22 Ω は NO（スタック）側へ置く**
- **理由**: 22 Ω で突入のピークが 0.68 A（接点の開閉電流 1 A の 68 %）。NO 側に置けば、リレーの中でどこの極間が短絡しても ±15 V の間に 44 Ω 以上が入る
- **根拠**: [NOW] L25／[review/stack_relay_power.md](review/stack_relay_power.md) §1.3（R ごとの突入のピーク）／[review/rail_detect.md](review/rail_detect.md) §0.4／[review/rail_detect_review.md](review/rail_detect_review.md) 冒頭のユーザー決定 (3)・§6（極間短絡のときの 22 Ω の電力。耐パルスの 1206 では焼けるので溶断型が要る）／[spice/stack_relay/](spice/stack_relay/)
- **前提・外れる条件**: 査読の範囲は 15〜33 Ω。22 Ω は [review/stack_relay_power.md](review/stack_relay_power.md) の推奨を採ったもの（33 Ω を退ける理由は、しきい値を下げた後は残っていない: [_review](review/stack_relay_power_review.md) 3-4・§4、[review/rail_detect_review.md](review/rail_detect_review.md) 要約 5）。最悪の角でも LDO のヘッドルームは目安（≥ 1 V、DS の設計例の "for optimal performance"）を満たす（[_review](review/stack_relay_power_review.md) 3-2〜3-4）。**ヒューズ抵抗の品番の単発パルス曲線は未収集**
- **却下した案**:
  - 4.7〜10 Ω — 突入のピーク 1.48〜3.10 A は DS の保証の外（抵抗負荷の開閉 1 A を物差しにすると超える）。RS6 が 300 mA で頭打ちなら、娘のバルク無しでも親の +15 V は 9.8〜10.7 V まで落ちる〔仮定〕（[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 1-3・2-2）
  - 22 Ω を COM 側 — 極間短絡が ±15 V の直結になる（[review/rail_detect.md](review/rail_detect.md) §0.4）
  - ±15 V を DPDT 2 個に分ける — ユーザーが 1 個のままを選んだ
- **状態**:
  - 決定: ±15 V は DPDT 1 個・22 Ω は NO 側（[review/rail_detect_review.md](review/rail_detect_review.md) 冒頭のユーザー決定 (3)）
  - いったんの決め: 22 Ω・ヒューズ抵抗（[NOW] L25）

### 2-5 制御線は全段共通、各娘はジャンパで自分の段を選ぶ

- **決定**: 制御線は全段に同じ番号で素通しする。電源用 SET は段ごと（4 本）で、各娘はジャンパで 1 本を選ぶ。**リセットは音声用（ARST）と電源用（PRST）の 2 本で、どちらも全段共通**。ch 選択線は共通。音声用 SET は共通 1 本（§2-6）。スタックの制御・電源のコネクタは **2×12（24 本、[NOW] L25）**
- **理由**: 縦積みで各娘が同じピンを見るので、段ごとに違う線を通すなら番号をずらす仕掛けが要る。全段共通＋ジャンパなら娘の基板は 1 種類のまま
- **根拠**: [NOW] L24・L25／[review/stack_relay_power.md](review/stack_relay_power.md) §7.2（線の表）・§5.3（リセットの順番）／[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 6-1・7-2（音声 SET を共通にしても 21 本で 2×10 には入らない）。[NOW] L24 の「RESET 共通 1 本」は古い（順番をファームで守るには 2 本要る）
- **前提・外れる条件**:
  - 24 本の内訳は下書きの算術〔計算〕: [review/stack_relay_power.md](review/stack_relay_power.md) §7.2 の 24 本（段ごとの音声 SET 4 本を含む）から 3 本を引いた 21 本（`PG_N` を含む）に、`MON_P`・`MON_N`・`RAIL_OK`（§5-2・§5-3）を足した数。`PG_N` を残すか、予備の GND を何本にするかは未確定（V21-未決-22）
  - 娘の MCP23017 を残して I²C を通すなら 2 本増えて入らない（同 §7.2、V21-未決-03）。電源用 SET と音声用 SET で選ぶ段を食い違えない配置が要る（同 §7.2）
- **却下した案**: 今の 2×8 のまま — 本数が足りない（同 §7）／親にスロット 4 口を横に並べるバックプレーン — 縦積みに決めた（[review/arch_zero_base.md](review/arch_zero_base.md) §0.1 #15 は横並びを推していた）
- **状態**:
  - 決定: 全段共通・ジャンパで段を選ぶ（[NOW] L24）
  - いったんの決め: 2×12・24 本（[NOW] L25。音声 SET を共通 1 本にした決定の帰結）

### 2-6 音声用 SET は全段共通の 1 本（査読で D10 と呼んだ件）

- **決定**: 音声用リレーの SET は**スタック全段に共通の 1 本**。条件: 音声 SET は「全リセット（全娘の電源リレーと音声リレー）→ 選んだ娘の電源 SET → レール良好 → 共通の音声 SET」の**1 つの手順の中でだけ出す**（ファームの責務、§6-2）
- **理由**: レールの無い娘は B1（§5-4）で音声 SET のコイルに電源が来ないので、共通の SET が届いても**セットできない**。共通線だけに残る弱点（選んでいない娘の電源リレーが衝撃でラッチすると、その娘でも B1 が通る）は、上の手順が必ず全リセットから始まることで消える
- **根拠**: ユーザー判断（2026-09-25「共通で破綻しないならそれで決定」）／[NOW] L25／[review/stack_relay_power.md](review/stack_relay_power.md) §7.2（共通案の弱点）／[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 7-4（段ごとの SET でも、衝撃でセットされた音声リレーは消せない）／[review/rail_detect_review.md](review/rail_detect_review.md) §3.3（B1）
- **前提・外れる条件**: 聴取中に衝撃で別の娘の電源リレーがラッチすると、その娘はレールが立ち、共通の ch 選択でその娘の ch の LDO も入る（音声リレーはリセットのままなのでバスには出ない）。RS6 の負荷は最悪 2 ch 分で +15 V 89 %（HP 最大、[review/bulk_parent_sim.md](review/bulk_parent_sim.md) §0.3）。次の切替の全リセットで切れる。ジャンパの重複で 2 枚が同じ段を選ぶ事故は [review/stack_relay_power.md](review/stack_relay_power.md) §7.2 の弱点として残る
- **却下した案**: 段ごとの音声 SET（4 本）— 衝撃でラッチした音声リレーはどちらでも防げず、残る弱点はファームの手順で消せるので、ピンを 3 本使う理由が弱い
- **状態**: 決定（条件つき、ユーザー判断 2026-09-25）

### 2-7 全リセット → 1 つだけセット。リセットの順番はファーム

- **決定**: 切替はいつも全リセットから。リセットの順番（音声を先・電源を後）は**ファームで守り、ハードは足場だけ**置く。パルス幅もファーム（§6）
- **理由**: 娘のバルクを外したので、電源接点が開いてから LDO が落ち始めるまで 0.4〜3.8 ms しかなく、リセット時間と同じ桁。同時に切るとバスに制御されない過渡が出うる。ただし**壊れはしない**ので、ハードで保証するのは必須ではなく保険
- **根拠**: [NOW] L25／[review/stack_relay_power.md](review/stack_relay_power.md) §0.1-7・§5.3／[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 6-1（ファームの ARST → 20 ms → PRST で足りる）
- **前提・外れる条件**: ハードで順序を保証する（PRST が音声のリセットも叩き、電源だけ 10 ms 遅らせる）かは未決（V21-未決-06、[review/rail_detect.md](review/rail_detect.md) §0.5 D6）
- **却下した案**: —
- **状態**: いったんの決め（[NOW] L25）

### 2-8 2 段目: 娘の中は TMUX7612 で ch を選び、選んだ ch の石だけ LDO の EN で給電

- **決定**: 娘の中の ch 選択は TMUX7612。ch の**出力だけでなく入力も**切る（入出力 L/R＝ch あたり 1 パッケージ）。選んだ ch のソケットだけ、ch ごとの正負 LDO（TPS7A49／TPS7A30）の EN で給電する。TMUX は娘の電源リレーの後ろの ±15 V（LDO の前）に載り、**選んだ娘の中では常時（ch の EN では切らない）**。選んでいない娘では電源ごと落ち、境目のリレーでバスから切られる
- **理由**: 電源を落とした石の入力が共有の `TONE` バスにつながったままだと、どの石でも入力の絶対最大を越え、入力保護ダイオード越しにバスを低いインピーダンスで負荷する（PT2314E の最小負荷 5 kΩ を大きく割る）。アナログスイッチ自身も、バスにつながっている間は通電していないとスイッチがクランプになる
- **根拠**: [NOW] L9・L17・L25／[review/pm12_judgement.md](review/pm12_judgement.md) §5・[_review](review/pm12_judgement_review.md) §E／[review/ds_errata_review.md](review/ds_errata_review.md) O1〜O3（OPA1652・OPA1612・NJM5532 の入力保護ダイオード）／[review/dcdc_2stage_review.md](review/dcdc_2stage_review.md) 1.1（ch に 1 パッケージ、娘の上なので板スイッチの後ろに載る）／V21-継-15（入力クランプ）・V21-継-16（アナログスイッチはバスにつながっている間は通電）
- **前提・外れる条件**: 電源を切った石の出力も ESD 構造でレールにつながるので、出力も切る（V21-継-14）。正側 LDO だけが切れて負側が残る状態は NJM5532 の DS が注意する形（[review/pm12_judgement.md](review/pm12_judgement.md) §5.3-2）
- **却下した案**: 出力だけ切る（v2 の図）— 電源の無い石の入力に信号がかかる（[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6.3-2）／ch ごとの絶縁 DC-DC — 同時に生きる ch が 1 つなら守る相手が無い（[review/rejected_review.md](review/rejected_review.md) N1）
- **状態**: 決定（ユーザー判断 2026-09-25）

### 2-9 EN は娘の切られたレールから作る。1 ch だけ ON のデコーダは既定 OFF

- **決定**: ch の LDO の EN の論理は娘の切られたレール（電源リレーの後ろ）から給電し、**EN が LDO の IN を超えない形にする**。娘ごとに「1 ch だけ ON できる」デコーダを置き、有効化の既定は OFF。レールが落ちたら EN も切る（§5-5）
- **理由**: TPS7A49 の絶対最大は「EN – IN −36 / +0.3 V」。`3V3` が生きていて ±15 V が無いとき（主電源スイッチ OFF で Pico が USB だけで動く場合、RS6 が保護で止まっている間）に 3.3 V の EN を出すと定格を破る。起動の順序では防げず、DC-DC の型番でも直らない
- **根拠**: [NOW] L15・L25／[pow] §2（TPS7A49 絶対最大 EN–IN、VEN(high) 2.1 V、VEN ≤ VIN）・§3（TPS7A30 EN–IN −0.3/+36 V）／[review/main_power_compare_review.md](review/main_power_compare_review.md) 1-6・§3.3／[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6 冒頭・§6.2・§6.3-1
- **前提・外れる条件**: EN 保護は要る（ユーザー決定、[review/arch_zero_base.md](review/arch_zero_base.md) 冒頭）。手段は「EN をレールから作る」（決定）で、[NOW] L15 の直列 R＋EN→IN ショットキー＋プルダウンは査読の読みでは不要（[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6.2）。残すかは未決。**1 ch だけ**をハードで守るのは娘の中だけで、娘をまたぐ排他は §2-6・§6 に残る
- **却下した案**: ファームの規約だけで排他する — MCP23017 の POR 後は全ピンが入力で、プルダウンが守るのはリセット中だけ。ファームのバグ（ポートに全ビット 1 を書く等）には効かない（[review/main_power_compare_review.md](review/main_power_compare_review.md) 1-5）
- **状態**:
  - 決定: EN の論理を娘の切られたレールから給電（[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6 冒頭のユーザー決定、[NOW] L25）。1 ch だけ ON のデコーダ・既定 OFF（[NOW] L15）
  - 未決: デコーダの素子と置き場所、娘の 3.3 V の作り方（発振器・チャージポンプの無いもの）、直列 R＋ショットキーを残すか（V21-未決-02、[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6.4 A1）

### 2-10 切替の間は音声を GND へ落とすミュート

- **決定**: 切替の間は、音声を GND へ落として無音にする
- **理由**: 過渡の出どころ（TMUX と境目のリレーの切替、LDO の立ち上がり、出力結合の整定、娘のレールの切替）は全部 `AMP_SEL` バスに出るので、バスより上流の PT2314E のミュートでは消せない
- **根拠**: [NOW] L25／[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6.3-5／参考製品 [datasheets/reference/Kyohritsu_KP-HAMP61_manual.pdf](datasheets/reference/Kyohritsu_KP-HAMP61_manual.pdf) — PDF p2（本文テキスト層）「切り替え時はオペアンプの電源の切り替えと音声回路の切り替えを行いますが、…1 秒程度の無音期間（音声回路を安全な GND 信号と接続）が取られる構造」、PDF p3（画像、[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6 で読んだもの）「選択されていないオペアンプが、電源も含めて回路から完全に切り離されている」。操作子はスイッチ 1 個（p1）。無音を検出して電源を切る機構がある（p1・p2）
- **前提・外れる条件**:
  - `AMP_SEL` を直接 GND に落とすと、選んだ石の出力を結合コンデンサ越しに交流短絡するので避ける（[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6.3-5）
  - ミュートの長さの 2τ/3τ は τ 0.48 s の場合。NC 10 kΩ を採り、TMUX で ch を選んでから音声リレーをセットする順なら τ は約 21 ms で、待ちはずっと短くなりうる（[review/stack_relay_power.md](review/stack_relay_power.md) §0.1-6、[_review](review/stack_relay_power_review.md) 5-3）。実測（V21-実測-12）で決める
- **却下した案**: —
- **状態**:
  - 決定: 方針（切替の間は GND へ落とすミュート）
  - 未決: 場所（ポットの前／HP 入力と LINE 出力／HP 出力の後ろ）、素子（常開・常閉・ラッチング・半導体）、時間（V21-未決-01、[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6.4）

### 2-11 `TONE` バスに 100 kΩ のプルダウン

- **決定**: 親の `TONE_L/R` に 100 kΩ で GND への DC の基準を置く
- **理由**: `TONE` バスは直列のコンデンサに挟まれて DC が浮いている（査読時の回路図で確認: [review/stack_relay_power_review.md](review/stack_relay_power_review.md) 5-4）。音声リレーをセットした瞬間に娘側（NC 抵抗で 0 V）とバスの DC の段差が入りうる
- **根拠**: [NOW] L25／[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 5-4／[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6.1（20 Hz で約 −0.08 dB、PT2314E の最小負荷 5 kΩ の内側）
- **前提・外れる条件**: —
- **却下した案**: —
- **状態**: いったんの決め（[NOW] L25）

---

## 3. 電源

### 3-1 主電源の DC-DC は RS6-1215D

- **決定**: ±15 V の絶縁 DC-DC は `RS6-1215D`（入手できれば）。SIP8 の新しいフットプリント（推奨穴 Ø1.00 +0.15/−0 mm）を作る
- **理由**: 1 ch の設計点で出力の合計が定格の **36〜63 %** で、候補の中で軽負荷の領域からいちばん遠い（軽負荷の振る舞いを決めるのは片側ではなく合計の電力）。あわせて最大容量性負荷 ±660 µF（出力ごと）、絶縁容量 110 pF max
- **根拠**: [NOW] L14／[review/main_power_compare.md](review/main_power_compare.md)・[_review](review/main_power_compare_review.md) §3.1（理由の順番を直した）／[pow] §1（±200 mA、9–18 V、±660 µF、110 pF max、内部動作周波数「0-100% load」Min 200 kHz、起動 2 ms、UVLO ON 9 V typ、OLP 150 %、SIP8 のピン配置と穴径。CTRL は開放で ON）／[scripts/rail_budget.py](scripts/rail_budget.py)（`--adc-from-pd`）／[scripts/dcdc2/](scripts/dcdc2/)
- **前提・外れる条件**:
  - ADC の LDO を ±15 V に載せない（§4-4。載せると定格に入らない）
  - 突入をどこまで出せるか・OLP の形（出力ごとか合計か、定電流かヒカップか）は要実測（V21-実測-01）。8 ch が同時に入る故障では +15 V が定格の 136〜161 % のまま流れ続けうるので、§2-9 のデコーダと §6 の手順で防ぐ
  - 今のフットプリント（1″×1″）にも、リポジトリにある SIP8 の FP（穴 Ø0.8）にも合わないので、新しい FP が要る
  - v2 の記録にある 6 W 低 Ciso 群（10〜20 pF）は 1 ch 通電で候補の電力帯に入ったが、比較に入れていない（[review/v2_carryover.md](review/v2_carryover.md) の「絶縁 DC-DC の絶縁容量 — 探索結果」の行、V21-未決-21）
- **却下した案**:
  - `TMR 9-1223` — Cout ±200 µF でレールの見込みの上側を超えうる、500 kHz は全負荷の値で軽負荷の記載が無い、金属ケース（[review/main_power_compare.md](review/main_power_compare.md) §2.1、[_review](review/main_power_compare_review.md) 1-3）（次点。絶縁容量 50 pF max は RS6 より良い。−15 V は軽負荷側でベンチ確認が要る、[_review](review/main_power_compare_review.md) §3.1）
  - `TMR 10-1223WI` — Cout ±220 µF、絶縁容量 1000 pF typ、4.1〜4.5 V で起動するので PD が交渉する前の 5 V で動いてしまう（同上）
  - `REC20K-2415DZ`（v2 の石）— 1 ch では −15 V が定格の約 8 % で DS の Note4（10 % 未満は仕様を満たさないことがある）より下、絶縁容量 2000 pF typ（同上、[review/dcdc_2stage_review.md](review/dcdc_2stage_review.md) 1.2）
  - Mornsun `URA` — v2 と同じく NFND（V21-継-13）。「軽負荷で周波数を下げる」は決め手ではない（[review/rejected_review_review.md](review/rejected_review_review.md) #12）
  - ±15 V を 2 台に分ける（ソケット用と常時系）— HP バッファの電流は分けても共有側に残る（[review/rejected_review_review.md](review/rejected_review_review.md) N4）
- **状態**: 決定（ユーザー判断 2026-09-25、入手できれば）

### 3-2 PD は 12 V 固定

- **決定**: PD の受け電圧は 12 V に固定する（他の設定にしない）
- **理由**: ADC の LDO（LT1763）を PD 12 V から直接取るので、IN の絶対最大 ±20 V に対して 20 V 設定は許容差の分だけ超えうる。RS6 の入力範囲も 9〜18 V（サージ 25 V は 1 秒まで）
- **根拠**: [NOW] L11／[review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) §1 の表（LT1763 の IN 絶対最大）・§7.4／[pow] §1（RS6 入力範囲）
- **前提・外れる条件**: PD モジュールは交渉前に 5 V を出す。主電源スイッチを入れたまま USB-C を挿すと、その間 ADC 側だけが立つ（[review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) §7.4「PD の 5 V の窓」）。RS6 は UVLO で止まっている
- **却下した案**:
  - 20 V — LT1763 の絶対最大を許容差の分だけ超えうる
  - 15 V — LT1763・RS6 とも範囲内だが、固定にした（v2 の「PD 入力 — どの電圧で受けるか」「12 V が出なかったときの手順」の 15 V は v2.1 では使わない）。15 V を退ける理由の記録は無い
- **状態**: いったんの決め（[NOW] L11）

### 3-3 PT2314E・計測は生の ±15 V、TMUX は娘の切られた ±15 V、ソケットは ch ごとの LDO で ±12 V

- **決定**: ±15 V はそのまま、親の PT2314E（9 V レギュレータ経由）と計測系、娘の TMUX7612 に使う（TMUX は娘の電源リレーの後ろ。選んだ娘の中では ch の EN で切らない、§2-8）。ソケットは ch ごとの正負 LDO（TPS7A49／TPS7A30）で ±12 V。LDO の出力電圧は帰還の分圧で決まるので、ch ごとに選べる
- **理由**: ±12 V を DC-DC で直に作ると TMUX7612 の平坦域の膝がレールに追従して下がる（DS 本文: 平坦域は「概ね VSS+5 V〜VDD−5 V」。Figure 5-4 の目読みで Ron が底から離れ始めるのは ±15 V で約 +10.6 V、±12 V で約 +7.6 V）。ソケットだけを LDO の後ろで ±12 V にすれば膝は動かず、ch ごとの EN（§2-8）と PSRR も LDO が持つ
- **根拠**: [NOW] L17・L22／[sw] §1（平坦域の本文、Figure 5-4）／[pow] §2（TPS7A49 の出力電圧の式 R1 = R2 (VOUT/VFB − 1)、PSRR 72 dB @120 Hz）・§3（TPS7A30）／[review/rejected_review.md](review/rejected_review.md) #9／[review/pm12_judgement.md](review/pm12_judgement.md)・[_review](review/pm12_judgement_review.md)
- **前提・外れる条件**: ±12 V で電源範囲から外れる石は無い。ただし ±12 V で振幅が保証されるのは OPA1612・OPA2140 だけ。最悪要求（9.45 Vpk）と LDO の総合精度 ±2.5 % を入れると、余裕が正で残るのは保証の 2 石と typ グラフの 5 石。推定 min の石は 0 dB 前後か負（[review/pm12_judgement_review.md](review/pm12_judgement_review.md) 要約 3・5・6、A 表）。TPS7A49 の IOUT は 150 mA まで（[pow] §2）
- **却下した案**:
  - ±12 V の DC-DC で系全体を ±12 V（v2 の「±15 V の理由は3つとも消えた…±12 V 側にも重い障害」の検討、`REC10K-2412DAW/H2` ほか）— TMUX の膝が下がる。PT2314E の 9 V レギュレータ（L7809）の入力も 11.5 V（出力の許容差を保証する試験条件の下限）を割る（v2 の「`+9V`…が規定入力範囲を割る」。11.5 V の読みは [review/v2_carryover.md](review/v2_carryover.md) の訂正 #5）
  - `NSD10-12D12` — 2″×1″ で新しいフットプリント、最小負荷 20 mA/レール（1 ch 運転と合わない）、±12 V 出力（V21-継-13、[review/decisions_audit_1.md](review/decisions_audit_1.md)）
- **状態**: 決定（ユーザー判断 2026-09-25）

### 3-4 PT2314E は +15 V → L7809 のまま

- **決定**: PT2314E の電源は今までどおり +15 V から L7809 で 9 V
- **理由**: 電源だけ一次側（PD）へ移すと、PT2314E の帰り電流がグランドの木の中の唯一の橋を通る（v2 で一度潰したバグの再導入）
- **根拠**: v2 の「副次案『`+9V` 枝を `+15V` から外す』は一度潰したバグの再導入」／[review/decisions_audit_1_review.md](review/decisions_audit_1_review.md) 修正の要点 1（この v2 の項は「却下の再検討」ではなく維持）／[review/rejected_review_review.md](review/rejected_review_review.md) #8
- **前提・外れる条件**: +15 V の負荷を非対称にする唯一の塊がこれ（+15 V だけに 35〜48 mA）で、動かせない（[review/main_power_compare.md](review/main_power_compare.md) §3.2）
- **却下した案**: PT2314E を PD 12 V 側へ — 上の理由
- **状態**: 決定（ユーザー判断 2026-09-25。[review/decisions_audit_1.md](review/decisions_audit_1.md) の決定⑤）

### 3-5 娘のダンパのバルクは外す

- **決定**: 娘の ±15 V のバルク（ダンパ）を外す
- **理由**: 直列 R が 1 Ω 以上なら、どの角でも親→娘の伝達に共振の山が無い。バルクを残すと突入の電荷が増えて親の落ち込みを大きくするだけになる
- **根拠**: [NOW] L25／[review/stack_relay_power.md](review/stack_relay_power.md) §0.1-3・§4（1 Ω 以上で 144/144 組とも山なし、22 Ω・バルク無しで fsw 帯 −42.7 dB 以下）／[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 4-1（安定性の懸念なし）／[spice/stack_relay/](spice/stack_relay/)
- **前提・外れる条件**: ch LDO の CIN は 10 µF（DS の強い推奨、[pow] §2）。リセット時に電源接点が開いてから LDO が落ちるまでの余裕は小さくなる（§2-7）
- **却下した案**: 娘ごとに RC ダンパ（35〜45 µF・0.1〜0.2 Ω）— [NOW] L19–20 の旧方針。直列 22 Ω を入れた後は突入を増やすだけ（上の根拠）／親だけにバルク（直列 R なし、**ユーザー案**）— 共振が娘の側に残り、親を盛っても直らない（[review/bulk_parent_sim.md](review/bulk_parent_sim.md) §0.1・§0.2）
- **状態**: いったんの決め（[NOW] L19 の「残す」を L25 で差し替え）

### 3-6 親の +15 V/−15 V に +100 µF は任意

- **決定**: 親のバルク +100 µF は足場として置けるようにし、**要否は RS6 の突入を実測して決める**。実測は基板を起こす前に
- **理由**: 22 Ω・娘のバルク無しなら、RS6 が 300 mA で頭打ちでも親の最低は約 12.25 V で、PT2314E の 9 V は動かない。+100 µF が効くのは RS6 の OLP がヒカップ型か 300 mA 以下で頭打ちするときの保険だけ
- **根拠**: [NOW] L25／[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 2-5・2-6（L7809 の挙動モデル）・2-3（どの R でも RS6 の電流は 300 mA を超える）
- **前提・外れる条件**: RS6 の出力インピーダンスと電流制限の形は DS に無く、シミュレーションは〔仮定〕の上（[review/stack_relay_power.md](review/stack_relay_power.md) §8）
- **却下した案**: 必須にする（[review/stack_relay_power.md](review/stack_relay_power.md) §0.2 の推奨）— 査読で任意に格下げ
- **状態**:
  - いったんの決め: 任意＝足場を置く（[NOW] L25）
  - 要実測: 実装するか。基板を起こす前に（V21-実測-01）

### 3-7 ch LDO: CNR/SS は必須、後ろの容量は合計 22 µF 以下

- **決定**: ch の LDO には CNR/SS（10 nF）を付ける。LDO の出力側の容量は合計 22 µF 以下
- **理由**: CNR 無しだと立ち上がりが電流制限になり、娘のレールが 8.6〜12.6 V まで落ちる。DS 上は安定に必須ではないが、この構成では必須
- **根拠**: [NOW] L25／[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 4-4・2.4（自作の LDO 起動モデル）／[pow] §2（tSS = 1.4 × CNR[nF] ms）
- **前提・外れる条件**: 22 µF の上限は、レール良好のしきい値を 13.0 V に置いていたときの制約。しきい値を約 10.5 V に下げた（§5-1）後は制約が消える、と査読が支持している（[review/rail_detect.md](review/rail_detect.md) §0.2、[review/rail_detect_review.md](review/rail_detect_review.md) 要約 5）
- **却下した案**: —
- **状態**: いったんの決め（CNR/SS 必須・合計 22 µF 以下: [NOW] L25）。**ただし 22 µF の前提（しきい値 13.0 V）はしきい値を下げたことで消えた** → 上限を外すかはユーザー確認待ち（V21-未決-07）

### 3-8 コイル電源は L7805C（PD 12 V からのリニア）

- **決定**: `+5V_COIL` は `BP5293-50` をやめて `L7805C`。入力側の PPTC は、コイルの最悪の同時通電（約 560 mA・30 ms）で切れない値にする
- **理由**: `+5V_COIL` は全娘へ配られ、娘の上でリレーの間を音声の近くに通る。BP5293 は 570 kHz の内部発振器を持ち、軽負荷で間欠動作に入る。聴取中はコイル電流が 0 なので、スイッチングの無いリニアで足りる
- **根拠**: [NOW] L25／[review/arch_zero_base.md](review/arch_zero_base.md) §0.1 #9／[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §0.1（BP5293 の発振器）・§6.1／[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 7-3（最悪 46.7 mA × 12 ＝ 560 mA、リニアでは入力電流＝出力電流で、今の PPTC 0.4 A 保持をパルスの間超える）
- **前提・外れる条件**: PPTC のトリップ曲線は未照合
- **却下した案**: BP5293 のまま — 発振器（上の理由）
- **状態**: いったんの決め（[NOW] L25）

### 3-9 電源系統の独立は b-1、PD 入口に CMC の足場

- **決定**: 「電源系統の独立」は **b-1**（系統ごとに自分のレギュレータ、グランドは 1 点で結ぶ木）と読む。PD の受け端子の直後にコモンモードチョークの足場（0 Ω で素通し）を置く
- **理由**: ADC のグランドの付け替え（§4-4）で ADC の LDO の直流が `A_GND` を通らなくなり、b-1 が成り立つ形になった。ガルバニックに切る読み（b-2・b-3）が効くかは、PD 充電器が音に出ているかで決まり、誰も測っていない
- **根拠**: [NOW] L16／[review/rejected_review.md](review/rejected_review.md) §0（b-1/b-2 の定義）／[review/rejected_review_review.md](review/rejected_review_review.md) §2（b-3〜b-6）／[review/main_power_compare.md](review/main_power_compare.md) §4／[_review](review/main_power_compare_review.md) 1-7（「字義どおり」なのは ADC の LDO の直流についてだけ。AFE は ±15 V から取って `ADC_GND` へ帰る）
- **前提・外れる条件**: PD 充電器の A-B-A（V21-実測-03）で差が高域なら CMC を実装、音声帯なら b-3（PD だけを絶縁）を検討。木が成り立つのはシャーシを 1 点で落とすときだけ（パネル部品の金属部・ジャックのスリーブ・PD モジュールのシェルがパネルに触れる閉路）（[review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) §3.2・§8-1）
- **却下した案**: b-2（一次と音声側を電気的に切る）— ADC の LDO を PD から取る決定と両立しない（帰り道が無くなる）（[review/rejected_review.md](review/rejected_review.md) §3.1-4）
- **状態**:
  - いったんの決め: b-1 の読み、CMC の足場（0 Ω で実装）（推奨をユーザーが受けた、2026-09-25）
  - 要実測: CMC を実装するか（V21-実測-03）

### 3-10 −15 V のプリロード抵抗は足場（DNP、3.0 kΩ）

- **決定**: DC-DC の −Vout と COM の足元に 3.0 kΩ の足場を置き、実装しない（±15 V 間のブリーダではなく −15 V と COM の間のプリロード）
- **理由**: RS6 のクロスレギュレーションは「25 % to 100 % load」で typ だけ規定。1 ch・typ・無音の −15 V は 26.2〜26.7 % で、INA1650 が min 側に振れるか軽い石を挿すと 25 % を割る（軽い端 23.6 %）。3.0 kΩ（5 mA、75 mW）を入れれば軽い端でも 26 % を超える
- **根拠**: [NOW] L16／[review/main_power_compare.md](review/main_power_compare.md) §3.4／[review/dcdc_2stage_review.md](review/dcdc_2stage_review.md) 要約 5・1.2
- **前提・外れる条件**: −15 V が軽いときに電圧がどちらへ振れるかは DS に無い。電圧の偏り自体は、±15 V に直結の負荷をどれも止めない（[review/main_power_compare.md](review/main_power_compare.md) §3.3）。実装は実測で決める（V21-実測-02）
- **却下した案**: —
- **状態**:
  - いったんの決め: 足場（DNP）（推奨をユーザーが受けた、2026-09-25）
  - 要実測: 実装するか（V21-実測-02）

### 3-11 ヘッドホンバッファの電源に RC の足場

- **決定**: ヘッドホンバッファ（OPA1652）の電源に自前の RC を入れられる足場を置く
- **理由**: 32 Ω を鳴らす信号電流（各レール平均 5〜25 mA、瞬時 16〜80 mA）は音声帯で変わる負荷として共有の ±15 V に載る。加えて 32 Ω に連続で出すとバッファの接合温度が定格を超える
- **根拠**: [NOW] L16／[review/main_power_compare.md](review/main_power_compare.md) §1.4・§4（b-5）／[review/main_power_compare_review.md](review/main_power_compare_review.md) 1-2・§3.5（連続正弦で約 0.82 W・+117 °C）
- **前提・外れる条件**: LINE 出力に HP と相関する成分が出るかは未測定（V21-実測-08）。HP の帰りをバッファのデカップの GND へ寄せる配線と組にしないと効きが半分（同 1-7）
- **却下した案**: —
- **状態**:
  - いったんの決め: 足場（推奨をユーザーが受けた、2026-09-25）
  - 要実測: 実装するか（V21-実測-08）

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
- **却下した案**: 分解能を上げること自体を目的にする — v2 の「そもそも: 測定系が答えるべき問いには既に答えが出ている」と同じ
- **状態**: 決定（ユーザー判断 2026-09-25）

### 4-3 結合は差動（INA1650 をタップのバッファの後ろ）、片側（今の形）に戻せる足場

- **決定**: タップのバッファの後ろに INA1650 を置き、− 入力を GND センス線へ、REF を `ADC_GND` へ。逆相を作る反転段は残し、その基準を `ADC_GND` へ移す。ジャンパ／0 Ω で今の片側（Q1）へ戻せる形にする
- **理由**: ch 側のグランドと計測側の `A_GND` の差は、今の片側では信号と直列に乗る（除去 0 dB）。差動なら DS の CMRR（85 dB min、±18 V 条件）で落ち、REF を `ADC_GND` に取れば ADC の電源・グランドの置き場が自由になる（§4-4 の付け替えの前提）
- **根拠**: [NOW] L12／[review/tap_compare.md](review/tap_compare.md) §2.2・[_review](review/tap_compare_review.md) §2.1（「43 dB」は別の差の値で、Q1 の ch↔計測側の差は 0 dB）／[review/adc_gnd_retree.md](review/adc_gnd_retree.md) §2・[_review](review/adc_gnd_retree_review.md) §4／[tap] Q2-2（INA1650: CMRR 85/91 dB、IQ 10.5/12 mA、入力バッファ内蔵）
- **前提・外れる条件**: **そのグランド差が実際に効いているかは測っていない**（V21-実測-07）。効いていなければ Q2 は保険で、実績があるのは Q1（v1 の同じ形で −106 を出した）だけ（[review/tap_compare_review.md](review/tap_compare_review.md) §3）。±15 V での CMRR の規定値は無い
- **却下した案**: INA1620・SSM2141・SSM2143・AD8274・INA134/137・THAT1200 — 入力インピーダンスが低く両脚にバッファが要る、差動アンプとしての CMRR の規定が無い、個別高調波の規定が無い、など（[review/tap_compare.md](review/tap_compare.md) §2.2）／絶縁系の結合は §4-10
- **状態**:
  - 決定: Q2（差動）と、Q1 に戻せる足場（ユーザー判断 2026-09-25）
  - いったんの決め: REF を `ADC_GND`・反転段の基準を `ADC_GND` へ（提案で査読が支持したもの）
  - 未決: GND センス点と切替の形（V21-未決-08）

### 4-4 ADC の LDO は PD 12 V（主電源スイッチの後ろ）から。ADC のグランドの木を付け替える

- **決定**: 計測系の LDO（`+3V3_A` / `+5V_A`）は PD 12 V（ネット `PD_12V_SW`、主電源スイッチの後ろ）から取る。`ADC_GND`–`A_GND` の NetTie をやめ、**グランド選択の 1×3 ヘッダ**で Q2 は `ADC_GND` を `D_GND` 側の葉に、Q1 へ戻すときは `A_GND` 側へ結ぶ
- **理由**: RS6 で ADC を +15 V に載せると、1 ch・max・無音で約 212 mA（定格の 106 %）、HP 最大で約 237 mA（119 %）〔計算: [review/main_power_compare.md](review/main_power_compare.md) §1.5 の 124.8／150.2 mA ＋ `rail_budget.py` の ADC 枝 max 86.9 mA〕。**定格に入らない**。記録の 197.7 mA／98.9 % は INA1650 を足す前の値（[review/v2_carryover.md](review/v2_carryover.md) の訂正 #31）
- **根拠**: [NOW] L10／[review/adc_gnd_retree.md](review/adc_gnd_retree.md) §0.1・§3・[_review](review/adc_gnd_retree_review.md) §0・§3（骨格は覆らなかった。付け替え後は ADC の直流の帰りが `ADC_GND` → ヘッダ → `D_GND` → `PD_GND` と帰り、`A_GND` を通らない）／[review/DECISIONS_v21_review.md](review/DECISIONS_v21_review.md) B2（212 mA の算術）／[scripts/rail_budget.py](scripts/rail_budget.py) `--adc-from-pd`
- **前提・外れる条件**: 1×3 ヘッダ＋シャント 1 個なら、Q1・Q2 を同時に結ぶ閉路は物理的に起きない（[review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) §3.1）。「木」はガルバニックな話で、DC-DC の絶縁容量の輪・`±15V_AFE` の R・筐体の閉路は別（同 §3.2）。PD 給電では電源断のたびに「±15 V はあるが ADC の電源が無い」窓が開く（§4-6）
- **却下した案**:
  - ADC の LDO を +15 V のまま（v2 の「非絶縁バック…を削除。ADC の LDO は `+15V` 直結」）— 上の理由（RS6 の定格に入らない）
  - `ADC_GND` を `PD_GND` へ結ぶ — 木にはなるが I²S の帰りが 2 ホップになる（[review/adc_gnd_retree.md](review/adc_gnd_retree.md) §3.1）
  - ADC 枝の電源に絶縁 DC-DC（v2 の「…を別の DC-DC に替える案」「絶縁コンバータで置き換える案について」）— b-1 の読み（§3-9）では要らない。スイッチング源が 1 つ増える（[review/rejected_review.md](review/rejected_review.md) #2）
- **状態**: 決定（PD 12 V から・付け替えの方向: ユーザー判断 2026-09-25）

### 4-5 ADC の枝に PPTC を新設

- **決定**: PD 12 V から ADC の LDO へ行く枝に PPTC を置く
- **理由**: PD 本線（受け端子 → 主電源スイッチ → `PD_12V_SW`）には枝より手前のヒューズが無く、他の枝はそれぞれ自分の保護を持つ。ADC の枝だけが無保護になる。v2 の「戻さない」は LDO が +15 V（DC-DC の短絡保護の後ろ）にあることが前提だった
- **根拠**: [NOW] L10–11／[review/adc_gnd_retree.md](review/adc_gnd_retree.md) §6.1・[_review](review/adc_gnd_retree_review.md) §2・§7.4／v2 の「ADC 枝の PPTC は戻さない」（[review/v2_carryover.md](review/v2_carryover.md)）
- **前提・外れる条件**: 定格は PPTC の DS（温度ディレーティング）を取ってから（hold 0.25 A 級が候補、未照合）。LDO 前の直列 R はフォールト電流を受けるのでパルス定格のある品（[review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) §6.2）
- **却下した案**: 計測の 5 V レギュレータ入口の PPTC の後ろ（`PD_12V_MEAS`）から取る — PPTC は増えないが、ADC の枝の短絡で Pico も落ち、5 V レギュレータの入力脈流の隣になる（同 §7.4 の表・§10-4）
- **状態**: いったんの決め（[NOW] L11）

### 4-6 ADC 前の直列 47 Ω → 100 Ω（電源断ごとの窓は許す）

- **決定**: ADC を直接駆動するドライバと ADC 入力の間の直列抵抗を 47 Ω から 100 Ω にする。電源を切るたびに開く窓は許す
- **理由**: PD 給電では電源断のとき ADC の電源が ±15 V より先に落ち、その間（約 15〜40 ms）ドライバの出力が ADC 入力のクランプへ流れる。フルスケールで 14〜16 mA pk と PCM1804 の絶対最大 ±10 mA を超えるが、100 Ω なら 6.5 mA
- **根拠**: [NOW] L11／[review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) §7.1・§7.4（代償は ADC 入力 10 kΩ との分圧 −0.09 dB と DS の値からの逸脱）
- **前提・外れる条件**: この構成では 47 Ω はドライバの帰還ループの外にあるので電流を制限できる（DS の図はループの中）（同 §9 訂正の一覧、47 Ω の行）
- **却下した案**: ドライバを `+5V_A` の単電源にする — 構造で解けるが `+5V_A` の負荷と ADC の VCC への信号電流が増え、過剰（同 §7.4 (b)）／何もしない — 窓は「事故のときだけ」ではなく電源を切るたびに開く（同 (c)）
- **状態**:
  - いったんの決め: 100 Ω、窓は許す（[NOW] L11）
  - 未決: VCOM とドライバ +IN の間の 1 kΩ（逆向きの窓の保険。RS6 なら故障時だけの保険）（同 (d)、V21-未決-10）

### 4-7 `±15V_AFE` の直列は 22〜33 Ω

- **決定**: ADC 側のオペアンプ（INA1650・反転段・ドライバ）の ±15 V デカップを `ADC_GND` に揃え、その手前に各レール 22〜33 Ω の直列抵抗（`±15V_AFE`）
- **理由**: デカップを `ADC_GND` に置くと、±15 V のリップル電流が `ADC_GND` → `D_GND` → `A_GND` と渡り、その大きさはほぼ Vripple / R。4.7 Ω だと 265 kHz で最大 10〜21 mA p-p を `A_GND` の星点へ入れるが、22〜33 Ω なら 1.5〜4.5 mA p-p
- **根拠**: [NOW] L11／[review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) §6.1（表）・§9 C3
- **前提・外れる条件**: 33 Ω で V+ が約 13.7 V まで下がっても、INA1650 の同相の上限（V+ − 2 V）はフルスケール 7.74 Vpk の上（同 §1 の表）。ADC の HF の電流（ドライバのキックバック）は `ADC_GND` の中で閉じる（[review/adc_gnd_retree.md](review/adc_gnd_retree.md) §4）
- **却下した案**: 4.7 Ω — 上の理由／フェライトビーズ — 265 kHz ではほとんど効かない（[review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) §6.1）
- **状態**: いったんの決め（[NOW] L11）

### 4-8 INA1650 の RCOM は 0 Ω（1 MΩ に替えられる足場）

- **決定**: INA1650 の COM は 0 Ω で `ADC_GND` へ。1 MΩ に替えられるフットプリントにする
- **理由**: RCOM = 0 ならセンス線が切れても Q1 相当に落ちるだけで、センス線の電流は nA 級。1 MΩ だと断線で −9.5 dB になり、センス線に約 6 µA pk/ch の信号電流が出る
- **根拠**: [NOW] L11／[review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) §4・§9 C1・C2・§10-6／[tap] Q2-2（20 Ω の不整合で 83.7 dB、RCOM 1 MΩ で 89.6 dB）
- **前提・外れる条件**: 源インピーダンスの不整合は 1 Ω 未満の見込みで、RCOM の差は小さい（同 §1 の表）
- **却下した案**: 1 MΩ（[review/adc_gnd_retree.md](review/adc_gnd_retree.md) の推奨）— 上の理由で仮置きは 0 Ω
- **状態**: いったんの決め（仮置き、[NOW] L11）

### 4-9 計測側の予備 12 V 入口は残し、主電源スイッチを迂回する旨を注記

- **決定**: 計測側の予備 12 V 入口とそのヒューズは残し、「ここから給電すると主電源スイッチを迂回する（受け端子から給電しているときはスイッチ後の 12 V が出ている端子になる）」と図に注記する
- **理由**: 予備入口はスイッチ後の `PD_12V_SW` につながっている（査読時の回路図、[review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) §2）
- **根拠**: [NOW] L11／[review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) §2（副作用）・§10-7
- **前提・外れる条件**: 両方から同時に給電すると電源が並列になる（同 §2）
- **却下した案**: —
- **状態**: いったんの決め（仮置き、[NOW] L11）

### 4-10 却下した結合・絶縁の案

- **決定**: 計測タップの経路は、絶縁アンプ・信号トランス・デジタル絶縁・ADC の絶縁島のどれも採らない
- **理由**: どれも −106 dBc（差の検出）を良くする根拠が記録に無く、ADC の電源の置き場を先に決めてしまうか、ADC の隣に新しい高周波源を置く
- **根拠**: [review/tap_compare.md](review/tap_compare.md) §2.3〜§2.5・[_review](review/tap_compare_review.md) §2・§3／[review/rejected_review.md](review/rejected_review.md) #1・[_review](review/rejected_review_review.md) #1
- **前提・外れる条件**: b-2（ガルバニックに切る）を採るなら見直す（§3-9）
- **却下した案**:
  - 絶縁アンプ（ISO224B・AMC3330 ほか）— DS の THD は −84 dB（10 kHz）で 1 kHz 未満の規定が無い。ISO224 の雑音は DS の中で 3 倍食い違い、悪い方なら雑音だけで −106 を割る。内部の ΔΣ・搬送波・DC-DC が ADC の隣に来る（[review/tap_compare_review.md](review/tap_compare_review.md) 6-1・6-2）
  - ライン・トランス（JT-11P-1）— 1 kHz の「<0.001 %」は typ 列で、1320 Hz の H3 とその安定性は DS に無い。二次側にバッファが要り、寸法も不明（同 3-5・6-3）
  - デジタル絶縁（ISO7741 を I²S に）— −106 に効く筋が記録から立たず（「本命」の記録は ADC 自身の床の話）、ADC の電源を ±15 V 側に固定する。部品代ほぼゼロの比較相手（ADC 出力への直列抵抗）がある（同 5-4〜5-6、§3「別枠」）
  - ADC を絶縁した島（v2 の「【却下】ADC を絶縁した島にする案」）— 却下のまま。島が動かすのは測定床の実用律速より下の部分で、装置は計測器ではない（[review/rejected_review.md](review/rejected_review.md) #1）。RS6 で絶縁容量が下がっても「島の性能は DC-DC の絶縁容量で決まる」構図は残る（[review/decisions_audit_1_review.md](review/decisions_audit_1_review.md) 修正の要点 4）
  - PT2314E 境界の絶縁 I²C（`ADuM1250` 級、v2 の「`DGND`(25) はチップの足元で `A_GND` へ」の節。V21-継-05）— b-1 なら理由（`D_GND` はどのみち娘へ引く）は成り立ち、むしろ強まる（[review/decisions_audit_2_review.md](review/decisions_audit_2_review.md) 3.3）
  - USB アイソレータ（`ADuM3160`）— USB を抜いた A/B で床の差 2.9 dB（n=1）（[review/rejected_review_review.md](review/rejected_review_review.md) #10）
- **状態**: v2 の却下を引き継ぐ（v2.1 で個別の判断はしていない。Q2 の選択はこれらを退けた判断ではない）。絶縁アンプ・トランス・デジタル絶縁は v2.1 の査読の順位で採っていないだけで、ユーザーは判断していない

---

## 5. 監視と連動

### 5-1 レール検知はしきい値つき、しきい値は下げる

- **決定**: 娘の ±レールの検知はしきい値で行い、立ち上がり（遅延つき）で音声 SET を許し、立ち下がり（即時）で音声を自動リセット。+ と − の両方。しきい値は 13.0 V から下げる。検知の分圧は **0.1 %**、ただし他の公差・不良にも耐える作りにする
- **理由**: 立ち下がりのしきい値を約 10.5 V まで下げると、ch LDO の起動時の落ち込み（最悪 13.44 V）から離れて迷惑トリップしない。分圧 1 % だと立ち下がり帯の下端が約 10 V を割る
- **根拠**: [NOW] L25／[review/rail_detect.md](review/rail_detect.md) 冒頭（ユーザー決定）・§0.2（0.1 % で帯 10.24〜10.79 V / 11.68〜12.22 V（+））／[review/rail_detect_review.md](review/rail_detect_review.md) 冒頭（ユーザー決定）・要約 3・§2（帯の重なりの判定は不要な条件、1 % の弱点は下端だけ）
- **前提・外れる条件**: 13.0 V のしきい値（[review/stack_relay_power.md](review/stack_relay_power.md) §0.2）は公差込みで窓の上端に張り付いていた（[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 3-7）。EN の保護（EN ≤ IN + 0.3 V）だけなら、しきい値を高く置く必要は DS 上は無い
- **却下した案**: 13.0 V — 上の理由
- **状態**:
  - 決定: しきい値で検知・しきい値を下げる・分圧 0.1 %（ユーザー判断 2026-09-25）
  - 値は案: 立ち上がり ≈ ±12 V・遅延 10〜20 ms／立ち下がり ≈ ±10.5 V（[NOW] L25）

### 5-2 レールは Pico が読む（共通の `MON_P`/`MON_N`、LM4040 で比率校正）

- **決定**: 各娘の分圧したレールをダイオード OR でスタック共通の `MON_P`/`MON_N` に載せ、Pico の ADC で読む。**ADC0 の `DEST_ADC` を解放**して LM4040-2.5 を読み、比率で校正する。しきい値・遅延・読みの妥当性の判定はファーム
- **理由**: 娘の部品が監視 IC 案の約半分で、しきい値をファームで変えられ、読みの妥当性（張り付き・片側だけ等）を見て誤「良」の多くを検出できる
- **根拠**: [NOW] L25／[review/rail_detect_review.md](review/rail_detect_review.md) §7・§8-1（(c) を第一候補）
- **前提・外れる条件**: RP2350 の ADC はオフセット・利得・INL の規定が無く、比率校正が前提。Pico の 3V3 の公差はどの DS にも無い（V21-実測-04）。`DEST_ADC` は v2 で位置センスラダーを廃止した後の空きで、ファームは読んでいない（[NOW] L208）。Pico 2 の `AGND` の扱いは Pico 2 の DS で確かめる（リポジトリに無い）（[review/rail_detect_review.md](review/rail_detect_review.md) §7.1・§10）
- **却下した案**:
  - (a) 娘ごとに窓型の監視 IC（TPS3701 ＋ TPS3808 ＋ LM4040）— 単一の不良（オープンドレインの配線の開放、基準側の抵抗の開放、LM4040 の短絡など）で誤「良」になる経路が 4 つ以上あり、TPS3808 の遅延は CT の公差込みで 9.1〜23.4 ms と 10〜20 ms に入らない。娘 1 枚で IC 約 10 個（[review/rail_detect_review.md](review/rail_detect_review.md) §3.2・§2-3・§1 表）
  - (b) Pico だけ（I²C 経由で切る）— 突然の断では EN が切れる前にレールが割れる（I²C の書き込み 0.29 ms ＋ 待ち 最大約 0.9 ms に対し 0.20 ms）。ファームが止まると何も守られない（同 §7.4・§7.5）
  - ディスクリート（ツェナー＋トランジスタ）だけで精度の層を作る — ツェナーの公差で下端 10 V を守れない（[review/rail_detect.md](review/rail_detect.md) §2.2）
- **状態**: いったんの決め（[NOW] L25）

### 5-3 `RAIL_OK` を Pico から直接（Pico が High を出している間だけ「良」）

- **決定**: Pico の空き GPIO から直接 `RAIL_OK` をスタックへ出す。**Pico が能動的に High を出している間だけ「良」**（外付けプルダウン）。娘の上で EN の許可と音声 SET のゲートに AND し、立ち下がりで音声リレーをリセット。Pico のリセット・停止で全段の音声がリセットされる
- **理由**: I²C（100 kbit/s・共用）経由では突然の断に間に合わない。直結の GPIO なら EN が 0.1〜0.2 ms で切れる。既定が「不良」なのでフェイルセーフの向き
- **根拠**: [NOW] L25／[review/rail_detect_review.md](review/rail_detect_review.md) §7.4・§7.5・§9 R3
- **前提・外れる条件**: ファームがハングして High を出し続ける形は残る → §5-4 の後ろ盾で塞ぐ。BOOTSEL・デバッガの停止・起動中はウォッチドッグも助けない（同 §7.5）
- **却下した案**: 娘がオープンドレインで引き下げる PG 線 — 電源の無い娘が線を放すと既定が「良」になる向き（[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6.3-3）
- **状態**: いったんの決め（[NOW] L25）

### 5-4 精度の要らない後ろ盾（B1・B2）

- **決定**: **B1**: 音声 SET のコイル電源を、娘の ±レールがおおむねある（約 ±7 V を越える）ときだけ ON になる PMOS 越しにする（ツェナー＋トランジスタ）。どこが開放しても SET 不可に倒れる。RESET のコイル電源は常時の `+5V_COIL` のまま。**B2**: その「レールがある」信号の立ち下がりでもリセットの単安定を撃つ
- **理由**: 精度の層（§5-2）が誤「良」で固まっても、電源の無い娘の音声がバスにつながる形をハードで消せる。AZ850P2 は SET と RESET のコイルの＋端子が別ピンなので、SET 側だけをゲートできる
- **根拠**: [NOW] L25／[review/rail_detect_review.md](review/rail_detect_review.md) §3.3・§8-2／[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6.3-6
- **前提・外れる条件**: 部品の DS は未収集。TBD62083A のクランプの COMMON をどちらへ繋ぐかは要整理（同上）。B1 は §2-6（音声 SET を共通にした決定）の理由そのもの
- **却下した案**: —
- **状態**: いったんの決め（[NOW] L25）

### 5-5 レールが落ちたら音声を自動リセット、EN も切る

- **決定**: レールが落ちたら音声リレーをハードで自動リセットする。同じ信号で ch の LDO の EN も切る
- **理由**: 接点の瞬断や衝撃で電源が切れても、音声がバスにつながったまま・ミュートも掛かっていない状態が残る。EN を切らないと EN が IN を超えうる（§2-9）
- **根拠**: [NOW] L25／[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 6-3（自動リセットの経路が無いという指摘）／[review/rail_detect.md](review/rail_detect.md) §0.3／[review/rail_detect_review.md](review/rail_detect_review.md) §8-1
- **前提・外れる条件**: 律速はリレーの復帰時間（AZ850 は 1 ms typ、max は DS に無い、V21-実測-05）。SET と RESET のコイル電流の重なりは µs ではなく sub-ms〜ms になりうるが、リセットパルスが長いので最後はリセットで終わる（[review/rail_detect_review.md](review/rail_detect_review.md) 2-4）。電源リレーまで自動で切るかは未決（[review/rail_detect.md](review/rail_detect.md) §0.5 D5、V21-未決-06）
- **却下した案**: —
- **状態**: いったんの決め（[NOW] L25）

### 5-6 TBD62083A は 5 V 振幅で駆動（`+5V_COIL` の AHCT を 1 段）

- **決定**: コイルドライバ TBD62083A の入力を、`+5V_COIL` で動く AHCT 系を 1 段通して 5 V 振幅にする
- **理由**: TBD62083A の出力電圧（VDS）は VIN = 5 V の条件でしか規定されていない。3.3 V 駆動で保証されるのは「100 mA で VOUT = 2 V」だけで、コイル端の電圧が感動電圧に届く保証が無い。自動リセットという安全機能がこの保証外に乗っていた
- **根拠**: [NOW] L25／[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §0.2-5／[review/rail_detect_review.md](review/rail_detect_review.md) §5-1・§8-3／[sw] §3（TBD62083A）
- **前提・外れる条件**: AHCT の DS は未収集。LVC を 5 V で動かすと 3.3 V の信号を受けられない（同 §5-1）。TBD62083A は VCC ピンが無く入力電圧だけで動くので、電源の無い娘にもリセットが届く（[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6.1）
- **却下した案**: 3.3 V で直接駆動 — 上の理由（v1/v2 で動いた実績はありうるが DS の保証ではない）
- **状態**: いったんの決め（[NOW] L25）

### 5-7 ±15 V の有無を Pico へ知らせる

- **決定**: ±15 V（スタックの常時側）の有無を Pico が読めるようにし、ファームは ±15 V が無い間は電源 SET も EN も出さない
- **理由**: Pico は USB だけで動くので、主電源 OFF でも `3V3` と制御線が生きている（§2-9 の EN–IN の件）
- **根拠**: [NOW] L15／[review/main_power_compare_review.md](review/main_power_compare_review.md) §3.3
- **前提・外れる条件**: 形は未決（`MON_P`/`MON_N` で兼ねるか、親の +15 V を別に分圧して読むか）
- **却下した案**: —
- **状態**:
  - 決定: 検知線を置く（[NOW] L15）
  - 未決: 形（V21-未決-23）

---

## 6. ファームの責務

ハードが保証することと、ファームが守ることを分けて置く。ハードの後ろ盾は「ファームが間違えたときに壊さない・つながない」ためのもので、手順そのものはファームが持つ。

### 6-1 ハードが保証すること（ファームに依らない）

各行の状態は右端の項目の状態に従う。

| 何を | どうやって | 項目 |
|---|---|---|
| レールの無い娘は音声 SET できない | B1（音声 SET のコイル電源をレールでゲート） | §5-4 |
| レールが落ちたら音声リセット、EN 切り | B2 と `RAIL_OK` の立ち下がりで単安定 → RESET コイル。EN の許可にも AND | §5-4・§5-5 |
| Pico が止まったら全段の音声リセット | `RAIL_OK` は Pico が High を出している間だけ良 | §5-3 |
| 電源の無い娘にもリセットが届く | コイル電源と全リセットは常時系統、TBD62083A は VCC 無し | §2-1・§5-6 |
| EN が LDO の IN を超えない | EN の論理を娘の切られたレールから | §2-9 |
| 娘の中で同時に ON は 1 ch まで、既定 OFF | デコーダ | §2-9 |
| 切ったノードが浮かない | NC 抵抗 → GND、`TONE` バスに 100 kΩ | §2-3・§2-11 |
| 極間短絡で ±15 V を直結しない | 22 Ω を NO 側、溶断型 | §2-4 |

### 6-2 ファームが守ること

- **厳密に 1 ch**: 全 OFF → 1 ch ON。温めておく ch は作らない（§1-2）。状態: 決定
- **切替の手順（娘をまたぐとき）**: ミュート → **全リセット（全娘の音声リレーと電源リレー。音声が先・電源が後、例: ARST → 20 ms → PRST）** → 選んだ娘の電源 SET → レール良好（立ち上がりのしきい値 ＋ 遅延）→ ch 選択 → 整定待ち → **共通の音声 SET** → ミュート解除（[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6.3-9、[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 6-1）。状態: 決定（全リセットから始め、音声 SET をこの中でだけ出す: §2-6）／いったんの決め（音声を先・電源を後の順: §2-7）
- **音声 SET の規則**: 音声 SET は、上の「全リセット → 電源 SET → レール良好 → 共通の音声 SET」の 1 つの手順の中でだけ出す。それ以外で音声 SET を出さない（§2-6）。状態: 決定（ユーザー判断 2026-09-25）
- **同じ娘の中で ch を変えるとき**: ミュート → ch を全 OFF → 番地 → ch を ON（TMUX と LDO の EN が同時に切り替わる）→ LDO の立ち上がり（CNR 10 nF で正側 14 ms・負側 9 ms、[pow] §2・§3）＋整定待ち → ミュート解除。境目のリレーは動かさない（[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6.3-9）。状態: 未決（推奨。[NOW] に無い）
- **パルス幅**: コイルのパルスは 20 ms 以上（Panasonic の「セット・リセット時間の 5 倍以上」、AZ850 の typ 2 ms の 10 倍）。SET と RESET のコイルに同時に電圧を加えない（[review/stack_relay_power.md](review/stack_relay_power.md) §6、[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 8-1、[bnd] §3.3 TQ）。状態: 未決（推奨。[NOW] に無い、V21-未決-24）
- **EN を上げる条件**: ±15 V があることを確かめてから（主電源スイッチ OFF で Pico が USB だけで動いているときに EN を上げない）（§2-9・§5-7、[review/main_power_compare_review.md](review/main_power_compare_review.md) 1-6）。状態: 決定（§5-7）
- **レール監視**: `MON_P`/`MON_N` を読み、LM4040 を ADC0 で読んで比率校正。しきい値（案: 約 ±12 V / 約 ±10.5 V）と遅延をファームで持つ。張り付き・片側だけなどの妥当性を見る。`RAIL_OK` は能動的に High を出し、異常では落とす（§5-1〜§5-3）。状態: いったんの決め
- **迷惑トリップを無限に再試行しない**（誤「不良」で EN 切り → 回復 → 良 → EN → 落ち込み…を繰り返しうる）（[review/rail_detect_review.md](review/rail_detect_review.md) §3.1）。状態: 未決（推奨）
- **電源投入時**: 全リセットから始める（ラッチングリレーは停電前・衝撃の状態を保持しうる、§2-1）。PT2314E には電源投入後 50 ms は I²C を送らない（v2 の「電源投入後 Td ≈ 50 ms は叩かない」、[sw] §5）。PT2314E の I²C は 100 kbit/s（3.3 V ロジック × VDD 9 V で Standard）。状態: 決定（全リセット: §2-1）／v2 から引き継ぎ（PT2314E）
- **運用**: 娘は電源を切ってから抜き挿しする。挿したら起動し直す（起動時の全リセットで前歴を消す。セットのまま外した娘を電源の入った箱へ挿すと、音声が前歴のままバスにつながり、起動時のリセットは走らない）（[review/stack_relay_power_review.md](review/stack_relay_power_review.md) §3 (e)）。状態: 未決（推奨、V21-未決-25）
- **待ち時間の目安**: ch の入力結合の整定は 5τ で 0.5 s 級。ミュートの長さは τ の取り方で変わる（§2-10 の前提）。状態: 未決（V21-未決-01、V21-実測-12）

---

## 7. v2 から引き継ぐもの

v2 から引き継いだ決定。どれも状態は「**v2 から引き継ぎ（v2.1 で再考していない）**」— v2 で決めたことを、v2.1 の前提で見直さずにそのまま持っている。
どれを引き継ぐかは棚卸し（[audit_1](review/decisions_audit_1.md)・[_review](review/decisions_audit_1_review.md)／[audit_2](review/decisions_audit_2.md)・[_review](review/decisions_audit_2_review.md)／[audit_3](review/decisions_audit_3.md)・[_review](review/decisions_audit_3_review.md)）の「維持」から選んだ。「前提変更」で原則だけ引き継ぐものはそう書いた。
棚卸しの行番号は [review/README.md](review/README.md) の基準（`5d2cd25` 時点の v2.1）で読む。**v2 の決定ログは読まない。** ここに書いていない v2 の決定は、v2.1 の決定ではない。

### 7-1 UI・操作

- **V21-継-01 エンコーダ ×3（CH / BASS / TREBLE）**
  - 決定: EC11 系・押し SW 付き ×3。回して候補、押して確定。CH の確定で入るのは入力切替と ch LDO の EN（§2-8）
  - 理由: 操作は v2.1 で変えない。音量と DEST は物理操作子なのでエンコーダに載せない
  - 出典: `FrontPanel.kicad_sch`（ENC）、[datasheets/RotaryEncoder_EC11_generic.md](datasheets/RotaryEncoder_EC11_generic.md)
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）
- **V21-継-02 音量は Amp の後の手回し A50k デュアル ×2（HP / LINE 独立）。IC にしない**
  - 決定: PGA2310・digipot は信号経路に入れない。音量は LCD に出さない
  - 理由: 遠隔操作が要らないので音量 IC を入れる理由が無い（UI・コスト・SNR）。「±5 V で振幅が足りない」は振幅の上限の話で、専用電源を足しても解けない
  - 出典: `FrontPanel.kicad_sch`、[datasheets/TI_PGA2310.pdf](datasheets/TI_PGA2310.pdf)（却下した側）、[PARTS.md](PARTS.md) §2.2（ポット）
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）
- **V21-継-03 出力段: PHONE はユニティバッファ、LINE はポット直出し、ゲインは付けない**
  - 決定: HP のバッファは OPA1652（DIP-8 ソケット）、LINE はバッファ無し。バッファは全 ch に共通に掛かるので、1 回の比較の中では差し替えない
  - 理由: ワイパー（最大 12.5 kΩ）では 64〜120 Ω を駆動できない。LINE の相手はアクティブスピーカー。つなぐ実機（HD 560S 120 Ω・Cloud III 64 Ω）では出力は足りないのでなく過剰で、ゲインを足すとポットの使用域が下端に寄る
  - 出典: [ds_facts/opamps.md](ds_facts/opamps.md) §8（OPA1652 の出力 ±30 mA、p1）、[datasheets/opamps/TI_OPA1652.pdf](datasheets/opamps/TI_OPA1652.pdf)、[PARTS.md](PARTS.md) §0a
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）
- **V21-継-04 DEST は機械スイッチ。リレーは使わない**
  - 決定: DPDT ON–ON 1 本で PHONE↔LINE。MUTE 位置と位置センスのラダーは無い（電源断は PWR SW）
  - 理由: 出口はユーザーが手で選ぶもので、ファームが知る必要が無い。音声経路の接点が増えない
  - 出典: `FrontPanel.kicad_sch`
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）
- **V21-継-05 トーンは PT2314E。`DGND` はチップの足元で `A_GND`。I²C 境界は BSS138 ×2 のレベルシフタ**
  - 決定: Bass/Treble だけ使い、音量は 0 dB 固定。ch 選択の前に置き、全 ch に配る。PT 側のプルアップは `VCC_TONE`（9 V）へ
  - 理由: 無印 PT2314 は買えない（E はピン・外付け網とも同じ）。PT2314E の VIH min 3.0 V に 3.3 V のプルアップでは余裕 0.3 V しか無い。P82B96 は Sx 側の VOL 0.8〜1.0 V が PT2314E の VIL max 1.0 V・RP2350 の VIL 0.8 V を食い切る（`PCA9306` 等の見送りも成立）
  - 出典: [ds_facts/switch_control.md](ds_facts/switch_control.md) §5（PT2314E の VIL/VIH、p12）、[datasheets/Princeton_PT2314E.pdf](datasheets/Princeton_PT2314E.pdf)、[datasheets/RaspberryPi_RP2350.pdf](datasheets/RaspberryPi_RP2350.pdf)。P82B96 の DS はリポジトリに無い（v2 で読んだ値）
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）
- **V21-継-06 HP の固定パッドは付けない（0 Ω）。DNP で後から付けられる足場**
  - 理由: ソケットは ±12 V（§3-3）で、固定 −20 dB は過剰
  - 出典: ルート回路図の HP 経路
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）

### 7-2 計測（Q1 の土台）

- **V21-継-07 計測タップの「+」側にユニティバッファ**
  - 理由: 無いとバスから見た負荷が重くなり、TMUX7612 の H3 が悪くなる
  - 出典: `MeasureControl.kicad_sch`、[ds_facts/tap.md](ds_facts/tap.md)、[review/tap_facts.md](review/tap_facts.md) §2、[datasheets/opamps/TI_OPA1656.pdf](datasheets/opamps/TI_OPA1656.pdf)
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）
- **V21-継-08 ADC 前段の入力抵抗 6.19 k（PT2314E 経路について）**
  - 理由: PT2314E の VOMAX typ 2.6 Vrms × Amp ゲイン 2 を ADC のフルスケールに入れる（ヘッドルームの不足を直した）。LPF の極は変えない。DIRECT の振幅は V21-未決-14
  - 出典: [ds_facts/switch_control.md](ds_facts/switch_control.md) §5（PT2314E の VOMAX）、[datasheets/TI_PCM1804.pdf](datasheets/TI_PCM1804.pdf)、`MeasureControl.kicad_sch`
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）
- **V21-継-09 `MCLK_SENSE` は無い**
  - 理由: ファームが読んでいない。12.288 MHz がグランドの境目を渡る経路が一本減る
  - 出典: `MeasureControl.kicad_sch`、`firmware/board.py`
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）

### 7-3 部品選定の理屈

- **V21-継-10 2.2 µF の出力フィルムは公差でなく耐圧で選ぶ**
  - 決定: 耐圧を上げない。ch 間の揃いは LCR 選別（[PARTS.md](PARTS.md) §0c の MATCH）
  - 理由: フィルムの体積は概ね C×V で、効くのは体積、体積は耐圧で決まる。耐圧を上げると基板に入らない。公差の生む ch 間差は f0 付近の話で可聴帯に効かない
  - 出典: [PARTS.md](PARTS.md) §0c、図のフットプリント
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）
- **V21-継-11 受動部品の型番は回路が固まってから DigiKey API でまとめて選ぶ**
  - 決定: API の入手性の欄は信用せず `ProductUrl` を開く
  - 出典: `scripts/digikey_search.py`、[PARTS.md](PARTS.md) §0b
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）
- **V21-継-12 DIP-28 ソケットは 0.300"・板バネ（dual-wipe）型**
  - 決定: 挿さるのは MCP23017 だけ。娘の MCP を残すかは V21-未決-03
  - 出典: 図のフットプリント
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）
- **V21-継-13 却下のまま（理由は v2.1 でも成り立つ）**
  - 固定 6 V の三端子（7806 級）— `LT1763-5` の実負荷の規定は 6 V < VIN（[ds_facts/power.md](ds_facts/power.md) の LT1763、[datasheets/ADI_LT1763.pdf](datasheets/ADI_LT1763.pdf) p4）
  - Aimtec AM10TW / AM15CW — 絶縁容量 2000 pF、DigiKey では Marketplace 出品（[datasheets/Aimtec_AM10TW-LPZ.pdf](datasheets/Aimtec_AM10TW-LPZ.pdf)、[datasheets/Aimtec_AM15CW-LPZ.pdf](datasheets/Aimtec_AM15CW-LPZ.pdf)）
  - TDK-Lambda CCG — OVP なし・RC 負論理・絶縁容量が非公表（[datasheets/TDK-Lambda_CCG15-30.pdf](datasheets/TDK-Lambda_CCG15-30.pdf)）／CUI PYBE10 — NFND、50 % 未満で周波数を下げる（[datasheets/CUI_PYBE10.pdf](datasheets/CUI_PYBE10.pdf)）
  - Mornsun URA — DigiKey の品が全数 NFND（2026-09-05 に API で確認）
  - MeanWell `NSD10-12D12` — 2″×1″ で新しいフットプリント、最小負荷 20 mA/レール（[datasheets/MeanWell_NSD10-D.pdf](datasheets/MeanWell_NSD10-D.pdf)。§3-1 の却下の行も参照）
  - 入力ヒューズ `T3.15 A` — PD の故障電流の範囲で切れず、保護にならない（今のヒューズの見直しは V21-未決-16）
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）

### 7-4 回路の原則

- **V21-継-14 電源を切るなら出力も切る**
  - 理由: オペアンプの出力は電源が無くても ESD 構造でレールにつながる。§2-8 の前提
  - 出典: [review/arch_zero_base_review.md](review/arch_zero_base_review.md)
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）
- **V21-継-15 電源を切るなら入力も切る（入力クランプ）**
  - 理由: 失敗はスイッチの外で起きる。電源 0 V の石の入力保護がクランプし、結合容量越しに電流が流れる
  - 出典: [ds_facts/opamps.md](ds_facts/opamps.md)（入力保護の行。〔2026-09-25 照合で追加〕の行を含む）
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）
- **V21-継-16 アナログスイッチ自身は、バスにつながっている間は通電しておく**
  - 決定: v2.1 では「バスにつながっている間は」と読む。選んでいない娘の TMUX は電源ごと落とし、境目のリレーで切る（§2-1・§2-8）
  - 理由: 電源の落ちたスイッチは自分のピンでバスをクランプする
  - 出典: [ds_facts/boundary.md](ds_facts/boundary.md)（"Pins are diode-clamped to the power-supply rails."）
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）
- **V21-継-17 出力側のスイッチは 47 Ω の出力抵抗の後ろ**
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）
- **V21-継-18 break-before-make はファームで担保する**
  - 決定: 全 OFF → 待つ → 目標 ON。§6-2 と同じ
  - 出典: [ds_facts/switch_control.md](ds_facts/switch_control.md)（TMUX7612）
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）
- **V21-継-19 グランドは木。結合は系統ごとに 1 か所、2 か所目は閉路。同居は結合ではない**
  - 決定: 同じシート・同じ基板に `A_GND` と `D_GND` があってもネットは別。NetTie は足さない。回路図では表せないので、ルールとして残す（棚卸しの査読で「却下の再検討」から維持へ直した）
  - 出典: 図の NetTie、[review/adc_gnd_retree.md](review/adc_gnd_retree.md)
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）
- **V21-継-20 シャーシは 1 点で落とす**（原則だけ。v2 の木の記述は古い）
  - 理由: 2 点だとシャーシ経由のループになる。落とす先は V21-未決-15
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）
- **V21-継-21 I²S の帰り・クロック結合の注意**
  - 決定: 効く順は `ADC_GND` の帰路を短く（銅箔）→ I²S に直列ダンパ（足場は V21-未決-10）→ 測定中に LCD を電源ごと切れること → Pico の電源を静かにする（効きは小さい）。基板の境目は遅い信号（I²C）のところに置く
  - 出典: [review/tap_facts.md](review/tap_facts.md)、[review/tap_compare.md](review/tap_compare.md)（BCK の周波数の読みは [review/v2_carryover.md](review/v2_carryover.md) の訂正 #12）
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）
- **V21-継-22 基板間はワイヤでなくヘッダのスタック。DIP ソケットに手が届くこと**
  - 理由: 接点と線材を減らす方向が効く。この装置の目的はオペアンプの差し替えなので、ソケットへの手の届きは最大の制約（縦積みでの確認は V21-未決-20）
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）
- **V21-継-23 ヘッダの挿抜寿命は制約にしない**
  - 決定: 電流は縦積みで突入 0.68 A・コイル 560 mA のパルスが加わるので、品番の DS で確かめる
  - 出典: [review/stack_relay_power.md](review/stack_relay_power.md) §7.3
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）

### 7-5 道具・手順の警告

- **V21-継-24 DC-DC は同じ仕様でも絶縁容量が桁で違う。サフィックス違いに注意**（部品選定の罠）
  - 出典: [datasheets/](datasheets/) の各 DC-DC の DS
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）
- **V21-継-25 レール容量は `scripts/sch_facts.py rails` でそのつど回路図から数え直す。数値を文書に書かない**
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）
- **V21-継-26 DC-DC の表の `Fsw` 欄で候補を比べない**
  - 理由: 見出しの条件が full load
  - 出典: RS6 の読みは [review/v2_carryover.md](review/v2_carryover.md) の訂正 #2
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）
- **V21-継-27 同じ前提を渡した並列の結論の一致は、独立の裏付けにならない**
  - 理由: 探索範囲の指定そのものが盲点になる
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）
- **V21-継-28 「USB で 23 dB」を DC-DC 不要の論拠にしない**
  - 理由: 再現は 2.9 dB
  - 出典: [review/tap_facts.md](review/tap_facts.md) §4（「床の悪化は 23 dB ではなく 2.9 dB」の項）
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）
- **V21-継-29 参照番号は「最大値＋1」で採らない。PPTC の下流には `PWR_FLAG`**
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）
- **V21-継-30 買ったことを採用の根拠にしない**（I/O エキスパンダも同じ）
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）
- **V21-継-31 TMUX7612 の DS は表を取り違えやすい**
  - 決定: ±15 V の表と ±20 V の表が別。平坦度の条件は VS ±10 V
  - 出典: [datasheets/TI_TMUX7612.pdf](datasheets/TI_TMUX7612.pdf)、[ds_facts/switch_control.md](ds_facts/switch_control.md)
  - 状態: v2 から引き継ぎ（v2.1 で再考していない）

---

## 8・9. v2.1 では成り立たない v2 の決定・訂正された記録 → [review/v2_carryover.md](review/v2_carryover.md)（2026-09-25 に移した）

---

## 10. 未決・要実測

### 10-1 実測するもの（安い順・基板を起こす前に要るものを先に）

| ID | 何を | 決まるもの | 出典 |
|---|---|---|---|
| V21-実測-01 | **RS6 の突入**（娘の電源リレーのメイクでどこまで出すか）と **OLP の形**（出力ごとか合計か、定電流かヒカップか） | 親 +100 µF の要否（§3-6）、22 Ω での親の落ち込み、極間短絡時の 22 Ω の電力（§2-4）。**基板を起こす前に** | [NOW] L25、[review/stack_relay_power.md](review/stack_relay_power.md) §8、[review/rail_detect_review.md](review/rail_detect_review.md) §10-5 |
| V21-実測-02 | **RS6 の軽負荷での −15 V**（1 ch・無音・軽い石）の電圧と波形、周波数（バーストの有無） | プリロードの実装（§3-10） | [review/rejected_review.md](review/rejected_review.md) §4 D4、[review/main_power_compare_review.md](review/main_power_compare_review.md) §4-1 |
| V21-実測-03 | **PD 充電器 ↔ 12 V のリニア電源／電池の A-B-A（最低 2 回）**、音声出力の床とスパーを外の機材で。差の周波数 | CMC の実装（§3-9）、b-3 の要否 | [review/rejected_review_review.md](review/rejected_review_review.md) §6、[review/main_power_compare.md](review/main_power_compare.md) §4 |
| V21-実測-04 | **Pico の 3V3 の公差**（Pico 2 基板の DS がリポジトリに無い） | 比率校正の前提、監視のしきい値の誤差 | [review/rail_detect.md](review/rail_detect.md) §0.5 D8、[review/rail_detect_review.md](review/rail_detect_review.md) §10-1 |
| V21-実測-05 | **AZ850 のコイルのインダクタンスと最大リセット時間** | SET/RESET の重なり、自動リセットの時間予算（§5-5） | [review/rail_detect_review.md](review/rail_detect_review.md) §10-3 |
| V21-実測-06 | ADC のデジタル動作が音声出力に漏れているか（I²S の 3 本を Pico 側で外す A-B-A。**リセット保持の形は使わない**: 1.37 s でパワーダウンに入る） | デジタル絶縁・直列抵抗の要否 | [review/tap_compare_review.md](review/tap_compare_review.md) 6-6・§4-D |
| V21-実測-07 | ch 側グランドと計測側 `A_GND` の差（タップ入力の短絡点を変えた無信号キャプチャ 2 通り） | Q2 が保険か実益か（§4-3）。v1 での負の結果だけが強い | [review/tap_compare_review.md](review/tap_compare_review.md) 6-5 |
| V21-実測-08 | HP 32 Ω を鳴らす／外すで LINE 出力の A-B-A、TMUX・L7809 のピンの ±15 V の AC | HP バッファの RC の実装（§3-11） | [review/main_power_compare.md](review/main_power_compare.md) §4 (b-5) |
| V21-実測-09 | 石の熱の整定（通電してから何秒で H3・音が落ち着くか） | 切り替えてから聴くまでの待ち（§1-2） | [review/rejected_review_review.md](review/rejected_review_review.md) §6 U2 |
| V21-実測-10 | ADC 系の実電流（電流計を直列に 1 回） | ADC 枝の PPTC・LDO 前の R の定格（§4-5） | [review/rejected_review_review.md](review/rejected_review_review.md) §6 |
| V21-実測-11 | 容量負荷のメイク回数試験（22 Ω・AZ850） | 電源用リレーの品種（§2-2） | [review/stack_relay_power_review.md](review/stack_relay_power_review.md) 1-4 |
| V21-実測-12 | ch を ON してからの出力 DC の整定（NC 10 kΩ・選んでから音声リレーをセットする順も含めて） | ミュートの長さ（§2-10） | [review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6.4、[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 5-3 |

DS を取るもの（リポジトリに無い）: 22 Ω ヒューズ抵抗の品番（単発パルス曲線）、PPTC（RXEF 系）の温度別 hold 電流、AHCT 系、PMOS・ツェナー（B1）、RB160M-30、TPS3307 の MR、Pico 2 基板、5×20 F2A の溶断 I²t、娘の 3.3 V を作る素子（発振器なし）、2.54 mm スタックヘッダの接点定格（突入 0.68 A・コイル 560 mA のパルス、[review/stack_relay_power.md](review/stack_relay_power.md) §7.3）。確かめる事実: PT2314E の POR 直後の音量状態、PCM1804 の VCOM の駆動能力、RS6 の入手性（[review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) §10-11、[review/rail_detect_review.md](review/rail_detect_review.md) §10、[review/main_power_compare_review.md](review/main_power_compare_review.md) §5）。

### 10-2 決めること

| ID | 決めること | 選択肢 | 出典 |
|---|---|---|---|
| V21-未決-01 | ミュートの場所・素子・時間 | ポットの前／HP 入力と LINE 出力／HP 出力の後ろ、常開・常閉・ラッチング・半導体、時間は τ の取り方次第（約 1 s／1.5 s は τ 0.48 s のとき、NC 10 kΩ なら約 21 ms の τ） | §2-10、[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6.4 |
| V21-未決-02 | ch のデコーダの置き場所と EN の形、娘の 3.3 V | 娘（2→4 デコーダ＋FET、レールから 3.3 V）／親。直列 R＋ショットキーを残すか | §2-9、[review/arch_zero_base_review.md](review/arch_zero_base_review.md) §6.4 A1 |
| V21-未決-03 | 娘の MCP23017 を残すか（I²C をスタックに通すか） | 残す（コネクタ +2 本で 2×12 に入らない）／親からのレベル線だけ | [NOW] L25、[review/arch_zero_base.md](review/arch_zero_base.md) §0.1 #1、[review/stack_relay_power.md](review/stack_relay_power.md) §7.2 |
| V21-未決-04 | NC 側の抵抗値 | 音声 10 kΩ（4.7〜22 kΩ）、レール 2.2 kΩ（1〜4.7 kΩ） | §2-3、[review/stack_relay_power.md](review/stack_relay_power.md) §0.2 |
| V21-未決-05 | 電源リレーの品種（AZ850P2-5 で両役か） | 1 品種（推奨）／電源だけ 2 A 級 | §2-2 |
| V21-未決-06 | リセットの順序をハードでも保証するか、PRST を音声リセットの OR に入れるか、自動リセットを電源リレーにも入れるか | — | §2-7・§5-5、[review/rail_detect.md](review/rail_detect.md) §0.5 D5・D6 |
| V21-未決-07 | ch LDO の後ろの容量の上限（22 µF）を外すか | 前提（しきい値 13.0 V）は消えた、という査読の読みを採るか | §3-7 |
| V21-未決-08 | GND センス点と Q1/Q2 の切替の形 | 娘→母板のコネクタの `A_GND` ピン際 1 点（推奨）／外部取り出し端子の GND／娘に専用ピン。1×3 ヘッダ＋シャント／スライドスイッチ | §4-3、[review/adc_gnd_retree.md](review/adc_gnd_retree.md) §5・§7.4 |
| V21-未決-09 | 計測側の予備の音声端子（2P、GND 極なし）を 3P にするか外すか | — | [review/adc_gnd_retree.md](review/adc_gnd_retree.md) §7.4-10 |
| V21-未決-10 | ADC 入力の逆向きの窓の保険（VCOM–ドライバ +IN に 1 kΩ）、I²S の直列抵抗（0 Ω の足場） | — | §4-6、[review/adc_gnd_retree.md](review/adc_gnd_retree.md) §6.4 |
| V21-未決-11 | LDO 前のフィルタの形 | 入口の電解を低 ESR に／足元を 1 µF に／2 段 | [review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) §6.2・§10-2 |
| V21-未決-12 | v2.1 の試験レベル | バス 3.70 Vrms（−3.4 dBFS、DUT は v1 より +5.5 dB）／v1 と同じ DUT 振幅（−8.9 dBFS、平均を増やす） | [review/tap_compare_review.md](review/tap_compare_review.md) §2.3・§4-A |
| V21-未決-13 | ch 側の入力 220 kΩ を戻すか | 入力スイッチを先に閉じ 5τ 待てば聴こえるバスに出る前に吸収される。安い保険 | [review/rejected_review.md](review/rejected_review.md) #6、[_review](review/rejected_review_review.md) #6 |
| V21-未決-14 | DIRECT の置き方と切替、ライン入力の振幅の定義 | — | §1-5、[NOW] L27 |
| V21-未決-15 | シャーシを 1 点で落とす先（パネル部品の金属部のグランドの扱いを含む） | — | [review/adc_gnd_retree_review.md](review/adc_gnd_retree_review.md) §8-1・§10-8 |
| V21-未決-16 | 入力ヒューズ（今の F2A 速断のままか）と DC-DC 入口の電解の耐圧・ESR | 突入の I²t は 0.007〜0.034 A²s の見積もり。RS6 の DS に推奨ヒューズは無い | [review/main_power_compare_review.md](review/main_power_compare_review.md) 1-6・§4-7 |
| V21-未決-17 | 娘の最終枚数 | 固定側・レール容量・故障時の ch 数が枚数に比例（電源 SET は 4 本＝4 枚まで） | [review/main_power_compare_review.md](review/main_power_compare_review.md) §4-8、§2-5 |
| V21-未決-18 | 議論中の回路: Cf の足場、高速娘の網、バイアス | — | [NOW] L28 |
| V21-未決-19 | PCB: グランドの NetTie 群とグランド選択ヘッダを 1 か所に寄せる、`ADC_GND` の島は 1 か所でしか外とつながらないゾーンに。縦積みのリレーは上下・隣とも 5 mm 以上離す（DS の制約、§2-1） | — | [review/adc_gnd_retree.md](review/adc_gnd_retree.md) §7.4-13、[review/stack_relay_power_review.md](review/stack_relay_power_review.md) §3 (c) |
| V21-未決-20 | 縦積みで下の段の DIP ソケットに手が届くか（V21-継-22） | 積み方・段の数・挿し替えの手順 | [review/decisions_audit_3_review.md](review/decisions_audit_3_review.md)（3884 の補足） |
| V21-未決-21 | 6 W 低 Ciso 群（10〜20 pF、±200 mA 上限）を主電源の比較に入れるか | 軽負荷の振る舞い・Cout・入力範囲を満たすかは誰も見ていない。RS6 はこの群より絶縁容量が 5〜10 倍悪い | §3-1・[review/v2_carryover.md](review/v2_carryover.md)、[review/decisions_audit_1_review.md](review/decisions_audit_1_review.md) 修正の要点 3 |
| V21-未決-22 | 2×12 の内訳（`PG_N` を残すか、予備の GND を何本にするか） | — | §2-5、[review/stack_relay_power.md](review/stack_relay_power.md) §7.2、[review/rail_detect_review.md](review/rail_detect_review.md) §7.3・§7.6 |
| V21-未決-23 | ±15 V の有無を Pico へ知らせる検知線の形 | `MON_P`/`MON_N` で兼ねる／親の +15 V を別に分圧して読む | §5-7 |
| V21-未決-24 | コイルのパルス幅 | 20 ms 以上（推奨） | §6-2、[review/stack_relay_power_review.md](review/stack_relay_power_review.md) 8-1 |
| V21-未決-25 | 活線で娘を抜き挿ししない運用 | 電源を切ってから抜き挿し・挿したら起動し直す（推奨） | §6-2、[review/stack_relay_power_review.md](review/stack_relay_power_review.md) §3 (e) |
