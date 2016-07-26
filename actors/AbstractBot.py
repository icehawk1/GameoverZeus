#!/usr/bin/env python2
# coding=UTF-8
"""Defines abstract base classes for all kinds of clients"""
import logging
from abc import ABCMeta, abstractmethod
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.python import log

from resources import emu_config


class Runnable(object):
    """A class that executes code, similar to the Java class of the same name"""
    __metaclass__ = ABCMeta

    def __init__(self, name=""):
        self.stopthread = False
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
    """Executs a command every x seconds"""
    __metaclass__ = ABCMeta

    def __init__(self, pauseBetweenDuties=emu_config.botcommand_timeout, **kwargs):
        """:param pauseBetweenDuties: How long to wait between invocations of performDuty()"""
        super(CommandExecutor, self).__init__(**kwargs)
        self.pauseBetweenDuties = float(pauseBetweenDuties)
        self.lc = LoopingCall(self.performDuty)

    def start(self):
        """Starts the runnable, so that it regularly calls performDuty()"""
        logging.debug("Started performing duties every %d seconds" % self.pauseBetweenDuties)
        observer = log.PythonLoggingObserver()
        observer.start()

        lcDeferred = self.lc.start(float(self.pauseBetweenDuties))
        lcDeferred.addErrback(self.errback)

        reactor.run(installSignalHandlers=0)

    @abstractmethod
    def performDuty(self, *args, **kwargs):
        """Does the actual work. Is called regularly and should be implemented by subclasses."""

    def stop(self):
        """Stops performDuty() from being called"""
        logging.debug("Stopping %s" % self.name)
        self.stopthread = True
        if self.lc.running:
            self.lc.stop()
        if reactor.running:
            reactor.stop()

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
