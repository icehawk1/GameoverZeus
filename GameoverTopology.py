#!/usr/bin/python

import random
from mininet.log import setLogLevel
from mininet.topo import Topo


class GameoverTopology(Topo):
    num_bots = 10
    num_proxies = 3
    num_cncservers = 2

    switch = None
    botdict = dict()
    proxydict = dict()
    cncserverdict = dict()

    def build(self, n=2):
        """Single switch connected to n hosts."""
        self.switch = self.addSwitch('switch1')

        for i in range(self.num_cncservers):
            cncserver = self.addHost("cnc%s" % i)
            self.cncserverdict[cncserver] = CnCServer(cncserver)
            self.addLink(cncserver, self.switch)

        for i in range(self.num_proxies):
            proxy = self.addHost("proxy%s" % i)
            self.proxydict[proxy] = Proxy(proxy, random.choice(self.cncserverdict.keys()))
            self.addLink(proxy, self.switch)

        for i in range(self.num_bots):
            bot = self.addHost("bot%s" % i)
            self.botdict[bot] = Bot(bot, random.choice(self.proxydict.keys()))
            self.addLink(bot, self.switch)


class Bot:
    def __init__(self, name, proxy):
        """
        :type proxy: str
        """
        assert isinstance(name, str)
        assert isinstance(proxy, str)
        self.name = name
        self.proxy = proxy


class Proxy:
    def __init__(self, name, cncserver):
        assert isinstance(name, str)
        assert isinstance(cncserver, str)
        self.name = name
        self.cncserver = cncserver


class CnCServer:
    def __init__(self, name):
        assert isinstance(name, str)
        self.name = name

if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
