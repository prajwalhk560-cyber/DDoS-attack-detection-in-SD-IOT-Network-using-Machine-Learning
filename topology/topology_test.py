#!/usr/bin/env python2
"""
topology_test.py  (Python 2)

- Builds the 5-host / 3-switch topology (h1..h5, s1,s2,s3).
- Connects switches to a RemoteController at 127.0.0.1:6653.
- Starts iperf server on h1 (background).
- Runs safe, short iperf client tests from h2,h3,h4,h5 to h1 (3s, 1M).
- Captures and prints results, then drops to Mininet CLI.

Usage:
  1) Start Ryu in another terminal:
       ryu-manager ryu.app.simple_switch_13
  2) Run this script:
       sudo python2 ~/topology_test.py
"""
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import time

class CustomTopo(Topo):
    def build(self):
        # Switches
        s1 = self.addSwitch('s1')   # h1,h2
        s2 = self.addSwitch('s2')   # h3,h4,h5
        s3 = self.addSwitch('s3')   # core

        # Hosts (h1 labeled victim - label only)
        h1 = self.addHost('h1', ip='10.0.0.1/24')
        h2 = self.addHost('h2', ip='10.0.0.2/24')
        h3 = self.addHost('h3', ip='10.0.0.3/24')
        h4 = self.addHost('h4', ip='10.0.0.4/24')
        h5 = self.addHost('h5', ip='10.0.0.5/24')

        # Host-to-switch links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s2)
        self.addLink(h5, s2)

        # Switch-to-core links
        self.addLink(s1, s3)
        self.addLink(s2, s3)

def run_tests():
    setLogLevel('info')
    topo = CustomTopo()
    # Make sure this port matches your running Ryu controller
    c0 = RemoteController('c0', ip='127.0.0.1', port=6653)

    net = Mininet(topo=topo, controller=c0, link=TCLink, switch=OVSSwitch, autoSetMacs=True)
    net.start()

    info("\n*** Hosts and their IPs:\n")
    for h in net.hosts:
        info("  %s: %s\n" % (h.name, h.IP()))

    info("\n*** Starting a safe iperf server on h1 (background)\n")
    h1 = net.get('h1')
    # kill any existing iperf on host, then start server
    h1.cmd('killall -9 iperf >/dev/null 2>&1 || true')
    server_out = h1.cmd('iperf -s &')
    time.sleep(0.5)

    # Small helper: run a single iperf client test from src to dst_ip with time & bw limits
    def run_iperf_client(src_host, dst_ip, duration=3, bandwidth='1M'):
        info("\n*** Running iperf: %s -> %s for %ds @ %s\n" % (src_host.name, dst_ip, duration, bandwidth))
        # Ensure no leftover iperf client
        src_host.cmd('killall -9 iperf >/dev/null 2>&1 || true')
        cmd = 'iperf -c %s -t %d -b %s' % (dst_ip, duration, bandwidth)
        out = src_host.cmd(cmd)
        return out

    # List of attacker hosts to test (safe, sequential)
    attackers = ['h2', 'h3', 'h4', 'h5']
    dst_ip = h1.IP()
    results = {}

    # Trigger small pings first so controller learns MACs (helps flows be installed)
    info("\n*** Triggering brief pings to stimulate MAC learning\n")
    for src in attackers:
        sh = net.get(src)
        ping_out = sh.cmd('ping -c 1 %s' % dst_ip)
        info(ping_out)

    time.sleep(0.5)

    # Run iperf tests sequentially, capture outputs
    for src in attackers:
        sh = net.get(src)
        out = run_iperf_client(sh, dst_ip, duration=3, bandwidth='1M')
        results[src] = out
        # brief sleep between tests
        time.sleep(0.5)

    # Print summarized results
    info("\n*** iperf test summaries:\n")
    for src, out in results.items():
        info("---- %s -> %s ----\n" % (src, dst_ip))
        # print only the last 10 lines (iperf result area)
        lines = out.strip().splitlines()
        summary = '\n'.join(lines[-10:])
        info(summary + '\n')

    info("\n*** Tests complete. Dropping to Mininet CLI for further manual checks.\n")
    CLI(net)

    # On exit from CLI, cleanup
    info("\n*** Stopping network and cleaning up\n")
    net.stop()

if __name__ == '__main__':
    run_tests()

A
A

