# トーンの 4 案の比較（`review/tone_options_compare.md`）の否定側査読

- 作成: 2026-09-26（否定側査読のエージェント、読み取り専用）。書いたのはこのファイルだけ
- 状態: 作業中（調べながら書き足している）
- 対象: [tone_options_compare.md](tone_options_compare.md)（以下「対象」）
- `AudioV2/`・`Audio/` の文書は読んでいない

## 作業メモ（調べた順）

- M0: 対象・CLAUDE・NOW・DECISIONS（§1-1・§1-5・§2-1・§2-10〜12・§6-2・§7-1）・[TCBR] 全文を読んだ
- M1（途中）: NJW1194 p1・p8 を画像で確認 — セレクタ → 音量ラダーのワイパ → TSW の 2 接点（ワイパ直／TONE の戻り）→ 出力アンプ。TONE ブロックの入力はワイパの節。音量 MUTE なら TSW の両接点とも音楽は乗らない
- M2（途中）: PT2314E p11・p12（表）・p13（THD vs 振幅、9 V: 1 V で約 0.03 %、2 V で約 0.1 %、低い振幅側の傾きは雑音の床）・p14（残留雑音 A 重み 9 V で約 7 µV）を画像で確認。比べる石の THD は ds_facts/opamps.md に無く、各 DS の表（条件がばらばら）
- M3（途中）: PCM186x p13・PCM512x p1・p8、NJW1194 p3〜p5・p22、PGA2310 p1・p5、AmpChannel の 20 k/20 k を確認
