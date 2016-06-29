#!/usr/bin/env python2.7
# coding=UTF-8
from mininet.topo import Topo

ports = [10001, 10002, 10003]

class FirewallTopology(Topo):
    """This class implements a simple Topology with two nodes and one switch.
The nodes try to talk to each other on three different ports. However, the Switch acts as a Firewall and prevents it
completely on one port, allows outgoing but no incoming connections for another port and allows everything on the
third port."""
    switch = None
    insideHost = None
    outsideHost = None

    def build(self):
        switch = self.addSwitch("switch1")
        insideHost = self.addHost('inside2')
        outsideHost = self.addHost('outside3')

        self.addLink(switch, insideHost)
        self.addLink(switch, outsideHost)

topos = {'fwtopo': (lambda: FirewallTopology())}
