#!/usr/bin/env python2.7
# coding=UTF-8
"""Some utility functions related to mininet networks"""
import random

from marshmallow import Schema, fields, post_load

from resources import emu_config


class NetworkAddress(object):
    def __init__(self, host="localhost", port=emu_config.PORT):
        self.host = host
        self.port = port


class NetworkAddressSchema(Schema):
    host = fields.Str()
    port = fields.Int()

    @post_load
    def make_address(self, data):
        return NetworkAddress(**data)


def createRandomDPID():
    dpidLen = 16
    return ''.join([random.choice('0123456789ABCDEF') for x in range(dpidLen)])
