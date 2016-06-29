#!/usr/bin/env python2.7
# coding=UTF-8
from mininet.topo import Topo


class FirewallTopology(Topo):
    """This class implements a simple Topology with two nodes and one switch.
The nodes try to talk to each other on three different ports. However, the Switch acts as a Firewall and prevents it
completely on one port, allows outgoing but no incoming connections for another port and allows everything on the
third port."""

    def __init__(self):
        Topo.__init__(self)


topos = {'fwtopo': (lambda: FirewallTopology())}
