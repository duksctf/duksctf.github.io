F.<x> = PolynomialRing(GF(2))
def keygen():
    d1 = random_prime(3020, lbound=2000)
    d2 = random_prime(3020, lbound= 2000)
    p = F.irreducible_element(d1, "random") #irreducible element in GF(2)[x] of degree d1
    q = F.irreducible_element(d2, "random") #irreducible element in GF(2)[x] of degree d2
    n = p*q
    phi = (2**d1-1)*(2**d2-1)
    e = 65537
    while(gcd(e,phi) != 1):
        e = e+2
    d = inverse_mod(e,phi)
    return (d, e, n)
    

def toBits(pt):
    return ''.join('{0:08b}'.format(x, 'b') for x in bytearray(pt))

#Converts an array of bits into bytes
def bitsToBytes(bits):
    chars = []
    for b in range(len(bits) / 8):
        byte = bits[b*8:(b+1)*8]
        chars.append(bytes([int(b''.join(byte), 2)]))
    ret = b''.join(chars)
    return ret

#Encodes a polynomial into a bitstring
def polyToBits(pol):
    rb = [str(a).encode() for a in pol]
    while len(rb) % 8 != 0: #We want a multiple of 8 bits
        rb.append(b"0")
    rb.reverse() #We start with coefs of largest degree
    #At this point we have an array of bits representing the poly
    return bitsToBytes(rb)

#Encrypts the bitstring plaintext <pt> under key <e,n> where e is an integer and n a polynomial in GF(2)[x]
#The resulting ciphertext is also a bitstring
def encrypt(pt, e,  n):
    G.<y> = QuotientRing(F, F.ideal(n))#We need to take the result modulo n
    enc = toBits(pt)
    pt = 0
    for b in enc:
        pt = pt*y
        if b == "1" :
            pt = pt + 1
    return polyToBits(pt^e)



def toPolynomial(bytes):
    p = 0
    for b in toBits(bytes):
        p = p*x
        if b == "1" :
            p = p + 1
    return p

import base64

n = base64.b64decode(b"VEMzrwSqKHkgDJcR5NJwCT8gEwOi+4ncmtVjC6MIbG75Wnb3uaKUX1VGyzj+/FauKafYmJNN71xsI0upbU/mNaqNIqaaUC4ovhDARl1+U5/vX294W5bX/Lf7y6NqPYm0K4OlZMU6Swei970MBeRtW+WochEvKMQLedcXMyrmPWXhR5UOxSMM2IG5zO/GWFNDEawAZmx6cSUuIQulzmIhNW9UOXaI9janUgcnWqwz0XWVurjEcxWGqF0d/Sz6LeRvGQ8GdMT4Y+czzCn8A5UzKGULJUarIJpR49Z7Rwq1jsvhwggrZiuWRzz7TcUf6QrJrVAG9C/xcYLfH/TLGX15SZ8dmKSeK00KO18PDBTW/3QW8b8pTwRmYi7y/W9u6l5Tlq4tErB3SwDzaCGAEGj31fDi3mNFVi8WgaJ+xbw1JttKTTjCCdb5hVgdp/oZ0w6WUeuMQ5DqYcWLWlCZH2Td6pLFtYzBhtD9d33wtBh8Fprw8LlVtV4j2ThmNB9rmOuJlotyXGDnQgz67evlvNEsw6VBOpDX9TmxrIsnOTN8qvb+2/mHf+Ue34PhgwzPyPJYAJkkkua0Sa09Ib5f08kkvhzTLSMI8if5O+85GTVeeu0TjUeKg2B27j/5/GX7XEpEnLg/bbXioaMb1CjAQUsdkga6HyOqlIAMf2y2MyXhyeJxV/6UREV0U+JHuJQ/lEGUzWaiaoIrLdUDnlO7QDfCOK2K40vuQ78pAksn2W6EpbTm7SXytbILwZ/5QdaLf2Rkq2I4DxTawATFKYHkJoSRaY6IQBDvF1U2uRF8rlnozIEni/6FxqLA8w==")
ct = base64.b64decode(b"GvWl8yFZlAyJTvJqQ7SCoADYPnuhKKOmg2VRXwz0KkMqelFzn/WFV8HnyL5FhcrrJC2F3bt2IGAVr5DRZA0812I5+0pk94ANnKZcy4+PwSWbxdOV8h05W0qp99ZpygEU+0N9bdSR/XzxyF+Eb0l9iTlxCbT/yGnI+aZCgYz4LbgUatmUVx/HE2d3E05eZa8EC5gfdSmTy3rzE3MOb3FsS4Bs16EenTzWj/49vkQPUOIjP+iSavL6DIDLivoQolOtH5ensz5iRPOf/FNnVDc92vz5LCBnqyCGkq6kCmcB/Nv0PygougwCV20UkuMUkZn7/PyFks12rVpCXa24ORYGgIQry1kgrzkllPQSu/ilzxPASL7iIT0gcUVA33r8lAgwuRhvPpJTkOmzw4Oktf0MuSM5O/FUWXfJy6ccH0G8HWpsNCqDg3tdZl5weCdeQsb3TJkKXouUXjwDRL4lVxWTk0bG0Y0riQC5JqSq9gpixaXJ5gzAJ+pntSUD5ou3t+L1x1pMAmEk+B3H9VOLX3UHoKYJ/I61ta0sLwoJG+Kvo1yNpK67IUwHSYqo21ZK9HQYZ+cOKhrdYFUsu9MRYl7dx0uLp/V5lTEkK+8sKWuFpbgjDWiTVFBn6ONS9QiBEvP6pxfFvKOu22cgvlfHY0E5bV+6gau/drp/u3jysyms5oTOhmNX0aLoryykKcBOneYnFX+Oj8zR7Hs0EaaOaK1Tpq3eRC2rGTG7E6itGZVoy+EQQPqRvodU4CP/UFs/Nm3gqMZ4wGZoyM4m+lOXunIQP5Fb4CsgEJIuwNQb6IzSsIWTj0PLiJXykg==")
e = 65537

poly = toPolynomial(n)

# print(factor(poly))

d1 = 2689
d2 = 2237
phi = (2**d1-1)*(2**d2-1)

inv_e = inverse_mod(e,phi)

print(encrypt(ct, inv_e, poly))


ct = base64.b64decode(b"KWY2oNyBodbTRAqqFmGu5L2jOFqJKsuc7IH1bPOU8HWq9gRCGY2Dy2SsD9vL79ZAqbEua43WkzMlYgKfL5zkWHckDJ/dE/QhbIBNKEdAuWguEqi/eQUF/EEKbUsxVIjE7yu4skVA4+yQTGXOxrX5sThXhmBXC3A/PtdVa48tePnaZI7n4niZQqwRJoaew65qSgA91l231f5TXYYKKvl4q0XpHt4z2WOtYNpkm5kL7IR3VhkdbNDwospIwvMuyGeIGRMdrugh+GVXXh4+yNpi0QMUqjfUPG2zMLooFTa2Ap10+nBC+rlxmLd+OITa0cJclwYnWR+QEs6XLdo82HtFz7Gp2L8GHp3Qd3QPxyJArdGkbgZwKZm9gi3mB7EVQZYPG8vxK4yUQA+aDM/jBYYC/1Crfsbj27JRa5OagcoHcIS+RutTvlRLXIubXvRN9bgRTG2UThwmXb2aLKAJHPwTUDpX6OKF+34vymKGF+30sVq2w0V5dWP1cwBkDhurVzbywuMFay3NzP5Vki9gZ13/guPO0si2xTG6n9yDaHM7Gn7G8xDBOnn7KCFdgJZh/qDpKlgSWikL7+N+KxDUJnfNBcvu2XCx0SCwAcjrUSdw/MIWhWBiU5bFPCDFjzkiZ5p5B9XJDSyDmM2TvNuHcCKvg/okLuK5EXtWUMW30rxaBRAghqXwebtDeFzHcZcrN1qM82cPSJfvKxQ04EqbN2d46ziqO4D1vgP2Erm4TWwds4Y1fmJ/d4Xn+Qr6SABD6V2M+3oByxURdFBj82jUgt1hsnG7dRk0uR8c37PYEaflpsJb0vPr8RfnsDJbjqctAAram9QAiRTASty8ZQiz7i7B0RGLd7TEMAypFaEeak05jL0vR4+OTYOEr6ccO9gHllshXjs=")
n = base64.b64decode(b"TSlcr5GWVc/H61JvhVpI3JROn9gPdv30xG7JJNX71+yXqkKOl2v133SNYTjTeORr7K9V87r2fuzTBefbAFm9pLWkqj41w5Y06a7MmcdP2g8CMf08+2Xp+HYwqhFiznXM89f805UP4HrtEMaQaMZ4x9SylIIS6JnyecqAj7n1SW8yiSuhs0dh1886SWNUj8fMaSxBAeZ54KPdiuzn7qqTqD6/+1TNx/ASrD4hmXo1epO6IJckRYKSU3FYMO/HqHn6enL4v8p11p1Nja/QIJv3gl/a6pB8qn33U/fSgIcIH0+oXprjPL4hJ5j9g5pXrtgZfk9qE6m9pZ+J8DtwiFjTsBEJwLUMj2CNVPOyB04X5BrJZ0slEvNGNKDsjpF3Fx2JAhQmpruMF7ib8fEwEQDPbPkplp2w8oP9UDuBrDMUAGietxsjFr/5W3BGu6M1l+BU7hSgN4BALZCLTK0sPuTEun7y2d2mC21S8GswOY3m2A14S20ltK255Cch9hK3GwGoucf09gS4ZVeGaLqp99H24cbdFQcJ1uoVwaun5a/2pVttvGOQr6OKdbav8Q3EYdD7wgH9Jl9WPOkGCMUaoNnZziIqG2q9LalDLysqRwRFF0jlL7MlzLymf1gFb7IqynBNvFC7qffcq2bvXqEKiXjDHbGmnj9e6F8qLdrRNyqr8rBddc4LmFjunqkoPXYSBeEiEosG1fpH/az4wUDyIsVd7AEfMOXTMq+4gLTtQj3yQ2nQhtY0Y3KXeLhRzbnVh7iXQ3fFQtY+akQURlZV9fNqjDrO7aziUxmC7FGSazZhg1M6xapw8waOCJITcP31eVd4xmmDamR+N428wrfRyhrz5TuueeXuritgWLBmwGznWNbjDDm/ywRfTKdgI7pDxst+AO8=")

poly = toPolynomial(n)

# print(factor(poly))

d1 = 2917
d2 = 2473

phi = (2**d1-1)*(2**d2-1)

d = pow(2,(d1*d2-1), phi)

def encrypt(pt, n, x=2):
    G.<y> = QuotientRing(F, F.ideal(n)) #We will take our polynomials mod n
    enc = toBits(pt)
    pt = 0
    for b in enc:
        pt = pt*y
        if b == "1" :
            pt = pt + 1
    return polyToBits(pt**x)

# print(encrypt(ct, p, 2**(n_prime-1)))
print(encrypt(ct, poly, d))
