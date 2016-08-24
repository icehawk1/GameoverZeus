#!/usr/bin/env python2
# coding=UTF-8
import sys, string, re, logging, json
from utils.MiscUtils import createLinePlot, mkdir_p, datetimeToEpoch, average
from utils.LogfileParser import parseMachineReadableLogfile
from resources.emu_config import logging_config


def readExperimentStartStopTime():
    logentries = parseMachineReadableLogfile(runnable="KademliaExperiment")

    tmp = [datetimeToEpoch(entry.entrytime) for entry in logentries if "Experiment started" in entry.message]
    assert len(tmp) == 1
    startTime = int(tmp[0])
    # startTime = tmp[0] if len(tmp)==1 else 1470046796

    tmp = [datetimeToEpoch(entry.entrytime) for entry in logentries if "Experiment ended" in entry.message]
    assert len(tmp) == 1
    stopTime = int(tmp[0])

    return startTime, stopTime


def readTimesCommandsWereIssued():
    logentries = parseMachineReadableLogfile(runnable="KademliaExperiment")

    result = []
    for entry in logentries:
        if "send command" in string.lower(entry.message):
            match = re.match("Send command ([\w_\-.]+) to bot ([\w_\-.]+)", entry.message)
            curr = (int(datetimeToEpoch(entry.entrytime)), match.group(1), match.group(2))
            result.append(curr)

    return sorted(result, key=lambda e: e[0])


def plotBotsThatRegistered(startTime, outfile):
    assert isinstance(startTime, int)

    logentries = parseMachineReadableLogfile(runnable="CnCServer")
    extractNum = lambda msg: re.match("Number of bots: (\d+)", msg).group(1)
    data = [(int(datetimeToEpoch(entry.entrytime) - startTime), int(extractNum(entry.message)))
            for entry in logentries if "Number of bots" in entry.message]
    print data
    createLinePlot([e[0] for e in data], "experiment runtime in seconds", [e[1] for e in data],
                   "number of bots that have registered with CnC server", outfile)


def readTimeToPropagateCommand(issuetime):
    assert isinstance(issuetime, int)

    logentries = parseMachineReadableLogfile(runnable="KademliaBot")
    result = [datetimeToEpoch(entry.entrytime) - issuetime for entry in logentries if "received command" in entry.message]
    return result


if __name__ == '__main__':
    logging.basicConfig(**logging_config)

    startTime, stopTime = readExperimentStartStopTime()
    issuetimes = [tp[0] for tp in readTimesCommandsWereIssued()] + [sys.maxint]
    print issuetimes

    receivings = []
    for entry in parseMachineReadableLogfile(runnable="KademliaBot"):
        if "received command" in entry.message and "ddos_server" in entry.message:
            time = datetimeToEpoch(entry.entrytime)
            tmp = re.match("received command: (.*)", entry.message).group(1)
            print tmp
            command = json.loads(tmp)
            receivings.append((time, command["bot"]))
    print receivings

    for i in range(1, len(issuetimes)):
        timings = [r[0] - issuetimes[i - 1] for r in receivings if (issuetimes[i - 1] <= r[0] <= issuetimes[i])]
        print "It took %s (avg: %d) seconds to issue the %d. command"%(timings, average(timings), i)
        botlist = [r[1] for r in receivings if (issuetimes[i - 1] <= r[0] <= issuetimes[i])]
        print "Got %d responses from %d different bots"%(len(botlist), len(set(botlist)))
