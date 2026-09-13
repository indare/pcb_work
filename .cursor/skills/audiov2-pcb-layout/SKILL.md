---
name: audiov2-pcb-layout
description: >-
  AudioV2 PCB 配置・配線の判断にメーカー横断ガイドと主要部品 DS の Layout 節を使う。
  Use when routing or placing AudioV2 PCB (AmpBankSwitch, parent rough, zones,
  A_GND/D_GND, TMUX7612, OPA165x, MCP23017), when the user asks about PCB layout
  guidelines, manufacturer app notes, or 配線／配置／ベタ／デカップ.
---

# AudioV2 PCB 配置・配線（メーカー資料）

## いつ読むか

- 親／娘の配置・配線・ベタ・デカップを進めるとき
- A↔D グラウンド、SEL／アナログ並走、ビア位置を決めるとき
- 「メーカーの推奨は？」と聞かれたとき

回路図から導出できる数値はここに書かない（[SOURCE_OF_TRUTH.md](../../../SOURCE_OF_TRUTH.md)）。
現況・凍結判断は [AudioV2/NOW.md](../../../AudioV2/NOW.md)。

## 判断の優先順

1. **プロジェクト既決**（NOW / 既存配線方針）を壊さない  
   例: 娘 v0.1 凍結、A↔D は親 `NT1603` 一点、AMP_SEL は B.Cu、TSSOP パッド上ビア禁止
2. **メーカー横断ガイド**（グラウンド哲学・区画・多基板）→ [reference.md](reference.md) §1
3. **当該部品の DS Layout / Power** → [reference.md](reference.md) §2
4. 一般高速 AN（SCAA082 等）は補助。音響帯でも「並走禁止・デカップ直近」は有効

## エージェントの手順

1. 対象ネット／部品を特定する（ネット名で語る。designator に依存しない）
2. [reference.md](reference.md) で該当メーカー＋部品のリンクを開く（必要なら PDF を取得）
3. 推奨を **この基板の既決** と突き合わせ、矛盾があれば既決を優先し、差を短く報告する
4. 配線案を出すときは根拠を「DS §…／MT-031／SLYT512」など一次資料名で添える

## AudioV2 で効きやすい要点（要約）

| テーマ | 実務 |
|---|---|
| グラウンド | 系統別ベタ＋星型タイ。二重結合を安易に増やさない。配置で電流を分ける |
| デカップ | ピン直近・低 ESR。ピンと C のあいだにビアを入れない（TI）。TMUX は敏感時ビア回避を検討 |
| アナログ×デジ | 並走禁止、交差は直角。SEL と S/D 音声を離す |
| トレース | 直角コーナー回避（TMUX DS）。電源は幅広低インダクタンス |
| 多基板 | カード間はコネクタの GND ピンと親側一点結合を意識（TI SLYT 多基板節） |

## やらないこと

- 文献を根拠に NOW の凍結（娘 NetTie 見送り等）を勝手に覆す
- 回路図から取れる部品数・ネット一覧をスキルに複製する
- `build_*.py` 全面再生成や生成シートの手直しを「Layout 改善」で正当化しない

## 詳細

文献 URL・部品対応表は [reference.md](reference.md)。
