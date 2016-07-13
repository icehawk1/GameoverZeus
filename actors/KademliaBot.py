#!/usr/bin/env python2
# coding=UTF-8
"""This file implements a bot that uses the Kademlia protocol to receive and distribute commands."""

import logging, random
from twisted.internet import reactor
from kademlia.network import Server
from twisted.python import log
import netifaces

from actors.AbstractBot import Runnable
from resources import emu_config


class KademliaBot(Runnable):
    """Allows the KademliaBot to be run in its own thread."""

    def __init__(self, name="KademliaBot%d" % random.randint(1, 1000),
                 port=emu_config.kademlia_default_port, peerlist=[]):
        Runnable.__init__(self, name)
        self.kserver = Server()
        current_command = {"command": "default_command"}
        self.port = port
        self.peerlist = peerlist

    def start(self):
        """Implements start() from the superclass."""

        observer = log.PythonLoggingObserver()
        observer.start()

        possible_interfaces = [iface for iface in netifaces.interfaces() if "eth" in iface]
        logging.debug("Interfaces: %s" % possible_interfaces)
        iface = netifaces.ifaddresses(possible_interfaces[0])[2][0]['addr']
        logging.debug("Node %s starts with %s on %s" % (self.name, self.peerlist, iface))

        self.kserver.listen(self.port, interface=iface)
        serverDeferred = self.kserver.bootstrap([(peer, emu_config.kademlia_default_port) for peer in self.peerlist])
        serverDeferred.addCallback(self.executeBot)
        serverDeferred.addErrback(self.errback)

        # The argument is necessary to run the reactor outside the main thread
        reactor.run(installSignalHandlers=0)

    def executeBot(self, peersfound=[]):
        """Method that is called regularly and checks for new commands"""
        self.kserver.get("current_command").addCallbacks(self.executeCurrentCommand, self.errback)
        if not self.stopthread:
            reactor.callLater(emu_config.botcommand_timeout, self.executeBot)

    def executeCurrentCommand(self, result):
        """If the bot received a new command, this method executes the command"""
        logging.debug("Got new command: %s" % result)
        # TODO: Ein CommandExecutor-Modul erstellen und hier verwenden
        pass

    def errback(self, failure):
        """Given to defereds to report errors"""
        logging.warning("Kademlia Error in %s: %s" % (self.name, failure))

    def stop(self):
        """Implements stop() from the superclass."""
        reactor.stop()

if __name__ == '__main__':
    logging.basicConfig(**emu_config.logging_config)
    reactor.install()

    logging.info("KademliaBot direkt von der CLI")
    bot = KademliaBot()
    bot.start()
    bot.stop()
