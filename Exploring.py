#!/usr/bin/env python2.7
from mininet.net import Mininet, Controller
import time
from mininet.log import setLogLevel

setLogLevel('info')

mn = Mininet(controller=Controller)
mn.addController("assadfdsa")
time.sleep(2)

sw = mn.addSwitch("switch1")
h1 = mn.addHost("h1")
h2 = mn.addHost("h2")
mn.addLink(h1, sw)
mn.addLink(h2, sw)

mn.start()
time.sleep(2)
mn.pingAll()
time.sleep(2)
mn.stop()
