#!/usr/bin/env python2
# coding=UTF-8
"""This file defines a class that centrally controls every Host in the network. This includes all sorts of actors.
It is also responsible for triggering random events such as bot desinfections, traffic generation, etc.
It uses unix sockets to communicate with the bots because they are independent of the network communication in mn."""

import logging, json, re
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
from thrift.transport.TTransport import TTransportException

from HostActions import OverlordClient
from resources.emu_config import SOCKET_DIR
from utils.MiscUtils import mkdir_p

class Overlord(object):
    """Central controller for everything."""

    def __init__(self):
        self.knownHosts = dict()
        mkdir_p(SOCKET_DIR)

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
        # TODO: Keep track of running Runnables
        """Instruct the given hosts to run a certain Runnable.
        :param runnable: The name of a subclass of AbstractBot.Runnable that does the work that the hosts shall be doing.
        :type runnable: str
        :param importmodule: The name of  the module where the subclass of AbstractBot.Runnable is defined.
        :type importmodule: str
        :param kwargs: The constructor parameter for the runnable
        :type kwargs: dict
        :param hostlist: A list of hosts that will execute the runnable. Defaults to all currently known hosts.
        :type hostlist: list"""
        assert isinstance(importmodule, str)
        assert isinstance(runnable, str)
        assert isinstance(kwargs, dict)

        if hostlist is None:
            hostlist = self.knownHosts.values()
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
                logging.error("Could not send startRunnable command to connector %s: %s" % (connector.id, ex.message))

    def stopRunnable(self, runnable, hostlist=None):
        """Stops the given runnable on the given hosts. Hosts that do not run a runnable with the given name are silently skipped.
        :param runnable: The name of a subclass of AbstractBot.Runnable that does the work that the hosts shall be doing.
        :type runnable: str
        :param hostlist: A list of hosts that will execute the runnable. Defaults to all currently known hosts.
        :type hostlist: list"""

        if hostlist is None:
            hostlist = self.knownHosts.values()

        logging.debug("Stopping runnable %s of hosts %s" % (runnable, [host.id for host in hostlist]))

        for connector in hostlist:
            try:
                assert isinstance(connector, _HostConnector)
                connector.startCommunication()
                connector.client.stopRunnable(runnable)
                connector.stopCommunication()
            except TTransportException as ex:
                logging.error("Could not send stopRunnable command to connector %s: %s" % (connector.id, ex.message))

    def stopEverything(self, hostlist=None):
        """Stops everything that is running on the given hosts. Called before the program exits."""
        self.stopRunnable("*", hostlist)
        logging.debug("Stopped all runnables for all hosts")

class _HostConnector(object):
    """Encapsulates the communication channel to the given host"""

    def __init__(self, hostid):
        self.id = str(hostid)
        assert re.match("[a-zA-Z0-9_]+", self.id), "Invalid host id: %s" % hostid

        transport = TSocket.TSocket(unix_socket=SOCKET_DIR + self.id)
        logging.debug("Use socket %s" % (SOCKET_DIR + self.id))
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
