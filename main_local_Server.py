# main_local_server.py
# Servidor local + MQTT (funciona en LAN, puerto 80)
# Requisitos: tu archivos existentes: connect_wifi.py, uts_water.py, cifrar_aes.py, (y opcionalmente main_esp32.py)
# Diseñado para MicroPython (ESP32)

import network
import socket
import ujson
import time
import machine
from machine import Pin
from uts_water import medir_distancia
from cifrar_aes import cifrar_valor, descifrar_valor, firmar_datos, verificar_firma  # ajusta según tus funciones
try:
    from umqtt.simple import MQTTClient
except:
    MQTTClient = None

# ------------------------
# Configuración hardware
# ------------------------
UMBRAL_DISTANCIA = 25  # cm
BOMBA_PIN = Pin(4, Pin.OUT)
LED_PIN = Pin(35, Pin.OUT)

# Estado interno (para la UI local)
estado = {
    "distancia": None,
    "bomba": 0,
    "ultimo_ts": None,
    "last_publish_ok": False
}

# ------------------------
# Conexión WiFi (LAN)
# ------------------------
# Usamos tu módulo connect_wifi (debe exponer connect() que devuelve la interfaz)
import connect_wifi
wlan = connect_wifi.connect()  # se espera que conect_wifi haga SSID/PSK y devuelva wlan object
# Si tu connect_wifi no devuelve wlan, ignora la asignación; el código asume que WLAN está conectado después de la llamada.

def ip_info():
    try:
        ip = wlan.ifconfig()[0]
    except:
        ip = "0.0.0.0"
    return ip

# ------------------------
# MQTT (opcional)
# ------------------------
MQTT_BROKER = "broker.hivemq.com"
MQTT_TOPIC_PUB = "tuaguacero/LWF"
MQTT_TOPIC_SUB = "tuaguacero/control_filtros"
mqtt = None

def mqtt_setup():
    global mqtt
    if MQTTClient is None:
        print("umqtt no disponible")
        return
    try:
        mqtt = MQTTClient("tuaguacero_local", MQTT_BROKER)
        mqtt.set_callback(mqtt_callback)
        mqtt.connect()
        mqtt.subscribe(MQTT_TOPIC_SUB)
        print("MQTT conectado y suscrito")
    except Exception as e:
        mqtt = None
        print("No se pudo conectar a MQTT:", e)

def mqtt_callback(topic, msg):
    # Mensajes de control desde la nube pueden alterar la bomba localmente
    try:
        data = ujson.loads(msg)
        if "bomba_filtro" in data:
            val = bool(data["bomba_filtro"])
            BOMBA_PIN.value(1 if val else 0)
            estado["bomba"] = 1 if val else 0
            print("Control remoto MQTT aplicado:", estado["bomba"])
    except Exception as e:
        print("Error en callback MQTT:", e)

def mqtt_publish(payload):
    global mqtt
    if mqtt is None:
        mqtt_setup()
    if mqtt is None:
        return False
    try:
        mqtt.publish(MQTT_TOPIC_PUB, ujson.dumps(payload))
        return True
    except Exception as e:
        print("Error publicando MQTT:", e)
        try:
            mqtt.connect()
        except Exception as e2:
            print("Reconexión MQTT fallida:", e2)
            mqtt = None
        return False

# Intentar inicializar MQTT (no fatal si falla)
mqtt_setup()

# ------------------------
# Funciones de negocio
# ------------------------
def medir_y_actualizar():
    try:
        dist = medir_distancia()
    except Exception as e:
        print("Error midiendo distancia:", e)
        dist = None
    if dist is not None:
        estado["distancia"] = float(dist)
        estado["ultimo_ts"] = time.time()
        # Determinar estado de bomba por umbral
        bomba_encender = 1 if float(dist) <= UMBRAL_DISTANCIA else 0
        estado["bomba"] = bomba_encender
        BOMBA_PIN.value(bomba_encender)
    else:
        # mantener estado previo si no se puede medir
        pass
    # Preparar payload cifrado similar a tu main
    try:
        payload = {
            "dist": cifrar_valor(estado["distancia"]) if estado["distancia"] is not None else None,
            "bomba_filtro": cifrar_valor(bool(estado["bomba"])),
            # "pin": cifrar_valor(PIN_AUTENTICACION),  # si existe en tu cifrado
        }
        json_data = ujson.dumps(payload)
        firma = firmar_datos(json_data.encode())
        mensaje_final = {"data": payload, "firma": firma}
        ok = mqtt_publish(mensaje_final)
        estado["last_publish_ok"] = bool(ok)
    except Exception as e:
        print("Error armando/enviando payload:", e)
        estado["last_publish_ok"] = False

# ------------------------
# Servidor HTTP
# ------------------------
HTML_DASH = """\
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Tu Agua Cero - Local</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{font-family:Arial,Helvetica;color:#222;background:#f6f9fc;padding:12px}
.card{background:#fff;padding:12px;margin:8px;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.1)}
h1{font-size:18px;margin:0 0 8px}
button{padding:10px 14px;border-radius:6px;border:0;cursor:pointer}
.on{background:#2d9a4a;color:white}
.off{background:#d9534f;color:white}
.small{font-size:13px;color:#666}
</style>
</head>
<body>
<div class="card">
<h1>Tu Agua Cero — Panel Local</h1>
<p class="small">IP: {ip}</p>
<p>Distancia (cm): <strong id="dist">{dist}</strong></p>
<p>Bomba estado: <strong id="bomba">{bomba}</strong></p>
<button onclick="fetch('/api/bomba', {method:'POST', body: JSON.stringify({estado:1})}).then(()=>load())" class="on">Encender Bomba</button>
<button onclick="fetch('/api/bomba', {method:'POST', body: JSON.stringify({estado:0})}).then(()=>load())" class="off">Apagar Bomba</button>
<p class="small">Última publicación cloud: {pub}</p>
</div>
<script>
function load(){
  fetch('/api/status').then(r=>r.json()).then(j=>{
    document.getElementById('dist').innerText = j.distancia === null ? 'n/a' : j.distancia;
    document.getElementById('bomba').innerText = j.bomba;
  }).catch(e=>console.log(e));
}
setInterval(load, 3000);
load();
</script>
</body>
</html>
"""

def start_server(port=80):
    addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    print('Servidor HTTP escuchando en', addr)
    return s

def handle_client(cl):
    try:
        cl_file = cl.makefile('rwb', 0)
    except:
        try:
            cl_file = cl.makefile('rwb')
        except:
            cl_file = None
    if cl_file is None:
        cl.close()
        return

    try:
        request_line = cl_file.readline()
        if not request_line:
            cl.close()
            return
        request_line = request_line.decode('utf-8')
        method, path, _ = request_line.split()
        # leer headers (y descartarlos)
        while True:
            h = cl_file.readline()
            if not h or h == b'\r\n':
                break
        body = b''
        if method == 'POST':
            # Intentamos leer todo lo que quede en el socket (no perfecto, pero suficiente para payloads pequeños)
            try:
                # socket recv non-blocking small wait
                cl.settimeout(0.1)
                while True:
                    part = cl.recv(1024)
                    if not part:
                        break
                    body += part
            except:
                pass
            # Si body está vacío, puede ser que el client ya cerró la conexión; ignoramos en ese caso
        # Rutas
        if path == '/' or path.startswith('/index'):
            html = HTML_DASH.format(ip=ip_info(), dist=str(estado["distancia"]), bomba=str(estado["bomba"]),
                                   pub=str(estado["last_publish_ok"]))
            response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: {}\r\n\r\n{}'.format(len(html), html)
            cl.send(response.encode('utf-8'))
        elif path.startswith('/api/status'):
            resp = {
                "ip": ip_info(),
                "distancia": estado["distancia"],
                "bomba": estado["bomba"],
                "ultimo_ts": estado["ultimo_ts"],
                "last_publish_ok": estado["last_publish_ok"]
            }
            data = ujson.dumps(resp)
            response = 'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\n\r\n{}'.format(len(data), data)
            cl.send(response.encode('utf-8'))
        elif path.startswith('/api/bomba'):
            # manejar POST con JSON {"estado": 1} o 0
            if method == 'POST':
                try:
                    # si body viene con cabeceras leídas, intentar extraer JSON
                    raw = body.decode('utf-8')
                    # A veces el navegador envía 'Content-Length' y body viene limpio; si no, intentar leer de cl_file
                    if not raw:
                        raw = cl_file.read().decode('utf-8')
                    j = ujson.loads(raw)
                    nuevo = int(j.get("estado", 0))
                    BOMBA_PIN.value(1 if nuevo else 0)
                    estado["bomba"] = 1 if nuevo else 0
                    # enviar confirmación
                    resp = ujson.dumps({"ok": True, "bomba": estado["bomba"]})
                    response = 'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\n\r\n{}'.format(len(resp), resp)
                    cl.send(response.encode('utf-8'))
                except Exception as e:
                    resp = ujson.dumps({"ok": False, "error": str(e)})
                    response = 'HTTP/1.1 400 Bad Request\r\nContent-Type: application/json\r\nContent-Length: {}\r\n\r\n{}'.format(len(resp), resp)
                    cl.send(response.encode('utf-8'))
            else:
                resp = ujson.dumps({"ok": False, "error": "use POST"})
                response = 'HTTP/1.1 405 Method Not Allowed\r\nContent-Type: application/json\r\nContent-Length: {}\r\n\r\n{}'.format(len(resp), resp)
                cl.send(response.encode('utf-8'))
        else:
            resp = "Not found"
            response = 'HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\nContent-Length: {}\r\n\r\n{}'.format(len(resp), resp)
            cl.send(response.encode('utf-8'))
    except Exception as e:
        print("Error manejando cliente:", e)
    finally:
        try:
            cl_file.close()
        except:
            pass
        try:
            cl.close()
        except:
            pass

# ------------------------
# Loop principal
# ------------------------
def main_loop():
    server = start_server(80)
    last_measure = 0
    measure_interval = 2  # segundos
    # Usamos select-like behavior: aceptamos conexiones y periódicamente medimos
    while True:
        # Si MQTT tiene mensajes entrantes, revisarlos
        try:
            if mqtt:
                # reciba mensajes pendientes (non-blocking)
                mqtt.check_msg()
        except Exception:
            pass
        # Aceptar cliente con timeout corto
        server.settimeout(0.5)
        try:
            cl, addr = server.accept()
            print("Conexion desde", addr)
            handle_client(cl)
        except OSError:
            # timeout o no hay conexiones
            pass
        # medición periódica
        now = time.time()
        if now - last_measure >= measure_interval:
            medir_y_actualizar()
            last_measure = now
        # pequeño sleep para evitar busy loop
        time.sleep(0.05)

if __name__ == "__main__":
    print("IP asignada:", ip_info())
    try:
        main_loop()
    except KeyboardInterrupt:
        print("Detenido por usuario")
