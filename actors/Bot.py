#!/usr/bin/env python2.7
# coding=UTF-8
import blinker
import json
import logging
import os
import random
import requests
import sys
import time
from threading import Thread, Timer

import Bot_Commands
from AbstractBot import AbstractBot
from resources import emu_config
from utils.NetworkUtils import NetworkAddressSchema


class Bot(AbstractBot):
    """Implements a bot that, in regular intervals, fetches commands from the given CnC-Server
    and renews its registration with said server. The possible commands are defined in Bot_Commands.py."""

    def __init__(self, peerlist=[], name=""):
        AbstractBot.__init__(self, peerlist, name=name, probability_of_disinfection=0.1)
        self.current_command = None
        self.threads = []

    def performDuty(self, args):
        # If there is a CnC-Server in the peerlist
        if len(self.peerlist) > 0:
            try:
                cncserver = random.choice(self.peerlist)
                self.fetchCurrentCommand(cncserver)
                self.registerWithCnCServer(cncserver)
                self.executeCurrentCommand()
            except requests.ConnectionError:
                logging.debug("Duty of bot %s failed" % self.id)

    def fetchCurrentCommand(self, cncserver):
        """Fetches a command from the CnC-Server and executes. This way the Botmaster can control the bots.
        The CnC-Server does not need to keep track of their addresses because they pull from it and reverse proxies
        can be used, so that the bots do not need to know the identity of the CnC-Server. """

        response = requests.get("http://%s:%s/current_command" % (cncserver, emu_config.PORT),
                                headers={"Accept": "application/json"})
        if response.status_code == 200:
            self.current_command = json.loads(response.text)

    def executeCurrentCommand(self):
        """Executes the last command that has been fetched from the CnC-Server"""

        if isinstance(self.current_command, dict) and self.current_command.has_key("command") \
                and self.current_command["command"] != "":
            methodToCall = getattr(Bot_Commands, self.current_command["command"])
            try:
                methodToCall(**self.current_command["kwargs"])
            except TypeError:
                logging.warning("Command %s got invalid parameters: %s"
                                % (self.current_command["command"], self.current_command["kwargs"]))

    def registerWithCnCServer(self, cncserver):
        """Notifies the CnC-Server that this bot exists and is still operational."""

        response = requests.post("http://%s:%s/register" % (cncserver, emu_config.PORT),
                                 data={'id': self.id})
        if not response.text == "OK":
            logging.debug(
                "Registration of bot %s failed with %s: %s" % (self.id, response.status_code, response.text))

    def sendOutRandomTraffic(self, probability):
        """Sends random traffic to a random host to generate noise in the network.
        ITGSend (belongs to D-ITG) is a traffic generator that sends out random traffic.
        It is able to simulate various application of which one is randomly chosen."""

        simulated_apps = ["Telnet", "DNS", "Quake3", "CSa", "CSi", "VoIP -x G.723.1", "VoIP -h CRTP -VAD G.711.2"]
        known_ips = ["localhost"]
        if random.uniform(0, 1) < probability:
            # We can ignore the log files, because we are just using the traffic as noise
            os.system(
                "ITGSend -a %s -l /dev/null -x /dev/null %s" % (
                random.choice(known_ips), random.choice(simulated_apps)))

        if not bot.stopthread:
            Timer(10, self.sendOutRandomTraffic, args=[probability]).start()

if __name__ == "__main__":
    logging.basicConfig(format="%(threadName)s: %(message)s", level=logging.INFO)

    logging.info("Bot is starting")
    schema = NetworkAddressSchema()
    peerlist = [schema.loads(sys.argv[i]).data.host for i in range(1, len(sys.argv))]
    bot = Bot(peerlist=peerlist)

    # Start listening for incoming D-ITG traffic
    itgrecvThread = Thread(name="ITGRecv_thread", target=bot.listenForIncomingNoiseTraffic, args=())
    itgrecvThread.start()
    # Start sending out traffic to random ips
    itgsend_thread = Thread(name="ITGSend_thread", target=bot.sendOutRandomTraffic, args=(0.05,))
    itgsend_thread.start()

    time.sleep(235)
    blinker.signal("stop").send()
    logging.info("Bot is stopping")
