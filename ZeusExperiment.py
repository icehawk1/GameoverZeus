#!/usr/bin/env python2
# coding=UTF-8
import os, time, logging, sys, json
from datetime import datetime
sys.path.append(os.path.dirname(__file__))
from mininet.cli import CLI

from resources import emu_config
from utils.MiscUtils import mkdir_p, datetimeToEpoch
from utils.TcptraceParser import TcptraceParser
from utils.ExperimentUtils import initMininet, startMininet, cleanup, addHostToMininet

if __name__ == '__main__':
    logging.basicConfig(**emu_config.logging_config)
    cleanup()
    mininet, overlord, switch = initMininet()

    # Create all the hosts that make up the experimental network and assign them to groups
    hosts = set()
    for i in range(1, 6):
        current_host = addHostToMininet(mininet, switch, "host%d"%i, overlord, bw=25)
        hosts.add(current_host)
    cncserver = addHostToMininet(mininet, switch, "cnc1", overlord)
    victim = addHostToMininet(mininet, switch, "victim1", overlord, bw=90)
    sensor = addHostToMininet(mininet, switch, "sensor1", overlord)
    nodes = lambda: hosts | {cncserver, victim, sensor}
    assert len(nodes()) == len(hosts) + 3, "nodes: %s"%nodes()

    startMininet(mininet, nodes())
    victimAddress = (victim.IP(), emu_config.PORT)

    overlord.startRunnable("TestWebsite", "TestWebsite", hostlist=[victim.name])
    overlord.startRunnable("Sensor", "Sensor", {"pagesToWatch": ["http://%s:%d/?root=1234"%victimAddress]},
                           hostlist=[sensor.name])
    overlord.startRunnable("CnCServer", "CnCServer", {"host": "10.0.0.6"}, hostlist=[cncserver.name])
    for h in hosts:
        overlord.startRunnable("zeus.Bot", "Bot", hostlist=[h.name],
                               kwargs={"name": h.name, "peerlist": [cncserver.IP()], "pauseBetweenDuties": 1})
    pcapfile = "/tmp/botnetemulator/tcptrace/victim.pcap"
    mkdir_p(os.path.dirname(pcapfile))
    victim.cmd("tshark -i any -F pcap -w %s port http or port https &"%pcapfile)
    logging.debug("Runnables wurden gestartet")
    time.sleep(25)

    kwargs = json.dumps({"url": "http://%s:%d/ddos_me"%victimAddress})
    urlOfCnCServer = "http://%s:%d/current_command"%(cncserver.IP(), emu_config.PORT)
    result = cncserver.cmd("timeout 60s wget -q -O - --post-data 'command=ddos_server&timestamp=%d&kwargs=%s' '%s'"
                           %(datetimeToEpoch(datetime.now()), kwargs, urlOfCnCServer), verbose=True)
    logging.debug("wget: %s"%result)

    time.sleep(25)
    overlord.desinfectRandomBots(0.3, [h.name for h in hosts])
    time.sleep(15)
    overlord.desinfectRandomBots(0.2, [h.name for h in hosts])
    time.sleep(15)
    overlord.desinfectRandomBots(1, [h.name for h in hosts])
    time.sleep(25)

    # CLI(net)
    print "tshark: ", victim.cmd("jobs")
    overlord.stopEverything()
    mininet.stop()

    ttparser = TcptraceParser()
    stats = ttparser.extractConnectionStatisticsFromPcap(os.path.dirname(pcapfile))
