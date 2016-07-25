#!/usr/bin/env python2
# coding=UTF-8
import unittest, logging, time
from mininet.net import Mininet

from utils import Floodlight, LogfileParser
from utils.MiscUtils import addHostToMininet
from overlord.Overlord import Overlord
from actors.RandomTrafficGenerator import RandomTrafficReceiver
from actors.AbstractBotTest import RunnableTest
from resources.emu_config import logging_config


class RandomTrafficGeneratorTest(RunnableTest, unittest.TestCase):
    def createObjectUnderTest(self):
        return RandomTrafficReceiver()

    def testSendReceiveTraffic(self):
        net = Mininet(controller=Floodlight.Controller)
        net.addController("controller1")
        overlord = Overlord()
        switch = net.addSwitch("switch1")
        receiver = addHostToMininet(net, switch, "receiver", overlord, bw=20)
        sender = addHostToMininet(net, switch, "sender", overlord, bw=25)

        overlord.startRunnable("RandomTrafficGenerator", "RandomTrafficReceiver", hostlist=[receiver.name])
        overlord.startRunnable("RandomTrafficGenerator", "RandomTrafficSender",
                               {"current_peerlist": [receiver.IP()], "probability": 0.8}, hostlist=[sender.name])
        logging.debug("Runnables wurden gestartet")
        time.sleep(2)

        # TODO: Verify that Traffic was sent by parsing the logfile
        logentries = LogfileParser.parseMachineReadableLogfile("RandomTrafficSender")
        print logentries
        self.assertTrue(len(logentries) > 0)

        overlord.stopEverything()
        net.stop()


if __name__ == '__main__':
    logging.basicConfig(**logging_config)
    unittest.main()
