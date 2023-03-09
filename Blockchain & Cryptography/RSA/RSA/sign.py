""
Using the FastECDSA library, modify the skeleton file “sign.py” and create a function, “sign,” that takes in a single message m, and, 
creates a new key-pair for an ECDSA signature scheme,
and signs the message m. Your function should return the ECDSA public key and the signature. 
Recall that an ECDSA signature consists of 2 integers, r,s. These should be returned as a list of length two.
Thus your function, “sign,” should return two elements, a public key and a list of length two 
that holds the two components of the signature.
When using the FastECDSA library, you need to specify the elliptic curve and the hash function. 
Your function should use the curve SECP256K1 (the “Bitcoin” curve) and the hash functions SHA256.
""
from fastecdsa.curve import secp256k1
from fastecdsa.keys import export_key, gen_keypair

from fastecdsa import curve, ecdsa, keys
from hashlib import sha256

def sign(m):
    #generate public key
    public_key = point()
    #generate signature
    r = 0
    s = 0
    return( public_key, [r,s] )

