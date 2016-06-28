#!/usr/bin/env python2.7
# coding=UTF-8
import emu_config
from marshmallow import Schema, fields, post_load


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
