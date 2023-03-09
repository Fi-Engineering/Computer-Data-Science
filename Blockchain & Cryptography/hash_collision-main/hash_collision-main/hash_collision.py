
# -*- coding: utf-8 -*-
"""
Created on Fri May 14 08:59:25 2021

@author: Alex I

one:

 

Use a brute-force algorithm to find a partial collision.

Using the template “hash_collision.py” write a function called “hash_collision” 
     that takes a single input, k, where k is an integer. 
     The function “hash_collision” should return two variables, x and y,
     such that that the SHA256(x) and SHA256(y) match on their final k bits. 
     The return variables, x and y, should be encoded as bytes.

To encode a string as bytes:
    str = "Hello World"
    byte_str = str.encode('utf-8')

Your algorithm should be randomized, i.e., 
    hash_collision(k) should not always return the same colliding pair.

Hash_collion.py:

import hashlib

import os

def hash_collision(k):

    if not isinstance(k,int):
        print( "hash_collision expects an integer" )
        return( b'\x00',b'\x00' )
    if k
        print( "Specify a positive number of bits" )
        return( b'\x00',b'\x00' )

    #Collision finding code goes here



    x = b'\x00'
    y = b'\x00'
    return( x, y )


"""



import hashlib
import os


def hash_collision(k):
 
    #Collision finding code goes here:
        
    d = {}

    for _ in range(4200000): 
        # create random bytes
        x = str(os.urandom(42)).encode('utf-8')
        y = ""

        xHash = hashlib.sha256(x).hexdigest()
    
        xBin = bin(int(xHash, base=16))[2:]

        indx = xBin[-k:]
        eqls = 0

        if d.get(indx):
            y = d.get(indx)
            eqls = 1
            break
        else:
            d[indx] = x

        if eqls == 1:
            return x, y

    return x, y     
'''
def main():
    print('\n\nHash Collision in Python:\n\n')
    
    go = '3'
    while go=='3':
        print('Testing function hash_collisiont():')
        print('takes one int argument, returns two variables, x and y, encoded as bytes, ')
        print('such that the SHA256(x) and SHA256(y) match on their final k bits. ')
        ok = False;
        while not ok:
            
            try:
                k = int(input('Enter value for k; must be an int > 0: '))
                if(k>0):
                    ok = True;
            except:
                print('k must be an int! ')
        """    
        print('\n\ntest byte encoding: \n') 
        str = "Nobody inspects the Spammish Disposition"
        print('this string: ', str, ' byte encodes as: ')
        byte_str = str.encode('utf-8')
        print('byte_str: ', byte_str, '\n\n')
        """
        
        print('\n\n')
        x, y = hash_collision(k)

        print('x: ', x)
        #print('type(x): ', type(x))
        print('y: ', y) 
        #print('type(y): ', type(y))
        print('\n')
        
        
        
        go = input('To run again enter 3: ')
    
    print('\n\nProcess terminated without exception.\n\n')
    
    
main()    

'''


