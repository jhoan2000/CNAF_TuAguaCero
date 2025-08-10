# Escribe tu código aquí :-)
from machine import Pin, time_pulse_us
import time



print("start")
trig = Pin(5, Pin.OUT)   # D2
echo = Pin(23, Pin.IN)    # D1

bomba_pin = Pin(4, Pin.OUT)
def medir_distancia():
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)

    duracion = time_pulse_us(echo, 1, 20000)  # Máx. 30 ms espera
    print("duracion", duracion)
    if duracion < 0:
        print("Error de medición")
        return 0

    distancia = round((duracion / 2) * 0.0343, 2)  # cm
    print("Distancia :", distancia)
    return str(distancia)


