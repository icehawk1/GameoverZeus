#!/usr/bin/env python2
# coding=UTF-8
import unittest, os
from utils import LogfileParser


class LogfileParserTest(unittest.TestCase):
    mocklogfile = "/tmp/blubdibla.log"

    def setUp(self):
        with open(self.mocklogfile, mode="w") as fp:
            fp.write("2016-07-21 13:24:33,369|machine_readable.mychild|Ich bin eine Message\n")
            fp.write("1333-12-01 03:24:33,00963|machine_readable.yeah|I am a message\n")
            fp.write("\n")
        LogfileParser.logfile = self.mocklogfile

    def tearDown(self):
        os.remove(self.mocklogfile)

    def testReadFullFile(self):
        entries = LogfileParser.parseMachineReadableLogfile()
        self.assertEqual(2, len(entries))
        self.assertEqual("I am a message", entries[1].message)
        self.assertEqual(7, entries[0].entrytime.month)
        self.assertEqual("yeah", entries[1].runnable)

    def testReadOnlyRunnable(self):
        entries = LogfileParser.parseMachineReadableLogfile("yeah")
        self.assertEqual(1, len(entries))
        self.assertEqual("I am a message", entries[0].message)
