#!/usr/bin/env python2
# coding=UTF-8
import logging, os, time, shutil, random
from datetime import datetime
from abc import ABCMeta, abstractmethod
from mininet.net import Mininet
from mininet.node import Switch

from overlord.Overlord import Overlord
from utils import Floodlight
from utils.MiscUtils import mkdir_p, pypath, createRandomDPID, datetimeToEpoch
from resources import emu_config

class Experiment(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.cleanup()
        self._nodedict = dict()
        self.outputdir = "/tmp/botnetemulator"
        if os.path.exists(self.outputdir):
            shutil.rmtree(self.outputdir)
        mkdir_p(self.outputdir)
        self.tsharkCommand = "tshark -i any -F pcap -w %s port http or port " + str(emu_config.PORT) + " &"

    def executeExperiment(self):
        name = self.__class__.__name__

        logging.debug("Initialise experiment %s"%name)
        self._setup()
        logging.info("Starting experiment %s"%name)
        self._start()

        doNextStep = True
        currentIteration = 0
        while doNextStep:
            logging.info("Step %d on %d "%(currentIteration, datetimeToEpoch(datetime.now())))
            doNextStep = self._executeStep(currentIteration)
            currentIteration += 1

        logging.info("Stoping experiment %s after %d iterations"%(name, currentIteration))
        self._stop()

    def getNodes(self, category):
        if self._nodedict.has_key(category):
            return self._nodedict[category]
        else:
            logging.debug("Node category %s does not exist, but those do: %s"%(category, self._nodedict.keys()))
            return []

    def setNodes(self, category, nodes):
        assert isinstance(nodes, set) or isinstance(nodes,frozenset), "nodes is a %s"%type(nodes)
        if len(nodes) > 8:
            logging.debug("Created the category %s which includes the following nodes: %s"%(category, random.sample(nodes, 8)))
        else:
            logging.debug("Created the category %s with the following nodes: %s"%(category, nodes))
        self._nodedict[category] = nodes

    @abstractmethod
    def _setup(self):
        self.mininet, self.overlord, self.switch = self.initMininet()


    @abstractmethod
    def _start(self):
        pass

    @abstractmethod
    def _executeStep(self, num):
        assert len(self.getNodes("bots")) > 0, "The key bots must be set"

        disinfected = set(self.overlord.desinfectRandomBots(0.3, [h.name for h in self.getNodes("bots")]))
        bots = {h for h in self.getNodes("bots") if not h.name in disinfected}
        self.setNodes("bots", bots)
        time.sleep(15)
        logging.debug("len(bots) == %d"%len(self.getNodes("bots")))
        return len(self.getNodes("bots")) > 0

    @abstractmethod
    def _stop(self):
        pass

    def initMininet(self, ctrl=Floodlight.Controller):
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
        mininet.start()
        for h in nodeSet:
            h.cmd(pypath + " python2 overlord/Host.py %s &"%h.name)
        time.sleep(15)

    def cleanup(self):
        os.system("fuser -kn tcp 6633")
        os.system("rm -rf /tmp/overlordsockets/ /tmp/loading_times/ /tmp/*.log /tmp/botnetemulator /tmp/pymp-*")
