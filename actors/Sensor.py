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

from AbstractBot import Runnable
from resources.emu_config import logging_config
from utils.MiscUtils import mkdir_p


def measureLoadingTime(url):
    page = urllib.urlopen(str(url))
    start = time.time()
    page.read()
    end = time.time()
    page.close()

    return end - start


class Sensor(Runnable):
    """Helper class to let this sensor be run in a thread"""

    def __init__(self, name="", pagesToWatch=[], outputdir="/tmp/loading_times"):
        """:param pagesToWatch: A list of URLs whose loading time shall be measured
        :param outputdir: Directory to store the resulting graphs"""
        Runnable.__init__(self, name)
        self.loadingTimesDict = {page: [] for page in pagesToWatch}
        self.outputdir = outputdir
        self.lc = None

    def start(self):
        observer = log.PythonLoggingObserver()
        observer.start()

        self.lc = LoopingCall(self.performDuty)
        lcDeferred = self.lc.start(0.1)
        lcDeferred.addErrback(self.errback)

        reactor.run(installSignalHandlers=0)

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
        self.lc.stop()
        reactor.stop()

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

    def errback(self, failure):
        """Given to defereds to report errors"""
        logging.warning("%s in %s: %s" % (failure.type, self.name, failure.getErrorMessage()))


if __name__ == "__main__":
    logging.basicConfig(**logging_config)
    sensor = Sensor("sensor", pagesToWatch=["http://heise.de", "https://www.google.com"])
    thread = Thread(name="Runnable %s" % sensor.name, target=sensor.start)
    thread.start()

    time.sleep(12)
    sensor.stop()
    thread.join()
