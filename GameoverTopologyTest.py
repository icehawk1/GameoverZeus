#!/usr/bin/env python2.7
import random
import time
import unittest

from api.BotnetComponents import CnCServer, Proxy, Bot
from api.LayeredTopology import LayerDescription, LayeredTopology

class GameoverTopologyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        descs = [LayerDescription("CnC", 2), LayerDescription("Proxy", 5),
                 LayerDescription("Bot", 10)]
        cls.topology = LayeredTopology(descs)

        for name in descs[0].getNamesOfBots():
            currentbot = CnCServer(cls.topology.net.getNodeByName(name))
            currentbot.start()
            # cls.topology.layers["CnC"] = descs[0]
            cls.topology.layers["CnC"].botdict[name] = currentbot

        for name in descs[1].getNamesOfBots():
            currentbot = Proxy(cls.topology.net.getNodeByName(name),
                               random.choice(cls.topology.layers["CnC"].botdict.values()))
            currentbot.start()
            # cls.topology.layers["Proxy"] = descs[1]
            cls.topology.layers["Proxy"].botdict[name] = currentbot

        for name in descs[2].getNamesOfBots():
            currentbot = Bot(cls.topology.net.getNodeByName(name))
            currentbot.peerlist.append(random.choice(cls.topology.layers["Proxy"].botdict.values()))
            currentbot.start()
            # cls.topology.layers["Proxy"] = descs[2]
            cls.topology.layers["Bot"].botdict[name] = currentbot

        time.sleep(6)

    @classmethod
    def tearDownClass(cls):
        cls.topology.stop()

    #@unittest.skip("Takes long if it fails")
    def testPingAll(self):
        """test if pingAll succeeds without packet loss"""
        packet_loss = self.topology.net.pingAll()
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
