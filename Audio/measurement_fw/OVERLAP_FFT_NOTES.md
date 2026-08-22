# オーバーラップ FFT 改善メモ（他チャット共有用）

最終更新: **2026-08-22**

30 本バー維持のまま **分解能↑** と **fps↑** を両立したい、という方針の整理。  
実装は未着手。次チャットは本メモと `overlap_budget.py` から始められる。

---

## ゴール（変えない／変えたい）

| 項目 | 方針 |
|---|---|
| 表示バー数 | **30 本固定**（1/3 oct。UI の束ね方だけ） |
| 分解能 | FFT 窓を長く（N↑ → Δf = fs/N を細く） |
| fps | ホップを短く（オーバーラップ。更新周期 = hop/fs） |
| 見ない帯域 | いまどおり可聴帯〜20 kHz 想定 |

**非オーバーラップのまま N を伸ばすと fps が落ちる**ので、両立には **長い窓 + 短い hop** が必要。

ADC の fs だけ上げて N 据え置きは、fps 向きでも分解能向きではない（Δf が粗くなる）。

---

## 現状パイプライン（ボトルネックの前提）

```text
PCM1804 48 kHz ──PIO/DMA──► spectrum.frame()
                              ├ start_into(次バッファ)   # フレームごとに張り直し
                              ├ analyze(今)  FFT L+R + バンド + 低域 IIR
                              └ wait(DMA)
core1: BandWorker / core0: LCD 差分 SPI（gen 更新時のみ）
```

| 層 | いまの実効 | オーバーラップ狙いでの位置づけ |
|---|---|---|
| ADC 48 kHz | N=1024 で窓 ≈21 ms（非OL時 ≈47 fps 床） | 連続ストリームとしては足りる。**天井ではない** |
| Pico 2 解析 | C `fft_q15` ≈1.9 ms/1024/ch。前後は Python | **本命の上限**（秒間 FFT 回数 × 1回コスト） |
| LCD ST7796 @40 MHz | 差分 `fill_rect` | 解析が速くなったあとの **第二壁** |
| 低域 1/3 oct | 帯域幅の整定（~Q/f0） | hop を短くしても消えない **別制約** |

C FFT 化済みなので「FFT をもう一回速く」より、**連続 DMA + ホットパス C 化で hop を短く使えるか**が残最適化。

---

## 成り立つ条件（再掲）

\[
T_{\text{hop}} = \frac{\text{hop}}{f_s},\quad
\Delta f = \frac{f_s}{N},\quad
\text{解析は } T_{\text{hop}} \text{ 以内に L+R を終える必要あり}
\]

- 30 本は `octave_bins` 集計の話 → N/hop と独立
- 表示 fps は gen 間引き可能。**分解能用に回したい解析レート**は core1 計算で頭打ち

目安（実機 C FFT 1.9 ms/1024 をベースにした机上。正確な表はモック参照）:

| N | hop | 予算 | 感触 |
|---|---|---|---|
| 1024 | 1024 | ≈21 ms | いまに近い。余裕 |
| 1024 | 512 | ≈11 ms | 現実的な次 |
| 1024 | 256 | ≈5 ms | 2ch FFT だけで逼迫。糊の C 化必須級 |
| 2048 | 512 | ≈11 ms | 分解能↑。要実測 |

---

## 次に触る順（実装ガイド）

1. **連続リングバッファ I2S**（前提工事）  
   いまの `start_into`/`wait` スナップショットをやめ、DMA を止めずに hop だけ進める。
2. **ホストで予算・hop 論理を固める** → `python3 overlap_budget.py`
3. **ホットパス** unpack / バンド dB /（必要なら IIR）を C 寄せ
4. **実機**で `(N, hop)` を振り、core1 実時間と LCD 描画 fps を分計
5. 解析が予算内に入ったあと、棒 SPI を詰める

低域の「粘り」は 30 本 1/3 oct を維持する限り物理限界。fps と混同しない。

---

## テスト／モック

| ファイル | 役割 |
|---|---|
| `overlap_budget.py` | **CPython ホスト可**。予算表・MockRing・擬似負荷。実機不要 |
| `fft_test.py` | 既存。実機での FFT 正しさ・速度 |
| `c_fft/on_pico_check.py` | 既存。C FFT 実機タイミング |
| `c_fft/test_host.c` | 既存。ホスト C 自己検証 |

```bash
cd Audio/measurement_fw
python3 overlap_budget.py           # 予算表 + mock 自己テスト
python3 overlap_budget.py --n 2048 --hop 512 --fft-ms 4.2
```

モックが表すもの:

- `MockI2sRing` … 連続取り込み相当（hop 進めるだけ）
- `budget_ok(n, hop, fft_ms, glue_ms)` … 1 ホップ予算に 2ch 解析が収まるか
- 実 SPI/PIO は含まない（計算上限の机上切り分け用）

---

## 他チャットへの引き継ぎ文（コピペ可）

```text
MeasurementADC スペアナ: 30本固定のまま分解能↑とfps↑を両立したい。
方針はオーバーラップ FFT（N大・hop小）。ADC/LCDよりPico2の解析スループットが本命。
現状は非OLの start_into/wait。詳細とホストモックは
Audio/measurement_fw/OVERLAP_FFT_NOTES.md と overlap_budget.py。
まず予算表で (N,hop) を選び、連続DMAリング→ホットパスC化→実機計測の順。
```

---

## 関連

- ファーム概要: [README.md](README.md)
- C FFT: [c_fft/README.md](c_fft/README.md)
- 実機状態: [../MeasurementADC_STATUS.md](../MeasurementADC_STATUS.md)
