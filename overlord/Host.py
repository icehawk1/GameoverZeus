#!/usr/bin/env python2.7
# coding=UTF-8
"""This file implements a script that can run any Runnable in a separate Thread. It can start and stop it any time.
It is intended to be run on every mininet host to help the architecture being flexible and to allow the overlord to
control all hosts."""

import logging
import os
import random
import socket
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket, TTransport

from HostActions import OverlordClient

try:
    from resources.emu_config import SOCKET_DIR
except:
    # If we execute the script directly from the command line, emu_config wont be found
    SOCKET_DIR = "/tmp/overlordsocket/"


class HostActionHandler(object):
    """Handles RPC calls from the overlord."""

    def __init__(self, hostid=random.randint(1, 10000000)):
        self.currentRunnables = dict()
        self.hostid = hostid

    def startRunnable(self, command, params):
        """Starts the given runnable. Throws an exception if the runnable is not found in the actors module."""

        assert isinstance(command, str)
        assert isinstance(params, dict)
        pass

    def stopRunnable(self, command):
        """Stops the given runnable. Does nothing if that runnable does not exist or is not running."""

        pass

    def getID(self):
        """Returns the host id"""
        return self.hostid


if __name__ == '__main__':
    logging.basicConfig(format="%(threadName)s: %(message)s", level=logging.DEBUG)

    handler = HostActionHandler()
    processor = OverlordClient.Processor(handler)

    logging.debug("Host %s has been created" % handler.getID())

    # Clean up sockets from earlier launches
    if not os.path.isdir(SOCKET_DIR):
        os.remove(SOCKET_DIR)
        os.mkdir(SOCKET_DIR)
    socketFile = SOCKET_DIR + str(handler.getID())
    if os.path.exists(socketFile):
        os.remove(socketFile)

    logging.debug("Opening socket %s" % socketFile)
    serversocket = socket.socket(socket.AF_UNIX)
    serversocket.bind(socketFile)
    transport = TSocket.TServerSocket(unix_socket=socketFile)

    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    server.serve()
