#!/usr/bin/env python2.7
# coding=UTF-8
import random, unittest, logging

from topologies.LayeredTopology import LayeredTopologyFactory
from actors.CnCServer import CnCServer
from actors.Bot import Bot

class GameoverTopologyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        factory = LayeredTopologyFactory([("CnC", 2, {}), ("Proxy", 5, {}), ("Bot", 10, {})])
        factory.buildLayer("CnC", 2, lambda nodename, net: CnCServer(name=nodename))
        factory.buildLayer("Proxy", 5,
                           lambda nodename, net: Bot(name=nodename))  # TODO: Durch richtige Proxies ersetzen
        factory.buildLayer("Bot", 10, lambda nodename, net: Bot(name=nodename))

        for bot in factory.layers["Bot"].botdict.values():
            assert isinstance(bot.peerlist, list), "type(bot.peerlist): %s" % type(bot.peerlist)
            bot.peerlist.append(random.choice(factory.layers["CnC"].botdict.values()))
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

    def testMeasureStealthyness(self):
        pass

    def testMeasureEffectiveness(self):
        pass

    def testMeasureEfficiency(self):
        pass

    def testMeasureRobustness(self):
        pass

if __name__ == '__main__':
    logging.basicConfig(format="%(threadName)s: %(message)s", level=logging.DEBUG)
    unittest.main()
