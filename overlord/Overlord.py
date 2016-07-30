#!/usr/bin/env python2
# coding=UTF-8
"""This file defines a class that centrally controls every Host in the network. This includes all sorts of actors.
It is also responsible for triggering random events such as bot desinfections, traffic generation, etc.
It uses unix sockets to communicate with the clients because they are independent of the network communication in mn."""

import logging, json, re, random, time, os, pkgutil
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
from thrift.transport.TTransport import TTransportException

from HostActions import OverlordClient
from resources.emu_config import SOCKET_DIR
from utils.MiscUtils import mkdir_p
from utils import LogfileParser

class Overlord(object):
    """Central controller for everything."""

    def __init__(self):
        self.knownHosts = dict()
        mkdir_p(SOCKET_DIR)

        # Remove machine readable logfile from previous runs
        if os.path.exists(LogfileParser.logfile):
            os.remove(LogfileParser.logfile)

    def addHost(self, hostid):
        """Adds a host to the network"""
        self.knownHosts[hostid] = _HostConnector(hostid)
        logging.debug("added host %s" % hostid)

    def getIDsOfAllKnownHosts(self):
        """Return a set of the IDs of all hosts that are currently controlled by this Overlord"""
        result = set()
        for host in self.knownHosts.values():
            host.startCommunication()
            result.add(host.client.getID())
            host.stopCommunication()
        return result

    def startRunnable(self, importmodule, runnable, kwargs=dict(), hostlist=None):
        """Instruct the given hosts to run a certain Runnable.
        :param runnable: The name of a subclass of RandomTrafficReceiver.Runnable that does the work that the hosts shall be doing.
        :type runnable: str
        :param importmodule: The name of  the module where the subclass of RandomTrafficReceiver.Runnable is defined.
        :type importmodule: str
        :param kwargs: The constructor parameter for the runnable
        :type kwargs: dict
        :param hostlist: A list of hosts that will execute the runnable. Defaults to all currently known hosts.
        :type hostlist: list"""
        assert isinstance(importmodule, str)
        assert isinstance(runnable, str)
        assert isinstance(kwargs, dict)

        # Test if importmodule exists and has a runnable with the given name
        try:
            runnableLoader = pkgutil.find_loader('actors.%s'%importmodule)
            assert runnableLoader is not None, "The runnable %s does not exist in module %s"%(runnable, importmodule)
        except ImportError as ex:
            logging.error("The module actors.%s does not exist"%importmodule)

        # By default, start runnable on all known hosts
        if hostlist is None:
            hostlist = self.knownHosts.keys()
        assert isinstance(hostlist, list)

        for hostid in hostlist:
            try:
                assert isinstance(hostid, str)
                assert self.knownHosts.has_key(hostid)
                connector = self.knownHosts[hostid]
                assert isinstance(connector, _HostConnector)

                connector.startCommunication()
                connector.client.startRunnable(importmodule, runnable, json.dumps(kwargs))
                connector.stopCommunication()
            except TTransportException as ex:
                logging.error("Could not send startRunnable command to connector %s: %s" % (hostid, ex.message))

    def stopRunnable(self, runnable="*", hostlist=None):
        """Stops the given runnable on the given hosts. Hosts that do not run a runnable with the given name are silently skipped.
        :param runnable: The name of a subclass of RandomTrafficReceiver.Runnable that does the work that the hosts shall be doing.
                        Give a star or leave out to stop every runnable on the hosts.
        :type runnable: str
        :param hostlist: A list of hosts that will execute the runnable. Defaults to all currently known hosts.
        :type hostlist: list"""

        if hostlist is None:
            hostlist = self.knownHosts.keys()

        for hostid in hostlist:
            try:
                assert isinstance(hostid, str)
                connector = self.knownHosts[str(hostid)]
                assert isinstance(connector, _HostConnector)
                connector.startCommunication()
                logging.debug("Stopping runnable %s of host %s" % (runnable, connector.id))
                connector.client.stopRunnable(runnable)
                connector.stopCommunication()
            except TTransportException as ex:
                logging.error("Could not send stopRunnable command to connector %s: %s" % (hostid, ex.message))

    def stopEverything(self, hostlist=None):
        """Stops everything that is running on the given hosts. Called before the program exits."""
        self.stopRunnable(hostlist=hostlist)
        logging.debug("Stopped all runnables for all hosts")

    def removeRandomBots(self, probability, hostlist=None):
        """Goes through hostlist and randomly decides, with the given probability, if it will stop all runnables on that machine
        :param probability: The probability that a node will be stoped as a float between 0 and 1
        :param hostlist: A list of hosts that will execute the runnable. Defaults to all currently known hosts.
        :type hostlist: list of strings
        :type probability: a float between 0 and 1
        :return: the clients that were removed"""
        probability = float(probability)
        assert 0 <= probability <= 1

        if hostlist is None:
            hostlist = self.knownHosts.values()
        toRemove = [str(host) for host in hostlist if random.uniform(0, 1) <= probability]
        self.stopRunnable(hostlist=toRemove)
        return toRemove

    def desinfectRandomBots(self, probability, hostlist=None):
        """Goes through hostlist and randomly decides, with the given probability, if it will stop all runnables on that machine
            and then start the Victim runnable.
            :param probability: The probability that a node will be stoped as a float between 0 and 1
            :param hostlist: A list of hosts that will execute the runnable. Defaults to all currently known hosts.
            :type hostlist: list of strings
            :type probability: a float between 0 and 1
            :return: the clients that were desinfected"""
        desinfected = self.removeRandomBots(probability, hostlist)
        time.sleep(3)
        self.startRunnable("Victim", "Victim", hostlist=desinfected)
        return desinfected

class _HostConnector(object):
    """Encapsulates the communication channel to the given host"""

    def __init__(self, hostid):
        self.id = str(hostid)
        assert re.match("[a-zA-Z0-9_-]+", self.id), "Invalid host id: %s" % hostid

        socketfile = SOCKET_DIR + self.id
        transport = TSocket.TSocket(unix_socket=socketfile)
        # Buffering is critical. Raw sockets are very slow
        self.transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        # Create a client that will be used to remotely invoke commands on the host
        self.client = OverlordClient.Client(protocol)

    def startCommunication(self):
        """Opens the communication channel, so that self.client can be used."""
        self.transport.open()

    def stopCommunication(self):
        """Closes the communication."""
        self.transport.close()
