---
layout: post
title: "PlaidCTF 2020 - Reee"
mathjax: true

date: 2020-04-19
---

*Execute an unscrambling function to get the compare algorithm. Then figure out what the algorithm does to recover the flag.*

<!--more-->

### Description

Reversing (150 pts)
#### Story

*Tired from all of the craziness in the Inner Sanctum, you decide to venture out to the beach to relax. You doze off in the sand only to be awoken by the loud “reee” of an osprey. A shell falls out of its talons and lands right where your head was a moment ago. No rest for the weary, huh? It looks a little funny, so you pick it up and realize that it’s backwards. I guess you’ll have to reverse it.
Problem Details*

[Download](/resources/2020/plaidctf/reee/reee-969a38276c46a65001faa2eaf75bf6ab3c444096b9d34094fd0e500badfaa73d.tar.gz)

Hint: Flag format

The flag format is pctf{$FLAG}. This constraint should resolve any ambiguities in solutions.

### Details

Points:      150

Category:    reverse

### Solution

The file is a standard x86-64 binary:
```bash
$ file reee
reee: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 2.6.32, BuildID[sha1]=3ccec76609cd013bea7ee34dffc8441bfa1d7181, stripped
```

And it's waiting an argument:
```bash
$ ./reee hello
Wrong!
```

I opened it in radare2:

<img src="/resources/2020/plaidctf/reee/r2main.png" width="800">

I remarked that the argument is passed to the **fcn.004006e5** function and if the result is 0 then the string *"Correct!"* is printed. But this function seems scrambled: 

<pre><font color="#C19C00">[0x004006e5]&gt;</font> s fcn.004006e5; pd 10
       <font color="#0037DA">╎╎</font>   <font color="#C50F1F">; CALL XREFS from main @ 0x400699, 0x4006a5, 0x4006db</font>
<font color="#3A96DD">┌</font> 60: <font color="#C50F1F">fcn.004006e5</font> (int64_t arg2, uint32_t arg4, int64_t arg_58ae7f6ah);
<font color="#3A96DD">│</font> bp: <font color="#C19C00">1</font> (vars 0, args <font color="#C19C00">1</font>)
<font color="#3A96DD">│</font> sp: 0 (vars 0, args 0)
<font color="#3A96DD">│</font> rg: <font color="#C19C00">2</font> (vars 0, args <font color="#C19C00">2</font>)
<font color="#3A96DD">│</font>      <font color="#0037DA">╎╎</font>   <font color="#13A10E">0x004006e5</font>      <font color="#CCCCCC">f9</font>             <font color="#CCCCCC">stc</font>
<font color="#3A96DD">│</font>      <font color="#0037DA">╎╎</font>   <font color="#13A10E">0x004006e6</font>      <font color="#CCCCCC">93</font>             <font color="#CCCCCC">xchg</font><font color="#3A96DD"> eax</font>,<font color="#3A96DD"> ebx</font>
<font color="#3A96DD">│</font>     <font color="#3A96DD">┌───&lt;</font> <font color="#13A10E">0x004006e7</font>      <font color="#C19C00">752d</font>           <font color="#13A10E">jne 0x400716</font>
<font color="#3A96DD">│</font>     <font color="#3A96DD">│</font><font color="#0037DA">╎╎</font>   <font color="#13A10E">0x004006e9</font>      <font color="#CCCCCC">dbc6</font>           <font color="#CCCCCC">fcmovnb</font><font color="#3A96DD"> st</font>(<font color="#3A96DD">0</font>),<font color="#3A96DD"> st</font>(<font color="#C19C00">6</font>)
<font color="#3A96DD">│</font>     <font color="#3A96DD">│</font><font color="#0037DA">╎╎</font>   <font color="#13A10E">0x004006eb</font>      <font color="#CCCCCC">ab</font>             <font color="#B4009E"><b>stosd dword</b></font><font color="#3A96DD"><b> </b></font>[<font color="#3A96DD">rdi</font>],<font color="#3A96DD"> eax</font>
<font color="#3A96DD">│</font>     <font color="#3A96DD">│</font><font color="#0037DA">╎└─&lt;</font> <font color="#13A10E">0x004006ec</font>      <font color="#CCCCCC">e0a2</font>           <font color="#13A10E">loopne</font><font color="#3A96DD"> </font><font color="#C19C00">0x400690</font>
<font color="#3A96DD">│</font>     <font color="#3A96DD">│</font><font color="#0037DA">╎</font>    <font color="#13A10E">0x004006ee</font>      <font color="#C19C00">3b49</font><font color="#CCCCCC">9d</font>         <font color="#3A96DD">cmp ecx</font>,<font color="#3A96DD"> dword </font>[<font color="#3A96DD">rcx </font>-<font color="#3A96DD"> </font><font color="#C19C00">0x63</font>] <font color="#0037DA">; arg4</font>
<font color="#3A96DD">│</font>     <font color="#3A96DD">│</font><font color="#0037DA">╎</font>    <font color="#13A10E">0x004006f1</font>      <font color="#CCCCCC">8c</font><font color="#C19C00">5c</font><font color="#CCCCCC">86dd</font>       <font color="#CCCCCC">mov word </font>[<font color="#3A96DD">rsi </font>+<font color="#3A96DD"> rax</font>*<font color="#3A96DD">4 </font>-<font color="#3A96DD"> </font><font color="#C19C00">0x23</font>],<font color="#3A96DD"> ds</font> <font color="#0037DA">; arg2</font>
      <font color="#3A96DD">│</font><font color="#0037DA">╎</font>    <font color="#13A10E">0x004006f5</font>      <font color="#CCCCCC">0e</font>             <font color="#E74856"><b>invalid</b></font>
      <font color="#3A96DD">│</font><font color="#0037DA">└──&lt;</font> <font color="#13A10E">0x004006f6</font>      <font color="#C19C00">73</font><font color="#CCCCCC">cd</font>           <font color="#13A10E">jae 0x4006c5</font><font color="#C50F1F">                ; main+0x77</font>
</pre>

In fact if we break just before the function call we have the function unscrambled. I just checked that the scrambling was the same for different input arguments:

<pre><font color="#C19C00">[0x004006d4]&gt;</font> ood hello; dcu 0x4006d4
child received signal 9
Stepping failed!
Process with PID 10921 started...
= attach 10921 10921
File dbg:////reee  hello reopened in read-write mode
Continue until 0x004006d4 using 1 bpsize
<font color="#C19C00">[0x7fde560fcfe6]&gt;</font> s fcn.004006e5; pd 10
            <font color="#C50F1F">; CALL XREFS from main @ 0x400699, 0x4006a5, 0x4006db</font>
<font color="#3A96DD">┌</font> 60: <font color="#C50F1F">fcn.004006e5</font> (int64_t arg2, uint32_t arg4, int64_t arg_58ae7f6ah);
<font color="#3A96DD">│</font> bp: <font color="#C19C00">1</font> (vars 0, args <font color="#C19C00">1</font>)
<font color="#3A96DD">│</font> sp: 0 (vars 0, args 0)
<font color="#3A96DD">│</font> rg: <font color="#C19C00">2</font> (vars 0, args <font color="#C19C00">2</font>)
<font color="#3A96DD">│</font>           <font color="#13A10E">0x004006e5</font>      <font color="#C19C00">55</font>             <font color="#881798">push</font><font color="#3A96DD"> rbp</font>
<font color="#3A96DD">│</font>           <font color="#13A10E">0x004006e6</font>      <font color="#C19C00">48</font><font color="#CCCCCC">8bec</font>         <font color="#CCCCCC">mov</font><font color="#3A96DD"> rbp</font>,<font color="#3A96DD"> rsp</font>
<font color="#3A96DD">│</font>           <font color="#13A10E">0x004006e9</font>      <font color="#CCCCCC">e814</font><font color="#13A10E">000000</font>     <font color="#16C60C"><b>call 0x400702</b></font>
<font color="#3A96DD">│</font>           <font color="#13A10E">0x004006ee</font>      <font color="#CCCCCC">8ac8</font>           <font color="#CCCCCC">mov</font><font color="#3A96DD"> cl</font>,<font color="#3A96DD"> al</font>                  <font color="#0037DA">; arg4</font>
<font color="#3A96DD">│</font>           <font color="#13A10E">0x004006f0</font>      <font color="#CCCCCC">b8</font><font color="#C19C00">32</font><font color="#CCCCCC">e4</font><font color="#C19C00">5f</font><font color="#CCCCCC">ae</font>     <font color="#CCCCCC">mov</font><font color="#3A96DD"> eax</font>,<font color="#3A96DD"> </font><font color="#C19C00">0xae5fe432</font>
            <font color="#13A10E">0x004006f5</font>      <font color="#CCCCCC">05ce1ba0</font><font color="#C19C00">51</font>     <font color="#C19C00">add</font><font color="#3A96DD"> eax</font>,<font color="#3A96DD"> </font><font color="#C19C00">0x51a01bce</font>
            <font color="#13A10E">0x004006fa</font>      <font color="#C50F1F">ff</font><font color="#CCCCCC">c0</font>           <font color="#C19C00">inc</font><font color="#3A96DD"> eax</font>
        <font color="#3A96DD">┌─&lt;</font> <font color="#13A10E">0x004006fc</font>      <font color="#C19C00">73</font><font color="#CCCCCC">08</font>           <font color="#13A10E">jae 0x400706</font>
        <font color="#3A96DD">│</font>   <font color="#13A10E">0x004006fe</font>      <font color="#CCCCCC">8ac1</font>           <font color="#CCCCCC">mov</font><font color="#3A96DD"> al</font>,<font color="#3A96DD"> cl</font>
        <font color="#3A96DD">│</font>   <font color="#13A10E">0x00400700</font>      <font color="#CCCCCC">c9</font>             <font color="#B4009E"><b>leave</b></font></pre>

Then we can decompile the function:

<pre><font color="#C19C00">[0x00400702]&gt;</font> pdg
<font color="#0037DA">bool</font> <font color="#C50F1F">fcn.00400702</font>(<font color="#B4009E"><b>void</b></font>)
{
    <font color="#0037DA">char</font> cVar1;
    <font color="#0037DA">char</font> *in_RAX;
    <font color="#0037DA">int32_t</font> iVar2;
    <font color="#0037DA">int64_t</font> iVar3;
    <font color="#0037DA">char</font> *pcVar4;
    <font color="#0037DA">uint8_t</font> uVar5;
    <font color="#0037DA">int32_t</font> iVar6;
    <font color="#0037DA">int32_t</font> iVar7;
    <font color="#0037DA">bool</font> bVar8;
    
    iVar3 = <font color="#C19C00">-1</font>;
    pcVar4 = in_RAX;
    <font color="#B4009E"><b>do</b></font> {
        <font color="#B4009E"><b>if</b></font> (iVar3 == <font color="#C19C00">0</font>) <font color="#B4009E"><b>break</b></font>;
        iVar3 = iVar3 + <font color="#C19C00">-1</font>;
        cVar1 = *pcVar4;
        pcVar4 = pcVar4 + <font color="#C19C00">1</font>;
    } <font color="#B4009E"><b>while</b></font> (cVar1 != <font color="#C19C00">&apos;\0&apos;</font>);
    iVar2 = ~(<font color="#0037DA">uint32_t</font>)iVar3 - <font color="#C19C00">1</font>;
    uVar5 = <font color="#C19C00">0x50</font>;
    iVar6 = <font color="#C19C00">0</font>;
    <font color="#B4009E"><b>while</b></font> (iVar6 &lt; <font color="#C19C00">0x539</font>) {
        iVar7 = <font color="#C19C00">0</font>;
        <font color="#B4009E"><b>while</b></font> (iVar7 &lt; iVar2) {
            in_RAX[iVar7] = in_RAX[iVar7] ^ uVar5;
            uVar5 = uVar5 ^ in_RAX[iVar7];
            iVar7 = iVar7 + <font color="#C19C00">1</font>;
        }
        iVar6 = iVar6 + <font color="#C19C00">1</font>;
    }
    bVar8 = <font color="#C19C00">true</font>;
    iVar6 = <font color="#C19C00">0</font>;
    <font color="#B4009E"><b>while</b></font> (iVar6 &lt; iVar2) {
        <font color="#B4009E"><b>if</b></font> (bVar8 == <font color="#C19C00">false</font>) {
            bVar8 = <font color="#C19C00">false</font>;
        } <font color="#B4009E"><b>else</b></font> {
            bVar8 = in_RAX[iVar6] == *(<font color="#0037DA">char</font> *)((<font color="#0037DA">int64_t</font>)iVar6 + <font color="#C19C00">0x4008eb</font>);
        }
        iVar6 = iVar6 + <font color="#C19C00">1</font>;
    }
    <font color="#B4009E"><b>return</b></font> bVar8;
}
</pre>

So the first byte of the flag is XORed with 0x50 the second byte is XORed with the first byte of the flag and so on 1337 times. The result is compared with the data stored at **0x4008eb**. If they match it prints **"Correct"**. Since the 34th byte is 0 I guessed the flag length was 33. So we can starts from the results:

<pre><font color="#C19C00">[0x00400702]&gt;</font> pxj 34@0x4008eb
[72,95,54,53,53,37,20,44,29,1,3,45,12,111,53,97,126,52,10,68,36,44,74,70,25,89,91,14,120,116,41,19,44,0]</pre>

And come back to the beginning, *i.e.* until the value to XORed equals 0x50. Since we do not know the last byte value XORed we have to bruteforce it. It gives in Python:

```python
data = [72,95,54,53,53,37,20,44,29,1,3,45,12,111,53,97,126,52,10,68,36,44,74,70,25,89,91,14,120,116,41,19,44]
length = len(data)-1

for k in range(0,256):
	mask = k
	flag = bytearray(data)
	for i in range(0,1337):
		for j in range(length,-1,-1):
			mask = flag[j] ^ mask
			flag[j] = flag[j] ^ mask
	if mask == 0x50:
		print(flag[:length+1])
```

And I got the flag:
```
bytearray(b'pctf{ok_nothing_too_fancy_there!}')
```
<center>
<img src="/resources/2020/plaidctf/reee/z3.png" width="300">