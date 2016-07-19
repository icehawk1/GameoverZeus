#!/usr/bin/env python2
# coding=UTF-8
import json, logging, os, random, requests, sys, time
from threading import Thread, Timer

from actors import BotCommands
from AbstractBot import AbstractBot
from resources import emu_config
from utils.MiscUtils import NetworkAddressSchema


class Bot(AbstractBot):
    """Implements a bot that, in regular intervals, fetches commands from the given CnC-Server
    and renews its registration with said server. The possible commands are defined in BotCommands.py."""

    def __init__(self, peerlist=[], **kwargs):
        AbstractBot.__init__(self, peerlist, probability_of_disinfection=0.1, **kwargs)
        self.current_command = None
        self.threads = []

    def performDuty(self):
        logging.debug("Doing my duties")
        # If there is a CnC-Server in the peerlist
        if len(self.peerlist) > 0:
            try:
                cncserver = random.choice(self.peerlist)
                self._registerWithCnCServer(cncserver)
                self._fetchCurrentCommand(cncserver)
                if self.current_command is not None:
                    self._executeCurrentCommand()
            except Exception as ex:
                logging.debug("Duty of bot %s failed with %s: %s" % (self.id, type(ex).__name__, ex))

    def _fetchCurrentCommand(self, cncserver):
        """Fetches a command from the CnC-Server and executes. This way the Botmaster can control the bots.
        The CnC-Server does not need to keep track of their addresses because they pull from it and reverse proxies
        can be used, so that the bots do not need to know the identity of the CnC-Server. """

        response = requests.get("http://%s:%s/current_command" % (cncserver, emu_config.PORT),
                                headers={"Accept": "application/json"})
        if response.status_code == 200:
            newCmd = json.loads(response.text)
            if newCmd != self.current_command:
                logging.debug("Replaced command %s with %s" % (self.current_command, newCmd))
            self.current_command = newCmd
        else:
            self.current_command = None

    def _executeCurrentCommand(self):
        """Executes the last command that has been fetched from the CnC-Server"""

        if isinstance(self.current_command, dict) and self.current_command.has_key("command") \
                and self.current_command["command"] != "":
            try:
                BotCommands.executeCurrentCommand(self.current_command)
            except TypeError as ex:
                logging.warning("Command %s got invalid parameters %s: %s"
                                % (self.current_command["command"], self.current_command["kwargs"], ex.message))

    def _registerWithCnCServer(self, cncserver):
        """Notifies the CnC-Server that this bot exists and is still operational."""

        response = requests.post("http://%s:%s/register" % (cncserver, emu_config.PORT),
                                 data={'id': self.id})
        if not response.text == "OK":
            logging.debug(
                "Registration of bot %s failed with %s: %s" % (self.id, response.status_code, response.text))

    def _sendOutRandomTraffic(self, probability):
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
            Timer(10, self._sendOutRandomTraffic, args=[probability]).start()

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
    itgsend_thread = Thread(name="ITGSend_thread", target=bot._sendOutRandomTraffic, args=(0.05,))
    itgsend_thread.start()

    time.sleep(235)
    bot.stop()
    logging.info("Bot is stopping")
