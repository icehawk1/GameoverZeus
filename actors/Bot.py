#!/usr/bin/env python2.7
# coding=UTF-8
import logging, random, time, json, string
import blinker
# from blinker import signal
from threading import Thread
from AbstractBot import AbstractBot, executeBot
import Bot_Commands
import requests

PORT = 8080

class Bot(AbstractBot):
    def __init__(self, peerlist=[], name=""):
        AbstractBot.__init__(self, peerlist, name=name, probability_of_disinfection=0.1)
        self.current_command = None

    def performDuty(self, args):
        if len(self.peerlist) > 0:
            try:
                tmp = requests.get("http://%s:%s/current_command" % (random.choice(self.peerlist), PORT),
                                   headers={"Accept": "application/json"})
                response = json.loads(tmp.text)

                if isinstance(response, dict) and response.has_key("command"):
                    methodToCall = getattr(Bot_Commands, response["command"])
                    try:
                        methodToCall(**response["kwargs"])
                    except TypeError:
                        logging.warning(
                            "Kommand %s mit falschen argumenten aufgerufen: %s" % (
                            response["command"], response["kwargs"]))

                response = requests.post("http://%s:%s/register" % (random.choice(self.peerlist), PORT),
                                         data={'id': self.id})
                if not response.text == "OK":
                    logging.debug(
                        "Registration of bot %s failed with %s: %s" % (self.id, response.status_code, response.text))
            except requests.ConnectionError:
                logging.debug("Duty of bot %s failed" % (self.id))

if __name__ == "__main__":
    logging.basicConfig(format="%(threadName)s: %(message)s", level=logging.INFO)

    logging.info("Starting to mess things up")
    bot = Bot(peerlist=["localhost"])
    Thread(name="cnc_comm_thread", target=executeBot, args=(bot, 5)).start()

    time.sleep(35)
    blinker.signal("stop").send()
    logging.info("Everything messed up pretty thoroughly")
