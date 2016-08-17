#!/usr/bin/env python2
# coding=UTF-8
import logging, sys, random
import tornado.web
from threading import Thread
import tornado.httpserver
from primefac import primefac

from actors.AbstractBot import Runnable
from resources import emu_config


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            self.set_header("Content-Type", "text/plain")
            root = int(self.get_argument('root', default="0"))
            self.write("The square of %d is %d" % (root, root ** 2))
        except ValueError as ex:
            self.write("This is not a number: %s" % self.get_argument('root', default="0"))


class DDoSHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            self.set_header("Content-Type", "text/plain")

            composite = int(self.get_argument('composite', default="9123456789012345678901456780")) + random.randint(1, 10000)
            # print composite
            primes = [str(p) for p in primefac(composite)]

            self.write("%d ="%composite)
            for p in primes:
                self.write(" * ".join(primes))
            self.write("\n")
        except ValueError as ex:
            self.set_status(400, "Parameter composite not valid")
            self.write("This is not a number: %s"%self.get_argument('composite', default="0"))


class Victim(Runnable):
    """Allows the Website to be run in its own thread."""

    def __init__(self, name="", host="0.0.0.0", port=emu_config.PORT):
        """:param host: The IP-Address on which to listen for incomming connections
        :param port: The Port on which to listen for incomming connections"""
        Runnable.__init__(self, name)
        self.host = host
        self.port = port
        handlers = [("/", MainHandler), ("/ddos_me", DDoSHandler)]
        self.httpserver = tornado.httpserver.HTTPServer(tornado.web.Application(handlers, autoreload=False))

    def start(self):
        """Implements start() from the superclass."""
        self.httpserver.listen(self.port, self.host)

    def stop(self):
        """Implements stop() from the superclass."""
        self.httpserver.stop()


if __name__ == "__main__":
    logging.basicConfig(**emu_config.logging_config)

    if len(sys.argv) >= 3:
        runable = Victim("testwebsite", sys.argv[2], int(sys.argv[3]))
    else:
        runable = Victim("testwebsite")

    thread = Thread(name="Runnable %s"%runable.name, target=runable.start)
    thread.start()
