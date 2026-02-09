import logging
import os
import socket
import time
from logger import log_event, log_connection

BANNER = "SSH-2.0-OpenSSH_8.2p1\r\n"

def run_honeypot():
    # Setup server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 22))
    server.listen(5)
    
    log_event("Honeypot service simulation started.")

    while True:
        client, addr = server.accept()
        start_time = time.time()
        
        try:
            client.send(BANNER.encode())
            client.settimeout(2.0)
            data = client.recv(1024)
            
            duration = time.time() - start_time
            attack_data = data.decode('utf-8', 'ignore').strip() if data else "No data"
            
            # CALL YOUR NEW CUSTOM LOGGER
            log_connection(addr[0], addr[1], attack_data, duration)
            
        except Exception as e:
            log_event(f"Connection error: {e}", "ERROR")
        finally:
            client.close()

if __name__ == "__main__":
    run_honeypot()