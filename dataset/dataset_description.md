# Dataset Description

The dataset used in this project consists of packet captures generated during DDoS attack simulations in a Software Defined IoT (SD-IoT) environment.

Traffic was generated using Mininet and hping3 and captured using Wireshark.

## Traffic Types

- Normal Traffic
- TCP Flood
- UDP Flood
- ICMP Flood

## Capture Format

Packet Capture (.pcap)

## Feature Extraction

Packet-level features such as protocol type, packet length, TCP flags, source IP, destination IP, and timestamps were extracted from the packet capture and used during the machine learning workflow.

The original packet capture (`ddos_capture.pcap`) is included in this repository.