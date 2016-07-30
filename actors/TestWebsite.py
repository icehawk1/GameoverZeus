#!/usr/bin/env python2
# coding=UTF-8
import logging, sys
import tornado.web
from threading import Thread
from tornado.ioloop import IOLoop
import tornado.httpserver

from actors.AbstractBot import Runnable
from resources import emu_config
from utils.MiscUtils import NetworkAddressSchema, NetworkAddress


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            self.set_header("Content-Type", "text/plain")
            root = int(self.get_argument('root', default="0"))
            self.write("The square of %d is %d" % (root, root ** 2))
        except ValueError as ex:
            self.write("This is not a number: %s" % self.get_argument('root', default="0"))


class DDoSHandler(tornado.web.RequestHandler):
    keydict = {"default": "no_param", "erster": "first", "zweiter": "second", "dritter": "third"}

    def get(self):
        self.set_header("Content-Type", "application/json")
        key = self.get_argument('key', default="default")
        if self.keydict.has_key(key):
            self.write('{"%s":"%s"}' % (key, self.keydict[key]))
        else:
            self.set_status(404, "No such key")
            self.write("No such key in %s" % self.keydict.keys())

    def post(self):
        key = self.get_argument('key', default=None)
        if key is None:
            self.write("Please provide one of the following keys: %s" % self.keydict.keys())
        elif self.keydict.has_key(key):
            self.write("OK")
        else:
            self.set_status(404, "No such key")
            self.write("No such key in %s" % self.keydict.keys())


class TestWebsite(Runnable):
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
        runable = TestWebsite("testwebsite", sys.argv[2], int(sys.argv[3]))
    else:
        runable = TestWebsite("testwebsite")

    thread = Thread(name="Runnable %s"%runable.name, target=runable.start)
    thread.start()
