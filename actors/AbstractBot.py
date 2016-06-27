#!/usr/bin/env python2.7
# coding=UTF-8
import logging, random, time, os
from abc import ABCMeta, abstractmethod
from blinker import signal
from threading import Timer


class Runnable(object):
    """A class that executes code, similar to the Java class of the same name"""
    __metaclass__ = ABCMeta

    def __init__(self):
        self.stopthread = False
        signal('stop').connect(self.stop)

    def start(self, pauseBetweenDuties=15, args=()):
        """Starts the runnable, so that it performs its duties"""
        logging.info("Started performing duties every %d seconds" % pauseBetweenDuties)

        while not self.stopthread:
            self.performDuty(args)
            time.sleep(pauseBetweenDuties)

    @abstractmethod
    def performDuty(self, args):
        """Does the actual work"""

    def stop(self, sender):
        logging.info("Catched stop signal from %s" % sender)
        self.stopthread = True


class AbstractBot(Runnable):
    """The abstract base class for all bots in the simulated botnets"""
    __metaclass__ = ABCMeta

    def __init__(self, peerlist=[], desinfect_timeout=10, prob=0):
        Runnable.__init__(self)
        self.peerlist = peerlist
        self.id = random.randint(1, 100000)
        desinfect_thread(desinfect_timeout, prob)


def desinfect_thread(timeout, probability_of_desinfection):
    if random.uniform(0, 1) <= probability_of_desinfection:
        os.execv("./Victim.py", ["useless"])
    else:
        Timer(timeout, desinfect_thread, args=[probability_of_desinfection]).start()


def executeBot(bot, pauseBetweenDuties):
    bot.start(pauseBetweenDuties=pauseBetweenDuties)
