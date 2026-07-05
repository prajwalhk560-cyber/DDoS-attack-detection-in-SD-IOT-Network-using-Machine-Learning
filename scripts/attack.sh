#!/usr/bin/env bash
# attack.sh - simple, safe traffic generator (iperf3) + capture (tcpdump)
# NOTE: Run only in lab environments or against machines you own / have permission to test.

set -e

if [ $# -lt 1 ]; then
  echo "Usage: $0 <server-ip> [bandwidth] [duration]"
  echo "  example: $0 10.0.0.2 10M 15"
  exit 1
fi

SERVER_IP="$1"
BANDWIDTH="${2:-10M}"
DURATION="${3:-15}"

PCAP="/tmp/iperf_${SERVER_IP//./_}.pcap"
IFACE="eth0"

# Try to detect an interface if eth0 doesn't exist
if ! ip link show "$IFACE" >/dev/null 2>&1; then
  IFACE=$(ip -o link show | awk -F': ' '/: e/ {print $2; exit}') || IFACE="eth0"
fi

echo "Server: $SERVER_IP | bw: $BANDWIDTH | dur: ${DURATION}s | iface: $IFACE"
echo "Starting tcpdump (background) -> $PCAP"
sudo timeout $((DURATION + 5)) tcpdump -n -i "$IFACE" -w "$PCAP" >/dev/null 2>&1 &
TCPDUMP_PID=$!

sleep 1
if ! command -v iperf3 >/dev/null 2>&1; then
  echo "iperf3 not found. Install inside Mininet host or on system and retry."
  kill "$TCPDUMP_PID" 2>/dev/null || true
  exit 1
fi

echo "Running iperf3 client to $SERVER_IP for ${DURATION}s at $BANDWIDTH..."
iperf3 -c "$SERVER_IP" -t "$DURATION" -b "$BANDWIDTH" || true

sleep 1
if ps -p "$TCPDUMP_PID" >/dev/null 2>&1; then
  kill "$TCPDUMP_PID" 2>/dev/null || true
fi

echo "Done. Capture saved to: $PCAP"
echo "Analyze: tshark -r $PCAP -q -z io,stat,1  OR open with Wireshark"


