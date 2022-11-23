---
layout: post
title: "BlackAlps 22 - Polynomial 1 and 2"
mathjax: true

date: 2022-11-16
---

*Textbook RSA and Rabin except we use irreducible polynomials of prime degrees instead of primes, making factorization possible.*

<!--more-->

## Polynomial 1

### Description

*An engineer just saw in his algebra class the similarities between prime numbers and irreducible polynomials.  He decides to reinvent cryptosystems based on these similarities, starting with the famous RSA cryptosystem.  You are given the encryption script, the public key (e,n) and a ciphertext.* 

### Details

Category:    Crypto

### Solution

We're provided a `.sage` file and some parameters, let's first take a look at that.

```python
F.<x> = PolynomialRing(GF(2))
def keygen():
    d1 = random_prime(3020, lbound=2000)
    d2 = random_prime(3020, lbound= 2000)
    p = F.irreducible_element(d1, "random") #irreducible element in GF(2)[x] of degree d1
    q = F.irreducible_element(d2, "random") #irreducible element in GF(2)[x] of degree d2
    n = p*q
    phi = (2**d1-1)*(2**d2-1)
    e = 65537
    while(gcd(e,phi) != 1):
        e = e+2
    d = inverse_mod(e,phi)
    return (d, e, n)

# Helper functions toBits, bitsToBytes and polyToBits omitted but available in the annex solve.sage

#Encrypts the bitstring plaintext <pt> under key <e,n> where e is an integer and n a polynomial in GF(2)[x]
#The resulting ciphertext is also a bitstring
def encrypt(pt, e,  n):
    G.<y> = QuotientRing(F, F.ideal(n))#We need to take the result modulo n
    enc = toBits(pt)
    pt = 0
    for b in enc:
        pt = pt*y
        if b == "1" :
            pt = pt + 1
    return polyToBits(pt^e)
```

We're faced with a modified `RSA` system where $p$ and $q$ are irreducible elements in $GF(2)[x]$ of two random prime degrees. The rest of the system works as a regular `RSA`.

Unlike the integer factorization problem that is the basis for `RSA` security, it's not a difficult problem to factor a large degree polynomial, `sagemath` actually does it in a second. From that result, it's easy to evaluate the degree of the polynomials `p` and `q` and therefore retrieve `d1` and `d2`. Once we know both of the random primes, we can compute $$\phi(n) = (2^{d_{1}}-1) * (2^{d_{2}}-1)$$. Once we have $\phi(n)$, we can compute $$d = e^{-1} \mod \phi(n)$$.

Then, we can retrieve the message with regular `RSA` decryption, by calling the encrypt function again to compute $m = ct^d \mod n$ .

```python
# helper function toPolynomial() available in the annex file solve.sage
# n, ct and e are given as parameters

poly = toPolynomial(n)

# print(factor(poly)) -> we see d1 and d2
d1 = 2689
d2 = 2237
phi = (2**d1-1)*(2**d2-1)

inv_e = inverse_mod(e,phi)

print(encrypt(ct, inv_e, poly))
```

We retrieve something like *"What is the chance that we recover this one ! Zero !!! Why even trying. We have the new RSA and, as a bonus, it is much much more faster. I'm the new Rivest, Shamir and Adleman combined! The flag will be given soon. It's BA22{D1ff3r3ntUnd3rly1ngPr0bl3m}"* and here is the flag !

## Polynomial 2

### Description

*After the RSA failure, he decided to try the same idea with the Rabin cryptosystem.  You are given the encryption script, the public key n and a ciphertext.*

### Details

Category:    Crypto

### Solution

The source code is mostly the same, except we have generated `n` but don't have `e` and that the encrypt function looks different. 

```python
def encrypt(pt, n):
    G.<y> = QuotientRing(F, F.ideal(n)) #We will take our polynomials mod n
    enc = toBits(pt)
    pt = 0
    for b in enc:
        pt = pt*y
        if b == "1" :
            pt = pt + 1
    return polyToBits(pt**2)
```

This time we're facing the [Rabin cryptosystem](https://en.wikipedia.org/wiki/Rabin_cryptosystem).

A quick read informs us that the system is also based on the difficulty of integer factorization, which we have proved easy on polynomials in the first challenge. So we decide to do the same as before and retrieve `d1` and `d2` then calculate $$\phi(n)$$.

```python
d1 = 2917
d2 = 2473
phi = (2**d1-1)*(2**d2-1)
```

Then, we need to find a way to invert the encryption $$ct = m^2 \mod n$$. My colleague found [this question](https://crypto.stackexchange.com/questions/17988/algorithm-for-computing-square-roots-in-gf2n) on the crypto stack exchange that explains you can retrieve $x$ from $x^2$ by computing $$(x^2)^{2^{n-1}} \mod n$$ since $$(x^2)^{2^{n-1}} = x^{2*2^{n-1}} = x^{2^n}$$ and $$x^{2^n} \equiv x \mod n$$. Computing to the power of $$2^{n-1}$$ would be expensive, luckily we can use [Euler's theorem](https://en.wikipedia.org/wiki/Euler%27s_theorem) to reduce the exponent, so $$x^y \mod n \equiv x^{y \mod \phi(n)} \mod n$$. Reducing the exponent this way allows for a faster computation.

```python
d = pow(2,(d1*d2-1), phi)

def encrypt(pt, n, x=2):
    G.<y> = QuotientRing(F, F.ideal(n)) #We will take our polynomials mod n
    enc = toBits(pt)
    pt = 0
    for b in enc:
        pt = pt*y
        if b == "1" :
            pt = pt + 1
    return polyToBits(pt**x)

print(encrypt(ct, poly, d))
```

And here we go again : *"What is the chance that we recover this one ! Zero !!! Why even trying. We have the new Rabin and, as a bonus, it is much much much much faster. I'm the new legendary cryptographer!! The flag will be given soon and repeated. It's BA22{Irr3duc1b1l1tySh4llN0tR3pla4cePrimality}"*.



Challenges resources are available in the [resources folder](https://github.com/duksctf/duksctf.github.io/tree/master/resources/2022/blackalps/polynomials)

