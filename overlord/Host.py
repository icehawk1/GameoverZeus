#!/usr/bin/env python2.7
# coding=UTF-8
"""This file implements a script that can run any Runnable in a separate Thread. It can start and stop it any time.
It is intended to be run on every mininet host to help the architecture being flexible and to allow the overlord to
control all hosts."""

import logging, time, os, importlib, random, sys, socket, tempfile
from threading import Thread
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket, TTransport
from HostActions import OverlordClient
from resources.emu_config import SOCKET_DIR


class HostActionHandler(object):
    """Handles RPC calls from the overlord. Implements the methods defined in HostActions.thrift ."""

    def __init__(self, hostid=random.randint(1, 10000000)):
        self.currentRunnables = dict()
        self.hostid = hostid

    def startRunnable(self, importmodule, command, kwargs):
        """Starts the given runnable. Throws an exception if the runnable is not found in the actors modulestr.
        :param command: The name of the Runnable that should be started
        :param kwargs: A dict that contains the parameter for the command's constructor"""

        assert isinstance(command, str)
        assert isinstance(kwargs, dict)
        print "%s.startRunnable(%s,%s)" % (self.hostid, command, kwargs)

        # Import module and create object
        moduleobj = importlib.import_module("actors." + importmodule)
        try:
            constructorobj = getattr(moduleobj, command)
            runnable = constructorobj(**kwargs)
        except AttributeError:
            raise NotImplementedError("%s.%s() does not exist" % (moduleobj, command))

        # Start runnable in her own Thread
        thread = Thread(name="Runnable %s" % command, target=runnable.start)
        thread.start()

        self.currentRunnables[command] = (runnable, thread)

    def stopRunnable(self, command):
        """Stops the given runnable. Does nothing if that runnable does not exist or is not running.
        :param command: Which runnable should be stopped"""
        if self.currentRunnables.has_key(command):
            logging.debug("%s.stopRunnable(%s)" % (self.hostid, command))

            runnable, thread = self.currentRunnables[command]
            runnable.stop()
            thread.join()
        else:
            logging.debug("Runnable %s not found" % command)

    def getID(self):
        """Returns the host id"""
        return self.hostid


def createRPCServer(processor):
    """Creates RPC server that is configured to listen on a socket in SOCKET_DIR
    :param processor: Thrift Processor that will handle incoming RPC calls"""

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
    # We need buffering for performance
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    result = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    return result


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        # Create temporary file and get absolute path of it
        logfile = tempfile.mkstemp(prefix=sys.argv[1] + "_")[1]
        # Write log to file and delete old logs
        logging.basicConfig(format="%(threadName)s: %(message)s", level=logging.DEBUG, filename=logfile, filemode="w")
        handler = HostActionHandler(sys.argv[1])
    else:
        logging.basicConfig(format="%(threadName)s: %(message)s", level=logging.DEBUG)
        handler = HostActionHandler()

    logging.debug("Host %s has been created" % handler.getID())

    server = createRPCServer(OverlordClient.Processor(handler))
    server.serve()