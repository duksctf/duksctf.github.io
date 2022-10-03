---
layout: post
title: "SEKAI 2022 - Symbolic Needs 2"
mathjax: true

date: 2022-10-01
---

*Cryptocurrency scammer was caught and laptop confiscated, use strings to recover command used to access his wallet and patch + decompile python pyc file to regenerate bip39 mnemonic and recreate the private key.

<!--more-->

### Description

Recover the private key of the wallet address `0xACa5872e497F0Cc626d1E9bA28bAEC149315266e`. Submit the key wrapped with `SEKAI{}`.

Attachment md5sum: 4be69c88e6f19dd9c9f8e6c52bc93c28

Author: BattleMonger

### Details

Points:      482

Category:    forensic

Validations: 18

### Solution

We receive a memory dump of a linux computer.
Running strings on it leds nothing at the beginning and after some times trying to make work this f****** volatility2 crap under a not anymore supported version of python2 was a nightmware. I gave up on this task and later on a hint was released: **stick to what you used for Part 1, you all are also missing a very basic but extremely useful command.**

OMG we are talking about strings, right ? So let's continue to dig inside. I tried grepping for all crypto keyword without luck, and then I started thinking about base64/base32 keyword as it should be encoded/encrypted somewhere to not show up directly with a grep command.

Running our good old strings | grep command lead to the following artifact:

```bash
-> $ strings dump.mem |grep -i base32
base32
ncat -lvnp 1234 -c 'echo N4GQ2CQAAAAAAEFG5JRPEAIAADRQAAAAAAAAAAAAAAAAAAAAAAAAACIAAAAEAAAAABZ6QAAAABSAAZABNQAFUAD2A5SQA2QBMQBBSAC2AJLQA3QLAEAACAABABSQGZADQMAQCADFASBQAAIALEAGOAC2AVSQMZAEMQCYGAUPBZNAOZIHUAEKCAFABGQQAWQFK4AGIAIEAACABAYDAEAG4CBRABZS65YBAEAACAABABMQAAIAMQDFUCTFBNSQVAYBMQDWIAMFAIMQAWQKMUGGKCVABVSQ4ZIKQMAWICDFBZSQVAYBMQEBMAAYAALQBIIBQMAVUCTHABNA6ZIQMQAGKDTFBKBQCZAIQMBUIAC5CRNBCZIPUAJGKBLFCNSQUZIRMUIWICAXACCQEGIAMQDYGATEAIMAAGIAUEAQCADRLFSQGZAJQMAQCADEAFJQAKIK5EAAAAAAJ3UQCAAAAB5BQVLTMFTWKORAFYXXOYLMNRSXIIDQMFZXG53POJSHUDLCNFYDGOLMNFZXILTUPB2NUALSNQKAAAAAABS6KHWNHGMBH4AWTJ3BE3XKCYFWPVQQSR6WWFSHC2WEUE3P5AP7G46OA3IBWAIA5EBAAAAA5EGAAAAA3ICVO4TPNZTSSFG2ANZXS462ARQXEZ3W3IEHAYLTON3W64TE3ICXA4TJNZ2NUBDFPBUXJWQFO5XXEZDT3ICG64DFN3NACZW2ARZGKYLE3IFHG4DMNF2GY2LOMVZ5UBDDN5SGLWQDMJUW5WQDON2HFWQFPJTGS3DM3IBWYZLO3IEG23TFNVXW42LD3ICXEYLOM5S5UALJ3IDGC4DQMVXGJWQDNFXHJKIAOINQAAAAOINQAAAA7IEHIZLTOQZC44DZ3IEDY3LPMR2WYZJ6AEAAAADTEIAAAAAIAABAEDQBAYAQQAIIAECAGDACBYARZ7YEAMIAGIQBAQBRIARGAEGAE=== | base32 -d > file.pyc'
base32hexmem
base32
```
Running the exact same command lead to the file [file.pyc](/resources/2022/sekai/symbol_needs_2/file.pyc) which is a python `3.10.7` byte-compiled file.
It exist several tool to decompile python bytecode unfortunately all I've tested so far was not able to decompile correctly this file.
The most promising tool I found was [pycdc](https://github.com/zrax/pycdc) from Zrax.
When runinng the tool I got the following output:

```bash
> $ ./pycdc ../../file.pyc 
# Source Generated with Decompyle++
# File: file.pyc (Python 3.10)

Unsupported opcode: WITH_EXCEPT_START
import sys
# WARNING: Decompyle incomplete
```

It seems that the python file contains some new opcode from python 3.10.X and that the tool does not support it, yet.

There is another utility to disassemble the opcode as well which was working correctly but as I was in a hurry I didn't wanted to reverse the opcode by hand.

One idea came in my mind, as I guessed more or less the start of the script, why not just implement the opcode as a "NOOP" in the `pycdc` and see what happend ? We are on CTF, right ?

Here is the small patch I made:

```bash
diff '--color=auto' -r pycdc/ASTree.cpp pycdc_patched/ASTree.cpp
2507a2508,2511
> 	case Pyc::RERAISE_A:
> 	   break;
> 	case Pyc::WITH_EXCEPT_START:
> 	   break;
```
Annnd yes, it worked:

```python
-> $ ./pycdc ../file.pyc 
# Source Generated with Decompyle++
# File: file.pyc (Python 3.10)

import sys

try:
    password = sys.argv[1]
finally:
    pass
print('Usage: ./wallet password')
exit()
words = []
with open('bip39list.txt', 'r') as f:
    words = f.read().splitlines()
    None(None, None, None)
if not None:
    pass

code = 0x26F4036773F33FD1BC4E55616472CD7F65086B670B2DD5B84BB4D16F02730E734F72E500L
code = bin(code)[2:]
code = str(code.zfill(len(code) + (12 - len(code) % 12)))
mnemonic = []
for i in range(0, len(code), 12):
    mnemonic.append(words[int(code[i:i + 12], 2) - 1])
print('Wrong')
```
So the script read a file called [bip39list.txt](/resources/2022/sekai/symbol_needs_2/bip39list.txt) which is in fact a list of known words used to generate randomly a seed for creating public/private key for cryptocurrency wallet.

Then it used a variable called `code` as a bitstream to define which words is in the mnemonic passphrase.
Running this code lead to:

```python
['evidence', 'leopard', 'solution', 'layer', 'legend', 'danger', 'orient', 'project', 'silver', 'flower', 'wrong', 'path', 'stove', 'throw', 'fortune', 'report', 'nuclear', 'old', 'target', 'exact', 'broom', 'hawk', 'toss', 'paper']
```
 
The address of the wallet come from ethereum blockchain. It is easily verifiable using the website [blockchain explorer](https://www.blockchain.com/explorer).
To recover the private key, we used the [Mnemonic Code Converter](https://iancoleman.io/bip39/) from Ian Coleman.
The private key can be found on the derived address section and is: `0x81c458e9fae445de18385a3379513acc8e191e4c2667c85aa0a52a32ec4e6d55`.

The flag is: **SEKAI{0x81c458e9fae445de18385a3379513acc8e191e4c2667c85aa0a52a32ec4e6d55}**

Challenges resources are available in the [resources folder](https://github.com/duksctf/duksctf.github.io/tree/master/resources/2022/sekai/symbolic_needs_2)
