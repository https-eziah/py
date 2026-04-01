from flask import Flask, request, redirect
from datetime import datetime

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
    return redirect("https://example.com")

if __name__ == '__main__':
    app.run(debug=True)