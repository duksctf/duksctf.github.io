---
layout: post
title: "GreHack 2019 - Shady Secrets Sharing"
mathjax: true

date: 2019-11-16

---

*Shamir secret sharing scheme. Only the prime number to perform computations is unknown but using anyone allows to recover the secret.*

<!--more-->

### Description

by [Antoxyde](https://twitter.com/Antoxyde)

solved 2 times

150 points

Dark secret are being shared out there.. Try to find you way through!

[Download](/resources/2019/grehack/shadysecretsharing/157384352045369723575d08aa73fdb1d959072a6a30499a61c4e7a75.tar.gz)

### Solution

The scheme is a standard [Shamir's Secret Sharing](https://en.wikipedia.org/wiki/Shamir%27s_Secret_Sharing) algorithm with a 6 part threshold among 12 participants. In this case there is 38 secrets which are the characters of the flag. The file *secret_data_shhhhh.txt* contains the shares and the participants associated for each of the 38 secrets:

```python
with open("secret_data_shhhhh.txt") as f:
        data = f.read()
    
secret_data = eval(data)
print(len(secret), secret_data[0])

38 [('KassKou', 55831235), ('xXIPT4BL3SXx', 489187427), ('cypherpunk', 2407374785), ('__malloc_hook', 8280553175), ('Rainbow Bash', 22532355551), ('L1c0rn3P0w4', 52130507315)]

```

Since we have 6 shares we are able to reconstruct the secret. The algorithm is defined over the integers but nothing prevent us to compute the solution in a finite field if the prime is bigger than 256. The following script inspired by Wikipedia computes the Lagrange interpolation of the shares:

```python
#!/usr/bin/env python3
import gmpy2

#5th Mersennes prime
prime = 8191

def lagrange_interpolate(x, x_s, y_s, p):
    k = len(x_s)
    assert k == len(set(x_s)), "points must be distinct"
    def PI(vals):  # upper-case PI -- product of inputs
        accum = 1
        for v in vals:
            accum *= v
        return accum
    nums = []  # avoid inexact division
    dens = []
    for i in range(k):
        others = list(x_s)
        cur = others.pop(i)
        nums.append(PI(x - o for o in others))
        dens.append(PI(cur - o for o in others))
    den = PI(dens)
    num = sum([ nums[i] * den * y_s[i] % p * gmpy2.invert(dens[i], p)
               for i in range(k)])
    return ( num * (gmpy2.invert(den, p) + p)) % p

if __name__ == '__main__':

    my_super_hackerz_party_members = ['KassKou', 'xXIPT4BL3SXx', 'cypherpunk', '__malloc_hook', 'Rainbow Bash', 'L1c0rn3P0w4', 'Patrick', 'k4l1_i5_b43', 'p0rt_f0rward3r', 'GH19{NotTheFlag}', 'Kabriolé', 'Kadabra']	
	
    with open("secret_data_shhhhh.txt") as f:
        data = f.read()
    
    secret_data = eval(data)

    for i in range(len(secret_data)):
        shares = []
        for d in secret_data[i]:
            x = my_super_hackerz_party_members.index(d[0]) + 1
            shares.append((x,d[1]))
	
        x_s, y_s = zip(*shares)
        print(chr(lagrange_interpolate(0, x_s, y_s, prime)), end="")
    print()

```

The script execution reconstructs properly the flag:
```
GH19{p0lyn0mial5_4r3_fun_4r3'nt_th3y?}
```

