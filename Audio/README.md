# Audio（AudioCase）

KiCad プロジェクトと関連ドキュメント。

## ドキュメント案内

| ファイル | 内容 |
|---|---|
| [MeasurementADC_STATUS.md](MeasurementADC_STATUS.md) | **現状・次作業・箱内配線方針**（まずここ） |
| [MeasurementADC_BRINGUP.md](MeasurementADC_BRINGUP.md) | 初号機の切り分けログ（履歴） |
| [MeasurementADC_ORDER.md](MeasurementADC_ORDER.md) | 発注・在庫 |
| [measurement_fw/README.md](measurement_fw/README.md) | 計測 Pico2 ファーム |
| [../Control/README.md](../Control/README.md) | Controll 親／子ファーム |
| [../README.md](../README.md) | リポジトリ全体・KiCad MCP |

## 階層シート

| シート | 役割 | いまの扱い |
|---|---|---|
| PowerModule | **DKMW20F-15** ±15 / ±660mA（1″×1″。TMR 6 は電流不足の次点）。計算メモ: [PowerModule_TEC3_REDESIGN.md](PowerModule_TEC3_REDESIGN.md) | 箱に入れる |
| AmpModule | NE5532 Amp（×10 想定）。AMP401 は DIP-8 ソケット | ラインアウト（J11）。ADC へは AdcBuffer 経由 |
| AdcBuffer | ゲイン1バッファ。実装は **OPA1652AID-DIP**（共立 Q5M411） | Amp L/R_OUT → MeasurementADC AUDIO |
| HeadphoneBuffer | ゲイン1電流バッファ。実装は **NJM4556A**（DIP-8 ソケット） | SW101 PHONE → パッド → RV101 → バッファ → J103 |
| Controll | CH1–10 リレー（親＋子） | 実機では外している |
| MeasurementADC | 計測＋LCD | 初号応急配線で稼働 |
| EQModule | EQ | 今号では使わない |
| RVConvert | RV 変換 | 箱計画に含むかは別途 |

## 出力切り替えとヘッドホン出力

SW101（DP3T）で Amp 出力の行き先を選ぶ。中央位置はミュート。

- PHONE: `SW101` → 固定パッド `R102/R101`（L）`R104/R103`（R）→ `RV101` A50k デュアル → `HeadphoneBuffer`（`R901/R903` 10Ω → `C901/C902` 470µF）→ `J103`
- LINE: `SW101` → `RV102` A50k デュアル → `J104`
- ADC への分岐はスイッチより手前なので、切り替え位置に関係なく測定できる

固定パッドは 8.2kΩ 直列＋910Ω 並列で約 −20dB。±15V・ゲイン1では最大出力がヘッドホンに対して過大で、
ボリュームが回転下端だけで使われてしまうため入れている。不要なら直列を 0Ω、並列を未実装にすればバイパスできる。
直列と並列の位置を取り違えると分圧にならず減衰が効かないので、必ず 8.2kΩ をスイッチ側の直列、910Ω を
ポット側から GND へ落とす並列にする。

**`RV101` はバッファより前**に置く。50kΩ のポットを 32Ω のヘッドホンより後ろに置くと、
ワイパー出力インピーダンス（中点で最大約 12.5kΩ）に対して負荷が軽すぎて −50dB 級まで落ち、
回転上端の数度だけで音が出るうえヘッドホン電流が抵抗体を流れる。

`C901/C902` は 470µF の**無極性（バイポーラ）**電解。両電源で出力の直流はほぼ 0V なので極性品は使わない。
故障時にヘッドホンへ ±15V が出るのを防ぐのと、電源投入時のポップ抑制が目的。
`R902/R904` 100kΩ はヘッドホン未接続時に出力ノードを確定させるブリード。

### SW101 はパネル実装（基板側は 2x04 ヘッダ）

KiCad 標準ライブラリに 2P3T（8ピン）のフットプリントが無く、選択機はパネルから操作する部品なので、
基板側は `PinHeader_2x04_P2.54mm_Vertical` にしてパネル実装の 2P3T スイッチへリード線で引く。
`SW_DIP_SPSTx04` 系は 8 パッドあるが独立 4 回路でピン機能が違うため流用しない。

| ヘッダピン | スイッチ端子 | つながる先 |
|---|---|---|
| 3 | L 極 コモン | Amp L 出力（ADC への分岐と共通） |
| 1 | L PHONE | 固定パッド `R102` → `RV101` |
| 2 | L MUTE | 未接続 |
| 4 | L LINE | `RV102` |
| 7 | R 極 コモン | Amp R 出力 |
| 5 | R PHONE | 固定パッド `R104` → `RV101` |
| 6 | R MUTE | 未接続 |
| 8 | R LINE | `RV102` |

## AdcBuffer の入力極性

`AMP801` は**上下反転で描いてある**（− 入力が上、+ 入力が下）。信号は `R804/R809` 0Ω で **+ 入力**へ入り、
`R805/R810` 100kΩ が + 入力のバイアスプルダウン、帰還は `R801/R806` 0Ω で **− 入力**へ戻り、
`R803/R808` 10kΩ が − 入力の Rg。Rf=0Ω なのでゲインは 1。

反転を戻して + と − を入れ替えると帰還が + 入力に回って正帰還になり、出力が電源レールに張り付く。
シンボルの向きだけで極性が決まるので、このシートを編集したら `Net-(AMP801A-+)` に `R804`/`R805` が、
`Net-(AMP801A--)` に `R801`/`R803` が入っていることをネットリストで確認する。

## オペアンプソケットの差し替え

3 か所すべて DIP-8 ソケットだが、役割が違うので入れられる品種が違う。**取り違えると壊す。**  
手持ち在庫の一覧は **[OPAMP_INVENTORY.md](OPAMP_INVENTORY.md)**。

| ソケット | 役割 | 標準 | 差し替え | 制約 |
|---|---|---|---|---|
| `AMP401`（AmpModule） | 電圧増幅 ×10（プリアンプ） | NE5532 | 手持ち DIP／DIP 化モジュール（在庫表） | 高速石は安定性注意。SOIC 単体は不可 |
| `AMP801`（AdcBuffer） | 測定系ゲイン1バッファ | OPA1652AID-DIP | 原則固定 | 測定の基準。ここを動かすと比較の土台が動く |
| `AMP901`（HeadphoneBuffer） | ヘッドホン電流ドライバ | NJM4556A | **不可** | 32Ω 直接駆動が必要。電圧アンプ系は電流不足 |

`AMP401` の出力は AdcBuffer 経由で測定 ADC にも、SW101 経由でヘッドホン／ラインにも行く。
つまりここを差し替えると、聴いている音と測っている波形が同じ変化を受ける。比較実験はこのソケットで行う。

## 分割 Gerber

`split/Gerber/` — `01_main` … `06_measurement_adc`。再生成は `scripts/regenerate_split_gerbers.py`。

## S式の健全性チェック

回路図・基板ファイルをテキスト編集したら `python3 scripts/check_sexpr.py -q .` で括弧の対応を確認する。
既知の壊れ方（`property` の閉じ括弧が早い）は `--fix` で直せる。手順は [`.cursor/rules/kicad-sexpr-integrity.mdc`](../.cursor/rules/kicad-sexpr-integrity.mdc)。

コミット時にも同じ検査が走る。クローン直後は一度だけ有効化が必要。

```bash
git config core.hooksPath .githooks
```
