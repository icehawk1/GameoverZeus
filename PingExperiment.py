#!/usr/bin/env python2
# coding=UTF-8
import os, time, logging, sys, json, random
from datetime import datetime

sys.path.append(os.path.dirname(__file__))
from mininet import net
from mininet.cli import CLI

from utils import Floodlight
from resources import emu_config
from overlord.Overlord import Overlord
from utils.MiscUtils import addHostToMininet, mkdir_p, datetimeToEpoch
from utils.TcptraceParser import TcptraceParser

pypath = "PYTHONPATH=$PYTHONPATH:%s "%emu_config.basedir

if __name__ == '__main__':
    logging.basicConfig(**emu_config.logging_config)
    os.system("fuser -kn tcp 6633")
    os.system("rm -rf /tmp/overlordsockets/ /tmp/loading_times/ /tmp/*.log /tmp/botnetemulator /tmp/pymp-*")

    net = net.Mininet(controller=Floodlight.Controller)
    net.addController("controller1")
    overlord = Overlord()
    switch = net.addSwitch("switch1")

    servents = [addHostToMininet(net, switch, "servent%d"%i, overlord, bw=25) for i in range(2)]
    victim = addHostToMininet(net, switch, "victim%d"%i, overlord, bw=25)

    peng = addHostToMininet(net, switch, "peng%d"%1, overlord, bw=25)
    bumm = addHostToMininet(net, switch, "bumm%d"%1, overlord, bw=25)

    net.start()

    for h in servents + [victim]:
        h.cmd(pypath + " python2 overlord/Host.py %s &"%h.name)
    time.sleep(1)
    for h in servents:
        peerlist = [peer.IP() for peer in servents if not peer == h]
        overlord.startRunnable("ping.Servent", "Servent", {"peerlist": peerlist, "pauseBetweenDuties": 5},
                               hostlist=[h.name])
    overlord.startRunnable("TestWebsite", "TestWebsite", {}, hostlist=[h.name])
    time.sleep(2)

    curlcmd = "timeout 60s wget  -O - --post-data 'command=ddos_server&kwargs=%s&timestamp=%d' '%s'"%(
        json.dumps({"url": "http://%s:%d/ddos_me"%(victim.IP(), emu_config.PORT)}), datetimeToEpoch(datetime.now()),
        "http://%s:%d/current_command"%(servents[0].IP(), emu_config.PORT))
    result = peng.cmd(curlcmd, verbose=True)
    print peng.cmd("echo $?")
    logging.info("wget: %s"%result)
    time.sleep(2)

    time.sleep(15)

    print "servent: ", servents[0].cmd("jobs")
    print "victim: ", victim.cmd("jobs")

    # CLI(net)
    overlord.stopEverything()
    net.stop()
