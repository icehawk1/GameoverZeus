#!/usr/bin/env python2
# coding=UTF-8
import os, string, re, logging
from utils.MiscUtils import createLoadtimePlot, mkdir_p, datetimeToEpoch, average
from utils.LogfileParser import parseMachineReadableLogfile
from resources.emu_config import logging_config


def readExperimentStartStopTime():
    logentries = parseMachineReadableLogfile(runnable="ZeusExperiment")

    tmp = [datetimeToEpoch(entry.entrytime) for entry in logentries if "Experiment started" in entry.message]
    assert len(tmp) == 1
    startTime = int(tmp[0])
    # startTime = tmp[0] if len(tmp)==1 else 1470046796

    tmp = [datetimeToEpoch(entry.entrytime) for entry in logentries if "Experiment ended" in entry.message]
    assert len(tmp) == 1
    stopTime = int(tmp[0])

    return startTime, stopTime


def readTimeCommandWasIssued():
    logentries = parseMachineReadableLogfile(runnable="ZeusExperiment")
    result = sorted([(datetimeToEpoch(entry.entrytime), entry.message.replace("issued command", "").strip())
                     for entry in logentries if "issued command" in string.lower(entry.message)])
    return result


def plotBotsThatRegistered(startTime, outfile):
    assert isinstance(startTime, int)

    logentries = parseMachineReadableLogfile(runnable="CnCServer")
    extractNum = lambda msg: re.match("Number of bots: (\d+)", msg).group(1)
    data = [(int(datetimeToEpoch(entry.entrytime) - startTime), int(extractNum(entry.message)))
            for entry in logentries if "Number of bots" in entry.message]
    print data
    createLoadtimePlot([e[0] for e in data], [e[1] for e in data], outfile)


def readTimeToPropagateCommand(issuetime):
    assert isinstance(issuetime, int)

    logentries = parseMachineReadableLogfile(runnable="Bot")
    result = [datetimeToEpoch(entry.entrytime) - issuetime for entry in logentries if "received command" in entry.message]
    return result


if __name__ == '__main__':
    logging.basicConfig(**logging_config)

    startTime, stopTime = readExperimentStartStopTime()
    issuetimes = readTimeCommandWasIssued()
    assert len(issuetimes) == 1
    propTimes = readTimeToPropagateCommand(issuetimes[0][0])
    print "It took %s (avg: %d) seconds to propagate the command to the bots"%(propTimes, average(propTimes))
    plotBotsThatRegistered(startTime, "/tmp/botnetemulator/NumRegisteredBotsVsTime.pdf")
