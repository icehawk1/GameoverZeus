#!/usr/bin/env python2
# coding=UTF-8
"""This file implements a sensor. A sensor is a machine that randomly surfes the net and may fall prey to an attack by
a botnet. If it is attacked sucessfully it changes to a bot."""

import logging, os, random
import psutil
import tornado.web
from threading import Thread
from tornado.ioloop import IOLoop
import tornado.httpserver

from actors.AbstractBot import Runnable
from resources import emu_config

probability_of_infection = 0.5
victimid = random.randint(1, 1000)

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


class Victim(Runnable):
    """Helper class to let this sensor be run in a thread"""

    def __init__(self, name=""):
        Runnable.__init__(self, name)
        app = tornado.web.Application([("/ddos_me", DDoSHandler)], autoreload=False)
        self.httpserver = tornado.httpserver.HTTPServer(app)

    def start(self, port=emu_config.PORT):
        """Implements start() from the superclass."""
        logging.debug("processes listening on %d: %s"%(port, [(psutil.Process(con.pid).cmdline(), con.pid) for con in
                                                              psutil.net_connections() if con.laddr[1] == port]))
        self.httpserver.listen(port)

    def stop(self):
        """Implements stop() from the superclass."""
        self.httpserver.stop()


if __name__ == "__main__":
    logging.basicConfig(format="%(threadName)s: %(message)s", level=logging.INFO)
    victim = Victim("sensor")
    thread = Thread(name="Runnable sensor", target=victim.start, args=(8081,))
    thread.start()
