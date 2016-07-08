#!/usr/bin/env python2.7
# coding=UTF-8

class AbstractTopology(object):
    """Abstract base class for all topologies"""

    def __init__(self, mininet, probability_of_cpulimitation=0):
        self.mininet = mininet
        self.mininet.addController("controller1")
        self.probability_of_cpulimitation = probability_of_cpulimitation
        assert 0 <= self.probability_of_cpulimitation <= 1, \
            "probability_of_cpulimitation must be between 0 and 1: %d" % self.probability_of_cpulimitation
