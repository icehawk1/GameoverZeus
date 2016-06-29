#!/usr/bin/env python2.7
# coding=UTF-8
import unittest, time
from mininet.net import Mininet

from FirewallTopology import *


class FirewallTopologyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fwtopo = FirewallTopology()
        cls.mininet = Mininet(cls.fwtopo)
        cls.mininet.start()
        cls.switch = cls.mininet.getNodeByName("switch1")
        cls.insideHost = cls.mininet.getNodeByName("inside2")
        cls.outsideHost = cls.mininet.getNodeByName("outside3")

    @classmethod
    def tearDownClass(cls):
        cls.mininet.stop()

    # Port 0 is completely open
    def testCommuncationOnPort0(self):
        """Port 0 is completely open, so traffic from outside to inside should be allowed"""
        server_process, server_stdout = self.extractResult(self.outsideHost, self.insideHost, ports[0])
        print "stdout: ", server_stdout
        self.assertTrue("connected with " + self.outsideHost.IP() + " port" in server_stdout)
        server_process.terminate()

    def testCommuncationOnPort1_fromOutside(self):
        """Port 1 only allows outgoing connections, so a connect from the outside to the inside should be denied"""
        server_process, server_stdout = self.extractResult(self.outsideHost, self.insideHost, ports[1])
        print server_stdout
        self.assertFalse("connected with " + self.outsideHost.IP() + " port" in server_stdout)
        server_process.terminate()

    def testCommuncationOnPort1_fromInside(self):
        """Port 1 only allows outgoing connections, so a connect from the inside to the inside should be allowed"""
        server_process, server_stdout = self.extractResult(self.insideHost, self.outsideHost, ports[1])
        print "stdout: ", server_stdout
        self.assertTrue("connected with " + self.insideHost.IP() + " port" in server_stdout)
        server_process.terminate()

    def testCommuncationOnPort2(self):
        """Port 2 is completely closed, so communication should be denied"""
        server_process, server_stdout = self.extractResult(self.insideHost, self.outsideHost, ports[2])
        print server_stdout
        self.assertFalse("connected with " + self.insideHost.IP() + " port" in server_stdout)
        server_process.terminate()

    def extractResult(self, server, client, port):
        server_process = server.popen("iperf -t 1 -s -n %d" % ports[0])
        client_process = client.popen("iperf -t 1 -c %s -n %d" % (server.IP(), port,))
        time.sleep(2)
        # Skip header
        client_process.stdout.readline()
        client_process.stdout.readline()
        client_process.stdout.readline()
        client_process.stdout.readline()
        # Read result
        client_stdout = client_process.stdout.readline()
        return server_process, client_stdout
