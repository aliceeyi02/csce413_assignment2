from flask import Flask, render_template, request, g
import datetime
import time
import os

app = Flask(__name__)
LOG_FILE = "/app/logs/honeypot.log"

@app.before_request
def start_timer():
    # starting a timer before the request begings
    g.start_time = time.time()

@app.after_request
def log_everything(response):
    # find the duration for the logs
    duration = time.time() - g.start_time
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # find data for logs
    ip = request.remote_addr
    port = request.environ.get('REMOTE_PORT', '0000') 
    username = request.form.get('username', '-')
    password = request.form.get('password', '-')
    path = request.path
    method = request.method
    
    #  formatting for log
    log_entry = (f"[{timestamp}] SRC: {ip}:{port} | DUR: {duration:.4f}s | "
                 f"ACTION: {method} {path} | AUTH: {username}:{password}\n")

    # write to log file
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)
        
    return response

@app.route('/', methods=['GET', 'POST'])
def index():
    # database connection "failed"
    error = None
    if request.method == 'POST':
        error = "Critical Error: Database Connection Timed Out. Please try again later."
    return render_template('index.html', error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)