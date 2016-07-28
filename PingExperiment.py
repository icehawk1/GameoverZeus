#!/usr/bin/env python2
# coding=UTF-8
import os, time, logging, sys, json, random

sys.path.append(os.path.dirname(__file__))
from mininet import net
from mininet.cli import CLI

from utils import Floodlight
from resources import emu_config
from overlord.Overlord import Overlord
from utils.MiscUtils import addHostToMininet, mkdir_p
from utils.TcptraceParser import TcptraceParser

pypath = "PYTHONPATH=$PYTHONPATH:%s "%emu_config.basedir

if __name__ == '__main__':
    logging.basicConfig(**emu_config.logging_config)
    os.system("fuser -kn tcp 6633")

    net = net.Mininet(controller=Floodlight.Controller)
    net.addController("controller1")

    overlord = Overlord()
    switch = net.addSwitch("switch1")

    hosts = []
    for i in range(1, 100):
        current_host = addHostToMininet(net, switch, "host%d"%i, overlord, bw=25)
        hosts.append(current_host)
    servents = []
    for i in range(1, 10):
        current_servent = addHostToMininet(net, switch, "servent%d"%i, overlord, bw=25)
        servents.append(current_servent)
    clients = []
    for i in range(1, 6):
        current_client = addHostToMininet(net, switch, "client%d"%i, overlord, bw=25)
        clients.append(current_client)

    victim = addHostToMininet(net, switch, "victim1", overlord, bw=90)
    sensor = addHostToMininet(net, switch, "sensor1", overlord)

    net.start()

    for node in hosts + servents + clients + [victim, sensor]:
        node.cmd(pypath + " python2 overlord/Host.py %s &"%node.name)
    time.sleep(15)

    overlord.startRunnable("TestWebsite", "TestWebsite", hostlist=[victim.name])
    overlord.startRunnable("Sensor", "Sensor", {"pagesToWatch": ["http://%s/?root=432"%victim.IP()]},
                           hostlist=[sensor.name])
    for h in hosts:
        overlord.startRunnable("ping.Victim", "Victim", {"name": h.name}, hostlist=[h.name])
    for h in servents:
        overlord.startRunnable("ping.Servent", "Servent", {"name"    : h.name,
                                                           "peerlist": [peer.IP() for peer in
                                                                        random.sample(servents, 2)]}, hostlist=[h.name])
    for h in clients:
        overlord.startRunnable("ping.Client", "Client", {"name"    : h.name,
                                                         "peerlist": [peer.IP() for peer in
                                                                      random.sample(servents, 2)]}, hostlist=[h.name])

    pcapfile_ddos = "/tmp/botnetemulator/tcptrace/victim-ddostraffic.pcap"
    pcapfile_legitimate = "/tmp/botnetemulator/tcptrace/victim-legitimatetraffic.pcap"
    mkdir_p(os.path.dirname(pcapfile_ddos))
    tshark_cmd = "tshark -i any -F pcap -w %s not host %s &"%(pcapfile_ddos, victim.IP())
    victim.cmd(tshark_cmd)
    victim.cmd("tshark -i any -F pcap -w %s port http or port https or port %d and host %s &"%(
        pcapfile_legitimate, emu_config.PORT, victim.IP()))
    print "tshark_cmd: ", tshark_cmd
    logging.debug("Runnables wurden gestartet")
    time.sleep(25)

    chosenOne = random.choice(servents)
    curlcmd = "timeout 60s curl -X POST --data 'command=ddos_server&kwargs=%s' '%s'"%(
        json.dumps({"url": "http://%s:%d/ddos_me"%(victim.IP(), emu_config.PORT)}),
        "http://%s:%d/current_command"%(chosenOne.IP(), emu_config.PORT))
    print curlcmd
    result = chosenOne.cmd(curlcmd, verbose=True)
    print chosenOne.cmd("echo $?")
    logging.info("curl: %s"%result)
    time.sleep(25)
    print "desinfect 1"
    # overlord.desinfectRandomBots(0.3, [h.name for h in clients+servents])
    time.sleep(15)
    print "desinfect 2"
    # overlord.desinfectRandomBots(0.2, [h.name for h in clients+servents])
    time.sleep(15)
    print "desinfect all"
    # overlord.desinfectRandomBots(1, [h.name for h in clients+servents])
    time.sleep(25)

    CLI(net)
    print "tshark: ", victim.cmd("jobs")
    overlord.stopEverything()
    net.stop()

    print "parsing pcap files"
    ttparser = TcptraceParser()
    stats = ttparser.extractConnectionStatisticsFromPcap(os.path.dirname(pcapfile_ddos))
