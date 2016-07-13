#!/usr/bin/env python2
# coding=UTF-8
"""Some utility functions that fit nowhere else"""
import os, errno
import random

from marshmallow import Schema, fields, post_load

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
