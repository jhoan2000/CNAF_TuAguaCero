# Escribe tu código aquí :-)
from machine import Pin, time_pulse_us
import time



print("start")
trig_ac = Pin(35, Pin.OUT)   # D2
echo_ac = Pin(36, Pin.IN)    # D1

trig_af = Pin(33, Pin.OUT)   # D3
echo_af = Pin(34, Pin.IN)    # D4

def medir_distancia():
    trig_ac.value(0)
    time.sleep_us(2)
    trig_ac.value(1)
    time.sleep_us(10)
    trig_ac.value(0)

    duracion_ac = time_pulse_us(echo_ac, 1, 20000)  # Máx. 30 ms espera
    print("duracion agua cruda", duracion_ac)
    if duracion_ac < 0:
        print("Error de medición agua cruda")
        return 0

    distancia_ac = round((duracion_ac / 2) * 0.0343, 2)  # cm
    print("Distancia agua cruda :", distancia_ac)
    return str(distancia_ac)

    trig_af.value(0)
    time.sleep_us(2)
    trig_af.value(1)
    time.sleep_us(10)
    trig_af.value(0)

    duracion_af = time_pulse_us(echo_af, 1, 20000)  # Máx. 30 ms espera
    print("duracion agua filtrada", duracion_af)
    if duracion_af < 0:
        print("Error de medición agua filtrada")
        return 0

    distancia_af = round((duracion_af / 2) * 0.0343, 2)  # cm
    print("Distancia agua cruda :", distancia_af)
    return str(distancia_ac, distancia_af)

while  True :
    medir_distancia()
    time.sleep(3)
