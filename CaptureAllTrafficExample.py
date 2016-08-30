#!/usr/bin/env python2
# coding=UTF-8
import re, os, signal, time, shlex
from subprocess import PIPE, Popen
import netifaces

mnIfacePattern = r"s1-.*"
outputfile = "/tmp/blub.pcap"
botnetTrafficCommand = 'sudo tshark -q -r "%s"  -z conv,ip -p -2 -R "icmp"'%outputfile
legitimateTrafficCommand = 'sudo tshark -q -r "%s"  -z conv,ip -p -2 -R "tcp or udp"'%outputfile
sizeRegex = r"[\d\.]+\s+<->\s+[\d\.]+\s+(\d+\s+){5}(\d+)\s+.*"

if __name__ == '__main__':
    if os.path.exists(outputfile):
        os.remove(outputfile)

    mininetInterfaces = [iface for iface in netifaces.interfaces() if re.match(mnIfacePattern, iface)]
    for iface in mininetInterfaces:
        assert isinstance(iface, str)
    print "mininetInterfaces:", mininetInterfaces

    tsharkCommand = "tshark -w %s -i %s "%(outputfile, " -i ".join(mininetInterfaces))
    print "tshark command:", tsharkCommand
    tsharkProc = Popen(shlex.split(tsharkCommand), stdout=PIPE, stderr=PIPE)

    time.sleep(60)
    tsharkProc.send_signal(signal.SIGHUP)
    assert os.path.isfile(outputfile)

    stdout, stderr = tsharkProc.communicate()
    assert isinstance(stdout, str)
    assert isinstance(stderr, str)
    print "stdout:", stdout
    print "stderr:", stderr

    botnetTsharkProc = Popen(shlex.split(botnetTrafficCommand), stdout=PIPE, stderr=PIPE)
    legitimateTsharkProc = Popen(shlex.split(legitimateTrafficCommand), stdout=PIPE, stderr=PIPE)
    stdout, stderr = botnetTsharkProc.communicate()
    # print "botnet:",stdout

    botnetSize = sum([int(re.match(sizeRegex, line).group(2)) for line in stdout.splitlines() if re.match(sizeRegex, line)])
    print "The botnet produced %d bytes of traffic"%botnetSize

    stdout, stderr = legitimateTsharkProc.communicate()
    # print "legitimate:",stdout
    botnetSize = sum([int(re.match(sizeRegex, line).group(2)) for line in stdout.splitlines() if re.match(sizeRegex, line)])
    print "The legitimate usage produced %d bytes of traffic"%botnetSize
