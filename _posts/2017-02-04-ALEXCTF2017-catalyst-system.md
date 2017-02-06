---
layout: post
title: "AlexCTF 2017 - Catalyst System"
date: 2017-02-04
---

*Elf binary asking for username/password, the username is used to compute a
seed to srand, which then get use to substract rand() with every 4 bytes of the
password.*

<!--more-->

### Description

*CEO of catalyst systems decided to build his own log in system from scratch, he thought that it is so safe that no one can fool around with him!*

### Details

Points:      150

Category:    reverse

Validations: 201

### Solution

We were given a binary file [catalyst](/resources/2017/alexctf/catalyst_system/catalyst).
Some recon:

``` bash
-> $ file catalyst 
catalyst: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 2.6.32, BuildID[sha1]=3c4646c45da147f57cfa3fe0b9f1022d84fbe85f, stripped

-> $ strings catalyst 
REDACTED
/lib64/ld-linux-x86-64.so.2
libc.so.6
fflush
puts
time
putchar
printf
strlen
your flag is: ALEXCTF{
invalid username or password
```
Runing the binary shows that some delay has been added during the beginning:

<img src="/resources/2017/alexctf/catalyst_system/ida_start.png" width="800">

We patched the *jmp short loc_400EA5* and the *jmp short loc_400F5E* to jump
after the boring *sleep* function using [keypatch](https://github.com/keystone-engine/keypatch) whic is a plugin to patch binary directly in IDA using real assembly language and not opcode:

<img src="/resources/2017/alexctf/catalyst_system/keypatch.png" width="800">

Here is the graph of the patched binary without the pesky *sleep* function:

<img src="/resources/2017/alexctf/catalyst_system/ida_result.png" width="800">

After removing the function we started looking at the username parsing. It do
some calcuation on the bytes in order to validate it, this looks like a perfect
case for enhancing our skills with [angr](http://angr.io/) which is a symbolic
execution framework.

Here is the python script to retrieve the username:

``` python
import angr
import sys
p = angr.Project('./catalyst',  load_options={'auto_load_libs': False})
main = 0x400D93

init = p.factory.blank_state(addr=main)

def hook_printf(state):
    pass

p.hook(0x00400DCD, hook_printf,length=5)
p.hook(0x00400DD7, hook_printf,length=5)
p.hook(0x00400DE1, hook_printf,length=5)
p.hook(0x00400DEB, hook_printf,length=5)
p.hook(0x00400DF5, hook_printf,length=5)
p.hook(0x00400DFF, hook_printf,length=5)
p.hook(0x00400E09, hook_printf,length=5)
p.hook(0x00400E13, hook_printf,length=5)
p.hook(0x00400E1D, hook_printf,length=5)
p.hook(0x00400e27, hook_printf,length=5)
p.hook(0x00400e31, hook_printf,length=5)
p.hook(0x00400e3b, hook_printf,length=5)


pg = p.factory.path_group(init, threads=8)
ex = pg.explore(find=(0x00400D92, ), avoid=(0x00400D7C, 0x00400C83))

if ex.found:
    print ex.found[0].state.posix.dumps(0)
```

We hooked the *puts* function because it looks like angr's implement was buggy.
Running our script gave us the username:

``` bash
-> $ ./get_username.py  
catalyst_ceoÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀ`ÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀÀ
```
So the username was *catalyst_ceo*.

Now we need to find the password. Looking again in the binary, the function
*sub_400977* use srand which is seeded by the sum of the three first bytes of
the username.

<img src="/resources/2017/alexctf/catalyst_system/ida_last.png" width="800">

After the srand, several *rand()* was substracted to some constants.
We wrote a simple C program in order to get the value for *srand()* the we
added the value with constants to generate the password:

``` c
#include <stdio.h>
#include <stdlib.h>


int main()
{
    srand(1162690094);
    printf("rand0: %d\n", rand());
    printf("rand1: %d\n", rand());
    printf("rand2: %d\n", rand());
    printf("rand3: %d\n", rand());
    printf("rand4: %d\n", rand());
    printf("rand5: %d\n", rand());
    printf("rand6: %d\n", rand());
    printf("rand7: %d\n", rand());

    printf("rand8: %d\n", rand());
    printf("rand9: %d\n", rand());
}
```
And the python script to get the flag:

``` python
#!/usr/bin/env python2
from struct import pack

password = ""

password += pack('<I', (6833993 + 0x55EB052A) & 0xffffffff)
password += pack('<I', (1732044087 + 0x0EF76C39)& 0xffffffff)
password += pack('<I', (2068121063 + 0xCC1E2D64)& 0xffffffff)
password += pack('<I', (1889579618 + 0xC7B6C6F5)& 0xffffffff)
password += pack('<I', (869606716 + 0x26941BFA)& 0xffffffff)
password += pack('<I', (1364883061 + 0x260CF0F3)& 0xffffffff)
password += pack('<I', (1500347741 + 0x10D4CAEF)& 0xffffffff)
password += pack('<I', (2094174281 + 0x0C666E824)& 0xffffffff)
password += pack('<I', (1508322742 + 0x0FC89459C)& 0xffffffff)
password += pack('<I', (1179934733 + 0x2413073A)& 0xffffffff)
print password
```
Using the username and password gave us the flag:

``` Bash
-> $ ./catalyst
 ▄▄▄▄▄▄▄▄▄▄▄  ▄            ▄▄▄▄▄▄▄▄▄▄▄  ▄       ▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄ 
▐░░░░░░░░░░░▌▐░▌          ▐░░░░░░░░░░░▌▐░▌     ▐░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌
▐░█▀▀▀▀▀▀▀█░▌▐░▌          ▐░█▀▀▀▀▀▀▀▀▀  ▐░▌   ▐░▌ ▐░█▀▀▀▀▀▀▀▀▀  ▀▀▀▀█░█▀▀▀▀ ▐░█▀▀▀▀▀▀▀▀▀ 
▐░▌       ▐░▌▐░▌          ▐░▌            ▐░▌ ▐░▌  ▐░▌               ▐░▌     ▐░▌          
▐░█▄▄▄▄▄▄▄█░▌▐░▌          ▐░█▄▄▄▄▄▄▄▄▄    ▐░▐░▌   ▐░▌               ▐░▌     ▐░█▄▄▄▄▄▄▄▄▄ 
▐░░░░░░░░░░░▌▐░▌          ▐░░░░░░░░░░░▌    ▐░▌    ▐░▌               ▐░▌     ▐░░░░░░░░░░░▌
▐░█▀▀▀▀▀▀▀█░▌▐░▌          ▐░█▀▀▀▀▀▀▀▀▀    ▐░▌░▌   ▐░▌               ▐░▌     ▐░█▀▀▀▀▀▀▀▀▀ 
▐░▌       ▐░▌▐░▌          ▐░▌            ▐░▌ ▐░▌  ▐░▌               ▐░▌     ▐░▌          
▐░▌       ▐░▌▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄▄▄  ▐░▌   ▐░▌ ▐░█▄▄▄▄▄▄▄▄▄      ▐░▌     ▐░▌          
▐░▌       ▐░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌     ▐░▌▐░░░░░░░░░░░▌     ▐░▌     ▐░▌          
 ▀         ▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀       ▀  ▀▀▀▀▀▀▀▀▀▀▀       ▀       ▀           
Welcome to Catalyst systems
Loading
Username: catalyst_ceo
Password: sLSVpQ4vK3cGWyW86AiZhggwLHBjmx9CRspVGggj
Logging in
your flag is: ALEXCTF{1_t41d_y0u_y0u_ar3__gr34t__reverser__s33}
```

 
The flag was: **ALEXCTF{1_t41d_y0u_y0u_ar3__gr34t__reverser__s33}**

Challenges resources are available in the [resources
folder](https://github.com/duksctf/duksctf.github.io/tree/master/resources/2017/alexctf/catalyst_system)
