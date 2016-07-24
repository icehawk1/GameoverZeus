#!/usr/bin/env python2
# coding=UTF-8
"""Some utility functions that fit nowhere else"""
import os, errno, random
from mininet.net import Mininet
from mininet.node import Switch
from marshmallow import Schema, fields, post_load
from datetime import datetime

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
