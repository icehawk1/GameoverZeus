#!/usr/bin/env python2
# coding=UTF-8
"""This file contains utilities to parse the machine readable logfile,
which is used to collect the results of a Runnable for later analysis"""
import string, os
from datetime import datetime
from utils.MiscUtils import mkdir_p

# Example log entry: 2016-07-21 13:24:33,369|machine_readable.mychild|Ich bin eine Message

#: The file where the logs are written to
logfile = "/tmp/botnetemulator/machine_readable.log"


def writeLogentry(runnable, message):
    """Appends an entry to the machine readable logfile
    :param runnable: The runnable that issued the log entry.
            Should be the name of the class and can be used for searching entries.
    :param message: An explanatory message to be included with the entry"""
    assert isinstance(runnable, str)
    assert isinstance(message, str)
    mkdir_p(os.path.dirname(logfile))  # Make sure directory exists

    datestr = datetime.now().isoformat(" ")
    print datestr
    with open(logfile, mode="a") as fp:
        fp.write("%s|%s|%s" % (datestr, string.strip(runnable), string.strip(message)))

def parseMachineReadableLogfile(runnable=None):
    """Parses the machine readable logfile and returns its contents
    :param runnable: Only return entries from this runnable
    :return: A list of Logentry's with the same order as in the logfile"""
    mkdir_p(os.path.dirname(logfile))  # Make sure directory exists

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
        self.runnable = splitted[1]
        #: The message that was recorded
        self.message = splitted[2]
