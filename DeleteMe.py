#!/usr/bin/env python2
# coding=UTF-8
import time, logging
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.python import log
from threading import Thread

from actors.AbstractBot import Runnable
from resources.emu_config import logging_config


class Blub(Runnable):
    lc = None  # Responsible for the regular execution of performDuty()

    def start(self):
        logging.info("start stuff")
        observer = log.PythonLoggingObserver()
        observer.start()

        self.lc = LoopingCall(self.performDuty)
        lcDeferred = self.lc.start(0.1)
        lcDeferred.addErrback(self.errback)

        reactor.run(installSignalHandlers=0)

    def performDuty(self):
        logging.debug("Duty is calling")

    def stop(self):
        logging.debug("Stopping Blub")
        reactor.stop()
        logging.debug("reactor.stop() done")

    def errback(self, failure):
        logging.debug("error: %s" % failure)

    def cbLoopDone(self, result):
        """
        Called when loop was stopped with success.
        """
        logging.debug("Loop done.")


if __name__ == '__main__':
    logging.basicConfig(**logging_config)

    sensor = Blub("adsfsa")
    thread = Thread(name="Runnable %s" % sensor.name, target=sensor.start)
    thread.start()

    time.sleep(3)
    sensor.stop()
