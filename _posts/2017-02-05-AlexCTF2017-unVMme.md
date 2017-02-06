---
layout: post
title: AlexCTF 2017 - unVM me
date: 2017-02-05
---

*A Python byte code file was provided without the source code. After its decompilation, we noticed that each 5-byte slice of the flag was hash with MD5 and compared. After brute forcing the hashes contained in the file we got the flag.*

<!--more-->

### Description

*If I tell you what version of python I used .. where is the fun in that?*

*Attachment: [unvm_me.pyc](/resources/2017/alexctf/unvmme/unvm_me.pyc)*


### Details

Points:      250 

Category:    reverse

Validations: 334

### Solution

Runing the program with Python 2 gave:

```bash
$ python unvm_me.pyc
Can you turn me back to python ? ...
well as you wish.. what is the flag: 123456789
nice try
```

I used [uncompyle2](https://github.com/wibiti/uncompyle2) to have the corresponding source code:


```bash
$ uncompyle2 unvm_me.pyc
# 2017.02.04 20:16:49 CET
#Embedded file name: unvm_me.py
import md5
md5s = [174282896860968005525213562254350376167L,
 137092044126081477479435678296496849608L,
 126300127609096051658061491018211963916L,
 314989972419727999226545215739316729360L,
 256525866025901597224592941642385934114L,
 115141138810151571209618282728408211053L,
 8705973470942652577929336993839061582L,
 256697681645515528548061291580728800189L,
 39818552652170274340851144295913091599L,
 65313561977812018046200997898904313350L,
 230909080238053318105407334248228870753L,
 196125799557195268866757688147870815374L,
 74874145132345503095307276614727915885L]
print 'Can you turn me back to python ? ...'
flag = raw_input('well as you wish.. what is the flag: ')
if len(flag) > 69:
    print 'nice try'
    exit()
if len(flag) % 5 != 0:
    print 'nice try'
    exit()
for i in range(0, len(flag), 5):
    s = flag[i:i + 5]
    if int('0x' + md5.new(s).hexdigest(), 16) != md5s[i / 5]:
        print 'nice try'
        exit()

print 'Congratz now you have the flag'
+++ okay decompyling unvm_me.pyc 
# decompiled 1 files: 1 okay, 0 failed, 0 verify failed
# 2017.02.04 20:16:49 CET
```

So each 5 bytes of the input flag is hash with md5 and compared with hardcoded hashes in the file. I used the [HashKiller.co.uk](https://hashkiller.co.uk/md5-decrypter.aspx) to bruteforce the MD5 hashes and I obtained the flag:

**ALEXCTF{dv5d4s2vj8nk43s8d8l6m1n5l67ds9v41n52nv37j481h3d28n4b6v3k}**

