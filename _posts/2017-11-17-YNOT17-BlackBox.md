---
layout: post
title: "Y-Not-CTF - BlackBox"
mathjax: true

date: 2017-11-17
---

*The binary ask for a password and use RunPE technic to create a new process. Two technic can be used, first is to dump the PE when the program copy it, second is to break on SetThreadContext and put a breakpoint on the new entrypoint.*

<!--more-->

### Description

*An idea is like a virus. Resilient. Highly contagious. And even the smallest seed of an idea can grow. It can grow to define or destroy you. (quote Inception movie)*

### Details

Points:      474

Category:    reverse

Validations: 4

### Solution

We were given a file called [blackbox.exe](/resources/2017/ynotctf/blackbox/blackbox_9d4eede1603846f7cf5acd389a4f9a2bc92fd6b3.exe).

After launching the file a password is asked.

```
C:\Users\test\Desktop>blackbox_9d4eede1603846f7cf5acd389a4f9a2bc92fd6b3.exe
Enter password: aaa
Bad password!
```

Opening the file in ida pro shown an interesting technic used by malware to
thwart antivirus. the main code looks like this:

```c
int __cdecl main(int argc, const char **argv, const char **envp)
{
  int v3; // ecx
  DWORD v4; // eax
  char v6; // [esp+0h] [ebp-1Ch]

  dword_436CA0 = (int (__stdcall *)(_DWORD, _DWORD))WaitForSingleObject;
  sub_401020("Enter password: ", v6);
  sub_401050("%21s", &v6);
  v4 = sub_401090(v3, &v6);
  dword_436CA0(v4, -1);
  return 0;
}

```

The password seems to be 21 char long and the verification seems to be in
sub_401090:

```c
DWORD __fastcall sub_401090(int a1, CHAR *a2)
{
  CHAR *v2; // edi
  signed int v3; // eax
  int v4; // esi
  DWORD result; // eax
  CONTEXT *v6; // eax
  const CONTEXT *v7; // edi
  int v8; // ebx
  signed int v9; // edi
  CONTEXT *v10; // [esp+8h] [ebp-464h]
  char *v11; // [esp+Ch] [ebp-460h]
  char Buffer; // [esp+10h] [ebp-45Ch]
  struct _PROCESS_INFORMATION ProcessInformation; // [esp+14h] [ebp-458h]
  struct _STARTUPINFOA StartupInfo; // [esp+24h] [ebp-448h]
  CHAR Filename; // [esp+68h] [ebp-404h]

  v2 = a2;
  v3 = 0;
  do
    dword_41E8B0[v3++] ^= 0xFEu;
  while ( v3 < 96768 );
  v4 = dword_41E8EC;
  result = GetModuleFileNameA(0, &Filename, 0x400u);
  if ( *(_DWORD *)&dword_41E8B0[v4] == 'EP' )
  {
    ProcessInformation = 0i64;
    memset(&StartupInfo, 0, 0x44u);
    result = CreateProcessA(&Filename, v2, 0, 0, 0, 4u, 0, 0, &StartupInfo, &ProcessInformation);
    if ( result )
    {
      v6 = (CONTEXT *)VirtualAlloc(0, 4u, 0x1000u, 4u);
      v7 = v6;
      v10 = v6;
      v6->ContextFlags = 65543;
      result = GetThreadContext(ProcessInformation.hThread, v6);
      if ( result )
      {
        ReadProcessMemory(ProcessInformation.hProcess, (LPCVOID)(v7->Ebx + 8), &Buffer, 4u, 0);
        v11 = (char *)VirtualAllocEx(
                        ProcessInformation.hProcess,
                        *(LPVOID *)((char *)&dword_41E8E4 + v4),
                        *(int *)((char *)&dword_41E900 + v4),
                        0x3000u,
                        0x40u);
        WriteProcessMemory(ProcessInformation.hProcess, v11, dword_41E8B0, *(int *)((char *)&dword_41E904 + v4), 0);
        if ( *(unsigned __int16 *)((char *)&word_41E8B6 + v4) > 0u )
        {
          v8 = 0;
          v9 = 0;
          do
          {
            WriteProcessMemory(
              ProcessInformation.hProcess,
              &v11[*(_DWORD *)((char *)&unk_41E9A8 + dword_41E8EC + v8 + 12)],
              &dword_41E8B0[*(_DWORD *)((char *)&unk_41E9A8 + dword_41E8EC + v8 + 20)],
              *(_DWORD *)((char *)&unk_41E9A8 + dword_41E8EC + v8 + 16),
              0);
            v8 += 40;
            ++v9;
          }
          while ( v9 < *(unsigned __int16 *)((char *)&word_41E8B6 + v4) );
          v7 = v10;
        }
        WriteProcessMemory(ProcessInformation.hProcess, (LPVOID)(v7->Ebx + 8), (char *)&dword_41E8E4 + v4, 4u, 0);
        v7->Eax = (DWORD)&v11[*(int *)((char *)&dword_41E8D8 + v4)];
        SetThreadContext(ProcessInformation.hThread, v7);
        ResumeThread(ProcessInformation.hThread);
        result = (DWORD)ProcessInformation.hThread;
      }
    }
  }
  return result;
}
```

This is a classic implementation of the technique called [RunPE](https://www.adlice.com/runpe-hide-code-behind-legit-process/).

The binary will create a new process with the same content using *CreateProcess* API with the flag *CREATE_SUSPENDED*, then it will remove everything inside it and replace it with it's own code.

In the challenge binary, a simple xor is used to hide the real program.

It's not hard to unpack such malware, we can simply run the decryption code and
dump it, or we can put a break point on the newest process and dump the binary
using [x64dbg](https://x64dbg.com/) Scylla plugin.

#### First technique, dump the decrypted code

in our case, the malware is using simple xor technique to derypt his payload:

```c
do
    dword_41E8B0[v3++] ^= 0xFEu;
  while ( v3 < 96768 );
  v4 = dword_41E8EC;
```

Putting a breakpoint after the *while* condition will be enough to dump the
decrypted code at address *0x41E8B0*.

When the malware is using obfuscation and is trying to hide the final payload,
it's better to break on *ZwWriteVirtualMemory* or *WriteProcessMemory*:

Here is the calling method:

```
BOOL WINAPI WriteProcessMemory(
  _In_  HANDLE  hProcess,
  _In_  LPVOID  lpBaseAddress,
  _In_  LPCVOID lpBuffer,
  _In_  SIZE_T  nSize,
  _Out_ SIZE_T  *lpNumberOfBytesWritten
);
```

The *lpBuffer* will contains the new binary.

#### More funny method, Break on SetThreadContext

Another method is to break on the API *SetThreadContext* which is responsible
to setup the new context for the created thread. At the end of the code we see
this snippet:

```c
v7->Eax = (DWORD)&v11[*(int *)((char *)&dword_41E8D8 + v4)];
SetThreadContext(ProcessInformation.hThread, v7);
```

Here, v7 is a structure of type [CONTEXT](https://www.nirsoft.net/kernel_struct/vista/CONTEXT.html).
This structure is undocumented by microsoft and it contains all the context for
the newer thread. The *ULONG Eip* is the new entrypoint in the newer process.

Putting a breakpoint on it and resuming the first binary should break on the
entrypoint of the new process.

From here, just dump the binary using `Scylla`.

x64dbg snippet:

```
01091256 | 89 87 B0 00 00 00        | mov dword ptr ds:[edi+B0],eax           | [edi+B0]:EntryPoint
0109125C | FF B5 AC FB FF FF        | push dword ptr ss:[ebp-454]             |
01091262 | FF 15 24 70 0A 01        | call dword ptr ds:[<&SetThreadContext>] |
```
Here eax contains the entrypoint: 0x004012B8

Attaching the debugger to the second process spawned and settings a break point
on this address should break when resuming:

<img src="/resources/2017/ynotctf/blackbox/x64dbg.png">

BAMM, now using *Scylla* to dump: 

<img src="/resources/2017/ynotctf/blackbox/scylla.png">


Reversing the dumped [binary](/resources/2017/ynotctf/blackbox/blackbox_dump.exe), showed another simple xor operation:

```c
signed int __cdecl sub_401032(int a1, _DWORD *a2)
{
  signed int result; // eax
  int v3; // ecx

  result = 1;
  if ( a1 == 1 )
  {
    v3 = 0;
    while ( ((unsigned __int8)byte_416494[v3] ^ *(_BYTE *)(*a2 + v3)) == byte_4164AC[v3] )
    {
      if ( ++v3 >= 21 )
      {
        sub_401006("Congratz!");
        goto LABEL_7;
      }
    }
    sub_401006("Bad password!");
LABEL_7:
    result = 0;
  }
  return result;
}
```
Using ida pro *Export Data* and a little [python script](/resources/2017/ynotctf/blackbox/solve.py) showed us the flag: **YNOT17{RUN_P3_1S_FUN}** 

```python
from itertools import izip

a = "732298B81C9D7F70E9BE3F307EA220BEE093BB1C7A"
b = "2A6CD7EC2DAA0422BCF060604DFD11EDBFD5EE5207"

flag = ''.join(chr(ord(c)^ord(k)) for c,k in izip(a.decode("hex"), b.decode("hex")))

print flag
```

I would like to thanks YNOTCTF Organizer st4ck for his Windows task, there is
not so much in CTF these days.

Challenges resources are available in the [resources
folder](https://github.com/duksctf/duksctf.github.io/tree/master/resources/2017/ynotctf/blackbox)

