#!/usr/bin/env python2
# coding=UTF-8
"""Starts and stops the Floodlight OpenFlow controller and enables its use in the Mininet() constructor"""
from mininet import node
import os
from resources import emu_config


class Controller(node.Controller):
    """Custom Controller that starts and stops Floodlight with custom options"""
    floodlight = 'nohup /usr/bin/floodlight'

    def start(self):
        """Start Floodlight with standard config file"""
        node.Controller.start(self)
        self.cmd(self.floodlight, '-cf %s/resources/floodlight.conf  &' % emu_config.basedir)

    def stop(self, *args, **kwargs):
        super(node.Controller, self).stop(*args, **kwargs)
        os.remove("./nohup.out")
