# AudioV2 シンボル／回路図 修正 TODO（クラウドエージェント用）

**ベースブランチ:** `cursor/manual-volume-kicad-2c9e`（remote 最新）  
**親 PR:** https://github.com/indare/pcb_work/pull/23  
**根拠:** [SYMBOL_REVIEW_SUMMARY.md](SYMBOL_REVIEW_SUMMARY.md)（4視点レビュー統合）

**禁止:** `Audio/` 直下の既存 `.kicad_sch` を改変しない。`--no-verify` でコミットしない。

**共通検証（各 WP 完了時）:**

```bash
python3 Audio/scripts/check_sexpr.py -q AudioV2
# シンボル lib を触ったら:
kicad-cli sym export svg -o /tmp/audiov2-sym AudioV2/AudioV2.kicad_sym
# シートを触ったら:
cd AudioV2 && kicad-cli sch export netlist -o /tmp/audiov2.net AudioV2Case.kicad_sch
```

ブランチ名は `cursor/<descriptive>-2c9e`。完了したら commit → push → PR（base=`cursor/manual-volume-kicad-2c9e` または `main` に積み上げる場合は親 PR と調整）。

---

## WP-A — シンボルライブラリ本体（ファイル衝突少）

**担当ファイル:** `AudioV2/AudioV2.kicad_sym` のみ（必要なら `CIRCUIT_DESIGN.md` 1 行追記）

| ID | 作業 | Done |
|---|---|---|
| A1 | ライブラリ末尾の **二重 `(embedded_fonts no)`** を除去（シンボル内の 1 個は残す）。`kicad-cli sym export svg` が **3 シンボルとも成功**すること | [ ] |
| A2 | PT2314 の float 座標（例 `13.970000000000002`）を **2.54 グリッドの有限小数**に正規化 | [ ] |
| A3 | 可能なら property に KiCad 10 系の `(show_name no)` 等を他カスタムシンボルと揃える（任意） | [ ] |

**完了条件:** `kicad-cli sym export svg … AudioV2.kicad_sym` exit 0。sexpr OK。

---

## WP-B — embed / pin_connect / 再生成（メイン）

**担当ファイル:** `AudioV2/scripts/sch_helpers.py`, `AudioV2/scripts/wire_circuit_design.py`, 再生成後の `*.kicad_sch`

| ID | 作業 | Done |
|---|---|---|
| B1 | `embed_lib_symbols`: `(extends …)` シンボルを **親のピン付き定義へ flatten** して埋め込む。対象: `LM7809_TO220`←`LM7805`, `MCP23017-E/SP`←`MCP23017x-x-SO`。ネットリストで U3/MCP の **pins が空でない**こと | [ ] |
| B2 | `SYMBOL_SOURCES` の OLED: `ER_OLEDM0.91`（128×32）をやめる。**128×64 用途** — 当面は `Connector:Conn_01x04_Pin` 等のヘッダ＋注記「2.42″ OLED I2C」でも可。Value/FP に 0.91 / 128×32 を残さない | [ ] |
| B3 | `pin_connect` / PowerModule 配線を修正。ジャンクション `(83.82, 45.72)` 付近で **PD_GND・F1・DKMW ±Vin・R.C.・7809 GND が同一ネットに合流しない**こと。一次／二次（A_GND）を混ぜない。R.C. は DS どおり（通常オープン or 仕様どおり） | [ ] |
| B4 | `CTRL_LIBS` / `OUTPUT_LIBS` を実配置に合わせ、未使用埋め込みを削減 | [ ] |
| B5 | `python3 AudioV2/scripts/wire_circuit_design.py all` で再生成 → sexpr / netlist | [ ] |

**完了条件:** PowerModule 一次短絡が消える。LM7809/MCP がピン付き。OLED 埋め込みに 0.91″ が残らない。sexpr 0。

---

## WP-C — ドキュメント／足場の毒抜き（軽量・並行可）

**担当ファイル:** docs + `generate_kicad_scaffold.py` 注意書き（大規模 PGA 巻き戻し再実行はしない）

| ID | 作業 | Done |
|---|---|---|
| C1 | `CIRCUIT_DESIGN.md` チェックリストに WP-A/B 項目を反映（未完/完了） | [ ] |
| C2 | `generate_kicad_scaffold.py` / `KICAD_SCAFFOLD_TODO.md` 先頭に **「手回し化後は wire_circuit_design.py を使え。scaffold 再実行で PGA に戻る」** 警告 | [ ] |
| C3 | `PARTS.md` に「図上 Value への MPN 記載はレイアウト時」と現状を明記（任意） | [ ] |
| C4 | 未追跡 `PowerModule-bom.xml` は **コミットしない**（.gitignore 推奨） | [ ] |

---

## WP-D — 否定レビュー再検（別エージェント・コンテキストなし）

**入力:** この TODO の Done 状況 + [SYMBOL_REVIEW_SUMMARY.md](SYMBOL_REVIEW_SUMMARY.md) + 現行ツリーのみ。  
**事前会話・他エージェントの「直した」主張は信用しない。** 自分でコマンドを再実行する。

| ID | 確認 | Done |
|---|---|---|
| D1 | `AudioV2.kicad_sym` が load できる | [ ] |
| D2 | PowerModule に一次短絡ジャンクションが無い（ネットリスト or 座標検査） | [ ] |
| D3 | LM7809 / MCP23017 埋め込みにピンがある | [ ] |
| D4 | OLED 埋め込みが 0.91/128×32 でない | [ ] |
| D5 | 残リスク一覧（Relay 未配線・親 hier・ENC 未結線等）を更新 | [ ] |

**判定:** `PASS` / `CONDITIONAL` / `FAIL` を一言で。FAIL ならブロッカーを最大 3 つ。

---

## 作業分担（推奨）

| エージェント | 担当 | ブランチ例 |
|---|---|---|
| Cloud-A | **WP-A** | `cursor/audiov2-sym-lib-fix-2c9e` |
| Cloud-B | **WP-B** | `cursor/audiov2-embed-wire-fix-2c9e` |
| 親（本ラン） | TODO/要約のメンテ、WP-C の一部、完了後に **WP-D をコンテキストなしで起動** | — |

WP-A と WP-B が両方 `*.kicad_sch` の埋め込みを触る場合は **B が A の後に再生成**するか、B が A の sym 修正を取り込んでから `wire_circuit_design.py all`。

---

## 変更履歴

| 日付 | 内容 |
|---|---|
| 2026-08-30 | 初版 — 4視点レビュー後の修正 TODO |
