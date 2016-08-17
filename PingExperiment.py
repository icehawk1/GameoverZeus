#!/usr/bin/env python2
# coding=UTF-8
import os, time, logging, sys, json, random
from datetime import datetime

sys.path.append(os.path.dirname(__file__))
from mininet.cli import CLI

from resources import emu_config
from utils.MiscUtils import datetimeToEpoch
from utils.TcptraceParser import TcptraceParser


if __name__ == '__main__':
    logging.basicConfig(**emu_config.logging_config)
    cleanup()
    mininet, overlord, switch = initMininet()

    # Create all the hosts that make up the experimental network and assign them to groups
    servents = {addHostToMininet(mininet, switch, "servent%d"%i, overlord, bw=25) for i in range(10)}
    nonInfectedHosts = set()
    victim = addHostToMininet(mininet, switch, "victim%d"%1, overlord, bw=125)
    sensor = addHostToMininet(mininet, switch, "sensor%d"%1, overlord)
    bots = lambda: (servents)
    nodes = lambda: (bots() | {victim, sensor} | nonInfectedHosts)
    assert len(nodes()) > 0
    assert len(bots()) > 0 and len(servents) <= len(nodes())

    victimAddress = (victim.IP(), emu_config.PORT)
    startMininet(mininet, nodes())

    for h in servents:
        peerlist = random.sample([peer.IP() for peer in servents if not peer == h], 3)
        overlord.startRunnable("ping.Servent", "Servent", {"peerlist": peerlist, "pauseBetweenDuties": 5},
                               hostlist=[h.name])
    overlord.startRunnable("Victim", "Victim", {}, hostlist=[victim.name])
    overlord.startRunnable("Sensor", "Sensor", {"pagesToWatch": ["http://%s:%d/?root=1432"%victimAddress]},
                           hostlist=[sensor.name])
    time.sleep(5)

    chosenOne = random.sample(servents, 1)[0]
    curlcmd = "timeout 60s wget -q -O - --post-data 'command=ddos_server&kwargs=%s&timestamp=%d' '%s'"%(
        json.dumps({"url": "http://%s:%d/ddos_me"%victimAddress}), datetimeToEpoch(datetime.now()),
        "http://%s:%d/current_command"%(chosenOne.IP(), emu_config.PORT))
    result = chosenOne.cmd(curlcmd, verbose=True)
    #print chosenOne.cmd("echo $?")
    logging.info("wget: %s"%result)
    time.sleep(2)

    time.sleep(25)
    for i, prob in enumerate([0.3, 0.2, 1]):
        print "desinfect %d"%i
        desinfected = set(overlord.desinfectRandomBots(prob, [h.name for h in bots()]))
        servents -= desinfected
        nonInfectedHosts |= desinfected
        print bots()
        time.sleep(15)
    time.sleep(10)

    print "servent: ", chosenOne.cmd("jobs")
    print "victim: ", victim.cmd("jobs")

    #CLI(mininet)
    overlord.stopEverything()
    mininet.stop()
