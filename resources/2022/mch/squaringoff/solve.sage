from Crypto.Util.number import  long_to_bytes

n = 0xfffffffe00000002fffffffe0000000100000001fffffffe00000001fffffffe00000001fffffffefffffffffffffffffffffffe000000000000000000000001
p = 115792089210356248762697446949407573530086143415290314195533631308867097853951
h = 4275333096397007849067777941008675457617279615546105194323216811550797075772016607215703868747693795339025886078058526791464546941731743196384839138407576

factors_n = [
 (2, 1),
 (3, 1),
 (5, 2),
 (17, 1),
 (257, 1),
 (641, 1),
 (1531, 1),
 (65537, 1),
 (490463, 1),
 (6700417, 1),
 (835945042244614951780389953367877943453916927241, 1),
 (p, 1)]

print(prod([p^e for (p,e) in factors_n]) == p*(p-1))

factors_str = "[3, 1; 5, 2; 17, 1; 257, 1; 641, 1; 1531, 1; 65537, 1; 490463, 1; 6700417, 1; 835945042244614951780389953367877943453916927241, 1; 115792089210356248762697446949407573530086143415290314195533631308867097853951, 1]"
factors_ord = [(3, 1),( 5, 2),( 17, 1),( 257, 1),( 641, 1),( 1531, 1),( 65537, 1),( 490463, 1),( 6700417, 1),( 835945042244614951780389953367877943453916927241, 1),(115792089210356248762697446949407573530086143415290314195533631308867097853951, 1)]
G = Zmod(n)
ord = G(h).multiplicative_order()

print(prod([p^e for (p,e) in factors_ord]) == ord)

# Discrete logarithm in Zp
c = h % n
a = int(pow(c,p-1,n)-1) // p
b = int(pow(2,p-1,n)-1) // p
x = (a*inverse_mod(b,p)) % p

print(long_to_bytes(x))
print(pow(2,x*(p-1),n) == pow(h,(p-1),n))

def pohligHellmanPGH(p,g,h):
  #g must be small
    F=IntegerModRing(p)
    g=F(2)
    h=F(h)
    G=[]
    H=[]
    X=[]
    c=[]
    N=factors_ord
    for i in range(0,len(N)-2):
        G.append(g^((p-1)/(N[i][0]^N[i][1])))
        H.append(h^((p-1)/(N[i][0]^N[i][1])))
        X.append(log(H[i],G[i]))
        c.append((X[i],(N[i][0]^N[i][1])))
        
    #print("G=",G,"\n","H=",H,"\n","X=",X)
    c.append((x,(N[len(N)-1][0]^N[len(N)-1][1])))

	#Using Chinese Remainder
    c.reverse()

    for i in range(len(c)):
        if len(c) < 2:
            break
        t1=c.pop()
        t2=c.pop()
        r=crt(t1[0],t2[0],t1[1],t2[1])
        m=t1[1]*t2[1]
        c.append((r,m))

    return c[0]

x2 = pohligHellmanPGH(n,2,h)
x2 = x2[0] % (ord//factors_n[-2][0])

print(long_to_bytes(x2))