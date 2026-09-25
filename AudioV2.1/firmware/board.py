"""AudioV2 Pico ピン／I²C（MeasureControl・FrontPanel のネットに合わせる）。

数値の正は回路図。ここはファームが読むためのコピー。
"""

# I²C0 — PT2314E 同居。OLED が無いので 100 kHz でよい。
I2C_ID = 0
I2C_SDA = 20
I2C_SCL = 21
I2C_FREQ_HZ = 100_000

# FrontPanel MCP23017（UI）。ストラップ固定 **0x22**（娘ジャンパから除外）。
MCP_UI_ADDR = 0x22

# 娘 AmpBank MCP — 基板ジャンパ A2/A1/A0（6 段）。UI 0x22 を飛ばす。
# Bridged12=GND=0 / 2-3 bridge=3V3=1。出荷時オール GND → 0x20。
AMP_ADDR_TIERS = (
    0x20,  # 000 tier1
    0x21,  # 001 tier2
    0x23,  # 011 tier3
    0x24,  # 100 tier4
    0x25,  # 101 tier5
    0x26,  # 110 tier6
)

# ENC INT（MCP OD → Pico）
ENC_INTA = 16
ENC_INTB = 17

# Waveshare LCD SPI0
LCD_CS = 5
LCD_DC = 6
LCD_RST = 7
LCD_EN = 8
LCD_SCK = 18
LCD_MOSI = 19

# タッチ（当面未使用でもピンは確保）
TP_SDA = 10
TP_SCL = 11
TP_INT = 12
TP_RST = 13

# DEST_ADC はラダー廃止済み。読む必要なし（図では D_GND プル）。
DEST_ADC = 26

# Amp バックエンド: "switch" | "relay"（起動時に決める／設定定数）
AMP_BACKEND = "switch"
