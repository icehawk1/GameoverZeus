#!/usr/bin/python
# coding=UTF-8
"""This file defines a layered Topology. See class LayeredTopology for details."""

import random, time
from mininet.net import Mininet, Controller

from AbstractTopology import AbstractTopology
from utils.Floodlight import Controller
from utils.MiscUtils import createRandomDPID


class LayeredTopology(AbstractTopology):
    """This class defines a base Topology where the botnet is separated into layers. Each layer has its own external_switch and the
    switches are connected serially from the first to the last layer. Therefore all traffic from a layer n host to a
    layer n+k host has to go to all the switches for the inbetween layers.
    The Topology allows an arbitrary number of named layers with an arbitrary number of bots each.
    It will also run some command on all hosts in each layer. All hosts of one layer will run the same command but it may
     differ between layers.

    To use the class, first add a few layers and then call start(). Not the other way around."""

    def __init__(self, mininet=Mininet(controller=Controller)):
        """
        Initialises the LayeredTopology, so that layers can be added.
        :type mininet: Mininet
        """
        AbstractTopology.__init__(self, mininet)
        self.layers = dict()
        self.started = False

    def addLayer(self, layername, num_bots=0, command=None, opts={}):
        """Adds a layer to the topology.
        :param layername: The name of this layer. Used to give the mn hosts some meaningful names. Should not be long.
        :param num_bots: The number of bots in this layer.
        :param command: The command to run on each bot in this layer
        :param opts: Some additional options to give to Mininet.addHost() and Mininet.addSwitch()

        :type command: str
        :type opts: dict"""
        assert not self.started, "You can't add new layers after the network has been started"

        current_layer = _Layer(layername, num_bots, command)
        self.layers[layername] = current_layer
        print current_layer.switchname
        switch = self.mininet.addSwitch(current_layer.switchname, opts=opts, dpid=createRandomDPID())

        for i in range(num_bots):
            botname = _constructNameOfBot(current_layer.name)
            self.mininet.addHost(botname, opts=opts)
            self.mininet.addLink(botname, switch)
            self.layers[layername].botlist.append(self.mininet.getNodeByName(botname))

    def _connectSwitches(self):
        """Connects the switches in the different layers with each other, so that bots on different switches can talk to each other."""
        switchnames = [layer.switchname for layer in self.layers.values()]
        # Important: The switches should NOT be connected in a ring. Mininet doesn't like that!
        for i in range(1, len(switchnames)):
            self.mininet.addLink(switchnames[i - 1], switchnames[i])

    def start(self):
        """Starts operation of the defined Topology. It will also start the command for each of the layers."""
        self.started = True
        self._connectSwitches()

        self.mininet.start()
        for layer in self.layers.values():
            for bot in layer.botlist:
                bot.cmd("%s &" % layer.command)
        time.sleep(5)

    def stop(self):
        self.mininet.stop()


class _Layer(object):
    """Base class for value objects that each describe one _Layer in the layered topology."""

    def __init__(self, name, num_bots=0, command=None, opts={}):
        self.name = name
        self.num_bots = num_bots
        if command is not None:
            self.command = command
        else:
            self.command = "echo %s" % self.name
        self.opts = opts

        self.botlist = []
        self.switchname = _constructNameOfSwitch(name)


def _constructNameOfSwitch(layername):
    """Constructs the name of a bot from the name of the layer it is in."""
    # Please Note: Mininet (or more precisely the OS) can't cope with interface names longer than a few characters -.-
    return "sw%s" % layername[:8]


def _constructNameOfBot(layername):
    """Constructs the name of a bot from the name of the layer it is in.
    Note: This function will generate a different name each time it is run."""
    # Please Note: Mininet (or more precisely the OS) can't cope with interface names longer than a few characters -.-
    return "b%s-%s" % (random.randint(1, 999), layername[:5])
