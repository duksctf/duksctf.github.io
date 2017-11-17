#!/usr/bin/env python3
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils

curve = ec.SECP256R1()
algo = ec.ECDSA(hashes.SHA256())

# we read the file as being an OpenSSH key and return it as a public key:
def readPubKey(filename):
    with open(filename, 'r') as f:
        data = f.read()
        return serialization.load_ssh_public_key(data,default_backend())

def testInt(inp):
    try:
        privateKey = ec.derive_private_key(
                inp, pubnum.curve,default_backend())
        if pubnum.public_numbers()==privateKey.public_key().public_numbers():
            return True, privateKey
        else:
            return False, None
    except:
        return False, None

pubnum=readPubKey("id_ecdsa.pub")
with open("allrng.txt","r") as f:
    for number in f.readlines():
        ok, priv = testInt(int(number.strip(),10))
        if ok:
            print 'Success, the secret int is:', number
            data = priv.private_bytes(encoding=serialization.Encoding.PEM,
                     format=serialization.PrivateFormat.TraditionalOpenSSL,
                     encryption_algorithm=serialization.NoEncryption())
            with open("id_ecdsa.priv","w") as f2:
                f2.write(data)
            print "Written to id_ecdsa.priv:","\n",data
            break
