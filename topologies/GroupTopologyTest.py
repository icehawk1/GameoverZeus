#!/usr/bin/env python2.7
# coding=UTF-8
"""This file tests whether bots can be correctly separated via the Floodlight firewall. It uses a special BRITE file
where every node is in the same AS but not every node is connected to every other node. The expectation is that firewall
rules can be used to enforce that two nodes can ping each other iff they are connected in the BRITE file."""

import os
import time
import unittest

from resources import emu_config
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
        """Tests that two unconnected hosts can't ping each other"""
        ausys = self.topology.autonomousSystems[1]
        packetLoss = self.topology.mininet.ping([ausys.botdict[2], ausys.botdict[1]])
        self.assertEquals(100, packetLoss)

    def testHostsWithoutEdgeAreSeparated2(self):
        """Tests that two other unconnected hosts can't ping each other"""
        ausys = self.topology.autonomousSystems[1]
        packetLoss = self.topology.mininet.ping([ausys.botdict[3], ausys.botdict[4]])
        self.assertEquals(100, packetLoss)

    def testHostsWithEdgeCanConnect(self):
        """Tests that two connected hosts can ping each other"""
        ausys = self.topology.autonomousSystems[1]
        packetLoss = self.topology.mininet.ping([ausys.botdict[2], ausys.botdict[4]])
        self.assertEquals(0, packetLoss)

    def testHostsWithEdgeCanConnect2(self):
        """Tests that two other connected hosts can ping each other"""
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
