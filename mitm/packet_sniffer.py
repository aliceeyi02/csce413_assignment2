#!/usr/bin/env python3
import json
import argparse
from scapy.all import sniff, IP, TCP, Raw

def extract_json_from_payload(payload):
    """Attempt to decode and parse JSON from raw bytes."""
    try:
        start = payload.find(b'{')
        end = payload.rfind(b'}')
        if start != -1 and end != -1:
            json_str = payload[start:end+1].decode('utf-8', errors='ignore')
            return json.loads(json_str)
    except:
        return None

def packet_handler(packet):
    """Callback function to process each captured packet."""
    if packet.haslayer(Raw) and packet.haslayer(IP):
        payload = packet[Raw].load
        data = extract_json_from_payload(payload)
        
        if data:
            src = packet[IP].src
            dst = packet[IP].dst
            print(f"\n[+] JSON Caught! {src} -> {dst}")
            print(json.dumps(data, indent=4))
            
            # checking for flag
            if "flag" in str(data).lower():
                print(">>> !!! FLAG DETECTED !!! <<<")
            print("-" * 40)

def main():
    parser = argparse.ArgumentParser(description="Parameter-based JSON Flag Hunter")
    
    # parameters
    parser.add_argument("-i", "--interface", required=True, help="Network interface (e.g., br-54760...)")
    parser.add_argument("-n", "--net", default="172.20.0.0/16", help="Subnet to watch (default: 172.20.0.0/16)")
    parser.add_argument("-p", "--ports", default="1-65535", help="Port range (default: 1-65535)")
    
    args = parser.parse_args()

    # BPF filter
    bpf_filter = f"tcp and net {args.net} and portrange {args.ports}"

    print(f"[*] Starting sniffer on {args.interface}...")
    print(f"[*] Filter: {bpf_filter}")
    print("[*] Waiting for JSON traffic...")

    try:
        sniff(iface=args.interface, filter=bpf_filter, prn=packet_handler, store=0)
    except KeyboardInterrupt:
        print("\n[*] Stopping sniffer.")
    except Exception as e:
        print(f"\n[!] Error: {e}")

if __name__ == "__main__":
    main()