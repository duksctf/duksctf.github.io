---
layout: post
title: "SEKAI 2022 - Symbolic Needs 1"
mathjax: true

date: 2022-10-01
---

*Cryptocurrency scammer was caught and laptop confiscated, build volatility 3 linux profile and find the bash command using linux.bash.Bash.*

<!--more-->

### Description

We recently got hold of a cryptocurrency scammer and confiscated his laptop.

Analyze the memdump. Submit the string you find wrapped with SEKAI{}.

Attachment md5sum: 4be69c88e6f19dd9c9f8e6c52bc93c28

Author: BattleMonger

### Details

Points:      467

Category:    forensic

Validations: 24

First Blood: Yes

### Solution

We receive a memory dump of a linux computer.
The go to tool to analyze such file is [volatility3](https://github.com/volatilityfoundation/volatility3/) as we at duks love to play with latest tool, we decided to give it a shot and not use the oldest python2 only, volatility2.
Inside the documentation of [volatility3](https://volatility3.readthedocs.io/en/latest/symbol-tables.html) we can understand how to create a new symbol table file for the kernel we have.
First we have to find which kernel/linux version it is. We can use the `banners.Banner` plugins for that:

```bash
-> $ vol -s . -f dump.mem banners.Banners
Volatility 3 Framework 2.0.1
Progress:  100.00		PDB scanning finished                  
Offset	Banner

0x42400200	Linux version 5.15.0-43-generic (buildd@lcy02-amd64-076) (gcc (Ubuntu 11.2.0-19ubuntu1) 11.2.0, GNU ld (GNU Binutils for Ubuntu) 2.38) #46-Ubuntu SMP Tue Jul 12 10:30:17 UTC 2022 (Ubuntu 5.15.0-43.46-generic 5.15.39)
0x437c3718	Linux version 5.15.0-43-generic (buildd@lcy02-amd64-076) (gcc (Ubuntu 11.2.0-19ubuntu1) 11.2.0, GNU ld (GNU Binutils for Ubuntu) 2.38) #46-Ubuntu SMP Tue Jul 12 10:30:17 UTC 2022 (Ubuntu 5.15.0-43.46-generic 5.15.39)9)
```
so we are digging with a kernel `5.15.0-43-generic` from Ubuntu. we discovered that the exact linux version is `Ubuntu 22.04 LTS` using `strings`.

After some research, we found a blog post explaining in detail how to create a [new profile](https://beguier.eu/nicolas/articles/security-tips-3-volatility-linux-profiles.html).

We found on the ubuntu repository the good version of the kernel, we used `docker` to generate a new ubuntu image and install the specified kernel with the debugging symbol and run the `dwarf2json` tool on it.
Using our newly created [symbol table](/resources/2022/sekai/symbolic_needs_1/linux-image-5.15.0-43-generic-amd64.json)

Using this newly created symbol table, we use the `linux.bash.Bash` plugins to see what was doing the scammer when the forensic image has been taken:

```bash
> $ volatility3/vol.py -s symbols/ -f dump.mem linux.bash.Bash
Volatility 3 Framework 2.4.0
Progress:  100.00		Stacking attempts finished                 
PID	Process	CommandTime	Command

1863	bash	2022-08-29 13:45:56.000000 	72.48.117.53.84.48.110.95.119.51.95.52.114.51.95.49.110.33.33.33
```
Ok a weird looking bash command or bash artifact is shown. As we are in CTF let's try just a bunch of python code to decode this weird looking number, right ?

```python
a = "72.48.117.53.84.48.110.95.119.51.95.52.114.51.95.49.110.33.33.33"
flag = ""
for i in a.split("."):
    flag += chr(int(i))
print(flag)
```
And we get our flag: **SEKAI{H0u5T0n_w3_4r3_1n!!!}**

Challenges resources are available in the [resources folder](https://github.com/duksctf/duksctf.github.io/tree/master/resources/2022/sekai/symbolic_needs_1)

