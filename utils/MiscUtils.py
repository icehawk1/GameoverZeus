#!/usr/bin/env python2
# coding=UTF-8
"""Some utility functions that fit nowhere else"""
import os, errno, random, sys, re, shlex
from subprocess import Popen, PIPE
import validators
from mininet.net import Mininet
from mininet.node import Switch
from marshmallow import Schema, fields, post_load
from datetime import datetime
from matplotlib import pyplot
import numpy

from resources import emu_config

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


def createRandomDPID():
    """Creates one of those strange number mininet needs"""
    dpidLen = 16
    return ''.join([random.choice('0123456789ABCDEF') for x in range(dpidLen)])


def addHostToMininet(mn, switch, hostname, overlord, **linkopts):
    """Creates a new host in the mininet network that is connected to the given switch and to the overlord"""
    assert isinstance(mn, Mininet)
    assert isinstance(switch, Switch)
    assert isinstance(hostname, str)

    result = mn.addHost(hostname, dpid=createRandomDPID())
    overlord.addHost(result.name)
    link = mn.addLink(result, switch)
    link.intf1.config(**linkopts)
    link.intf2.config(**linkopts)
    return result


def datetimeToEpoch(datetimeObj):
    """Takes the given datetime object and returns the number of seconds since Epoch
    :return: A positive or negative integer"""
    return int((datetimeObj - datetime(1970, 1, 1)).total_seconds())

def createLoadtimePlot(x,y,outputfile):
    """Writes a pdf to the given path that contains a plot of the given values.
    :param x: The values of the X-Axis
    :param y: The values on the Y-Axis
    :param outputfile: Where the plot should be written to."""
    assert len(x) == len(y)

    pyplot.ioff()  # Ensure that matplotlib does not try to show a gui
    pyplot.plot(numpy.array(x), numpy.array(y))
    pyplot.xlabel("time")
    pyplot.ylabel('loading time')
    pyplot.savefig(outputfile)


def createTcpResetPlot(pcapfile, outputfile="/tmp/resetsVsTime.pdf"):
    """Creates a pdf file that contains a plot that shows how many packets
    with TCP reset flag are seen every second in the given pcap file.
    :param pcapfile: The file containing the network traffic dump to analyse
    :param outputfile: Where the plot should be written to."""
    pathRE = "[\w-/]+"
    assert re.match(pathRE, pcapfile) and os.path.isfile(pcapfile)
    assert re.match(pathRE, outputfile)

    proc = Popen(shlex.split('tshark -r %s "tcp.flags.reset == 1"'%pcapfile))
    stdout, stderr = proc.communicate()

    data = {}
    for line in stdout.splitlines():
        match = re.search("\d+\s+(\d+)\.*\d*\s+[\d.]+ -> [\d.]+.*\[RST.*", line)
        if match:
            tick = int(match.group(1))
            if data.has_key(tick):
                data[tick] += 1
            else:
                data[tick] = 1

    maxkey = max(data.keys())
    x = [tick for tick in range(maxkey)]
    y = [data[tick] if data.has_key(tick) else 0 for tick in range(maxkey)]

    createLoadtimePlot(x, y, outputfile)


def average(seq):
    """Computes the arithmetic mean over the given iterable. Returns 0 on an empty sequence.
    :type seq: Iterable of numbers"""
    if len(seq) > 0:
        return float(sum(seq))/len(seq)
    else:
        return 0  # Mathematically not true, but OK for our purposes
