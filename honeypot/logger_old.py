import os
from datetime import datetime
from pathlib import Path

# In Docker, we want to point to the specific path defined in your Dockerfile
LOG_FILE = Path("/app/logs/honeypot.log")

def _write_to_file(line: str):
    """The core engine: opens the file, appends the line, and closes it."""
    try:
        # Ensure the directory exists
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        # If writing fails, we print to the console so 'docker logs' sees it
        print(f"CRITICAL LOG ERROR: {e}")

def log_event(message: str, level: str = "INFO"):
    """Standard system logs."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _write_to_file(f"{ts} - {level} - [SYSTEM] {message}")

def log_connection(ip, port, data, duration):
    """Specific format for Honeypot ATTACK logs."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Formatting it exactly how your assignment likely expects
    log_entry = f"{ts} - WARNING - [ATTACK] IP: {ip}, Port: {port}, Data: {data}, Duration: {duration:.2f}s"
    _write_to_file(log_entry)
    # Also print it so you can see it live in your terminal
    print(log_entry, flush=True)