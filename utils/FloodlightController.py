#!/usr/bin/env python2.7
# coding=UTF-8
from mininet.node import Controller
import time
import emu_config


class FloodlightController(Controller):
    """Custom Controller that starts and stops Floodlight with custom options"""
    floodlight = 'nohup /usr/bin/floodlight'

    def start(self):
        """Start Floodlight with standard config file"""
        self.cmd(self.floodlight, '-cf %s/resources/floodlight.conf  &' % emu_config.basedir)
        time.sleep(2)

    def stop(self):
        """Stop Floodlight"""
        self.cmd('kill %nohup')
