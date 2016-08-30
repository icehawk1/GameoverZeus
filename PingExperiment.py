#!/usr/bin/env python2
# coding=UTF-8
import os, time, logging, sys, json, random
from datetime import datetime

from resources.emu_config import logging_config, PORT
from utils.TcptraceParser import TcptraceParser
from Experiment import BriteExperiment
from utils.MiscUtils import mkdir_p, datetimeToEpoch


class PingExperiment(BriteExperiment):
    def __init__(self):
        super(PingExperiment, self).__init__()
        self.pcapfile = os.path.join(self.outputdir, "tcptrace/victim.pcap")
        mkdir_p(os.path.dirname(self.pcapfile))

    def _setup(self):
        super(PingExperiment, self)._setup()

        nodes = set(self.topology.nodes)
        assert len(nodes) >= 28
        self.setNodes("servents", set(random.sample(nodes, 10)))
        nodes -= self.getNodes("servents")
        self.setNodes("clients", set(random.sample(nodes, 15)))
        nodes -= self.getNodes("clients")
        self.setNodes("victim", set(random.sample(nodes, 1)))
        nodes -= self.getNodes("victim")
        self.setNodes("sensor", set(random.sample(nodes, 1)))
        self.setNodes("bots", self.getNodes("servents") | self.getNodes("clients"))

    def _start(self):
        super(PingExperiment, self)._start()

        pingresult = self.mininet.pingPair()
        logging.debug("pingpair: %s"%pingresult)

        assert len(self.getNodes("victim")) >= 1
        # Get a random element from a set. random.choice() does not work here.
        victim = random.sample(self.getNodes("victim"), 1)[0]
        logging.debug("IP of Victim: %s"%(victim.IP()))
        # Start the necessary runnables
        self.overlord.startRunnable("Victim", "Victim", hostlist=[h.name for h in self.getNodes("victim")])
        self.overlord.startRunnable("Sensor", "Sensor", {"pagesToWatch": ["http://%s:%d/?root=1234"%(victim.IP(), PORT)]},
                                    hostlist=[h.name for h in self.getNodes("sensor")])
        for h in self.getNodes("servents"):
            peerlist = random.sample([peer.IP() for peer in self.getNodes("servents") if not peer == h], 3)
            self.overlord.startRunnable("ping.Servent", "Servent", {"peerlist": peerlist, "pauseBetweenDuties": 5},
                                        hostlist=[h.name])
        for h in self.getNodes("clients"):
            peerlist = random.sample([peer.IP() for peer in self.getNodes("servents") if not peer == h], 3)
            self.overlord.startRunnable("ping.Client", "Client", {"peerlist": peerlist, "pauseBetweenDuties": 5},
                                        hostlist=[h.name])

        victim.cmd(self.tsharkCommand%self.pcapfile)
        logging.debug("Runnables wurden gestartet")
        time.sleep(35)

        chosenOne = random.sample(self.getNodes("servents"), 1)[0]
        kwargsStr = json.dumps({"url": "http://%s:%d/ddos_me"%(victim.IP(), PORT)})
        curlcmd = "timeout 60s wget -q -O - --post-data 'command=ddos_server&kwargs=%s&timestamp=%d' '%s'"%(
            kwargsStr, datetimeToEpoch(datetime.now()), "http://%s:%d/current_command"%(chosenOne.IP(), PORT))
        result = chosenOne.cmd(curlcmd, verbose=True)
        assert result.strip() == "OK", "Could not send the DDoS-command to the bot %s: |%s|"%(chosenOne, result)


    def _executeStep(self, num):
        result = super(PingExperiment, self)._executeStep(num)
        return result

    def _stop(self):
        print "jobs servent: ", random.sample(self.getNodes("servents"), 1)[0].cmd("jobs")
        print "jobs victim: ", random.sample(self.getNodes("victim"), 1)[0].cmd("jobs")
        super(PingExperiment, self)._stop()

    def _produceOutputFiles(self):
        ttparser = TcptraceParser()
        stats = ttparser.plotConnectionStatisticsFromPcap(self.pcapfile)


if __name__ == '__main__':
    logging.basicConfig(**logging_config)
    experiment = PingExperiment()
    experiment.executeExperiment()
