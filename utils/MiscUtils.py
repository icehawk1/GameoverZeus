#!/usr/bin/env python2
# coding=UTF-8
"""Some utility functions that fit nowhere else"""
import os, errno, random, logging
from marshmallow import Schema, fields, post_load
from datetime import datetime
import matplotlib
matplotlib.use('pdf')
from matplotlib import pyplot
import numpy

from resources import emu_config

#: Environment variable that contains the searchpath for python modules/packages. Needed for the imports in Host.py to work.
pypath = "PYTHONPATH=$PYTHONPATH:%s "%emu_config.basedir

def mkdir_p(path):
    """Creates all directories in this path that did not exist beforehand. Silently skips existing directories.
    (i.e. Behaves like mkdir -p in Linux.)"""
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class NetworkAddress(object):
    """A combination of host and port"""

    def __init__(self, host="localhost", port=emu_config.PORT):
        self.host = host
        self.port = port


class NetworkAddressSchema(Schema):
    """Needed to serialize a NetworkAddress using Marshmallow"""
    host = fields.Str()
    port = fields.Int()

    @post_load
    def make_address(self, data):
        return NetworkAddress(**data)

def datetimeToEpoch(datetimeObj):
    """Takes the given datetime object and returns the number of seconds since Epoch
    :return: A positive or negative integer"""
    return int((datetimeObj - datetime(1970, 1, 1)).total_seconds())


def createLinePlot(x, xlabel, y, ylabel, outputfile):
    """Creates a line plot.
    :param xlabel: Label on the x-axis
    :param ylabel: Label on the y-axis
    :type x: list of float
    :type xlabel: str
    :type y: list of float
    :type ylabel: str
    :type outputfile: str"""
    pyplot.ioff()  # Ensure that matplotlib does not try to show a gui
    pyplot.plot(numpy.array(x), numpy.array(y))
    pyplot.xlabel("experiment runtime in seconds")
    pyplot.ylabel('loading time in seconds')
    logging.debug("saving line plot to %s"%outputfile)
    pyplot.savefig(outputfile)
    pyplot.clf()  # Discard values of this figure, so we can start with a fresh one

def removeSuffixes(text, suffixes):
    """If text ends with one of the given suffixes, returns text without this suffix, else returns text unchanged
    :type text: str
    :type suffixes: list or str"""
    assert isinstance(text, str), "text has wrong type %s"%type(text)

    if isinstance(suffixes, str):
        if not text.endswith(suffixes) or len(suffixes) == 0:
            return text
        else:
            return text[:-len(suffixes)]
    elif isinstance(suffixes, list):
        for sfx in suffixes:
            if not len(sfx) == 0 and text.endswith(sfx):
                return text[:-len(sfx)]
        return text
    else:
        assert False, "suffixes has wrong type %s"%type(suffixes)


def createRandomDPID():
    """Creates one of those strange number mininet needs"""
    dpidLen = 16
    return ''.join([random.choice('0123456789ABCDEF') for x in range(dpidLen)])


def average(seq):
    """Computes the arithmetic mean over the given iterable. Returns 0 on an empty sequence.
    :type seq: Iterable of numbers"""
    if len(seq) > 0:
        return float(sum(seq))/len(seq)
    else:
        return 0  # Mathematically not true, but OK for our purposes
