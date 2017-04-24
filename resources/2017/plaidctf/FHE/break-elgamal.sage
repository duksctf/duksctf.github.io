from ast import literal_eval

P = 173679354585523418477187462024504455998034329173335339952282476171310698849633901515173353474480211201
F = GF(P)
N = 35

# Baby-step giant-step algorithm
def baby_step(g, h, n):
    m = ceil(sqrt(n))
    m2 = m / 2

    # We split into 2 halves because the full table does not fit in RAM...
    # Also, we start with the 2nd half, which contains the log we look for in the largest prime

    # 2nd half
    tbl = {}
    for j in range(m2, m):
        tbl[int(g**j)] = j
    a = g ** (-m)
    y = h
    for i in range(m):
        yy = int(y)
        if yy in tbl:
            return i*m + tbl[yy]
        y = y * a

    # 1st half
    tbl = {}
    for j in range(m2):
        tbl[int(g**j)] = j
    a = g ** (-m)
    y = h
    for i in range(m):
        yy = int(y)
        if yy in tbl:
            return i*m + tbl[yy]
        y = y * a

# Discrete logarithm in group of order p^e
def prime_power(g, h, p, e):
    x = 0
    gamma = g ** (p ** (e-1))
    for k in range(e):
        hi = ((g ** (-x)) * h) ** (p ** (e-1-k))
        d = baby_step(gamma, hi, p)
        x = x + d * (p ** k)
    return x

# Pohlig-Hellman algorithm in any group
def pohlig_hellman(g, h, n):
    fact = list(factor(n))
    print 'Factors of P-1:', fact
    a = []
    b = []
    for p, e in fact:
        print 'Solving log mod ' + str(p) + '^' + str(e)
        gi = g ** (n / (p ** e))
        hi = h ** (n / (p ** e))
        xi = prime_power(gi, hi, p, e)
        v = int(gi ** xi) % (p ** e)
        w = int(hi) % (p ** e)
        a.append(xi)
        b.append(p**e)
    return crt(a, b)

g = F(19)
h = F(52774084559796279986932845454574924346254819718383580319471373405857169799126978135712589651459738007)
z = F(74806619223436318057488019757923349388331709109526109048262015729998830471407099824963764117455225281)
u = F(161202540669710418030574172350388444507933259401173773637054984225018825685147997081838166382338594386)
c = F(99581767808000746292621272224666290248510197049015601126446298319169184317601777135057806610999909987)

x = pohlig_hellman(g, h, P-1)
print "x =", x
s = u ** x
m = c * s ** (-1) - z
#print m
hm = '{:x}'.format(int(m))
#print hm
flag = hm.decode('hex')
print flag

