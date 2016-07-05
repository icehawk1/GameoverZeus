#!/usr/bin/env python2.7
# coding=UTF-8
"""This file implements a victim. A victim is a machine that randomly surfes the net and may fall prey to an attack by
a botnet. If it is attacked sucessfully it changes to a bot."""

import logging
import os
import random
import time
import tornado.web
from blinker import signal
from threading import Thread
from tornado.ioloop import IOLoop

from AbstractBot import Runnable
from resources import emu_config

probability_of_infection = 0.5
victimid = random.randint(1, 1000)


def make_app():
    signal("got-infected").connect(replace_with_bot)
    return tornado.web.Application([
        ("/infect", InfectionHandler)
    ], autoreload=True)


class InfectionHandler(tornado.web.RequestHandler):
    """Handles an infection attempt and lets this attempt be successful with a predefined probability"""
    registered_bots = dict()

    def get(self):
        self.set_header("Content-Type", "text/plain")
        self.write("Not yet infected")

    def post(self):
        self.set_header("Content-Type", "text/plain")
        if random.uniform(0, 1) <= probability_of_infection:
            logging.info("Victim %d has been infected" % victimid)
            # Use a separate Thread for replacing this process, so that Tornado has time to finish the HTTP communication
            botthread = Thread(name="cnc_comm_thread", target=replace_with_bot, args=(["useless"],))
            botthread.start()
        else:
            logging.info("Victim %d has managed to evade infection" % victimid)


def replace_with_bot(args):
    """Replaces this whole process including all threads that have bin started by a newly spawned bot."""
    time.sleep(2)
    os.execv(emu_config.basedir + "/actors/Bot.py", args)


class Victim(Runnable):
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
