#!/usr/bin/env python2.7
import unittest

from GameoverTopology import *


class GameoverTopologyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.topology = GameoverTopology()
        cls.topology.start()

    @classmethod
    def tearDownClass(cls):
        cls.topology.stop()

    def testPingAll(self):
        """test if pingAll succeeds without packet loss"""
        packet_loss = self.topology.net.pingAll()
        self.assertEquals(0, packet_loss)

    def testCommunicationFromBotToCnCServer(self):
        bot = random.choice(self.topology.botdict.values())
        proxy = random.choice(bot.peerlist)
        wgetoutput = bot.hostinstance.cmd("wget -O - %s:8000" % proxy.hostinstance.IP())
        print wgetoutput
        self.assertTrue("200 OK" in wgetoutput)
        self.assertTrue("Directory listing for /" in wgetoutput)


if __name__ == '__main__':
    unittest.main()
