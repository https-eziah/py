from flask import Flask, request, redirect
from datetime import datetime

import os

app = Flask(__name__)

def log_ip(ip):
    with open("ips.txt", "a") as f:
        f.write(f"{datetime.now()} - {ip}\n")

@app.route('/')
def home():
    return "Server is running!"

@app.route('/go')
def track():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    log_ip(ip)
    return redirect("https://www.youtube.com")

if __name__ == '__main__':
    # Render provides the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

    