#!/usr/bin/env python2
# coding=UTF-8
import logging, time, threading
from actors.AbstractBot import Runnable


class TestRunnable(Runnable):
    def __init__(self, toPrint):
        Runnable.__init__(self, name="TestRunnable")
        self.toPrint = toPrint

    def start(self):
        while not self.stopthread:
            logging.info("Runnable %s is still running")
            time.sleep(5)
            with open("/tmp/test.txt", "a") as myfile:
                myfile.write(self.toPrint + "\n")

    def stop(self):
        self.stopthread = True
