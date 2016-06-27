#!/usr/bin/env python2.7
# coding=UTF-8
import logging, time, string, json
import tornado.ioloop
from tornado.web import RequestHandler


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


class MainHandler(RequestHandler):
    def get(self):
        self.write("I am a CnC server")


class CurrentCommandHandler(RequestHandler):
    def get(self):
        if "json" in string.lower(self.request.headers.get("Accept")):
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps({"command": "printParams", "kwargs": {"hallo": "welt", "hello": "world"}}))
        else:
            self.set_header("Content-Type", "text/plain")
            self.write("Command: hello there")


class RegisterHandler(RequestHandler):
    registered_bots = dict()

    def get(self):
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
        logging.info("Bot %s has registered itself with the server" % botid)


if __name__ == "__main__":
    logging.basicConfig(format="%(threadName)s: %(message)s", level=logging.INFO)
    app = make_app()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
