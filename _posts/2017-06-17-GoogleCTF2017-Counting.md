---
layout: post
title: "Google CTF 2017 - Counting (RE)"
date: 2017-06-18
---

*We're given two files: an ELF binary `counter`, and some data `code`. The goal of the challenge is then to find the output of `./counter 9009131337`. Keywords: reverse engineering, virtual machine, hailstone sequence, fibonnaci modulo*

<!--more-->

### Description

*This strange program was found, which apparently specialises in counting. In order to find the flag, you need to find what the output of ./counter 9009131337 is.*

*File1: [counter](../resources/2017/gctf/counting/counter)*

*File2: [code](../resources/2017/gctf/counting/code)*

### Details

Points:      246

Category:    reverse

Validations: 33

### Solution

---
#### Part 1 - Initial analysis

We're given 2 files: a stripped x64 ELF `counter`, and some data `code`:
```bash
$ file code counter
code:    data
counter: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 2.6.24, BuildID[sha1]=ac70b7c58cc7989f829c0f0d50431ea0a92cbefb, stripped
```

Our goal is to find the output of `counter` for `9009131337`, however testing it for small inputs like `10, 20, 30, 40` already takes quite some time...
```bash
$ time ./counter 40
CTF{0000000000000280}

real	2m1.388s
user	2m0.744s
sys	0m0.008s
```

Fortunately, opening `counter` in IDA reveals a pretty small quantity of code. It's mainly composed of 3 functions:
- the main function
- a 2nd function reading and parsing the content of `code`
- a 3rd function iterating over the read content and performing some computations

This scheme very much evokes a virtual machine, where `code` would be a program, and `counter` its interpreter. This is confirmed by the reverse engineering, that reveals the following pseudo-algorithm for the main function:

```c
{% raw %}int main(int argc, argv) {
    read_and_parse_code();

    uint64_t *registers = malloc(26 * sizeof(uint64_t));
    memset(registers, 0, 26 * sizeof(uint64_t);
    registers[0] = strtol(argv[1], NULL, 10);

    uint32_t entry_point = 0;
    execute_code(registers, entry_point)

    printf("CTF{%016llx}\n", registers[0]);
    return 0;
}{% endraw %}
```

---

#### Part 2 - Virtual machine

Analyzing the parsing function (which I named `read_and_parse_code` above) gives us initial information on the VM instructions format. It also contains strings like `"Invalid reg"` or `"Invalid ins"`, that add semantic for some checked data. In the end we can deduce the following:
- each instruction is of size `0x10`
- there are only 3 types of instructions: `0`, `1`, and `2`
- there are 26 registers (from R0 to R25)
- some fields for an instruction are named `next`, `reg`, or `amo`
- instructions have the following fields, depending on their type:
    - all instructions: `type (+0x0)`
    - type 0: `reg (+0x4)` and `next (+0x8)`
    - type 1: `reg (+0x4)`, `next1 (+0x8)`, and `next2 (+0xC)`
    - type 2: `amo (+0x4)`, `next1 (+0x8)`, and `next2 (+0xC)`
- other offsets are unused

Inspecting the execution function (which I named `execute_code` above) then allows us to find the implementation of these 3 instructions:
- instruction type 0 is `INC_THEN_GOTO`:
    - inconditionnaly increment the pointed register
    - then go to the `next` instruction

    ```c
    regs[ instr.reg ] += 1;
    pc = instr.next;
    ```

- instruction type 1 is `IF_DEC_THEN`:
    - if the pointed register is not 0, decrement it and go to `next1`
    - otherwise, only go to `next2`

    ```c
    if( instr.reg ] > 0 ) {
        regs[ instr.reg ] -= 1;
        pc = instr.next1;
    } else {
        pc = instr.next2;
    }
    ```

- instruction type 2 is slightly more complicated:
    - copy the registers values in a newly allocated array
    - recursively call `execute_code` with entry point `next1`
    - import `amo` numbers of registers from the results of the call (meaning a function can have several return values)
    - then go to `next2`

    ```c
    memcpy(new_regs, regs, 26 * sizeof(uint64_t));
    execute_code(new_regs, instr.next1);
    memcpy(regs, new_regs, instr.amo * sizeof(uint64_t));
    pc = entry.next2;
    ```
    It's a sub-function `CALL`!

Quite unusual. But we now have all the needed information to understand what `code` implements.

Before starting, we can still deduce a few important things from `execute_code`:
- a function can have several return values (specified in the `amo` field of a `CALL` instruction, and returned in registers `{R0..RN}`)
- execution of a function returns when `pc == count_instr` where `count_instr` is the total number of instructions in `code` (`0x77`).

---

#### Part 3 - VM program

The program in `code` contains `0x77 (119)` instructions. Displaying them in hex after removing the unused parts, gives something that is good enough to analyze:

```bash
| PC  | TYPE    | REG/AMO | NEXT1  | NEXT2
-------------------------------------------------
(:00, '0100 .... 0000 .... 01000000 02000000')     > IF_DEC_THEN       R0, :01, :02
(:01, '0000 .... 0100 .... 00000000 ........')     > INC_THEN_GOTO     R1, :01
(:02, '0000 .... 0200 .... 03000000 ........')     > INC_THEN_GOTO     R2, :03
(:03, '0000 .... 0200 .... 04000000 ........')     > INC_THEN_GOTO     R2, :04
...
(:0d, '0200 .... 0100 .... 6c000000 0e000000')     > CALL              {R0}, :6c, :0e
...
(:10, '0100 .... 0200 .... 10000000 11000000'),    > IF_DEC_THEN       R2, :10, :11
(:11, '0100 .... 0000 .... 12000000 13000000'),    > IF_DEC_THEN       R0, :12, :13
(:12, '0000 .... 0200 .... 11000000 ........'),    > INC_THEN_GOTO     R2, :11
...
(:31, '0200 .... 0200 .... 5c000000 32000000')     > CALL              {R0..R1}, :5C, :32
...
(:75, '0100 .... 0100 .... 76000000 77000000')
(:76, '0000 .... 0000 .... 75000000 ........')
```

**Static analysis**

By manualy analysing the hex-displayed program, we learn several things:

- Functions:
    - We can split the program in sub-functions by looking at the `next1` field of all the `CALL` instructions
    - We can also learn how many return values these sub-functions have by looking at the `amo` field of the `CALL` instructions

    For instance, the 2 `CALL`s instructions above at `:0D` and `:31` indicate that there's a sub-function at `:6C` that have only one return value (returned in `{R0}`), and another one at `:5C` that have 2 return values (returned in `{R0..R1}`)

    We thus identify 9 sub-functions (in addition to the main af `:00`), at offsets `:14`, `:1D`, `:2D`, `:40`, `:54`, `:5C`, `:63`, `:6C` and `:71`, all having a unique return value, except for `:5C` that has 2.

- Patterns:

    We can identify instruction patterns for commonly used operations:

    - A `IF_DEC_THEN` jumping to itself can be understood as *"decrement reg until it's 0"*: it is thus `SET reg=0`.

        ```bash
        :selfpc     IF_DEC_THEN  <reg>, :selfpc, <next>
        ```
        For instance, the above instruction at `:10` is `SET R2=0`

    - The following `IF_DEC_THEN` + `INC_THEN_GOTO` couple can be understood as *"increment regY until regX-- is 0"*. It is thus `ADD regY, regX`.

        ```bash
        :pc1    IF_DEC_THEN    <regX>, :pc2, <next>
        :pc2    INC_THEN_GOTO  <regY>, :pc1
        ```
        For instance, the above couple at `:11` and `:12` is `ADD R2, R0`

    - Chaining these 2 first patterns (`SET regX, 0` + `ADD regX, regY`) can be simplified to `MOV regX, regY`

        For instance, the previously inspected instructions at `:10`, `:11` and `:12` actually implements `MOV R2, R0`


We can then start individually reversing the identified functions. Starting with the small ones reveals that `:54` is only `return R1 as R0`, or that `:6C` is `return (R1 < R2)`, but also that this is quite time consuming, and we better move to a dynamic analysis.


**Dynamic analysis**

The good part of having a 3-instructions VM is that it's pretty simple to implement. The script [`exec.py`](../resources/2017/gctf/counting/exec.py) is a simple interpreter that executes a function from an entry point, and that can print the registers values and the instruction details at each step. It can be used to perform black-box analysis of individual sub-functions, by only observing the outputs for given inputs:

```python
# function :71 below seems to be `return (R1 - R2)`

In [3]: exec_code(pc=0x71, regs=[0,10,2]) [0]
Out[3]: 0x8 (8)

In [4]: exec_code(pc=0x71, regs=[0,123,45]) [0]
Out[4]: 0x4e (78)
```

Using this interpreter mixed with some static analysis for confirmation, we can fully understand the goal of each function, detailed below. We start from the simple functions that don't contain any calls, to then move up to the bigger ones, and finally reach `main`. The file [`code_disass_full.txt`](../resources/2017/gctf/counting/code_disass_full.txt) contains the fully commented disassembly of `code`.

- function `:71`: `R1_SUB_R2 { RETURN R0 = MAX(0, R2-R1) }`
- function `:6C`: `R1_LT_R2  { RETURN R0 = (R1 < R2) }`
- function `:63`: `R1_MOD_R2 { RETURN R0 = (R1 % R2) }`
- function `:5C`: `DIV_R2_2  { RETURN R0 = (R2 / 2), R1 = (R2 % 2) }`
- function `:54`: `RET_R1    { RETURN R0 = R1 }`
- function `:40`:
    ```
    F40 {
        RETURN R0=0 if R1==0
        RETURN R0=1 if R1==1
        ELSE RETURN R0 = (F40(R1-1, R2) + F40(R1-2, R2)) % R2
    }
    ```
    We recognize here a recursive function summing its 2 preceding values, but using a modulo. It's the [Fibonacci suite](https://en.wikipedia.org/wiki/Fibonacci_number), so `F40 = FIBONACCI_MODULO`.

- function `:2D`:
    ```
    F2D = {
        RETURN R0 = (R1 / 2) IF R1 is pair
        RETURN R0 = (R1 * 3 + 1) IF R1 is odd
    }
    ```
    This time, we recognize in this function the formula to compute the next element of the [Hailstone sequence](https://en.wikipedia.org/wiki/Collatz_conjecture), so `F2D = HAILSTONE_NEXT`. The *Collatz conjecture* is that this sequence eventually reaches 1 for all positive integer, but it has not been proven. However this has been verified for at least all values up to `5×2^60`.

- function `:1D`:
    ```
    F1D {
        R2 = 0
        DO
            R1 = HAILSTONE_NEXT(R1)
            R2 += 1
        WHILE (R1 > 1)
        RETURN R0 = R2
    }
    ```
    This function increments a counter for each iteration of the hailstone sequence for a given parameter, until it reaches `1`: in other words, it computes the length of the hailstone sequence for this parameter. So `F1D = LEN_HAILSTONE`

- function `:14`:
    ```
    F14 {
        R2 = 0
        DO
            R2 += LEN_HAILSTONE(R1)
            R1 -= 1
        WHILE (R1 > 0)
        RETURN R0 = R2
    }
    ```
    This function sums the lengths of the hailstone sequences of all values from 1 to a given parameter. So `F14 = SUM_LEN_HAILSTONE`

- function `:00` (`main`):

    ```
    MAIN {
        IF PARAM < 11
            RETURN R0 = 0
        ELSE
            MOD = SUM_LEN_HAILSTONE(PARAM)
            FLAG = FIBONACCI_MODULO(PARAM, MOD)
            RETURN R0 = FLAG
    }
    ```
    Finally, the main function computes a fibonnaci modulo of the given parameter, using the result of `SUM_LEN_HAILSTONE` for this parameter as modulo.
    That's it. That's the end of the reverse-engineering part: The entire challenge can now be resumed in the following one-liner:
    ```
    flag = fibonnaci_modulo( N = 9009131337, MOD = SUM{i=1..N}(length(hailstone_sequence(i))))
    ```

---
#### Part 4 - Solving

Both the **hailstone sequence** and **fibonnaci sequence modulo** have already been discussed online: [link1](https://rosettacode.org/wiki/Hailstone_sequence), [link2](https://medium.com/competitive/huge-fibonacci-number-modulo-m-6b4926a5c836), or [link3](https://stackoverflow.com/questions/37009744/calculate-huge-fibonacci-number-modulo-m-in-c).

The interesting part to know about fibonnaci, is that it is cyclic when computed to a modulo. The period of this cycle for a given modulo is called the [Pisano period](https://en.wikipedia.org/wiki/Pisano_period) (see links 2 and 3 above).

The problem can then be decomposed in 3 parts:
0. Finding the modulo by summing the length for all hailstone sequences up to `9009131337`
0. Finding the pisano period for this given modulo
0. Computing the fibonnaci number for `9009131337` with the given modulo and pisano period

Fortunately, publicly available implementations from the above links can be adapted to perform these 3 tasks. See files [`hailstone.c`](../resources/2017/gctf/counting/hailstone.c), [`pisano.c`](../resources/2017/gctf/counting/pisano.c), and [`fibo_mod.c`](../resources/2017/gctf/counting/fibo_mod.c)

```bash
$ time ./hailstone 9009131337
<MOD:0x1da61603168>
./hailstone 9009131337  1164.38s user 5.17s system 99% cpu 19:38.43 total

$ time ./pisano $(( 0x1da61603168 ))
<PISANO:0x876915450>
./pisano $(( 0x1da61603168 ))  460.00s user 1.95s system 99% cpu 7:45.60 total

$ time ./fibo_mod 9009131337 $(( 0x1da61603168 )) $(( 0x876915450 ))
<FLAG:0x1bae15b6382>
./fibo_mod 9009131337 $(( 0x1da61603168 )) $(( 0x876915450 ))  111.83s user 0.28s system 99% cpu 1:52.68 total
```

The final flag is then `CTF{000001bae15b6382}`.

One final note here, is that the pisano period we found was greater than `9009131337`. This means that it didn't bring any benefits, and computing it was actually useless... But it was still interesting to learn it exists :)
