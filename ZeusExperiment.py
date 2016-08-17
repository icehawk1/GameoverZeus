#!/usr/bin/env python2
# coding=UTF-8
import logging, os, random, time, json
from datetime import datetime

from resources.emu_config import logging_config, PORT, basedir
from Experiment import Experiment
from topologies.BriteTopology import BriteTopology, applyBriteFile
from utils.MiscUtils import pypath, datetimeToEpoch, mkdir_p


class ZeusExperiment(Experiment):
    def __init__(self):
        super(ZeusExperiment, self).__init__()
        self.britefile = os.path.join(basedir, "resources/topdown.brite")
        self.pcapfile = os.path.join(self.outputdir, "tcptrace/victim.pcap")
        mkdir_p(os.path.dirname(self.pcapfile))

    def _setup(self):
        super(ZeusExperiment, self)._setup()
        self.topology = BriteTopology(self.mininet)
        applyBriteFile(self.britefile, [self.topology])
        assert len(self.topology.nodes) > 0
        logging.debug("Adding %d nodes from %s"%(len(self.topology.nodes), self.britefile))
        for node in self.topology.nodes:
            self.overlord.addHost(node.name)

        nodes = set(self.topology.nodes)
        assert len(nodes) >= 28
        # Create all the hosts that make up the experimental network and assign them to groups
        self.setNodes("bots", set(random.sample(nodes, 25)))
        nodes -= self.getNodes("bots")
        self.setNodes("cncserver", set(random.sample(nodes, 1)))
        nodes -= self.getNodes("cncserver")
        self.setNodes("victim", set(random.sample(nodes, 1)))
        nodes -= self.getNodes("victim")
        self.setNodes("sensor", set(random.sample(nodes, 1)))
        self.setNodes("nodes",
                      self.getNodes("bots") | self.getNodes("cncserver") | self.getNodes("victim") | self.getNodes("sensor"))

        assert len(self.getNodes("nodes")) == len(self.getNodes("bots")) + 3, "nodes: %s"%self.getNodes("nodes")

    def _start(self):
        self.topology.start()
        for h in self.getNodes("nodes"):
            h.cmd(pypath + " python2 overlord/Host.py %s &"%h.name)
        time.sleep(15)

        victim = next(iter(self.getNodes("victim")))  # Get one element from a set ...
        cncserver = next(iter(self.getNodes("cncserver")))

        # Start the necessary runnables
        self.overlord.startRunnable("TestWebsite", "TestWebsite", hostlist=[victim.name])
        self.overlord.startRunnable("Sensor", "Sensor",
                                    {"pagesToWatch": ["http://%s:%d/?root=1234"%(victim.IP(), PORT)]},
                                    hostlist=[h.name for h in self.getNodes("sensor")])
        self.overlord.startRunnable("zeus.CnCServer", "CnCServer", {"host": "10.0.0.6"},
                                    hostlist=[h.name for h in self.getNodes("cncserver")])
        for h in self.getNodes("bots"):
            self.overlord.startRunnable("zeus.Bot", "Bot", hostlist=[h.name],
                                        kwargs={"name": h.name, "peerlist": [cncserver.IP()], "pauseBetweenDuties": 1})

        victim.cmd("tshark -i any -F pcap -w %s port http or port https &"%self.pcapfile)
        logging.debug("Runnables wurden gestartet")
        time.sleep(25)

        # Initiate DDoS attack
        kwargs = json.dumps(
            {"url": "http://%s:%d/ddos_me?composite=%d"%(victim.IP(), PORT, 9999123456789012345678901456780L)})
        urlOfCnCServer = "http://%s:%d/current_command"%(cncserver.IP(), PORT)
        result = cncserver.cmd("timeout 60s wget -q -O - --post-data 'command=ddos_server&timestamp=%d&kwargs=%s' '%s'"
                               %(datetimeToEpoch(datetime.now()), kwargs, urlOfCnCServer), verbose=True)
        logging.debug("wget: %s"%result)

    def _executeStep(self, num):
        super(ZeusExperiment, self)._executeStep(num)

    def _stop(self):
        self.overlord.stopEverything()
        self.topology.stop()


if __name__ == '__main__':
    logging.basicConfig(**logging_config)

    experiment = ZeusExperiment()
    experiment.executeExperiment()
