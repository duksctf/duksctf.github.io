import sys
import struct

CODE_ENTRY_COUNT = 0x77
SIZEOF_ENTRY = 0x10
SIZEOF_DWORD = 4
SIZEOF_WORD = 2
NUM_REGS = 26
CODE_RETURN = CODE_ENTRY_COUNT
TOTAL_SIZE = CODE_ENTRY_COUNT*SIZEOF_ENTRY

maxlvl = 10000
code = open("./code").read()[4:]
assert(len(code) == TOTAL_SIZE)

class Entry(object): pass

def log(lvl, s):
    if lvl <= maxlvl:
        sys.stdout.write(s)

def intofsize(buff, off, size, frmt):
    assert(off >= 0 and off <= (SIZEOF_ENTRY-size))
    return struct.unpack(frmt, buff[off:off+size])[0]

def dword(buff, off):
    return intofsize(buff, off, SIZEOF_DWORD, "<I")

def word(buff, off):
    return intofsize(buff, off, SIZEOF_WORD, "<H")

def fetch(off):
    assert(off <= (TOTAL_SIZE-SIZEOF_ENTRY))
    buff = code[(off):(off+SIZEOF_ENTRY)]
    e = Entry()
    e.type = word(buff, 0)
    if e.type == 0:
        e.reg = word(buff, 4)
        e.next = dword(buff, 8)
    elif e.type == 1:
        e.reg = word(buff, 4)
        e.next1 = dword(buff, 8)
        e.next2 = dword(buff, 12)
    elif e.type == 2:
        e.nret = word(buff, 4)
        e.call = dword(buff, 8)
        e.next = dword(buff, 12)
    return e


def pc2off(pc):
    assert(pc < CODE_ENTRY_COUNT)
    return pc*SIZEOF_ENTRY


def exec_code(pc, regs, lvl=0):
    regs += [0] * (NUM_REGS - len(regs)) # init missing registers to 0

    while pc != CODE_RETURN:
        log(lvl, "[R0:%04x][R1:%04x][R2:%04x][R3:%04x][R4:%04x] " % (regs[0],regs[1],regs[2],regs[3],regs[4]))
        log(lvl, "%s[PC:%04x]" % ("  "*lvl,pc))

        entry = fetch(pc2off(pc))

        log(lvl, "[TYPE:%04x]" % (entry.type))

        if entry.type == 0:
            log(lvl, "[REG:%04x][NEX:%08x][UNU:........]\n" % (entry.reg, entry.next))

            regs[ entry.reg ] += 1
            pc = entry.next

        elif entry.type == 1:
            log(lvl, "[REG:%04x][NX1:%08x][NX2:%08x]\n" % (entry.reg, entry.next1, entry.next2))

            if regs[ entry.reg ] > 0:
                regs[ entry.reg ] -= 1
                pc = entry.next1
            else:
                pc = entry.next2

        elif entry.type == 2:
            log(lvl, "[NRT:%04x][CAL:%08x][NEX:%08x]\n" % (entry.nret, entry.call, entry.next))

            new_regs = exec_code(entry.call, regs[:], lvl+1) # pass regs by value, not ref
            regs = new_regs[:entry.nret] + regs[entry.nret:]
            pc = entry.next

        else:
            raise "Invalid entry <pc:%u> <entry:%s>" % (pc, entry)

    return regs


regs = [0] * NUM_REGS
main = 0


f14 = 0x14
"""
=> SUM_1D, SEE ALGO

In [32]: regs = [0]*NUM_REGS; regs[1] = 10; exec_code(f14, regs)
Out[32]: [0x43 (67), ...]
In [38]: sum([res1d[i] for i in xrange(10+1)])
Out[38]: 0x43 (67)

In [46]: res14 = {}
In [47]: for i in xrange(30): regs = [0]*NUM_REGS; regs[1] = i; regs = exec_code(f14, regs); res14[i] = regs[0]

In [48]: verif14 = {}
In [49]: for x in xrange(30): verif14[x] = sum([res1d[i] for i in xrange(x+1)])

In [61]: res14 == verif14
Out[61]: True
"""

f1d = 0x1d
"""
=> COUNT_2D(R1), SEE ALGO

In [19]: for i in xrange(50): regs = [0]*NUM_REGS; regs[1] = i; regs = exec_code(f1d, regs); res[i] = regs[0]
In [20]: res
Out[20]:
{0x0 (0): 0x0 (0),
 0x1 (1): 0x0 (0),
 0x2 (2): 0x1 (1),
 0x3 (3): 0x7 (7),
 0x4 (4): 0x2 (2),
 0x5 (5): 0x5 (5),
 0x6 (6): 0x8 (8),
 0x7 (7): 0x10 (16),
 0x8 (8): 0x3 (3),
 0x9 (9): 0x13 (19),
 0xa (10): 0x6 (6),
 0xb (11): 0xe (14),
 0xc (12): 0x9 (9),
 0xd (13): 0x9 (9),
 0xe (14): 0x11 (17),
 0xf (15): 0x11 (17),
 0x10 (16): 0x4 (4),
 0x11 (17): 0xc (12),
 0x12 (18): 0x14 (20),
 0x13 (19): 0x14 (20),
 0x14 (20): 0x7 (7),
 0x15 (21): 0x7 (7),
 0x16 (22): 0xf (15),
 0x17 (23): 0xf (15),
 0x18 (24): 0xa (10),
 0x19 (25): 0x17 (23),
 0x1a (26): 0xa (10),
 0x1b (27): 0x6f (111),
 0x1c (28): 0x12 (18),
 0x1d (29): 0x12 (18),
 0x1e (30): 0x12 (18),
 0x1f (31): 0x6a (106),
 0x20 (32): 0x5 (5),
 0x21 (33): 0x1a (26),
 0x22 (34): 0xd (13),
 0x23 (35): 0xd (13),
 0x24 (36): 0x15 (21),
 0x25 (37): 0x15 (21),
 0x26 (38): 0x15 (21),
 0x27 (39): 0x22 (34),
 0x28 (40): 0x8 (8),
 0x29 (41): 0x6d (109),
 0x2a (42): 0x8 (8),
 0x2b (43): 0x1d (29),
 0x2c (44): 0x10 (16),
 0x2d (45): 0x10 (16),
 0x2e (46): 0x10 (16),
 0x2f (47): 0x68 (104),
 0x30 (48): 0xb (11),
 0x31 (49): 0x18 (24)}

In [21]: def verif1d(x):
    ...:     count = 0
    ...:     while x >= 2:
    ...:         x = (x/2) if x%2==0 else (x*3 + 1)
    ...:         count += 1
    ...:     return count
    ...:
In [22]: verif = {}
In [23]: for i in xrange(50): verif[i] = verif1d(i)
In [24]: verif == res
Out[24]: True
"""

f2d = 0x2d
"""
=> RET_DIV2_OR_MUL(R1), RETURN (R1/2) if R1 is pair else RETURN (R1*3 + 1)

In [14]: for i in xrange(100): regs = [0]*NUM_REGS; regs[1] = i; regs = exec_code(f2d, regs); res[i] = regs[0]
"""

f40 = 0x40
"""
TODO

In [6]: regs = [0]*NUM_REGS; regs[1] = 10; regs[2] = 100; regs[0] = exec_code(f40, regs[:])[0]; regs
Out[6]: [0x37 (55), ...]

In [7]: def verif40(x,y):
   ...:     if x==0: return 0
   ...:     elif x==1: return 1
   ...:     else: return ((verif40(x-1,y) + verif40(x-2, y)) % y)

In [8]: verif40(10,100)
Out[8]: 0x37 (55)

In [9]: verif40(10,50)
Out[9]: 0x5 (5)

In [10]: regs = [0]*NUM_REGS; regs[1] = 10; regs[2] = 50; regs[0] = exec_code(f40, regs[:])[0]; regs
Out[10]: [0x5 (5), ...]

In [31]: [verif40(x,100000000000) for x in xrange(30)]
Out[31]:
[0x0 (0),
 0x1 (1),
 0x1 (1),
 0x2 (2),
 0x3 (3),
 0x5 (5),
 0x8 (8),
 0xd (13),
 0x15 (21),
 0x22 (34),
 0x37 (55),
 0x59 (89),
 0x90 (144),
 0xe9 (233),
 0x179 (377),
 0x262 (610),
 0x3db (987),
 0x63d (1597),
 0xa18 (2584),
 0x1055 (4181),
 0x1a6d (6765),
 0x2ac2 (10946),
 0x452f (17711),
 0x6ff1 (28657),
 0xb520 (46368),
 0x12511 (75025),
 0x1da31 (121393),
 0x2ff42 (196418),
 0x4d973 (317811),
 0x7d8b5 (514229)]
"""

f54 = 0x54
"""
=> RET_R1(R1), RETURN R1 AS R0

In [9]: regs = [0]*NUM_REGS; regs[1] = 1337; exec_code(f54, regs)
Out[9]: [0x539 (1337), 0x0 (0), ... ]
"""

f5c = 0x5c
"""
=> DIV_BY_2(R2), QUOTIENT in R0, REST in R1

In [10]: regs = [0]*NUM_REGS; regs[2] = 1337; exec_code(f5c, regs)
Out[11]: [0x29c (668), 0x1 (1), ...]
In [12]: 1337 == 668*2 + 1
Out[12]: True

In [9]: regs = [0]*NUM_REGS; regs[2] = 44; exec_code(f5c, regs)
Out[9]: [0x16 (22), ...]
"""

f63 = 0x63
"""
=> R1_MOD_R2(R1,R1), RETURN (R1 % R2)

In [30]: regs = [0]*NUM_REGS; regs[1] = 12345; regs[2] = 654; exec_code(f63, regs)
Out[30]: [0x23d (573), ...]
In [31]: 12345 % 654 == 573
Out[31]: True
"""

f6c = 0x6c
"""
=> R1_LT_R2(R1,R2), RETURN (R1 < R2)
In [20]: regs = [0]* NUM_REGS; regs[1] = 4; regs[2] = 12; exec_code(f6c, regs)
Out[20]: [0x1 (1), ...]

In [21]: regs = [0]* NUM_REGS; regs[1] = 40; regs[2] = 12; exec_code(f6c, regs)
Out[21]: [0x0 (0), ...]

In [22]: regs = [0]* NUM_REGS; regs[1] = 123; regs[2] = 123; exec_code(f6c, regs)
Out[22]: [0x0 (0), ...]
"""

f71 = 0x71
"""
=> R1_SUB_R2, RETURN MAX(0, R2-R1)

In [45]: regs = [0]*NUM_REGS; regs[1] = 1234; regs[2] = 654; exec_code(f71, regs)
Out[45]: [0x244 (580), ...]
In [46]: 1234 - 654 == 580
Out[46]: True

In [48]: regs = [0]*NUM_REGS; regs[1] = 1; regs[2] = 12; exec_code(f71, regs)
Out[48]: [0x0 (0), ...]
"""
