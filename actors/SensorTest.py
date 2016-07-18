#!/usr/bin/env python2
# coding=UTF-8
import shutil, unittest, time, random, os
from threading import Thread
import Sensor


class SensorTest(unittest.TestCase):
    """NOTE: This testcase requires a working internet connection"""

    @classmethod
    def setUpClass(cls):
        # Mock out the http connection
        Sensor.measureLoadingTime = lambda url: random.uniform(0, 1)

    def setUp(self):
        self.sensor = Sensor.Sensor("sensor", pagesToWatch=["http://heise.de", "https://www.google.com"])
        self.sensor.pauseBetweenDuties = 1
        thread = Thread(name="Runnable %s" % self.sensor.name, target=self.sensor.start)
        shutil.rmtree(self.sensor.outputdir, ignore_errors=True)

        thread.start()
        time.sleep(2.5)
        self.sensor.stop()

    def tearDown(self):
        shutil.rmtree(self.sensor.outputdir, ignore_errors=True)

    def expectOutputfilesToExist(self):
        self.assertTrue(os.path.exists(self.sensor.outputdir))
        self.assertEqual(2, len(os.listdir(self.sensor.outputdir)))

    def testIfLoadingTimesAreValid(self):
        self.assertEqual(2, len(self.sensor.loadingTimesDict.keys()))

        for key in self.sensor.loadingTimesDict.keys():
            self.assertEqual(3, len(self.sensor.loadingTimesDict[key]))
            self.assertTrue(0 <= sum(self.sensor.loadingTimesDict[key]) <= 3)
