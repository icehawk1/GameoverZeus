#!/usr/bin/env python2
# coding=UTF-8
"""This file implements a bot that uses the Kademlia protocol to receive and distribute commands."""
import tornado.platform.twisted

tornado.platform.twisted.install()
from twisted.internet import reactor
from twisted.python import log

import logging, random, string, json, socket, time
from threading import Thread
from kademlia.network import Server
import netifaces
import tornado.web
from tornado.ioloop import IOLoop

from actors.AbstractBot import Runnable
from resources import emu_config
from actors.BotCommands import executeCurrentCommand

iface_searchterm = "eth"


# noinspection PyAbstractClass
class CurrentCommandHandler(tornado.web.RequestHandler):
    """A handler that lets bots fetch the current command via HTTP GET and lets the botmaster issue a new command via
    HTTP POST."""

    current_command = {"command": "default_command", "kwargs": {}}

    # noinspection PyMethodOverriding,PyAttributeOutsideInit
    def initialize(self, kserver):
        self.kserver = kserver

    def get(self):
        if "json" in string.lower(self.request.headers.get("Accept")):
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps(self.current_command))
        else:
            self.set_header("Content-Type", "text/plain")
            if not self.current_command == {}:
                self.write(
                    "%s: %s"%(self.current_command["command"], " ".join(self.current_command["kwargs"].values())))

    def post(self):
        logging.debug(
            'Received POST: %s != %s == %s'%(self.get_body_argument("command"), self.current_command["command"],
                                             self.get_body_argument("command") != self.current_command["command"]))
        if self.get_body_argument("command") != self.current_command["command"]:
            # noinspection PyBroadException
            old_command = self.current_command
            try:
                self.current_command["command"] = self.get_body_argument("command")
                self.current_command["kwargs"] = json.loads(self.get_body_argument("kwargs"))
                logging.debug("The KademliaBot has received a new command: "%self.current_command)
                self.kserver.set("current_command", json.dumps(self.current_command)).addCallbacks(self._setSuccess,
                                                                                                   self._setFailure)
            except Exception as ex:
                # rolls the change back
                logging.warning("Command could not be applied: %s %s"%(ex, ex.message))
                self.current_command = old_command

        self.set_header("Content-Type", "text/plain")
        self.write("OK")

    def _setSuccess(self, result):
        logging.debug("Result of successful set command: %s"%result)

    def _setFailure(self, failure):
        logging.warning("Result of failed set command: %s"%failure)


# TODO: Use CommandExecutor instead of Runnable
class KademliaBot(Runnable):
    """Allows the KademliaBot to be run in its own thread."""

    def __init__(self, name="KademliaBot%d" % random.randint(1, 1000),
                 port=emu_config.kademlia_default_port, peerlist=[]):
        super(KademliaBot, self).__init__(name=name)
        self.kserver = Server()
        self.port = port
        self.peerlist = peerlist

    def start(self):
        """Implements start() from the superclass."""
        self._startTornado()
        self._startKademlia()
        try:
            IOLoop.current().start()
        except socket.error as ex:
            logging.warning("Could not start the KademliaBot: %s"%ex)

    def _startTornado(self):
        app = self.make_app()
        app.listen(emu_config.PORT)
        logging.debug("Start the KademliaBot %s on port %d"%(self.name, self.port))

    def make_app(self):
        """Starts the web interface that is used to interact with this server."""
        handlers = [("/current_command", CurrentCommandHandler, {"kserver": self.kserver})]
        return tornado.web.Application(handlers, autoreload=True)

    def _startKademlia(self):
        observer = log.PythonLoggingObserver()
        observer.start()

        possible_interfaces = [iface for iface in netifaces.interfaces() if iface_searchterm in iface
                               and netifaces.ifaddresses(iface).has_key(netifaces.AF_INET)]
        if len(possible_interfaces) == 0:
            logging.error("No suitable interfaces found, tried the following: %s"%netifaces.interfaces())
        logging.debug("Interfaces: %s"%netifaces.ifaddresses(possible_interfaces[0]))
        ipAddr = netifaces.ifaddresses(possible_interfaces[0])[netifaces.AF_INET][0]["addr"]
        logging.debug("Node %s starts with %s on %s"%(self.name, self.peerlist, ipAddr))

        self.kserver.listen(self.port, interface=ipAddr)
        serverDeferred = self.kserver.bootstrap([(peer, emu_config.kademlia_default_port) for peer in self.peerlist])
        serverDeferred.addCallback(self.executeBot)
        serverDeferred.addErrback(self.errback)

    def executeBot(self, peersfound=[]):
        """Method that is called regularly and checks for new commands"""
        self.kserver.get("current_command").addCallbacks(self.handleCommand, self.errback)
        if not self.stopthread:
            reactor.callLater(emu_config.botcommand_timeout, self.executeBot)

    def handleCommand(self, command):
        """If the bot received a new command, this method executes the command"""
        logging.debug("Got (new?) command: %s"%command)
        if command is not None:
            executeCurrentCommand(json.loads(command))

    def errback(self, failure):
        """Given to defereds to report errors"""
        logging.warning("Kademlia Error in %s: %s" % (self.name, failure))

    def stop(self):
        """Implements stop() from the superclass."""
        IOLoop.current().stop()

if __name__ == '__main__':
    logging.basicConfig(**emu_config.logging_config)

    iface_searchterm = "s0"
    logging.info("KademliaBot direkt von der CLI")
    bot = KademliaBot()
    thread = Thread(name="Runnable KademliaBot", target=bot.start)
    thread.start()

    time.sleep(10)

    bot.stop()
