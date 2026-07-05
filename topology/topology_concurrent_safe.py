#!/usr/bin/env python2
# topology_concurrent_safe.py  (Python 2)
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import time

class CustomTopo(Topo):
    def build(self):
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')

        h1 = self.addHost('h1', ip='10.0.0.1/24')  # target (lab only)
        h2 = self.addHost('h2', ip='10.0.0.2/24')
        h3 = self.addHost('h3', ip='10.0.0.3/24')
        h4 = self.addHost('h4', ip='10.0.0.4/24')
        h5 = self.addHost('h5', ip='10.0.0.5/24')

        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s2)
        self.addLink(h5, s2)

        self.addLink(s1, s3)
        self.addLink(s2, s3)

def run():
    setLogLevel('info')
    topo = CustomTopo()
    c0 = RemoteController('c0', ip='127.0.0.1', port=6653)
    net = Mininet(topo=topo, controller=c0, link=TCLink, switch=OVSSwitch, autoSetMacs=True)
    net.start()

    info("\n*** Hosts:\n")
    for h in net.hosts:
        info("  %s: %s\n" % (h.name, h.IP()))

    # start iperf server on h1
    h1 = net.get('h1')
    h1.cmd('killall -9 iperf >/dev/null 2>&1 || true')
    h1.cmd('iperf -s &')
    time.sleep(0.5)

    # concurrent clients (controlled)
    clients = ['h2','h3','h4','h5']
    duration = 5
    bandwidth = '1M'   # safe, limited bw per client
    info("\n*** Starting concurrent iperf clients (duration=%ds, bw=%s each)\n" % (duration, bandwidth))

    for src in clients:
        host = net.get(src)
        cmd = 'iperf -c %s -t %d -b %s > /tmp/%s_iperf.out 2>&1 &' % (h1.IP(), duration, bandwidth, src)
        host.cmd(cmd)

    time.sleep(duration + 1)

    info("\n*** Client outputs:\n")
    for src in clients:
        out = net.get(src).cmd('tail -n 20 /tmp/%s_iperf.out' % src)
        info("--- %s -> %s ---\n%s\n" % (src, h1.IP(), out))

    info("\n*** Done. Dropping to Mininet CLI for inspection\n")
    CLI(net)
    net.stop()

if __name__ == '__main__':
    run()

