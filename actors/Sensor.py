#!/usr/bin/env python2
# coding=UTF-8
"""This file implements a sensor node that can measure the loading time of a given webpage and prints a nice graph on shutdown."""
import logging, urllib, time, os, urlparse
from timeit import timeit

from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.python import log
from threading import Thread
from matplotlib import pyplot
import numpy

from AbstractBot import CommandExecutor
from resources.emu_config import logging_config
from utils.MiscUtils import mkdir_p


def measureLoadingTime(url):
    page = urllib.urlopen(str(url))
    start = time.time()
    page.read()
    end = time.time()
    page.close()

    return end - start


class Sensor(CommandExecutor):
    """Helper class to let this sensor be run in a thread"""

    def __init__(self, name="", pagesToWatch=[], outputdir="/tmp/loading_times"):
        """:param pagesToWatch: A list of URLs whose loading time shall be measured
        :param outputdir: Directory to store the resulting graphs"""
        CommandExecutor.__init__(self, name=name)
        self.loadingTimesDict = {page: [] for page in pagesToWatch}
        self.outputdir = outputdir
        self.pauseBetweenDuties = 0.5

    def performDuty(self):
        """Implements method from superclass"""
        n = 3
        times = []
        for page in self.loadingTimesDict.keys():
            loadTime = timeit(lambda: measureLoadingTime(page), number=n) / n
            self.loadingTimesDict[page].append(loadTime)
            times.append(loadTime)
        logging.debug("Calculated loading times for %s: %s" % (self.loadingTimesDict.keys(), times))

    def stop(self):
        """Writes graphs of all measured loading times to the outputdir. Implements method from superclass."""
        CommandExecutor.stop(self)

        mkdir_p(self.outputdir)  # Ensure outputdir exists
        pyplot.ioff()  # Ensure that matplotlib does not try to show a gui
        for page in self.loadingTimesDict.keys():
            pyplot.close()
            y = self.loadingTimesDict[page]
            x = [i for i in range(1, len(y) + 1)]
            pyplot.plot(numpy.array(x), numpy.array(y))
            pyplot.xlabel("time")
            pyplot.ylabel('loading time')

            outputfile = os.path.join(self.outputdir, urlparse.urlparse(page).hostname) + ".pdf"
            pyplot.savefig(outputfile)


if __name__ == "__main__":
    logging.basicConfig(**logging_config)
    sensor = Sensor("sensor", pagesToWatch=["http://heise.de", "https://www.google.com"])
    sensor.pauseBetweenDuties = 1
    thread = Thread(name="Runnable %s" % sensor.name, target=sensor.start)
    thread.start()

    time.sleep(12)
    sensor.stop()
    thread.join()
