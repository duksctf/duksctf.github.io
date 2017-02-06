---
layout: post
title: "AlexCTF 2017 - Unknown Format"
date: 2017-02-04
---

*We received a USB PCAP of an update transaction between a computer and Amazon
Kindle. After reconstructing the update, we used a tool called KindleTool in
order to deobfuscate the binary, then we used some python code to inflate the
malformed gzip inside.*

<!--more-->

### Description

*Once more our agents managed to sniff data passed over USB, they told us that this is high profile data hidden by people knows what they are doing, they have dedicated devices for reading that secret file format. Can you help us finding what is the secret message?*

### Details

Points:      200

Category:    forensic

Validations: 54

### Solution

We were given a file called [usb_sniff.pcap](/resources/2017/alexctf/unknown_format/usb_sniff.pcap).
After digging around the file for a while it appears that it's a USB transfer of
several files.
We looked on google first bytes of the transfer "SP01 and FC04" which led us to a github
account [KindleTool](https://github.com/NiLuJe/KindleTool) from NiLuJe. This
tool help of reversing of image for many Kindle format.

<img src="/resources/2017/alexctf/unknown_format/usb_pcap.png" width="800">

We extracted first two packet of 
[URB's](https://www.kernel.org/doc/Documentation/usb/URB.txt)  and then we reconstructed the image with cat:

``` bash
cat packet1.bin packet.bin > packet.bin

```

After compiling the tool we tried some command to extract or convert the update
without luck.
We used the convert with *-w option* to unwrapp the signatures header and then the *dm* to deobfuscate the binary.
After reading the code of KindleTool, we found that after the *FC04* and some
bytes there is a gziped sections of data.

<img src="/resources/2017/alexctf/unknown_format/gzip_header.png" width="800">

We used *dd* to extract the broken gziped archive: 

``` bash
dd if=packet.bin of=broken.bin skip=1 bs=254
```
We tried to extract it with *tar xvf* whic didn't works.
We used then a simple python script from [stackoverflow](https://stackoverflow.com/questions/26794514/how-to-extract-data-from-corrupted-gzip-files-in-python):

``` python
# http://stackoverflow.com/questions/2423866/python-decompressing-gzip-chunk-by-chunk
# http://stackoverflow.com/questions/3122145/zlib-error-error-3-while-decompressing-incorrect-header-check/22310760

def read_corrupted_file(filename, CHUNKSIZE=1024):
    d = zlib.decompressobj(zlib.MAX_WBITS | 32)
    with open(filename, 'rb') as f:
        result_str = ''
        buffer=f.read(CHUNKSIZE)
        try:
            while buffer:
                result_str += d.decompress(buffer)
                buffer=f.read(CHUNKSIZE)
        except Exception as e:
            print 'Error: %s -> %s' % (filename, e.message)
        return result_str

In [3]: read_corrupted_file("broken.bin")
REDACTED
0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00ALEXCTF{Wh0_N33d5_K1nDl3_t0_3X7R4Ct_K1ND13_F1rMw4R3}\n\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00

```
The flag was: **ALEXCTF{Wh0_N33d5_K1nDl3_t0_3X7R4Ct_K1ND13_F1rMw4R3}**

Challenges resources are available in the [resources
folder](https://github.com/duksctf/duksctf.github.io/tree/master/resources/2017/alexctf/unkown_format)

