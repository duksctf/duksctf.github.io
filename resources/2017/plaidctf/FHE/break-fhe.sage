from ast import literal_eval

P = 173679354585523418477187462024504455998034329173335339952282476171310698849633901515173353474480211201
F = GF(P)
N = 35

def fhe_decrypt(t, C):
    v = t * C
    m = v[0] * t[0]**(-1)
    return m

def break_fhe(M, title):
    # Known plaintext attack: FHE(x^(p-1)) = FHE(1)
    print 'Computing ' + title + '^(P-1)' + ' ...'
    MM = M ** (P-1)
    print 'Computed ' + title + '^(P-1)'
    # We recover the key by solving a linear system
    S = matrix.identity(N-1) - MM[:-1].transpose()[:-1]
    t = list(S.inverse() * MM[-1][:-1])
    t.append(1) # Last key element is always 1
    return vector(t)

def parse_files():
    # Parse public key file
    with open("pubkey", "r") as f:
        fG, fH, fZ = literal_eval(f.readline())
        G = matrix(F, fG)
        H = matrix(F, fH)
        Z = matrix(F, fZ)

    # Parse cipher text
    with open("enc", "r") as f:
        fU, fC = literal_eval(f.readline())
        U = matrix(F, fU)
        C = matrix(F, fC)

    return G, H, Z, U, C

# Get ciphertexts
G, H, Z, U, C = parse_files()

# Recover FHE secret key
t = break_fhe(Z, 'Z')

# Decrypt
g = fhe_decrypt(t, G)
h = fhe_decrypt(t, H)
z = fhe_decrypt(t, Z)
u = fhe_decrypt(t, U)
c = fhe_decrypt(t, C)

print '*' * 10 + ' Decrypted FHE ' + '*' * 10
print 'g =', g
print 'h =', h
print 'z =', z
print 'u =', u
print 'c =', c

