#!/usr/bin/env bash
# capture_and_ping.sh
# Usage: sudo ./capture_and_ping.sh
# Starts tcpdump capturing attacker(h1..h4) <-> victim(h5),
# runs a short Mininet pingall test (linear 5 hosts),
# stops capture and copies pcap to project dir.

set -euo pipefail

PCAP_TMP="/tmp/attacker_victim.pcap"
DEST_DIR="$HOME/project/mininet/examples"
DEST="${DEST_DIR}/attacker_victim.pcap"

# BPF filter: h5 (10.0.0.5) AND (h1 or h2 or h3 or h4)
# Adjust IPs here if your hosts have different addresses.
BPF="(host 10.0.0.5) and (host 10.0.0.1 or host 10.0.0.2 or host 10.0.0.3 or host 10.0.0.4)"

# Interface to capture on. "any" is safe (captures on all host interfaces).
# You can replace "any" with a specific bridge (e.g., s1) if you know it.
IFACE="any"

# Ensure destination directory exists
mkdir -p "${DEST_DIR}"

# Cleanup function to stop tcpdump if script is killed
cleanup() {
  if [[ -n "${TCPDUMP_PID-}" ]]; then
    echo "Stopping tcpdump (pid ${TCPDUMP_PID})..."
    sudo kill "${TCPDUMP_PID}" 2>/dev/null || true
    sleep 1
  fi
}
trap cleanup EXIT

echo "Starting tcpdump on interface '${IFACE}' (filter: ${BPF}) -> ${PCAP_TMP}"
# Start tcpdump with -U to write packets as they arrive and -n to avoid DNS resolution
sudo tcpdump -i "${IFACE}" -n -U -w "${PCAP_TMP}" "${BPF}" &
TCPDUMP_PID=$!
echo "tcpdump pid: ${TCPDUMP_PID}"
sleep 1   # give tcpdump a moment to start

echo "Running Mininet test (linear topology with 5 hosts) -> pingall"
# This runs a short non-interactive topology and runs pingall, then exits.
# If you want to run your existing miniedit topology instead, run the pingall
# from inside that Mininet session and then run this script to capture only.
sudo mn --topo linear,5 --mac --switch ovs --controller remote --test pingall

echo "Mininet test finished. Stopping tcpdump..."
sudo kill "${TCPDUMP_PID}"
# wait a moment for tcpdump to flush/write final packets
sleep 1

# Ensure file exists and is readable
if [[ -f "${PCAP_TMP}" ]]; then
  echo "Copying pcap to ${DEST}"
  sudo cp "${PCAP_TMP}" "${DEST}"
  sudo chown "$(id -u):$(id -g)" "${DEST}"
  echo "Saved: ${DEST}"
else
  echo "ERROR: pcap file not found at ${PCAP_TMP}" >&2
  exit 2
fi

echo "Done."

