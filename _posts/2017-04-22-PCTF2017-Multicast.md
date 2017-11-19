---
layout: post
title: "PlaidCTF 2017 - Multicast"
mathjax: true

date: 2017-04-22
---

*The same flag is encrypted 5 times with RSA small public exponent and linear padding. The generalization of Håstad's broadcast attack and the Coppersmith method allow to recover the flag.*

<!--more-->

### Description
Many [messages](/resources/2017/plaidctf/multicast/multicast_684d222a7554c098301c2d8a608c85dd.tar.gz) intercepted.

Break them.

### Details

Points:      175

Category:    Crypto

Validations: 74

### Solution

Two files were given, one with 20 large integers and one Sage script. The script file consists in encrypting the same flag 5 times with RSA and public exponent $$e = 5$$. Hopefully the padding values $$a_i$$ and $$b_i$$ are also given in the file as well as the modulus $$n_i$$ and the ciphertexts $$c_i$$. We noticed that the generalization of the Håstad's broadcast [attack](https://en.wikipedia.org/wiki/Coppersmith%27s_attack#H.C3.A5stad.27s_broadcast_attack) allows us to solve this challenge. With these values we can create the polynomials $$h_i(x) = (a_i x + b_i)^5 -c_i$$. Then we make each $$h_i$$ monic by dividing them with the coeficient of degree 5. We used the Chinise remainder theorem to find the values $$T_i$$ such that $$T_i = 1 \mod n_i$$ and $$T_i = 0\mod n_j$$ for $$i \neq j$$. With those value we could built the combined polynomial:

$$h(x) = \sum T_i h_i(x) \mod n_1 \cdot n_2 \cdot n_3 \cdot n_4 \cdot n_5$$

Now we have to solve the equation $$h(x) = 0$$ and a solution will be the flag. We used the Coppersmith method to solve the equation and the sage [script](https://github.com/mimoo/RSA-and-LLL-attacks/blob/master/coppersmith.sage) given by David Wong. The complete Sage script to recover the flag that was:

```python
from binascii import unhexlify

f = open("data.txt", "r")

a = []
b = []
c = []
n = []

for i in range(5):
    a.append(int(f.readline().strip()))
    b.append(int(f.readline().strip()))
    c.append(int(f.readline().strip()))
    n.append(int(f.readline().strip()))
    
f.close()

r = [PolynomialRing(Integers(n[i]),'x') for i in range(5)]
h = [r[i]([b[i], a[i]]) **5 - c[i] for i in range(5)]

# Make h monic:
for i in range(5):
    h[i] = Integer(list(h[i])[5]).inverse_mod(n[i]) * h[i]

t = []
t.append(crt([1, 0, 0, 0, 0], n))
t.append(crt([0, 1, 0, 0, 0], n))
t.append(crt([0, 0, 1, 0, 0], n))
t.append(crt([0, 0, 0, 1, 0], n))
t.append(crt([0, 0, 0, 0, 1], n))

N = n[0]*n[1]*n[2]*n[3]*n[4]

R = PolynomialRing(Integers(N),'X')

H = sum([t[i]*R(list(h[i])) for i in range(5)])

dd = 5
beta = 1                                # b = N
epsilon = beta / 7                      # <= beta / 7
mm = ceil(beta**2 / (dd * epsilon))     # optimized value
tt = floor(dd * mm * ((1/beta) - 1))    # optimized value
XX = ceil(N**((beta**2/dd) - epsilon))  # optimized v

load("coppersmith.sage")
solution = coppersmith_howgrave_univariate(H, N, beta, mm, tt, XX)
print(unhexlify("{:x}".format(solution[0])))
```

Which reveals the flag:

```bash
potential roots: [(48256277589562736290346738984160936248669152041168006480231762961805279486041361025591223549819869423406508417405, 1)]
PCTF{L1ne4r_P4dd1ng_w0nt_s4ve_Y0u_fr0m_H4s7ad!}
```
