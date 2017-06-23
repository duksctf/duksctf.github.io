#!/usr/bin/env python

import socket
import time
import binascii
from pyblake2 import blake2b

# Size of a permutation of sqares on Rubik's cube: 6 faces, each 3x3
N = 6*9


#################### NETWORK ####################
def recvuntil(s, until, maxlen=2048):
    buf = ''
    while until not in buf and len(buf) < maxlen:
        tmp = s.recv(1)
        if len(tmp) == 0:
            raise socket.error
        buf += tmp
    return buf

def recvline(s):
    line = recvuntil(s, '\n')
    print '-->', line.rstrip()
    return line.strip()

def sendprint(sock, line):
    print '<--', line
    sock.send(line + '\n')

# Read a cube for (a, b)
def getcube(sock, a, b):
    for i in range(6):
        recvline(sock)

    sendprint(sock, '1')
    recvline(sock)
    sendprint(sock, str(a))
    recvline(sock)
    sendprint(sock, str(b))
    recvline(sock)
    cube = recvline(sock)
    return cube

# Read cube for (a=i, 0) or (0, b=i)
def getcubeX(sock, letter, i):
    if letter == 'a':
        return getcube(sock, i, 0)
    else:
        return getcube(sock, 0, i)


#################### PERMUTATIONS ####################
# Compose two permutations
def permcompose(p, q):
    r = [0] * N
    for i in range(N):
        r[i] = p[q[i]]
    return r

# Invert a permutation
def invperm(perm):
    tmp = [-1] * N
    for i in range(N):
        tmp[perm[i]] = i
    return tmp

# Permute a string
def permstr(s, perm):
    l = list(s)
    tmp = [''] * N
    for i in range(N):
        tmp[perm[i]] = l[i]
    return ''.join(tmp)

# Get a permutation's order
def getorder(perm):
    tmp = [i for i in range(N)]
    order = 0
    while True:
        order += 1
        tmp = permcompose(perm, tmp)

        is_neutral = True
        for i in range(N):
            if tmp[i] != i:
                is_neutral = False
                break

        if is_neutral:
            return order


#################### CONVERT CUBE INTO PERMUTATION ####################
# Direct algorithm to extract a permutation from a cube
def cube2perm(zero, cube):
    # Indices of distinguished squares
    CENTERS = [
        4, # top
        22, 25, 28, 31, # sides
        49 # bottom
    ]
    SIDES = [
        (3,10), (7,13), (5,16), (1,19), # top
        (23,24), (26,27), (29,30), (32,21), # sides
        (34,48), (37,46), (40,50), (43,52) # bottom
    ]
    CORNERS = [
        (0,9,20), (6,11,12), (8,14,15), (2,17,18), # top
        (51,44,33), (45,35,36), (47,38,39), (53,41,42) # bottom
    ]

    perm = [0] * N

    for i in CENTERS:
        for a in CENTERS:
            if zero[i] == cube[a]:
                perm[i] = a
                break

    for i, j in SIDES:
        for a, b in SIDES:
            if sorted([zero[i], zero[j]]) == sorted([cube[a], cube[b]]):
                if zero[i] == cube[b]:
                    a, b = b, a
                perm[i] = a
                perm[j] = b
                break

    for i, j, k in CORNERS:
        for a, b, c in CORNERS:
            if sorted([zero[i], zero[j], zero[k]]) == sorted([cube[a], cube[b], cube[c]]):
                if zero[i] == cube[b]:
                    a, b = b, a
                elif zero[i] == cube[c]:
                    a, c = c, a
                if zero[j] == cube[c]:
                    b, c = c, b
                perm[i] = a
                perm[j] = b
                perm[k] = c
                break

    return perm

# Get permutation for a letter ('a' or 'b')
def solveperm(sock, letter, zero):
    newcube = getcubeX(sock, letter, 1)
    return cube2perm(zero, newcube)

#################### BABY-STEP GIANT-STEP ####################
def solvesk(zero, pk, perma, permb):
    ordera = getorder(perma)
    orderb = getorder(permb)

    # Compute orbit of perma
    ha = {zero: 0}
    s = zero
    for i in range(1, ordera):
        s = permstr(s, perma)
        ha[s] = i

    # Start from pk and iterate permb^-1
    invpermb = invperm(permb)
    s = pk
    for i in range(orderb):
        # A match was found
        if s in ha:
            return ha[s], i
        s = permstr(s, invpermb)

    return None

#################### EXTRACT THE FLAG ####################
def getflag(sock):
    user = 'test'

    # 6 lines of menu
    for i in range(6):
        recvline(sock)

    # Get zero cube (i.e. non-permuted)
    sendprint(sock, '1')
    recvline(sock)
    sendprint(sock, '0')
    recvline(sock)
    sendprint(sock, '0')
    recvline(sock)
    zero = recvline(sock)
    print "Zero cube:", zero

    # Solve permutations a and b
    perma = solveperm(sock, 'a', zero)
    print "Permutation a:", perma, "of order", getorder(perma)
    permb = solveperm(sock, 'b', zero)
    print "Permutation b:", permb, "of order", getorder(permb)

    # 6 lines of menu
    for i in range(6):
        recvline(sock)

    # Register a new user
    sendprint(sock, '2')
    recvline(sock)
    sendprint(sock, user)
    recvline(sock)
    sendprint(sock, zero)

    # 7 lines of menu
    for i in range(7):
        recvline(sock)

    # Login the new user
    sendprint(sock, '3')
    recvline(sock)
    sendprint(sock, user)
    recvline(sock)
    pk = recvline(sock)

    # 2 lines of information
    for i in range(2):
        recvline(sock)

    # Login challenge
    tmp = recvline(sock)
    challenge = tmp[26:26+16]
    print "Parsed challenge:", challenge
    salt = binascii.unhexlify(challenge)

    # Compute the handshake
    h = blake2b(key=salt, digest_size=16)
    h.update(pk)
    handshake = h.hexdigest()
    sendprint(sock, handshake)

    # 7 lines of menu
    for i in range(7):
        recvline(sock)

    # List users
    sendprint(sock, '4')

    # Extract admin pk from user list
    recvline(sock)
    for i in range(2):
        tmp = recvline(sock)
        tmpname = tmp[10:]

        tmp = recvline(sock)
        if tmpname == 'admin':
            adminpk = tmp[5:]
            print 'Admin pk:', adminpk

        recvline(sock)

    # 6 lines of menu
    for i in range(6):
        recvline(sock)

    # Login as admin
    sendprint(sock, '3')
    recvline(sock)
    sendprint(sock, 'admin')
    recvline(sock)
    pk = recvline(sock)

    # 2 lines of information
    for i in range(2):
        recvline(sock)

    # Login challenge
    tmp = recvline(sock)
    challenge = tmp[26:26+16]
    print "Parsed challenge:", challenge
    salt = binascii.unhexlify(challenge)

    # Extract challenger's sk
    sk = solvesk(zero, pk, perma, permb)
    a, b = sk
    print "Secret key for", pk, "is:", "(a=" + str(a) + ", b=" + str(b) + ")"

    # Extract permutation from admin's pk
    permadmin = cube2perm(zero, adminpk)
    print "Admin's permutation:", permadmin

    # Compute handshake cube
    cube = zero
    for i in range(a):
        cube = permstr(cube, perma)
    cube = permstr(cube, permadmin)
    for i in range(b):
        cube = permstr(cube, permb)

    print "Handshake cube:", cube

    # Compute the handshake
    h = blake2b(key=salt, digest_size=16)
    h.update(cube)
    handshake = h.hexdigest()
    sendprint(sock, handshake)

    # Get the flag \o/
    recvline(sock)
    tmp = recvline(sock)
    flag = tmp.split(' ')[-1]
    print "Flag:", flag


if __name__ == "__main__":
    # Create connection and discard first line of info
    sock = socket.socket()
    sock.connect(("rubik.ctfcompetition.com", 1337))
    recvline(sock)

    # Get the flag
    getflag(sock)

