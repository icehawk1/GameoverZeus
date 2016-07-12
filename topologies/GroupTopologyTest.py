#!/usr/bin/env python2.7
# coding=UTF-8
import os
import time
import unittest

import emu_config
from topologies.BriteTopology import BriteTopology, createGraphFromBriteFile


class BriteTopologyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.topology = BriteTopology()
        createGraphFromBriteFile(emu_config.basedir + "/testfiles/group.brite", [cls.topology])
        cls.topology.start()

    @classmethod
    def tearDownClass(cls):
        cls.topology.stop()
        time.sleep(2)
        os.system("mn -c")

    def testHostsWithoutEdgeAreSeparated(self):
        ausys = self.topology.autonomousSystems[1]
        packetLoss = self.topology.mininet.ping([ausys.botdict[2], ausys.botdict[1]])
        self.assertEquals(100, packetLoss)

    def testHostsWithoutEdgeAreSeparated2(self):
        ausys = self.topology.autonomousSystems[1]
        packetLoss = self.topology.mininet.ping([ausys.botdict[3], ausys.botdict[4]])
        self.assertEquals(100, packetLoss)

    def testHostsWithEdgeCanConnect(self):
        ausys = self.topology.autonomousSystems[1]
        packetLoss = self.topology.mininet.ping([ausys.botdict[2], ausys.botdict[4]])
        self.assertEquals(0, packetLoss)

    def testHostsWithEdgeCanConnect2(self):
        ausys = self.topology.autonomousSystems[1]
        bot0 = ausys.botdict[0]
        bot1 = ausys.botdict[1]
        print bot0.cmd("ifconfig bot0-eth0", shell=True)
        print bot1.cmd("ifconfig bot1-eth0", shell=True)
        packetLoss = self.topology.mininet.ping([bot0, bot1])
        self.assertEquals(0, packetLoss)

    def testHostCanPingItself(self):
        ausys = self.topology.autonomousSystems[1]
        packetLoss = self.topology.mininet.ping([ausys.botdict[3], ausys.botdict[3]])
        self.assertEquals(0, packetLoss)
