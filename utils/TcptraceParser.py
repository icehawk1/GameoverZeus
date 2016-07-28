#!/usr/bin/env python2
# coding=UTF-8
import shlex, logging, os, re, fnmatch
from subprocess import Popen, PIPE
from datetime import datetime, timedelta

from utils.MiscUtils import mkdir_p, createLoadtimePlot, datetimeToEpoch, removeSuffixes

class TcptraceParser(object):
    def __init__(self, outputdir="/tmp/botnetemulator/tcptrace"):
        self.outputdir = outputdir

    def extractConnectionStatisticsFromPcap(self, pcapdir):
        """Extracts the communicating hosts, relative time of first packet and duration for every tcp connection
            in the given pcap file.
            :param pcapdir: The path to a directory containing files in pcap or pcapng format.
            :return: A list of TcpConnection objects ordered by the connection start time."""
        result = []
        for pcapfile in os.listdir(pcapdir):
            if fnmatch.fnmatch(pcapfile, '*.pcap') or fnmatch.fnmatch(pcapfile, "*.pcapng"):
                ttoutput = self._runTcpTraceOnPcap(os.path.join(pcapdir, pcapfile))
                print "ttoutput: ", ttoutput
                result.append(self._extractConnectionStatistics(ttoutput))
                self._createPlotOfLoadingTimes(result[-1], "%s.pdf"%removeSuffixes(pcapfile, [".pcap", ".pcapng"]))
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
        from the given output of tcptrace -ln. See file testfiles/httpconnections.tcptrace for an example of what
        this method parses.
        :type ttoutput: str
        :param ttoutput: The output that tcptrace produced
        :return: A list of TcpConnection objects ordered by the connection start time."""
        assert isinstance(ttoutput, str), "type ttoutput: %s"%type(ttoutput)

        hostRE = r"host \w+:\s*([0-9.]+):([0-9]+)"  # Matches a line containing one of the hosts that are communicating here
        startTimeRE = r'first packet:\s*([\w\s:\.]+)\s*'  # Matches a line containing the time the first packet of this connection was seen
        lastPacketRE = r'last packet:\s*([\w\s:\.]+)\s*'  # Matches the time the last packet was seen
        dateformat = "%a %b %d %H:%M:%S.%f %Y"  # How the dates in the input are formatted, used to convert them to a datetime object
        connectionSeparatorRE = "=====+"  # The descriptions of the individual connections are separated by a line of =

        result = []
        current_connection = TcpConnection()
        for line in ttoutput.splitlines():
            if re.search(hostRE, line) and current_connection.host1 is None:
                # If the line contains the IP of one of the hosts
                match = re.search(hostRE, line)
                current_connection.host1 = (match.group(1), int(match.group(2)))
            elif re.search(hostRE, line):
                # If the line contains the IP of one of the hosts and the first host was already seen, it has to be the second host
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

    def _createPlotOfLoadingTimes(self, connection_statistics, filename):
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

        createLoadtimePlot(x, y, "%s/%s"%(self.outputdir, filename))

class TcpConnection(object):
    host1 = None
    host2 = None
    startTime = None
    duration = None

    def isComplete(self):
        return self.host1 is not None and self.host2 is not None and self.startTime is not None and self.duration is not None
