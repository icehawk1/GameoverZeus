#!/usr/bin/env python2.7
"""Tests whether the current system has everything that is needed to run the BotnetEmulator"""

import importlib
import os
import subprocess
import unittest
from distutils.spawn import find_executable


class SanityCheck(unittest.TestCase):
    """Tests whether the current system has everything that is needed to run the BotnetEmulator"""

    def testRequiredToolsAreInstalled(self):
        """test if all required tools are installed"""
        required_commands = ["mn", "python", "mitmdump", "floodlight"]
        for cmd in required_commands:
            self.assertTrue(find_executable(cmd) or find_executable(cmd + ".exe"), "%s is not installed." % cmd)

    def testRequiredPythonModulesAreInstalled(self):
        """test if all required python modules are installed"""
        required_modules = ["blinker", "tornado", "mininet", "twisted.names", "marshmallow", "requests", "pygraphviz",
                            "timeout_decorator"]
        for module in required_modules:
            try:
                importlib.import_module(module)
            except ImportError, e:
                self.fail("Module %s is not installed" % module)

    def testDefaultOpenflowControllerExists(self):
        """Checks whether a default Openflow Controller is defined"""
        self.assertTrue(os.path.isfile("/usr/bin/controller"),
                        "There is no default Openflow Controller defined. Please create a link called "
                        "/usr/bin/controller to the controller executable you want to use.")

    def testRunningAsRoot(self):
        """Tests whether the script was executed as root"""
        self.assertEquals(os.getuid(), 0, "Please run the BotnetEmulator as root.")

    @unittest.skip("Takes several seconds")
    def testMininetWorks(self):
        """Executes the mn selftest"""
        output = str(subprocess.check_output("mn --test=pingall", shell=True, stderr=subprocess.STDOUT))
        self.assertTrue("Results: 0% dropped" in output)


if __name__ == '__main__':
    unittest.main()
