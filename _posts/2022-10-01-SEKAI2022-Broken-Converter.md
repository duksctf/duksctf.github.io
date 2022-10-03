---
layout: post
title: "SEKAI 2022 - Broken Converter"
mathjax: true

date: 2022-10-01
---

*XPS file which looks corrupt but in fact it is a OpenType font inside scrambled using Microsoft custom algorithm and then using fontdrop website to recover his secret.*

<!--more-->

### Description

Miku has finally finished her assignment and is ready to submit – but for some reason, the school requires all assignments to be submitted as `.xps` files. Miku found a converter online and used the converted file for submission. The file looked good at first, but it seems as if there’s something broken in the converter. Can you help her figure out what is wrong?

Note:
This challenge shares the same file as flag Mono.
Author: pamLELcu

### Details

Points:      100 / 368

Category:    forensic

Validations: 94 / 47


### Solution

We receive a [XPS file](/resources/2022/sekai/broken_converter/Assignment-broken.xps) which looks like broken. After unzipping the file inside the folder `Resources` we found a file called `02F30FAD-6532-20AE-4344-5621D614A033.odttf`.
After researching on the web about this file we found thanks to [wikipedia](02F30FAD-6532-20AE-4344-5621D614A033.odttf) that it a file used in the `Microsoft XML Paper Specification` and is an obfuscated OpenType font.

The popular tool [okular](https://github.com/KDE/okular/blob/master/generators/xps/generator_xps.cpp) from KDE already implemented the algorithm to desobfuscate it.
With the following [python script](/resources/2022/sekai/broken_converter/unscramble.py) it is possible to unscramble it. In fact the scrambling is easy to understand, the first 32bytes are scrambled with the `name` of the file (guid).

With the file descrambled, we can use the site [fontdrop](https://fontdrop.info/) to analyze it.
Looking at the `Glyphs` table, the flags is written:

<img src="/resources/2022/sekai/broken_converter/flag_glyphs.png" width="800">

BONUS:

They were another task with the same file. The flag can also be recovered using the same tool again.
This time playing with the different feature of the font:

<img src="/resources/2022/sekai/broken_converter/flag.gif">


Challenges resources are available in the [resources folder](https://github.com/duksctf/duksctf.github.io/tree/master/resources/2022/sekai/broken_converter)

