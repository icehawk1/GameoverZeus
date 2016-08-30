#!/usr/bin/env python2
# coding=UTF-8
"""This file defines an abstract base component of the botnet emulators architecture. Subclass the Experiment class and
define its abstract methods to implement a new botnet experiment."""

import logging, os, time, shutil, random
from datetime import datetime
from abc import ABCMeta, abstractmethod
from mininet.net import Mininet
from mininet.node import Switch

from overlord.Overlord import Overlord
from utils import Floodlight
from utils.MiscUtils import mkdir_p, pypath, createRandomDPID, datetimeToEpoch
from resources import emu_config
from topologies.BriteTopology import BriteTopology, applyBriteFile
from utils.LogfileParser import writeLogentry

class Experiment(object):
    """The Experiment class is the central component of the botnet emulators architecture.
    It is responsible for instantiating the topology and the overlord and defining the main steps of the experiment,
    as well as starting and stopping it.
    To implement an actual botnet experiment, the class defines some abstract methods that need to be overriden
    as per the Strategy pattern.

    Some of the abstract methods have default implementations that should be called using the super() operator.

    Please note that none of the methods in this class are thread-safe."""
    __metaclass__ = ABCMeta

    def __init__(self):
        self.cleanup()
        self._nodedict = dict()
        self.outputdir = "/tmp/botnetemulator"
        if os.path.exists(self.outputdir):
            shutil.rmtree(self.outputdir)
        mkdir_p(self.outputdir)
        self.tsharkCommand = "tshark -i any -F pcap -w %%s port http or port %d &"%emu_config.PORT

    def executeExperiment(self):
        """This method implements the execution strategy of all botnet experiments. It corresponds to the execute() method
        from the strategy pattern."""
        name = self.__class__.__name__  # Name of the subclass

        writeLogentry(runnable=name, message="Experiment started")

        logging.debug("Initialise %s"%name)
        self._setup()
        self.setNodes("nodes", frozenset(self.mininet.hosts))  # Category that includes all Mininet hosts
        logging.info("Starting %s"%name)
        self._start()

        doNextStep = True
        currentIteration = 0
        while doNextStep:
            logging.info("Step %d on %d "%(currentIteration, datetimeToEpoch(datetime.now())))
            doNextStep = self._executeStep(currentIteration)
            currentIteration += 1

        logging.info("Stoping %s after %d iterations"%(name, currentIteration))
        self._stop()
        logging.info("Produce output files")
        self._produceOutputFiles()

        writeLogentry(runnable=name, message="Experiment ended")

    def getNodes(self, category):
        """Get all Mininet hosts that belong to the given category."""
        if self._nodedict.has_key(category):
            return self._nodedict[category]
        else:
            logging.debug("Node category %s does not exist, but those do: %s"%(category, self._nodedict.keys()))
            return []

    def setNodes(self, category, nodes):
        """Set the Mininet hosts that will belong to the given category."""
        assert isinstance(nodes, set) or isinstance(nodes,frozenset), "nodes is a %s"%type(nodes)
        if len(nodes) > 8:
            logging.debug("Created the category %s which includes the following nodes: %s"%(category, random.sample(nodes, 8)))
        else:
            logging.debug("Created the category %s with the following nodes: %s"%(category, nodes))
        self._nodedict[category] = nodes

    @abstractmethod
    def _setup(self):
        """Initialises the experiment and creates the necessary object. Usually, this is the method were one puts the
        Mininet hosts into categories. At least the bots category is needed."""
        self.mininet, self.overlord, self.switch = self._initMininet()


    @abstractmethod
    def _start(self):
        """This starts the actual execution of the experiment. When this method has returned,
        the class should be ready for _executeStep() to be called. Usually, this method starts Mininet, the Overlord,
        the Host scripts, and all the necessary runnables."""
        pass

    @abstractmethod
    def _executeStep(self, num):
        """Executes a single step in the experiment.
        :param num: The number of steps that have executed so far. One step correspends to one call of this method.
        :return: True if this experiment is not yet finished and should be continued, False otherwise"""
        assert len(self.getNodes("bots")) > 0, "The setup() method should have set a node category (with setNodes()) called bots1"

        disinfected = set(self.overlord.desinfectRandomBots(0.3, [h.name for h in self.getNodes("bots")]))
        self.setNodes("bots", {h for h in self.getNodes("bots") if not h.name in disinfected})
        logging.debug("len(bots) == %d"%len(self.getNodes("bots")))
        time.sleep(15)
        return len(self.getNodes("bots")) > 0

    @abstractmethod
    def _stop(self):
        """Stops the execution of this experiment"""
        pass

    @abstractmethod
    def _produceOutputFiles(self):
        """Produces the files that are used to report the results of this experiment to the researcher."""
        pass

    def _initMininet(self, ctrl=Floodlight.Controller):
        """Initialise a default configuration of Mininet"""
        mininet = Mininet(controller=ctrl)
        mininet.addController("controller1")
        overlord = Overlord()
        switch = mininet.addSwitch("switch1")
        return mininet, overlord, switch

    def addHostToMininet(self, mn, switch, hostname, overlord, **linkopts):
        """Creates a new host in the mininet network that is connected to the given switch and to the overlord"""
        assert isinstance(mn, Mininet)
        assert isinstance(switch, Switch)
        assert isinstance(hostname, str)

        result = mn.addHost(hostname, dpid=createRandomDPID())
        overlord.addHost(result.name)
        link = mn.addLink(result, switch)
        link.intf1.config(**linkopts)
        link.intf2.config(**linkopts)
        return result

    def startMininet(self, mininet, nodeSet):
        """Starts the given Mininet instance and the Host scripts on the given nodes"""
        mininet.start()
        for h in nodeSet:
            h.cmd(pypath + " python2 overlord/Host.py %s &"%h.name)
        time.sleep(15)

    def cleanup(self):
        """Cleans up files and processes lingering from an earlier experiment. NOTE: This also deletes the results of the
        experiment if they were not saved."""
        logging.info("Deleting files created by previous experiment. Includes the result from that experiment.")
        os.system("fuser -kn tcp 6633")
        os.system("rm -rf /tmp/overlordsockets/ /tmp/loading_times/ /tmp/*.log /tmp/botnetemulator /tmp/pymp-*")
        os.system("mn -c")


class BriteExperiment(Experiment):
    """An experiment on the BriteTopology"""
    __metaclass__ = ABCMeta

    def __init__(self, britefile="resources/topdown.brite"):
        super(BriteExperiment, self).__init__()
        self.britefile = os.path.join(emu_config.basedir, britefile)

    @abstractmethod
    def _setup(self):
        super(BriteExperiment, self)._setup()

        self.topology = BriteTopology(self.mininet)
        applyBriteFile(self.britefile, [self.topology])
        assert len(self.topology.nodes) > 0
        logging.debug("Adding %d nodes from %s"%(len(self.topology.nodes), self.britefile))
        for node in self.topology.nodes:
            self.overlord.addHost(node.name)

    @abstractmethod
    def _start(self):
        super(BriteExperiment, self)._start()

        self.topology.start()
        for h in self.getNodes("nodes"):
            h.cmd(pypath + " python2 overlord/Host.py %s &"%h.name)
        time.sleep(15)

    def _stop(self):
        self.overlord.stopEverything()
        self.topology.stop()
