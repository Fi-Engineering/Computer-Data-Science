# -*- coding: utf-8 -*-
"""
Created on Wed May 12 07:26:44 2021

@author: Alex 

    Create a Caesar Cipher in Python. Use the template “caesar.py” provided.
    Your code should have two functions: encrypt(key,plaintext) and decrypt(key,ciphertext). 
    They should each take a key and a message. Assume the key is an integer and the message
        is a string with only characters from the 26 letters of the alphabet. 
    Assume the string is all in upper case.
    
    For example:
        encrypt(1,"BASE")
    should yield "CBTF" 
    
    def encrypt(key,plaintext):
        ciphertext=""
        #YOUR CODE HERE
        return ciphertext


    def decrypt(key,ciphertext):
        plaintext=""
       #YOUR CODE HERE
        return plaintext 


"""

def encrypt(key,plaintext):
    alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    #print('len(alpha:' , len(alpha))
    ciphertext = ''
    #ptLen = len(plaintext)
    for i in range(len(plaintext)):
        for j in range(len(alpha)):
            if(plaintext[i]==alpha[j]):
                #ciphertext.append(alpha[(j+key % 26)])
                ciphertext = ciphertext + alpha[((j+key)%26)]
    return ciphertext


def decrypt(key, ciphertext):
    alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    #print('len(alpha:' , len(alpha))
    plaintext = ''
    #ptLen = len(plaintext)
    for i in range(len(ciphertext)):
        for j in range(len(alpha)):
            if(ciphertext[i]==alpha[j]):
                if(j-key<0):
                     plaintext = plaintext + alpha[(26 + (j-key))%26]
                else:
                     plaintext = plaintext + alpha[(j-key)%26]
    return plaintext


'''
def main():
    print('\n\nCaesar Cipher in Python:\n\n')
    
    go = '3'
    while go=='3':
        print('Testing function encrypt():')
        key = int(input('Enter key, an integer >=0, <=26: '))
        plaintext = input('Enter plaintext string, all uppercase, all alpha: ')
        ciphertext = encrypt(key, plaintext)
        print('ciphertext is: ', ciphertext)
        print('\n')
        
        print('Testing function decrypt():')
        key = int(input('Enter key, an integer >=0, <=26: '))
        ciphertext= input('Enter ciphertext string, all uppercase, all alpha: ')
        plaintext = decrypt(key, ciphertext)
        print('plaintext is: ', plaintext)
        
        go = input('To run again enter 3: ')
    
    print('\n\nProcess terminated without exception.\n\n')
    
    
    
main()    

'''

