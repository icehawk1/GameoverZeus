#!/usr/bin/env python2.7
from actors import Bot_Commands


def urg(x):
    print "x^2 == %d" % (x ** 2)


Bot_Commands.pengbumm = urg

Bot_Commands.pengbumm(3)
