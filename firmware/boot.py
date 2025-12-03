import network, urequests, machine, os, time

WIFI_SSID = "ZTE_E2FF51"
WIFI_PASS = "35600911"

SERVER = "http://192.168.0.154:5000"
URL_VERSION = SERVER + "/firmware/version"
URL_MAIN = SERVER + "/firmware/main"
URL_BOOT = SERVER + "/firmware/boot"
URL_README = SERVER + "/firmware/README"
URL_AES = SERVER + "/firmware/cifrar_aes"
URL_UTS = SERVER + "/firmware/uts_water"
URL_CONNECT_MQTT = SERVER + "/firmware/connect_mqtt"


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
        print("GET:", url)
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
    if "version.txt" in os.listdir():
        with open("version.txt") as f:
            local_ver = f.read().strip()
            print("VL: ", local_ver)
    print("HERE 3")
    # versión remota
    remote_ver = get(URL_VERSION)
    
    if not remote_ver:
        print("No pude obtener versión remota")
        return
    else : print("VR: ", remote_ver)

    remote_ver = remote_ver.strip()
    print("Local:", local_ver, "Remota:", remote_ver)

    if local_ver == remote_ver:
        print("Sin actualización")
        return

    print("Nueva actualización disponible!")

    # descargar main.py
    new_main = get(URL_MAIN)
    new_boot = get(URL_BOOT)
    new_readme = get(URL_README)
    new_aes = get(URL_AES)
    new_uts = get(URL_UTS)
    new_connect_mqtt = get(URL_CONNECT_MQTT)
    files = {
        "main.py": new_main,
        "boot.py": new_boot,
        "README": new_readme,
        "cifrar_aes.py": new_aes,
        "uts_water.py": new_uts,
        "connect_mqtt.py": new_connect_mqtt
    }
    for filename, content in files.items():
        if content:
            with open(filename, "w") as f:
                f.write(content)
                print(f"{filename} actualizado.") 
        else:
            print(f"Error descargando {filename}")
            return
          
    # actualizar versión
    with open("version.txt", "w") as f:
        f.write(remote_ver)
    print("Actualizado → Reiniciando")
    time.sleep(5)
    machine.reset()


wifi()
update()
