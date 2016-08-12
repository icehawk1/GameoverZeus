#!/usr/bin/env python2
# coding=UTF-8
import os, time, logging, sys, json
from datetime import datetime
sys.path.append(os.path.dirname(__file__))
from mininet.cli import CLI

from resources import emu_config
from utils.MiscUtils import mkdir_p, datetimeToEpoch
from utils.TcptraceParser import TcptraceParser
from Experiment import Experiment


class ZeusExperiment(Experiment):
    def __init__(self):
        super(ZeusExperiment, self).__init__()
        self.pcapfile = os.path.join(self.outputdir, "tcptrace/victim.pcap")
        mkdir_p(os.path.dirname(self.pcapfile))

    def _setup(self):
        super(ZeusExperiment, self)._setup()

        # Create all the hosts that make up the experimental network and assign them to groups
        self.setNodes("bots",
                      {self.addHostToMininet(self.mininet, self.switch, "host%d"%i, self.overlord, bw=25) for i in range(25)})
        self.setNodes("cncserver", {self.addHostToMininet(self.mininet, self.switch, "cnc1", self.overlord)})
        self.setNodes("victim", {self.addHostToMininet(self.mininet, self.switch, "victim1", self.overlord, bw=90)})
        self.setNodes("sensor", {self.addHostToMininet(self.mininet, self.switch, "sensor1", self.overlord)})
        self.setNodes("nodes",
                      self.getNodes("bots") | self.getNodes("cncserver") | self.getNodes("victim") | self.getNodes("sensor"))
        assert len(self.getNodes("nodes")) == len(self.getNodes("bots")) + 3, "nodes: %s"%self.getNodes("nodes")

    def _start(self):
        # Start the Mininet network
        self.startMininet(self.mininet, self.getNodes("nodes"))
        victim = next(iter(self.getNodes("victim")))  # Get one element from a set ...
        cncserver = next(iter(self.getNodes("cncserver")))

        # Start the necessary runnables
        self.overlord.startRunnable("TestWebsite", "TestWebsite", hostlist=[victim.name])
        self.overlord.startRunnable("Sensor", "Sensor", {"pagesToWatch": ["http://%s:%d/?root=1234"%(victim.IP(), emu_config.PORT)]},
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
        kwargs = json.dumps({"url": "http://%s:%d/ddos_me?composite=%d"%(victim.IP(), emu_config.PORT, 9999123456789012345678901456780L)})
        urlOfCnCServer = "http://%s:%d/current_command"%(cncserver.IP(), emu_config.PORT)
        result = cncserver.cmd("timeout 60s wget -q -O - --post-data 'command=ddos_server&timestamp=%d&kwargs=%s' '%s'"
                               %(datetimeToEpoch(datetime.now()), kwargs, urlOfCnCServer), verbose=True)
        logging.debug("wget: %s"%result)

    def _stop(self):
        victim = next(iter(self.getNodes("victim")))

        # CLI(net)
        print "tshark: ", victim.cmd("jobs")
        self.overlord.stopEverything()
        self.mininet.stop()

        ttparser = TcptraceParser()
        stats = ttparser.extractConnectionStatisticsFromPcap(os.path.dirname(self.pcapfile))


if __name__ == '__main__':
    logging.basicConfig(**emu_config.logging_config)
    experiment = ZeusExperiment()
    experiment.executeExperiment()
