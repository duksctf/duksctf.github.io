---
layout: post
title: "PlaidCTF 2019 - R u SAd?"
mathjax: true

date: 2019-04-13

---

*RSA encrypted flag and prime inveses are given*

<!--more-->

### Description

Tears dripped from my face as I stood over the bathroom sink. Exposed again! The tears melted into thoughts, and an idea formed in my head. [This](/resources/2019/plaidctf/rusad/rusad.zip) will surely keep my secrets safe, once and for all. I crept back to my computer and began to type.

### Details

Points:     150

Category:   Crypto

### Solution

Opening the archive gave us the a 512-bytes encrypted flag, what seems to be a public key and a script for encryption and decryption. Inspecting the script showed us that the public key is a Python oblect serialize with pickle. We inspected the key object:


```python
from rusad import *
f = open("key.sad.pub", "rb")
key = pickle.load(f) 
f.close()
dir(key)

[...]
'bits',
 'iPmQ',
 'iQmP',
 'ispriv',
 'ispub',
 'priv',
 'pub']

```

We noticed that the key is a RSA public key with 4096 bits and the value **iPmQ** and **iQmP** seems interesting. Looking at the script we noticed that these values are :
$$ \mathbf{iPmQ} = p^{-1} \mod q $$ and $$ \mathbf{iQmP} = q^{-1} \mod p $$ which are used during Chinese remainder theorem computation and not properly removed.

From the Bézout's identity we have:

$$ \mathbf{iPmQ} \cdot p - \mathbf{iQmP} \cdot q = 1 $$

$$\Rightarrow\quad \mathbf{iPmQ} \cdot N - \mathbf{iQmP} \cdot q^2 - q = 0 $$

Since both **iPmQ** and **iQmP** are positive we must have one of them with the negative sign in the Bézout's identity and since the value **iQmP** is reduced modulo $$p$$ we have to replace the equation with.:

$$\mathbf{iPmQ} \cdot N + \mathbf{iQmP} \cdot q^2 - (N+1)q = 0 $$

Then we solved the equation for q in Sage:



```python
sage: P.<x> = PolynomialRing(IntegerRing(), implementation='NTL')
sage: poly = ipmq * N + iqmp * x^2 - (N+1) * x
sage: poly.roots()
[(25004672227855409995386175663336188685177638541286666056441830847618100808198668167307814236224429885295241140194633625051478252429462828073782848889819460674774292004752724556602147320684206242726073358822655212944688523823150236245522627662371134165404316388528738697090763677910441487876514668914442018764569771021916503649822836288868439220382922721194436569302106969570041514638164319835688101248578648742016186666021527781591528560611986692317045407081396778512783312692838307769559661780971287324753785154074832628454871505400166651610503632212720604214996108967812794633118832616768643612648168060802523582631,
  1)]
```

And we have the value for $$q$$. Then retriving the flag is easy:

```python
from rusad import *
q = 25004672227855409995386175663336188685177638541286666056441830847618100808198668167307814236224429885295241140194633625051478252429462828073782848889819460674774292004752724556602147320684206242726073358822655212944688523823150236245522627662371134165404316388528738697090763677910441487876514668914442018764569771021916503649822836288868439220382922721194436569302106969570041514638164319835688101248578648742016186666021527781591528560611986692317045407081396778512783312692838307769559661780971287324753785154074832628454871505400166651610503632212720604214996108967812794633118832616768643612648168060802523582631
p = key.N // q
d, _, g = egcd(key.E, (p-1) * (q-1))

f = open("flag.enc", "rb")
data = f.read() 
f.close()

data_num = bytes2num(data)
m = pow(data_num,d,key.N)

print(unpad(num2bytes(m,512))) 

b'PCTF{Rub_your_hands_palm_to_palm_vigorously_for_at_least_20_seconds_to_remove_any_private_information}\n
```
