---
layout: post
title: Insomni'hack 2016 - Pcapbleeding
date: 2016-03-21
---


The [Insomni'hack](http://insomnihack.ch/) conference and CTF happened last Friday in Geneva, as usual it was a lot of fun. And as usual, Dragon Sector won the CTF, beating a few other world-class teams that made the trip for this on-site jeopardy CTF. About 80 teams registered, and the final ranking looks as follows for the first 25 teams:

![Ranking](/resources/2016/insomnihack/pcapbleeding/ranking.png) 

There was only one challenge in the crypto category, "pcapbleeding". With such a name, the vulnerability was obvious: [Heartbleed](http://heartbleed.com/). We were given three files
<ul>
        <li><code>attack_log.pcap</code>, a capture of a partial TLS session</li>
        <li><code>hb_scrt_ch.crt</code>, the certificate of the server</li>
        <li><code>pcap_flag.pcapng</code>, this one is self-explanatory</li>
</ul>
I worked on this challenge with my teammate Brecht Wyseur from the duks team. Here's how we solved it:

<!--more-->

Our first step was to look at the certificate and extract its public key.We did this with the command
<pre><code>openssl x509 -in hb_scrt.crt -text</code></pre>
and then manually copied the RSA-2048 modulus, equal to
<pre><code>0x00bf683ed2cc8c1f259bbf6428904cd5c32ae974e9bb1b52e39a31451923b4dbbd9502e34fec0a0441da9cc8ebdb2970ee9f945d4b01f1971ea3512f63c37f696c68bd34f552d9f2a92fa03a7e5965f2f9d80134c9dea1aa94732a506a114bc6160ab8d99c875922037a0bf39345d4ed0502270d3774f160163716db5c3f393c1d68f4a00c8c301b38ff9ba053eb9b7e1d60968761e6d3134abae2e04afc94069facd0566d93f11998be89ea4ac03f169c2f1da87ca15e997a4acf67c64052768ba00881f6288ddbb2bb6815935315ef52db939dd3e1cb39eafb188985ca445cee8b7f26a179770dca2f36d3d35bb7faef629d392a943a5cbad41d2ffabf4e1d61</code></pre>
The second step was to recover part of the private key from the network capture, doing first
<pre><code>tcpflow -r attack_log.pcap</code></pre>
in order to extract the reassembled content of the TCP session. Then the only thing we had to do was to lazily look for a prime number that factored the modulus in this dump, namely in the file <code>192.168.105.160.00443-192.168.105.001.40572</code> (obviously, the private key parts needed to be in the data sent from the server to the client). To do this I wrote the following script:

{% highlight %}
from binascii import hexlify
from pyprimes import isprime
import sys

fn = sys.argv[1]

d = open(fn, 'r').read()

n=0x00bf683ed2cc8c1f259bbf6428904cd5c32ae974e9bb1b52e39a31451923b4dbbd9502e34fec0a0441da9cc8ebdb2970ee9f945d4b01f1971ea3512f63c37f696c68bd34f552d9f2a92fa03a7e5965f2f9d80134c9dea1aa94732a506a114bc6160ab8d99c875922037a0bf39345d4ed0502270d3774f160163716db5c3f393c1d68f4a00c8c301b38ff9ba053eb9b7e1d60968761e6d3134abae2e04afc94069facd0566d93f11998be89ea4ac03f169c2f1da87ca15e997a4acf67c64052768ba00881f6288ddbb2bb6815935315ef52db939dd3e1cb39eafb188985ca445cee8b7f26a179770dca2f36d3d35bb7faef629d392a943a5cbad41d2ffabf4e1d61

for i in range(0, len(d) - 128):
    nb = bytearray(d[i:i+128])
    nb.reverse()
    # convert to int
    p = int(hexlify(nb), 16)
    if not isprime(p):
        continue
    q = n / p
    if q * p == n:
        print 'factor found: ', p
        
{% endhighlight %]

which after a few seconds found the prime factor
<pre><code>162800346840897460776468813649884118748559125156676009651818806350253200631182399318398587210444328205266057474343495440234163281091254518673126741452325095375914485073473011961346710968389549502805048181472650809456469931148070907250674606060817482309018037066114703019632076408777754991395159477650420299677</code></pre>
Note the <code>reverse()</code> in the code above, to parse numbers in little-endian rather than big-endian order. We first overlooked this detail and lost almost an hour...

To decrypt the encrypted data, you could just use Wireshark. It takes the private key in PEM format, which in this case yields
<pre><code>-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAry8C7aRdXa8bbb48yc0KVJ0QJZBVgnMK+yXznOdPFr71Gqun
4CM2F0aAwNpP6Ff+aQeSaWGKLoibEELWWE7BxrKUPui5fChqd7ftvi47lxUrT6cZ
7AkrigL7dmdXV53D/8uv6pmOtZs2T4rCSMRyLm88x642hvOP3r7XjZEeDbexvGul
Yd9NN5U8+icL8PNsZIxOZ6mUgK79X3RW5Gy3+cfZuIj8m6qwLCXn/bF8DENvzV33
sNDgv6biKOFSzlBo1g/n6wyBLUp2UB8cq8ir8/7LXDe4iSw/ox3DNyft3AnyMe7c
3SiM2si9O4zGchT7xIbhRrKaFv1y6LtGALro5wIDAQABAoIBADKsSY+OBMfNmASF
i7XfzoYtLHeBKYrjViDRmIchTXpJ4EJHtvaZmNLgvOuL+qM9mMSuwQYkhcDyGNB6
VOAUX+7mxwTvcn/cfPeGR4nEe842/GE8972T5Xk1ZaGZQOWCKCi8tXUJ2ALmE66s
d4hu8oxF9vHXjcQ5fbszvswfVu8mYd/duTncfIrcCO7lszWm6Bv9D1u/D/gF96Ud
yu4hSqGhv4cT4szfkwls4xXz55eFAPpbwFIB2lxVUEetbEpKIRpgi++IPMO3xGcD
b4/k132iX/Hcaeo2+2LhjKxDU4bkecLvRPYIDvA//tA7GUsWjWoiVyKx+YfE96EV
BTVmvakCgYEA3xngcKf9T06/gGc39a5ohGOy4Ee/W9cuCTNuTjiEou7B9flky+4j
+4UWrcE7xX4oYXib7DazDXsdIw7N9UGbpCEysvWKM4poIorl/32BLaX+QzZSLn8e
KmbeL0ZHOy8iHM6/iqbb7eMBWKstVgoAflbiAoOXAh/VwafqHuUBg0sCgYEAyQQ9
Kea7+NBRILIDHMAvPh8OWT/thS0QHeYiGFZlCktyVw/PZgzEPui32R2krGvS6NoW
zUQmtMJVo4oxIRTdIJUiQ2vG37LkmCU2pgBYi0ad+FMaoJ+Ww8sHlPFZsubreIpK
8FDVuuCDD3vxK3p2Hm4etyBvJC75kew0QapbU1UCgYBGLlW0GqRMtnD3a4DnAB5Q
xywV8Xv44A/TRSKF6LGQr5rETdevbxJSpOMldYvf7He3ccFa5ToeG4Rm6tlPNXxI
fUj9ktAOtpNbimYfoNNqELWTXxsrFUHgBMwQAwOVUpZgiYknjKXSh3587hws3Kib
FamzMMHoISuU58V2QoPfUQKBgH3d1Z6DB3hImEPsst4xyGMRdx6TVNpq2QifrQGo
NyQ3EaVKFQdFPyxU86lTUmVULn/27wgggEv200DPquuX8M4SE547wg8YKOLLimhv
FwI+eXOgNbAVvYVjf5/Xb98BkLetgDbxpqKZKfdsGBqtV4C+WyU3feAeOc8RI7dq
QDzxAoGAEF1LwoWPh94YVJs/f1Tjk3euX5YjXLj5StbsV2DOA9wtqL5DPrL9JmpY
gXsNl4AeeDwSlAkh8+KXKJ+AZVvGjQnIwU8jAvtee3cOYhvHUAXDB1b+yLe6Z2q4
knqPghny1B3tfhbT9ow4jtrlm8jiumhVwg44gQhmcSSiRCMBwfs=
-----END RSA PRIVATE KEY-----</code></pre>
I used some script found online to make the conversion. Loading it in Wireshark to decrypt the encrypted capture then directly gave the flag: <code>INS={HB_pr1v4te_key5_le3k}</code>

![wireshark](/resources/2016/insomnihack/pcapbleeding/wireshark.png)

