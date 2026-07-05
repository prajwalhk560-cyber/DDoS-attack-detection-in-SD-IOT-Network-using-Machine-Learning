#!/usr/bin/env python2
"""
topology.py  (Python 2)

Creates a Mininet topology with:
 - 5 hosts: h1..h5   (h1 = "victim" by label only)
 - 3 switches: s1, s2, s3
 - Connections:
     - h1, h2 -> s1
     - h3, h4, h5 -> s2
     - s1 <-> s3
     - s2 <-> s3
 - Remote controller (intended to be a Ryu controller)
 - Starts the Mininet CLI for manual testing.
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink

class CustomTopo(Topo):
    def build(self):
        # Switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')

        # Hosts (h1 labeled 'victim' in comments only)
        h1 = self.addHost('h1', ip='10.0.0.1/24')  # victim (label only)
        h2 = self.addHost('h2', ip='10.0.0.2/24')
        h3 = self.addHost('h3', ip='10.0.0.3/24')
        h4 = self.addHost('h4', ip='10.0.0.4/24')
        h5 = self.addHost('h5', ip='10.0.0.5/24')

        # Links: hosts to switches
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s2)
        self.addLink(h5, s2)

        # Links: switches to core switch s3
        self.addLink(s1, s3)
        self.addLink(s2, s3)

def run():
    setLogLevel('info')

    topo = CustomTopo()
    # RemoteController expects a controller running separately (e.g., ryu-manager)
    c0 = RemoteController('c0', ip='127.0.0.1', port=6653)

    net = Mininet(topo=topo, controller=c0, link=TCLink, switch=OVSSwitch, autoSetMacs=True)
    net.start()

    print("\n*** Hosts and their IPs:")
    for h in net.hosts:
        print("  %s: %s" % (h.name, h.IP()))

    print("\n*** You can run tests from the Mininet CLI.")
    print("*** Example safe tests:")
    print("  mininet> pingall")
    print("  mininet> h1 iperf -s &")
    print("  mininet> h2 iperf -c 10.0.0.1 -t 3 -b 1M")
    print("  mininet> h2 ping -c 3 h1")

    CLI(net)
    net.stop()

if __name__ == '__main__':
    run()
