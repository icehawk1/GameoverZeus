#!/usr/bin/env python2.7
# coding=UTF-8
import os, logging, sys
from blinker import signal


def stop():
    os.system("kill %mitmdump")

if __name__ == "__main__":
    logging.basicConfig(format="%(threadName)s: %(message)s", level=logging.INFO)
    signal("stop").connect(stop)

    if len(sys.argv) >= 2:
        cncip = sys.argv[1]
        os.system("mitmdump -q --anticache -p 8080 -R 'http://%s:8080/' " % cncip)
    else:
        cncip = "localhost"
        os.system("mitmdump -q --anticache -p 8081 -R 'http://%s:8080/' " % cncip)
