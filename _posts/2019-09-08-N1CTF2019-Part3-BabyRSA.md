---
layout: post
title: "N1CTF 2019 - Part3-BabyRSA"
mathjax: true

date: 2019-09-08

---

*RSA encrypted flag but each flag bit is encrypted at a time with random padding. The padding is a square thus using computing the Jacobi symbol for each bit encryption reveals the flag.*

<!--more-->

### Description

The plaintext space in TokyoWesterns CTF real-baby-rsa challenge is too small, so I decide to add some random padding to the plaintext to prevent bruteforce attack. Hope this padding can prevent the hackers. XD

attachment：https://share.weiyun.com/5DMLSFC password：hujqnt

or

https://drive.google.com/file/d/1FNPT90x-rGhUwAKR5b18jnwMvHG91vgW/view?usp=sharing


### Details

Points:     227

Category:   Crypto

### Solution

We were given a [script](/resources/2019/n1ctf/part3-babyrsa/BabyRSA.zip) which was used to encrypt the flag and the encrypted flag file. Each flag bit is padded with a random number and then encrypted. At a first view the challenge does not seem solvable since the function which return the least significant bit of the RSA plaintext is a hard-core predicate *i.e* it is a function as hard as preforming the full decryption without the private key. But looking at how the padding is computed :

```python
padding = random.randint(0, 2**1000) ** 2
message = padding << 1 + m % 2
```

We noticed that the padding is a square and is is shifted by two (or multiply by two) before be added to the plaintext bit. Thus if a the plaintext bit is 0 the corresponding ciphertext will be:

$$ c = (2 {P}^2) ^ e = 2^e ({P}^e)^2$$

with $P$ the random number from the padding. If the plaintext bit is 1 we have the corresponding ciphertext is

$$ c = (2 {P}^2 + 1) ^ e $$

We can divide by $2^e$ each ciphertexts and test with the [Jacobi symbol](https://en.wikipedia.org/wiki/Jacobi_symbol) if the number is a square modulo $N$ or not. The Jacobi symbol $\left(\frac{a}{p}\right)$ for a prime number $p$ is defined to be 1 if $a$ is a square and -1 if not. For our case $\left(\frac{a}{N}\right) = \left(\frac{a}{p}\right) \left(\frac{a}{q}\right)$. Thus if $\left(\frac{c}{N}\right) = -1$ we know that the plaintext bit was 1. Thus we can write a script to reveal the plaintext:

```python
#!/usr/bin/env python3

# Then x2 ≡ a (mod n) is solvable if and only if:
# The Legendre symbol ( a p ) = 1  ({\tfrac {a}{p}})=1} ({\tfrac {a}{p}} =1 } for all odd prime divisors p of n.
import gmpy2

N = 23981306327188221819291352455300124608114670714977979223022816906368788909398653961976023086718129607035805397846230124785550919468973090809881210560931396002918119995710297723411794214888622784232065592366390586879306041418300835178522354945438521139847806375923379136235993890801176301812907708937658277646761892297209069757559519399120988948212988924583632878840216559421398253025960456164998680766732013248599742397199862820924441357624187811402515396393385081892966284318521068948266144251848088067639941653475035145362236917008153460707675427945577597137822575880268720238301307972813226576071488632898694390629
e = 0x10001
invert2 = pow(gmpy2.invert(2,N),e,N)

with open('flag.enc', 'r') as f:
    l = f.read().split("\n")

byte = ""
flag = ""
for c in l:
    if len(c) > 2:
        c = int(c[2:-1], 16)
        if gmpy2.jacobi(c * invert2, N) == -1:
            byte = "1" + byte
        else:
            byte = "0" + byte
        
        if len(byte) == 8:
            flag = chr(int(byte, 2)) + flag
            byte = ""

flag = chr(int(byte, 2)) + flag
print(flag)
```

It outputs the flag:

```bash
N1CTF{You_can_leak_the_jacobi_symbol_from_RSA}
```

