import random
import RNG

for _ in range(10):
    test = random.getrandbits(128)
    print RNG.genECDSAPriv(test)

