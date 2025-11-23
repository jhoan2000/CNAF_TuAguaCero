import time
import network
from machine import Pin

# --- Conexión WiFi () ---
ssid , password = "ZTE_E2FF51", "35600911"

sta = network.WLAN(network.STA_IF)
sta.active(True)
# Conéctate
led = Pin(35, Pin.OUT)
if not sta.isconnected():
    print('Conectando a la red...')
    sta.connect(ssid, password)
    for _ in range(20): # Espera hasta 10 segundos
        if sta.isconnected():
            break
        led.on()
        time.sleep(0.5) # Resultado
        led.off()
        time.sleep(0.5) # Resultado

        if sta.isconnected():
            print('Conectado. Dirección IP:', sta.ifconfig()[0])
            led.on()
            time.sleep(3)
            led.off()
        else: print('❌ No se pudo conectar al WiFi.')
