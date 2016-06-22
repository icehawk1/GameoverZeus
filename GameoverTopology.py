#!/usr/bin/python
import random
import time
from mininet.net import Mininet
from mininet.topo import Topo

from BotnetComponents import *


class GameoverTopology:
    def __init__(self, num_bots=10, num_proxies=3, num_cncservers=2):
        self.num_bots = num_bots
        self.num_proxies = num_proxies
        self.num_cncservers = num_cncservers
        self.botdict = dict()
        self.proxydict = dict()
        self.cncdict = dict()
        self.switch = None

        hostnames = ["bot%s" % i for i in range(num_bots)]
        hostnames += ["proxy%s" % i for i in range(num_proxies)]
        hostnames += ["cnc%s" % i for i in range(num_cncservers)]
        self.mntopo = InternalTopology(["switch1"], hostnames)
        self.net = Mininet(self.mntopo)

    def start(self):
        self.build()
        self.net.start()

    def stop(self):
        for component in self.cncdict.values() + self.proxydict.values() + self.botdict.values():
            component.stop()
        self.net.stop()

    def build(self):
        """A layered topology consisting of a CnC-Layer, a Proxy-Layer and a Bot-Layer"""
        # TODO: Nicht mehr die Namen der Nodes verwenden um sie anzusprechen

        for i in range(self.num_cncservers):
            name = "cnc%s" % i
            instance = CnCServer(self.net.getNodeByName(name))
            instance.start()
            self.cncdict[name] = instance

        for i in range(self.num_proxies):
            name = "proxy%s" % i
            instance = Proxy(self.net.getNodeByName(name), random.choice(self.cncdict.values()))
            instance.start()
            self.proxydict[name] = instance

        for i in range(self.num_bots):
            name = "bot%s" % i
            self.botdict[name] = Bot(self.net.getNodeByName(name))
            self.botdict[name].peerlist.append(random.choice(self.proxydict.values()))
            self.botdict[name].start()

        time.sleep(5)  # Wait until all services have been started


class InternalTopology(Topo):
    """Internal class that actually implements the Topology. Should not be used outside this file."""

    def __init__(self, switchnames, hostnames):
        self.switchnames = switchnames
        self.hostnames = hostnames
        Topo.__init__(self)

    def build(self):
        """Builds the topology"""
        # print "#Proxies: %s" %GameoverTopology.num_proxies
        for name in self.switchnames:
            self.addSwitch(name)
        for name in self.hostnames:
            self.addHost(name)
            self.addLink(name, self.switchnames[0])  # TODO: Keine direkte Referenz auf einen Switch mehr
