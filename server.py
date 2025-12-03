from flask import Flask, send_from_directory, jsonify
import os

app = Flask(__name__)

FIRMWARE_FOLDER = "firmware"

@app.get("/firmware/list")
def list_files():
    files = os.listdir(FIRMWARE_FOLDER)
    return jsonify(files)

@app.get("/firmware/file/<path:filename>")
def download_file(filename):
    return send_from_directory(FIRMWARE_FOLDER, filename)

@app.get("/firmware/version")
def version():
    return send_from_directory(FIRMWARE_FOLDER, "version.txt")

@app.get("/")
def home():
    return {"status": "OK", "message": "Servidor OTA funcionando"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
