#!/usr/bin/env python2
# coding=UTF-8
"""This file contains utilities to parse the machine readable logfile,
which is used to collect the results of a Runnable for later analysis"""
import string, logging
from datetime import datetime
from utils.MiscUtils import mkdir_p

# Example log entry: 2016-07-21 13:24:33,369|machine_readable.mychild|Ich bin eine Message

logdir = "/tmp/botnetemulator"
#: The file where the logs are written to
logfile = "%s/machine_readable.log" % logdir


def _configureMRLogger(filename=logfile):
    mkdir_p(logdir)
    handler = logging.FileHandler(filename=filename, mode="a")
    handler.setFormatter(logging.Formatter("%(asctime)s|%(name)s|%(message)s"))
    mrlogger.addHandler(handler)
    mrlogger.setLevel(logging.INFO)


#: The logger used to collect results from Runnables
mrlogger = logging.getLogger("machine_readable")
if len(mrlogger.handlers) == 0:  # If it is not configured already
    _configureMRLogger()


def parseMachineReadableLogfile(runnable=None):
    """Parses the machine readable logfile and returns its contents
    :param runnable: Only return entries from this runnable
    :return: A list of Logentry's with the same order as in the logfile"""
    result = []
    with open(logfile, "r") as fp:
        for line in fp:
            try:
                logentry = Logentry(line)
                if runnable is None or runnable == logentry.runnable:
                    result.append(logentry)
            except ValueError as ex:
                pass
    return result


class Logentry(object):
    """Represents an Entry in the machine readable logfile, which is used to communicate the results of a Runnable"""

    def __init__(self, logentry):
        assert isinstance(logentry, str)
        splitted = [string.strip(x) for x in logentry.split("|")]

        #: The time when the entry was recorded as given in the logfile
        self.entrytime = datetime.strptime(splitted[0], "%Y-%m-%d %H:%M:%S,%f")
        #: The Runnable that issued the log entry
        self.runnable = string.split(splitted[1], ".", maxsplit=1)[1]
        #: The message that was recorded
        self.message = splitted[2]
