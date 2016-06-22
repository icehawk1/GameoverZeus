#!/usr/bin/python
import collections
from mininet.net import Mininet
from mininet.topo import Topo


class LayeredTopology:
    def __init__(self, layerdescriptions):
        """:type layerdescriptions: Collection of LayerDescription"""
        assert isinstance(layerdescriptions, collections.Iterable)
        self.layers = dict()
        (self.mntopo, self.net) = self.startMininet(layerdescriptions)
        for desc in layerdescriptions:
            self.layers[desc.name] = desc

    @staticmethod
    def startMininet(layerdescriptions):
        mntopo = InternalTopology(layerdescriptions)
        net = Mininet(mntopo)
        net.start()
        return mntopo, net

    def stop(self):
        for layer in self.layers.values():
            for bot in layer.botdict.values():
                bot.stop()
        self.net.stop()


class LayerDescription:
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

    def getNameOfSwitch(self):
        return "sw-%s" % self.name

    def getNamesOfBots(self):
        return ["bot%s-%s" % (i, self.name) for i in range(self.numbots)]


class Layer(LayerDescription):
    def __init__(self, name, numbots, **opts):
        LayerDescription.__init__(self, name, numbots, opts=opts)
        self.botdict = dict()


class InternalTopology(Topo):
    """Internal class that actually implements the Topology. Is used by Mininet for callbacks. Should not be used outside this file."""

    def __init__(self, desclist):
        """:type desclist: Iterable collection of layer descriptions that instructs build on the layers it should build"""
        assert isinstance(desclist, collections.Iterable)
        self.desclist = desclist
        Topo.__init__(self)

    def build(self):
        """Builds the topology"""
        for layer in self.desclist:
            assert isinstance(layer.opts, dict)
            if layer.opts is not None:
                self.addSwitch(layer.getNameOfSwitch(), opts=layer.opts)
            else:
                self.addSwitch(layer.getNameOfSwitch())

        for i in range(1, len(self.desclist)):
            self.addLink(self.desclist[i - 1].getNameOfSwitch(), self.desclist[i].getNameOfSwitch())

        for layer in self.desclist:
            for botname in layer.getNamesOfBots():
                self.addHost(botname)
                self.addLink(botname, layer.getNameOfSwitch())
