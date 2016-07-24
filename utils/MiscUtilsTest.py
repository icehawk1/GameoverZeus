#!/usr/bin/env python2
# coding=UTF-8
import unittest
from datetime import datetime

from utils import MiscUtils


class MiscUtilsTest(unittest.TestCase):
    def testDatetimeToEpoch(self):
        self.assertEqual(1352621554, MiscUtils.datetimeToEpoch(datetime(2012, 11, 11, 8, 12, 34)))
