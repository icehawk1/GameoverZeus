#!/usr/bin/env python2.7
# coding=UTF-8
from AbstractTopology import AbstractTopology
from utils.BriteFileReader import BriteGraphAccepter
from mininet.net import Mininet
from utils.FloodlightController import FloodlightController
import time


class BriteFlatrouterTopology(AbstractTopology, BriteGraphAccepter):
    def __init__(self, mininet=Mininet(controller=FloodlightController), opts=dict()):
        """
        Initialises the LayeredTopology, so that layers can be added.
        :type mininet: Mininet
        """
        AbstractTopology.__init__(self, mininet)
        self.started = False
        self.autonomousSystems = dict()
        self.modelname = None
        self.opts = opts

    def writeHeader(self, num_nodes, num_edges, modelname):
        super(BriteFlatrouterTopology, self).writeHeader(num_nodes, num_edges, modelname)
        self.modelname = modelname

    def addNode(self, nodeid, asid, nodetype):
        super(BriteFlatrouterTopology, self).addNode(nodeid, asid, nodetype)
        assert not self.started

        self.mininet.addHost(_createBotname(nodeid), opts=self.opts)
        bot = self.mininet.getNodeByName(_createBotname(nodeid))

        if not self.autonomousSystems.has_key(asid):
            aut = _AutonomousSystem()
            aut.asid = asid
            aut.botdict = dict()
            aut.switch = self.mininet.addSwitch(_createSwitchname(asid))
            self.autonomousSystems[asid] = aut

        self.autonomousSystems[asid].botdict[nodeid] = bot
        self.mininet.addLink(bot, self.autonomousSystems[asid].switch)

    def addEdge(self, edgeid, fromNode, toNode, communicationDelay, bandwidth, fromAS, toAS, edgetype):
        super(BriteFlatrouterTopology, self).addEdge(edgeid, fromNode, toNode, communicationDelay, bandwidth,
                                                     fromAS, toAS, edgetype)
        assert not self.started

        self.mininet.addLink(_createBotname(fromNode), _createBotname(toNode))

    def writeFooter(self):
        super(BriteFlatrouterTopology, self).writeFooter()
        self._connectSwitchesToSwitches()
        self._connectASNodesToSwitches()

    def start(self):
        """Starts operation of the defined Topology. It will also start the command for each of the layers."""
        self.started = True
        self.mininet.start()
        time.sleep(5)

    def stop(self):
        self.mininet.stop()
        pass

    def _connectSwitchesToSwitches(self):
        askeys = self.autonomousSystems.keys()
        for i in range(1, len(askeys)):
            switch1 = self.autonomousSystems[askeys[i - 1]].switch
            switch2 = self.autonomousSystems[askeys[i]].switch
            self.mininet.addLink(switch1, switch2)

    def _connectASNodesToSwitches(self):
        for autsys in self.autonomousSystems.values():
            for bot in autsys.botdict.values():
                self.mininet.addLink(autsys.switch, bot)


class _AutonomousSystem(object):
    botdict = dict()
    switch = None
    asid = None

    def __len__(self):
        return len(self.botdict.values())


def _createBotname(nodeid):
    return "bot%d" % nodeid


def _createSwitchname(asid):
    return "sw%d" % asid
