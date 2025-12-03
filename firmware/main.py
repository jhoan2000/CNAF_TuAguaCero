# Escribe tu código aquí :-)
from machine import Pin, time_pulse_us
import ujson
from umqtt.simple import MQTTClient
import time
from uts_water import medir_distancia
from cifrar_aes import *
from control_filtrado import sistema_filtrado
#import connect_wifi

# --- Configuración del sistema ---
UMBRAL_DISTANCIA = 25 # 
UMBBRAL_AGUA_CRUDA = (120, 20)  # cm (max, min)
UMBRAL_AGUA_FILTRADA = (100, 20)  # cm (max, min)
sistema_purgado = False
control_manual = 0  # 0: automático, 1: detener, 2: purgar
# --- Variables protegidas ---

led = Pin(35, Pin.OUT)
control_manual_pin = Pin(4, Pin.IN, Pin.PULL_UP)

# --- Conexión MQTT ---
mqtt = MQTTClient("weather_monitor", "broker.hivemq.com")
mqtt.connect()


def control_callback(topic, msg):
    try:
        data = ujson.loads(msg)
        if "control_manual" in data:
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
    distancia_ac, distancia_af  = medir_distancia()
    bomba_estado, valvula_estado =sistema_filtrado(UMBRAL_AGUA_FILTRADA, UMBBRAL_AGUA_CRUDA, distancia_ac, distancia_af ) # No medido en este ejemplo)

    payload = {
        "dist_ac": cifrar_valor(distancia_ac),
        "dist_af": cifrar_valor(distancia_af),
        "bomba_filtro": cifrar_valor(bomba_estado),
        "valvula_purga": cifrar_valor(valvula_estado),
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
