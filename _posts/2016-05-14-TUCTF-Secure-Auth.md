---
layout: post
title: "TU CTF 2016 - Secure Auth"
date: 2016-05-14
---

*To authenticate on a server we had to provide a message signed with a RSA private key. Hopefully the server allows us to sign any message execpt the one requested with the same key.*

<!--more-->


### Description

*We have set up this fancy automatic signing server!*

*We also uses RSA authentication, so it’s super secure!*

*nc 104.196.116.248 54321*

### Details

Points:      150

Category:    crypto

Validations: ??

### Solution

When we connected to the server, it allow us to sign any message. To check which kind of encryption is is we sent $$1$$ and the answer was $$1$$. We could deduce that plain RSA without padding was used *i.e*: $$c = m^d \mod n$$.
```

However, here $$n$$ is unknown. We can make a guess that $$e=65535$$ and since $$(m^d)^e = m \mod n$$ we can recover $$n$$. We just send $$p_1 = 2$$ and $$p_2 = 3$$ to the server and we got their signed version. Then $$n = \gcd\left((2^d)^e-2, (3^d)^e)-3\right)$$. We use python to compute $$n$$:

``` python
import gmpy2

p1 = 2
c1 = ...
p2 = 3
c2 = ...
n = gmpy2.gcd(c1**e -p1, c2**e-p2)
n
```

After a few minutes of computation we got:
``` python
n = ...
```

the message to sign was m="". The idea to bypass the server is to sign $$m\cdot 2$$ which is different than $$m$$ and the inverse of $$2$$ modulo $$n$$ and finally the correct signature is $$m\cdot 2 \cdot 2^{-1} \mod n$$.
