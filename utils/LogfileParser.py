#!/usr/bin/env python2
# coding=UTF-8
"""This module defines a machine readable 'log file' where the observations done by actors are stored and provides functionality
to parse and write this log file. For example: When the sensor node has retrieved a web page from the server it monitors,
it will add an entry to the log file containing the time it took to load the page. The author of this thesis did not want to use
the Python logging module, because he is already using that for informational logging and it would conflict."""
import string, os
from datetime import datetime
from utils.MiscUtils import mkdir_p

# Example log entry: 2016-07-21 13:24:33,369|machine_readable.mychild|Ich bin eine Message

#: The file where the logs are written to
logfile = "/tmp/botnetemulator/machine_readable.log"


def writeLogentry(runnable, message, timeissued=None):
    """Appends an entry to the machine readable logfile
    :param runnable: The runnable that issued the log entry.
            Should be the name of the class and can be used for searching entries.
    :param message: An explanatory message to be included with the entry
    :param timeissued: Time when the event happened, that this entry is refering to"""
    mkdir_p(os.path.dirname(logfile))  # Make sure directory exists
    if timeissued is None: timeissued = datetime.now()

    with open(logfile, mode="a") as fp:
        fp.write("%s|%s|%s\n" % (timeissued.isoformat(" "), string.strip(str(runnable)), string.strip(str(message))))

def parseMachineReadableLogfile(runnable=None):
    """Parses the machine readable logfile and returns its contents
    :param runnable: Only return entries from this runnable
    :return: A list of Logentry's ordered by their timestamp"""
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
    return sorted(result, key=lambda entry: entry.entrytime)


class Logentry(object):
    """Represents an Entry in the machine readable logfile, which is used to communicate the results of a Runnable"""

    def __init__(self, logentry):
        assert isinstance(logentry, str)
        splitted = [string.strip(x) for x in logentry.split("|", 2)]

        #: The time when the entry was recorded as given in the logfile
        self.entrytime = datetime.strptime(splitted[0], "%Y-%m-%d %H:%M:%S.%f")
        #: The Runnable that issued the log entry
        self.runnable = splitted[1]
        #: The message that was recorded
        self.message = splitted[2]
