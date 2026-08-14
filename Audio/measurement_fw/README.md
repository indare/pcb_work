# MeasurementADC ファームウェア

計測モジュール側 Pico2（A702）の MicroPython コード。
ハードの立ち上げ経緯は `../MeasurementADC_BRINGUP.md`、進捗は `../MeasurementADC_STATUS.md`。

## 構成

| ファイル | 役割 |
|---|---|
| `i2s_rx.py` | PIO による I2S スレーブ受信（PCM1804 がマスタ） |
| `fft.py` | FFT とオクターブバンド集計。浮動小数点版と固定小数点版 |
| `spectrum.py` | 受信から 10 バンドまでの実時間経路 |
| `adc_check.py` | クロック実測と I2S 受信のブリングアップ確認 |
| `fft_test.py` | `fft.py` の自己検証と速度計測 |
| `spectrum_monitor.py` | 10 バンドをシリアルに出す簡易表示器 |

## 使い方

```bash
cd Audio/measurement_fw

# ハードの確認
mpremote connect <port> cp i2s_rx.py :i2s_rx.py + run adc_check.py

# FFT の検証
mpremote connect <port> cp fft.py :fft.py + run fft_test.py

# スペクトル表示
mpremote connect <port> cp fft.py i2s_rx.py spectrum.py : + run spectrum_monitor.py
```

`adc_check.py` が正常なら次のようになる。

```
SCKI  12288215 Hz   BCK  3072015 Hz   LRCK  48000.5 Hz
SCKI/LRCK = 256.002     BCK/LRCK = 64.000
```

## FFT の実装方針

`FFT`（浮動小数点）と `FFTFixed`（Q15 固定小数点）の 2 つがある。
実時間経路で使うのは後者で、前者は正しさの基準。

MicroPython の float は boxed で、`@micropython.native` にしても演算が
ランタイム呼び出しのまま残るため 1 割しか速くならない。viper なら整数演算が
素のマシン命令になり、実測で 50 倍以上違った。

| n | 分解能 | 浮動 | 固定 |
|---|---|---|---|
| 512 | 93.8 Hz | 203 ms | 5.2 ms |
| 1024 | 46.9 Hz | 435 ms | 11.0 ms |
| 2048 | 23.4 Hz | 951 ms | 22.2 ms |

n=4096 は両者ともメモリ不足。

固定小数点版の精度は、レベル読みが 0 〜 −80dBFS で誤差 0.01dB、
浮動小数点版とのビンごとの差は 0.017dB。実効ノイズフロアは約 −65dBFS で、
24bit ADC の実力には届かないが 10 バンド表示には十分。

桁あふれ対策で段ごとに 1/2 しており、そのままだと切り捨て誤差が
毎段 −0.5LSB に偏ってスパーになる。半 LSB 足して丸めるとノイズフロアが
−49dBFS から −59dBFS に改善し、入力正規化の切り捨ても丸めると −65dBFS になった。

## ピン割当

A702（Pico2）の実配線。GP9 と GP15 は基板上では未接続で、飛ばし配線で使っている。

| GPIO | 物理ピン | ネット |
|---|---|---|
| GP0 | 1 | `ADC_DATA` |
| GP1 | 2 | `ADC_BCK` |
| GP2 | 4 | `ADC_LRCK` |
| GP3 | 5 | `LCD_SCK` |
| GP4 | 6 | `LCD_MOSI` |
| GP5 | 7 | `LCD_CS` |
| GP6 | 9 | `LCD_DC` |
| GP7 | 10 | `LCD_RST` |
| GP8 | 11 | `LCD_EN` |
| GP9 | 12 | **飛ばし配線** CN3F-1（SCKI）。測定プローブ専用 |
| GP10 | 14 | `TP_SDA` |
| GP11 | 15 | `TP_SCL` |
| GP12 | 16 | `TP_INT` |
| GP13 | 17 | `TP_RST` |
| GP15 | 20 | **飛ばし配線** `ADC_nRST` |

Pico は基板上で横向きに寝ている。**南の列が西から東へ 1〜20、
北の列が東から西へ 21〜40。** 物理12番(GP9) は「南の列を USB 側から 12 個目」。

## 注意

- **GP9 を出力にしないこと。** Y701 と R718(33Ω) を挟んで衝突し SCKI が化ける。
  衝突させると SCKI/LRCK が 256 ではない中途半端な値（実測で 149.2）になる。
  標準にない分周比が出たら、まずドライバの衝突を疑う
- **`machine.I2S` は使えない。** rp2 の実装はクロックを自分で生成するマスタ専用で、
  マスタである PCM1804 と衝突する
- DATA / BCK / LRCK は**連番の GPIO** である必要がある。
  PIO の `wait` が in_base からの相対インデックスでピンを見るため
- RST の H は駆動しない。R719 のプルアップに任せて監視 IC とワイヤ AND にする

## 入力が浮いているときの見え方

アナログ側が未通電だと、両チャンネルとも **約 1196Hz の倍音列**が −15dBFS 前後で出る。
時間波形は 0 / −2.0M / +2.3M の 3 値をカクカク行き来する非正弦波で、
16 倍音まで揃う。入力が開放でデルタシグマ変調器がまともに動いていないため。

デジタル側の不具合ではないので、アナログ front-end を立ち上げるまでは
この見え方を基準にしてよい。逆に、通電後もこれが残るなら別の原因がある。

## 応急構成（初号機）

`ADC_nRST` は U710 の RESET 出力が L 固定だったため **U710 の 1番をリフト**している。
Y701 は初号 FP の GND/VDD 入れ替えのため空中配線。詳細は `../MeasurementADC_BRINGUP.md`。
