# --- Configuración protegida ---
import ujson
import uhashlib
import ubinascii
import ucryptolib
import time

SECRET_KEY = b"TuAguaCero101124" # exactamente 16 bytes
PIN_AUTENTICACION = "101124" # PIN de autenticación para el usuario
# --- AES ECB Encryption ---
def cifrar_valor(valor):
    aes = ucryptolib.aes(SECRET_KEY, 1)  # AES MODE_ECB

    valor_str = str(valor)

    # --- Rellenar a múltiplo de 16 (Padding con espacios) ---
    while len(valor_str) % 16 != 0:
        valor_str += " "

    encrypted = b""
    # --- Cifrar por bloques ---
    for i in range(0, len(valor_str), 16):
        block = valor_str[i:i+16].encode()
        encrypted += aes.encrypt(block)

    return ubinascii.b2a_base64(encrypted).decode().strip()

# --- Cifrado de datos (hash para integridad) ---
def firmar_datos(data_json):
    h = uhashlib.sha256()
    h.update(data_json + SECRET_KEY)
    return h.digest().hex()
