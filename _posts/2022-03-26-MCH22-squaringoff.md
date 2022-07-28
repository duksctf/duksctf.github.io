---
layout: post
title: "May Contain Hackers 2022 - Squaring Off"
mathjax: true

date: 2022-07-25
---

*Discrete logarigm of in the multiplicative groups of a square prime.*

<!--more-->

### Description

[Download](/resources/2022/mch/squaringoff/squaringoff.tgz)

### Details

Points:      300

Category:    Crypto

Validations: 5


### Solution

The problem was simple, we had to solve the discrete logarithm of $2^{flag} \mod n$. We could quickly figure out that $n$ is a square of a prime number.

```bash
sage: n = 0xfffffffe00000002fffffffe0000000100000001fffffffe00000001fffffffe00000001fffffffefffffffffffffffffffffffe000000000000000000000001
sage: h = 4275333096397007849067777941008675457617279615546105194323216811550797075772016607215703868747693795339025886078058526791464546941731743196384839138407576
sage: n.is_prime()
False
sage: n.factor()
115792089210356248762697446949407573530086143415290314195533631308867097853951^2
```

It means that the order of the multiplicative group is $\varphi(n) = p(p-1)$. The first idea was to compute the [Pohlig-Hellman algorithm](https://en.wikipedia.org/wiki/Pohlig%E2%80%93Hellman_algorithm) to recover the flag:
```bash
sage: p = 115792089210356248762697446949407573530086143415290314195533631308867097853951
sage: factor(p-1)
2 * 3 * 5^2 * 17 * 257 * 641 * 1531 * 65537 * 490463 * 6700417 * 835945042244614951780389953367877943453916927241
sage: pari(f"znlog(Mod({h}, {n}), Mod({2}, {n}), [{ord}, {factors_str}])")
```

However, $p$ and the largest factor of $p-1$ were too big, the computation was not finishing. Then we figure out that there is an isomorhism between the cyclic group:

$$H = \{ x \in (\mathbb{Z}/p^2\mathbb{Z})^*, x^{p-1} = 1 \mod p\}$$

to the additive group $\mathbb{Z}/p\mathbb{Z}$ exactly as in the [Okamoto–Uchiyama cryptosystem](https://en.wikipedia.org/wiki/Okamoto%E2%80%93Uchiyama_cryptosystem). This isomorphism is $L(x) = \frac{x-1}{p}$ and gives directly the discrete logarithm in the subgroup of order $p$. However, this was not enougth to recover the flag.

Thus, we run the Pohlig-Hellman algorithm on the remaining factors except $p$ and the second bigger one. The we reconstruct the flag modulus $n$ divided by the missing prime number and it was sufficient to recover the flag completely:
```bash
sage: solve.sage
b'flag{1b8cdf523310e91a3790a5c938707f6b}'
```

Here it the full [solution](/resources/2022/mch/squaringoff/solve.sage).