

import hashlib
import os
import re

'''
def proceed():
        import sys
        x = input('to continue enter 3: ')
        if(x == "3"):
            pass
        else:
            print('\nProcess terminated by user\n')
            sys.exit(0)
 '''

def hash_preimage(target_string):
    if not all( [x in '01' for x in target_string ] ):
        print( "Input should be a string of bits" )
        return
   
    xBin = 0
    lenTS = len(target_string)
    
    while xBin != target_string:
        
        x = str(os.urandom(42)).encode('utf-8')
       
        xHash = hashlib.sha256(x).hexdigest()
     
        xBinFull = bin(int(xHash, base=16))[2:]
       
        endNdx = len(xBinFull)
        startNdx = endNdx - lenTS
        xBinFull = str(xBinFull)
        
        xBin = xBinFull[startNdx:endNdx]
         

    nonce = x
    return( nonce )
'''

def main():
    print('\n\nA brute-force algorithm to find a partial preimage:\n\n')
    
    go = '3'
    while go=='3':
        print('Testing function hash_preimage():\n\n')
        
        STRING_TO_HASH = 'The quick brown fox jumps over the lazy dog.'
        HASH_OF_STRING = hashlib.sha256(STRING_TO_HASH.encode('utf-8')).hexdigest()
        print ("Hash of string: " + STRING_TO_HASH + " is " + str(HASH_OF_STRING))
        print('\n\n')
        
        targetString = ''
        stringOK = False;
        
        #if not re.search('[0-1]', targetString):
            #stringOK = False;    
        
        while not stringOK:
            targetString = input('Enter target string in bits (0s and 1s): ')
            print('targetString: ', targetString, '\n')
            if not isinstance(targetString, str):
                print('not parsed as string')
            
         
            stringOK = True;
            for i in range(len(targetString)):
               # print('targetString[i]: ', targetString[i])
               # if not isinstance(targetString[i], str):
               #     print('not parsed as string')
                
                if(targetString[i]=='0' or targetString[i]=='1'):
                #if(targetString[i]!='0'):  # this runs ok, so the logic above is wrong
                    
                    continue;
                    #print('inside if: ')
                   # print('targetString[i]: ', targetString[i])
                   # stringOK = False;
                   # print('stringOK: ', stringOK, '\n')   
                else:
                    stringOK = False;
                    print('target string must consist of only 0s and 1s')
            print('stringOK: ', stringOK, '\n')            
           
            
            
        print('\n')
        nonce = hash_preimage(targetString)
        
        print('nonce is: ', nonce)
        
        print('\n')
        
       
        
        go = input('To run again enter 3: ')
    
    print('\n\nProcess terminated without exception.\n\n')
    
    
    
main()    
'''
