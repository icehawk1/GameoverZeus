#!/usr/bin/env python2.7
# coding=UTF-8
import dns.resolver
import logging
import subprocess
import time
import unittest
from tornado.httpclient import HTTPClient

from resources import emu_config


class GameoverTopologyTest(unittest.TestCase):
    """Tests whether the nameserver correctly answers requests and whether addresses can be updated."""

    @classmethod
    def setUpClass(cls):
        cls.dnsresolver = dns.resolver.Resolver(configure=False)
        cls.dnsresolver.nameservers = ['127.0.0.1']
        cls.dnsresolver.port = 10053

        cls.http_client = HTTPClient()

    def setUp(self):
        self.nameserver_proc = subprocess.Popen(["python", emu_config.basedir + "/actors/nameserver.py"])
        time.sleep(3)

    def tearDown(self):
        self.nameserver_proc.terminate()
        time.sleep(1)

    def testResolveName(self):
        """Tests if a request for a previously known hostname is answered correctly"""

        response = self.dnsresolver.query("lokaler_horst", "A")

        self.assertEquals(len(response), 1)
        self.assertEquals("127.0.0.1", response[0].to_text())

    def testChangeEntry(self):
        """Tests updating an address and then fetching the updated address"""

        new_address = "127.1.2.3"

        response = self.http_client.fetch("http://%s:%s/register-host" % ("localhost", 8080),
                                          method='POST', body="hostname=lokaler_horst&address=%s" % new_address)
        self.assertEquals(int(response.code), 200)
        time.sleep(4)

        response = self.dnsresolver.query("lokaler_horst", "A")
        self.assertEquals(len(response), 1)
        self.assertEquals(new_address, response[0].to_text())


if __name__ == "__main__":
    logging.basicConfig(format="%(threadName)s: %(message)s", level=logging.DEBUG)
    unittest.main()
