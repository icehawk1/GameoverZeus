#!/usr/bin/env python2
# coding=UTF-8
from actors.ping.Servent import Servent
import unittest
import requests
from resources import emu_config
from actors.AbstractBotTest import RunnableTest


class ServentTest(RunnableTest, unittest.TestCase):
    def setUp(self):
        super(ServentTest, self).setUp()
        self.assertTrue(isinstance(self.objectUnderTest, Servent),
                        msg="type(OUT)==%s"%type(self.objectUnderTest))

    def createObjectUnderTest(self):
        return Servent(peerlist=[])

    def verifyOUTisRunning(self):
        response = requests.get("http://localhost:%d/current_command"%emu_config.PORT)
        self.assertEqual(200, response.status_code)

    def verifyOUThasBeenRun(self):
        self.fail("We can't really test this yet")
