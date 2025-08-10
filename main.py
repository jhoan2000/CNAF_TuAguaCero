import flet as ft
import paho.mqtt.client as mqtt
import json
import threading
import time
import hashlib
import base64
from Crypto.Cipher import AES
import os
SECRET_KEY = b"TuAguaCero101124" # Clave secreta de 16 bytes
PIN_AUTORIZADO = "101124"

# Variables globales
distancia = "---"
bomba_riego = False
page = None
#------------------------------------
MIN_DIST = 20
MAX_DIST = 115
# Contenedor de la barra
barra_altura_px = 300  # altura visual de la barra
#-----------------------------------
# Descifrado AES ECB
def descifrar_valor(valor_base64):
    cipher = AES.new(SECRET_KEY, AES.MODE_ECB)
    encrypted_bytes = base64.b64decode(valor_base64)
    decrypted = cipher.decrypt(encrypted_bytes).decode()
    return decrypted.strip()


# Validar firma
def validar_datos(data, firma):
    json_bytes = json.dumps(data).encode()
    h = hashlib.sha256()
    h.update(json_bytes + SECRET_KEY)
    return h.hexdigest() == firma


def on_connect(client, userdata, flags, rc):
    print("Conectado al broker MQTT")
    client.subscribe("tuaguacero/LWF")

def on_message(client, userdata, msg):
    global distancia, bomba_riego
    try:
        decoded = msg.payload.decode()
        payload = json.loads(decoded)

        data = payload.get("data")
        firma = payload.get("firma")

        if not validar_datos(data, firma):
            print("⚠️ Firma inválida. Ignorando mensaje.")
            return

        pin_cifrado = data.get("pin")
        if descifrar_valor(pin_cifrado) != PIN_AUTORIZADO:
            print("⚠️ PIN no autorizado")
            return

        distancia = descifrar_valor(data["dist"])
        bomba_riego = descifrar_valor(data["bomba_filtro"])
        bomba_riego = bomba_riego.lower() == "true"  # Convertir a booleano

        print(
            f"Datos recibidos: Distancia={distancia} m, Riego={bomba_riego}"
        )
        update_ui()
    except Exception as e:
        print("Error al procesar mensaje:", e)
        print("Contenido bruto:", msg.payload)


def update_ui():
    txt_dist.value = f"distancia: {distancia} m"
    txt_filtros.value = "FILTRANDO AGUA" if bomba_riego else "FILTRADO DESACTIVADO"
    txt_filtros.color = "green" if bomba_riego else "red"
    try:
        porcentaje = (MAX_DIST - float(distancia)) / (MAX_DIST - MIN_DIST)
        porcentaje = max(0, min(1, porcentaje))  # limitar entre 0 y 1
        # Altura del agua
        agua.height = barra_altura_px * porcentaje

        # Posición del indicador
        indicador.top = barra_altura_px * (1 - porcentaje)
        indicador.bgcolor = ft.Colors.GREEN if porcentaje > 0.3 else ft.Colors.RED
    except:
        pass
    page.update()




mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message


def start_mqtt():
    mqtt_client.connect("broker.hivemq.com", 1883, 60)
    mqtt_client.loop_forever()


def main(p):
    global page, txt_dist, txt_filtros, indicador, agua
    page = p
    page.title = "Nivel F Tu Agua Cero"
    page.favicon =  "icon.ico"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT

    

    txt_dist = ft.Text(f"distancia: {distancia} m", size=24)
    txt_filtros = ft.Text(
        f"FILTRADO DESACTIVADO", size=28, weight=ft.FontWeight.BOLD, color="blue"
    )


    # Fondo del tanque
    barra_fondo = ft.Container(
        width=300,
        height=barra_altura_px,
        bgcolor=ft.Colors.BLUE_GREY_200,
        border_radius=10
    )
    # Agua (altura se calcula dinámicamente)
    agua = ft.Container(
        width=300,
        height=0,  # se ajusta según porcentaje
        bgcolor=ft.Colors.BLUE_400,
        opacity=0.5,  # semitransparente
        bottom=0  # anclado abajo
    )


    # Indicador de nivel
    indicador = ft.Container(
        width=300,
        height=2,
        bgcolor=ft.Colors.RED,
        top=0
    )
    # Layout con barra y valor
    barra_con_indicador = ft.Stack(
        [
            barra_fondo,
            agua,
            indicador
        ],
        width=300,
        height=barra_altura_px
    )

    # Función para actualizar el nivel
    def actualizar_barra():
        try:
            # distancia → porcentaje (invertido porque más distancia es menos agua)
            porcentaje = (MAX_DIST - float(distancia)) / (MAX_DIST - MIN_DIST)
            porcentaje = max(0, min(1, porcentaje))  # limitar a [0, 1]

            # calcular posición Y del indicador (0 arriba, barra_altura_px abajo)
            pos_y = barra_altura_px * (1 - porcentaje)
            indicador.top = pos_y
            indicador.bgcolor = ft.Colors.GREEN if porcentaje > 0.3 else ft.Colors.RED
        except:
            pass

    def enviar_comando_filtros(encender: bool):
        payload = {"bomba_filtro": encender}
        mqtt_client.publish("tuaguacero/control_filtros", json.dumps(payload))
        print(f"Comando enviado: {payload}")

    # --- Botón para cambiar estado ---
    def toggle_filtros(e):
        nuevo_estado = not bomba_riego
        enviar_comando_filtros(nuevo_estado)

    btn_filtros = ft.ElevatedButton("Encender/Apagar filtros", on_click=toggle_filtros)

    contenido_sensor = ft.Column(
        [
            ft.Text("Estado del Sensor", size=40, weight=ft.FontWeight.BOLD),
            txt_dist,
            txt_filtros,
            barra_con_indicador,  # barra visual del tanque
            btn_filtros
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        visible=False,
    )

    # --- Enviar comando para encender/apagar usando el mismo estado que bomba_riego ---
    

    txt_usuario = ft.TextField(label="Usuario")
    txt_clave = ft.TextField(label="PIN", password=True)

    def autenticar(e):
        if txt_clave.value == PIN_AUTORIZADO:
            dlg.open = False
            contenido_sensor.visible = True
            page.update()
        else:
            txt_clave.error_text = "PIN incorrecto"
            page.update()

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Inicio de Sesión"),
        content=ft.Column(
            [
                txt_usuario,
                txt_clave,
            ]
        ),
        actions=[ft.TextButton("Ingresar", on_click=autenticar)],
        actions_alignment=ft.MainAxisAlignment.END,
        open=True,
    )
    page.add(contenido_sensor)  # aunque esté oculto

    page.dialog = dlg
    page.open(dlg)  # <-- aquí lo muestras al iniciar

    def update_task():
        while True:
            if contenido_sensor.visible:
                txt_dist.value = f"distancia: {distancia} m"
                txt_filtros.value = (
                    "FILTRANDO AGUA" if bomba_riego else "FILTRADO DESACTIVADO"
                )
                txt_filtros.color = "green" if bomba_riego else "red"
                page.update()
            time.sleep(1)

    threading.Thread(target=update_task, daemon=True).start()

threading.Thread(target=start_mqtt, daemon=True).start()

ft.app(target=main, assets_dir="assets", view=ft.WEB_BROWSER, port=int(os.environ.get("PORT", 5000)))