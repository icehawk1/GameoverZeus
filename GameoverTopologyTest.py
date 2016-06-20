#!/usr/bin/env python2.7
import time
import unittest
from mininet.net import Mininet

from GameoverTopology import *


class GameoverTopologyTest(unittest.TestCase):
    topo = GameoverTopology()
    net = Mininet(topo)

    @classmethod
    def setUpClass(cls):
        cls.net.start()

    @classmethod
    def tearDownClass(cls):
        cls.net.stop()

    def testPingAll(self):
        """test if pingAll succeeds without packet loss"""
        packet_loss = self.net.pingAll()
        self.assertEquals(0, packet_loss)

    @unittest.skip("takes a long time")
    def testPingPair(self):
        """test if pingPair succeeds without packet loss"""
        packet_loss = self.net.pingPair()
        self.assertEquals(0, packet_loss)

    def testConnectToHttpServer(self):
        cncserver = self.net.get(random.choice(self.topo.cncserverdict.keys()))
        cncserver.cmd('python -m SimpleHTTPServer 8000 &')
        time.sleep(5)

        bot = self.net.get(random.choice(self.topo.botdict.keys()))
        wgetoutput = bot.cmd("wget -O - %s:8000" % cncserver.IP())
        print wgetoutput
        self.assertTrue("200 OK" in wgetoutput)
        self.assertTrue("Directory listing for /" in wgetoutput)

        cncserver.cmd("kill %python")

    def testCommunicationFromBotToCnCServer(self):
        pass


if __name__ == '__main__':
    unittest.main()
