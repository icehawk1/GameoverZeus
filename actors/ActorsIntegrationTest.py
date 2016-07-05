#!/usr/bin/env python2.7
# coding=UTF-8
import json
import requests
import subprocess
import tempfile
import time
import unittest

from resources import emu_config
from utils.NetworkUtils import NetworkAddress, NetworkAddressSchema


class ActorsIntegrationTest(unittest.TestCase):
    """Tests if the different classes in this module work well together."""

    def setUp(self):
        """Starts two bots, one proxy and one CnC-Server"""

        schema = NetworkAddressSchema()
        serialized_cncaddress = schema.dumps(NetworkAddress()).data
        serialized_proxyaddress = schema.dumps(NetworkAddress("localhost", 9999)).data

        self.cncProcess = subprocess.Popen([emu_config.basedir + "/actors/CnCServer.py", serialized_cncaddress])
        self.proxyProcess = subprocess.Popen(
            [emu_config.basedir + "/actors/Proxy.py", serialized_proxyaddress, serialized_cncaddress])
        time.sleep(3)
        self.botProcess1 = subprocess.Popen([emu_config.basedir + "/actors/Bot.py", serialized_proxyaddress])
        self.botProcess2 = subprocess.Popen([emu_config.basedir + "/actors/Bot.py", serialized_proxyaddress])
        time.sleep(2)

    def tearDown(self):
        self.cncProcess.terminate()
        self.proxyProcess.terminate()
        self.botProcess1.terminate()
        self.botProcess2.terminate()
        time.sleep(1)
        self.cncProcess.kill()
        self.proxyProcess.kill()
        self.botProcess1.kill()
        self.botProcess2.kill()

    def testHasBotRegistered(self):
        """Tests if the two bots have automatically registered themselves with the CnC-Server"""

        na = NetworkAddress()
        cnc_url = "http://%s:%s/register" % (na.host, na.port)

        raw_response = requests.get(cnc_url, headers={"Accept": "application/json"})
        response = json.loads(raw_response.text)
        self.assertEquals(2, response["num_clients"])

        response = requests.get(cnc_url)
        self.assertTrue("2" in response.text)

    def testBotAcceptsCommands(self):
        """Tests if the bot accepts commands from the CnC-server"""

        na = NetworkAddress()
        cnc_url = "http://%s:%s/current_command" % (na.host, na.port)

        temporary_file = tempfile.mkstemp()[1]
        print temporary_file, type(temporary_file)
        response = requests.post(cnc_url, data={'command': 'new_command',
                                                'kwargs': json.dumps({'x': 4, 'filename': temporary_file})})
        self.assertEquals("OK", response.text)

        time.sleep(5)
        with open(temporary_file, 'r') as read_from:
            line = read_from.readline()
            print "line: ", line
            self.assertEquals(16, int(line))

