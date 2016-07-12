#!/usr/bin/env python2.7
# coding=UTF-8
import logging
import os
import time
import unittest

from timeout_decorator import timeout

import emu_config
from BriteTopology import BriteTopology, createGraphFromBriteFile, BriteGraphAccepter


class BriteFileReaderTest(unittest.TestCase):
    inputfilename = emu_config.basedir + "/testfiles/flatrouter.brite"

    def setUp(self):
        pass

    def testReadToMockAccepter(self):
        accepter = MockAccepter()
        createGraphFromBriteFile(self.inputfilename, [accepter])
        self.assertEquals("RTWaxman", accepter.model_name)
        self.assertEquals(3, accepter.num_nodes)
        self.assertEquals(5, accepter.num_edges)


class MockAccepter(BriteGraphAccepter):
    num_nodes = 0
    num_edges = 0
    model_name = None

    def writeHeader(self, num_nodes, num_edges, modelname):
        self.model_name = modelname

    def addNode(self, nodeid, asid, nodetype):
        print nodeid, asid, nodetype
        self.num_nodes += 1

    def addEdge(self, edgeid, fromNode, toNode, communicationDelay, bandwidth, fromAS, toAS, edgetype):
        self.num_edges += 1

    def writeFooter(self):
        pass

class BriteTopologyTest(unittest.TestCase):
    def setUp(self):
        self.topology = BriteTopology()

    @classmethod
    def tearDownClass(cls):
        os.system("mn -c")

    def testFlatRouter(self):
        createGraphFromBriteFile(emu_config.basedir + "/testfiles/flatrouter.brite", [self.topology])
        self.assertEquals(2, len(self.topology.autonomousSystems))
        self.assertEquals(2, len(self.topology.autonomousSystems[1]))
        self.assertEquals("bot1", self.topology.autonomousSystems[2].botdict[1].name)

    def testTopDown(self):
        createGraphFromBriteFile(emu_config.basedir + "/testfiles/topdown.brite", [self.topology])
        self.assertEquals(4, len(self.topology.autonomousSystems))
        self.assertEquals(5, len(self.topology.autonomousSystems[7]))
        self.assertEquals("bot157", self.topology.autonomousSystems[9].botdict[157].name)


@unittest.skip("Only one of BriteMininetFlatrouterTest and BriteMininetTopdownTest can be active at the same time."
               "Otherwise they stop working.")
class BriteMininetFlatrouterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print "flatrouter"
        cls.topology = BriteTopology()
        createGraphFromBriteFile(emu_config.basedir + "/testfiles/flatrouter.brite", [cls.topology])
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
        cls.topology = BriteTopology()
        createGraphFromBriteFile(emu_config.basedir + "/testfiles/topdown.brite", [cls.topology])
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
