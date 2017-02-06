---
layout: post
title: AlexCTF 2017 - Bring weakness
date: 2017-02-04
---

*A sever shows us random looking numbers and we have to predict the output of the next number. The numbers were generated using a linear congruential generator. Using the Marsaglia method we were ale to fully recover the parameters of the PRNG and thus predict the number sequence.*

<!--more-->

### Description

*We got this PRNG as the most secure random number generator for cryptography.*

*Can you prove otherwise*

*nc 195.154.53.62 7412*


### Details

Points:      300 

Category:    crypto

Validations: 76

### Solution

When we connected to the server we got the following interaction:

```bash
$ nc 195.154.53.62 7412
Guessed 0/10
1: Guess the next number
2: Give me the next number
2
2607191779
Guessed 0/10
1: Guess the next number
2: Give me the next number
2
975774374
Guessed 0/10
1: Guess the next number
2: Give me the next number
```

So it seems that we have to guess the following value of a PRNG knowing the previous values but not the algorithm. After playing a bit with multiple connections to the server, I tried to see if the implementation was not a [linear congruential generator](https://en.wikipedia.org/wiki/Linear_congruential_generator). Meaning that the next value $$x_{n+1}$$ will be computed linearly from the previous value $$x_n$$ *i.e* $$x_{n+1} = ax_n +b \mod m$$. We have to find $$m$$, $$a$$, and $$b$$. I first noticed that all the values were coded on 32 bits so $$m < 2^{32}$$. Then according to the [Marsaglia](http://www.reteam.org/papers/e59.pdf) method we can find $$m$$ by computing the least common divisor of the determinants of several given outputs. We can repeat the procedure until $$m<2^{32}$$ which gave $$m = \mathtt{0xffffffff}$$. Computing $$a$$ is then easy because each consecutive outputs have a linear dependance thus $$a = (x_{n+2}-x_{n+1})(x_{n+1}-x_n)^{-1} \mod m$$. In our case it gave $$a = \mathtt{0x939a5ec0}$$. Finally we have $$b = x_{n+1} - ax_n \mod m = \mathtt{0x8aa90086}$$.

Then from a single value we are able to predict the next value with a simple computation. The complete computation are given in this [script](/resources/2017/alexctf/bringweakness/solution.py) which allows to recover the flag:

```bash
$ python3 solution.py 
[2333394338, 3027468667, 937323110, 3491539096, 1367160218, 2111818057, 1743138065, 385408531, 3028765313, 3928804162, 1369218140, 1408119226]
m = 0xffffffff
a=2476367552
b=2326331526
Initial number: 3688430318
Next number (in decimal) is

Next number: 896975107
Guessed 1/10
1: Guess the next number
2: Give me the next number
Next number (in decimal) is

Next number: 842681045
Guessed 2/10
1: Guess the next number
2: Give me the next number
Next number (in decimal) is

Next number: 234035431
Guessed 3/10
1: Guess the next number
2: Give me the next number
Next number (in decimal) is

Next number: 3961618553
Guessed 4/10
1: Guess the next number
2: Give me the next number
Next number (in decimal) is

Next number: 1021667737
Guessed 5/10
1: Guess the next number
2: Give me the next number
Next number (in decimal) is

Next number: 4154774900
Guessed 6/10
1: Guess the next number
2: Give me the next number
Next number (in decimal) is

Next number: 1597680361
Guessed 7/10
1: Guess the next number
2: Give me the next number
Next number (in decimal) is

Next number: 1400691188
Guessed 8/10
1: Guess the next number
2: Give me the next number
Next number (in decimal) is

Next number: 1765742767
Guessed 9/10
1: Guess the next number
2: Give me the next number
Next number (in decimal) is

Next number: 939554780
flag is ALEXCTF{f0cfad89693ec6787a75fa4e53d8bdb5}

```
