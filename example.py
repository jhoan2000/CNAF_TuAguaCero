from machine import Pin, SPI
import time
from sh1107_heltec import SH1107   # te lo paso abajo

# Pines Heltec LoRa 32 V3
DC  = Pin(17, Pin.OUT)
RST = Pin(21, Pin.OUT)
CS  = Pin(16, Pin.OUT)

# SPI del OLED
spi = SPI(2, baudrate=8000000, polarity=0, phase=0,
          sck=Pin(18), mosi=Pin(23))

# Reset hardware
RST.value(0)
time.sleep_ms(50)
RST.value(1)

# Crear display
oled = SH1107(spi, DC, RST, CS, 128, 64)

oled.fill(0)
oled.text("Hola Heltec!", 0, 0)
oled.text("SPI OK", 0, 12)
oled.show()
