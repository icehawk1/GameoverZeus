#!/usr/bin/env python2
# coding=UTF-8
"""This file defines a Runnable that is used as a mock object for testing purposes."""
import logging, time, os, unittest
from actors.AbstractBot import Runnable
from AbstractBotTest import RunnableTest

class TestRunnable(Runnable):
    def __init__(self, toPrint, outputdir="/tmp", **kwargs):
        super(TestRunnable, self).__init__(**kwargs)
        self.toPrint = toPrint
        self.outputdir = outputdir

    def start(self):
        while not self.stopthread:
            logging.info("Runnable %s is still running")
            time.sleep(5)
            with open("%s/test_%s.txt" % (self.outputdir, self.name), "a") as myfile:
                myfile.write(self.toPrint + "\n")

    def stop(self):
        self.stopthread = True
        time.sleep(1)


class TestRunnableTest(RunnableTest, unittest.TestCase):
    expected = "print this, bitch"
    inputfile = '/tmp/test_TestRunnableTest.txt'

    def tearDown(self):
        super(TestRunnableTest, self).tearDown()
        os.remove(self.inputfile)

    def createObjectUnderTest(self):
        return TestRunnable(self.expected, name="TestRunnableTest")

    def verifyOUThasBeenRun(self):
        self.assertTrue(os.path.exists(self.inputfile))
        with open(self.inputfile, 'r') as myfile:
            actual = myfile.read().replace("\n", "")
        self.assertEqual(self.expected, actual)


if __name__ == '__main__':
    unittest.main()
