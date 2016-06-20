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

    def testCommunicationFromBotToCnCServer(self):
        cncserver = self.net.get(random.choice(self.topo.cncserverdict.keys()))
        cncserver.cmd('python -m SimpleHTTPServer 8000 &')
        proxy = self.net.get(random.choice(self.topo.proxydict.keys()))
        proxy.cmd('mitmdump -p 8000 -q --anticache -R "http://%s:8000" &' % cncserver.IP())

        time.sleep(5)

        bot = self.net.get(random.choice(self.topo.botdict.keys()))
        wgetoutput = bot.cmd("wget -O - %s:8000" % proxy.IP())
        print wgetoutput
        self.assertTrue("200 OK" in wgetoutput)
        self.assertTrue("Directory listing for /" in wgetoutput)

        cncserver.cmd("kill %python")
        proxy.cmd("kill %mitmdump")
        pass


if __name__ == '__main__':
    unittest.main()
