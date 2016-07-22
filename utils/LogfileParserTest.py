#!/usr/bin/env python2
# coding=UTF-8
import unittest, os, logging
from utils import LogfileParser
from resources.emu_config import logging_config


class LogfileWritingTest(unittest.TestCase):
    def tearDown(self):
        os.remove(LogfileParser.logfile)

    def testWriteLogentry(self):
        LogfileParser.writeLogentry(type(self).__name__, "My entry :-)")
        self.assertTrue(os.path.exists(LogfileParser.logfile))
        self.assertTrue(os.path.getsize(LogfileParser.logfile) > 1)
        with open(LogfileParser.logfile, 'r') as fp:
            data = fp.read().replace('\n', '')
        self.assertTrue("My entry :-)" in data, "Data: %s" % data)

class LogfileParserTest(unittest.TestCase):
    mocklogfile = "/tmp/blubdibla.log"

    def setUp(self):
        with open(self.mocklogfile, mode="w") as fp:
            fp.write("2016-07-21 13:24:33.369|mychild|Ich bin eine Message\n")
            fp.write("1333-12-01 03:24:33.00963|yeah|I am a message\n")
            fp.write("\n")
        self.oldlog = LogfileParser.logfile
        LogfileParser.logfile = self.mocklogfile

    def tearDown(self):
        LogfileParser.logfile = self.oldlog
        os.remove(self.mocklogfile)

    def testReadFullFile(self):
        entries = LogfileParser.parseMachineReadableLogfile()
        self.assertEqual(2, len(entries))
        self.assertEqual("I am a message", entries[0].message)
        self.assertEqual(7, entries[1].entrytime.month)
        self.assertEqual("yeah", entries[0].runnable)

    def testReadOnlyRunnable(self):
        entries = LogfileParser.parseMachineReadableLogfile("yeah")
        self.assertEqual(1, len(entries))
        self.assertEqual("I am a message", entries[0].message)


if __name__ == '__main__':
    logging.basicConfig(**logging_config)
    unittest.main()
