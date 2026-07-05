#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
topology_with_xterms.py

Creates a 5-host, 3-switch topology and opens xterms for each host.

Topology layout:
    h1, h2 -- s1
    h3, h4, h5 -- s2
    s1 -- s3 -- s2
Controller: Remote (default 127.0.0.1:6653)

Run:
    xhost +SI:localuser:root
    ryu-manager ryu.app.simple_switch_13 &
    sudo mn -c
    sudo python2 topology_with_xterms.py
"""

from mininet.net import Mininet
from mininet.node import RemoteController, Controller, OVSSwitch
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.term import makeTerm
import time, sys

def build_topology(use_remote_controller=True, ctrl_ip='127.0.0.1', ctrl_port=6653):
    info('*** Building topology\n')

    if use_remote_controller:
        net = Mininet(controller=RemoteController, link=TCLink, switch=OVSSwitch)
        net.addController('c0', controller=RemoteController, ip=ctrl_ip, port=ctrl_port)
    else:
        net = Mininet(controller=Controller, link=TCLink, switch=OVSSwitch)
        net.addController('c0')

    # Switches
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')

    # Hosts
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    h3 = net.addHost('h3', ip='10.0.0.3/24')
    h4 = net.addHost('h4', ip='10.0.0.4/24')
    h5 = net.addHost('h5', ip='10.0.0.5/24')

    # Links
    net.addLink(h1, s1)
    net.addLink(h2, s1)

    net.addLink(h3, s2)
    net.addLink(h4, s2)
    net.addLink(h5, s2)

    net.addLink(s1, s3)
    net.addLink(s2, s3)

    info('*** Topology built successfully\n')
    return net


def main():
    setLogLevel('info')
    info('*** Creating and starting network\n')

    net = build_topology(use_remote_controller=True, ctrl_ip='127.0.0.1', ctrl_port=6653)

    try:
        net.start()
    except Exception as e:
        print >> sys.stderr, "ERROR starting network:", e
        net.stop()
        sys.exit(1)

    info('*** Network started successfully\n')
    time.sleep(1)

    # Open xterms for each host
    hosts = ['h1', 'h2', 'h3', 'h4', 'h5']
    info('*** Opening xterms for all hosts\n')

    for name in hosts:
        h = net.get(name)
        makeTerm(h, title=name, cmd="bash")
        time.sleep(0.3)

    info('*** All xterms opened. You can ping or run commands between hosts.\n')
    CLI(net)

    info('*** Stopping network\n')
    net.stop()


if __name__ == '__main__':
    main()

