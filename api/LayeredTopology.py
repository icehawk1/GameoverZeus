#!/usr/bin/python
# coding=UTF-8
import collections
import logging
import random
import time
from mininet.net import Mininet
from mininet.topo import Topo

from BotnetComponents import BotnetComponent

mntopo = None
net = None

class LayeredTopology:
    def __init__(self, layers):
        """:type layers: dict of all the layers in this topology with their names as keys"""
        assert isinstance(layers, dict)
        self.layers = layers
        self.startMininet()

    def startMininet(self):
        for layer in self.layers.values():
            for bot in layer.botdict.values():
                bot.start()
        time.sleep(5)

    def stop(self):
        assert net is not None
        for layer in self.layers.values():
            for bot in layer.botdict.values():
                bot.stop()
        net.stop()

    @staticmethod
    def pingAll():
        return net.pingAll()

class LayeredTopologyFactory:
    def __init__(self, descs):
        """:type descs: A list of 2-tuples that contain the name and the number of bots in each layer. This is needed to initialise mininet."""
        self.layers = dict()
        global mntopo, net
        mntopo = InternalTopology(descs)
        net = Mininet(mntopo)
        net.start()
        logging.info("Mininet started")

    def buildLayer(self, name, numbots, instanceBuilder, **opts):
        """
        :type name: str
        :type instanceBuilder: function or lambda that takes name as an argument and returns a subclass of BotnetComponent
        :type numbots: integer
        :type opts: dict
        """
        assert isinstance(numbots, int)
        assert isinstance(name, str)
        self.layers[name] = Layer(name, numbots, opts=opts)
        botdict = dict()

        for connected_bots in mntopo.botconnections.values():
            for botname in connected_bots:
                currentbot = instanceBuilder(botname, net)
                assert isinstance(currentbot, BotnetComponent)
                botdict[botname] = currentbot

        self.layers[name].botdict = botdict
        net.getNodeByName()

    def createTopology(self):
        return LayeredTopology(self.layers)


class Layer:
    """This class describes how a layer should look like when it is build.
    It does not represent an actual layer but is used by InternalTopology.build() to build a Layer"""

    def __init__(self, name, numbots, **opts):
        """:type numbots: integer"""
        assert isinstance(numbots, int)
        assert isinstance(name, str)
        self.name = name
        self.prefix = name[0:10]
        self.numbots = numbots
        self.opts = opts
        self.botdict = dict()
        self.switch = None

    def getNameOfSwitch(self):
        assert self.switch is not None
        return self.switch.name

    def getNamesOfBots(self):
        return [bot.name for bot in self.botdict.values()]


def constructNameOfSwitch(layername):
    """Constructs the name of a bot from the name of the layer it is in"""
    # Please Note: Mininet (or more precisely the OS) can't cope with interface names longer than a few characters -.-
    return "sw%s-%s" % (random.randint(1, 1000), layername[:4])


def constructNameOfBot(layername):
    """Constructs the name of a bot from the name of the layer it is in"""
    # Please Note: Mininet (or more precisely the OS) can't cope with interface names longer than a few characters -.-
    return "b%s-%s" % (random.randint(1, 1000), layername[:5])

class InternalTopology(Topo):
    """Internal class that actually implements the Topology. Is used by Mininet for callbacks. Should not be used outside this file."""
    botconnections = dict()  # Saves which Hosts are connected to which switch

    def build(self, desclist=[]):
        """Builds the topology.
        :type desclist: Iterable collection of layer descriptions that instructs build on the layers it should build"""
        assert isinstance(desclist, collections.Iterable)

        for layer in desclist:
            assert isinstance(layer[0], str)
            assert isinstance(layer[1], int)
            assert isinstance(layer[2], dict)

        switches = []
        for layer in desclist:
            switchname = self.addSwitch(constructNameOfSwitch(layer[0]), opts=layer[2])
            switches.append(switchname)
            self.botconnections[switchname] = set()

            for i in range(layer[1]):
                botname = constructNameOfBot(layer[0])
                self.addHost(botname)
                self.addLink(botname, switchname)
                self.botconnections[switchname].add(botname)

        for i in range(1, len(switches)):
            self.addLink(switches[i - 1], switches[i])
