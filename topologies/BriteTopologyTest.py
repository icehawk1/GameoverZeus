#!/usr/bin/env python2.7
# coding=UTF-8
from BriteFlatrouterTopology import BriteFlatrouterTopology
from utils.BriteFileReader import createGraphFromBriteFile
import os, unittest, time, logging
from emu_config import basedir
from timeout_decorator import timeout


class BriteTopologyTest(unittest.TestCase):
    def setUp(self):
        self.topology = BriteFlatrouterTopology()

    @classmethod
    def tearDownClass(cls):
        os.system("mn -c")

    def testFlatRouter(self):
        createGraphFromBriteFile(basedir + "/testfiles/flatrouter.brite", [self.topology])
        self.assertEquals(2, len(self.topology.autonomousSystems))
        self.assertEquals(2, len(self.topology.autonomousSystems[1]))
        self.assertEquals("bot1", self.topology.autonomousSystems[2].botdict[1].name)

    def testTopDown(self):
        createGraphFromBriteFile(basedir + "/testfiles/topdown.brite", [self.topology])
        self.assertEquals(4, len(self.topology.autonomousSystems))
        self.assertEquals(5, len(self.topology.autonomousSystems[7]))
        self.assertEquals("bot157", self.topology.autonomousSystems[9].botdict[157].name)


@unittest.skip("Only one of BriteMininetFlatrouterTest and BriteMininetTopdownTest can be active at the same time."
               "Otherwise they stop working.")
class BriteMininetFlatrouterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print "flatrouter"
        cls.topology = BriteFlatrouterTopology()
        createGraphFromBriteFile(basedir + "/testfiles/flatrouter.brite", [cls.topology])
        cls.topology.start()

    @classmethod
    def tearDownClass(cls):
        cls.topology.stop()
        time.sleep(2)
        os.system("mn -c")

    @timeout(10)
    def testPingAll(self):
        """test if pingAll succeeds without packet loss"""
        packet_loss = self.topology.mininet.pingAll()
        self.assertEquals(0, packet_loss)


class BriteMininetTopdownTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print "topdown"
        cls.topology = BriteFlatrouterTopology()
        createGraphFromBriteFile(basedir + "/testfiles/topdown.brite", [cls.topology])
        cls.topology.start()

    @classmethod
    def tearDownClass(cls):
        cls.topology.stop()
        time.sleep(2)
        os.system("mn -c")

    @timeout(10)
    def testPingAll(self):
        """test if pingAll succeeds without packet loss"""
        packet_loss = self.topology.mininet.pingAll()
        self.assertEquals(0, packet_loss)


if __name__ == '__main__':
    logging.basicConfig(format="%(threadName)s: %(message)s", level=logging.DEBUG)
    unittest.main()
