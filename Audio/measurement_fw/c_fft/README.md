# c_fft — Q15 FFT の C 移植

`fft.py` の `FFTFixed` ホットパスを C に移植し、MicroPython の
**USER_C_MODULE** (`fft_q15`) として Pico 2 のファームに組み込みます。

## 実機の測定結果（n=1024, RP2350）

| 項目 | C `fft_q15` | Python viper |
|------|-------------|--------------|
| ピーク bin | 21 | 21 |
| ピーク dBFS | −6.02 | −6.02 |
| 全ビン一致 | **True** | — |
| 1 回あたり | **1.91 ms** | 10.23 ms |

−6 dBFS・bin 21。速度は約 **5.4 倍**（最適化前の C は 13.2 ms）。

## ホスト自己検証

```bash
cd Audio/measurement_fw/c_fft
make test       # ゴールデンハッシュ・レベル・値域ストレス
make sanitize   # UBSan（負シフトなどの未定義動作を止める）
```

ゴールデンは最適化前の全ビンスペクトルを固定しています。レベル読み
（0〜−80 dBFS）が誤差 0.01 dB 級、全ビンハッシュが一致することを確認します。
ホスト時間は参考値で、Pico 上とは別物です。

## ファーム再ビルド

依存はリポジトリ外の `.deps/`（MicroPython v1.28.0 と Arm GNU Toolchain）。

```bash
export PATH="$PWD/.deps/arm-gnu-toolchain-*/bin:$PATH"
make -C .deps/micropython/ports/rp2 BOARD=RPI_PICO2 \
  USER_C_MODULES="$PWD/Audio/measurement_fw/c_fft/micropython.cmake" -j8
```

BOOTSEL を押しながら挿すと `/Volumes/RP2350` が出るので、
`build-RPI_PICO2/firmware.uf2` をコピーします。書き込み後は一度 USB を
抜き差ししないと再列挙しないことがあります。

## 実機での確認

```bash
perl pico_exec.pl < on_pico_check.py
```

`pico_exec.pl` は CDC を 1 回だけ開き、文を 1 行ずつ REPL に流し、最後に
必ずソフトリセットして `main.py` を戻します。この Mac では次の制約があり、
それに合わせた作りになっています。

- 抜き差し 1 回につき `open()` が成功するのは 1 回だけ。2 回目はカーネル内で
  固まり、`SIGALRM` も届かない
- tty が canonical + echo で上がるため、raw モードにしないと自分が送った行が
  返ってくる
- paste モードは実行前に全文をエコーし返すため、待ち時間が読めない

`mpremote` はこの環境では CDC を固めるので使いません。

## メモリ

テーブルは MicroPython のヒープ（`m_new`）から取ります。rp2 ポートでは GC
ヒープがほぼ全 RAM を占有するため、libc の `calloc` はそこと重なる領域を返し、
初期化でテーブルを書いた瞬間に MCU ごとロックします。ホストでは通常の malloc
なので、この不具合はホストテストでは出ません。

C コアは埋め込み側がバッファを渡せます。

```c
size_t words = fft_q15_store_words(n);
int32_t *store = /* 呼び出し側で確保 */;
fft_q15_init_with(&f, n, store);
```

`fft_q15_init()` は `calloc` で確保するホスト向けの入口です。

## 契約（Python と揃える）

| 項目 | 内容 |
|------|------|
| 入力 | `int32` 時系列 n 点（2 の冪、`array('i')`） |
| 窓 | Hann、Q15 |
| 正規化 | ピークを ~14 bit に合わせて `shift` |
| バタフライ | 半 LSB 丸め、段ごと `>>1` |
| 出力 | 片側パワー `n/2+1`、dBFS 分母は `full_scale_power(ref)` |

## 次のステップ

`spectrum.py` から C を呼ぶ。表示・IIR・バンド集計は Python のまま。

```text
spectrum.py
  └─ fft_q15.FFT(n).power_into(samples, out)   # いまの FFTFixed.power と同じ契約
```

FFT は 1 フレームあたり約 10 ms → 2 ms になります。2ch なら約 16 ms 浮くので、
描画以外の計算余裕は大きくなります。体感 fps は描画側次第です。
