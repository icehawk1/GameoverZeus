#!/usr/bin/env python2
# coding=UTF-8
import os, logging, random, time, json
from datetime import datetime

from resources.emu_config import logging_config, PORT
from utils.MiscUtils import mkdir_p, datetimeToEpoch
from Experiment import BriteExperiment
from utils.LogfileParser import writeLogentry
from utils.TcptraceParser import TcptraceParser

def sendDDoSCommand(hostList, victimip):
    if len(hostList)==0:
        logging.warn("Could not send ddos command to empty host list")
        return

    botToIssueCommandFrom = random.sample(hostList, 1)[0]
    writeLogentry(runnable="KademliaExperiment", message="Send command %s to bot %s"%("ddos_server", botToIssueCommandFrom))

    kwargsStr = json.dumps({"url": "http://%s:%d/ddos_me"%(victimip, PORT)})
    urlToAttack = "http://%s:%d/current_command"%(botToIssueCommandFrom.IP(), PORT)
    result = botToIssueCommandFrom.cmd("timeout 60s wget -q -O - --post-data 'command=ddos_server&kwargs=%s&timestamp=%d' '%s'"
                                       %(kwargsStr, datetimeToEpoch(datetime.now()), urlToAttack), verbose=True)

    assert "OK" in result.strip(), "Could not send the DDoS-command to the bot %s: |%s|"%(botToIssueCommandFrom, result)


class KademliaExperiment(BriteExperiment):
    def __init__(self):
        super(KademliaExperiment, self).__init__()
        self.pcapfile = os.path.join(self.outputdir, "tcptrace/victim.pcap")
        mkdir_p(os.path.dirname(self.pcapfile))

    def _setup(self):
        """Creates all the hosts that make up the experimental network and assign them to groups"""
        super(KademliaExperiment, self)._setup()

        nodes = set(self.topology.nodes)
        assert len(nodes) >= 37
        self.setNodes("bots", set(random.sample(nodes, 25)))
        nodes -= self.getNodes("bots")
        self.setNodes("users", set(random.sample(nodes, 25)))
        nodes -= self.getNodes("users")
        self.setNodes("victim", set(random.sample(nodes, 1)))
        nodes -= self.getNodes("victim")
        self.setNodes("sensor", set(random.sample(nodes, 1)))

    def _start(self):
        super(KademliaExperiment, self)._start()

        pingresult = self.mininet.pingPair()
        assert int(pingresult) == 0, "pingpair: %s"%pingresult

        assert len(self.getNodes("victim")) >= 1
        victim = random.sample(self.getNodes("victim"), 1)[0]  # Get a random element from a set
        logging.debug("IP of Victim: %s"%(victim.IP()))

        # Start the necessary runnables
        self.overlord.startRunnable("Victim", "Victim", hostlist=[victim.name])
        self.overlord.startRunnable("Sensor", "Sensor", {"pagesToWatch": ["http://%s:%d/?root=1234"%(victim.IP(), PORT)]},
                                    hostlist=[h.name for h in self.getNodes("sensor")])
        for h in self.getNodes("users"):
            current_peerlist = random.sample([x.IP() for x in self.getNodes("users") | self.getNodes("bots") if not x == h], 3)
            self.overlord.startRunnable("overbot.KademliaUser", "KademliaUser",
                                        {"name": h.name, "peerlist": current_peerlist}, hostlist=[h.name])
        for h in self.getNodes("bots"):
            current_peerlist = random.sample([x.IP() for x in self.getNodes("users") | self.getNodes("bots") if not x == h], 3)
            self.overlord.startRunnable("overbot.KademliaBot", "KademliaBot",
                                        {"name": h.name, "peerlist": current_peerlist}, hostlist=[h.name])

        victim.cmd(self.tsharkCommand%self.pcapfile)
        logging.debug("Runnables wurden gestartet")
        time.sleep(35)

    def _executeStep(self, num):
        result = super(KademliaExperiment, self)._executeStep(num)

        victim = random.sample(self.getNodes("victim"), 1)[0]
        sendDDoSCommand(self.getNodes("bots"), victim.IP())
        time.sleep(35)

        return result

    def _produceOutputFiles(self):
        ttparser = TcptraceParser()
        stats = ttparser.plotConnectionStatisticsFromPcap(self.pcapfile)


if __name__ == '__main__':
    logging.basicConfig(filename='/var/log/botnetemulator.log', filemode="w", **logging_config)

    experiment = KademliaExperiment()
    experiment.executeExperiment()
