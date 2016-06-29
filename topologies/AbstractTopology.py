#!/usr/bin/env python2.7
# coding=UTF-8

class AbstractTopology(object):
    def __init__(self, mininet):
        self.mininet = mininet
        self.mininet.addController("controller1")
