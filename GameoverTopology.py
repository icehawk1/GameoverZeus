#!/usr/bin/python

from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.util import dumpNodeConnections


class SingleSwitchTopo(Topo):
    num_bots = 10
    num_proxies = 3
    num_cncservers = 2

    "Single switch connected to n hosts."

    def build(self, n=2):
        switch = self.addSwitch('switch1')

        for i in range(self.num_bots):
            bot = self.addHost("bot%s" % i)
            self.addLink(bot, switch)

        for i in range(self.num_proxies):
            proxy = self.addHost("proxy%s" % i)
            self.addLink(proxy, switch)

        for i in range(self.num_cncservers):
            cncserver = self.addHost("cnc%s" % i)
            self.addLink(cncserver, switch)


def simpleTest():
    "Create and test a simple network"
    topo = SingleSwitchTopo(n=4)
    net = Mininet(topo)
    net.start()
    print "Dumping host connections"
    dumpNodeConnections(net.hosts)
    print "Testing network connectivity"
    net.pingAll()
    net.pingPair()
    net.stop()


if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    simpleTest()
