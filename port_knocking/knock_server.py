#!/usr/bin/env python3
import argparse
import logging
import socket
import time
import os
import select

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

def open_protected_port(protected_port, remote_ip):
    os.system(f"iptables -I INPUT -p tcp -s {remote_ip} --dport {protected_port} -j ACCEPT")
    logging.info(f"!!! SUCCESS: Opened port {protected_port} for {remote_ip}")

def initialize_firewall(protected_port):
    logging.info(f"Initializing firewall: Dropping all traffic to port {protected_port}")
    os.system("iptables -F INPUT")
    os.system(f"iptables -A INPUT -p tcp --dport {protected_port} -j REJECT")

def listen_for_knocks(sequence, window_seconds, protected_port):
    logger = logging.getLogger("KnockServer")
    initialize_firewall(protected_port)

    # sockets for every port in the sequence
    sockets = []
    for knock_port in sequence:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.bind(('0.0.0.0', knock_port))
            s.setblocking(False)
            sockets.append(s)
        except Exception as e:
            logger.error(f"Could not bind to port {knock_port}: {e}")
            return

    client_states = {} # { ip: [current_step_index, last_knock_time] }
    logger.info(f"Server ready. Sequence: {sequence}. Window: {window_seconds}s")

    while True:
        readable, _, _ = select.select(sockets, [], [], 0.1)
        now = time.time()
        
        for s in readable:
            try:
                data, addr = s.recvfrom(1024)
                if not addr:
                    continue
                
                ip = addr[0]
                knock_port = s.getsockname()[1]
                port_index = sequence.index(knock_port)

                if ip not in client_states:
                    # sequence begins at the first port
                    if port_index == 0:
                        client_states[ip] = [1, now]
                        logger.info(f"[*] Knock 1/{len(sequence)} from {ip} on {knock_port}")
                    else:
                        logger.warning(f"[!] Out-of-order knock from {ip} on {knock_port}. Ignoring.")
                else:
                    current_step, _ = client_states[ip]
                    
                    if port_index == current_step:
                        client_states[ip][0] += 1
                        client_states[ip][1] = now
                        logger.info(f"[*] Knock {client_states[ip][0]}/{len(sequence)} from {ip} on {knock_port}")

                        if client_states[ip][0] == len(sequence):
                            open_protected_port(protected_port, ip)
                            del client_states[ip]
                    else:
                        # incorrect port flagged and reset
                        logger.warning(f"[!] WRONG PORT {knock_port} from {ip}. Resetting sequence.")
                        del client_states[ip]

            except Exception as e:
                logger.error(f"Error handling packet: {e}")

        # timeout between knocks
        for ip in list(client_states.keys()):
            if (now - client_states[ip][1]) > window_seconds:
                logger.info(f"[-] Session expired for {ip}. Sequence reset.")
                del client_states[ip]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sequence", default="1234,5678,9012")
    parser.add_argument("--protected-port", type=int, default=2222)
    parser.add_argument("--window", type=float, default=10.0)
    args = parser.parse_args()

    setup_logging()
    sequence = [int(p) for p in args.sequence.split(",")]
    
    try:
        listen_for_knocks(sequence, args.window, args.protected_port)
    except KeyboardInterrupt:
        logging.info("Server shutting down.")

if __name__ == "__main__":
    main()