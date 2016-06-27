#!/usr/bin/env python2.7
# coding=UTF-8
import logging, random, time, os
from blinker import signal
from string import upper, lower
from threading import Thread, Timer
from tornado.httpclient import HTTPClient

from AbstractBot import AbstractBot


class Proxy(AbstractBot):
    def __init__(self, peerlist=[]):
        AbstractBot.__init__(self, peerlist)
        self.current_command = None

    def performDuty(self, args):
        if len(self.peerlist) > 0:
            response = http_client.fetch("http://%s:%s/current_command" % (random.choice(self.peerlist), PORT))
            assert "command" in lower(response.body)

            response = http_client.fetch("http://%s:%s/register" % (random.choice(self.peerlist), PORT),
                                         method='POST', body="id=%d" % self.id)
            assert "OK" in upper(response.body)


def executeProxy(bot):
    bot.start(pauseBetweenDuties=5)


if __name__ == "__main__":
    logging.basicConfig(format="%(threadName)s: %(message)s", level=logging.INFO)
    Timer(10.0, desinfect_thread).start()

    logging.info("Starting to mess things up")
    proxy = Proxy(peerlist=["localhost"])
    proxythread = Thread(name="cnc_comm_thread", target=executeProxy, args=(proxy,))
    proxythread.start()

    logging.info("Going to sleep now")
    time.sleep(35)
    logging.info("Everything messed up pretty thoroughly")
    signal("stop").send()
