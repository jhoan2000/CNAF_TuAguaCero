from machine import Pin, time_pulse_us
import ujson
from umqtt.simple import MQTTClient
import time

# --- Conexión MQTT ---
class  star_conect_mqtt():
    def __ init__(self, name, broker):
        self.name = name
        self.broker = broker
        
def star_conect_mqtt():
    mqtt = MQTTClient("weather_monitor", "broker.hivemq.com")
    mqtt.connect()

    mqtt.set_callback(control_callback)
    mqtt.subscribe("tuaguacero/control_filtros")
