#!/usr/bin/env python2
# coding=UTF-8
import os, time, logging, sys, json
from datetime import datetime

sys.path.append(os.path.dirname(__file__))
from mininet import net
from mininet.cli import CLI

from utils import Floodlight
from resources import emu_config
from overlord.Overlord import Overlord
from utils.MiscUtils import addHostToMininet, mkdir_p, datetimeToEpoch
from utils.TcptraceParser import TcptraceParser
from utils.LogfileParser import writeLogentry, logfile

pypath = "PYTHONPATH=$PYTHONPATH:%s "%emu_config.basedir

if __name__ == '__main__':
    logging.basicConfig(**emu_config.logging_config)
    # Remove machine readable logfile from previous runs
    if os.path.exists(logfile):
        os.remove(logfile)
    print datetimeToEpoch(datetime.now())
    writeLogentry(runnable="ZeusExperiment", message="Experiment started")

    net = net.Mininet(controller=Floodlight.Controller)
    net.addController("controller1")

    overlord = Overlord()
    switch = net.addSwitch("switch1")

    hosts = []
    for i in range(1, 6):
        current_host = addHostToMininet(net, switch, "host%d"%i, overlord, bw=25)
        hosts.append(current_host)
    cncserver = addHostToMininet(net, switch, "cnc1", overlord)
    victim = addHostToMininet(net, switch, "victim1", overlord, bw=90)
    sensor = addHostToMininet(net, switch, "sensor1", overlord)

    net.start()
    # net.pingAll()

    for node in hosts + [victim, cncserver, sensor]:
        node.cmd(pypath + " python2 overlord/Host.py %s &"%node.name)
    time.sleep(5)

    overlord.startRunnable("TestWebsite", "TestWebsite", hostlist=[victim.name])
    overlord.startRunnable("Sensor", "Sensor", {"pagesToWatch": ["http://%s/?root=432"%victim.IP()]},
                           hostlist=[sensor.name])
    overlord.startRunnable("CnCServer", "CnCServer", {"host": "10.0.0.6"}, hostlist=[cncserver.name])
    for h in hosts:
        overlord.startRunnable("Bot", "Bot",
                               {"name": h.name, "peerlist": [cncserver.IP()], "pauseBetweenDuties": 1},
                               hostlist=[h.name])
    pcapfile = "/tmp/botnetemulator/tcptrace/victim.pcap"
    mkdir_p(os.path.dirname(pcapfile))
    victim.cmd("tshark -i any -F pcap -w %s  &"%pcapfile)
    logging.debug("Runnables wurden gestartet")
    time.sleep(25)

    writeLogentry(runnable="ZeusExperiment", message="issued command ddos_server")
    result = cncserver.cmd("curl -X POST --data 'command=ddos_server&kwargs=%s' '%s'"
                           %(json.dumps({"url": "http://%s:%d/ddos_me"%(victim.IP(), emu_config.PORT)}),
                             "http://%s:%d/current_command"%(cncserver.IP(), emu_config.PORT)), verbose=True)
    logging.debug("curl: %s"%result)
    time.sleep(45)
    overlord.desinfectRandomBots(0.3, [h.name for h in hosts])
    time.sleep(45)
    overlord.desinfectRandomBots(0.2, [h.name for h in hosts])
    time.sleep(45)
    overlord.desinfectRandomBots(1, [h.name for h in hosts])
    time.sleep(45)

    # CLI(net)
    print "tshark: ", victim.cmd("jobs")
    overlord.stopEverything()
    net.stop()

    ttparser = TcptraceParser(host="victim")
    stats = ttparser.extractConnectionStatisticsFromPcap(pcapfile)

    writeLogentry(runnable="ZeusExperiment", message="Experiment ended")
