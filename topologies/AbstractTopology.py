#!/usr/bin/env python2.7
# coding=UTF-8

class AbstractTopology(object):
    """Abstract base class for all topologies"""
    def __init__(self, mininet):
        self.mininet = mininet
        self.mininet.addController("controller1")
