#!/usr/bin/env python2
# coding=UTF-8
"""This file implements a bot that uses the Kademlia protocol to receive and distribute commands."""

import logging, time, json
from tornado.ioloop import IOLoop
from tornado import web

from actors.AbstractBot import Runnable
from resources import emu_config


class MainHandler(web.RequestHandler):
    """Returns the current bots ID on HTTP GET"""

    def initialize(self, botid=0):
        self.botid = botid

    def get(self):
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps({"botid": self.botid}))


class KademliaBot(Runnable):
    """Allows the KademliaBot to be run in its own thread."""

    def __init__(self, name="KademliaBot", botid_of_parent=0):
        Runnable.__init__(self, name)
        self.botid = self._createBotid(botid_of_parent)

    def start(self, port=emu_config.PORT):
        """Implements start() from the superclass."""

        handlers = [("/", MainHandler, {"botid": self.botid}), ]
        app = web.Application(handlers, autoreload=True)
        app.listen(port)
        IOLoop.current().start()

    def stop(self):
        """Implements stop() from the superclass."""
        IOLoop.current().stop()

    def _createBotid(self, botid_of_parent):
        return 4


if __name__ == '__main__':
    print "KademliaBot"
    bot = KademliaBot()
    print long(9878)
    bot.start()
    bot.stop()
