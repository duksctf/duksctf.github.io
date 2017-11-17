def genRNG(x):
    p = 14219462995139870823732990991847116988782830807352488252401693038616204860083820490505711585808733926271164036927426970740721056798703931112968394409581
    g = 13281265858694166072477793650892572448879887611901579408464846556561213586303026512968250994625746699137042521035053480634512936761634852301612870164047
    keyLength = 32
    ret = 0
    ths = round((p-1)/2)
    for i in range(keyLength*8):
        x = pow(g,x,p)
        if x > ths:
            ret += 2**i
    return ret

values={0}
with open("subgroup.txt", "r") as f:
    for x in f.readlines():
        values.add( genRNG(int(x.strip(),10)) )

print "There are %d different values in this set." % len(values)

with open("allrng.txt","w") as f:
    for x in values:
        f.write("%d\n" % x)
    
