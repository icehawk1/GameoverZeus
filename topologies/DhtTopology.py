#!/usr/bin/env python2
# coding=UTF-8
from mininet.net import Mininet

from topologies.BriteTopology import BriteTopology
from utils import Floodlight


class DhtTopology(BriteTopology):
    def __init__(self, mininet=Mininet(controller=Floodlight.Controller), **kwargs):
        super(BriteTopology, self).__init__(mininet, **kwargs)

    def addBot(self):
        pass

    def addVictim(self):
        pass
