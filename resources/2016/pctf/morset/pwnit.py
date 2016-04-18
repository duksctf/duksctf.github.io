#!/usr/bin/env python2
from pwn import *
from morse_talk import decode, encode
import binascii
import hashlib
from base36 import base36decode, base36encode

r = remote("morset.pwning.xxx", 11821)
p = r.recv()
print binascii.unhexlify("0{:02x}".format(base36decode(decode(p))))

temp = binascii.unhexlify("0{:02x}".format(base36decode(decode(p)))).split("SHA256(")[1][:-2]
print "to hash is: %s" % temp
h = hashlib.new("sha256")
h.update(temp)
print "hexdigest: %s" % h.hexdigest()
print "hexlified: %s" % binascii.hexlify(h.hexdigest())
print "base36ed: %s" % base36encode(int(binascii.hexlify(h.hexdigest()),16))

r.sendline(encode(base36encode(int(binascii.hexlify(h.hexdigest()),16))))

import time; time.sleep(1)
rep = r.recv().rstrip().strip()
print "rep is: %s" % rep
print binascii.unhexlify("{:02x}".format(base36decode(decode(rep))))

