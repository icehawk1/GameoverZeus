#!/usr/bin/env python2
# coding=UTF-8
"""This file defines a topology that reads a random network generated with BRITE and creates a Mininet topology from it.
It first executes the random network generator BRITE and parses its output file. Those information is used to create a Mininet network.
The BriteTopology module also contains functionality to plot the generated network.
Each autonomous system from the BRITE output file runs in its own subnet."""
import logging, random, re, time, os, tempfile, subprocess
from abc import abstractmethod, ABCMeta
from mininet.node import CPULimitedHost
from mininet.util import custom
from mininet.net import Mininet

from resources.emu_config import basedir
from AbstractTopology import AbstractTopology

emptyLineRe = re.compile(r"^\s*$")  # Matches an empty line


def createBriteFile(configFile):
    """Runs the BRITE random network generator with the given config file and returns the path to its output file.
    The output file contains a randomly generated network topology and can be parsed by applyBriteFile().
    :param configFile: Path to the BRITE configuration file. Syntax as described in the BRITE manual.
    :type configFile: str"""

    assert os.path.isfile(configFile), "The given config file (%s) does not exist or is not a file"%configFile
    outfile = tempfile.mkstemp(suffix=".brite")[1]  # Get filename of temporary file
    workdir = os.path.join(basedir, "resources/BRITE/Java")
    assert os.path.isdir(workdir)
    seedfile = os.path.join(basedir, "resources/brite.seed")
    assert os.path.isfile(seedfile)

    # BRITE has the annoying habit of adding a file extension to the output file given
    retcode = subprocess.call("java Main.Brite %s %s %s"%(configFile, outfile.replace(".brite", ""), seedfile), shell=True,
                              cwd=workdir)
    if retcode != 0:
        logging.warning("BRITE returned with exit code %d"%retcode)

    assert os.path.getsize(outfile) > 1, "BRITE output file was not populated with a network topology"
    return outfile

def applyBriteFile(inputfilename, accepters):
    """Reads a BRITE output file and passes its contents to the accepters.
    :param inputfilename: The path to the BRITE output file
    :type accepters: list of BriteGraphAccepter"""
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
    and the number of nodes and edges.
    :type accepters: list of BriteGraphAccepter"""
    firstline = inputfile.readline()
    secondline = inputfile.readline()

    # Parse first line of the header
    regex = re.compile(r"Topology:\s*\(\s*(\d+)\s*Nodes,\s*(\d+)\s*Edges\s*\)")
    match = regex.match(firstline)
    assert match is not None, "First line of file %s is invalid: %s" % (inputfile.name, firstline)
    num_nodes, num_edges = match.group(1, 2)

    # Parse second line
    # Model (1 - RTWaxman):  20 100 100 1  2  0.15000000596046448 0.20000000298023224 1 1 10.0 1024.0
    regex = re.compile(r"Model\s*\(\d+\s*-\s*([\w_-]+)\).*")
    # regex = re.compile(r"Model\s*\(\d+\s*-\s*([\w_-])\):.*")
    match = regex.match(secondline)
    assert match is not None, "Second line of file %s is invalid: %s" % (inputfile.name, secondline)
    modelname = match.group(1)

    for acc in accepters:
        acc.writeHeader(int(num_nodes), int(num_edges), str(modelname))

    while True:
        line = inputfile.readline()
        if not line.startswith("Model"):
            break


def _readNodes(inputfile, accepters):
    """Parses the list of nodes
    :type accepters: list of BriteGraphAccepter"""

    # Matches one of the lines describing a single node
    nodeRe = re.compile(r"(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d-]+)\s([\w_-]+)\s*")

    # Skip over beginning
    while True:
        line = inputfile.readline()
        if emptyLineRe.match(line):
            continue
        elif re.compile("Nodes:.*").match(line):
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
    """Parses the list Edges
    :type accepters: list of BriteGraphAccepter"""

    # Matches one of the lines describing an edge
    edgeRe = re.compile(
        r"(\d+)\s+(\d+)\s+(\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(-?\d+\.\d+)\s+([\d-]+)\s+([\d-]+)\s+([\w_-]+)\s+([-_\w]+)\s*")

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
            logging.warning("File %s contained invalid edge description: %s"%(inputfile.name, line))
            continue


class BriteGraphAccepter(object):
    """This is the base class for all objects where applyBriteFile will write its output to.
    It defines some callbacks that are invoked by applyBriteFile."""
    __metaclass__ = ABCMeta
    wroteHeader = False

    @abstractmethod
    def writeHeader(self, num_nodes, num_edges, modelname):
        """Invoked when starting to read the BRITE output file"""
        self.wroteHeader = True

    @abstractmethod
    def addNode(self, nodeid, asid, nodetype):
        """Invoked when reading a node
        :param nodeid: unique id of this node
        :param asid: unique of the AS this node belongs to
        :param nodetype: Whether this node is at the border of an AS or in the middle of one"""
        assert self.wroteHeader, "You have to invoke writeHeader() first"

    @abstractmethod
    def addEdge(self, edgeid, fromNode, toNode, communicationDelay, bandwidth, fromAS, toAS, edgetype):
        """Invoked when reading an edge.
        :param edgeid: Unique id of this edge
        :param fromNode: source of the edge
        :param toNode: target of the edge
        :param communicationDelay: How long it takes to send a packet along this edge
        :type communicationDelay: Float
        :param bandwidth: How much data can be send along this edge.
        :type bandwidth: Float
        :param fromAS: AS of the source node
        :param toAS: AS of the target node
        :param edgetype: Whether this edge is between two AS or within an AS"""
        assert self.wroteHeader, "You have to invoke writeHeader() first"

    @abstractmethod
    def writeFooter(self):
        """Invoked after all nodes and edges have been read"""
        pass


class BriteTopology(AbstractTopology, BriteGraphAccepter):
    """The mn topology created from the given BRITE output file.
    It will have a number of interconnected autonomous systems and each AS will have one external_switch and a number of
    hosts. Each host in an AS is connected to that external_switch."""

    def __init__(self, mininet, opts=None, **kwargs):
        """
        Initialises the LayeredTopology, so that layers can be added.
        :type mininet: Mininet
        :param kwargs: A number of keyword arguments to be given to AbstractTopology.__init__()
        """
        AbstractTopology.__init__(self, mininet, **kwargs)
        self.started = False
        self.autonomousSystems = dict()
        self.modelname = None
        self.opts = opts if opts is not None else dict()
        self.cpulimitedhost = custom(CPULimitedHost)

    def writeHeader(self, num_nodes, num_edges, modelname):
        """Invoked when starting to read the BRITE output file"""
        super(BriteTopology, self).writeHeader(num_nodes, num_edges, modelname)
        self.modelname = modelname

    def addNode(self, nodeid, asid, nodetype):
        """Converts a node in the BRITE output file to a mn host. Invoked for every node in the BRITE output file."""

        super(BriteTopology, self).addNode(nodeid, asid, nodetype)
        assert not self.started

        bot = self._addHost(nodeid)

        if not self.autonomousSystems.has_key(asid):
            autsys = _AutonomousSystem()
            autsys.asid = asid
            autsys.botdict = dict()
            autsys.switch = self.mininet.addSwitch(_createSwitchname(asid))
            self.autonomousSystems[asid] = autsys

        self.autonomousSystems[asid].botdict[nodeid] = bot
        # TODO: Use the bandwidth given by BRITE instead of random values
        self._addLinkBetweenNodes(bot, self.autonomousSystems[asid].switch)

    def _addHost(self, nodeid):
        """Adds a mininet host to the topology"""
        if random.uniform(0, 1) < self.probability_of_cpulimitation:
            bot = self.mininet.addHost(_createBotname(nodeid), host=self.cpulimitedhost, opts=self.opts)
        else:
            bot = self.mininet.addHost(_createBotname(nodeid), opts=self.opts)

        super(BriteTopology, self)._addHost(bot)
        return bot

    def addEdge(self, edgeid, fromNode, toNode, communicationDelay, bandwidth, fromAS, toAS, edgetype):
        """Invoked for every edge in the BRITE output file. Converts that edge into a connection between two mn hosts."""
        assert not self.started
        super(BriteTopology, self).addEdge(edgeid, fromNode, toNode, communicationDelay, bandwidth, fromAS, toAS, edgetype)

    def writeFooter(self):
        """Invoked after fully reading the BRITE output file"""
        super(BriteTopology, self).writeFooter()
        self._connectSwitchesToSwitches()
        self._connectASNodesToSwitches()

    def start(self):
        """Starts operation of the defined Topology. It will also start the command for each of the layers."""
        self.started = True
        self.mininet.start()
        time.sleep(2)

    def stop(self):
        """Stops the operation of this topology. Usually called when the experiment is over."""
        self.mininet.stop()

    def _connectSwitchesToSwitches(self):
        """Connects all the switches to each other."""
        askeys = self.autonomousSystems.keys()
        for i in range(1, len(askeys)):
            switch1 = self.autonomousSystems[askeys[i - 1]].switch
            switch2 = self.autonomousSystems[askeys[i]].switch
            self._addLinkBetweenNodes(switch1, switch2)

    def _connectASNodesToSwitches(self):
        """Connects the nodes in a common autonomous system to their external_switch"""
        for autsys in self.autonomousSystems.values():
            for bot in autsys.botdict.values():
                self._addLinkBetweenNodes(autsys.switch, bot)

class _AutonomousSystem(object):
    """A value class for an autonomous system as generated by BRITE"""
    botdict = dict()
    switch = None
    asid = None

    def __len__(self):
        return len(self.botdict.values())


def _createBotname(nodeid):
    return "bot%d" % nodeid


def _createSwitchname(asid):
    return "sw%d" % asid
