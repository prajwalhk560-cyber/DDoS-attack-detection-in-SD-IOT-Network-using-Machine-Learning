#!/usr/bin/python3

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel

class MyTopo(Topo):
    def build(self):
        # Add hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')

        # Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        # Add links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(s1, s2)
        self.addLink(h3, s2)
        self.addLink(h4, s2)

def run():
    topo = MyTopo()
    net = Mininet(topo=topo,
                  switch=OVSSwitch,
                  controller=lambda name: RemoteController(name, ip='127.0.0.1', port=6633))

    net.start()

    print("\n*** Initial Ping Test")
    net.pingAll()

    # Disable link between h1 and s1
    print("\n*** Bringing down link h1 <-> s1")
    net.configLinkStatus('h1', 's1', 'down')
    net.pingAll()

    # Re-enable link
    print("\n*** Bringing up link h1 <-> s1")
    net.configLinkStatus('h1', 's1', 'up')
    net.pingAll()

    CLI(net)  # Drop to CLI for further testing
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()

