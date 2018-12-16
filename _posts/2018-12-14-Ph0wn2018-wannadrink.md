---
layout: post
title: "Ph0wn 2018 - Wanna drink? Move your arm!"
mathjax: true

date: 2018-12-14
---

*An ssh access to a Lego Mindstorms platforms: ev3dev is given to control three motors of a robot arm. The goal is to open the fridge door.*

<!--more-->

### Description

Ph0wn aliens have abducted my coke and put it in the fridge. But, now, I am thirsty. Open the door with the robotic arm, and you will get a free coke ... and a flag!

Fortunately, the aliens have left a few instructions in case they would format their internal memory.

You first must request access to the robot by giving your IP address, one team at a time. Then you can connect to the robot on ph0wn2018-robot with IP address 10.210.17.146

Once connected, you must make a program to move the arm and open the door. The door must rotate of 180 degrees to get the can. Knocking down the fridge is prohibited (you must get the can without destroying the fridge, you vandals!)

The flag is NOT in the robot system, it is printed on the coke can.

Oh, by the way, a very powerful lazer beam will strike your own computer if you were to erase to content of the system, or if you get the can without using the robotic arm.

Last but not least, they have noted the login/password on a post-it just next to the printed manual:

    Login: robot
    Password: maker

The flag has the usual format.

Author: ludoze

### Details

Points:      500 (intermediate)

### Solution

The robotic arm was made with Lego:

<img src="/resources/2018/ph0wn/wannadrink/robot.jpg" width="800">

When connecting to the server, we had few indication about the service used:

```
$ ssh robot@10.210.17.146
            _____     _
   _____   _|___ /  __| | _____   __
  / _ \ \ / / |_ \ / _` |/ _ \ \ / /
 |  __/\ V / ___) | (_| |  __/\ V /
  \___| \_/ |____/ \__,_|\___| \_/

Debian jessie on LEGO MINDSTORMS EV3!

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.
```

According to the [documentention](https://www.ev3dev.org/docs/tutorials/tacho-motors/), the motors are located in the */sys/class/tacho-motor/* folder. Three motors were present: *motor0*, *motor1* and *motor3*. It is possible to list all the available commands and parameters:

```
$ ls /sys/class/tacho-motor/motor0/
address        driver_name    polarity      ramp_up_sp  stop_action
command        duty_cycle     position      speed       stop_actions
commands       duty_cycle_sp  position_sp   speed_pid   subsystem
count_per_rot  hold_pid       power         speed_sp    time_sp
device         max_speed      ramp_down_sp  state       uevent

$ cat /sys/class/tacho-motor/motor0/commands 
run-forever run-to-abs-pos run-to-rel-pos run-timed run-direct stop reset
```

Basically we were interested by the speed and the movement of each motors. We were able to move them with the following commands:

```
$ export M3=/sys/class/tacho-motor/motor3
$ cat $M3/position_sp
0
$ cat $M3/speed_sp
500
$ echo 100 > $M3/speed_sp
$ echo 50 > $M3/position_sp
$ echo run-to-abs-pos > $M3/command
$ cat $M3/position_sp
50
```

After playing a bit with the tree motors, we were able to find that *motor0* controls angular movement, *motor1* vertical movements and *motor3* is the pinch.

Finally it was only a matter of time to find the proper sequence to open the fridge door and the flag was stick to the can inside:

<img src="/resources/2018/ph0wn/wannadrink/can.jpg" width="800">
