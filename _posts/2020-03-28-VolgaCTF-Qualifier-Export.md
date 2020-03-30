---
layout: post
title: "VolgaCTF Qualifier 2020 - Export"
mathjax: true

date: 2020-03-28
---

*Key recovery attack of a stream cipher which turn out to be the A5/2 cipher from GSM. Existing attacks apply to recover the secret key.*

<!--more-->

### Description

*We've got some algorithm from our friends, but we are not sure how secure it is. Can you take a look?*

*To prove it's bad send us the recovered key in hex format like*
```
VolgaCTF{0x0123456789ABCDEF}
```

[server.py](/resources/2020/volgactf/export/server.py) [cipher.py](/resources/2020/volgactf/export/cipher.py)

```
nc export.q.2020.volgactf.ru 7778
```

### Details

Points:      300

Category:    crypto

Validations: 10

### Solution

The server simply encrypts a message coming from us and return directly. The message is split in block of 115 bits and process one by one updating a frame number.

The cipher takes an unknown key of 64 bits. The frame number is 22 bits and incremented for each block. It uses 4 LFSRs for a total of a 82-bit state. The last LFSR is used to clock the three others and uses the majority function to decide which one will be updated. The structure of the cipher and the majority function made me think about the A5/1 cipher used in the GSM cellular telephone protocol I studied a long time ago during my [studies](https://link.springer.com/book/10.1007/b136373).

<img src="/resources/2020/volgactf/export/a52.png" width="800">

However when comparing the output of the cipher.py file to the test vector of A5/1 algorithm it did not match. It turns out that it was the A5/2 algorithm which was similar but developped to be weaker and used for export. It makes the title of this challenge clear then. Then I figured out that Barkan, Biham and Keller developed an [attack](https://www.cs.technion.ac.il/users/wwwb/cgi-bin/tr-info.cgi?2006/CS/CS-2006-07) to recover the secret key of this algorithm. I even found a publicly available implementation of the attack [online](https://github.com/rblaze/a52crack). The test vectors were the same expect that the key bits were swapped for each bytes:

```c
const unsigned char goodAtoB[15] = {
		0xf4, 0x51, 0x2c, 0xac, 0x13, 0x59, 0x37, 0x64,
		0x46, 0x0b, 0x72, 0x2d, 0xad, 0xd5, 0x00
	};
	const unsigned char goodBtoA[15] = {
		0x48, 0x00, 0xd4, 0x32, 0x8e, 0x16, 0xa1, 0x4d,
		0xcd, 0x7b, 0x97, 0x22, 0x26, 0x51, 0x00
	};
//	const u_char key[8] = {0x00, 0xfc, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff};
	const u_char key[8] = {0x00, 0x3f, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff};
	const u_int testframe = 0x21;
```

So we would need to swap back the key once found. I compiled it
```bash
$ cd common/ && make && cd .. && cd precomp/ && make
```
And then precompute tables for the attack
```bash
$ ./precomp 0 &
$ ./precomp 1 &
$ ./precomp 2 &
$ ./precomp 3 &
cd ..
```
I waited a couple of hours and the precomputation was ready. The file **main.cpp** contains a test function which would perform the attack. It expects 3 blocks of 48 bytes of keystream with consecutive frame numbers. Then it will return the secret key. To have the keystream, I sent null bytes to the server and I got the following answer:

```
rD6Y6bBYmk8Z3tgdseWA2uDT/vYTfhYQd0l5/i2AVZXRNszyBVlXa1B9bYeA0Cy1T5Xm6FbsmdNq5c5AbjLdIn0oMRyV1Jh5lJoAE+UOwdUTUzLz3RB+3WtAJlkfCHeNcGjgq+K1ryLA4/hCLuvFeuMNfPwm5D6As5sB2atP7gJ33yd0AYMAuUZ5MM+ripdTicawFW3AuaMAbycI4R+jqJiatKLAdQ7r5Ab1CZUDcuA7BQDA3lONWRdFuYaHxWMTOPDAamQrC6l9efj9YvzEoHYAfMc8ew9jD5Nw9GOa8nyAiJasapDPtVxq072xzjDAJfTcNiAYFbLj8Wn28IxA
```

I arranged the result in my [C file](/resources/2020/volgactf/export/solve.cpp) and launched the attack:
```bash
$ make && ./solve
CRC selftest ok
A5 selftest ok
frame 00000000
...
R4 0000fffd
Key:
1101010100111111000110011111111111111111100011000010010110110011
```

Then I restored the bits in the correct order:
```python
s = "110101010011111100011001111111111111111110001100001001011011001"

print("VolgaCTF{0x", end="")
for b in range(8):
    print("{:X}".format(int(s[b*8:(b+1)*8][::-1],2)), end="")
print("}")
```
And got the flag.
```bash
VolgaCTF{0xABFC98FFFF31A44D}
```
