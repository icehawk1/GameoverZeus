#!/usr/bin/env python2
# coding=UTF-8
"""This file implements a legitimate Kademlia User, who randomly sets and reads keys.
This is done to simulate normal operation, it does not actually do anything."""
from twisted.internet import reactor

import logging, random, socket
from kademlia.network import Server
import netifaces
from tornado.ioloop import IOLoop

from actors.AbstractBot import Runnable
from resources import emu_config
from utils.MiscUtils import generateRandomString

iface_searchterm = "eth"


class KademliaUser(Runnable):
    """Allows the KademliaUser to be run in its own thread."""

    def __init__(self, name="KademliaUser%d"%random.randint(1, 1000),
                 port=emu_config.kademlia_default_port, peerlist=None):
        super(KademliaUser, self).__init__(name=name)
        self.kademliaServer = Server()
        self.port = port
        self.peerlist = peerlist if peerlist is not None else []

    def start(self):
        """Implements start() from the superclass."""
        self._startKademlia()
        try:
            IOLoop.current().start()
        except socket.error as ex:
            logging.warning("Could not start the KademliaUser: %s"%ex)

    def _startKademlia(self):
        possible_interfaces = [iface for iface in netifaces.interfaces() if iface_searchterm in iface
                               and netifaces.ifaddresses(iface).has_key(netifaces.AF_INET)]
        if len(possible_interfaces) == 0:
            logging.error("No suitable interfaces found, tried the following: %s"%netifaces.interfaces())
        logging.debug("Interfaces: %s"%netifaces.ifaddresses(possible_interfaces[0]))
        ipAddr = netifaces.ifaddresses(possible_interfaces[0])[netifaces.AF_INET][0]["addr"]
        logging.debug("Node %s starts with %s on %s"%(self.name, self.peerlist, ipAddr))

        self.kademliaServer.listen(self.port, interface=ipAddr)
        serverDeferred = self.kademliaServer.bootstrap([(peer, emu_config.kademlia_default_port) for peer in self.peerlist])
        serverDeferred.addCallback(self.executeBot)
        serverDeferred.addErrback(self.errback)

    def executeBot(self, peersfound=None):
        """Method that is called regularly and checks for new commands"""
        self.kademliaServer.get(generateRandomString(length=2)).addCallbacks(self.ignoreInput, self.errback)
        self.kademliaServer.set(generateRandomString(length=2), generateRandomString()).addCallbacks(self.ignoreInput,
                                                                                                     self.errback)
        reactor.callLater(emu_config.botcommand_timeout, self.executeBot)

    def ignoreInput(self, *args, **kwargs):
        """Gets whatever is the result of the Kademlia GET request and ignores it"""
        pass

    def errback(self, failure, *args, **kwargs):
        """Given to defereds to report errors. Ignores those errors."""
        logging.debug(
            "Kademlia Error (for the legitimate user, so non-existing keys are not a problem) in %s: %s"%(self.name, failure))
        pass
