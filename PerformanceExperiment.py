#!/usr/bin/env python2
# coding=UTF-8
"""This experiment measures the performance of Mininet with the given number of hosts and random traffic generation enabled.
While the emulator is running, the CPU load and RAM usage of the operating system is monitored.
It is also monitored if the sensor node executes its HTTP requests regularly. If that were not the case,
it would indicate that Mininet is loosing performance fidelity due to high system load. In addition,
it was tested whether every host can send an ICMP echo request ('ping') to every other host and how long this takes."""

import logging, shlex, re, random, time
from multiprocessing import Process
from datetime import datetime
from subprocess import PIPE, Popen

from resources.emu_config import logging_config, PORT
from Experiment import BriteExperiment
from topologies.BriteTopology import createBriteFile
from utils.LogfileParser import writeLogentry, parseMachineReadableLogfile
from utils.MiscUtils import datetimeToEpoch, createLinePlot

#: The number of Mininet hosts that the performance is measured with
numberOfMnHosts = 30
#: The number of seconds that this experiment should run
durationOfExperiment = 5*60


class PerformanceExperiment(BriteExperiment):
    def __init__(self):
        briteConfigFile = createBriteFile(numNodes=numberOfMnHosts)
        logging.debug("Using config file %s"%briteConfigFile)
        super(PerformanceExperiment, self).__init__(britefile=briteConfigFile)

    def _setup(self):
        """Creates all the hosts that make up the experimental network and assign them to groups"""
        super(PerformanceExperiment, self)._setup()

        nodes = set(self.topology.nodes)
        self.setNodes("victim", set(random.sample(nodes, 1)))
        nodes -= self.getNodes("victim")
        self.setNodes("sensor", set(random.sample(nodes, 1)))

    def _start(self):
        super(PerformanceExperiment, self)._start()
        victim = next(iter(self.getNodes("victim")))  # Get a sets only element ...

        pingstart = datetime.now()
        self.mininet.pingAll()
        logging.info("pingAll() took %d seconds to execute"%(datetime.now() - pingstart).seconds)

        # Start the necessary runnables
        self.overlord.startRunnable("Victim", "Victim", hostlist=[victim.name])
        self.overlord.startRunnable("Sensor", "Sensor", {"pagesToWatch": ["http://%s:%d/?root=1234"%(victim.IP(), PORT)]},
                                    hostlist=[h.name for h in self.getNodes("sensor")])
        self.overlord.startRunnable("RandomTrafficGenerator", "RandomTrafficReceiver", dict(), hostlist=self.getNodes("nodes"))
        self.overlord.startRunnable("RandomTrafficGenerator", "RandomTrafficSender",
                                    {"peerlist": [node.IP() for node in self.getNodes("nodes")], "probability": 0.1},
                                    hostlist=self.getNodes("nodes"))

        self.loadThread = Process(name="loadthread", target=self._measureCpuLoad)
        self.loadThread.start()
        self.ramThread = Process(name="ramthread", target=self._measureRamUsage)
        self.ramThread.start()

        self.startTime = datetime.now()

    def _executeStep(self, num):
        time.sleep(10)
        return (datetime.now() - self.startTime).seconds >= durationOfExperiment

    def _stop(self):
        super(PerformanceExperiment, self)._stop()
        self.loadThread.terminate()
        self.ramThread.terminate()

    def _produceOutputFiles(self):
        self._createCpuLoadGraph()
        self._createRamUsageGraph()

    def _measureCpuLoad(self):
        while True:
            with open("/proc/loadavg", mode="r") as fp:
                line = fp.readline()
                match = re.match("([\.\d]+) ([\.\d]+) ([\.\d]+).*", line)
                assert match, "Unrecognised format: %s"%line
                writeLogentry(runnable=self.__class__.__name__, message="load: %s"%match.group(1))

            time.sleep(1)

    def _measureRamUsage(self):
        while True:
            proc = Popen(shlex.split("free -m"), shell=True, stdout=PIPE)
            stdout, _ = proc.communicate()
            for line in stdout.splitlines():
                match = re.match("Mem:\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+).*", line)
                if match:
                    writeLogentry(runnable=self.__class__.__name__, message="ram: %d"%match.group(2))
                    break

            time.sleep(1)

    def _createCpuLoadGraph(self):
        logentries = parseMachineReadableLogfile(self.__class__.__name__)
        x_min = min([datetimeToEpoch(e.entrytime) for e in logentries])

        y = []
        x = []
        for entry in logentries:
            match = re.match("load: (\d+)", entry.message)
            if match:
                x.append(datetimeToEpoch(entry.entrytime) - x_min)
                y.append(int(match.group(1)))

        outputfile = "/tmp/botnetemulator/performance/cpu_load.svg"
        createLinePlot(x, "Runtime of experiment in seconds", y, "Average number of processes using the\n"
                                                                 "CPU simultaneously in the last minute", outputfile,
                       title="Load average")

    def _createRamUsageGraph(self):
        logentries = parseMachineReadableLogfile(self.__class__.__name__)
        x_min = min([datetimeToEpoch(e.entrytime) for e in logentries])

        y = []
        x = []
        for entry in logentries:
            match = re.match("ram: (\d+)", entry.message)
            if match:
                x.append(datetimeToEpoch(entry.entrytime) - x_min)
                y.append(int(match.group(1)))

        outputfile = "/tmp/botnetemulator/performance/ram_usage.svg"
        createLinePlot(x, "Runtime of experiment in seconds", y, "Used RAM in Megabytes", outputfile, title="RAM usage")


if __name__ == '__main__':
    logging.basicConfig(**logging_config)

    experiment = PerformanceExperiment()
    experiment.executeExperiment()
