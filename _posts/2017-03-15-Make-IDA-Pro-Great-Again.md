---
layout: post
title: "Make IDA Pro Great Again"
date: 2017-03-15
---

*In this post I will explain a neat way to use our own python version with IDA
Pro, then how to use a chrooted Arch Linux 32bit to run IDA Pro in
order not to pollute our host with pesky lib32-XX packages and Finally I will
document installation and configuration of some useful IDA Pro plugins.*

<!--more-->

### Introduction

Why not using already available techniques such as [Arybo, using rpyc to tunnel rpc call to
64bit python](https://pythonhosted.org/arybo/integration.html) or [idalink](https://github.com/zardus/idalink) or [Installing PIP package, and using them from IDA on a 64-Bit machine](http://www.hexblog.com/?p=726) ?
The reason is simple. I don't want to pollute my host with a ton of annoying pip
package, lib32-xx and so on. I also want to use some cool IDA Pro plugins like
[keypatch](http://www.keystone-engine.org/keypatch/), [ipyida](https://github.com/eset/ipyida) and [idaemu](https://github.com/36hours/idaemu).

Note: This entire procedure was realized on an Arch Linux 64bit os. It could easily
be applied to Ubuntu or other distributions.

### Let's get our hands dirty !! 

#### Install and configure a chroot and schroot environment

##### Arch Linux 32 bit chroot

Lot of tricks has been taken from [ArchLinux Wiki](https://wiki.archlinux.org/index.php/Install_bundled_32-bit_system_in_64-bit_system).

###### Install a few utilities and schroot

``` bash
sudo  pacman -S arch-install-scripts schroot
mkdir /opt/arch32
```
###### Configure custom pacman.conf

If you are using [multilib](https://wiki.archlinux.org/index.php/multilib) you
need to remove it from your custom pacman.conf.

Configure a custom pacman.conf without multilib support:
Copy the default one and remove:

```
[Multilib]
Include = /etc/pacman.d/mirrorlist
```

###### Create the chrooted installation of Arch 32bit

Note: There are some packages that are not needed for a normal installation of IDA Pro without plugins. I found it faster to install them during the pacstrap rather than from the chroot.

``` bash
linux32 pacstrap -C path/to/pacman.conf -di /opt/arch32 base base-devel zlib libxext libxrender libsm libice glibc glib2 fontconfig freetype2 python2-keystone python2 python2-jupyter_client python2-ipykernel python2-ipython libxkbcommon-x11 libxkbcommon cmocka
```
###### Configure our newly created chroot for users/network

``` bash
sudo su
cd /etc
for i in passwd* shadow* group* sudoers resolv.conf localtime locale.gen vimrc inputrc profile.d/locale.sh; do cp -p /etc/"$i" /opt/arch32/etc/; done
```
###### Configure schroot

Add the chrooted env in /etc/schroot/schroot.conf 

```
[Arch32]
type=directory
profile=arch32
description=Arch32
directory=/opt/arch32
users=youruser
groups=users
root-groups=root
personality=linux32
aliases=32,default
```

###### Configure schroot to run properly with ipython and jupyter

Edit /etc/schroot/arch32/mount and add:

```
/run/user/1000 /run/user/1000  none    rw,bind         0       0
```

Configuration of schroot is done. We need to change some stuff in order to make IDA Pro works with our own python.

#### Configure X and IDA Pro in the chroot

##### X Stuff

###### Give access to your X for the chroot
``` bash
xhost +local:
```

###### Find the display ID of your current X session (keep it for later)
``` bash
echo $DISPLAY
```

##### Configure IDA pro to use our own version of python

###### Enter the chroot
``` bash
sudo linux32 arch-chroot /opt/arch32
```

###### Change terminal in order to have proper auto-completion
``` bash
export TERM=xterm
```

###### OPTIONAL - Add some fonts to the chroot in order to shows properly the IDA Pro GUI:

If you are like me and you like to change your font in your X, don't forget to install it in the chroot in order to prevent having weird characters in IDA Pro.

``` bash
pacman -S adobe-source-code-pro-fonts xorg-fonts-type1 ttf-dejavu artwiz-fonts font-bh-ttf \
		  font-bitstream-speedo gsfonts sdl_ttf ttf-bitstream-vera \
		  ttf-cheapskate ttf-liberation \
		  ttf-freefont ttf-arphic-uming ttf-baekmuk
```

###### Configure your chroot to use the Xserver of your host
``` bash
export DISPLAY=:0 
```
Where 0 is the ID of your display as retrived earlier.
 
###### Install IDA Pro

Run the IDA Pro installer. When installing IDA don't forget choosing "no" when the installer asks to install the bundled version of python.

###### Configure IDA pro to use our own python
``` bash
cd /opt/ida-6.95/python/lib
rm python27.zip
mv python2.7 python_old
ln -s /usr/lib/python2.7 .
mv "python_old/lib-dynload/ida_*" /usr/lib/python2.7/lib-dynload
rm -r python_old
```

###### Exit from the chroot, very important
``` bash
exit
```

<strong style="color: red;">WARNING - Don't run schroot when chrooting with linux32, always leave the chroot with exit before schrooting.</strong>

<strong style="color: red;">WARNING - Rename your ~/.idapro and remove all plugins before launching IDA Pro for the first time.</strong>

###### Use schroot to launch our fully chrooted IDA (with access to the host home directory of the user in the schroot.conf)
``` bash
schroot -p /opt/ida-6.95/idaq
```

#### BONUS - Install and configure useful plugins for IDA pro

I'm a big fan of [IPython](https://ipython.org/) for auto-completion and rapid scripting of python snippets. I often patch binaries, but the patching function in IDA Pro is incomplete.
I like to use [unicorn-engine](http://www.unicorn-engine.org/) to emulate weird code as well.

##### Install, configure and patch ipyida

When I was using IDA Pro under Windows, one of my favorite plugin was [ida_ipython](https://github.com/james91b/ida_ipython). Unfortunately this plugin is Windows only. [Marc-Etienne](https://github.com/marc-etienne) from ESET developped a similar [plugin](https://github.com/marc-etienne) but this time available on Windows, Linux and Mac OSX.

###### Installation of ipyida

``` bash
cd ~/.idapro
cd plugins
git clone https://github.com/eset/ipyida.git
mv ipyida ipyida_temp
```

###### Monkey patching to remove Qt dependencies and use ipykernel rather than old IPython

``` bash
cd ipyida_temp
wget https://github.com/duksctf/duksctf.github.io/tree/master/resources/2017/ida/ipyida.patch
patch -p1 < ipyida.patch
```

###### Install it

``` bash
mv ipyida ipyida_temp/ipyida_plugin_stub.py ~/.idapro/plugins
mv ipyida ipyida_temp/ipyida ~/.idapro/plugins
```

##### Install keypatch in order to patch binaries, using assembly language
``` bash
wget https://raw.githubusercontent.com/keystone-engine/keypatch/master/keypatch.py
```

Note - Keypatch needs keystone (installed during the pacstrap).

##### Install Unicorn-Engine with the idaemu script to emulate things

###### Back in our chroot to install and configure Unicorn-Engine

<strong style="color: red;">WARNING - Don't chroot with linux32 if IDA Pro is running in the schroot, quit IDA Pro first.</strong>

``` bash
sudo linux32 arch-chroot arch_32_chroot
cd /root
mkdir build
```

###### Little trick to be able to run makepkg as root (normally not allowed):

[Makepkg](https://wiki.archlinux.org/index.php/makepkg) cannot be run as root for security reasons.
Here is a little trick to be able to package as root.

``` bash
chgrp nobody /root/build
chmod g+ws /root/build
setfacl -m u::rwx,g::rwx /root/build
setfacl -d --set u::rwx,g::rwx,o::- /root/build
```

###### Create unicorn-engine package
``` bash
git clone https://aur.archlinux.org/unicorn-git.git
cd unicorn-git
sudo -u nobody makepkg
```

###### Install it
``` bash
pacman -U unicorn-xxx.pkg.tar.xz
pacman -U python2-unicorn-xxx.pkg.tar.xz
```

###### Fix weird issue on unicorn egg file

``` bash
chown -R mofo:mofo /usr/lib/python2.7
```
PS: I know it's hacky, but it's a chroot so who cares...

###### Quit the chroot

``` bash
exit
```

##### Install idaemu plugins to use unicorn in IDA Pro

``` bash
wget https://raw.githubusercontent.com/36hours/idaemu/master/idaemu.py
```

#### BONUS2 - Adding our coloring theme to the chrooted IDA Pro 

I like to use the [consonance color theme](https://github.com/eugeii/ida-consonance) for my IDA Pro.
If you already applied a theme on your host, just copy the /opt/ida-xx/idacolor.cf to the /opt/ida-xx on your chroot.

### Wrap up and short demo

It took me a lot of research, for example trying to compile QT/PyQt is a lot of pain. I ended it up just removing the dependencies from the ipyida plugin.

Here is a little video of the ipyida plugin:

<img src="/resources/2017/ida/demo.gif" >

All the resources for this post are available [here](https://github.com/duksctf/duksctf.github.io/tree/master/resources/2017/ida).
                                                                            
I would like to thank [sh4ka](https://twitter.com/andremoulu) and [kamino](https://twitter.com/_kamino_) for tollerating me raging on this f****** Qt/PyQt nightmWare, while helping me on some python stuff and providing useful links.

If you have questions I'm available on IRC @freenode and on twitter [@dummys1337](https://twitter.com/dummys1337).
