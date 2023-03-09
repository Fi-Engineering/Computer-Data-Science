import random
from params import p
from params import g


def keygen():
    #p = 2357
    #g = 2
    a = random.randint(1, p-1)
    #a = 1751
    print('a: ', a, '\n')
    sk = a
    h= pow(g,sk,p)
    pk = h
    print('pk: ', pk, '\n')
    return pk, sk




def encrypt(pk,m):
    #p = 2357
    #g = 2
    r = random.randint(1, p-1) # should be q, but q is unknown
    #r = 1520
    c1 = pow(g,r,p)
    c2 = m *pow(pk,r,p) % p
    return [c1,c2]

def decrypt(sk, c):
    #p = 2357 
    #gamma = (pow(c[0],(p-1-sk), p))  #This one
    #gamma =  c[0]**(p-1-sk) % p
    #m = gamma *c[1] % p  
    #nsk = (pow(c[0],sk)) 
    #print(nsk)
    m = c[1] * (pow(c[0],-sk, p)) % p
    
    return m
   
    
'''
def main():
    
    print('\n\nEl-Gamal\n\n')
    print('check imported parameters p, g: ')
    #print('p: ', p, '\n')
    #print('g: ', g, '\n')
    
    print('\nkey gen: ')
    pk, sk = keygen()
    print('pk: ', pk)
    print('sk: ', sk, '\n')
    
    
    print('\nencrypt: ')
    m = int(input('input m, where m is int < p: ')) #HACM = 2035
    print('\n')
    
    c = encrypt(pk, m)
    
    print('c1: ', c[0])
    print('c2: ', c[1])
    print('\n')
    
    print('\ndecrypt m encrypted from prior function call: ')
    #y = exp_by_squaring_iterative(c[0], sk)
    #print('y: ', y, '\n')
    
    m = decrypt(sk, c)
    print('m: ', m)
    #print('type(m): ', type(m))
    print('\n')
    
    print('\n\nProcess terminated without exception.\n\n')

main()
'''
