#!/usr/bin/env python2
# coding=UTF-8
from tornado.platform.twisted import TwistedIOLoop
from twisted.internet import reactor

TwistedIOLoop().install()

import logging, socket, time
from threading import Thread
import tornado.web

from actors.AbstractBot import CurrentCommandHandler
from resources import emu_config
from actors.ping.Client import Client


class Servent(Client):
    def __init__(self, peerlist, name="Servent", *args, **kwargs):
        super(Servent, self).__init__(name=name, peerlist=peerlist, *args, **kwargs)

    def start(self):
        """Implements start() from the superclass."""
        app = self.make_app()
        app.listen(emu_config.PORT)
        logging.debug("Start the ping.Servent %s on port %d"%(self.name, emu_config.PORT))
        super(Servent, self).start()

    def make_app(self):
        """Starts the web interface that is used to interact with this server."""
        handlers = [("/current_command", ServentCommandHandler)]
        return tornado.web.Application(handlers, autoreload=True)

    def errback(self, failure):
        """Given to defereds to report errors"""
        logging.warning("Kademlia Error in %s: %s"%(self.name, failure))


# noinspection PyAbstractClass
class ServentCommandHandler(CurrentCommandHandler):
    def __init__(self, *args, **kwargs):
        super(ServentCommandHandler, self).__init__(*args, **kwargs)

    @property
    def current_command(self):
        return self._current_command

    @current_command.setter
    def current_command(self, current_command):
        logging.info("Set command: %s"%current_command)
        self._current_command = current_command


if __name__ == '__main__':
    if __name__ == '__main__':
        logging.basicConfig(**emu_config.logging_config)

        logging.info("Servent direkt von der CLI")
        bot = Servent(peerlist=[])
        thread = Thread(name="Runnable KademliaBot", target=bot.start)
        thread.start()

        time.sleep(10)

        bot.stop()
