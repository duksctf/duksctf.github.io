---
layout: post
title: "AlexCTF 2017 - Packed Movement"
date: 2017-02-04
---

*Elf binary asking for a flag. The binary was packed by [UPX](https://upx.github.io/) then poorly obfusctated using the [movfusator](https://github.com/xoreaxeaxeax/movfuscator), just looking at the assembly, a mov R2, 0xXX pattern appears, using a ida script to grab all mov R2 yield the flag.*

<!--more-->

### Description

*Being said that move instruction is enough to build a complete computer, anyway move on while you can.*

### Details

Points:      350

Category:    reverse

Validations: 99

### Solution

We were given a binary file called [move](/resources/2017/alexctf/packed_movement/move).
Some recon:

``` bash
-> $ file move
move: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.2, not stripped

-> $ strings move_upx
UPX!
/lib
nux.so.2
6	msigaction
trle
read
GmXs
LIBC_2.0@
7%Ah
pr g
C@&;
YIiF
'?F!
s\"{
```
Oh, first string showed that the binary was packed using [UPX](https://upx.github.io/)...

``` bash
-> $ upx -d move 
                       Ultimate Packer for eXecutables
                          Copyright (C) 1996 - 2013
UPX 3.91        Markus Oberhumer, Laszlo Molnar & John Reiser   Sep 30th 2013

        File size         Ratio      Format      Name
   --------------------   ------   -----------   -----------
  10308504 <-   2779568   26.96%  netbsd/elf386  move

Unpacked 1 file.
```
Opening the binary in IDA showes a mass of *mov* instructions which remains us the talk gave by [doma](https://twitter.com/xoreaxeaxeax) at recon on [movfuscator](https://github.com/xoreaxeaxeax/movfuscator):

<img src="/resources/2017/alexctf/packed_movement/ida_start.png" width="800">

Looking at this mess, a pattern was found. There is a suspicious *mov   R2,
0x41*, 0x41 = A in ASCII, it looks like it's the first bytes of the ALEXCTF{}
flag format.

We used a simple IDAPython script to search for this instruction and then get
the operand value:

``` python
import idaapi
import idc
start = 0x0804829C
flag = ""
while True:

    ea = idc.FindText(start,3 , 0, 0, "mov     R2, ")
    if ea:
        if idc.GetOperandValue(ea, 1) > 255:
            break
        flag += chr(idc.GetOperandValue(ea, 1))
    start = ea + 10
    if ea == idc.BADADDR:
        break

print flag
```

 
The flag was: **ALEXCTF{M0Vfusc4t0r_w0rk5_l1ke_m4g1c}**

Challenges resources are available in the [resources
folder](https://github.com/duksctf/duksctf.github.io/tree/master/resources/2017/alexctf/packed_movement)
