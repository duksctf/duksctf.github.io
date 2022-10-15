---
layout: post
title: "ASIS 2022 - Mariana"
mathjax: true

date: 2022-10-01
---

*Find 40 discrete logarithm fixed points to solve the challenge. The range check allows to solve the equation with the Chinese remainder theorem with a negative value.*

<!--more-->

### Description

[Mariana](/resources/2022/asis/mariana/mariana.py) works in the areas of cryptography and security. But some flaws exists in her work!

`nc 65.21.255.31 32066`

### Details

Points:      107

Category:    Cryptography

Validations: 41

### Solution
The script is asking 40 times for a discrete logarithm fixed point:

$$g^x = x \mod p$$

With $p$ being from 32 to 1280 bit long and $x$ being less than $p$. For the latest steps a solution involving the computation of a discrete logartihm will not be feasible. The title would indicate to look at the work of [Mariana Levin *et. al*](https://math.dartmouth.edu/~carlp/brizolis6.pdf) about discrete logarithm fixed point. However the paper proves that the solution exists but without any construction method. However in the paper there is a note saying: "*Note that if x is not restricted to the interval [1, p − 1] it is easy to find fixed points*. In our challenge, $x$ is limited to $p-1$ but in the code there is not limit to have a negative value.

The idea is the following, we are looking for a value of $x$ such that:

$$x \equiv 1 \mod p-1$$

$$x \equiv g \mod p$$

If so, we have the correct relation: $g^x = x \mod p$ and we must have $x < p$. The chinese remainder theorem (CRT) would give us a positive solution for the previous system modulo $p(p-1)$. It would be rejected by the server. But if we substract $p(p-1)$ to the result of the CRT it would give a negative value still correct.

The final script to automatized the 40 answers is the following:

```python
from sage.all import crt

import telnetlib

HOST = "65.21.255.31"

tn = telnetlib.Telnet(HOST, 32066)

# header
rsp = tn.read_until(b"for x.   |")
print(rsp.decode())

rsp = tn.read_until(b"\n")
print(rsp.decode())

while True:
    # p
    rsp = tn.read_until(b"\n")
    print(rsp.decode())
    exec(rsp.decode()[2:])

    # q 
    rsp = tn.read_until(b"\n")
    print(rsp.decode())
    exec(rsp.decode()[2:])

    rsp = tn.read_until(b"\n")
    print(rsp.decode())

    # CRT computation
    c = crt(1, g, p-1 , p) - p*(p-1)
    cmd = c.str().encode() + b"\n"

    tn.write(cmd)
    rsp = tn.read_until(b"\n")
    print(rsp.decode())
```

Which outputs the flag at the end:

```bash
$ solve.py
...
| Send the solution x = 
| Good job, try to solve the next level!
| p = 20060495634641923934290910042037415012965887049052082629378025578414094494317215752767229350560283637103129215245317866638158420602603765621357973975183610617486899951596907899625713829777825949642703336180486781294253558726793130837911364800464374046475660950482374585595881510361204635257734100278453594013796369208483140492740252211847837041081103872047376210156835506562419282005437
| g = 17128259023814750660220796259279795284170791486181711721648128733352156118458053198349603022545160428373749952344831733972901484222895150307930656564833027330762184748955605601775393310165180985683423720111484225049593443086585390492386320039883895157118956582795555111005609439268957878324133121128287666829754348637646678267889542533643145760727682471761594848292230791667831264374169
| Send the solution x = 
| Congratz! the flag is: ASIS{fiX3d_pOIn7s_f0r_d!5Cret3_l0g4riThmS!}
```