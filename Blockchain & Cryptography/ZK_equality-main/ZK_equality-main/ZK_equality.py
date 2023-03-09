from zksk import Secret, DLRep
from zksk import utils

def ZK_equality(G,H):

    #Generate two El-Gamal ciphertexts (C1,C2) and (D1,D2)

    #Generate a NIZK proving equality of the plaintexts
    
    #m = 117 # the message
    m = Secret(117)
    
    #m = Secret(utils.get_random_num(bits=128))
    
    #m = Secret() # from instructions?
    
   # m = 1
    
    r1 = Secret(utils.get_random_num(bits=128))
    
    #top_secret_bit = 1
    
    C1 = r1.value * G
    # A Pedersen commitment to the secret bit.
    C2 = r1.value * H + m.value * G  # error: only linear combinations of group elements are supported
    
    r2 = Secret(utils.get_random_num(bits=128))
    
    D1 = r2.value * G
    
    D2 = r2.value * H + m.value * G
      
    stmt = DLRep(C1, r1 * G) & DLRep(C2, r1*H+m*G) & DLRep(D1,r2*G) & DLRep(D2, r2*H+m*G)
    
    zk_proof = stmt.prove()

    #Return two ciphertexts and the proof
    return (C1,C2), (D1,D2), zk_proof


