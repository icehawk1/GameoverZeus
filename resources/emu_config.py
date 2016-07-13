#!/usr/bin/env python2
# coding=UTF-8
import os

basedir = os.path.dirname(os.path.realpath(__file__))  #: The directory where the python code of this emulator is stored
basedir = os.path.join(basedir, os.pardir)  # Start path should be the parent of this files directory
PORT = 8080  #: The port CnC Servers and proxies listen on per default
SOCKET_DIR = "/tmp/overlordsockets/"
