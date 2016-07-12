#!/usr/bin/env python2.7
# coding=UTF-8
import random

class AbstractTopology(object):
    """Abstract base class for all topologies. See package documentation for details."""

    def __init__(self, mininet, probability_of_cpulimitation=0, probability_unreliable_links=0):
        """:param mininet: Mininet instance to be used for running this topology
        :param probability_of_cpulimitation: How likely it is that a Host will be created as a CPULimitedHost
        :param probability_unreliable_links: How likely it is that any link between a host and switch will have
        some restrictions regarding packet loss and delay
        :param linkoptions: The bandwidth, delay and/or packet loss options to impose on unreliable links
        :type linkoptions: dict"""

        self.mininet = mininet
        self.mininet.addController("controller1")
        self.probability_of_cpulimitation = probability_of_cpulimitation
        self.probability_of_unreliable_links = probability_unreliable_links

        assert 0 <= self.probability_of_cpulimitation <= 1, \
            "probability_of_cpulimitation must be between 0 and 1: %d" % self.probability_of_cpulimitation
        assert 0 <= self.probability_of_unreliable_links <= 1, \
            "probability_unreliable_links must be between 0 and 1: %d" % self.probability_of_unreliable_links

    # TODO: Find a way to use the numbers given by BRITE instead of random values
    def _addLinkBetweenNodes(self, node1, node2):
        if random.uniform(0, 1) < self.probability_of_unreliable_links:
            linkoptions = {'bw': random.randint(1, 100), 'loss': random.uniform(1, 30),
                           'delay': '%dms' % random.uniform(1, 500)}
            self.mininet.addLink(node1, node2, linkoptions)
        else:
            self.mininet.addLink(node1, node2)
