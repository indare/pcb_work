# NJW1194 の代替（`review/njw1194_alternatives.md`）の否定側査読

- 作成: 2026-09-26（否定側査読のエージェント、読み取り専用）。書いたのはこのファイルだけ
- 状態: 書きかけ（コンテナ再起動に備えて早めに保存している）
- 対象: [njw1194_alternatives.md](njw1194_alternatives.md)（以下「対象」）
- 凡例: [DEC] §n = `AudioV2.1/DECISIONS.md`／〔DS 品名 p.n〕= `AudioV2.1/datasheets/tone/` の PDF（`pdftotext -layout`、結論を左右する頁は `pdftoppm -png -r 150` の画像で確かめた）／〔計算〕〔推論〕〔仮定〕／「確かめられず」＝根拠がリポジトリに無い
- `AudioV2/`・`Audio/` の文書は読んでいない

## 作業メモ

### M1. BD3814FV

- 画像で確認（p5・p6）: 制御語 ① は D16–D13 Treble（4 bit）・D12–D9 Bass（4 bit）・**D8 Tone（1 bit）**・D7–D3 は "*"（0 か 1）・D2–D0 の選択番地 000。② は FR 音量 D16–D10（7 bit）・FL 音量 D9–D3（7 bit）〔DS p5 画像〕。**符号表（D8 の 0/1、Bass/Treble の 4 bit、音量の 7 bit）はどの頁にも無い** — 対象を支持
- 応用回路 p6: FL/FR は IN → 10 µ → Ri=20K のラダー（MASTER VOLUME 0〜−95 dB 1 dB/step, MUTE）→ ワイパが (a) 2 接点スイッチの片側へ直、(b) BASS → TREBLE → スイッチのもう片側 → バッファ → OUTFL/OUTFR〔DS p6 画像〕— 対象を支持
