#!/usr/bin/python
# coding=UTF-8
import random
from abc import ABCMeta, abstractmethod
from mininet.node import Host


class BotnetComponent(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def start(self):
        """Starts the BotnetComponent, so that it is operational"""

    @abstractmethod
    def stop(self):
        """Stops operation of this component and cleans up everything"""


class Bot(BotnetComponent):
    peerlist = []

    def __init__(self, hostinstance):
        """
        :type hostinstance: Host
        """
        assert isinstance(hostinstance, Host)
        self.hostinstance = hostinstance

    def start(self):
        pass

    def stop(self):
        pass


class Proxy(Bot):
    def __init__(self, hostinstance):
        """
        :type hostinstance: Host
        """
        Bot.__init__(self, hostinstance)

    def start(self):
        assert len(self.peerlist) > 0
        cncserver = random.choice(self.peerlist)
        self.hostinstance.cmd(
            'mitmdump -p 8000 -q --anticache -R "http://%s:8000" &' % cncserver.hostinstance.IP())

    def stop(self):
        self.hostinstance.cmd("kill %mitmdump")


class CnCServer(Bot):
    def __init__(self, hostinstance):
        """:type hostinstance: Host"""
        Bot.__init__(self, hostinstance)

    def start(self):
        self.hostinstance.cmd('python -m SimpleHTTPServer 8000 &')

    def stop(self):
        self.hostinstance.cmd("kill %python")
