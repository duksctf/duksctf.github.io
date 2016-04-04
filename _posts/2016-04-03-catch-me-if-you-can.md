# Nuit Du Hack CTF Quals 2016 Catch me if you can writeup

## Description

> We managed to infect the computer of a target. We recorded all packets
> transferred over the USB port, but there is something unusual. We need them to
> be sorted to get the juicy secret.

## Details

Points:         **100**

Category:       **forensic**

Validations:    **50**

## Solution

We were given a file called [usb.pcap](/ressources/2016/ndh/catch_me_if_you_can/usb.pcap).
After digging around the file for a while it appears that it's a USB transfer of
several files.

We wrote a simple [python script](/ressources/2016/ndh/catch_me_if_you_can/extract_files.py) to extract the different blob with [scapy](http://www.secdev.org/projects/scapy/).

```python
#!/usr/bin/env python2

from scapy.all import *

pcap = rdpcap("usb.pcap")
for i,p in enumerate(pcap):
	if len(p) > 100:
		open(str(i),"wb").write(p.load[27:])
```

After analyzing those files, we found that there is **two** files in the transfer.
To reconstruct the two files, we simply use odd and even files for each. Here is
the [python script](/ressources/2016/ndh/catch_me_if_you_can/prepare_file.py) to do it:

```python
#!/usr/bin/env python2
from os.path import join
from os import listdir

working_dir = "working"

folder = []
files1 = []
files2 = []
for i in listdir(working_dir):
    folder.append(i)

folder.sort()
for i in folder:
    if int(i) % 2:
        files2.append(i)
    else:
        files1.append(i)

#reorder the blob
files1.sort()
files2.sort()

# create the files1
with open("files1.ods", "wb") as final_files1:

    # clean the sample
    for i in files1:
        final_files1.write(open(join(working_dir, i)).read(0x708))


# create the files2
with open("files2.ods", "wb") as final_files2:

    # clean the sample
    for i in files2:
        final_files2.write(open(join(working_dir, i)).read(0x708))
```

After running our script we were left with two files:
```
file files1.ods 
files1.ods: OpenDocument Spreadsheet
```
After opening the first file with [Libreoffice](https://fr.libreoffice.org/) we
were greated by:

![screenshot file1](/ressources/2016/ndh/catch_me_if_you_can/screen_file1.png "Screen file 1")

Fun isn't it...

Digging in the 2nd file is more profitable, it show us a sort of table with
alphabetic and letter:


![screenshot file2](/ressources/2016/ndh/catch_me_if_you_can/screen_file2.png "Screen file 2")

if you scroll to the **1048576** line vertical and to the top right most, yes there are
serious... you'll found a "code":
> g6d5g5f2b6g5d3e4d4b3c5b6k2j5j5g4l2 

Using this code with the weird alphbetical table give us the flag.

Challenges ressources are available in [ressources
folder](/ressources/2016/ndh/catch_me_if_you_can/)

