#!/usr/bin/env python2
# coding=UTF-8
"""This file defines a Writer that creates PDF and SVG visualizations from BRITE output files."""

import logging
import pygraphviz as pgv
import sys
from string import lower

from topologies.BriteTopology import BriteGraphAccepter, applyBriteFile

nodetype_to_color = {'RT_NODE': 'blue', 'RT_BORDER': 'red'}
edgetype_to_color = {'E_RT': 'blue', 'E_AS': 'red'}


class DotFileWriter(BriteGraphAccepter):
    def __init__(self):
        self.graph = None

    def writeHeader(self, num_nodes, num_edges, modelname):
        super(DotFileWriter, self).writeHeader(num_nodes, num_edges, modelname)
        self.graph = pgv.AGraph(directed=False, name=modelname)

    def addNode(self, nodeid, asid, nodetype):
        super(DotFileWriter, self).addNode(nodeid, asid, nodetype)

        attributes = {}
        if nodetype_to_color.has_key(nodetype):
            attributes["color"] = nodetype_to_color[nodetype]
        attributes["comment"] = "AS %d" % asid
        attributes["label"] = nodeid
        attributes["group"] = asid

        self.graph.add_node(nodeid, **attributes)

    def addEdge(self, edgeid, fromNode, toNode, communicationDelay, bandwidth, fromAS, toAS, edgetype):
        super(DotFileWriter, self).addEdge(edgeid, fromNode, toNode, communicationDelay, bandwidth, fromAS, toAS,
                                           edgetype)

        attributes = {}
        if edgetype_to_color.has_key(edgetype):
            attributes["color"] = edgetype_to_color[edgetype]
        attributes["comment"] = "delay %d, bandwidth %d" % (communicationDelay, bandwidth)

        self.graph.add_edge(fromNode, toNode, **attributes)

    def writeFooter(self):
        super(DotFileWriter, self).writeFooter()
        self.graph.layout()

    def generatePdf(self, filename):
        assert isinstance(filename, str)

        if lower(filename).endswith(".pdf"):
            self.graph.draw(filename)
            logging.info("Wrote PDF to %s" % filename)
        else:
            self.graph.draw(filename + ".pdf")
            logging.info("Wrote PDF to %s" % filename + ".pdf")

    def generateSvg(self, filename):
        assert isinstance(filename, str)

        if lower(filename).endswith(".svg"):
            self.graph.draw(filename)
            logging.info("Wrote SVG to %s" % filename)
        else:
            self.graph.draw(filename + ".svg")
            logging.info("Wrote SVG to %s" % filename + ".svg")


if __name__ == "__main__":
    if len(sys.argv) >= 4:
        writer = DotFileWriter()
        applyBriteFile(sys.argv[1], [writer])
        writer.generatePdf(sys.argv[2])
        writer.generateSvg(sys.argv[3])
