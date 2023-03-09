from fastecdsa.curve import secp256k1
from fastecdsa.keys import export_key, gen_keypair
import fastecdsa
from fastecdsa import curve, ecdsa, keys
from hashlib import sha256


'''
valid = fastecdsa.ecdsa.verify(sig: Tuple[rs, ], msg: MsgTypes, Q: fastecdsa.point.Point, 
curve: fastecdsa.curve.Curve = P256, hashfunc=<built-in function openssl_sha256>, 
prehashed: bool = False) 

valid = fastecdsa.ecdsa.verify(rs, m, public_key, secp256k1, hashfunc= sha256) 


'''

def sign(m):
    #generate public key
    #private_key, public_key = keys.gen_keypair(curve.secp256k1)
    
    private_key = keys.gen_private_key(curve.secp256k1)
    print('type(private_key', type(private_key))
    print('private key' , private_key)
    public_key = keys.get_public_key(private_key, curve.secp256k1)
    print('type(public_key', type(public_key))
    #public_key = point()
    #generate signature
    
    r = 0
    s = 0
    rs = []
    r, s = fastecdsa.ecdsa.sign(m, private_key,hashfunc= sha256, curve = secp256k1)
    print('r', r)
    print('s', s)
    
    rs.append(r)
    rs.append(s)
    
    valid = fastecdsa.ecdsa.verify(rs, m, public_key, secp256k1, hashfunc= sha256)
    #print(valid)
    
    return( public_key, [r,s] )
#m = input(' message ' )
#print(m)

#public_key, rs = sign(m)
#return(m)

