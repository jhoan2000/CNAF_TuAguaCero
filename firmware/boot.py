import network, urequests, os, machine, time

WIFI_SSID = "ZTE_E2FF51"
WIFI_PASS = "35600911"

SERVER = "http://192.168.0.154:5000"

URL_VERSION = SERVER + "/firmware/version"
URL_LIST = SERVER + "/firmware/list"
URL_FILE = SERVER + "/firmware/file/"


def wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conectando...")
        wlan.connect(WIFI_SSID, WIFI_PASS)
        while not wlan.isconnected():
            time.sleep(1)
    print("Conectado:", wlan.ifconfig())


def get(url):
    try:
        r = urequests.get(url)
        if r.status_code == 200:
            data = r.text
            r.close()
            return data
    except Exception as e:
        print("ERROR:", e)
    return None


def update():
    # versión local
    local_ver = "0"
    try:
        with open("version.txt") as f:
            local_ver = f.read().strip()
    except:
        print("version.txt no existe, usando versión 0")
        local_ver = "0"

    print("Versión local:", local_ver)

    # versión remota
    remote_ver = get(URL_VERSION)
    if not remote_ver:
        print("No pude obtener versión remota")
        return

    remote_ver = remote_ver.strip()
    print("Versión remota:", remote_ver)

    if local_ver == remote_ver:
        print("Sin actualización")
        return

    print("Nueva actualización disponible!")

    # obtener lista de archivos
    file_list_raw = get(URL_LIST)
    if not file_list_raw:
        print("Error obteniendo lista de archivos")
        return

    import json
    files = json.loads(file_list_raw)

    for filename in files:
        print("Descargando:", filename)
        content = get(URL_FILE + filename)

        if content:
            with open(filename, "w") as f:
                f.write(content)
            print("Actualizado:", filename)
        else:
            print("Error al descargar:", filename)

    # actualizar versión local
    with open("version.txt", "w") as f:
        f.write(remote_ver)

    print("Actualización completa. Reiniciando...")
    time.sleep(3)
    machine.reset()


wifi()
update()
