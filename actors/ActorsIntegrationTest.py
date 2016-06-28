#!/usr/bin/env python2.7
# coding=UTF-8
import time, random, unittest, subprocess, shlex, json
import requests

import emu_config
from utils.NetworkUtils import NetworkAddress, NetworkAddressSchema


class ActorsIntegrationTest(unittest.TestCase):
    def setUp(self):
        schema = NetworkAddressSchema()
        serialized_cncaddress = schema.dumps(NetworkAddress()).data
        serialized_proxyaddress = schema.dumps(NetworkAddress("localhost", 9999)).data

        self.cncProcess = subprocess.Popen([emu_config.basedir + "/actors/CnCServer.py", serialized_cncaddress])
        self.proxyProcess = subprocess.Popen(
            [emu_config.basedir + "/actors/Proxy.py", serialized_proxyaddress, serialized_cncaddress])
        self.botProcess = subprocess.Popen([emu_config.basedir + "/actors/Bot.py", serialized_proxyaddress])
        self.botProcess = subprocess.Popen([emu_config.basedir + "/actors/Bot.py", serialized_proxyaddress])
        time.sleep(5)

    def tearDown(self):
        self.cncProcess.terminate()
        self.proxyProcess.terminate()
        self.botProcess.terminate()
        time.sleep(1)
        self.cncProcess.kill()

    def testHasBotRegistered(self):
        na = NetworkAddress()
        cnc_url = "http://%s:%s/register" % (na.host, na.port)

        raw_response = requests.get(cnc_url, headers={"Accept": "application/json"})
        response = json.loads(raw_response.text)
        self.assertEquals(2, response["num_clients"])

        response = requests.get(cnc_url)
        self.assertTrue("2" in response.text)
