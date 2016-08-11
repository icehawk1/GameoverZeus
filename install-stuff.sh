#!/bin/bash
#Install gcc and virtualbox guest additions first
apt-get update
apt-get install --ignore-missing -y gcc floodlight git mininet iptables wireshark tshark d-itg curl wget git tcptrace\
                python-pip python-thrift thrift-compiler goldeneye pip siege
wget https://atom.io/download/deb -O atom.deb
gdebi atom.deb
pip2 install kademlia rfc3987 marshmallow validators twisted tornado netifaces matplotlib
apt-get upgrade
