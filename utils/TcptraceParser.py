#!/usr/bin/env python2
# coding=UTF-8
"""The TcpTraceParser module is responsible for analyzing network traffic dumps generated during experiments.
It executes the tcptrace tool and plots the page loading times found in the given pcap file.
It then plots the result against the time the connection was initiated.

Tcptrace is a tool that takes pcap files as produced by Wireshark, extracts individual TCP connections
and prints information on each connection."""
import shlex, logging, os, re, fnmatch
from subprocess import Popen, PIPE
from datetime import datetime, timedelta

from utils.MiscUtils import mkdir_p, createLinePlot, datetimeToEpoch, removeSuffixes, average

class TcptraceParser(object):
    def __init__(self, outputdir="/tmp/botnetemulator/tcptrace"):
        self.outputdir = outputdir
        mkdir_p(self.outputdir)  # Ensure outputdir exists

    def plotConnectionStatisticsFromPcap(self, pcaplocation):
        """Creates plots that show the impact of a DDoS attack as seen from the given pcap files.
            Extracts the communicating hosts, relative time of first packet and duration for every tcp connection
            in the given directory and returns those statistics.
            :param pcaplocation: The path to a directory containing files in pcap or pcapng format
                    or the path to one such loc.
            :return: A list of TcpConnection objects ordered by the connection start time."""
        pcaps = self._collectFilesToAnalyse(pcaplocation)
        logging.debug("Analyse the following files from %s: %s"%(pcaplocation, pcaps))
        result = []

        for pcapfile in pcaps:
            currdir = os.path.join(self.outputdir, removeSuffixes(os.path.basename(pcapfile), [".pcap", ".pcapng"]))
            mkdir_p(currdir)

            ttoutput = self._runTcpTraceOnPcap(pcapfile)
            stats = self._extractConnectionStatistics(ttoutput)
            result.append(stats)
            self._createPlotOfFailedConnections(stats, currdir)
            self._createPlotOfLoadingTimes(stats, os.path.join(currdir, "pageload_times.pdf"))

        return result

    def _collectFilesToAnalyse(self, pcaplocation):
        """Returns a list of files that shall be analysed by tcptrace
        :param pcaplocation: The path to a directory containing files in pcap or pcapng format
                    or the path to one such loc."""
        # Returns true when the parameter is the path to a pcap loc
        isPcap = lambda loc: (os.path.isfile(loc) and (fnmatch.fnmatch(loc, '*.pcap') or fnmatch.fnmatch(loc, "*.pcapng")))

        if os.path.isdir(pcaplocation):
            result = [os.path.join(pcaplocation, f) for f in os.listdir(pcaplocation) if isPcap(os.path.join(pcaplocation, f))]
        elif isPcap(pcaplocation):
            result = [pcaplocation]
        else:
            logging.error("The pcap loc(s) in %s could not be read. The filenames have to end in .pcap or .pcapng."%pcaplocation)
            result = []
        return result

    def _runTcpTraceOnPcap(self, pcapfile):
        """Runs tcptrace -ln on the given pcap loc and returns the input"""
        assert os.path.isfile(pcapfile), "pcap loc does not exist: %s"%pcapfile
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
        from the given output of tcptrace -ln. See loc testfiles/httpconnections.tcptrace for an example of what
        this method parses.
        :type ttoutput: str
        :param ttoutput: The output that tcptrace produced
        :return: A list of TcpConnection objects ordered by the connection start time."""
        assert isinstance(ttoutput, str), "type ttoutput: %s"%type(ttoutput)

        hostRE = r"host \w+:\s*([0-9.]+):([0-9]+)"  # Matches a line containing one of the hosts that are communicating here
        startTimeRE = r'first packet:\s*([\w\s:\.]+)\s*'  # The time the first packet of this connection was seen
        lastPacketRE = r'last packet:\s*([\w\s:\.]+)\s*'  # The time the last packet was seen
        completedRE = r'complete conn: (\w+)'  # Whether the connection has been completed or not
        dateformat = "%a %b %d %H:%M:%S.%f %Y"  # How the dates in the input are formatted (used to convert them to datetime)
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
            elif re.search(completedRE, line):
                match = re.search(completedRE, line)
                current_connection.connection_completed = True if match.group(1).lower() == "yes" else False
            elif re.search(connectionSeparatorRE, line):
                assert current_connection.isComplete()
                result.append(current_connection)
                current_connection = TcpConnection()
        result.append(current_connection)

        result = sorted(result, key=lambda conn: datetimeToEpoch(conn.startTime))
        return result

    def _createPlotOfLoadingTimes(self, connection_statistics, filename):
        """Creates a pdf that shows a plot with the relative time when a page load began on the x-axis
            and the time taken to complete the page load on the y-axis. Page load means that this sensor loads a web page
            from a web server and measures how long this takes.
            :param connection_statistics: A list of TcpConnection objects"""
        x, startTime, _ = self._extractXAxis(connection_statistics)

        connectionsGroupedByStarttime = dict()
        for con in connection_statistics:
            key = datetimeToEpoch(con.startTime) - startTime
            if not connectionsGroupedByStarttime.has_key(key):
                connectionsGroupedByStarttime[key] = []
            connectionsGroupedByStarttime[key].append(con)

        y = []
        for second in x:
            if connectionsGroupedByStarttime.has_key(second):
                # average duration of the connections that were started during the given second
                avg = average([con.duration.total_seconds() for con in connectionsGroupedByStarttime[second]])
                y.append(avg)
            else:
                y.append(0)

        createLinePlot(x, "experiment runtime in seconds", y, "loading time in seconds", os.path.join(self.outputdir, filename))

    def _createPlotOfFailedConnections(self, connection_statistics, outputdir):
        """Creates a pdf that shows a plot with the relative time when a page load began on the x-axis
            and the time taken to complete the page load on the y-axis. Page load means that this sensor loads a web page
            from a web server and measures how long this takes.
            :param connection_statistics: A list of TcpConnection objects"""
        assert os.path.isdir(outputdir)

        x, startTime, _ = self._extractXAxis(connection_statistics)

        completeConnectionsGroupedByStarttime = dict()
        failedConnectionsGroupedByStarttime = dict()
        for con in connection_statistics:
            key = datetimeToEpoch(con.startTime) - startTime

            insertInto = completeConnectionsGroupedByStarttime if con.connection_completed else failedConnectionsGroupedByStarttime
            if not insertInto.has_key(key):
                insertInto[key] = []
            insertInto[key].append(con)

        y1 = []  # Number of incomplete connections per second
        y2 = []  # Number of completed connections per second
        for second in x:
            y1.append(
                len(failedConnectionsGroupedByStarttime[second]) if failedConnectionsGroupedByStarttime.has_key(second) else 0)
            y2.append(len(completeConnectionsGroupedByStarttime[second]) if completeConnectionsGroupedByStarttime.has_key(
                second) else 0)

        createLinePlot(x, "experiment runtime in seconds", y1, "loading time in seconds",
                       os.path.join(outputdir, "failed_connections.pdf"))
        createLinePlot(x, "experiment runtime in seconds", y2, "loading time in seconds",
                       os.path.join(outputdir, "completed_connections.pdf"))

    def _extractXAxis(self, connection_statistics):
        x_raw = {datetimeToEpoch(conn.startTime) for conn in connection_statistics}
        startTime = min(x_raw)
        endTime = max(x_raw)
        x = [i for i in range(endTime - startTime)]
        return x, startTime, endTime


class TcpConnection(object):
    host1 = None
    host2 = None
    startTime = None
    duration = None
    connection_completed = None

    def isComplete(self):
        """Decides whether this object has received all necessary data"""
        return self.host1 is not None and self.host2 is not None and self.startTime is not None and self.duration is not None \
               and self.connection_completed is not None
