'''
In this homework you are asked to write a very simple blockchain.
 At its core, the blockchain is implemented as a linked list. 
 Each block, as can be seen in the Block class we’ve defined for you, 
 includes an index, a timestamp, a content and the hash of the previous block.
The class defines the genesis block.

# CR comment re line 6: really? Looks like an independent function to me

In the file linked_list.py, you need to define a function that generates the next blocks
 where the index of each block is the index of the previous block plus one, 
 the timestamp is the current time, and the content is a string “this is block i” 
 where i is the index of the block. You then need to append 5 blocks to your blockchain.

'''

import hashlib

import random

class Block:
    def __init__(self, index, timestamp, content, previous_hash):
      self.index = index
      self.timestamp = timestamp
      self.content = content
      self.previous_hash = previous_hash
      self.hash = self.calc_hash()
   
    def calc_hash(self):
      sha = hashlib.sha256()
      sha.update(str(self.index).encode('utf-8') + 
                 str(self.timestamp).encode('utf-8') + 
                 str(self.content).encode('utf-8') + 
                 str(self.previous_hash).encode('utf-8'))
      return sha.hexdigest()
      
M4BlockChain = []

from datetime import datetime
def create_genesis_block():
    return Block(0, datetime.now(), "Genesis Block", "0")

# cx to starter code appears to be necessary: 
lastBlock = create_genesis_block()
M4BlockChain.append(lastBlock)


block_list = []

block_list.append(lastBlock)

def next_block(last_block):
       
    content = "this is block " + str(last_block.index+1)
    return Block(last_block.index+1, datetime.now(), content, last_block.hash)


numNewBlocks = 5

    
# append 5 blocks to the blockchain
def app_five(block_list):

# loop to create numNewBlocks new blocks:
    #print('display results as calculated: ')
    lastBlock = block_list[0]
    for i in range(numNewBlocks):
        nextBlock = next_block(lastBlock)
        block_list.append(nextBlock)
        lastBlock = nextBlock
    for i in range(numNewBlocks+1):
        print(block_list[i].content)    
        #print(M4BlockChain[i]) # result = None
        
app_five(block_list)
