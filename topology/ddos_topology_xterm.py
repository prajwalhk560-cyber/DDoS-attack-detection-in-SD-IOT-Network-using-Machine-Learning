#!/usr/bin/env python2
"""
ddos_topology_combined_safe.py

- Builds 5-host / 3-switch topology (h1,h2 -> s1 ; h3,h4,h5 -> s2 ; s1,s2 -> s3)
- Connects switches to RemoteController at 127.0.0.1:6653 (configurable)
- Opens xterms:
    - h5-server: runs iperf -s (victim)
    - h1-client .. h4-client: run short iperf clients (3s @ 1M)
    - h5-monitor: runs monitor script that marks h5 unreachable if limit exceeded
- Writes a monitor script to /tmp/monitor_h5.sh (on host FS) and runs it inside h5.
- Usage:
    1) On host terminal: xhost +SI:localuser:root   # if you will run as sudo
    2) Start controller in another terminal: ryu-manager ryu.app.simple_switch_13
    3) Run: sudo python2 ~/ddos_topology_combined_safe.py
    4) When done: mininet> exit then sudo mn -c and xhost -SI:localuser:root
"""
from mininet.net import Mininet
from mininet.node import RemoteController, Controller, OVSSwitch
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.term import makeTerm
import time
import sys
import os

# Monitor script content (written to /tmp/monitor_h5.sh)
MONITOR_SCRIPT = r"""#!/bin/bash
# monitor_h5.sh
# Monitor inbound bytes on h5-eth0. If cumulative received bytes exceed
# LIMIT_BYTES, bring the interface down (makes host unreachable).
# Usage: ./monitor_h5.sh <limit_bytes> <poll_interval_seconds>

LIMIT_BYTES=${1:-200000}     # default limit 200000 bytes (~200 KB)
INTERVAL=${2:-1}             # default poll every 1 second
IFACE="h5-eth0"

echo "Monitor starting for interface $IFACE: limit=$LIMIT_BYTES bytes, interval=${INTERVAL}s"

# helper to get rx bytes
get_rx_bytes() {
    cat /sys/class/net/${IFACE}/statistics/rx_bytes 2>/dev/null || echo 0
}

initial=$(get_rx_bytes)
if [ -z "$initial" ]; then initial=0; fi
last=$initial
sum=0

while true; do
    sleep "$INTERVAL"
    cur=$(get_rx_bytes)
    if [ -z "$cur" ]; then
        echo "ERROR: cannot read /sys/class/net/${IFACE}/statistics/rx_bytes"
        exit 2
    fi

    delta=$((cur - last))
    if [ "$delta" -lt 0 ]; then
        delta=0
    fi
    sum=$((sum + delta))
    last=$cur

    echo "$(date +'%H:%M:%S') rx_delta=${delta} sum=${sum} bytes"

    if [ "$sum" -ge "$LIMIT_BYTES" ]; then
        echo "LIMIT EXCEEDED: sum=${sum} >= ${LIMIT_BYTES}. Marking $IFACE down (host unreachable)."
        ip link set dev ${IFACE} down
        echo "$(date +'%Y-%m-%dT%H:%M:%S') LIMIT_EXCEEDED sum=${sum} limit=${LIMIT_BYTES}" >> /tmp/monitor_h5.log
        exit 0
    fi
done
"""

def write_monitor_on_host(path="/tmp/monitor_h5.sh"):
    "Write the monitor script to the host filesystem and make it executable."
    try:
        with open(path, "w") as f:
            f.write(MONITOR_SCRIPT)
        os.chmod(path, 0o755)
        print "Wrote monitor script to %s" % path
    except Exception as e:
        print >> sys.stderr, "Failed to write monitor script to %s: %s" % (path, e)
        sys.exit(1)

def build_topology(use_remote_controller=True, ctrl_ip='127.0.0.1', ctrl_port=6653):
    info('*** Building topology\n')
    if use_remote_controller:
        net = Mininet(controller=RemoteController, link=TCLink, switch=OVSSwitch)
        net.addController('c0', controller=RemoteController, ip=ctrl_ip, port=ctrl_port)
        print "DEBUG: Using RemoteController at %s:%s" % (ctrl_ip, ctrl_port)
    else:
        net = Mininet(controller=Controller, link=TCLink, switch=OVSSwitch)
        net.addController('c0')
        print "DEBUG: Using internal Controller"

    # switches
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')

    # hosts
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    h3 = net.addHost('h3', ip='10.0.0.3/24')
    h4 = net.addHost('h4', ip='10.0.0.4/24')
    h5 = net.addHost('h5', ip='10.0.0.5/24')  # victim

    # links
    net.addLink(h1, s1)
    net.addLink(h2, s1)

    net.addLink(h3, s2)
    net.addLink(h4, s2)
    net.addLink(h5, s2)

    net.addLink(s1, s3)
    net.addLink(s2, s3)

    info('*** Topology built\n')
    return net

def main():
    setLogLevel('info')

    # 1) write monitor script on host
    write_monitor_on_host("/tmp/monitor_h5.sh")

    # 2) build topology
    net = build_topology(use_remote_controller=True, ctrl_ip='127.0.0.1', ctrl_port=6653)

    info('*** Starting network\n')
    try:
        net.start()
    except Exception as e:
        print >> sys.stderr, "ERROR: net.start() failed:", e
        net.stop()
        sys.exit(1)

    time.sleep(0.5)

    info('*** Hosts: %s\n' % [h.name for h in net.hosts])
    victim = net.get('h5')
    attackers = [net.get(n) for n in ('h1','h2','h3','h4')]

    # safe test params
    duration = 3
    bw = '1M'

    info('*** Opening xterms and starting iperf server & clients\n')

    # start iperf server in xterm for victim; keep shell open
    makeTerm(victim, title='h5-server', cmd="bash -c 'iperf -s; echo; echo \"iperf server exited. Press Enter to close.\"; read'")

    time.sleep(0.5)

    # open attacker xterms and run short iperf clients
    for a in attackers:
        cmd = "bash -c 'sleep 0.2; iperf -c %s -t %d -b %s; echo; echo \"Client finished. Press Enter to close.\"; read'" % (victim.IP(), duration, bw)
        makeTerm(a, title=a.name + '-client', cmd=cmd)
        time.sleep(0.15)

    # open a monitor xterm for h5 so you can see monitor output live
    # (monitor script is on host /tmp/monitor_h5.sh; hosts share host filesystem)
    monitor_limit = 200000   # bytes threshold (200 KB default)
    monitor_interval = 1     # seconds
    mon_cmd = "bash -c '/tmp/monitor_h5.sh %d %d; echo; echo \"Monitor exited. Press Enter to close.\"; read'" % (monitor_limit, monitor_interval)
    makeTerm(victim, title='h5-monitor', cmd=mon_cmd)

    info('\n*** Xterms are open. Monitor and server are running on h5.\n')
    info('*** Inspect flows from this terminal with:\n')
    info('    sh ovs-ofctl dump-flows s1\n')
    info('    sh ovs-ofctl dump-flows s2\n')
    info('    sh ovs-ofctl dump-flows s3\n')
    info('*** To capture packets on victim:\n')
    info('    h5 tcpdump -n -i h5-eth0 -c 200 -w /tmp/ddos_capture.pcap\n')
    info('\n*** Dropping to CLI - use exit to stop and cleanup\n')

    CLI(net)

    info('*** Stopping network and cleanup\n')
    try:
        net.stop()
    except Exception as e:
        print >> sys.stderr, "ERROR stopping network:", e

    print "Done."

if __name__ == '__main__':
    main()

