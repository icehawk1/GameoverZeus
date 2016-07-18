#!/usr/bin/env python2
# coding=UTF-8
"""This file implements a script that can run any Runnable in a separate Thread. It can start and stop it any time.
It is intended to be run on every mn host to help the architecture being flexible and to allow the overlord to
control all hosts."""

import logging, json, os, importlib, random, sys, socket, tempfile

sys.path.append(os.path.dirname(__file__))
from threading import Thread
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket, TTransport
from HostActions import OverlordClient
from resources.emu_config import SOCKET_DIR, logging_config


class HostActionHandler(object):
    """Handles RPC calls from the overlord. Implements the methods defined in HostActions.thrift ."""

    def __init__(self, hostid=random.randint(1, 10000000)):
        self.currentRunnables = dict()
        self.hostid = hostid

    def startRunnable(self, importmodule, command, kwargs):
        """Starts the given runnable. Throws an exception if the runnable is not found in the actors modulestr.
        :param importmodule: the module where the runnable needs to be imported from
        :param command: The name of the Runnable that should be started. Will be imported from the given module.
        :param kwargs: A dict (possibly as json-encoded string) that contains the parameter for the command's constructor"""

        assert isinstance(command, str)
        if isinstance(kwargs, str):
            kwargs = json.loads(kwargs)
        assert isinstance(kwargs, dict)

        logging.debug("%s.startRunnable(%s,%s)" % (self.hostid, command, kwargs))

        # Import module and create object
        moduleobj = importlib.import_module("actors." + importmodule)
        try:
            constructorobj = getattr(moduleobj, command)
            runnable = constructorobj(name=command, **kwargs)
        except AttributeError as ex:
            message = "%s.%s() does not exist: %s" % (moduleobj, command, ex)
            logging.error(message)
            raise NotImplementedError(message)

        # Start runnable in her own Thread
        thread = Thread(name="Runnable %s" % command, target=runnable.start, args=())
        thread.daemon = True
        thread.start()

        self.currentRunnables[command] = (runnable, thread)

    def stopRunnable(self, command="*"):
        """Stops the runnable representing the given command string. Does nothing if that runnable does not exist or is not running.
        :param command: Which runnable should be stopped. The same string as has been given to startRunnable(). Give * to stop all runnables."""
        if self.currentRunnables.has_key(command):
            logging.debug("%s.stopRunnable(%s)" % (self.hostid, command))
            runnable, thread = self.currentRunnables[command]
            runnable.stop()
            thread.join(timeout=3)
        elif command == "*":
            # Stop everything
            for runnable, thread in self.currentRunnables.values():
                runnable.stop()
                thread.join(timeout=3)
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
    # If a hostid is given
    if len(sys.argv) >= 2:
        # Create temporary file and get absolute path of it
        logfile = tempfile.mkstemp(prefix=sys.argv[1] + "_", suffix=".log")[1]
        # Write log to file and delete old logs
        logging.basicConfig(filename=logfile, filemode="w", **logging_config)
        handler = HostActionHandler(sys.argv[1])
    else:
        logging.basicConfig(**logging_config)
        handler = HostActionHandler()

    logging.debug("Host %s has been created" % handler.getID())

    server = createRPCServer(OverlordClient.Processor(handler))
    server.serve()