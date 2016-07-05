#!/usr/bin/env python2.7
# coding=UTF-8
"""This file defines a class that centrally controls every Host in the network. This includes all sorts of actors.
It is also responsible for triggering random events such as bot desinfections, traffic generation, etc.
It uses unix sockets to communicate with the bots because they are independent of the network communication in mininet."""

import logging
import re
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket
from thrift.transport import TTransport

from HostActions import OverlordClient

try:
    from resources.emu_config import SOCKET_DIR
except:
    # If we execute the script directly from the command line, emu_config wont be found
    SOCKET_DIR = "/tmp/overlordsocket/"


class Overlord(object):
    """Central controller for everything."""

    def __init__(self):
        self.knownHosts = dict()

    def addHost(self, hostid):
        """Adds a host to the network"""
        self.knownHosts[hostid] = _HostConnector(hostid)
        logging.debug("added host %s" % hostid)

    def getIDsOfAllKnownHosts(self):
        result = set()
        for host in self.knownHosts.values():
            host.startCommunication()
            result.add(host.client.getID())
            host.stopCommunication()
        return result


class _HostConnector(object):
    """Encapsulates the communication channel to the given host"""

    def __init__(self, hostid):
        self.id = str(hostid)
        assert re.match("[a-zA-Z0-9_]+", self.id)

        transport = TSocket.TSocket(unix_socket=SOCKET_DIR + self.id)
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


if __name__ == '__main__':
    overlord = Overlord()
    overlord.addHost(3545758)
    overlord.addHost(767082)
    overlord.addHost(4678221)
    print overlord.getIDsOfAllKnownHosts()
