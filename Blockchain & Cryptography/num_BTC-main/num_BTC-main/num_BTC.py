
'''
Calculating the number of circulating tokens at a given block height:

Bitcoin tokens are generated through block rewards. Initially, the block reward was 50 BTC,
and the reward halves every 210,000 blocks. Thus at Block 1 there were 50 BTC in circulation. 
At Block 2, there were 100 BTC etc.
Write a script called “num_BTC.py” that contains a function “num_BTC.” 
The function should take as input a block height (integer) and return the total 
number of tokens that have been mined so far (up to and including the given block). The 
returned value should be a float.
Note: your script should not need to interact with the blockchain.

'''

import math

def num_BTC(b):
    
    halfBlock = 210000
    
    initReward = 50
    

    """
    # option 1 from https://en.bitcoin.it/wiki/Controlled_supply
    denom = 10^8    
    
    numerator = 0
    
    for bit in range(b):
        numerator += halfBlock * ((initReward*denom)/(2^bit))
        print('num: ', numerator, '\n')
    
    c = float(numerator / denom)
    """
    # option 2 from https://docs.diadata.org/documentation/methodology/digital-assets/supplynumbers
    c = float(0)
    for bit in range(b):  
        #print('int(bit/halfBlock): ', int(bit/halfBlock))
        c += (initReward) / (2.0**math.floor((bit/halfBlock)))
        #print('c: ', c, '\n')
    
    #c = float(0)
    return c
'''
print('\n')
blockHeight = int(input('enter block height: '))
circTokens = num_BTC(blockHeight)
print('tokens in circulation at block height ', blockHeight, ' is: ', circTokens, '\n')
print('\n')
'''
