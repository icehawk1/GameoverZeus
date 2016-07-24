#!/usr/bin/env python2
# coding=UTF-8
import unittest
from resources.emu_config import basedir
from utils.TcptraceParser import TcptraceParser
from utils.MiscUtils import datetimeToEpoch


class TcptraceParserTest(unittest.TestCase):
    def setUp(self):
        self.objectUnderTest = TcptraceParser()

    def testHttpconnections(self):
        inputfile = basedir + "/testfiles/httpconnections.pcap"
        actual = self.objectUnderTest.extractConnectionStatisticsFromPcap(inputfile)

        self.assertEqual(249, len(actual))
        self.assertEqual(1469368567, datetimeToEpoch(actual[0].startTime))
        self.assertEqual(12.800143, actual[8].duration.total_seconds())
        self.assertEqual(("10.0.2.15", 43048), actual[141].host1)
        self.assertEqual(('178.255.83.1', 80), actual[141].host2)
        self.assertEqual(1469368612, datetimeToEpoch(actual[248].startTime + actual[248].duration))
        self.assertEqual(("83.97.42.2", 80), actual[248].host2)
