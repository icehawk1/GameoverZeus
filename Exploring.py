#!/usr/bin/env python2.7
from utils.NetworkUtils import NetworkAddress
import pickle

orig = NetworkAddress("blub", 1111)
dump = "" + pickle.dumps(orig)
copy = pickle.loads(dump)
assert copy.host == "blub"
assert copy.port == 1111
