# MeasurementADC ファームウェア

計測モジュール側 Pico2（A702）の MicroPython コード。
ハードの現状は `../MeasurementADC_STATUS.md`、切り分け履歴は `../MeasurementADC_BRINGUP.md`。

## 構成

| ファイル | 役割 |
|---|---|
| `i2s_rx.py` | PIO I2S スレーブ受信（PCM1804 がマスタ）。`start_into` / `wait` で DMA 重ね取り可 |
| `fft.py` | FFT とオクターブ集計。固定小数点＋低域 IIR |
| `spectrum.py` | 受信→10 バンド。ダブルバッファで DMA と FFT を重ねる |
| `lcd.py` | ST7796S（SPI0 GP18/19、MADCTL `0xE8`、SPI 40 MHz、`fill_rect` は CS を張ったまま窓＋画素） |
| `touch.py` | FT6336U（I2C1 GP10/11） |
| `spectrum_lcd.py` | LCD 10 バンド UI＋下端タッチメニュー |
| `adc_check.py` | クロック実測と I2S ブリングアップ |
| `fft_test.py` | `fft.py` の自己検証 |
| `c_fft/` | Q15 FFT の C 移植（USER_C_MODULE `fft_q15`。実機で viper の約 5.4 倍） |
| `spectrum_monitor.py` | 10 バンドをシリアル表示 |
| `lcd_test.py` | LCD 単体確認 |
| `main.py` | 電源投入で `spectrum_lcd.main()` を起動 |
| `capture_raw.py` | **生サンプルを USB へ base64 で吐くだけ**（THD 測定用。Pico 側で解析しない） |
| `analyze_thd.py` | **PC 側 float64 解析**。基本波・H2/H3/H5 の dBc と相対位相、複数回の再現性 |

### ⚠ `mpremote` で繋ぐとスペアナが止まる

**`mpremote` は接続時に Ctrl-C を送る**ので、`main.py` から自動起動している
`spectrum_lcd` が**その時点で停止する**。`exec` で状態を見に行くだけでも止まる
（「動いているか確認」が「動作停止」になる）。

- **測定するとき**: これは好都合。スペアナが PIO/DMA を掴んだままだと
  `capture_raw.py` と衝突するので、どのみち一度止める必要がある
- **スペアナへ戻すとき**: `mpremote connect <port> reset` を送ったあと
  **`mpremote` で触らないこと**。確認は LCD の表示で行う。
  確実にしたいなら電源の入れ直し

`mpremote run` は REPL 経由なので `main.py` は起動しない。測定中はリセットしない限り
スペアナは立ち上がらないので、連続キャプチャの邪魔にはならない。

### THD 測定に `spectrum.py` を使わない理由

ブリングアップ実測で **固定小数点 FFT の演算ノイズはピークから約 65dB 下**。
`NORM_BITS = 15` で 24bit の 9bit を捨て各段で `>>1` するので、
−100dB 級の高調波は丸め誤差に埋もれる。`power()` は位相も捨てる。
→ **`capture_raw.py` で生のまま出し、PC 側 numpy(float64) で解析する。**

## 使い方

```bash
cd Audio/measurement_fw

# ハード確認
mpremote connect COMx cp i2s_rx.py : + run adc_check.py

# LCD スペアナ一式＋起動用 main.py
mpremote connect COMx fs cp lcd.py touch.py fft.py i2s_rx.py spectrum.py spectrum_lcd.py main.py :
# 以降はリセット／電源投入でスペアナが自動起動する
```

`adc_check.py` が正常ならおおよそ次のとおり。

```
SCKI  12288215 Hz   BCK  3072015 Hz   LRCK  48000.5 Hz
SCKI/LRCK = 256.002     BCK/LRCK = 64.000
```

## LCD スペアナ UI

- 既定 **30**（1/3 oct, 25…20k）＋色 **WHT**。タッチで **20** / **15**、他パレットにも切替可
- **20** は低域を 1 oct（40…500 Hz）にした応答重視。1/3 oct の 25 Hz は帯域幅 5.8 Hz ＝ 約 170 ms、1 oct の 40 Hz なら約 35 ms
- 低域（FFT ビン不足）は IIR バンドパス（バンド幅に応じた Q）
- IIR の release はバンドごと。時定数はバンドパスの整定時間（Q/f0）と 0.12 秒の遅いほう。半減期は約 0.08〜0.12 秒
- FFT バンドにも軽い下り envelope（半減期約 0.1 秒）。上りは即時
- 表示レンジ既定 −60〜−18 dBFS。タッチで切替可。L/R の dB 横目盛はガター＋右端ラベル（棒の下は横断しない）
- FFT バンドは **密度表示**（帯域内ビン平均 / フルスケール正弦波ピーク）。広いバンドほど合計表示で伸びるのを抑える。低域 IIR は帯域 RMS のまま
- 下端メニュー（左→右）: レンジ / L+R|L|R / 色 / **30|20|15** / **1k|2k** / ピーク
- FFT 点数は既定 **1024**（Δf≈47 Hz）。**2k** は低域分解能が良い（Δf≈23 Hz）が fps は落ちる
- 解析は第2コア、LCD 描画は core0。I2S DMA 待ち中は GIL を手放す
- タッチ座標（MADCTL `0xE8`）: `x = 479 - ty`, `y = tx`

## ピン割当

初号基板のネット名と**実配線**が違うものに注意。回路図 rev 0.4 以降は実配線が正規ネットになる。

| GPIO | 物理 | 初号基板のネット | 実配線 / rev 0.4 のネット |
|---|---|---|---|
| GP0 | 1 | `ADC_DATA` | そのまま |
| GP1 | 2 | `ADC_BCK` | そのまま |
| GP2 | 4 | `ADC_LRCK` | そのまま |
| GP3 | 5 | `LCD_SCK` | **未使用（入力）**。rev 0.3 以降 NC |
| GP4 | 6 | `LCD_MOSI` | **未使用（入力）**。rev 0.3 以降 NC |
| GP5 | 7 | `LCD_CS` | そのまま |
| GP6 | 9 | `LCD_DC` | そのまま |
| GP7 | 10 | `LCD_RST` | そのまま |
| GP8 | 11 | `LCD_EN` | High で LCD_VCC ON |
| GP9 | 12 | （空き） | 初号は CN3F-1 へ飛ばし → rev 0.3 以降 `MCLK_SENSE`（R720 1k）。**駆動禁止** |
| GP10 | 14 | `TP_SDA` | そのまま |
| GP11 | 15 | `TP_SCL` | そのまま |
| GP12 | 16 | `TP_INT` | そのまま |
| GP13 | 17 | `TP_RST` | そのまま |
| GP15 | 20 | （空き） | 初号は飛ばし → `ADC_nRST`。rev 0.4 は `ADC_nMR`（TPS3307 ~MR、OD。H は駆動しない） |
| GP16 | — | （空き） | SPI0 ダミー MISO |
| GP18 | 24 | （空き） | 初号は LCD SCLK 飛ばし → rev 0.3 以降 `LCD_SCK` |
| GP19 | 25 | （空き） | 初号は LCD MOSI 飛ばし → rev 0.3 以降 `LCD_MOSI` |

Pico は横向き。**南の列が西→東 1〜20、北の列が東→西 21〜40。**

## 注意

- **GP9 を出力にしない**（Y701 と衝突して SCKI が化ける）
- **`machine.I2S` は使えない**（rp2 はマスタ専用）
- DATA/BCK/LRCK は連番 GPIO（PIO の相対ピン）
- GP15（`ADC_nMR`）の H は駆動しない（~MR は OD。`ADC_nRST` は U709 のプッシュプル）
- ノイズ床の引き算はしていない。棒が短いのは表示下限（既定 −60 dBFS）による

## 応急構成（初号機）

U710 1番リフト、Y701 空中配線、LCD SPI 飛ばし。詳細は `../MeasurementADC_BRINGUP.md`。

## `capture_hold.py` — USB を抜いたまま測る（A1 の切り分け）

`capture_raw.py` は `sys.stdout`（USB シリアル）に吐くので USB が要る。
だが **A1 で確かめたいのは「USB を抜くとスプリアスが消えるか」**なので、
挿したまま採ったのでは意味が無い。`capture_hold.py` は **RAM に保持して止まる**。

```
1. USB を抜く
2. Pico 上で main.py を main_capture.py の内容に差し替えておく（LCD スペアナは起動しない）
3. 基板の電源を入れ直す
4. 1320Hz を流す            → 音が来たら自動でラッチして停止する
5. USB を挿して mpremote で繋ぐ（接続時の Ctrl-C でアイドルが割れる）
6. import capture_hold; capture_hold.status()   → 何本採れたか
   import capture_hold; capture_hold.dump()     → capture_raw.py と同じ書式で吐く
7. analyze_thd.py にそのまま渡せる
```

**なぜ成立するか:**

- **電源が USB に依存しない。** Pico の VSYS は `D701`（ショットキ）経由で基板の
  `+5V_D` から来ている。USB を抜いても動き続ける
- **`mpremote` は Pico をリセットしない。** 接続時に Ctrl-C を送るだけなので、
  モジュールのグローバル（`capture_hold.HOLD`）は生き残る
- **採ったら止まる。** 連続で採り続けると **USB を挿した瞬間の汚れたデータで
  上書きしてしまい、切り分けにならない**

**副次的な利点:** LCD スペアナを起動しないので **SPI 40MHz が止まった状態**で測れる。
前回の測定も `mpremote` 接続でスペアナが止まっていたので、**条件が揃って直接比較できる**。

RAM は1本 128KB（16384 frames × 2ch × 4B）。`N_HOLD` は既定 2 で、
`MemoryError` になったら 1 に落ちる。`status()` が `mem_free` を出す。
