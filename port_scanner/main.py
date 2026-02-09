import socket
import sys
import concurrent.futures
from datetime import datetime
import ipaddress
import csv  # Added for CSV export

def scan_port(target, port):
    """Checks if a single port is open and grabs its banner."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.2)  # Reduced for faster scanning inside Docker
            if s.connect_ex((target, port)) == 0:
                banner = "No banner"
                try:
                    s.sendall(b"Hello\r\n")
                    banner = s.recv(1024).decode(errors='ignore').strip().replace(',', ';')
                except:
                    pass
                
                try:
                    service = socket.getservbyport(port)
                except:
                    service = "unknown"
                
                # Return target IP along with results for CSV mapping
                return {"ip": target, "port": port, "service": service, "banner": banner}
    except:
        pass
    return None

def scan_range(target, start_port, end_port):
    """Scans a range of ports using multithreading."""
    open_ports = []
    print(f"[*] Scanning {target} from port {start_port} to {end_port}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=1000) as executor:
        futures = {executor.submit(scan_port, target, port): port for port in range(start_port, end_port + 1)}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                print(f" [+] Found {result['ip']}:{result['port']} - {result['service']}")
                open_ports.append(result)

    return sorted(open_ports, key=lambda x: x['port'])

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 port_scanner.py <target> [start_port] [end_port]")
        sys.exit(1)

    target_input = sys.argv[1]
    try:
        start_port = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        end_port = int(sys.argv[3]) if len(sys.argv) > 3 else 1024
    except ValueError:
        print("[-] Error: Port range must be integers.")
        sys.exit(1)

    try:
        targets = [str(ip) for ip in ipaddress.ip_network(target_input, strict=False)]
    except ValueError:
        targets = [target_input]

    start_time = datetime.now()
    total_found = []

    for t in targets:
        results = scan_range(t, start_port, end_port)
        total_found.extend(results)

    # --- CSV Export Logic ---
    filename = f"scan_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    keys = ["ip", "port", "service", "banner"]
    
    with open(filename, "w", newline="") as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(total_found)

    duration = datetime.now() - start_time
    print(f"\n[+] Scan complete! Time elapsed: {duration}")
    print(f"[+] Found {len(total_found)} open ports. Results saved to: {filename}")

if __name__ == "__main__":
    main()