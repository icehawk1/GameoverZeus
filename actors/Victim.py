#!/usr/bin/env python2.7
# coding=UTF-8
import logging, os, random, time
import tornado.ioloop
from blinker import signal
from threading import Thread
from tornado.web import RequestHandler

probability_of_infection = 0.5
victimid = random.randint(1, 1000)


def make_app():
    signal("got-infected").connect(replace_with_bot)
    return tornado.web.Application([
        ("/", MainHandler),
        ("/infect", InfectionHandler)
    ], autoreload=True)


class MainHandler(RequestHandler):
    def get(self):
        self.write("I am a victim")


class InfectionHandler(RequestHandler):
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
    time.sleep(2)
    os.execv("./Bot.py", args)


if __name__ == "__main__":
    logging.basicConfig(format="%(threadName)s: %(message)s", level=logging.INFO)
    logging.info("Victim started")

    app = make_app()
    app.listen(8081)
    tornado.ioloop.IOLoop.current().start()
