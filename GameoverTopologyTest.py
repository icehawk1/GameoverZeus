#!/usr/bin/env python2.7
# coding=UTF-8
import random
import unittest

from api.BotnetComponents import CnCServer, Proxy, Bot
from api.LayeredTopology import LayeredTopologyFactory


class GameoverTopologyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        factory = LayeredTopologyFactory([("CnC", 2, {}), ("Proxy", 5, {}), ("Bot", 10, {})])
        factory.buildLayer("CnC", 2, lambda nodename, net: CnCServer(net.getNodeByName(nodename)))
        factory.buildLayer("Proxy", 5, lambda nodename, net: Proxy(net.getNodeByName(nodename)))
        factory.buildLayer("Bot", 10, lambda nodename, net: Bot(net.getNodeByName(nodename)))

        for bot in factory.layers["Bot"].botdict.values():
            bot.peerlist.append(random.choice(factory.layers["Proxy"].botdict.values()))
        for proxy in factory.layers["Proxy"].botdict.values():
            proxy.peerlist.append(random.choice(factory.layers["CnC"].botdict.values()))

        cls.topology = factory.createTopology()

    @classmethod
    def tearDownClass(cls):
        cls.topology.stop()

    #@unittest.skip("Takes long if it fails")
    def testPingAll(self):
        """test if pingAll succeeds without packet loss"""
        packet_loss = self.topology.pingAll()
        self.assertEquals(0, packet_loss)

    def testCommunicationFromBotToCnCServer(self):
        bot = random.choice(self.topology.layers["Bot"].botdict.values())
        proxy = random.choice(bot.peerlist)
        print proxy, proxy.hostinstance.IP()
        wgetoutput = bot.hostinstance.cmd("wget -O - %s:8000" % proxy.hostinstance.IP())
        print "wgetoutput: " + wgetoutput
        self.assertTrue("200 OK" in wgetoutput)
        self.assertTrue("Directory listing for /" in wgetoutput)


if __name__ == '__main__':
    unittest.main()
