
# decrypt_loader.py – Secure AES-256 model decryptor

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import os
import security_config

MODEL_KEY = security_config.SECRET_KEY
if not MODEL_KEY or MODEL_KEY == "fallback-secret-key":
    raise ValueError("MODEL_AES_KEY is not set. Check your .env file.")
MODEL_KEY = MODEL_KEY.encode()

def decrypt_model_npz(file_path):
    with open(file_path, "rb") as f:
        iv = f.read(16)
        ct = f.read()
    cipher = AES.new(MODEL_KEY, AES.MODE_CBC, iv)
    data = unpad(cipher.decrypt(ct), AES.block_size)
    return data
