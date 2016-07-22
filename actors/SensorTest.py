#!/usr/bin/env python2
# coding=UTF-8
import shutil, unittest, time, random, os, logging
from threading import Thread

import Sensor
from resources.emu_config import logging_config
from utils import LogfileParser

class SensorTest(unittest.TestCase):
    """NOTE: This testcase requires a working internet connection"""

    @classmethod
    def setUpClass(cls):
        # Mock out the http connection
        Sensor.measureLoadingTime = lambda url: round(random.uniform(0, 1), ndigits=3)

    def setUp(self):
        if os.path.exists(LogfileParser.logfile):
            os.remove(LogfileParser.logfile)

        self.sensor = Sensor.Sensor(name="sensor", pagesToWatch=["http://heise.de", "https://www.google.com"])
        self.sensor.pauseBetweenDuties = 1
        thread = Thread(name="Runnable %s" % self.sensor.name, target=self.sensor.start)
        shutil.rmtree(self.sensor.outputdir, ignore_errors=True)

        thread.start()
        time.sleep(2.5)
        self.sensor.stop()

    def tearDown(self):
        shutil.rmtree(self.sensor.outputdir, ignore_errors=True)

    @unittest.skip("Only one of the tests can be run at the same time")
    def testExpectOutputfilesToExist(self):
        self.assertTrue(os.path.exists(self.sensor.outputdir))
        self.assertEqual(2, len(os.listdir(self.sensor.outputdir)))

    def testIfLoadingTimesAreValid(self):
        loadingTimesDict = self.sensor._collectLoadingTimes()
        self.assertEqual(2, len(loadingTimesDict.keys()))

        for key in loadingTimesDict.keys():
            self.assertEqual(3, len(loadingTimesDict[key]))
            self.assertTrue(0 <= sum(loadingTimesDict[key]) <= 3)


if __name__ == '__main__':
    logging.basicConfig(**logging_config)
    unittest.main()
