#!/usr/bin/env python2
# coding=UTF-8
import logging, os, time
from abc import ABCMeta, abstractmethod

from resources.emu_config import logging_config
from Experiment import Experiment
from resources import emu_config
from topologies.BriteTopology import BriteTopology, applyBriteFile
from utils.MiscUtils import pypath


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


class BlubExperiment(BriteExperiment):
    def __init__(self):
        super(BlubExperiment, self).__init__()

    def _setup(self):
        super(BlubExperiment, self)._setup()

    def _start(self):
        super(BlubExperiment, self)._start()

        pingresult = self.mininet.pingPair()
        logging.debug("pingpair: %s"%pingresult)

    def _executeStep(self, num):
        return False

    def _stop(self):
        super(BlubExperiment, self)._stop()
        pass

    def _produceOutputFiles(self):
        pass


if __name__ == '__main__':
    logging.basicConfig(**logging_config)

    experiment = BlubExperiment()
    experiment.executeExperiment()