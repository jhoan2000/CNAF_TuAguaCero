# Escribe tu código aquí :-)
from machine import Pin, time_pulse_us
import ujson
from umqtt.simple import MQTTClient
import time
from uts_water import medir_distancia
from cifrar_aes import *

#import connect_wifi

UMBRAL_DISTANCIA = 25 # 
# --- Variables protegidas ---
bomba_pin = Pin(7, Pin.OUT)
val_purga = Pin(6, Pin.OUT)
led = Pin(35, Pin.OUT)

# --- Conexión MQTT ---
mqtt = MQTTClient("weather_monitor", "broker.hivemq.com")
mqtt.connect()


def control_callback(topic, msg):
    try:
        data = ujson.loads(msg)
        if "bomba_filtro" in data:
            estado = bool(data["bomba_filtro"])
            bomba_pin.value(1 if estado else 0)
            print("Bomba cambiada manualmente:", estado)
    except Exception as e:
        print("Error procesando comando:", e)

mqtt.set_callback(control_callback)
mqtt.subscribe("tuaguacero/control_filtros")


# --- Bucle principal ---
while True:
    mqtt.check_msg()  # revisa si hay comandos entrantes
    print(f"MENSAJE {mqtt.check_msg()}")
    distancia = medir_distancia()
    bomba_estado = float(distancia) <= UMBRAL_DISTANCIA  # Si la distancia es mayor al umbral, la bomba se enciende
    bomba_pin.value(1 if bomba_estado else 0)

    payload = {
        "dist": cifrar_valor(distancia),
        "bomba_filtro": cifrar_valor(bomba_estado),
        "pin": cifrar_valor(PIN_AUTENTICACION),
    }
    json_data = ujson.dumps(payload)
    firma = firmar_datos(json_data.encode())
    mensaje_final = ujson.dumps({"data": payload, "firma": firma})
    try:
        mqtt.publish("tuaguacero/LWF", mensaje_final)
        led.on()
        time.sleep(0.1) # Resultado
        led.off()
        time.sleep(0.1) # Resultado
        led.on()
        time.sleep(0.2) # Resultado
        led.off()
        time.sleep(0.2) # Resultado
        led.on()
        time.sleep(0.7) # Resultado
        led.off()
        time.sleep(0.2) # Resultado
    except Exception as e:
        print("Error publicando MQTT:", e)
        try:
            mqtt.connect()
        except:
            print("Error al reconectar al broker.")
        led.on()
        time.sleep(1) # Resultado
        led.off()
        time.sleep(1) # Resultado
    print("Publicado:", mensaje_final)
    time.sleep(2)
