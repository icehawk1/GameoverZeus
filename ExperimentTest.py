#!/usr/bin/env python2
# coding=UTF-8
import unittest
from Experiment import Experiment


class ExperimentTest(unittest.TestCase):
    def setUp(self):
        self.objectUnderTest = MockExperiment()

    def testMockExperimentGetsExecuted(self):
        self.objectUnderTest.executeExperiment()
        self.assertTrue(self.objectUnderTest.inited and self.objectUnderTest.started and self.objectUnderTest.stopped)
        self.assertEqual(10, self.objectUnderTest.num)


class MockExperiment(Experiment):
    """Simple Experiment that stops after 10 iterations and remembers if all its methods have been called"""

    def _setup(self):
        self.inited = True

    def _start(self):
        self.started = True

    def _executeStep(self, num):
        self.num = num
        return not num == 10

    def _stop(self):
        self.stopped = True
