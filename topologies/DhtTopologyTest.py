#!/usr/bin/env python2
# coding=UTF-8
import unittest

myvar = 8


class DhtTopologyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def testDistributeCommand(self):
        print "testDistributeCommand"
        pass

    def testInsertNewBot(self):
        self.assertEquals(6, myvar)
        pass

    def testLookupBot(self):
        pass


class PengBummTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def testBlubStuff(self):
        pass


def suite():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTest(loader.loadTestsFromTestCase(PengBummTest))
    suite.addTest(loader.loadTestsFromTestCase(DhtTopologyTest))
    return suite


if __name__ == '__main__':
    print "executed once per suite - startup"
    runner = unittest.TextTestRunner()
    runner.run(suite())
    print "executed once per suite - teardown"
