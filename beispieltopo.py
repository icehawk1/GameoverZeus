#!/usr/bin/env python2.7
# coding=UTF-8
from mininet.topo import Topo
from mininet.net import Mininet


class SwitchedTopo(Topo):
    """Three switches with a couple of hosts each"""

    def build(self, n=2):
        switch_cnc = self.addSwitch('sw1', opts={})
        switch_proxy = self.addSwitch("sw2", opts={})
        switch_bot = self.addSwitch("sw", opts={})

        self.addLink(switch_cnc, switch_proxy)
        self.addLink(switch_proxy, switch_bot)

        for i in range(2):
            self.addHost("bot-cnc-%s" % i)
            self.addLink("bot-cnc-%s" % i, switch_cnc)
        for i in range(5):
            self.addHost("proxy-%s" % i)
            self.addLink("proxy-%s" % i, switch_proxy)
        for i in range(10):
            self.addHost("bot-bot-%s" % i)
            self.addLink("bot-bot-%s" % i, switch_bot)


mntopo = SwitchedTopo(n=2)
net = Mininet(mntopo)

net.addHost("testhost")
net.addLink("sw2", "testhost")
net.start()
net.pingAll()
net.stop()
