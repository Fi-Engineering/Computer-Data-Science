#!/usr/bin/python3

from algosdk.v2client import algod
from algosdk import mnemonic
from algosdk import transaction


from algosdk import account, encoding




#Connect to Algorand node maintained by PureStake
algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "B3SU4KcVKi94Jap2VXkK83xx38bsv95K5UZm2lab"
#algod_token = 'IwMysN3FSZ8zGVaQnoUIJ9RXolbQ5nRY62JRqF2H'
headers = {
   "X-API-Key": algod_token,
}

acl = algod.AlgodClient(algod_token, algod_address, headers)
min_balance = 100000 #https://developer.algorand.org/docs/features/accounts/#minimum-balance

def send_tokens( receiver_pk, tx_amount ):
    params1 = acl.suggested_params()
    gen_hash = params1.gh
    first_valid_round = params1.first
    tx_fee = params1.min_fee
    last_valid_round = params1.last
    
   
    # source:
        #    https://py-algorand-sdk.readthedocs.io/en/v1.2.1_a/  
  
    # mnems must be 25 words in length:
    mnemSecret = (
            "awful drop leaf tennis indoor begin mandate discover uncle seven "
            "only coil atom any hospital uncover make any climb actor armed me"
            "asure need above hundred")

    # generate an account
    private_key, address = account.generate_account()
    print("Private key:", private_key)
    print('\n')
    print("Address:", address, '\n\n')
    
    sk = mnemonic.to_private_key(mnemSecret)
    pk = mnemonic.to_public_key(mnemSecret)
    
    
    
   
    
    print('\n\n')
    
    # check if the address is valid
    if encoding.is_valid_address(address):
        print("The address is valid\n\n")
    else:
        print("The address is invalid\n\n")

    #Your code here:
    
    # from tutorial:    
    send_to_address = receiver_pk  
        
    tx = transaction.PaymentTxn(pk, tx_fee, first_valid_round, last_valid_round, gen_hash, send_to_address, tx_amount, flat_fee=True)
    
    signed_tx = tx.sign(sk)
   # print('signed_tx: \n', signed_tx, '\n')
    
    sender_pk = pk
    
    
    try:
        #tx_confirm = acl.send_transaction(signed_tx) # TypeError: can only concatenate str (not "SignedTransaction") to str
        #print('\ninside try: \n')
        tx_confirm = acl.send_transaction(signed_tx)
        print('Transaction sent with ID', signed_tx.transaction.get_txid())
        txid = signed_tx.transaction.get_txid()
        #print('\ntxid\n', txid, '\n\n')
        wait_for_confirmation(acl, txid=signed_tx.transaction.get_txid())
    except Exception as e:
        print('\n', e, '\n\n')


    return sender_pk, txid

# Function from Algorand Inc.
def wait_for_confirmation(client, txid):
    """
    Utility function to wait until the transaction is
    confirmed before proceeding.
    """
    last_round = client.status().get('last-round')
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        print("Waiting for confirmation")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')))
    return txinfo


# create receiver account vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

mnemSecret = (
            "awful drop leaf tennis indoor begin mandate discover uncle seven "
            "only coil atom any hospital uncover make any climb actor armed me"
            "asure need above hundred")

# generate an account
private_key, address = account.generate_account()
print("Private key:", private_key)
print('\n')
print("Address:", address, '\n\n')

sk = mnemonic.to_private_key(mnemSecret)
pk = mnemonic.to_public_key(mnemSecret)

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^    

receiver_pk = pk 
tx_amount = 100000      # 100k microalgos ?????????

sender_pk, txid = send_tokens(receiver_pk, tx_amount)


