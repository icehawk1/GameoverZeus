#!/usr/bin/env python2.7
# coding=UTF-8
import os, logging, sys

assert os.environ["DEBUSSY"] == "1"
from utils.NetworkUtils import NetworkAddress, NetworkAddressSchema

def stop():
    os.system("kill %mitmdump")

if __name__ == "__main__":
    logging.basicConfig(format="%(threadName)s: %(message)s", level=logging.INFO)
    schema = NetworkAddressSchema()

    if len(sys.argv) >= 3:
        proxyaddress = schema.loads(sys.argv[1]).data
        cncaddress = schema.loads(sys.argv[2]).data
    else:
        proxyaddress = NetworkAddress()
        cncaddress = NetworkAddress()

    os.system(
        "mitmdump -q --anticache -p %s -R 'http://%s:%s/' " % (proxyaddress.port, cncaddress.host, cncaddress.port))
