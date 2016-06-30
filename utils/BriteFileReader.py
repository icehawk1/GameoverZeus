#!/usr/bin/env python2.7
# coding=UTF-8
import re, logging
from abc import abstractmethod, ABCMeta

emptyLineRe = re.compile(r"^\s*$")  # Matches an empty line


def createGraphFromBriteFile(inputfilename, accepters):
    """Reads a BRITE output file and passes its contents to the accepters."""
    # An example input file can be found in testfiles/flatrouter.brite

    assert isinstance(inputfilename, str)
    for accepter in accepters:
        assert isinstance(accepter, BriteGraphAccepter)

    with open(inputfilename, mode="r") as inputfile:
        _readHeader(inputfile, accepters)
        _readNodes(inputfile, accepters)
        _readEdges(inputfile, accepters)

    for acc in accepters:
        acc.writeFooter()


def _readHeader(inputfile, accepters):
    """Parses the header of a BRITE inputfile and extracts the name of the model used to generate the random topology
    and the number of nodes and edges."""
    firstline = inputfile.readline()
    secondline = inputfile.readline()

    # Parse first line of the header
    regex = re.compile(r"Topology:\s*\(\s*(\d+)\s*Nodes,\s*(\d+)\s*Edges\s*\)")
    match = regex.match(firstline)
    assert match is not None, "First line of file %s is invalid: %s" % (inputfile.name, firstline)
    num_nodes, num_edges = match.group(1, 2)

    # Parse second line
    # Model (1 - RTWaxman):  20 100 100 1  2  0.15000000596046448 0.20000000298023224 1 1 10.0 1024.0
    regex = re.compile(r"Model\s*\(\d+\s*-\s*([\w_-]+)\):.*")
    # regex = re.compile(r"Model\s*\(\d+\s*-\s*([\w_-])\):.*")
    match = regex.match(secondline)
    assert match is not None, "Second line of file %s is invalid: %s" % (inputfile.name, secondline)
    modelname = match.group(1)

    for acc in accepters:
        acc.writeHeader(int(num_nodes), int(num_edges), str(modelname))


def _readNodes(inputfile, accepters):
    """Parses the list of nodes"""

    # Matches one of the lines describing a single node
    nodeRe = re.compile(r"(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d-]+)\s([\w_-]+)\s*")

    # Skip over beginning
    while True:
        line = inputfile.readline()
        if (emptyLineRe.match(line)):
            continue
        elif (re.compile("Nodes:.*").match(line)):
            break

    # Match the actual nodes
    while True:
        line = inputfile.readline()
        match = nodeRe.match(line)
        if match:
            nodeid, asid, type = match.group(1, 6, 7)
            for acc in accepters:
                acc.addNode(int(nodeid), int(asid), str(type))
        elif emptyLineRe.match(line):
            # All nodes were parsed
            break
        else:
            logging.warning("File %s contained invalid node description: %s" % (inputfile.name, line))
            continue


def _readEdges(inputfile, accepters):
    """Parses the list Edges"""

    # Matches one of the lines describing an edge
    edgeRe = re.compile(
        r"(\d+)\s+(\d+)\s+(\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+"
        r"(\d+\.\d+)\s+([\d-]+)\s+([\d-]+)\s+([\w_-]+)\s+([-_\w]+)\s*")

    # Skip over beginning
    while True:
        line = inputfile.readline()
        if (emptyLineRe.match(line)):
            continue
        elif (re.compile("Edges:.*").match(line)):
            break

    # Match the actual edges
    while True:
        line = inputfile.readline()
        match = edgeRe.match(line)
        if match:
            edgeid, fromNode, toNode, communicationDelay = match.group(1, 2, 3, 5)
            bandwidth, fromAS, toAS, type = match.group(6, 7, 8, 9)
            for acc in accepters:
                acc.addEdge(int(edgeid), int(fromNode), int(toNode), float(communicationDelay),
                            float(bandwidth), int(fromAS), int(toAS), str(type))
        elif emptyLineRe.match(line):
            # All nodes were parsed
            break
        else:
            logging.warning("File %s contained invalid node description: %s" % (inputfile.name, line))
            continue


class BriteGraphAccepter(object):
    """This is the base class for all objects where createGraphFromBriteFile will write its output to."""
    __metaclass__ = ABCMeta
    wroteHeader = False

    @abstractmethod
    def writeHeader(self, num_nodes, num_edges, modelname):
        self.wroteHeader = True

    @abstractmethod
    def addNode(self, nodeid, asid, nodetype):
        assert self.wroteHeader, "You have to invoke writeHeader() first"

    @abstractmethod
    def addEdge(self, edgeid, fromNode, toNode, communicationDelay, bandwidth, fromAS, toAS, type):
        assert self.wroteHeader, "You have to invoke writeHeader() first"

    @abstractmethod
    def writeFooter(self):
        pass
