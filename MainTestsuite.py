#!/usr/bin/env python2
# coding=UTF-8
"""Invokes all Tests in this project"""

import logging
import os
import unittest

from resources import emu_config

if __name__ == '__main__':
    logging.basicConfig(**emu_config.logging_config)
    os.environ["DEBUSSY"] = "1"

    testSuite = unittest.TestSuite()
    testloader = unittest.TestLoader()
    testSuite.addTests(testloader.discover(emu_config.basedir, pattern="*Test.py"))
    testrunner = unittest.TextTestRunner()
    testrunner.run(testSuite)
