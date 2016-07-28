#!/usr/bin/env python2
# coding=UTF-8
"""This file runs a reverse proxy for the web application on the address given on the command line"""

import logging
import subprocess

from actors.AbstractBot import Runnable


class Proxy(Runnable):
    def __init__(self, name=""):
        Runnable.__init__(self, name)

    def start(self, proxyport=8080, cnchost=None, cncport=8080):
        command = "mitmdump -q --anticache -p %s -R 'http://%s:%s/' " % (proxyport, cnchost, cncport)
        logging.debug(command)
        mitmproc = subprocess.Popen(command)
        self.processes.append(mitmproc)

    def stop(self):
        logging.debug("Stop processes: %s" % [proc.pid for proc in self.processes])
        for proc in self.processes:
            proc.terminate()
