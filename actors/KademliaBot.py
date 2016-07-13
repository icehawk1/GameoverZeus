#!/usr/bin/env python2
# coding=UTF-8
"""This file implements a bot that uses the Kademlia protocol to receive and distribute commands."""

import logging, time, json

from actors.AbstractBot import Runnable
from resources import emu_config

class KademliaBot(Runnable):
    """Allows the KademliaBot to be run in its own thread."""

    def __init__(self, name="KademliaBot"):
        Runnable.__init__(self, name)

    def start(self, port=emu_config.PORT):
        """Implements start() from the superclass."""
        pass

    def stop(self):
        """Implements stop() from the superclass."""


if __name__ == '__main__':
    print "KademliaBot"
    bot = KademliaBot()
    bot.start()
    bot.stop()
