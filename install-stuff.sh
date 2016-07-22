#!/bin/bash
#Install gcc and virtualbox guest additions first
apt-get update
apt-get install floodlight git mininet iptables wireshark nmap openssh-server goldeneye pip python-matplotlib python-netifaces d-itg
wget https://atom.io/download/deb -O atom.deb
gdebi atom.deb
pip2 install kademlia
apt-get upgrade
