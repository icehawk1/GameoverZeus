#!/usr/bin/env python2.7
# coding=UTF-8
import unittest
from BriteFileReader import BriteGraphAccepter, createGraphFromBriteFile
import emu_config


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
