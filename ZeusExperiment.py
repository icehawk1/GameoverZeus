#!/usr/bin/env python2
# coding=UTF-8
import logging, os, random, time

from resources.emu_config import logging_config, basedir
from Experiment import Experiment
from topologies.BriteTopology import BriteTopology, applyBriteFile
from utils.MiscUtils import pypath


class BlubExperiment(Experiment):
    def __init__(self):
        super(BlubExperiment, self).__init__()
	self.britefile = os.path.join(basedir, "resources/topdown.brite")

    def _setup(self):
        super(BlubExperiment, self)._setup()
        self.topology = BriteTopology(self.mininet)
        applyBriteFile(self.britefile, [self.topology])
	assert len(self.topology.nodes)>0
	logging.debug("Adding %d nodes from %s"%(len(self.topology.nodes), self.britefile))
        for node in self.topology.nodes:
            self.overlord.addHost(node.name)

        nodes = set(self.topology.nodes)
        assert len(nodes) >= 28
        self.setNodes("bots", set(random.sample(nodes, 25)))
        nodes -= self.getNodes("bots")
        self.setNodes("non-bots", set(random.sample(nodes, 3)))
        self.setNodes("nodes", self.topology.nodes)

    def _start(self):
        self.topology.start()
        for h in self.getNodes("nodes"):
            h.cmd(pypath + " python2 overlord/Host.py %s &"%h.name)
        time.sleep(15)

    def _executeStep(self, num):
        super(BlubExperiment, self)._executeStep(num)

    def _stop(self):
        self.overlord.stopEverything()
        self.topology.stop()


if __name__ == '__main__':
    logging.basicConfig(**logging_config)

    experiment = BlubExperiment()
    experiment.executeExperiment()
