#!/usr/bin/env python2
from itertools import izip

a = "732298B81C9D7F70E9BE3F307EA220BEE093BB1C7A"
b = "2A6CD7EC2DAA0422BCF060604DFD11EDBFD5EE5207"

flag = ''.join(chr(ord(c)^ord(k)) for c,k in izip(a.decode("hex"), b.decode("hex")))

print flag
