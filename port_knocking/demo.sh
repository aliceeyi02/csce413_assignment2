#!/usr/bin/env bash

set -euo pipefail

TARGET_IP=${1:-172.20.0.40}
SEQUENCE=${2:-"1234,5678,9012"}
PROTECTED_PORT=${3:-2222}

CLIENT_SCRIPT="./knock_client.py"

echo "Port Knocking Demo Starting..."

echo "Resetting firewall..."
docker exec 2_network_port_knocking iptables -F INPUT
docker exec 2_network_port_knocking iptables -A INPUT -p tcp --dport "$PROTECTED_PORT" -j REJECT

echo "[1/3] Attempting protected port before knocking"
if nc -z -v -w 2 "$TARGET_IP" "$PROTECTED_PORT" 2>/dev/null; then
    echo "ERROR: Port is already open. Manual reset failed."
    exit 1
else
    echo "Confirmed: Port $PROTECTED_PORT is closed/filtered."
fi

echo ""
echo "[2/3] Step 2: Sending knock sequence: $SEQUENCE"
python3 "$CLIENT_SCRIPT" --target "$TARGET_IP" --sequence "$SEQUENCE"
sleep 1.5 

echo ""
echo "[3/3] Attempting protected port after knocking"
if nc -z -v -w 5 "$TARGET_IP" "$PROTECTED_PORT"; then
    echo "Success! Port is now open"
else
    echo "Failed to open port"
    exit 1
fi