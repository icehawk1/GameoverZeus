#!/usr/bin/env python2.7
# coding=UTF-8
import unittest, subprocess, time, logging
import dns.resolver
from tornado.httpclient import HTTPClient


class GameoverTopologyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dnsresolver = dns.resolver.Resolver()
        cls.dnsresolver.nameservers = ['127.0.0.1']
        cls.dnsresolver.port = 10053

        cls.http_client = HTTPClient()

    def setUp(self):
        self.nameserver_proc = subprocess.Popen(["python", "nameserver.py"])
        time.sleep(3)

    def tearDown(self):
        self.nameserver_proc.terminate()
        time.sleep(1)

    def testResolveName(self):
        response = self.dnsresolver.query("lokaler_horst", "A")
        self.assertEquals(len(response), 1)
        self.assertEquals("127.0.0.1", response[0].to_text())

    def testChangeEntry(self):
        new_address = "127.1.2.3"

        response = self.http_client.fetch("http://%s:%s/register-host" % ("localhost", 8080),
                                          method='POST', body="hostname=lokaler_horst&address=%s" % new_address)
        self.assertEquals(int(response.code), 200)
        time.sleep(4)

        response = self.dnsresolver.query("lokaler_horst", "A")
        self.assertEquals(len(response), 1)
        self.assertEquals(new_address, response[0].to_text())


if __name__ == "__main__":
    logging.basicConfig(format="%(threadName)s: %(message)s", level=logging.INFO)
    unittest.main()
