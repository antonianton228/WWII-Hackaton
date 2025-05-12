import os

import requests
from pprint import pprint
import json
import subprocess
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

def start_xray_with_config():
    subprocess.Popen(["xray", "run", "-c", 'proxy_config.json'])

# xray_config = json.loads(open("./TextGenerator/proxy_config.json", 'r', encoding="utf-8").read())
start_xray_with_config()

proxies = {
    'http': 'socks5://[::1]:1080',
    'https': 'socks5://[::1]:1080'
}

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
params = {"key": os.getenv("GENIMY_API")}
payload = {
    "contents": [{
        "parts": [{
            "text": "Что ты умеешь? Распиши все возможности"
        }]
    }]
}

response = requests.post(url, json=payload, params=params, proxies=proxies, timeout=10)
pprint(response.json())