#!/usr/bin/python

from mininet.log import setLogLevel
from mininet.topo import Topo


class GameoverTopology(Topo):
    num_bots = 10
    num_proxies = 3
    num_cncservers = 2

    switch = None
    botlist = list()
    proxylist = list()
    cncserverlist = list()

    def build(self, n=2):
        """Single switch connected to n hosts."""
        self.switch = self.addSwitch('switch1')

        for i in range(self.num_bots):
            bot = self.addHost("bot%s" % i)
            self.botlist += bot
            self.addLink(bot, self.switch)

        for i in range(self.num_proxies):
            proxy = self.addHost("proxy%s" % i)
            self.proxylist += proxy
            self.addLink(proxy, self.switch)

        for i in range(self.num_cncservers):
            cncserver = self.addHost("cnc%s" % i)
            self.cncserverlist += cncserver
            self.addLink(cncserver, self.switch)


if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
