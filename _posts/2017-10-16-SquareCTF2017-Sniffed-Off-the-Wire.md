---
layout: post
title: "SquareCTF 2017 - Sniffed Off the Wire"
date: 2017-10-16
---

*A sequence of command line escape codes is sent over the network and forms the flag if read with the tool more.*

<!--more-->

### Description

Sniffed Off the Wire

Sifting through the noise

After weeks of perching, our avian operatives captured a suspicious network flow. Maybe there's valuable data inside?

[sniffed-off-the-wire.pcap](/resources/2017/squarectf/sniffedoffthewire/sniffed-off-the-wire.pcap)

### Details

Points:      100

Category:    Forensics

### Solution

When opening the file of wireshark, there is a serie of TCP transactions which looks like:
```bash
[12;5HZ
[16;23HD
[8;2HK
...
```

It seemed to be command line [escape codes](https://en.wikipedia.org/wiki/ANSI_escape_code). We exported all the characters with `Analyze->Follow->TCP Stream` with the **Raw** option. Indeed the characters sent were escape codes and when the file was read with the tool `more` and enter key kept pressed, the flag appeared:

```bash
IYuFmcDBROZjVozrYVVQRtgNvHBWmFeeEDBiorENmcUxmTQdfxgzQgrdClphCYskIpdtedOsHQLOpam more tcp
m4ykYMarqwv(fl%)McnTNxCiOjOKxPOmzBYRGvlRFkPSwBotbbbOcIYSQmxGRKtDNMVpinMizKarbYC
--More--(48%)44N))dZYxKodcHdororUmLhAlXLCSFiMeohTRxVwQEaYbRPrsoMGgASTZuEbHfEDUw
[3;--More--(48%)jLzQSSkcyWVUwTtVbHOLzlJBmUPILSheSiGomiJIucZqWeertzbXwzGBmexAbK
W-MBre--(47%o46%)Q%skEZADAnOddgEHCXvvhBNlwuKTXDNlPQnNqestCVPuyYSNdoGSgTDXfHeVRk
N-More--(47%)-(46%)XpOmHrDCXmWEwpvDqWkhXdKHqeQZIfrZMIyubgPSgdstwOCIgSwEzhjJebDQ
I-More--(48%)%)EzpRLQsueNkCYXnaKCNTCoXBWiaIaLDyjmWASZlrUWcClyuQutWuRALyksZzgLKs
cNMore-H(46%)4UM)xQQnFAAbVGyOdWOoAXvjEkcHpEPHJHMVGQgDpRkHFawnuHaLZnBgHGxvIQVHNg
23;70Gzei-(47%)4N%yAxQhfZruoNVELeiZkpYEsXarLPJamLvrQhvPOSsmyjIxVYWRHcKvWVWnSAsT
53Hp;--More--(47%))PLeyhzxqOWttZFDpnwPhyqbXxgbFvhEcvpXWkzikIbRKEqRhSVaYGUhCenMR
Mj0F3A-YMorefX(D6t)WuvdvGVFMdNHyvvVzgKpByGSsqbkAkVBlZppUYlHiyJGnxdoyBsbcpkpEADv
jHfh;6--Morn--(45%)dHmYaRHKY                       RRuLZyetyQqloVMnYYgAwQZyhPpP
3HS4;4O-More--(46%)MkWjsmkaD  flag-IGxKMshp46TgD3  vBNgPhnRQTKZsYbctpvpfkMUVxQP
HnmEjeYbP3KoynWEuCszGPacXFLP                       AkrPKkWRQqDnoExocEOxjgbCylPx
e3FJF-poRe--D45%)%)oldAPXwDnYiRJenNFiXsRLmgWehDPmQaXYYlPbVrQOLIPMPFxapgbDDSNkUc
GP7RK-FoAeZQ(bB%aVfucraDIwjnZVgWvFSQaMKNqesroekRvYhEdpxIcYwKPLNIlLtaFwhKTjnDdzj
1Hg5;P--More--q46%tmxpwqfPudnZIjJjjJyvnVqlofmqHTXmHLQCFInVjLmwcxbbKCwSIKMUiRKuT
tzHa;-ZLXKe--oU2%zXawYSRNunhDHHiWLCKWKFsWVmblvJOUgoUSULCytCEEKsqkgQXKicWsEgURCI
NyHhQbQoexPtw3lEIevDxPhZRaviaWmbbXlBsVAkBWuhXUyLcpPPaShYABGnDgFpETBpnaKNcZotNqq
;13HB-More--(47%)VgkVEYdfXQyvCZYSEOVeaGibeBCNyeyOUjdHKXTzGqRGDMaDEvNBIsdTILFerS
;43HgMore--(j7%Ua%wsIJSAKpZrVBmSVPijTYLdcdwbnDQkPAtaZAdPuwMMtwBdAFsgxcQbVGKGaoo
sAVPcOqubjeDAvAqXggoehidBfAMxkHZAHyHAFZhGKlzcvJThTZzjrqsitdWLOTTKQDFfASweJbVyAz
17;12HLe--(48%)N)HmQPNXzMeKfDywrDPasgsNxaSEheppjvrwEzkWKmMnNVDsCBfwuHImAQjTDkJh
;xHmq-IorJk-(4J%mX)vqAvSdfBdSkyEDwKLQhPWLzLFoQxDOCemjTLTDedxoVUEodTituBAcjLgHGL
l-More--(45%)45%)%))
```
