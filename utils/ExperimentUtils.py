#!/usr/bin/env python2
# coding=UTF-8
import time, os, random
from utils import Floodlight
from mininet.net import Mininet
from mininet.node import Switch
from overlord.Overlord import Overlord
from resources import emu_config

#: Environment variable that contains the searchpath for python modules/packages. Needed for the imports in Host.py to work.
_pypath = "PYTHONPATH=$PYTHONPATH:%s "%emu_config.basedir


def initMininet(ctrl=Floodlight.Controller):
    mininet = Mininet(controller=ctrl)
    mininet.addController("controller1")
    overlord = Overlord()
    switch = mininet.addSwitch("switch1")
    return mininet, overlord, switch


def createRandomDPID():
    """Creates one of those strange number mininet needs"""
    dpidLen = 16
    return ''.join([random.choice('0123456789ABCDEF') for x in range(dpidLen)])


def addHostToMininet(mn, switch, hostname, overlord, **linkopts):
    """Creates a new host in the mininet network that is connected to the given switch and to the overlord"""
    assert isinstance(mn, Mininet)
    assert isinstance(switch, Switch)
    assert isinstance(hostname, str)

    result = mn.addHost(hostname, dpid=createRandomDPID())
    overlord.addHost(result.name)
    link = mn.addLink(result, switch)
    link.intf1.config(**linkopts)
    link.intf2.config(**linkopts)
    return result


def startMininet(mininet, nodeSet):
    mininet.start()
    for h in nodeSet:
        h.cmd(_pypath + " python2 overlord/Host.py %s &"%h.name)
    time.sleep(15)


def cleanup():
    os.system("fuser -kn tcp 6633")
    os.system("rm -rf /tmp/overlordsockets/ /tmp/loading_times/ /tmp/*.log /tmp/botnetemulator /tmp/pymp-*")
