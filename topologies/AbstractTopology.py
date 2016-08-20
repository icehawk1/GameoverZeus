#!/usr/bin/env python2
# coding=UTF-8
"""This module defines the abstract base interface for topologies.
Topologies implement the addition of Mininet hosts and links between them"""
import random

class AbstractTopology(object):
    """Abstract base class for all topologies. The Topology class encapsulates the layout of the simulated network.
    That is, it defines which nodes exist and how they are interconnected."""

    def __init__(self, mininet, probability_of_cpulimitation=0, probability_unreliable_links=0):
        """:param mininet: Mininet instance to be used for running this topology
        :param probability_of_cpulimitation: How likely it is that a Host will be created as a CPULimitedHost
        :param probability_unreliable_links: How likely it is that any link between a host and switch will have
        some restrictions regarding packet loss and delay"""

        self.mininet = mininet
        self.mininet.addController("controller1")
        self.probability_of_cpulimitation = probability_of_cpulimitation
        self.probability_of_unreliable_links = probability_unreliable_links
        self._nodes = set()

        assert 0 <= self.probability_of_cpulimitation <= 1, \
            "probability_of_cpulimitation must be between 0 and 1: %d" % self.probability_of_cpulimitation
        assert 0 <= self.probability_of_unreliable_links <= 1, \
            "probability_unreliable_links must be between 0 and 1: %d" % self.probability_of_unreliable_links

    def _addLinkBetweenNodes(self, node1, node2):
        """Adds a link between the given Mininet nodes and assigns random values for bandwidth, packet loss and delay"""
        if random.uniform(0, 1) < self.probability_of_unreliable_links:
            linkoptions = {'bw': random.randint(1, 100), 'loss': random.uniform(1, 30),
                           'delay': '%dms' % random.uniform(1, 500)}
            self.mininet.addLink(node1, node2, linkoptions)
        else:
            self.mininet.addLink(node1, node2)

    @property
    def nodes(self):
        """Returns a read-only view of the nodes in this topology"""
        return frozenset(self._nodes)

    def _addHost(self, mnhost):
        self._nodes.add(mnhost)
