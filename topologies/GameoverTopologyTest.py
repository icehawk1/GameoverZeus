#!/usr/bin/env python2.7
# coding=UTF-8
"""This file tests a topology where 6 Bots talk to 2 CnC servers via a number of Proxies. The names are resolved via
one nameserver."""

import logging
import os
import random
import time
import unittest

from timeout_decorator import timeout

from LayeredTopology import LayeredTopology
from resources import emu_config


class GameoverTopologyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.zeustopo = LayeredTopology()
        cls.zeustopo.addLayer("CnC", 2, emu_config.basedir + "/actors/CnCServer.py")
        cls.zeustopo.addLayer("Bot", 6, emu_config.basedir + "/actors/Bot.py")
        cls.zeustopo.addLayer("DNS", 1, emu_config.basedir + "/actors/nameserver.py")
        cls.zeustopo.start()

    @classmethod
    def tearDownClass(cls):
        cls.zeustopo.stop()
        time.sleep(2)
        os.system("mn -c")

    @timeout(10)
    def testPingAll(self):
        """test if pingAll succeeds without packet loss"""

        packet_loss = self.zeustopo.mininet.pingAll()
        self.assertEquals(0, packet_loss)

    def testCommunicationFromBotToCnCServer(self):
        bot = random.choice(self.zeustopo.layers["Bot"].botlist)
        cncserver = random.choice(self.zeustopo.layers["CnC"].botlist)

        wgetoutput = bot.cmd("wget -O - %s:8080" % cncserver.IP())
        self.assertTrue("200 OK" in wgetoutput, "wget: %s" % wgetoutput)
        self.assertTrue("I am a CnC server" in wgetoutput, "wget: %s" % wgetoutput)

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
