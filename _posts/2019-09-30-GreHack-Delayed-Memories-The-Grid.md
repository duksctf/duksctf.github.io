---
layout: post
title: "GreHAck 2019 - Delayed Memories - The Grid"
mathjax: true

date: 2019-09-30

---

* Three different way to solve a reverse challenge. *

<!--more-->

### Description

The flag doesn't follow any particular format.

DOWNLOAD FILE 

### Solution

We were given a [binary](/resources/2019/grehack/thegrid/thegrid_80f6b0f70565a2de15eab05c3ad603d18399bc2af1eabf870da6f2e4955b2a17) without much information.

```bash
$ r2 thegrid_80f6b0f70565a2de15eab05c3ad603d18399bc2af1eabf870da6f2e4955b2a17 
[0x000010c0]> ia
arch     x86
baddr    0x0
binsz    13820
bintype  elf
bits     64
canary   false
class    ELF64
compiler GCC: (Debian 9.2.1-4) 9.2.1 20190821
crypto   false
endian   little
havecode true
intrp    /lib64/ld-linux-x86-64.so.2
laddr    0x0
lang     c
linenum  false
lsyms    false
machine  AMD x86-64 architecture
maxopsz  16
minopsz  1
nx       true
os       linux
pcalign  0
pic      true
relocs   false
relro    partial
rpath    NONE
sanitiz  false
static   false
stripped true
subsys   linux
va       true
```

Neverthe less the strings were interesting:

```
[0x000010c0]> iz
[Strings]
nth paddr      vaddr      len size section type  string
―――――――――――――――――――――――――――――――――――――――――――――――――――――――
0   0x00002004 0x00002004 19  20   .rodata ascii You can't go there!
1   0x00002018 0x00002018 17  18   .rodata ascii Usage: %s <flag>\n
2   0x0000202a 0x0000202a 21  22   .rodata ascii You lost your way ...
3   0x00002040 0x00002040 9   10   .rodata ascii Nice job!
0   0x00003060 0x00004060 23  24   .data   ascii OOOOAOO|||||OOOOOOOOOOO
1   0x00003078 0x00004078 23  24   .data   ascii OO OOOO|||||OOOOO OOOOO
2   0x00003090 0x00004090 23  24   .data   ascii OO OAOA|||||OOOOO OOOOO
3   0x000030a8 0x000040a8 23  24   .data   ascii O  OOOO|          !!OOO
4   0x000030c0 0x000040c0 23  24   .data   ascii O OOOOO| |!!!!!!!!!!OOO
5   0x000030d8 0x000040d8 23  24   .data   ascii O O//OA| |!!!!!!!!!!OOO
6   0x000030f0 0x000040f0 23  24   .data   ascii O O//OO|        !!!!OOO
7   0x00003108 0x00004108 23  24   .data   ascii O OOOOO|||!!!!! !!!!OOO
8   0x00003120 0x00004120 23  24   .data   ascii O OOOOO|||||AAA AAOOOOO
9   0x00003138 0x00004138 23  24   .data   ascii O     ||||||AAA AAOOOOO
10  0x00003150 0x00004150 23  24   .data   ascii O---- ||||||AAA      OO
11  0x00003168 0x00004168 23  24   .data   ascii OOO|  ||||||AAAAAAOO OO
12  0x00003180 0x00004180 23  24   .data   ascii OOO| |||||||AAAAAAOO OO
13  0x00003198 0x00004198 23  24   .data   ascii OOO| |OOA|AAAAAAAAOO OO
14  0x000031b0 0x000041b0 23  24   .data   ascii OOO| |OOA|AAAAAAAAOO OO
15  0x000031c8 0x000041c8 23  24   .data   ascii OOO| |OOO|||||||||OO OO
16  0x000031e0 0x000041e0 23  24   .data   ascii OOO| |_____OO|||||OO OO
17  0x000031f8 0x000041f8 23  24   .data   ascii OOO|       |O|||||OO OO
18  0x00003210 0x00004210 23  24   .data   ascii OOO------| |O|||||OO OO
19  0x00003228 0x00004228 23  24   .data   ascii OOXXXXXXO| |O|||||   OO
20  0x00003240 0x00004240 23  24   .data   ascii OOO//XXXO|         OOOO
21  0x00003258 0x00004258 23  24   .data   ascii OOO//XXXO| OO|||||OOOOO
22  0x00003270 0x00004270 23  24   .data   ascii OOO!!XXXO| OO|||||OOOOO
23  0x00003288 0x00004288 23  24   .data   ascii OOO!!XXXO  OO||//////OO
24  0x000032a0 0x000042a0 23  24   .data   ascii OOO!!OOOO OOO||//////OO
25  0x000032b8 0x000042b8 23  24   .data   ascii OO        OOO|||||||OOO
26  0x000032d0 0x000042d0 23  24   .data   ascii OO !!OO OOOOO|||||O|OOO
27  0x000032e8 0x000042e8 23  24   .data   ascii OO !!OO OOOOO|||||O|OOO
28  0x00003300 0x00004300 23  24   .data   ascii OO !!OO OOOOOOOOOOO|OOO
29  0x00003318 0x00004318 23  24   .data   ascii OO OOOO       OOOOO|OOO
30  0x00003330 0x00004330 23  24   .data   ascii OO OOOOOOOOOO OOOOO|OOO
31  0x00003348 0x00004348 23  24   .data   ascii OO O|||||OOOO   OOO|OOO
32  0x00003360 0x00004360 23  24   .data   ascii OO O|||||OOOOOO OOO|OOO
33  0x00003378 0x00004378 23  24   .data   ascii OO O|||||OOOOO  OOO|OOO
34  0x00003390 0x00004390 23  24   .data   ascii OO O||||       OOOO|OOO
35  0x000033a8 0x000043a8 23  24   .data   ascii OO O|||||OOOOO OOOO|OOO
36  0x000033c0 0x000043c0 23  24   .data   ascii OO O|||||OOOOO OOOOOOOO
37  0x000033d8 0x000043d8 23  24   .data   ascii OO O|||||OOOOO     OOOO
38  0x000033f0 0x000043f0 23  24   .data   ascii OO  |||||OOOOOOOOO OOOO
39  0x00003408 0x00004408 23  24   .data   ascii OOO |||||OOOOOOOOO OOOO
40  0x00003420 0x00004420 23  24   .data   ascii OOO         OOOOOO OOOO
41  0x00003438 0x00004438 23  24   .data   ascii OOOO|||||OOOOOOOOO OOOO
42  0x00003450 0x00004450 23  24   .data   ascii OOOO|||||OOOOOOOOO OOOO
43  0x00003468 0x00004468 23  24   .data   ascii OOOO|||||OOOOOOOO  OOOO
44  0x00003480 0x00004480 23  24   .data   ascii O////////OOOOOOOO O   O
45  0x00003498 0x00004498 23  24   .data   ascii O////////OOOOOOOO   O O
46  0x000034b0 0x000044b0 23  24   .data   ascii O////////OOOOOOOOOOOO O
47  0x000034c8 0x000044c8 23  24   .data   ascii OOOOOOOOOOOOOOOOOOOOOOO
```

They seems to represent a maze.
We were three people to participate to the challenge and we found three diffrent method to
solve it.

### First method



