#!/usr/bin/env python3
"""Starter template for the port knocking server."""

import argparse
import logging
import socket
import time
import os

DEFAULT_KNOCK_SEQUENCE = [1234, 5678, 9012]
DEFAULT_PROTECTED_PORT = 2222
DEFAULT_SEQUENCE_WINDOW = 10.0


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


def open_protected_port(protected_port):
    """Open the protected port using firewall rules."""
    # TODO: Use iptables/nftables to allow access to protected_port.
    os.system(f"iptables -I INPUT -p tcp --dport {protected_port} -j ACCEPT")
    logging.info("TODO: Open firewall for port %s", protected_port)


def close_protected_port(protected_port):
    """Close the protected port using firewall rules."""
    # TODO: Remove firewall rules for protected_port.
    os.system(f"iptables -D INPUT -p tcp --dport {protected_port} -j ACCEPT")
    logging.info("TODO: Close firewall for port %s", protected_port)


def listen_for_knocks(sequence, window_seconds, protected_port):
    """Listen for knock sequence and open the protected port."""
    logger = logging.getLogger("KnockServer")
    logger.info("Listening for knocks: %s", sequence)
    logger.info("Protected port: %s", protected_port)

    sockets = []
    # TODO: Create UDP or TCP listeners for each knock port.
    for knock_port in sequence:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.bind(('0.0.0.0', knock_port))
            s.setblocking(False)
            sockets.append(s)
        except Exception as e:
            logger.error("Could not bind to port %d: %s", knock_port, e)

    # TODO: Track each source IP and its progress through the sequence.
    client_states = {}
    while True:
        for i, s in enumerate(sockets):
            try:
                # Increased buffer and checking for actual data
                data, addr = s.recvfrom(1024)
                if addr:
                    ip = addr[0]
                    now = time.time()
                    knock_port = sequence[i]
                    logger.info(f"[*] Raw hit detected on port {knock_port} from {ip}")

                    if ip not in client_states or (now - client_states[ip][1]) > window_seconds:
                        client_states[ip] = [0, now]

                    current_step, start_time = client_states[ip]
                    
                    # ... (rest of your logic: step, timeout check, etc.)
                    if knock_port == sequence[current_step]:
                        client_states[ip][0] += 1
                        if client_states[ip][0] == len(sequence):
                            open_protected_port(protected_port)
                            del client_states[ip]
                    else:
                        client_states[ip] = [0, now]
            except BlockingIOError:
                continue
            except Exception as e:
                logger.error(f"Socket error: {e}")
        time.sleep(0.01) # Small sleep to prevent 100% CPU usage

def parse_args():
    parser = argparse.ArgumentParser(description="Port knocking server starter")
    parser.add_argument(
        "--sequence",
        default=",".join(str(port) for port in DEFAULT_KNOCK_SEQUENCE),
        help="Comma-separated knock ports",
    )
    parser.add_argument(
        "--protected-port",
        type=int,
        default=DEFAULT_PROTECTED_PORT,
        help="Protected service port",
    )
    parser.add_argument(
        "--window",
        type=float,
        default=DEFAULT_SEQUENCE_WINDOW,
        help="Seconds allowed to complete the sequence",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    setup_logging()

    try:
        sequence = [int(port) for port in args.sequence.split(",")]
    except ValueError:
        raise SystemExit("Invalid sequence. Use comma-separated integers.")

    listen_for_knocks(sequence, args.window, args.protected_port)


if __name__ == "__main__":
    main()
    