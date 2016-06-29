#!/usr/bin/env python2.7
# coding=UTF-8
import unittest, logging, os
import emu_config

logging.basicConfig(format="%(threadName)s: %(message)s", level=logging.INFO)
os.environ["DEBUSSY"] = "1"

testSuite = unittest.TestSuite()
testloader = unittest.TestLoader()
testSuite.addTests(testloader.discover(emu_config.basedir, pattern="*Test.py"))
testrunner = unittest.TextTestRunner()
testrunner.run(testSuite)
