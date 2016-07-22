#!/usr/bin/env python2
# coding=UTF-8
import unittest, time
from threading import Thread
from abc import ABCMeta, abstractmethod
from timeout_decorator import timeout

from actors.AbstractBot import Runnable, CommandExecutor

class RunnableTest(object):
    """An abstract Base Test for all tests that test Subclasses of Runnable
    @DynamicAttrs"""
    __metaclass__ = ABCMeta
    objectUnderTest = None

    def setUp(self):
        self.objectUnderTest = self.createObjectUnderTest()
        self.assertTrue(self.objectUnderTest is not None)
        self.assertTrue(isinstance(self.objectUnderTest, Runnable), msg="type(OUT)==%s" % type(self.objectUnderTest))

        self.thread = Thread(name="Testthread", target=self.objectUnderTest.start)

    def tearDown(self):
        pass

    @abstractmethod
    def createObjectUnderTest(self):
        """Creates the object that should be tested by this testcase."""

    def verifyOUTisRunning(self):
        """Checks if the object under test is currently running.
        This method is intended to be overriden in a subclass."""
        return True

    def verifyOUThasBeenRun(self):
        """Checks whether the object under test has been executed earlier. It might have been stopped when this
        method is called. This method is intended to be overriden in a subclass."""
        return True

    @timeout(15)
    def testStartStopOfRunnable(self):
        """Tests whether the given runnable can be started, run for a time and then be stopped."""
        self.thread.start()
        time.sleep(1)
        self.verifyOUTisRunning()
        self.objectUnderTest.stop()
        self.verifyOUThasBeenRun()
        self.thread.join()


class CommandExecutorTest(RunnableTest, unittest.TestCase):
    def setUp(self):
        super(CommandExecutorTest, self).setUp()
        self.assertTrue(isinstance(self.objectUnderTest, CommandExecutor),
                        msg="type(OUT)==%s" % type(self.objectUnderTest))

    def createObjectUnderTest(self):
        return MockCommandExecutor(pauseBetweenDuties=0.1)

    def verifyOUTisRunning(self):
        oldlen = len(self.objectUnderTest.dutyTimes)
        time.sleep(0.2)
        newlen = len(self.objectUnderTest.dutyTimes)
        self.assertTrue(newlen > oldlen)

    def verifyOUThasBeenRun(self):
        self.assertTrue(len(self.objectUnderTest.dutyTimes) >= 10)


class MockCommandExecutor(CommandExecutor):
    dutyTimes = []

    def performDuty(self, *args, **kwargs):
        self.dutyTimes.append(time.clock())

if __name__ == '__main__':
    unittest.main()
