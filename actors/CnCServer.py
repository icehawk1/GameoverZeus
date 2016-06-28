#!/usr/bin/env python2.7
# coding=UTF-8
import logging, time, string, json, sys
import tornado.web
from tornado.ioloop import IOLoop
from threading import Thread

from AbstractBot import Runnable
import emu_config
from utils.NetworkUtils import NetworkAddressSchema

def make_app():
    return tornado.web.Application([
        ("/", MainHandler),
        ("/register", RegisterHandler),
        ("/current_command", CurrentCommandHandler)
    ], autoreload=True)


class BotInformation(object):
    def __init__(self, botid):
        self.last_seen = time.time()
        self.botid = botid


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("I am a CnC server")


class CurrentCommandHandler(tornado.web.RequestHandler):
    def get(self):
        if "json" in string.lower(self.request.headers.get("Accept")):
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps({"command": "printParams", "kwargs": {"hallo": "welt", "hello": "world"}}))
        else:
            self.set_header("Content-Type", "text/plain")
            self.write("Command: hello there")


class RegisterHandler(tornado.web.RequestHandler):
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
