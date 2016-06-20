#!/usr/bin/env python2.7
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

    # @unittest.skip("go away")
    def testPingAll(self):
        """test if pingAll succeeds without packet loss"""
        packet_loss = self.net.pingAll()
        self.assertEquals(0, packet_loss)

    def testPingPair(self):
        """test if pingPair succeeds without packet loss"""
        packet_loss = self.net.pingPair()
        self.assertEquals(0, packet_loss)


if __name__ == '__main__':
    unittest.main()
