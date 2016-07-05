#!/usr/bin/env python2.7
# coding=UTF-8
import json
import logging
from blinker import signal
from threading import Thread
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application
from twisted.internet import reactor, defer
from twisted.names import dns, error, server

from resources import emu_config

"""This file implements a nameserver that can issue requests for an internal set of known domain names
 and register new domains via a web interface. """

known_hosts = {"heise.de": b"11.22.33.44", "lokaler_horst": b"127.0.0.1"}
rr_update_signal = signal("rr-update")


class DynamicResolver(object):
    """
    A resolver which calculates the answers to certain queries based on an internal dictionary
    """

    def __init__(self):
        rr_update_signal.connect(rrUpdate)

    def answerQuery(self, query, timeout=None):
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


@rr_update_signal.connect
def rrUpdate(sender, hostname="", address=""):
    """Updates the address of the given hostname"""

    known_hosts[hostname] = address
    logging.debug("Hostname %s is now known under address %s" % (hostname, address))


def runNameserver():
    """Run the DNS server."""
    logging.debug("Nameserver starts")
    factory = server.DNSServerFactory(
        clients=[DynamicResolver()]
    )
    protocol = dns.DNSDatagramProtocol(controller=factory)
    reactor.listenUDP(10053, protocol)
    reactor.run()
    signal("stop").send()


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

        rr_update_signal.send(self, hostname=hostname, address=address)
        self.write("OK")


def make_app():
    """Starts the web application"""

    return Application([
        ("/register-host", HostRegisterHandler),
    ], autoreload=True)


def runWebserver():
    """Run a webserver that allows to register additonal domain names.
    Helper method so that the server can run in its own thread."""
    logging.debug("Webserver starts")
    app = make_app()
    app.listen(emu_config.PORT)
    IOLoop.current().start()


def stopWebserver(sender):
    """Stops the webserver"""
    IOLoop.instance().stop()


if __name__ == '__main__':
    logging.basicConfig(format="%(threadName)s: %(message)s", level=logging.INFO)

    webthread = Thread(name="webserver_thread", target=runWebserver, args=())
    webthread.start()
    signal("stop").connect(stopWebserver)

    runNameserver()
