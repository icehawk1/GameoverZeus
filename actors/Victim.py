#!/usr/bin/env python2.7
# coding=UTF-8
"""This file implements a victim. A victim is a machine that randomly surfes the net and may fall prey to an attack by
a botnet. If it is attacked sucessfully it changes to a bot."""

import logging
import random
import tornado.web
from blinker import signal
from threading import Thread
from tornado.ioloop import IOLoop

from AbstractBot import AbstractBot

probability_of_infection = 0.5
victimid = random.randint(1, 1000)


def make_app():
    return tornado.web.Application([
    ], autoreload=True)


class Victim(AbstractBot):
    """Helper class to let this victim be run in a thread"""

    def __init__(self, name=""):
        Runnable.__init__(self, name)

    def start(self, port=8080):
        """Implements start() from the superclass."""
        print type(self)
        app = make_app()
        app.listen(port)
        IOLoop.current().start()

    def stop(self):
        """Implements stop() from the superclass."""
        IOLoop.current().stop()


if __name__ == "__main__":
    logging.basicConfig(format="%(threadName)s: %(message)s", level=logging.INFO)
    victim = Victim("victim1")
    thread = Thread(name="Runnable victim1", target=victim.start, args=(8081,))
    thread.start()
