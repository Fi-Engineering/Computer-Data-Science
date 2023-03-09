from web3 import Web3
from hexbytes import HexBytes

IP_ADDR='18.188.235.196'
PORT='8545'


w3 = Web3(Web3.HTTPProvider('http://' + IP_ADDR + ':' + PORT))

#if w3.isConnected():
#    print( "Connected to Ethereum node" )
#else:
#    print( "Failed to connect to Ethereum node!" )

def get_transaction(tx):
    tx = {}   
    #tx = w3.eth.get_transaction(tx)
    return tx

# Return the gas price used by a particular transaction,
#   tx is the transaction
def get_gas_price(tx):
    transaction = w3.eth.get_transaction(tx)
    gas_price = transaction['gasPrice']
    return gas_price

def get_gas(tx):
    tx_receipt = w3.eth.get_transaction_receipt(tx)
    gas = tx_receipt['gasUsed']
    return gas

def get_transaction_cost(tx):
    tx_cost = get_gas_price(tx) * get_gas(tx)
    return tx_cost

def get_block_cost(block_num):
    block_cost = 0
    block = w3.eth.get_block(block_num)

    transactions = block['transactions']

    for transact in transactions:
        block_cost += get_transaction_cost(transact)
    return block_cost

# Return the hash of the most expensive transaction
def get_most_expensive_transaction(block_num):
    max_tx = HexBytes('0xf7f4905225c0fde293e2fd3476e97a9c878649dd96eb02c86b86be5b92d826b6') 

    block  = w3.eth.get_block(block_num)
    transactions = block['transactions']

    for transact in transactions:
        currentTxCost = get_transaction_cost(transact)
        if currentTxCost > get_transaction_cost(max_tx):
            max_tx = HexBytes(transact)
    return max_tx


#tx = w3.eth.get_transaction('0xb5c8bd9430b6cc87a0e2fe110ece6bf527fa4f170a4bc8cd032f768fc5219838')

#tx = get_transaction('0xd3CdA913deB6f67967B99D67aCDFa1712C293601')
#print(tx)


#gp = get_gas_price(tx)
#print("gas price" ,gp)

#gg = get_gas(tx)
#print(gg)


