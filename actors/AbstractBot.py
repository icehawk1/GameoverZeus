#!/usr/bin/env python2
# coding=UTF-8
"""Defines abstract base classes for all kinds of clients"""
import logging, string, json
from abc import ABCMeta, abstractmethod, abstractproperty
from twisted.internet.task import LoopingCall
from twisted.python import log
import tornado.web

from resources import emu_config


class Runnable(object):
    """A runnable is a class that encapsulates a process that can be run in its own thread and that can be started
    and stopped at any time. It was inspired by the Java standard library class with the same name."""
    __metaclass__ = ABCMeta

    def __init__(self, name=""):
        self.name = name
        self.processes = []  # A list of processes that can be stopped via terminate()

    @abstractmethod
    def start(self):
        """Starts the runnable so that it will perform its work. This may also be invoked by sending a start signal."""

    @abstractmethod
    def stop(self):
        """Stops the runnable so that it will not perform any further work until restartet.
        Its Thread may now safely be joined without the thread invoking join being blocked.
        This can alternatively be invoked by sending a stop signal."""


class CommandExecutor(Runnable):
    """Executes a method every x seconds"""
    __metaclass__ = ABCMeta

    def __init__(self, pauseBetweenDuties=emu_config.botcommand_timeout, **kwargs):
        """:param pauseBetweenDuties: How long to wait between invocations of performDuty() in seconds"""
        super(CommandExecutor, self).__init__(**kwargs)
        logging.debug("pause: %d, kwargs: %s"%(pauseBetweenDuties, kwargs))
        self.pauseBetweenDuties = float(pauseBetweenDuties)
        self.lc = LoopingCall(self.performDuty)

    def start(self):
        """Starts the runnable, so that it regularly calls performDuty()"""
        logging.debug("Started performing duties every %d seconds" % self.pauseBetweenDuties)
        observer = log.PythonLoggingObserver()
        observer.start()

        lcDeferred = self.lc.start(self.pauseBetweenDuties)
        lcDeferred.addErrback(self.errback)

    @abstractmethod
    def performDuty(self, *args, **kwargs):
        """Does the actual work. Is called regularly and should be implemented by subclasses."""

    def stop(self):
        """Stops performDuty() from being called"""
        logging.debug("Stopping %s" % self.name)
        if self.lc.running:
            self.lc.stop()


    def errback(self, failure):
        """Given to defereds to report errors"""
        logging.warning(
            "%s in %s: %s %s" % (failure.type, self.name, failure.getErrorMessage(), failure.getBriefTraceback()))

def executeBot(bot, pauseBetweenDuties):
    """Helper method for executing the bot in a new thread.
    :param bot: The bot that shall be started.
    :param pauseBetweenDuties: How long to wait between invocations of performDuty()"""
    assert isinstance(bot, Runnable)
    bot.start(pauseBetweenDuties=pauseBetweenDuties)


# noinspection PyAbstractClass, PyPropertyAccess
class CurrentCommandHandler(tornado.web.RequestHandler):
    """A handler that lets clients fetch the current command via HTTP GET and lets the botmaster issue a new command
    via HTTP POST."""
    __metaclass__ = ABCMeta

    @abstractproperty
    def current_command(self):
        pass

    @current_command.setter
    def current_command(self, prop):
        pass

    def get(self):
        """Returns the currently set command"""
        if "json" in string.lower(self.request.headers.get("Accept")):
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps(self.current_command))
        else:
            self.set_header("Content-Type", "text/plain")
            if len(self.current_command) > 0:
                self.write(
                    "%s: %s"%(self.current_command["command"], " ".join(self.current_command["kwargs"].values())))

    def post(self):
        """Changes the current command to the value given in the request body"""
        self.set_header("Content-Type", "text/plain")
        assert self.current_command is not None
        assert self.current_command.has_key("timestamp")

        try:
            # Note: Don't use self.current_command['key'] = value here, because the setter would not be invoked
            newCommand = {"command"  : self.get_body_argument("command"),
                          "timestamp": self.get_body_argument("timestamp"),
                          "kwargs"   : json.loads(self.get_body_argument("kwargs"))}
            if newCommand["timestamp"] > self.current_command["timestamp"]:
                logging.debug("newcommand: %s"%newCommand)
                self.current_command = newCommand
                self.write("OK")
            else:
                self.write("Command too old")
        except Exception as ex:
            # rolls the change back
            logging.warning("Command could not be applied: %s %s"%(ex, ex.message))
            self.set_status(400, "Command not accepted")
            self.write("Could not parse the body")
