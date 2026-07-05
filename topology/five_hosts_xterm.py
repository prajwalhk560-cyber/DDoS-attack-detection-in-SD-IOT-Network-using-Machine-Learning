#!/usr/bin/env python2
"""
five_hosts_xterm.py
Creates a topology with 5 hosts, 3 switches, and 1 controller.
Automatically opens xterms for all hosts.
"""

from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from subprocess import Popen

def topology():
    net = Mininet(controller=Controller, link=TCLink, switch=OVSSwitch)

    info('*** Adding Controller\n')
    c0 = net.addController('c0')

    info('*** Adding Switches\n')
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')

    info('*** Adding Hosts\n')
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    h3 = net.addHost('h3', ip='10.0.0.3/24')
    h4 = net.addHost('h4', ip='10.0.0.4/24')
    h5 = net.addHost('h5', ip='10.0.0.5/24')

    info('*** Creating Links\n')
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s2)
    net.addLink(h4, s2)
    net.addLink(h5, s2)
    net.addLink(s1, s3)
    net.addLink(s2, s3)

    info('*** Starting Network\n')
    net.start()

    info('*** Opening xterms for all hosts\n')
    hosts = [h1, h2, h3, h4, h5]
    for h in hosts:
        Popen(['xterm', '-hold', '-e', 'bash'], preexec_fn=lambda: h.cmd('bash'))

    info('*** Network is ready\n')
    CLI(net)

    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology()

