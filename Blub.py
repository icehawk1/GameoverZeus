#!/usr/bin/env python2
# coding=UTF-8
from tornado.platform.twisted import TwistedIOLoop
from twisted.internet import reactor
TwistedIOLoop(reactor).install()
from twisted.internet.task import LoopingCall

import logging, time, os
from threading import Thread
from resources.emu_config import logging_config


def performDuty():
    logging.info("duty")


def errback(failure):
    logging.error(failure)

if __name__ == "__main__":
    logging.basicConfig(**logging_config)

    lc = LoopingCall(performDuty)
    lcDeferred = lc.start(0.5)
    lcDeferred.addErrback(errback)

    reactorThread = Thread(target=reactor.run, kwargs={"installSignalHandlers": 0})
    reactorThread.start()
    time.sleep(3)
    reactor.callFromThread(reactor.stop)

    #
    # newServent = Bla.NewServent()
    # regular = Bla.Regular("Regular")
    #
    # reactor.callFromThread(newServent.start)
    # time.sleep(3)
    # os.system("netstat -tulpen | grep 8888")
    # reactor.callFromThread(regular.start)
    # time.sleep(2)
    # print "newServent.stop"
    # reactor.callFromThread(newServent.stop)
    # time.sleep(1)
    # reactor.callFromThread(regular.stop)
    # os.system("netstat -tulpen | grep 8888")
    # reactor.callFromThread(reactor.stop)
    # print "reactor should have been stopped"
    #
