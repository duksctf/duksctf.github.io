#!/usr/bin/env python2

from scapy.all import *

pcap = rdpcap("usb.pcap")
for i,p in enumerate(pcap):
	if len(p) > 100:
		open(str(i),"wb").write(p.load[27:])

