from flask import Flask, render_template, request, g
import datetime
import time
import os

app = Flask(__name__)
LOG_FILE = "/app/logs/honeypot.log"

@app.before_request
def start_timer():
    # Record the exact microsecond the request hits the server
    g.start_time = time.time()

@app.after_request
def log_everything(response):
    # Calculate duration
    duration = time.time() - g.start_time
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Get Source IP and Port
    # Note: request.environ gets the underlying WSGI details
    ip = request.remote_addr
    port = request.environ.get('REMOTE_PORT', '0000') 
    
    # Capture Auth Attempts
    username = request.form.get('username', '-')
    password = request.form.get('password', '-')
    
    # Capture Data/Commands (Raw body or form data)
    path = request.path
    method = request.method
    
    # Format: Timestamp | IP:Port | Duration | Method/Path | User:Pass
    log_entry = (f"[{timestamp}] SRC: {ip}:{port} | DUR: {duration:.4f}s | "
                 f"ACTION: {method} {path} | AUTH: {username}:{password}\n")

    # Ensure log directory exists and write
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)
        
    return response

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    if request.method == 'POST':
        error = "Critical Error: Database Connection Timed Out. Please try again later."
    return render_template('index.html', error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)