#!/usr/bin/env python2
# coding=UTF-8
import dns.resolver
import logging, os
import time
import unittest
from tornado.httpclient import HTTPClient

from actors.nameserver import Nameserver, DNS_PORT, known_hosts

class GameoverTopologyTest(unittest.TestCase):
    """Tests whether the nameserver correctly answers requests and whether addresses can be updated."""

    @classmethod
    def setUpClass(cls):
        cls.dnsresolver = dns.resolver.Resolver(configure=False)
        cls.dnsresolver.nameservers = ['127.0.0.1']
        cls.dnsresolver.port = DNS_PORT

        cls.http_client = HTTPClient()

        cls.dns_server = Nameserver()
        cls.dns_server.start()
        time.sleep(1)
        os.system("netstat -tulpen|grep %d"%DNS_PORT)

    @classmethod
    def tearDownClass(cls):
        os.system("netstat -tulpen|grep %d"%DNS_PORT)
        cls.dns_server.stop()

    def setUp(self):
        known_hosts = {"heise.de": b"11.22.33.44", "lokaler_horst": b"127.0.0.1"}

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
