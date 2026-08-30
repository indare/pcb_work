# AudioV2 シンボル／回路図レビュー要約（2026-08-30）

4エージェント（実装者・確認者・レビュー者・否定レビュー）の統合。修正の根拠ドキュメント。  
詳細な修正チケットは [SYMBOL_FIX_TODO.md](SYMBOL_FIX_TODO.md)。

---

## 総合判定

**Request changes / 製造不可。**  
PT2314 のピン名は DS と一致するが、シンボル lib の load 失敗・extends 埋め込みピン欠落・OLED 誤埋め込み・PowerModule 一次短絡があり、素案を信用できない。

| 視点 | 判定 |
|---|---|
| 実装者 | lib_id 欠落はなし。sym load 失敗・extends ピン 0・OLED 0.91 が本丸 |
| 確認者 | **条件付き** — PT2314 28/28 OK。OLED・実ネット未接続で無条件合格不可 |
| レビュー者 | **Request changes** — 手回し骨格は反映。Relay 未配線・親 hier・型番未記載 |
| 否定レビュー | **マージ拒否** — 電源短絡、検証の化石 ERC、実物と図の不一致 |

---

## ブロッカー（合意）

1. **`AudioV2.kicad_sym` が `kicad-cli` で読めない**  
   - 末尾の二重 `(embedded_fonts no)`  
   - 実測: `kicad-cli sym export svg …` → `Unable to load library`

2. **`embed_lib_symbols` が `extends` を flatten しない**  
   - `LM7809_TO220` → LM7805、`MCP23017-E/SP` → MCP23017x-x-SO  
   - ネットリスト／BOM でピン空

3. **OLED 誤埋め込み**  
   - lib_id `SSD1306-128x64` だが中身は `ER_OLEDM0.91`（128×32）  
   - PARTS/v1 ファームは **2.42″ / 128×64**（`Control/ssd1306.py`）

4. **PowerModule 一次短絡（否定レビュー・座標再確認）**  
   - ジャンクション `(83.82, 45.72)` に PD_GND・F1 系・DKMW ±Vin・R.C.・7809 GND が合流  
   - `sch_helpers.pin_connect` の座標取り違えが疑義  
   - 7809 が一次 GND と二次 +12 を跨ぐリスクも指摘

---

## DS／シンボル照合（確認者）

| 部品 | 結果 |
|---|---|
| PT2314 28pin | **全一致** |
| DKMW20F-12 / BP5293 / LM7809 / ULN2803 | OK |
| SW_DP3T / Dual pot **論理ピン** | 意図どおり（実ネットは未接続多数） |
| MCP23017 pin12 | 番号 OK、名称 `SCK`（正: SCL） |
| AZ850 | 番号 OK、ピン名空 |
| CH224_50224 | 4 ピン draft（3.3V 未モデル） |

---

## 設計整合（レビュー者）

- **OK:** PGA 削除、ENC×3、DEST トグル+ラダー、A50k Dual、計測 LCD を Control に載せない、Power 経路の意図  
- **NG:** RelayBoard wire 0、親 hier ピン不一致（`+3V3` vs `3V3`、±12V_IN 幽霊ピン等）、ENC/DEST→Pico 未結線、PARTS MPN 未記載、OLED FP

---

## 「合格に見せかける」落とし穴

- `check_sexpr.py` ✅ = 括弧のみ  
- `*-erc.rpt` = PGA/ENC×6 時代 or 子単体 ERC（gitignore）  
- netlist export 成功 ≠ 未接続ゼロ  
- WIRING は手回し化済みでも `generate_kicad_scaffold.py` は PGA に巻き戻せる  
- `PowerModule-bom.xml` 未追跡（コミットしない）

---

## 実物との差

| 図 | 実物（PARTS / v1） |
|---|---|
| `SW_DP3T` + `SW_SP3T`（2 シンボル） | C&K **7303SYZQE** 1 個（3PDT、端子番号が違う） |
| OLED 0.91″ 128×32 埋め込み | **2.42″** 128×64 SSD1309（AliExpress） |
| （Control に LCD なし） | スペアナ = Waveshare **29318**（MeasurementADC） |

---

## 修正後に否定レビューが再確認すべきコマンド

```bash
python3 Audio/scripts/check_sexpr.py -q AudioV2
kicad-cli sym export svg -o /tmp/audiov2-sym AudioV2/AudioV2.kicad_sym
cd AudioV2 && kicad-cli sch export netlist -o /tmp/audiov2.net AudioV2Case.kicad_sch
# PowerModule: 座標 83.82,45.72 付近の wire/junction 多重合流が消えているか
# 埋め込み: LM7809 / MCP23017 に (pin があるか、OLED に 0.91 / 128x32 が無いか
```

---

## 変更履歴

| 日付 | 内容 |
|---|---|
| 2026-08-30 | 初版 — 4視点レビュー統合 |
