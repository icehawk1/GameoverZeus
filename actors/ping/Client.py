#!/usr/bin/env python2
# coding=UTF-8
import random, json, logging
from actors.AbstractBot import CommandExecutor
from actors.BotCommands import executeCurrentCommand, fetchCurrentCommand


class Client(CommandExecutor):
    def __init__(self, peerlist, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        self.peerlist = peerlist

    def performDuty(self):
        # If we know at least one servent
        if len(self.peerlist) > 0:
            try:
                servent = random.choice(self.peerlist)
                current_command = fetchCurrentCommand(servent)
                # Execute old command if no new command was fetched
                if current_command is not None:
                    self._executeCurrentCommand(current_command)
            except Exception as ex:
                logging.warning("Duty of bot %s failed with %s: %s"%(self.name, type(ex).__name__, ex))

    def _executeCurrentCommand(self, current_command):
        """Executes the last command that has been fetched from the Servent"""
        try:
            executeCurrentCommand(current_command)
        except TypeError as ex:
            logging.warning("Command %s got invalid parameters %s: %s"
                            %(current_command["command"], current_command["kwargs"], ex.message))
