#!/usr/bin/python
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


class Proxy(BotnetComponent):
    def __init__(self, hostinstance, cncserver):
        """
        :type hostinstance: Host
        :type cncserver: CnCServer
        """
        assert isinstance(hostinstance, Host)
        assert isinstance(cncserver, CnCServer)
        self.hostinstance = hostinstance
        self.cncserver = cncserver

    def start(self):
        self.hostinstance.cmd(
            'mitmdump -p 8000 -q --anticache -R "http://%s:8000" &' % self.cncserver.hostinstance.IP())

    def stop(self):
        self.hostinstance.cmd("kill %mitmdump")


class CnCServer(BotnetComponent):
    def __init__(self, hostinstance):
        """:type hostinstance: Host"""
        assert isinstance(hostinstance, Host)
        self.hostinstance = hostinstance

    def start(self):
        self.hostinstance.cmd('python -m SimpleHTTPServer 8000 &')

    def stop(self):
        self.hostinstance.cmd("kill %python")
