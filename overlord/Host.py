#!/usr/bin/env python2
# coding=UTF-8
"""This file implements a script that can run any Runnable in a separate Thread. It can start and stop it any time.
It is intended to be run on every mn host to help the architecture being flexible and to allow the overlord to
control all hosts."""
from tornado.platform.twisted import TwistedIOLoop
from twisted.internet import reactor, threads

TwistedIOLoop().install()
from twisted.python import log

import logging, json, os, importlib, time, sys, socket, tempfile
from threading import Thread
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket, TTransport

from HostActions import OverlordClient
from resources.emu_config import SOCKET_DIR, logging_config


class HostActionHandler(object):
    """Handles RPC calls from the overlord. Implements the methods defined in HostActions.thrift ."""

    def __init__(self, hostid):
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

        logging.debug("%s.startRunnable(%s,%s)"%(self.hostid, command, kwargs))

        # Import module and create object
        moduleobj = importlib.import_module("actors." + importmodule)
        try:
            if not kwargs.has_key("name"):
                kwargs["name"] = command
            constructorobj = getattr(moduleobj, command)
            runnable = constructorobj(**kwargs)
        except AttributeError as ex:
            message = "%s.%s() does not exist: %s" % (moduleobj, command, ex)
            logging.error(message)
            raise NotImplementedError(message)

        # Start runnable in her own Thread
        defer = threads.deferToThread(runnable.start)
        self.currentRunnables[command] = (runnable, defer)

    def stopRunnable(self, command="*"):
        """Stops the runnable representing the given command string. Does nothing if that runnable does not exist or is not running.
        :param command: Which runnable should be stopped. The same string as has been given to startRunnable(). Give * to stop all runnables."""
        if self.currentRunnables.has_key(command):
            logging.debug("%s.stopRunnable(%s)" % (self.hostid, command))
            runnable, defer = self.currentRunnables[command]
            threads.blockingCallFromThread(reactor, runnable.stop)
            # runnable.stop()
            if not defer.called:
                defer.cancel()
        elif command == "*":
            # Stop everything
            for runnable, defer in self.currentRunnables.values():
                threads.blockingCallFromThread(reactor, runnable.stop)
                # runnable.stop()
                if not defer.called:
                    defer.cancel()
        else:
            logging.debug("Runnable %s not found" % command)

    def getID(self):
        """Returns the host id"""
        return self.hostid


def createRPCServer(processor):
    """Creates RPC server that is configured to listen on a socket in SOCKET_DIR
    :param processor: Thrift Processor that will handle incoming RPC calls"""

    # Clean up sockets from earlier launches
    if os.path.exists(SOCKET_DIR) and not os.path.isdir(SOCKET_DIR):
        os.remove(SOCKET_DIR)
        os.mkdir(SOCKET_DIR)

    socketFile = SOCKET_DIR + str(handler.getID())
    if os.path.exists(socketFile):
        os.remove(socketFile)

    logging.debug("Opening socket %s" % socketFile)
    serversocket = socket.socket(socket.AF_UNIX)
    serversocket.bind(socketFile)

    transport = TSocket.TServerSocket(unix_socket=socketFile)
    # We need buffering for performance reasons
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    result = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    return result


if __name__ == '__main__':
    assert len(sys.argv) >= 2, "Please provide a HostID"

    # Create temporary file and get absolute path of it
    logfile = tempfile.mkstemp(prefix=sys.argv[1] + "_", suffix=".log")[1]
    # Write log to file and delete old logs
    logging.basicConfig(filename=logfile, filemode="w", **logging_config)
    handler = HostActionHandler(sys.argv[1])

    # Start Twisted reactor
    observer = log.PythonLoggingObserver()
    observer.start()
    logging.info("Start Host %s"%sys.argv[1])
    reactorThread = Thread(target=reactor.run, kwargs={"installSignalHandlers": 0})
    reactorThread.start()
    time.sleep(1)
    assert reactor.running

    # Start RPC server for communicating with the Overlord
    server = createRPCServer(OverlordClient.Processor(handler))
    server.serve()

    logging.info("Stopping Host %s"%sys.argv[1])
    reactor.callFromThread(reactor.stop)
