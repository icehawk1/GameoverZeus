#!/usr/bin/env python2
# coding=UTF-8
"""This file implements a nameserver that can issue requests for an internal set of known domain names
 and register new domains via a web interface. """

import json, time, logging, os
from threading import Thread
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application
from twisted.internet import reactor, defer
from twisted.names import dns, error, server

from resources import emu_config
from actors.AbstractBot import Runnable

known_hosts = {}


class DynamicResolver(object):
    """
    A resolver which calculates the answers to certain queries based on an internal dictionary
    """

    def query(self, query, timeout=None):
        """Calculate the response to the given DNS query."""

        requested_hostname = query.name.name
        logging.debug("Received query for %s" % requested_hostname)

        if known_hosts.has_key(requested_hostname):
            answer = dns.RRHeader(name=requested_hostname,
                                  payload=dns.Record_A(address=known_hosts[requested_hostname]))
            answers = [answer]
            authority = []
            additional = []
            return defer.succeed((answers, authority, additional))
        else:
            return defer.fail(error.DomainError())


def rrUpdate(hostname="", address=""):
    """Updates the address of the given hostname"""

    known_hosts[hostname] = address
    logging.debug("Hostname %s is now known under address %s" % (hostname, address))


def runNameserver(dnsport):
    """Run the DNS server.
    :param dnsport: The port on which to listen for dns requests"""

    logging.debug("Nameserver starts")
    factory = server.DNSServerFactory(
        clients=[DynamicResolver()]
    )
    protocol = dns.DNSDatagramProtocol(controller=factory)
    reactor.listenUDP(dnsport, protocol)
    # Allow reactor to be started from non-main thread
    reactor.run(installSignalHandlers=0)


def stopNameserver():
    reactor.callFromThread(reactor.stop)

class HostRegisterHandler(RequestHandler):
    """Allows the address of a given hostname to be set via HTTP POST and dumps all known domains on a HTTP GET"""

    registered_bots = dict()

    def get(self):
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(known_hosts))

    def post(self):
        self.set_header("Content-Type", "text/plain")
        hostname = self.get_body_argument("hostname")
        address = self.get_body_argument("address")

        rrUpdate(hostname, address)
        self.write("OK")


def make_app():
    """Starts the web application"""

    return Application([
        ("/register-host", HostRegisterHandler),
    ], autoreload=False)


def runWebserver():
    """Run a webserver that allows to register additonal domain names.
    Helper method so that the server can run in its own thread."""
    logging.debug("Webserver starts")
    app = make_app()
    app.listen(emu_config.PORT)
    IOLoop.current().start()


def stopWebserver():
    """Stops the webserver"""
    IOLoop.instance().stop()


class Nameserver(Runnable):
    """Runs a nameserver that answers dns queries on the given port and accepts new domains via a web interface."""

    def __init__(self, name=""):
        Runnable.__init__(self, name)

    def start(self, dnsport=10053):
        webthread = Thread(name="webserver_thread", target=runWebserver, args=())
        webthread.start()

        dnsthread = Thread(name="nameserver_thread", target=runNameserver, args=(dnsport,))
        dnsthread.start()

    def stop(self):
        stopWebserver()
        stopNameserver()
