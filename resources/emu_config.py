#!/usr/bin/env python2
# coding=UTF-8
"""
This file contains various configuration variables for the botnet emulator
"""

import os, logging

basedir = os.path.dirname(os.path.realpath(__file__))  #: The directory where the python code of this emulator is stored
basedir = os.path.join(basedir, os.pardir)  #: Start path should be the parent of this files directory
PORT = 8080  #: The port CnC Servers and proxies listen on per default
#: Directory where the Overlord looks for sockets that he then uses to connect to the clients
SOCKET_DIR = "/tmp/overlordsockets/"
kademlia_default_port = 8468  #: Default port number where Kademlia servers listen for traffic
#: Number of seconds to sleep before a bot checks for new commands. Can be overriden in individual bot instances
botcommand_timeout = 15
#: Logging setting used throughout the emulator. Will be passed to logging.basicConfig()
logging_config = {'format': "[%(module)s.py:%(lineno)d (thread: %(threadName)s)]:%(levelname)s: %(message)s",
                  'level': logging.DEBUG}
