#!/usr/bin/env python2
# coding=UTF-8
from tornado.platform.twisted import TwistedIOLoop
from twisted.internet import reactor
TwistedIOLoop().install()

import logging, time, os
from datetime import datetime
from threading import Thread
import tornado.web
import tornado.httpserver

from actors.AbstractBot import CurrentCommandHandler
from resources import emu_config
from actors.ping.Client import Client
from utils.MiscUtils import datetimeToEpoch

_current_command = {"command": "default_command", "timestamp": datetimeToEpoch(datetime.now()), "kwargs": dict()}

class Servent(Client):
    """Defines a Servent that provides a web interface to request new commands and also requests and executes
        new commands in regular intervals"""

    def __init__(self, peerlist, name="Servent", *args, **kwargs):
        """:param peerlist: The list of servents where this Servent requests new commands from"""
        super(Servent, self).__init__(name=name, peerlist=peerlist, *args, **kwargs)
        app = tornado.web.Application([("/current_command", ServentCommandHandler, {"servent": self})],
                                      autoreload=False)
        self.httpserver = tornado.httpserver.HTTPServer(app)

    def start(self):
        """Makes the webserver listen on the configured port. Implements start() from the superclass."""
        self.httpserver.listen(emu_config.PORT)
        logging.debug("Start the ping.Servent %s on port %d"%(self.name, emu_config.PORT))
        super(Servent, self).start()  # Do not execute this at the beginning, because it does not terminate

    def stop(self):
        self.httpserver.stop()
        super(Servent, self).stop()

    def errback(self, failure):
        """Given to defereds to report errors"""
        logging.warning("Servent Error in %s: %s"%(self.name, failure))

    @property
    def current_command(self):
        return _current_command

    @current_command.setter
    def current_command(self, current_command):
        global _current_command
        _current_command = current_command

# noinspection PyAbstractClass
class ServentCommandHandler(CurrentCommandHandler):
    """Handles HTTP GET and POST Requests for the current command for tornado"""

    def initialize(self, servent):
        self.servent = servent

    @property
    def current_command(self):
        return self.servent.current_command

    @current_command.setter
    def current_command(self, value):
        self.servent.current_command = value

if __name__ == '__main__':
    logging.basicConfig(**emu_config.logging_config)

    serventObj = Servent([])
    serventThread = Thread(target=serventObj.start)
    serventThread.start()

    time.sleep(2)
    os.system('wget -q -O - --post-data=\'command=joinParams&kwargs={"hello":"bla","hallo":"blub"}&timestamp=%d\' '
              'localhost:8080/current_command'%datetimeToEpoch(datetime.now()))
    time.sleep(2)
    os.system('wget -q -O - localhost:8080/current_command')
    time.sleep(2)

    serventObj.stop()
    serventThread.join()
