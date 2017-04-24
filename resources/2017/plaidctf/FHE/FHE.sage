FLAG = "REDACTED"
P = 173679354585523418477187462024504455998034329173335339952282476171310698849633901515173353474480211201
F = GF(P)
N = 35

def random_vector(n):
    elems = [F.random_element() for _ in range(n)]
    return vector(elems)

class FHE(object):
    def __init__(self, n):
        self.n = n
        self.t = random_vector(n)

    def key(self):
        return self.t

    def encrypt(self, m):
        n = self.n
        t = self.t
        rows = [random_vector(n) for _ in range(n-1)]
        v = t[:-1] * matrix(rows)
        u = vector([t[-1]^(-1) * (m * t[i] - v[i]) for i in range(n)])
        rows.append(u)
        C = matrix(rows)
        return C

    def decrypt(self, C):
        t = self.t
        v = t * C
        m = v[0] * t[0]^(-1)
        return m

class Cipher(object):
    def __init__(self, n):
        self.fhe = FHE(n)

        self.x = F.random_element()

        g = F.multiplicative_generator()
        self.G = self.fhe.encrypt(g)
        self.H = self.G^(self.x)

        self.z = F.random_element()
        self.Z = self.fhe.encrypt(self.z)

    def pubkey(self):
        return (self.G, self.H, self.Z)

    def privkey(self):
        return self.x

    def encrypt(self, m):
        G = self.G
        H = self.H
        Z = self.Z

        M = self.fhe.encrypt(m)

        y = F.random_element()
        U = G^y
        S = H^y

        return (U, (M + Z) * S)

    def decrypt(self, (U, C)):
        u = self.fhe.decrypt(U)
        c = self.fhe.decrypt(C)
        x = self.x
        s = u^x
        m = c * s^(-1) - self.z
        return m

cipher = Cipher(N)
m = int(FLAG.encode('hex'), 16)
c = cipher.encrypt(m)

assert cipher.decrypt(c) == m

with open("pubkey", "w") as f:
    G, H, Z = cipher.pubkey()
    f.write(repr((G.rows(), H.rows(), Z.rows())))

with open("enc", "w") as f:
    U, C = c
    f.write(repr((U.rows(), C.rows())))
