---
layout: post
title: "GreHAck 2019 - Delayed Memories - The Grid"
mathjax: true

date: 2019-09-30

---

*Reverse challenge which is finally a maze. A move is encoded on 2 bit of a charactere given as input. The combination which gets you out of the maze is the flag.*

<!--more-->

### Description

The flag doesn't follow any particular format.

[DOWNLOAD FILE](/resources/2019/grehack/thegrid/thegrid_80f6b0f70565a2de15eab05c3ad603d18399bc2af1eabf870da6f2e4955b2a17)

### Solution

We were given a [binary](/resources/2019/grehack/thegrid/thegrid_80f6b0f70565a2de15eab05c3ad603d18399bc2af1eabf870da6f2e4955b2a17) without much information.

```shell
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

Nevertheless the strings were interesting:

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

We first noticed that the given argument should be 11 characters long or the program exits:
```nasm
0x0000126b          xor eax, eax                ; arg2                                                                                                                            
0x0000126d          repne scasb al, byte [rdi]                                                                                                                                    
0x0000126f          cmp rcx, 0xfffffffffffffff3                                                                                                                                   
0x00001273          jne 0x12cb
```

Then the program iterate over each characters of the argument until it reaches the null character:
<img src="/resources/2019/grehack/thegrid/move_code.png" width="800">

If a wrong input is given the binary complains:

```
[0x7ffff7dd6090]> ood aaaaaaaaaaa
Wait event received by different pid 22071
Process with PID 22072 started...
= attach 22072 22072
[0x7ffff7dd6090]> dc
hit breakpoint at: 55555555527d
[0x55555555527d]> dc
You can't go there!
[0x555555558060]> b 1130
[0x555555558060]> s 0x555555558060; psb
0x555555558060 OOOOAOO|||||OOOOOOOOOOO
0x555555558077 OO OOOO|||||OOOOO OOOOO
0x55555555808f OO OAOA|||||OOOOO OOOOO
0x5555555580a7 O  OOOO|          !!OOO
0x5555555580bf O OOOOO| |!!!!!!!!!!OOO
0x5555555580d7 O O//OA| |!!!!!!!!!!OOO
0x5555555580ef O O//OO|        !!!!OOO
0x555555558107 O OOOOO|||!!!!! !!!!OOO
0x55555555811f O OOOOO|||||AAA AAOOOOO
0x555555558137 O     ||||||AAA AAOOOOO
0x55555555814f O---- ||||||AAA      OO
0x555555558167 OOO|  ||||||AAAAAAOO OO
0x55555555817f OOO| |||||||AAAAAAOO OO
0x555555558197 OOO| |OOA|AAAAAAAAOO OO
0x5555555581af OOO| |OOA|AAAAAAAAOO OO
0x5555555581c7 OOO| |OOO|||||||||OO OO
0x5555555581df OOO| |_____OO|||||OO OO
0x5555555581f7 OOO|       |O|||||OO OO
0x55555555820f OOO------| |O|||||OO OO
0x555555558227 OOXXXXXXO| |O|||||   OO
0x55555555823f OOO//XXXO|         OOOO
0x555555558257 OOO//XXXO| OO|||||OOOOO
0x55555555826f OOO!!XXXO| OO|||||OOOOO
0x555555558287 OOO!!XXXO  OO||//////OO
0x55555555829f OOO!!OOOO OOO||//////OO
0x5555555582b7 OO        OOO|||||||OOO
0x5555555582cf OO !!OO OOOOO|||||O|OOO
0x5555555582e7 OO !!OO OOOOO|||||O|OOO
0x5555555582ff OO !!OO OOOOOOOOOOO|OOO
0x555555558317 OO OOOO       OOOOO|OOO
0x55555555832f OO OOOOOOOOOO OOOOO|OOO
0x555555558347 OO O|||||OOOO   OOO|OOO
0x55555555835f OO O|||||OOOOOO OOO|OOO
0x555555558377 OO O|||||OOOOO  OOO|OOO
0x55555555838f OO O||||       OOOO|OOO
0x5555555583a7 OO O|||||OOOOO OOOO|OOO
0x5555555583bf OO O|||||OOOOO OOOOOOOO
0x5555555583d7 OO O|||||OOOOO     OOOO
0x5555555583ef OO  |||||OOOOOOOOO OOOO
0x555555558407 OOO |||||OOOOOOOOO OOOO
0x55555555841f OOO         OOOOOO OOOO
0x555555558437 OOOO|||||OOOOOOOOO OOOO
0x55555555844f OOOO|||||OOOOOOOOO OOOO
0x555555558467 OOOO|||||OOOOOOOO  OOOO
0x55555555847f O////////OOOOOOOO O  XO
0x555555558497 O////////OOOOOOOO   OXO
0x5555555584af O////////OOOOOOOOOOOO O
```

BUt we noticed that some **X** characters appear at the end of the maze. After playing a bit with
the argument we suposed that the goal was to move up to the top of the maze and each character
would make a move of the cursor in the maze. According to the assembly:

```nasm
0x555555555275      mov dil, byte [rbx]
0x555555555278      test dil, dil
0x55555555527b      je 0x5555555552b7
0x55555555527d      shr edi, 6
0x555555555280      inc rbx
0x555555555283      and edi, 3
0x555555555286      call 0x5555555551fa
0x55555555528b      movsx edi, byte [rbx - 1]
0x55555555528f      sar edi, 4
0x555555555292      and edi, 3
0x555555555295      call 0x5555555551fa
0x55555555529a      movsx edi, byte [rbx - 1]
0x55555555529e      sar edi, 2
0x5555555552a1      and edi, 3
0x5555555552a4      call 0x5555555551fa
0x5555555552a9      mov dil, byte [rbx - 1]
0x5555555552ad      and edi, 3
0x5555555552b0      call 0x5555555551fa
0x5555555552b5      jmp 0x555555555275
```

We noticed that the character is first right shifted by 6 and only the two last bits are kept. Then a function is called.
Then the character is shifted by 4 and the two last bits are kept and the same function is called and so on. Thus we supposed that 
the function at **0x5555555551fa** was a move function which takes 2 bits of the character as input.

After debugging a bit with several character we could figure out which move matches which 2-bit value:

|----|------------|
|0   | **Left**   |
|1   | **Up**     |
|2   | **Right**  |
|3   | **Down**   |

Notice that one character was **@** and to pass it as a parameter in radare2 you have to use a double quote else it is interpreted as an address:

```shell
[0x000010c0]> "ood LeAd@Ze@VAY"
Process with PID 6486 started...
= attach 6486 6486
[0x7f92a9ded090]> dc
Nice job!
```

And the parameter is the flag to submit.
