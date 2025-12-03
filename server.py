from flask import Flask, send_file, jsonify

app = Flask(__name__)

# Ruta donde guardas los archivos que vas a enviar al ESP
FIRMWARE_FOLDER = "firmware/"


@app.get("/firmware/version")
def version():
    return send_file(FIRMWARE_FOLDER + "version.txt", mimetype="text/plain")


@app.get("/firmware/main")
def main_file():
    return send_file(FIRMWARE_FOLDER + "main.py", mimetype="text/plain")

@app.get("/firmware/boot")
def main_boot():
    return send_file(FIRMWARE_FOLDER +  "boot.py", mimetype="text/plain")

@app.get("/firmware/README")
def readme_file():
    return send_file(FIRMWARE_FOLDER + "README", mimetype="text/plain")

@app.get("/firmware/cifrar_aes")
def aes_file():
    return send_file(FIRMWARE_FOLDER + "cifrar_aes.py", mimetype="text/plain")

@app.get("/firmware/uts_water")
def uts_file():
    return send_file(FIRMWARE_FOLDER + "uts_water.py", mimetype="text/plain")

@app.get("/firmware/connect_mqtt")
def connect_mqtt_file():
    return send_file(FIRMWARE_FOLDER + "connect_mqtt.py", mimetype="text/plain")


@app.get("/")
def home():
    return {"status": "OK", "message": "Servidor OTA funcionando"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

