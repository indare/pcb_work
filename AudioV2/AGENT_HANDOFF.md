# AudioV2 エージェント引き継ぎメモ

**更新:** 2026-08-31（ローカル `DESK01`）  
**目的:** クラウド↔ローカル切替で会話 UI が分岐／短く見えることがあるため、別チャットからでも再開できるようにする。  
**作業の正:** 常に git ブランチ **`main`**（歴史的な `cursor/audiov2-*` 等は base にしない）。

関連:

- ルール: `.cursor/rules/work-on-main.mdc`
- ローカル会話: [Power/PD 整理系](37c7411c-c7bb-4644-9194-686ff5fe1fd5)

---

## 1. いま何をしているか（一言）

**PowerModule を実配線寄りに整理した**（PD 入口・パネル SW・VCC_TONE 端子）。  
ControlPanel に PWR SW + 12V LED を戻し、Case は論理橋のまま。  
次の話題候補: PD 往復端子の要否（入口 A vs B）、RelayBoard 本配線、ERC 残り。

---

## 2. 設計の確定事項（忘れないこと）

| 項目 | 内容 |
|---|---|
| 最終音量 | **手回しデュアルポット**（PGA / digipot 不採用） |
| DEST | トグル＋抵抗ラダー |
| Tone | PT2314。電源は **`VCC_TONE`(+9)** ← Power LM7809 |
| 基板分割 | **Power ≠ Control**。Control+Output 同居可。Power 同居は非推奨（GND/熱/EMI） |
| 隔離 | 一次 `PD_GND` ≠ 二次 `A_GND`。DKMW **R.C. = NC（オープン=ON）** |
| Output | `SW_SP3T`×2。Amp は図外 |

詳細: `DECISIONS.md` / `CIRCUIT_DESIGN.md` / `PARTS.md` / `WIRING.md`

### 2.1 PowerModule 現状（2026-08-31）

```text
J202 ← PD module (1=GND 2=+12)
        → PD_12V ──(Case)──► ControlPanel SW1 + D503 LED
                              → PD_12V_SW ──(Case)──► F201 → U201 DKMW +Vin
        PD_GND ←→ 一次（LED 戻りもここ）

U201 → ±12 / A_GND → J201（星型幹線 3P）
+12 → U202 LM7809 → J203 VCC_TONE OUT (1=A_GND 2=+9) → ControlPanel PT2314
```

| コネクタ | 役割 |
|---|---|
| **J202** | PD 給電モジュール入（外付け 50224 可） |
| **J201** | `+12` / `-12` / `A_GND` 星型出 |
| **J203** | `VCC_TONE` 出（2P。戻りは星点側 A_GND。幹線 A_GND と二重ループにしない） |

- シート注記も上記に更新済み
- **PWR SW / 12V LED の実体は ControlPanel**（フロント PCB）。Power に置かない
- オンボード USB-C / CH224 は外してよい（50224 モジュール代用がデフォルト想定の一つ）

### 2.2 PD 配線トポロジ（未決・議論メモ）

どちらも「SW 後で DKMW」は同じ。違うのは **PD モジュールの差し込み位置**。

| | 入口 | 実配線 |
|---|---|---|
| **A（いまの図）** | Power `J202` | Power→Panel へ未スイッチ HOT+GND、Panel→Power へ SW 済み HOT（**往復端子が必要**） |
| **B** | ControlPanel | Panel で SW 後、Power は `PD_12V_SW`+`PD_GND` だけ（往復の「出し」不要） |

- 守りたい本体は **Power**。ホット切り離しは **ControlPanel**
- 実配線の自然さは B 寄り、電源室に PD を集めるなら A
- **この話題は一旦打ち切り**（2026-08-31）。図は A のまま

### 2.3 GND / VCC_TONE

- `VCC_TONE` 戻り = 二次 `A_GND`（7809 GND と同一。衝突ではなく共用）
- 星型 `A_GND` とトーン用戻りを別ケーブルで両端接続すると **ループ**しやすい → J203 で寄り道（専用 2P）が方針

### 2.4 手持ちオペアンプ（2026-08-31 申告）

正本: **[`Audio/OPAMP_INVENTORY.md`](../Audio/OPAMP_INVENTORY.md)**

NJM5532DD / NJM4580DD / OPA2134PA / OPA1656ID / OPA2604AQ / LME49860NA / LT1364CN8 / **MUSE01**（2石→1DIP変換）・MUSES02D、および OPA828・OPA627AU・OPA1612・OPA2140・OPA1652 の DIP 化モジュール等。

---

## 3. マージ済み PR（このスレッドで扱った範囲）

| PR | 内容 | 状態 |
|---|---|---|
| #22–#28 | 手回し音量〜ラベル結線〜WP-C salvage | 上記履歴どおり。**#27/#28 MERGED** |

### 再発防止

- **禁止:** `generate_kicad_scaffold.py` 再実行。再生成は `wire_circuit_design.py`
- 親シート: 同名シートピンはローカルラベルで橋渡し
- sexpr 編集後は `python3 Audio/scripts/check_sexpr.py -q AudioV2`

---

## 4. 現状の git / 作業ツリー

作業ブランチは **`main`**。クラウド切替前に **push して origin/main と揃える**こと。

履歴ブランチ（`cursor/audiov2-*` 等）は base にしない。クラウドが古い `branchName` を fetch して落ちることがある → tip が必要なら一時復帰のみ。

---

## 5. 回路の完成度

### できている

- Power: PD モジュール入・DKMW・7809・J201/J202/J203・パネル SW ループ（論理）
- Control: SW1 PWR SW + D503 12V LED、PT2314 / Pico / ENC 等
- Output / ラベル結線素案（#27）

### 未着手・優先候補

1. PD 往復端子（A のままなら Power↔Panel 用コネクタ追加）or トポロジ B への図変更
2. **RelayBoard 本配線**
3. ERC 残り（Relay / Case 旧ピン・未配線が主。Power は概ねクリーン）
4. OLED FP、PT2314 未使用入力、Amp 幽霊ピン

### 検証

```bash
python3 Audio/scripts/check_sexpr.py -q AudioV2
cd AudioV2 && kicad-cli sch export netlist -o /tmp/audiov2.net AudioV2Case.kicad_sch
```

Windows: Git Bash + KiCad CLI（`.cursor/rules/kicad-cli-git-bash.mdc`）。

---

## 6. 会話タイムライン要約（追記）

…（〜08-30: ラベル結線・アノテ・クラウド切替）

11. Power をラベル→ワイヤへ整理。−12 デカップ・C217=7809 Cout・C219
12. Case=論理、SW/Volume 実体は子シート。SW/LED を一度 Power に寄せ→**Control に戻す**
13. 外付け 50224 前提。`J202` PD in、`J203` VCC_TONE out。R.C. 明示 NC
14. PD 入口 A vs B・往復端子の議論 → **一旦終了**（図は A）
15. 本メモ更新 → `main` に commit/push（クラウド同期用）
16. 手持ちオペアンプリストを `Audio/OPAMP_INVENTORY.md` に登録

---

## 7. 別チャット再開プロンプト（コピペ用）

```
AudioV2/AGENT_HANDOFF.md を読んで続きから。
ブランチは main（origin と同期済み前提）。
PowerModule は J201/J202/J203 + パネル SW ループ（トポロジ A）。
PD 入口 A vs B は未決（話題打ち切り）。次候補: 往復端子 or RelayBoard / ERC。
generate_kicad_scaffold.py は再実行しない。
```

---

## 8. 触ってよい／だめ

| OK | NG |
|---|---|
| `AudioV2/**` の sch / スクリプト / 文書 | `Audio/` 既存製造図の無闇な改変 |
| `wire_circuit_design.py` での再生成 | `generate_kicad_scaffold.py` 再実行 |
| sexpr 編集後は必ず `check_sexpr.py` | `--no-verify` でコミット |
| 新規作業は **`main`** | 旧 `cursor/audiov2-*` を base |

---

## 9. 変更履歴（このメモ）

| 日付 | 内容 |
|---|---|
| 2026-08-30 | 初版 — クラウド／ローカル会話の長期記憶化 |
| 2026-08-31 | Power 端子・SW 配置・PD A/B・VCC_TONE/GND 方針を追記 |
| 2026-08-31 | 手持ちオペアンプ在庫 → `Audio/OPAMP_INVENTORY.md` |
