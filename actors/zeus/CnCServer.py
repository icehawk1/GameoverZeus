#!/usr/bin/env python2
# coding=UTF-8
"""This file implements a CnC-Server that presents a web interface over which it can issue commands to clients
and keep track of clients that register themselves regularly with the server. A command may be any method that
is defined in BotCommands.py. This method will be executed by all clients that fetch it.
All handler support plain text and json output."""

import json, logging, string, sys, time, socket, os
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
import tornado.web
from threading import Thread
from tornado.ioloop import IOLoop
import tornado.httpserver

from actors.AbstractBot import Runnable, CurrentCommandHandler
from resources import emu_config
from utils.MiscUtils import NetworkAddressSchema, datetimeToEpoch

_current_command = {"command": "default_command", "timestamp": datetimeToEpoch(datetime.now()), "kwargs": dict()}

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
                       "/register where clients can register themselves so we can keep track of them."
                       "/current_command where clients can retrieve commands that they should execute")


# noinspection PyAbstractClass
class CnCCommandHandler(CurrentCommandHandler):
    """Handles HTTP GET and POST Requests for the current command for tornado"""

    @property
    def current_command(self):
        return _current_command

    @current_command.setter
    def current_command(self, value):
        global _current_command
        _current_command = value

class RegisterHandler(tornado.web.RequestHandler):
    """Bots can register via HTTP POST, the number of currently known clients can be retrieved via HTTP GET"""

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
        botid = self.get_body_argument("id")
        if self.registered_bots.has_key(botid):
            self.registered_bots[botid].last_seen = time.time()
        else:
            self.registered_bots[botid] = BotInformation(botid)
        self.write("OK")
        logging.debug("Bot %s has registered itself with the server" % botid)


class CnCServer(Runnable):
    """Allows the CnCServer to be run in its own thread."""

    def __init__(self, host="0.0.0.0", port=emu_config.PORT, **kwargs):
        Runnable.__init__(self, **kwargs)
        self.host = host
        self.port = port
        handlers = [("/", MainHandler), ("/register", RegisterHandler), ("/current_command", CnCCommandHandler)]
        app = tornado.web.Application(handlers, autoreload=False)
        self.httpserver = tornado.httpserver.HTTPServer(app)

    def start(self):
        """Implements start() from the superclass."""
        logging.debug("Start the CnCServer %s on %s:%d" % (self.name, self.host, self.port))
        try:
            self.httpserver.listen(self.port)
        except socket.error as ex:
            logging.error("Could not start the CnC-Server: %s"%ex)

    def stop(self):
        """Implements stop() from the superclass."""
        self.httpserver.stop()
        logging.debug("Stopping CnCServer %s on %s:%d" % (self.name, self.host, self.port))


if __name__ == "__main__":

    schema = NetworkAddressSchema()
    if len(sys.argv) >= 2:
        cncaddress = schema.loads(sys.argv[1]).data
        cncserver = CnCServer(port=cncaddress.port)
    else:
        cncserver = CnCServer()

    thread = Thread(name="Runnable %s" % cncserver.name, target=cncserver.start)
    thread.start()
