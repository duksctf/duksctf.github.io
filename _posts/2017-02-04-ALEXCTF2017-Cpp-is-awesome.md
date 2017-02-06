---
layout: post
title: "AlexCTF 2017 - CPP is awesome"
date: 2017-02-04
---

*C++ binary with weird strings inside, using a table of indexes with this
strings led us to the flag.*

<!--more-->

### Description

*They say C++ is complex, prove them wrong!*

### Details

Points:      100

Category:    reverse

Validations: 346

### Solution

We were given a file called [re2](/resources/2017/alexctf/cpp-is-awesome/re2).
Some recon:

``` bash
-> $ file  re2
re2: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 2.6.32, BuildID[sha1]=08fba98083e7c1f7171fd17c82befdfe1dcbcc82, stripped

-> $ strings re2
REDACTED
CXXABI_1.3
GLIBCXX_3.4.21
GLIBCXX_3.4
GLIBC_2.2.5
UH-@!`
AWAVA
AUATL
[]A\A]A^A_
L3t_ME_T3ll_Y0u_S0m3th1ng_1mp0rtant_A_{FL4G}_W0nt_b3_3X4ctly_th4t_345y_t0_c4ptur3_H0wev3r_1T_w1ll_b3_C00l_1F_Y0u_g0t_1t
Better luck next time
You should have the flag by now
Usage: 
 flag
;*3$"
```
A string look very promising: *L3t_ME_T3ll_Y0u_S0m3th1ng_1mp0rtant_A_{FL4G}_W0nt_b3_3X4ctly_th4t_345y_t0_c4ptur3_H0wev3r_1T_w1ll_b3_C00l_1F_Y0u_g0t_1t*
Opening the binary in IDA, then using the decompiler shows an non-obfuscated binary:

<img src="/resources/2017/alexctf/cpp-is-awesome/ida_start.png">

The code *if ( (_BYTE)v9 != off_6020A0[dword_6020C0[v15]] )* check if the input is equal the byte from the pointer *off_6020A0* which points to the interesting string found during the recon.
It use a table of offset located at *dword_6020C0*. With all those information it's easy to decrypt the flag with some lines of python:

``` python
#!/usr/bin/env python2

key = "L3t_ME_T3ll_Y0u_S0m3th1ng_1mp0rtant_A_{FL4G}_W0nt_b3_3X4ctly_th4t_345y_t0_c4ptur3_H0wev3r_1T_w1ll_b3_C00l_1F_Y0u_g0t_1t"

offset = [0x24, 0x0, 0x5, 0x36,0x65,0x07,0x27,0x26,0x2D,0x01,0x03,0x0,0x0D,0x56,0x01,0x03,0x65,0x03,0x2D,0x16,0x02,0x15,0x03,0x65,0x00,0x29,0x44,0x44,0x01,0x44,0x2B]

flag =  ""
for i in offset:
     flag += key[i]
print flag
```
The flag was: **ALEXCTF{W3_L0v3_C_W1th_CL45535}**

Challenges resources are available in the [resources
folder](https://github.com/duksctf/duksctf.github.io/tree/master/resources/2017/alexctf/cpp-is-awesome)
