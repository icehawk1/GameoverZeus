#!/usr/bin/env python2
# coding=UTF-8
import shlex, logging, os, re
from subprocess import Popen, PIPE
from datetime import datetime, timedelta

from utils.MiscUtils import mkdir_p, createLoadtimePlot, datetimeToEpoch

class TcptraceParser(object):
    def __init__(self, outputdir="/tmp/botnetemulator/tcptrace",host=None):
        self.outputdir = outputdir
        self.host = host

    def extractConnectionStatisticsFromPcap(self, pcapfile):
        """Extracts the communicating hosts, relative time of first packet and duration for every tcp connection
            in the given pcap file.
            :param pcapfile: The path to a file in pcap or pcapng format.
            :return: A list of TcpConnection objects ordered by the connection start time."""
        ttoutput = self._runTcpTraceOnPcap(pcapfile)
        result = self._extractConnectionStatistics(ttoutput)
        self._createPlotOfLoadingTimes(result)
        return result

    def _runTcpTraceOnPcap(self, pcapfile):
        """Runs tcptrace -ln on the given pcap file and returns the input"""
        assert os.path.isfile(pcapfile), "pcap file does not exist: %s"%pcapfile
        try:
            process = Popen(shlex.split("tcptrace -ln %s"%pcapfile), shell=False, stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                logging.warning("tcptrace returned an unsucessful return code %d: %s"%(process.returncode, stderr))
                return None
            else:
                return stdout
        except OSError as ex:
            logging.error("tcptrace execution failed: %s"%ex)
            return None

    def _extractConnectionStatistics(self, ttoutput):
        """Extracts the communicating hosts, relative time of first packet and duration for every tcp connection
        from the given output of tcptrace -ln.
        :type ttoutput: str
        :return: A list of TcpConnection objects ordered by the connection start time."""
        assert isinstance(ttoutput, str), "type ttoutput: %s"%type(ttoutput)

        hostRE = r"host \w+:\s*([0-9.]+):([0-9]+)"
        startTimeRE = r'first packet:\s*([\w\s:\.]+)\s*'
        lastPacketRE = r'last packet:\s*([\w\s:\.]+)\s*'
        dateformat = "%a %b %d %H:%M:%S.%f %Y"
        connectionSeparatorRE = "=====+"

        result = []
        current_connection = TcpConnection()
        for line in ttoutput.splitlines():
            if re.search(hostRE, line) and current_connection.host1 is None:
                match = re.search(hostRE, line)
                current_connection.host1 = (match.group(1), int(match.group(2)))
            elif re.search(hostRE, line):
                match = re.search(hostRE, line)
                current_connection.host2 = (match.group(1), int(match.group(2)))
            elif re.search(startTimeRE, line):
                match = re.search(startTimeRE, line)
                current_connection.startTime = datetime.strptime(match.group(1), dateformat)
            elif re.search(lastPacketRE, line):
                assert current_connection.startTime is not None
                match = re.search(lastPacketRE, line)
                current_connection.duration = datetime.strptime(match.group(1),
                                                                dateformat) - current_connection.startTime
                assert isinstance(current_connection.duration, timedelta)
            elif re.search(connectionSeparatorRE, line):
                assert current_connection.isComplete()
                result.append(current_connection)
                current_connection = TcpConnection()
        result.append(current_connection)

        result = sorted(result, key=lambda conn: datetimeToEpoch(conn.startTime))
        return result

    def _createPlotOfLoadingTimes(self, connection_statistics):
        """Creates a pdf file that shows a plot with the relative time when a page load began on the x-axis
            and the time taken to complete the page load on the y-axis. Page load means that this sensor loads a web page
            from a web server and measures how long this takes.
            :param connection_statistics: A list of TcpConnection objects"""
        mkdir_p(self.outputdir)  # Ensure outputdir exists

        raw_x = [datetimeToEpoch(conn.startTime) for conn in connection_statistics]
        raw_min = min(raw_x)
        x = [x - raw_min for x in raw_x]
        y = [conn.duration.total_seconds() for conn in connection_statistics]
        # logging.debug("x = %s"%x)
        # logging.debug("y = %s"%y)

        if self.host:
            createLoadtimePlot(x,y, "%s/loadingtimes-%s.pdf"%(self.outputdir,self.host))
        else:
            createLoadtimePlot(x, y, "%s/loadingtimes.pdf"%self.outputdir)

class TcpConnection(object):
    host1 = None
    host2 = None
    startTime = None
    duration = None

    def isComplete(self):
        return self.host1 is not None and self.host2 is not None and self.startTime is not None and self.duration is not None
