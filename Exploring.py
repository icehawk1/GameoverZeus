#!/usr/bin/env python2.7
import collections, random
from mininet.net import Mininet
from mininet.topo import Topo
from api.LayeredTopology import Layer


class SingleSwitchTopo(Topo):
    """Single switch connected to n hosts."""

    def build(self, n=2):
        switch_cnc = self.addSwitch('sw1', opts={})
        switch_proxy = self.addSwitch("sw2", opts={})
        switch_bot = self.addSwitch("sw", opts={})

        self.addLink(switch_cnc, switch_proxy)
        self.addLink(switch_proxy, switch_bot)

        for i in range(2):
            self.addHost("bot-cnc-%s" % i)
            self.addLink("bot-cnc-%s" % i, switch_cnc)
        print "1"
        for i in range(5):
            self.addHost("proxy-%s" % i)
            self.addLink("proxy-%s" % i, switch_proxy)
        print 2
        for i in range(10):
            self.addHost("bot-bot-%s" % i)
            self.addLink("bot-bot-%s" % i, switch_bot)
        print 3


class InternalTopology(Topo):
    """Internal class that actually implements the Topology. Is used by Mininet for callbacks. Should not be used outside this file."""

    def build(self, desclist=[]):
        """
        Inserts the necessary Mininet-hosts. This is a callback mandated by the Mininet-API.
        :type desclist: Iterable collection of layer descriptions that instructs build on the layers it should build
        """
        assert isinstance(desclist, collections.Iterable)

        for layer in desclist:
            assert isinstance(layer.opts, dict)
            if layer.opts is not None:
                switch = layer.getNameOfSwitch()
                print switch
                self.addSwitch(switch, opts=layer.opts)
            else:
                self.addSwitch(layer.getNameOfSwitch())

        for i in range(1, len(desclist)):
            self.addLink(desclist[i - 1].getNameOfSwitch(), desclist[i].getNameOfSwitch())

        for layer in desclist:
            for botname in layer.getNamesOfBots():
                self.addHost(botname)
                self.addLink(botname, layer.getNameOfSwitch())


descs = [Layer("CnC", 2), Layer("Proxy", 5), Layer("Bot", 10)]
# mntopo = InternalTopology(descs)
mntopo = SingleSwitchTopo(n=2)
net = Mininet(mntopo)

net.addHost("testhost")
net.addLink("sw2", "testhost")
net.start()
net.pingAll()
net.stop()
