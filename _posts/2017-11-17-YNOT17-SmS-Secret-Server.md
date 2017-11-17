---
layout: post
title: "Y-Not-CTF - SmS Secret Secure Server - Crypto"
date: 2017-11-17
---

*We're given a ssh username, server ip and public key using ECDSA, along with a _very secure RNG_ python script used to generate the ECDSA key. Exploiting a weakness in the RNG, we can enumerate all possible keys and find the private key to log on the server.*

<!--more-->

### Description

Here is a *very secure* PRNG used to generate a secret ECDSA key, you'll never find it.
And we were given a SSH command to log as bob on some local server, as well as two files:
[id_ecdsa.pub](/resources/2017/ynotctf/crypto-sms/id_ecdsa.pub) and [RNG.py](/resources/2017/ynotctf/crypto-sms/RNG.py)

### Details

Points:      600

Category:    crypto

Validations: 2

### Solution

The RNG script is really simple:
```python
def genECDSAPriv(x): #To seed with 128 bits of /dev/random
    p = 14219462995139870823732990991847116988782830807352488252401693038616204860083820490505711585808733926271164036927426970740721056798703931112968394409581
    g = 13281265858694166072477793650892572448879887611901579408464846556561213586303026512968250994625746699137042521035053480634512936761634852301612870164047
    keyLength = 32
    ret = 0
    ths = round((p-1)/2)
    #To increase security, throw away first 10000 numbers
    for j in range(10000):
        print pow(g,j,p)
        x = pow(g,x,p)
    for i in range(keyLength*8):
        x = pow(g,x,p)
        if x > ths:
            ret += 2**i
    return ret
```

As you can see, the 10000 first exponentiations are just thrown away, which makes it relatively slow to run.
This RNG is actually based on the ["Blum-Micali PRNG"](https://en.wikipedia.org/wiki/Blum–Micali_algorithm) and relies on the difficulty to solve the discrete logarithm problem in sufficiently big cyclic groups.

The `id_eddsa.pub` file is simply an SSH key in OpenSSH format:
```
ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBPZc7m3goxEkZjlzoa0f7dxod7vUT+NzSMMeyLl2YNLVvuNJ7WUel8VPkK3Q8hMLFMsKrIUCWJNHN5Lg3/edo1c= bob@mastercrypto
```

So, we know that we are dealing with an ECDSA keypair on the nist's curve P256. This curve has yet to be broken by cryptographers and is considered to provide a security of roughly 128 bits. So we won't try to crack the public key, but if we could find a flaw in the PRNG used, then we could regenerate the private key used to produce this public key.

Now, let's get back to that random number generators and let's run it a few time:
```python
import random
import RNG

test = random.getrandbits(128)
print RNG.genECDSAPriv(test)
```

And... Wow, this is slow: 7 seconds to compute the "_random_" value `52771737243107955452457115236761733307198355296235460844025885616021236394942`!

Let's see what it generates if we run it a few times:
```python
import random
import RNG

for _ in range(10):
    test = random.getrandbits(128)
    print RNG.genECDSAPriv(test)
```
and after an excruciating wait, we obtain:
```
56693337563003437446218818861732426020291386135230851162098750444697716348746
61755780926568637559237858671300217521743991821674967487710711470887002474632
115792089237316195423570985008687907853269984665640564039457584007913129639935
113386675126006874892437637723464852040582772270461702324197500889395432697493
42140956620106037719007025061362410290117084990469006220870867405983591508719
33803171228513919274316948727372377942283792080283425228211081800947874839530
77305463456367066925437428445119014850274586342778776595296254111629978560855
0
86242713400159816434894901935210166936780685400435707600778167226305422994341
77305463456367066925437428445119014850274586342778776595296254111629978560855
```

Mhhhh, this looks really bad: there is a 0 value, which makes no sense and even worse, there is twice the same value `77305463456367066925437428445119014850274586342778776595296254111629978560855`! 
The probability of obtaining either is theoretically around $$2^{-128}$$, already negligible, but to have both that's inconceivable. 

So we've confirmed that this RNG script is seriously broken, but to which extent? What could go wrong with Blum-Micali PRNG? Well, obviously, if one were to chose a generator  $$g$$ value which is not a root of the unity, then it wouldn't be a generator of the whole cyclic group $$/mathbb{Z}/p/mathbb{Z}$$, but would instead only generator a small subgroup $$/langle g/rangle>/lt/mathbb{Z}_p$$.

This can be easily empirically tested by simply trying to generate the first 10000 elements of the group with the following script:
```python
p = 14219462995139870823732990991847116988782830807352488252401693038616204860083820490505711585808733926271164036927426970740721056798703931112968394409581
g = 13281265858694166072477793650892572448879887611901579408464846556561213586303026512968250994625746699137042521035053480634512936761634852301612870164047

elements={1}

for i in range(10000):
    x = pow(g,i,p)
    elements.add(x)

print "There are %d elements in this set." % len(elements)

with open("subgroup.txt","w") as f:
    for x in elements:
        f.write("%d\n" % x)
```
Which return us a nice little: "There are 673 elements in this set." when run! So, we're effectively working in a small subgroup! 

Let's simply then run our RNG on all possible elements of this subgroup, thus obtaining all possible RNG's output values:
```python
def genRNG(x):
    p = 14219462995139870823732990991847116988782830807352488252401693038616204860083820490505711585808733926271164036927426970740721056798703931112968394409581
    g = 13281265858694166072477793650892572448879887611901579408464846556561213586303026512968250994625746699137042521035053480634512936761634852301612870164047
    keyLength = 32
    ret = 0
    ths = round((p-1)/2)
    for i in range(keyLength*8):
        x = pow(g,x,p)
        if x > ths:
            ret += 2**i
    return ret

values={0}
with open("subgroup.txt", "r") as f:
    for x in f.readlines():
        values.add( genRNG(int(x.strip(),10)) )

print "There are %d different values in this set." % len(values)

with open("allrng.txt","w") as f:
    for x in values:
        f.write("%d\n" % x)
```
And we thus obtain 318 different values that could have been outputted by the RNG script when generating the ECDSA private key, so let us try them all!

Now the hardest part begins, we must generate private keys given a secret integer and compare their public counterpart with the OpenSSH public key we were given at first!
Let's use Cryptography.io to do it, after digging through their online documentation, we end up with a script doing it all for us:

```python
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils

curve = ec.SECP256R1()
algo = ec.ECDSA(hashes.SHA256())

# we read the file as being an OpenSSH key and return it as a public key:
def readPubKey(filename):
    with open(filename, 'r') as f:
        data = f.read()
        return serialization.load_ssh_public_key(data,default_backend())

def testInt(inp):
    try:
        privateKey = ec.derive_private_key(
                inp, pubnum.curve,default_backend())
        if pubnum.public_numbers()==privateKey.public_key().public_numbers():
            return True, privateKey
        else:
            return False, None
    except:
        return False, None


pubnum=readPubKey("id_ecdsa.pub")
with open("allrng.txt","r") as f:
    for number in f.readlines():
        ok, priv = testInt(int(number.strip(),10))
        if ok:
            print 'Success, the secret int is:', number
            data = priv.private_bytes(encoding=serialization.Encoding.PEM,
                     format=serialization.PrivateFormat.TraditionalOpenSSL,
                     encryption_algorithm=serialization.NoEncryption())
            with open("id_ecdsa.priv","w") as f2:
                f2.write(data)
            print "Written to id_ecdsa.priv:","\n",data
            break
```

And we get the result:

```
Success, the secret int is: 74797630232915057348943966868030142897776888372961994633834332904430502239733

Written to id_ecdsa.priv: 
-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIKVd9V0q76rpV31XSrvqulXfVdKu+q6Vd9V0q76rpV31oAoGCCqGSM49
AwEHoUQDQgAE9lzubeCjESRmOXOhrR/t3Gh3u9RP43NIwx7IuXZg0tW+40ntZR6X
xU+QrdDyEwsUywqshQJYk0c3kuDf952jVw==
-----END EC PRIVATE KEY-----
```
Along with a file "id_ecdsa.priv", which we can use to authenticate as Bob on the SSH server we were given at the beggining.

Challenges resources are available in the [resources
folder](https://github.com/duksctf/duksctf.github.io/tree/master/resources/2017/ynotctf/)
