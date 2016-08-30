#!/usr/bin/env python2
# coding=UTF-8
from utils.TcptraceParser import TcptraceParser
import matplotlib

matplotlib.use('pdf')
import matplotlib.pyplot as pyplot

if __name__ == '__main__':
    pcapfile = "/tmp/zeus/victim.pcap"
    ttparser = TcptraceParser("/tmp/zeus")
    stats = ttparser.plotConnectionStatisticsFromPcap(pcapfile)
    pyplot.clf()

    pcapfile = "/tmp/overbot/victim.pcap"
    ttparser = TcptraceParser("/tmp/overbot")
    stats = ttparser.plotConnectionStatisticsFromPcap(pcapfile)
    pyplot.clf()

    pcapfile = "/tmp/ping/victim.pcap"
    ttparser = TcptraceParser("/tmp/ping")
    stats = ttparser.plotConnectionStatisticsFromPcap(pcapfile)
    pyplot.clf()
