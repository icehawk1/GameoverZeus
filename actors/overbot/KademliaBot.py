#!/usr/bin/env python2
# coding=UTF-8
"""This file implements a bot that uses the Kademlia protocol to receive and distribute commands."""
import tornado.platform.twisted

tornado.platform.twisted.install()
from twisted.internet import reactor
from twisted.python import log

import logging, random, json, socket, time
from threading import Thread
from kademlia.network import Server
import netifaces
import tornado.web
from tornado.ioloop import IOLoop

from actors.AbstractBot import Runnable, CurrentCommandHandler
from resources import emu_config
from actors.BotCommands import executeCurrentCommand

iface_searchterm = "eth"

# noinspection PyAbstractClass
class KademliaCommandHandler(CurrentCommandHandler):
    def __init__(self, kserver, *args, **kwargs):
        super(KademliaCommandHandler, self).__init__(*args, **kwargs)
        self._current_command = {"command": "default_command", "kwargs": {}}
        self.kserver = kserver

    @property
    def current_command(self):
        return self._current_command

    @current_command.setter
    def current_command(self, current_command):
        self._current_command = current_command
        logging.debug("The KademliaBot has received a new command: "%self.current_command)
        self.kserver.set("current_command", json.dumps(self.current_command)) \
            .addCallbacks(self._setSuccess, self._setFailure)

    def _setSuccess(self, result):
        """Called when the Kademlia set command was successful"""
        logging.debug("Result of successful set command: %s"%result)

    def _setFailure(self, failure):
        """Called when the Kademlia set command has failed"""
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
        handlers = [("/current_command", KademliaCommandHandler, {"kserver": self.kserver})]
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
