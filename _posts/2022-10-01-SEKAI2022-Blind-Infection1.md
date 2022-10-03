---
layout: post
title: "SEKAI 2022 - Blind Infection 1"
mathjax: true

date: 2022-10-01
---

*A ransomware encrypted some text file, but the user has already used an online paste website to save it. Read the firefox profiles backuped by snap and find tin the history the url of the paste.*

<!--more-->

### Description

*Consider using a fresh virtual machine for this challenge, as you may risk losing your data. We are not responsible for any damages caused.

Customer: Please help me... I don’t know what I did but now I can’t access my personal files anymore!

Investigator: It looks like they were encrypted. Have you ever backed them up before?

Customer: Yes, I had some links, actually! But they were encrypted as well, so I’m not sure what to do now.

Attachment md5sum: 60937547d80207b1b4f2d4174a8d719a

Author: BattleMonger*

### Details

Points:      470

Category:    forensic

Validations: 23

### Solution

We were given a file called [chall.zip](/resources/2022/sekai/blind_infection_1/chall.zip).
After digging around the file and folder it stand out that the juicy stuf  resides inside the `/home/sekaictf/Documents` folder where a lot of encrypted txt file are.

Inside the description, the customer tell us that he had some "links" as a backup.
Using the `tree -a` command, a folder called `snap/firefox` has been found inside the home user folder.
Inside this directory the profile of the customer can be found `common/.mozilla/firefox/p3zapakd.default`. To analyze quickly the firefox profile, the [firefed](https://github.com/numirias/firefed) tool has been used.

```bash
> $ firefed -f -p home/sekaictf/snap/firefox/common/.mozilla/firefox/p3zapakd.default/ history | grep -i paste
https://paste.c-net.org/LovedCyborg
https://paste.c-net.org/DictateSplinter
https://paste.c-net.org/WagonsClips
https://paste.c-net.org/BegunCarols
https://paste.c-net.org/SweptReport
https://paste.c-net.org/DetectedParanoid
https://paste.c-net.org/RomanovBaptiste
https://paste.c-net.org/GluttonyBamboo
https://paste.c-net.org/HavingGaining
https://paste.c-net.org/ElevenRejected
...
```

Opening one of the link shows that there is corelation of the encrypted .txt file and the paste. One of the encrypted txt file was `flag.txt`, so we think that one of the paste should contain the flag.
We wrote simple [python script]()



We wrote a simple [python script](/resources/2022/sekai/blind_infection_1/find_paste.py) to extract the different paste and search for a flag.

After a while, the flag **SEKAI{R3m3b3r_k1Dz_@lway5_84cKUp}** poped out of my console.

It is fun because I was already working on the second party of the challenge and I had the first blood only on the 2nd part, but in fact I had the first flag before the team that validated it.


Challenges resources are available in the [resources
folder](https://github.com/duksctf/duksctf.github.io/tree/master/resources/2022/sekai/blind_infection_1)

