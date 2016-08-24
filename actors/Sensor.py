#!/usr/bin/env python2
# coding=UTF-8
"""This file implements a sensor node that can measure the loading time of a given webpage and prints a nice graph on shutdown."""
import logging, time, os, urlparse
from timeit import timeit
from datetime import datetime
import requests
from threading import Thread
import matplotlib
# Force matplotlib to not use any Xwindows backend. Needed to run the botnet emulator over SSH.
matplotlib.use('PDF')
from matplotlib import pyplot
import numpy

from AbstractBot import CommandExecutor
from resources.emu_config import logging_config
from utils.MiscUtils import mkdir_p, datetimeToEpoch
from utils.LogfileParser import writeLogentry, parseMachineReadableLogfile

def measureLoadingTime(url):
    try:
        start = time.time()
        response = requests.get(url, timeout=5)
        end = time.time()

        return end - start
    except requests.exceptions.Timeout:
        return -1

class Sensor(CommandExecutor):
    """Helper class to let this sensor be run in a thread"""

    def __init__(self, pagesToWatch=[], outputdir="/tmp/botnetemulator/sensor", **kwargs):
        """:param pagesToWatch: A list of URLs whose loading time shall be measured
        :param outputdir: Directory to store the resulting graphs
        :param pauseBetweenDuties: How long to wait between invocations of performDuty()"""

        # Use different default value for param
        if not kwargs.has_key("pauseBetweenDuties"):
            kwargs["pauseBetweenDuties"] = 0.1

        super(Sensor, self).__init__(**kwargs)
        self.outputdir = outputdir
        self.pagesToWatch = pagesToWatch

    def performDuty(self):
        """Implements method from superclass"""
        n = 3
        try:
            starttime = datetime.now()
            for page in self.pagesToWatch:
                loadTime = float(timeit(lambda: measureLoadingTime(page), number=n)/n)
                writeLogentry(runnable=type(self).__name__, message="%s %f"%(page, loadTime), timeissued=starttime)
        except Exception as ex:
            logging.warning("Measurement of the loading times failed with an %s: %s"%(type(ex).__name__, ex.message))

    def stop(self):
        """Writes graphs of all measured loading times to the outputdir. Implements method from superclass."""
        logging.debug("Stopping sensor")
        super(Sensor, self).stop()

        logging.debug("Starting collection of loading times")
        loadingTimesDict = self._collectLoadingTimes()

        self._createPlotOfLoadingTimes(loadingTimesDict)

    def _collectLoadingTimes(self):
        logentries = parseMachineReadableLogfile(runnable=type(self).__name__)
        result = {}
        for entry in logentries:
            splited = entry.message.split(" ")
            if not result.has_key(splited[0]):
                result[splited[0]] = []

            #: The time when this entry was made as given in the logfile
            logtimestamp = entry.entrytime
            #: The time it took to load the page
            pageloadTime = float(splited[1])
            result[splited[0]].append((logtimestamp, pageloadTime))

#        logging.debug("Measured the following loading times: %s" % result)
        return result

    def _createPlotOfLoadingTimes(self, loadingTimesDict):
        """Creates a pdf file that shows a plot with the relative time when a page load began on the x-axis
        and the time taken to complete the page load on the y-axis. Page load means that this sensor loads a web page
        from a web server and measures how long this takes."""
        mkdir_p(self.outputdir)  # Ensure outputdir exists

        pyplot.ioff()  # Ensure that matplotlib does not try to show a gui
        for page in loadingTimesDict.keys():
            pyplot.close()

            raw_x = [datetimeToEpoch(tuple[0]) for tuple in loadingTimesDict[page]]
            raw_min = min(raw_x)
            x = [x - raw_min for x in raw_x]
            y = [tuple[1] for tuple in loadingTimesDict[page]]
            logging.debug("len(x) = %d"%len(x))
            logging.debug("len(y) = %d"%len(y))

            pyplot.plot(numpy.array(x), numpy.array(y))
            pyplot.xlabel("time")
            pyplot.ylabel('loading time')

            outputfile = os.path.join(self.outputdir, urlparse.urlparse(page).hostname) + ".pdf"
            pyplot.savefig(outputfile)


if __name__ == "__main__":
    logging.basicConfig(**logging_config)
    sensor = Sensor(name="sensor", pagesToWatch=["http://heise.de", "https://www.google.com"])
    sensor.pauseBetweenDuties = 1
    thread = Thread(name="Runnable %s" % sensor.name, target=sensor.start)
    thread.start()

    time.sleep(12)
    sensor.stop()
    thread.join()
