---
layout: post
title: "Insomni'hack 2019 - INSFS"
mathjax: true

date: 2019-03-22

---

*A serial connection gives access to a basic filesystem. Repairing the filesystem with debug tools and adjusting an offset gives access to protected data.*

<!--more-->

### Description

We developped a brand-new, super modern, secure EEPROM filesystem.

It features things like:

* Fixed size files !
* Protected (?) storage space !
* Debug utilities !
* Basic commands !
* Filesystem verification (?)

Our secure©® Technology™ is secret and we are only allowed to give you a black box with some USB cables dangling out of it.

Please come to the hardware challenge table to use our product.

Notes:

*The serial speed is 9600 bauds.
If the board fails to connect over serial, or the filesystem breaks entirely, disconnect it completely and reconnect it. This resets the challenge.
Please use one cable per team.*

You should be able to access the device. Please tell if you are not able and we'll help you out.

You may need CP2102/CP2109 UART Bridge Controller drivers

Author: marc

### Details

Points:     500
Category:   Hardware

### Solution

The hardware itself was hidden in a plastic box, only USB cable were available.

After connecting to the serial port we got the following menu:


```
$ sudo minicom -D /dev/ttyUSB0
|_   _| \ | |/ ____|  ____/ ____| 
   | | |  \| | (___ | |__ | (___   
   | | | . ` |\___ \|  __| \___ \ 
  _| |_| |\  |____) | |    ____) |
 |_____|_| \_|_____/|_|   |_____/ 
      SUPER SECURE FILE SYSTEM COMMANDS 
(1) ls          - List files
(2) writef      - Write file 
(3) cat         - Get file content
------ Debug tools -----
(4) readmem     - Dumps memory 
(5) writeb      - Write byte 
(6) fschk       - Manually check filesystem

```

Unfortunately the file system commands were not working properly, only the debug tools. The **readmem** command gave the following result:

```
------Memory dump-------
00 00 00 00 00 00 00 00 00 00 00 00 00 40 00 00 00 00 00 00 00 00 00 00 00 00 ...
F1 7E 53 69 6D 70 6C 65 4E 6F 74 01 00 80 54 68 69 73 20 69 73 20 61 20 73 69 ...
F1 7E 46 69 6C 65 31 00 00 00 00 01 00 C0 46 69 6C 65 73 79 73 74 65 6D 20 63 ...  
F1 7E 54 6F 6F 6C 73 00 00 00 00 01 01 00 56 61 72 69 6F 75 73 20 66 75 6E 63 ...  
F1 7E 46 69 6C 65 00 00 00 00 00 01 01 40 53 69 6D 70 6C 65 20 66 69 6C 65 73 ...  
F1 7E 4D 6F 6E 69 65 73 00 00 00 01 01 80 47 6F 74 20 6C 69 6B 65 2C 20 35 20 ...  
F1 7E 66 69 6C 65 6E 61 6D 65 00 01 01 C0 57 65 6C 63 6F 6D 65 20 74 6F 20 69 ...  
F1 7E 53 65 63 75 72 65 00 00 00 01 00 00 54 68 69 73 20 73 79 73 74 65 6D 20 ...  
00 00 00 00 00 00 00 00 00 00 00 00 02 40 00 00 00 00 00 00 00 00 00 00 00 00 ...  
F1 7E 54 65 73 74 00 00 00 00 00 00 00 00 54 68 69 73 20 69 73 20 61 20 74 65 ...  
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ... 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ...
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ...
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ...
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ...
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ...
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ...
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ...
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ...
00 00 00 00 00 00 00 00 00 00 00 00 05 00 00 00 00 00 00 00 00 00 00 00 00 00 ...
END OF UNPROTECTED USER DATA...

```

We copy the dump in a file an we started to interpret the data:

```
$ hexdump file.bin -C
00000000  00 00 00 00 00 00 00 00  00 00 00 00 00 40 00 00  |.............@..|
00000010  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
*
00000040  f1 7e 53 69 6d 70 6c 65  4e 6f 74 01 00 80 54 68  |.~SimpleNot...Th|
00000050  69 73 20 69 73 20 61 20  73 69 6d 70 6c 65 20 6e  |is is a simple n|
00000060  6f 74 65 00 00 00 00 00  00 00 00 00 00 00 00 00  |ote.............|
00000070  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
00000080  f1 7e 46 69 6c 65 31 00  00 00 00 01 00 c0 46 69  |.~File1.......Fi|
00000090  6c 65 73 79 73 74 65 6d  20 63 68 65 63 6b 73 20  |lesystem checks |
000000a0  69 6d 70 6c 65 6d 65 6e  74 65 64 00 00 00 00 00  |implemented.....|
000000b0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
000000c0  f1 7e 54 6f 6f 6c 73 00  00 00 00 01 01 00 56 61  |.~Tools.......Va|
000000d0  72 69 6f 75 73 20 66 75  6e 63 74 69 6f 6e 73 20  |rious functions |
000000e0  61 72 65 20 61 76 61 69  6c 61 62 6c 65 00 00 00  |are available...|
000000f0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
00000100  f1 7e 46 69 6c 65 00 00  00 00 00 01 01 40 53 69  |.~File.......@Si|
00000110  6d 70 6c 65 20 66 69 6c  65 73 79 73 74 65 6d 00  |mple filesystem.|
00000120  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
*
00000140  f1 7e 4d 6f 6e 69 65 73  00 00 00 01 01 80 47 6f  |.~Monies......Go|
00000150  74 20 6c 69 6b 65 2c 20  35 20 6d 6f 6e 69 65 73  |t like, 5 monies|
00000160  20 69 6e 20 74 6f 74 61  6c 00 00 00 00 00 00 00  | in total.......|
00000170  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
00000180  f1 7e 66 69 6c 65 6e 61  6d 65 00 01 01 c0 57 65  |.~filename....We|
00000190  6c 63 6f 6d 65 20 74 6f  20 69 6e 73 31 39 00 00  |lcome to ins19..|
000001a0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
*
000001c0  f1 7e 53 65 63 75 72 65  00 00 00 01 00 00 54 68  |.~Secure......Th|
000001d0  69 73 20 73 79 73 74 65  6d 20 69 73 20 73 65 63  |is system is sec|
000001e0  75 72 65 20 69 20 73 77  65 61 72 00 00 00 00 00  |ure i swear.....|
000001f0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
00000200  00 00 00 00 00 00 00 00  00 00 00 00 02 40 00 00  |.............@..|
00000210  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
*
00000240  f1 7e 54 65 73 74 00 00  00 00 00 00 00 00 54 68  |.~Test........Th|
00000250  69 73 20 69 73 20 61 20  74 65 73 74 2e 20 44 6f  |is is a test. Do|
00000260  20 6e 6f 74 20 75 73 65  20 69 6e 20 70 72 6f 64  | not use in prod|
00000270  75 63 69 6f 6e 00 00 00  00 00 00 00 00 00 00 00  |ucion...........|
00000280  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
*
000004c0  00 00 00 00 00 00 00 00  00 00 00 00 05 00 00 00  |................|
000004d0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
*
00000500
```

We noticed that each file start with **f1 7e** the we have a file name on 9 bytes and then a number. For the first file named SimpleNot this number is 0x80 which match the size of the file since the following file starts at address 0x80. For the beginning of the filesystem we have a correct size but no filename. With the **writeb** command we write the correct header **f1 7e** at address 0x00 and 0x01 and then the **ls** command worked:

```
0x0040 - SimpleNot
0x0080 - File1
0x00C0 - Tools
0x0100 - File
0x0140 - Monies
0x0180 - filename
0x01C0 - Secure
```

After the file named Secure, the command did not display the following files. We noticed that the size was set to 0. Thus we changed it to 0x500 which is the end of the unprotected data. Then the command **ls** gives:

```
0x0040 - SimpleNot
0x0080 - File1
0x00C0 - Tools
0x0100 - File
0x0140 - Monies
0x0180 - filename
0x01C0 - Secure
0x0500 - STOP HERE
0x0540 - NOTHING
0x0580 - TO SEE
0x05C0 - INS{BADF5
0x0600 - _1N53_
0x0640 - CuR3}
0x0680 - 
```

The flag appears **INS{BADF5_1N53_CuR3}**
