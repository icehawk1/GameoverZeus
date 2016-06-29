#!/usr/bin/env python2.7
# coding=UTF-8

def printParams(hallo, hello):
    print hallo + hello


def new_command(x, filename):
    print "new_command(", x, ", ", filename, ")"
    with open(filename, 'w') as write_to:
        write_to.write(str(x ** 2))


def urg(x):
    print "x^2 == %d" % (x ** 2)
