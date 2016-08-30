#!/usr/bin/env python2
# coding=UTF-8
import logging, os, random, time, json
from datetime import datetime

from resources.emu_config import logging_config, PORT
from Experiment import BriteExperiment
from utils.MiscUtils import datetimeToEpoch, mkdir_p
from utils.TcptraceParser import TcptraceParser

class ZeusExperiment(BriteExperiment):
    def __init__(self):
        super(ZeusExperiment, self).__init__()
        self.pcapfile = os.path.join(self.outputdir, "tcptrace/victim.pcap")
        mkdir_p(os.path.dirname(self.pcapfile))

    def _setup(self):
        """Creates all the hosts that make up the experimental network and assign them to groups"""
        super(ZeusExperiment, self)._setup()

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

    def _start(self):
        super(ZeusExperiment, self)._start()
        pingresult = self.mininet.pingPair()
        logging.debug("pingpair: %s"%pingresult)

#	pingresult = self.mininet.pingPair()
#        logging.debug("pingpair: %s"%pingresult)

        assert len(self.getNodes("victim")) == 1
        assert len(self.getNodes("cncserver")) == 1
        victim = next(iter(self.getNodes("victim")))  # Get a sets only element ...
        cncserver = next(iter(self.getNodes("cncserver")))
        logging.debug("IP of Victim: %s; IP of CnC server: %s"%(victim.IP(), cncserver.IP()))

        # Start the necessary runnables
        self.overlord.startRunnable("Victim", "Victim", hostlist=[victim.name])
        self.overlord.startRunnable("Sensor", "Sensor",
                                    {"pagesToWatch": ["http://%s:%d/?root=1234"%(victim.IP(), PORT)]},
                                    hostlist=[h.name for h in self.getNodes("sensor")])
        self.overlord.startRunnable("zeus.CnCServer", "CnCServer", {"host": cncserver.IP()},
                                    hostlist=[h.name for h in self.getNodes("cncserver")])
        for h in self.getNodes("bots"):
            self.overlord.startRunnable("zeus.Bot", "Bot", hostlist=[h.name],
                                        kwargs={"name": h.name, "peerlist": [cncserver.IP()], "pauseBetweenDuties": 1})

        victim.cmd(self.tsharkCommand%self.pcapfile)
        logging.debug("Runnables wurden gestartet")
        time.sleep(35)

        # Initiate DDoS attack
        kwargs = json.dumps(
            {"url": "http://%s:%d/ddos_me?composite=%d"%(victim.IP(), PORT, 9999123456789012345678901456780L),
	     "timeout":10})
        urlOfCnCServer = "http://%s:%d/current_command"%(cncserver.IP(), PORT)
        result = cncserver.cmd("timeout 60s wget -q -O - --post-data 'command=ddos_server&timestamp=%d&kwargs=%s' '%s'"
                               %(datetimeToEpoch(datetime.now()), kwargs, urlOfCnCServer), verbose=True)
        assert result.strip() == "OK", "Could not send the DDoS-command to the CnC server: %s"%result

    def _executeStep(self, num):
        return super(ZeusExperiment, self)._executeStep(num)

    def _produceOutputFiles(self):
        ttparser = TcptraceParser()
        stats = ttparser.plotConnectionStatisticsFromPcap(self.pcapfile)

if __name__ == '__main__':
    logging.basicConfig(**logging_config)
    # filename='/tmp/botnetemulator.log', filemode="w"

    experiment = ZeusExperiment()
    experiment.executeExperiment()
