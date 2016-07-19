#!/usr/bin/env python2
# coding=UTF-8
import os, time, logging, sys, json

sys.path.append(os.path.dirname(__file__))
from mininet import net
from mininet.cli import CLI
import requests

from utils import Floodlight
from resources import emu_config
from overlord.Overlord import Overlord

pypath = "PYTHONPATH=$PYTHONPATH:%s " % emu_config.basedir


def addHostToMininet(mn, switch, hostname, **linkopts):
    result = mn.addHost(hostname)
    overlord.addHost(result.name)
    link = mn.addLink(result, switch)
    link.intf1.config(**linkopts)
    link.intf2.config(**linkopts)
    return result


if __name__ == '__main__':
    logging.basicConfig(**emu_config.logging_config)

    os.system("fuser -k -n tcp 6633")  # Kill controller if it is still running
    net = net.Mininet(controller=Floodlight.Controller)
    net.addController("controller1")

    overlord = Overlord()
    switch = net.addSwitch("switch1")

    hosts = []
    for i in range(1, 6):
        current_host = addHostToMininet(net, switch, "host%d" % i, bw=25)
        hosts.append(current_host)
    cncserver = addHostToMininet(net, switch, "cnc1")
    victim = addHostToMininet(net, switch, "victim1", bw=90)
    sensor = addHostToMininet(net, switch, "sensor1")

    net.start()
    # net.pingAll()

    for node in hosts + [victim, cncserver, sensor]:
        node.cmd(pypath + " python2 overlord/Host.py %s &" % node.name)
    time.sleep(1)

    overlord.startRunnable("TestWebsite", "TestWebsite", hostlist=[victim.name])
    overlord.startRunnable("Sensor", "Sensor", {"pagesToWatch": ["http://%s/?root=422" % victim.IP()]},
                           hostlist=[sensor.name])
    overlord.startRunnable("CnCServer", "CnCServer", {"host": "10.0.0.6"}, hostlist=[cncserver.name])
    overlord.startRunnable("Bot", "Bot", {"peerlist": [cncserver.IP()], "pauseBetweenDuties": 1},
                           hostlist=[h.name for h in hosts])
    logging.debug("Runnables wurden gestartet")
    time.sleep(5)

    result = cncserver.cmd("curl -X POST --data 'command=ddos_server&kwargs=%s' '%s'"
                           % (json.dumps({"url": "http://%s:%d/ddos_me" % (victim.IP(), emu_config.PORT)}),
                              "http://%s:%d/current_command" % (cncserver.IP(), emu_config.PORT)), verbose=True)
    logging.debug("curl: %s" % result)
    time.sleep(5)
    # overlord.desinfectRandomBots(0.2, [h.name for h in hosts])
    # time.sleep(5)
    # overlord.desinfectRandomBots(0.2, [h.name for h in hosts])
    # time.sleep(5)

    # CLI(net)
    overlord.stopEverything()
    net.stop()
