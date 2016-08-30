#!/usr/bin/env python2
# coding=UTF-8
import logging, random, time
import matplotlib

matplotlib.use('svg')
from matplotlib import pyplot
import pylab
import numpy
from resources.emu_config import logging_config

factor = 10


def createLinePlot(x, xlabel, y, ylabel, outputfile, title=None):
    """Creates a line plot.
    :param xlabel: Label on the x-axis
    :param ylabel: Label on the y-axis
    :type x: list of float
    :type xlabel: str
    :type y: list of float
    :type ylabel: str
    :type outputfile: str
    :param title: A title to be printed above the graph
    :type title: str"""

    pyplot.ioff()  # Ensure that matplotlib does not try to show a gui
    if title is not None: pyplot.title(title)
    pyplot.plot(numpy.array(x), numpy.array(y), label=None)
    pyplot.axvline(35, color="red")
    pyplot.axvline(25*factor, color="red")
    pyplot.xlabel(xlabel)
    pyplot.ylabel(ylabel)
    pylab.legend(loc='upper left')
    logging.debug("saving line plot to %s"%outputfile)
    pyplot.savefig(outputfile)
    pyplot.clf()  # Discard values of this figure, so we can start with a fresh one


def generateY(val):
    if val <= 35:
        return random.uniform(0, 0.5)
    elif val <= 10*factor:
        return random.uniform(0.25, 2)
    elif val <= 15*factor:
        return random.uniform(0.2, 1.5)
    elif val <= 30*factor:
        return random.uniform(0.15, 1)
    else:
        return random.uniform(0.01, 0.4)


if __name__ == '__main__':
    logging.basicConfig(**logging_config)

    x = [i for i in range(35*factor)]
    y = [generateY(i) for i in range(35*factor)]
    createLinePlot(x, "experiment runtime in seconds", y, "loading time in seconds", "/tmp/blubplot.svg")
