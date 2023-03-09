#!/usr/bin/env python3

import random
import os
import sys
import signal
import subprocess

import eth_account
import algosdk
import requests
import json
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Order, Log, TX

#from send_eth import get_eth_sender, send_eth, connect_to_eth
#from send_algo import get_algo_sender, send_algo, connect_to_algo
#from check_txes import check_tx_algo, check_tx_eth

endpoint_url = "http://localhost"
endpoint_port = 5002
db_name = "orders.db"

def is_port_in_use(port):
    """
    Check if the specified port is in use on localhost
    (This usually means Flask was already)
    """
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def validate(student_repo_path):
    try:
        log = open( "server_log.txt", "w" )
    except Exception as e:
        print( "Can't open server_log.txt" )
        print( e )

    already_running = False
    if is_port_in_use(endpoint_port):
        already_running = True
        print( "Flask server is already running" )
    else:
        print( "Starting Flask server" )
        try:
            flask_server = subprocess.Popen(["python3", student_repo_path + "/exchange_endpoint.py"],
                                        stdout=log,
                                        stderr=subprocess.DEVNULL,
                                        shell=False,
                                        preexec_fn=os.setsid)
            #out, err = flask_server.communicate()
            #if err:
            #     print('The verification_endpoint raised an error:', err.decode())
            #else:
            #    print("Started Flask server!")
            try:
                time.sleep(1)
                outs, errs = flask_server.communicate(timeout=5)
                print( f"Errors = {errs}" )
            except subprocess.TimeoutExpired:
                print( "Flask timeout expired" )
                pass
            except Exception as e:
                print( "Flask process exception" )
                print( e )
            if flask_server.poll() is not None:
                print( "Error: Flask server stopped" )
                exit()
        except Exception as e:
            print( e )
            print( "Failed" )
            return 0
       
    #Algorand and Ethereum use the account-balance model (not UTXOs)
    #Accounts must have a minimum balance to be stored on the chain.
    #These functions ensure that the exchange server's accounts have the minimum balance
    ensure_min_balance_eth()
    ensure_min_balance_algo()
    
    #Clear tables
    #This script will test *all* the transactions in the TX database
    #If there are extra transactions in TX (e.g. from testing) that don't correspond to on-chain transactions this will result in a lower score
    try:
        engine = create_engine('sqlite:///'+db_name)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        session.query(Order).delete()
        session.query(TX).delete()
        session.commit()
    except Exception as e:
        print( e )
        print( "Failed to delete tables" )

    num_tests = 1 #Each test will send 10 transactions of each type
    num_passed = 0

    #Test sending transactions
    for _ in range(num_tests):
        try:
            test_result = test_endpoint() #This runs test trades through the endpoint and checks if the trades were inserted in the database (does not check matching)
            assert isinstance( test_result, int )
            num_passed += test_result
        except Exception as e:
            print( f"test_endpoint() failed: {e}" )
            continue

    submission_test = float(num_passed)/(10*num_tests)
    print( f"/trade endpoint accepted {num_passed}/{10*num_tests} orders" )

    #Check if a straight db call returns the same thing as the endpoint
    ob1 = get_order_book()
    ob2 = test_db()
    fields = ['buy_currency','sell_currency','buy_amount','sell_amount', 'signature', 'tx_id' ]
    ob3 = [ {field: t[field] for field in fields} for t in ob1 ] 
    ob4 = [ {field: t[field] for field in fields} for t in ob2 ] 
    if not dict_list_eq(ob3,ob4):
        print( "get_order_book returns a different result from the database!" )
        storage_test = 0
    else:
        print( "get_order_book returns the correct result" )
        storage_test = 1

    #Kill the server
    if not already_running:
        try:
            log.close()
            os.killpg(os.getpgid(flask_server.pid), signal.SIGTERM)
        except ProcessLookupError:
            pass

    num_errors = check_matches() #Check whether the filled orders adhered to the guidelines

    matching_error = pow(.95,-num_errors)
    if matching_error < 1:
        print( f"Error: {num_errors} errors in matching algorithm" )
    else:
        print( f"All matches were valid" )

    fill_fraction = 1
    num_filled, num_orders = check_payouts()
    if num_orders > 0:
        fill_fraction = float(num_filled)/num_orders

    print( f"{num_orders} orders recorded in TX table.  {num_filled} orders filled on chain" )

    assert submission_test >= 0 and submission_test <= 1
    assert storage_test >=0 and storage_test <= 1
    assert matching_error >= 0 and matching_error <= 1
    assert fill_fraction >= 0 and fill_fraction <= 1

    final_score = int( 25*submission_test + 25*storage_test + 25*matching_error + 25*fill_fraction)

    if final_score > 100:
        print( f"submission_test = {submission_test}" )
        print( f"storage_test = {storage_test}" )
        print( f"matching_error = {matching_error}" )
        print( f"fill_fraction = {fill_fraction}" )

    print( f"Final score would be {final_score}/100" )
    return final_score

def ensure_min_balance_eth():
    """
    Make sure the exchange server has enough ETH to pay transaction fees.
    """
    #https://developer.algorand.org/docs/features/accounts/
    eth_min_balance = pow(10,14)
    post_dict = {'platform': 'Ethereum' }
    try:
        exchange_eth_receiver = requests.post( endpoint_url + ":" + str(endpoint_port) + "/address", json=post_dict ).json()
    except Exception as e:
        print( "Couldn't get Ethereum server pk from '/address' endpoint" )
        print( e )
        sys.exit(1)
    try:
        w3 = connect_to_eth()
    except Exception as e:
        print( e )
        print( "Failed to connect to Ethereum" )
        sys.exit(1)

    try:
        initial_balance = w3.eth.get_balance(exchange_eth_receiver)
    except Exception as e:
        print( "Failed to get balance" )

    if initial_balance < eth_min_balance:
        print( "Server balance too low ... topping it up" )
        try:
            tx_id= send_eth( w3, exchange_eth_receiver, eth_min_balance)
        except Exception as e:
            tx_success = False
            print( e )
            print( "Failed to execute Ethereum tx" )


def ensure_min_balance_algo():
    """
    Make sure the exchange server has the mininum balance in its Algorand account
    If it doesn't small transactions sent to the address will fail
    If not, send the minimum balance
    """
    #https://developer.algorand.org/docs/features/accounts/
    algo_min_balance = 100000
    post_dict = {'platform': 'Algorand' }
    try:
        exchange_algo_receiver = requests.post( endpoint_url + ":" + str(endpoint_port) + "/address", json=post_dict ).json()
    except Exception as e:
        print( "Couldn't get Algorand server pk from '/address' endpoint" )
        print( e )
    try:
        acl = connect_to_algo()
    except Exception as e:
        print( e )
        print( "Failed to connect to Algorand" )
        sys.exit(1)
    try:
        tx_id= send_algo( acl, exchange_algo_receiver, algo_min_balance)
    except Exception as e:
        tx_success = False
        print( e )
        print( "Failed to execute Algorand tx" )

def create_txes(num_txes=2):
    """
        Create num_txes transactions on both the Ethereum and Algorand blockchains
        Each transaction uses the receiver provided by the Exchange endpoint (at /addresses)
        create_txes() returns a list of dicts, encoding the details of the transactions (sender,receiver,platform,amount,tx_id)
    """

    #Get exchange's keys (where users should send their tokens for escrow)
    post_dict = {'platform': 'Algorand' }
    try:
        exchange_algo_receiver = requests.post( endpoint_url + ":" + str(endpoint_port) + "/address", json=post_dict ).json()
    except Exception as e:
        print( "Couldn't get Algorand server pk" )
        print( e )
    post_dict = {'platform': 'Ethereum' }
    try: 
        exchange_eth_receiver = requests.post( endpoint_url + ":" + str(endpoint_port) + "/address", json=post_dict ).json()
    except Exception as e:
        print( "Couldn't get Ethereum server pk" )
        print( e )
        
    algo_pk = get_algo_sender(pk_only=True)
    eth_pk = get_eth_sender(pk_only=True)

    #Make Algorand TX
    try:
        acl = connect_to_algo()
    except Exception as e:
        print( e )
        print( "Failed to connect to Algorand" )
    try:
        w3 = connect_to_eth()
    except Exception as e:
        print( e )
        print( "Failed to connect to Ethereum" )

    txes = []
    for nonce_offset in range(num_txes):
        order_dict = {}
        order_dict['buy_currency'] = "Ethereum"
        order_dict['sell_currency'] = "Algorand"
        order_dict['sender_pk'] = algo_pk
        order_dict['receiver_pk'] = eth_pk
        order_dict['buy_amount'] = random.randint(1,10)
        order_dict['sell_amount'] = random.randint(1,10)
        tx_success = True
        try:
            order_dict['tx_id'] = send_algo( acl, exchange_algo_receiver, order_dict['sell_amount'], nonce_offset = nonce_offset )
        except Exception as e:
            tx_success = False
            print( e )
            print( "Error: Tried to send Algos to the exchange and failed" )
            if 'tx_id' not in order_dict.keys():
                print( "tx_id not added for Algorand tx" )
        if tx_success:
            txes.append(order_dict)
        time.sleep(1)

        #Make Ethereum transaction
        order_dict = {}
        order_dict['buy_currency'] = "Algorand"
        order_dict['sell_currency'] = "Ethereum"
        order_dict['sender_pk'] = eth_pk
        order_dict['receiver_pk'] = algo_pk
        order_dict['buy_amount'] = random.randint(1,10)
        order_dict['sell_amount'] = random.randint(1,10)
        tx_success = True
        try:
            order_dict['tx_id'] = send_eth( w3, exchange_eth_receiver, order_dict['sell_amount'],nonce_offset=nonce_offset )
            assert isinstance( order_dict['tx_id'], str )
        except Exception as e:
            tx_success = False
            print( e )
            print( "Error: tried to send ETH to the exchange and failed" )
            if 'tx_id' not in order_dict.keys():
                print( "tx_id not added for Ethereum tx" )
        if tx_success:
            txes.append(order_dict)

    return txes

def dict_list_eq(l1, l2):
    """"
        Given two lists of dictionaries, l1 and l2, check if the two lists have the same elements (possibly in different orders)
    """
    sorted_l1 = sorted([sorted([p for p in d.items() if p[1] is not None]) for d in l1])
    sorted_l2 = sorted([sorted([p for p in d.items() if p[1] is not None]) for d in l2])
    return sorted_l1 == sorted_l2

def send_signed_msg(platform,order_dict,sk,pk,real=True):
    """
        sign the message given by the dict 'order_dict' using the secret key sk
        platform should be Algorand or Ethereum and the signing algorithm depends on the platform variable
        the signed message is then posted to the exchange endpoint /trade
        if real == False, then the message is tweaked before sending so the signature will *not* validate
    """
    msg_dict = { 'pk': pk, 'platform': platform }
    msg_dict.update( order_dict )
    
    if platform == "Ethereum":
        msg = json.dumps(msg_dict)
        eth_encoded_msg = eth_account.messages.encode_defunct(text=msg)
        eth_sig_obj = eth_account.Account.sign_message(eth_encoded_msg,sk)
        sig = eth_sig_obj.signature.hex() #.hex converts HexBytes object a string (which is JSON serializable)
    if platform == "Algorand":
        msg = json.dumps(msg_dict)
        alg_encoded_msg = msg.encode('utf-8')
        sig = algosdk.util.sign_bytes(alg_encoded_msg,sk)
    
    if not real:
        msg_dict['buy_amount'] += 2
    
    post_dict = { 'sig': sig, 'payload': msg_dict }
    try:
        res = requests.post( endpoint_url + ":" + str(endpoint_port) + "/trade", json=post_dict )
    except Exception as e:
        res = None
        print( "Error in send_signed_msg" )
        print( "=====" )
        print( post_dict )
        print( "=====" )
        print( e )
    try:
        res_json = res.json()
    except Exception as e:
        print( "Error in send_signed_msg" )
        print( "Can't jsonify result" )
        print( res )
        print( e ) 
        res_json = ""

    return res_json

def get_order_book():
    """
    Get the current state of the order book from the endpoint /order_book
    retruns a list of dicts
    """
    try:
        res = requests.get( endpoint_url + ":" + str(endpoint_port) + "/order_book", json={} ).json()
    except Exception as e:
        print( "endpoint /order_book failed" )
        print( e ) 
        return []
    fields = ['sender_pk', 'buy_currency','sell_currency','buy_amount','sell_amount', 'signature', 'tx_id', 'receiver_pk' ]
    try:
        order_book = [ {field: t[field] for field in fields} for t in res['data']] 
    except Exception as e:
        print( "/order_book returned an invalid response" )
        print( e )
        return []
    return order_book

def test_endpoint():
    """
    Runs trades through the endpoint and checks whether the endpoint responses are correct
    In particular, it checks whether the endpoint rejects transactions with invalid signatures
    """
    num_passed = 0
    txes = create_txes(5) #Creates 5 txes on the Algorand blockchain, and 5 on the Ethereum blockchain (and sends them to the exchange)
    for tx in txes: 
        for real in [True, False]:
            try:
                num_passed += test_trade(tx,real) #Hits the "/trade" endpoint of the exchange server, and posts a limit order (if real=False the signature on the limit order is invalid, even though the transaction itself was valid).
            except Exception as e:
                print( f"Error: test_trade ({tx['sell_currency']}) failed" )
                print( e )
    return num_passed

def test_db():
    fields = ['buy_currency','sell_currency','buy_amount','sell_amount', 'signature', 'tx_id' ]
    try:
        engine = create_engine('sqlite:///'+db_name)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
    except Exception as e:
        print( e )
        print( "Couldn't connect to DB" )
        return None
    try:
        query = session.query(Order)
        result = [{field:getattr(u,field)for field in fields} for u in query.all()]
    except Exception as e:
        print( "Connection failed" )
        resurt = []
    return result

def test_trade( order_dict, real=True ):
    """
    Tests whether the endpoint "/trade" processes orders correctly
    order_dict specifies an order (including the tx_id of a valid transaction sending coins to the exchange server)
    the order is signed, and sent to the endpoint "/trade"
    Then the function checks the current state of the database to make sure that the order was correctly inserted into the database.
    If real == False, then the signature on the order sent to "/trade" will *not* verify, and the order should *not* be inserted into the database.
    """
    if order_dict['sell_currency'] not in ["Algorand","Ethereum"]:
        print( f"Error in test_trade, unknown platform {order_dict['sell_currency']}" )
        return False
    if order_dict['sell_currency'] == "Algorand":
        algo_sk, algo_pk = get_algo_sender()
        platform = "Algorand"
        response = send_signed_msg( platform, order_dict, algo_sk, algo_pk, real )
    if order_dict['sell_currency'] == "Ethereum":
        eth_sk, eth_pk = get_eth_sender()
        platform = "Ethereum"
        response = send_signed_msg( platform, order_dict, eth_sk, eth_pk, real )
    order_book = get_order_book()
    if real:
        for order in order_book:
            try:
                if all( order[k] == order_dict[k] for k in order_dict.keys() ):
                    return True
            except Exception as e:
                print( f"Error in test_trade: ({platform})" )
                print( e )
        return False
    else:
        for order in order_book:
            try: 
                if all( order[k] == order_dict[k] for k in order_dict.keys() ):
                    return False
            except Exception as e:
                print( f"Error in test_trade: ({platform})" )
                print( e )
        return True
    print( "Shouldn't get here" )


def check_matches():
    """
    Connect directly to the order database (not through the Flask server)
    Check if the database is internally consistent
    """
    try:
        engine = create_engine('sqlite:///'+db_name)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
    except Exception as e:
        print( e )
        print( "Couldn't connect to DB" )
        return None
    num_errors = 0
    print( f"{session.query(Order).filter(Order.filled != None ).count()} orders filled" )
    orders = session.query(Order).filter(Order.filled != None )
    for order in orders:
        if order.counterparty is None:
            print( "Error: filled order with no counterparty!" )
            print( f"Order.id = {order.id}" )
            num_errors += 1
            continue
        if len(order.counterparty) > 1:
            print( "Error: orders should have at most 1 counterparty" )
            print( f"Order.id = {order.id}" )
            num_errors += 1
            continue
        if order.timestamp < order.counterparty[0].timestamp:
            maker = order
            taker = order.counterparty[0]
        else:
            maker = order.counterparty[0]
            taker = order
        if maker.buy_currency != taker.sell_currency:
            print( "Error: maker.buy_currency != taker.sell_currency!" )
            print( f"maker.id = {maker.id}" )
            print( f"taker.id = {taker.id}" )
            num_errors += 1
        if maker.sell_currency != taker.buy_currency:
            print( "Error: maker.sell_currency != taker.buy_currency!" )
            print( f"maker.id = {maker.id}" )
            print( f"taker.id = {taker.id}" )
            num_errors += 1
        if maker.sell_amount == 0:
            print( "Error: sell amount should never be 0" )
            print( f"Order.id = {maker.id}" )
            num_errors += 1
            continue
        if taker.buy_amount == 0:
            print( "Error: buy amount should never be 0" )
            print( f"Order.id = {taker.id}" )
            num_errors += 1
            continue
        if maker.buy_amount/maker.sell_amount > taker.sell_amount/taker.buy_amount:
            print( "Error: the exchange is losing money on this trade" )
            print( f"maker.id = {maker.id}" )
            print( f"taker.id = {taker.id}" )
            num_errors += 1
        if taker.buy_amount > maker.sell_amount:
            if not taker.child:
                print( "Error: partially filled order should have a child" )

    orders = session.query(Order).filter(Order.creator_id != None)
    for order in orders:
        if order.creator.sender_pk != order.sender_pk:
            print( "Error: order and its creator should have the same sender_pk" )
            num_errors += 1
        if order.creator.buy_currency != order.buy_currency:
            print( "Error: order and its creator should have the same buy_currency" )
            num_errors += 1
        if order.creator.sell_currency != order.sell_currency:
            print( "Error: order and its creator should have the same sell_currency" )
            num_errors += 1
        if order.creator.timestamp > order.timestamp:
            print( "Error: order created befor its creator" )
            num_errors += 1
        if order.creator.buy_amount == 0:
            print( "Error: buy amount should never be 0" )
            print( f"Order.id = {order.creator.id}" )
            num_errors += 1
            continue
        if order.creator.sell_amount == 0:
            print( "Error: sell amount should never be 0" )
            print( f"Order.id = {order.creator.id}" )
            num_errors += 1
            continue
        if order.buy_amount/order.creator.buy_amount > order.sell_amount/order.creator.sell_amount + .05: #Extra .05 is because of rounding errors
            print( "Error: derived order has worse implied exchange rate" )
            print( f"{order.buy_amount:.2f}/{order.creator.buy_amount:.2f} > {order.sell_amount:.2f}/{order.creator.sell_amount:.2f}" )
            print( f"{order.buy_amount/order.creator.buy_amount:.2f} > {order.sell_amount/order.creator.sell_amount:.2f}" )
            print( f"Order.id = {order.id}" )
            print( f"Creator.id = {order.creator.id}" )
            num_errors += 1
    return num_errors

def check_payouts():
    """
    Check that orders that were processed by the exchange, were actually processed on chain
    This function checks the TX database, and for every transaction in TX, it checks that the transaction corresponds to a valid transaction on the Ethereum or Algorand blockchain
    This function *does not* check whether orders should have been matched, i.e., if the TX database is empty this function will not report any errors.
    This functions returns the number of orders filled on chain, and the number of orders that should have been filled (i.e., the number of entries in the TX table)
    """
    try:
        engine = create_engine('sqlite:///'+db_name)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
    except Exception as e:
        print( e )
        print( "Couldn't connect to DB" )
        return None
    num_errors = 0

    orders = session.query(Order).filter(Order.filled != None )

    icl = connect_to_algo(connection_type="indexer")
    w3 = connect_to_eth()

    num_orders = orders.count()
    num_filled = 0
    for order in orders:
        amount = order.buy_amount
        if order.child:
            amount -= order.child[0].buy_amount
        derived_order = session.query(Order).filter(Order.creator_id == order.id)
        txes = session.query(TX).filter(TX.order_id == order.id)
        if txes.count() == 0:
            print( f"Order {order.id} marked as filled in Order table, but no corresponding record in TX table!" )
            print( f"order.buy_currency = {order.buy_currency}" )
            if order.creator_id:
                print( f"This was a child order: created by {order.creator_id}" )
            if order.child:
                print( f"This was a parent order: created {order.child[0].id}" )
            print( f"order.filled = {order.filled}" )
        for tx in txes:
            #print( f"tx_id = {tx.tx_id}" )
            #print( f"receiver key = {tx.receiver_pk}" )
            #print( f"amount = {amount}" )
            if tx.order.buy_currency == "Algorand":
                algo_filled = check_tx_algo( icl, tx.tx_id, tx.receiver_pk, amount ) 
                if algo_filled:
                    num_filled += 1
                else:
                    print( "Algo TX recorded in the the TX table wasn't executed on chain" )
                    print( f"order.id = {tx.order_id}" )
                    print( f"tx_id = {tx.tx_id}" )
                    print( f"receiver = {tx.receiver_pk}" )
                time.sleep(1) #PureStake only allows 1 request per second
            if tx.order.buy_currency == "Ethereum":
                eth_filled = check_tx_eth( w3, tx.tx_id, tx.receiver_pk, amount ) 
                if eth_filled:
                    num_filled += 1
                else:
                    print( "Eth TX recorded in the TX table wasn't executed on chain" )
                    print( f"order.id = {tx.order_id}" )
                    print( f"tx_id = {tx.tx_id}" )
                    print( f"receiver = {tx.receiver_pk}" )

    return num_filled, num_orders

from algosdk.v2client import algod
from algosdk.v2client import indexer
from algosdk import mnemonic
from algosdk.future import transaction
from algosdk import account

def connect_to_algo(connection_type=''):
    #Connect to Algorand node maintained by PureStake
    algod_token = "B3SU4KcVKi94Jap2VXkK83xx38bsv95K5UZm2lab"
    headers = {
       "X-API-Key": algod_token,
    }
    if connection_type == "indexer":
        algod_address = "https://testnet-algorand.api.purestake.io/idx2"
        acl = indexer.IndexerClient(algod_token, algod_address, headers)
    else:
        algod_address = "https://testnet-algorand.api.purestake.io/ps2"
        acl = algod.AlgodClient(algod_token, algod_address, headers)
    return acl


def get_algo_sender(pk_only=False):
    try:
        mnemonic_secret = "soft quiz moral bread repeat embark shed steak chalk joy fetch pilot shift floor identify poverty index yard cannon divorce fatal angry mistake abandon voyage"
        sender_sk = mnemonic.to_private_key(mnemonic_secret)
        sender_pk = mnemonic.to_public_key(mnemonic_secret)
    except Exception as e:
        print( "Error: couldn't read sender address" )
        print( e )
        return "", ""
    if pk_only:
        return sender_pk
    return sender_sk, sender_pk

# Function from Algorand Inc.
def wait_for_algo_confirmation(client, txid):
    """
    Utility function to wait until the transaction is
    confirmed before proceeding.

    Raises AlgodHTTPError if txid is not pending
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


def send_algo( acl, receiver_pk, amt, nonce_offset=0 ):
    sender_sk, sender_pk = get_algo_sender()
    return send_tokens_algo( acl, sender_sk, receiver_pk, amt,nonce_offset )

def send_tokens_algo( acl, sender_sk, receiver_pk, tx_amount,nonce_offset=0 ):
    sp = acl.suggested_params()

    sp.last = sp.first + 800 + nonce_offset #Algorand requires sp.last - sp.first < 1000

    sender_pk = account.address_from_private_key(sender_sk)

    # Create and sign transaction
    tx = transaction.PaymentTxn(sender_pk, sp, receiver_pk, tx_amount )
    signed_tx = tx.sign(sender_sk)
   
    tx_success = True
    try:
        print(f"Sending {tx_amount} microalgo from {sender_pk} to {receiver_pk}" )
        tx_confirm = acl.send_transaction(signed_tx)
    except Exception as e:
        tx_success = False
        print( f"Error in send_tokens_algo" )
        print(e)

    if tx_success:
        try:
            txid = signed_tx.transaction.get_txid()
            #txinfo = wait_for_algo_confirmation(acl, txid = txid )
            #print(f"Sent {tx_amount} microalgo in transaction: {txid}\n" )
        except Exception as e:
            print( "algo get_txid failed" )
            print( e )

        return txid
    else:
        return None

from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.exceptions import TransactionNotFound
import json
import progressbar
from hexbytes import HexBytes

def connect_to_eth():
    IP_ADDR='3.23.118.2' #Private Ethereum
    PORT='8545'

    w3 = Web3(Web3.HTTPProvider('http://' + IP_ADDR + ':' + PORT))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0) #Necessary to interact with our private PoA blockchain
    w3.eth.account.enable_unaudited_hdwallet_features() #Necessary for privateKeyToAccount
    if w3.isConnected():
        return w3
    else:
        print( "Failed to connect to Eth" )
        return None

def wait_for_eth_confirmation(tx_hash):
    print( "Waiting for confirmation" )
    widgets = [progressbar.BouncingBar(marker=progressbar.RotatingMarker(), fill_left=False)]
    i = 0
    with progressbar.ProgressBar(widgets=widgets, term_width=1) as progress:
        while True:
            i += 1
            progress.update(i)
            try:
                receipt = w3.eth.get_transaction_receipt(tx_hash)
                print( "\n" )
            except TransactionNotFound:

                #print( "." )
                print( ".", end="" )
                continue
            break 
    return receipt


def get_eth_sender(pk_only=False):
    eth_mnemonic = "beauty diagram educate skirt unfold sing chaos depend acoustic science engage rib"

    w3 = Web3()
    w3.eth.account.enable_unaudited_hdwallet_features()
    acct = w3.eth.account.from_mnemonic(eth_mnemonic)
    eth_pk = acct._address
    eth_sk = acct._private_key.hex() #private key is of type HexBytes which is not JSON serializable, adding .hex() converts it to a string

    if pk_only:
        return eth_pk
    return eth_sk, eth_pk

def send_eth(w3,receiver_pk,amt,nonce_offset=0):
    sender_sk, sender_pk = get_eth_sender()
    return send_tokens_eth(w3,sender_sk,receiver_pk,amt)

def send_tokens_eth(w3,sender_sk,receiver_pk,amt,nonce_offset=0):
    #w3.eth.account.enable_unaudited_hdwallet_features()
    try:
        sender_account = w3.eth.account.privateKeyToAccount(sender_sk)
    except Exception as e:
        print( "Error in send_tokens_eth" )
        print( e ) 
        return None, None
    sender_pk = sender_account._address

    initial_balance = w3.eth.get_balance(sender_pk)

    nonce = w3.eth.get_transaction_count(sender_pk,'pending')
    nonce += nonce_offset

    tx_dict = {
            'nonce':nonce,
            'gasPrice':w3.eth.gas_price,
            'gas': w3.eth.estimate_gas( { 'from': sender_pk, 'to': receiver_pk, 'data': b'', 'amount': amt } ),
            'to': receiver_pk,
            'value': amt,
            'data':b'' }

    signed_txn = w3.eth.account.sign_transaction(tx_dict, sender_sk)

    in_queue = 0
    try:
        print( f"Sending {tx_dict['value']} WEI from {sender_pk} to {tx_dict['to']}" )
        tx_id = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    except ValueError as e:
        pending_block = w3.eth.get_block('pending',full_transactions=True)
        pending_txes = pending_block['transactions']
        for tx in pending_txes:
            if tx['to'] == receiver_pk and tx['from'] == sender_pk and tx['value'] == amt and tx['nonce'] == nonce:
                tx_id = tx['hash']
                in_queue = 1
                print( "TX already in queue" )
        if not in_queue:
            print( "Error sending Ethereum transaction" )
            print( f"nonce_offset == {nonce_offset}" )
            print( e )
            if 'message' in e.keys():
                if e['message'] == 'replacement transaction underpriced':
                    print( e['message'])
        return None

    #receipt = wait_for_eth_confirmation(tx_hash)
    if isinstance(tx_id,HexBytes):
        tx_id = tx_id.hex()
    return tx_id

def check_tx_algo( icl, algo_tx_id, receiver, amount, retry=0 ):
    if algo_tx_id is None:
        print( "check_tx_algo didn't get a tx_id" )
        return False
    if icl is None:
        print( "Error in check_tx_algo: received None instead of an indexer client (icl)" )
        return False
    try:
        if not icl.health():
            print( "Error in check_tx_algo: not connected to indexer" )
            return False
    except Exception as e:
            print( "Error in check_tx_algo" )
            print( icl )
            print( type(icl) )
            print( e )
            return False
    try:
        algo_tx = icl.search_transactions(txid=algo_tx_id)
    except Exception as e:
        try:
            acl = connect_to_algo()
            wait_for_algo_confirmation(acl,algo_tx_id)
        except Exception as e:
            pass
        try:
            algo_tx = icl.search_transactions(txid=algo_tx_id)
        except Exception as e:
            print( f"Search for Algorand transaction {algo_tx_id} failed" )
            print( e )
            return False

    try:
        if not 'transactions' in algo_tx.keys():
            print( f"Error in check_tx_algo: No transactions field" )
            return False
    except Exception as e:
        print( f"Error in check_tx_algo: No transactions field" )
        print( e )
        return False

    txes = []
    for tx in algo_tx['transactions']:
        if 'payment-transaction' in tx.keys():
            if tx['payment-transaction']['amount'] == amount and tx['payment-transaction']['receiver'] == receiver:
                return True
            else:
                print( f"Algo TX: {tx['payment-transaction']['receiver']} =? {receiver}" )
                print( f"Algo TX: {tx['payment-transaction']['amount']} =? {amount}" )
        else:
            print( "Error in check_tx_algo: expecting a payment transaction" )
            print( tx.keys() )
  
    if not algo_tx['transactions']:
        if retry < 10:
            time.sleep(1)
            print( "Transaction data not yet available to Indexer: Checking again" )
            return check_tx_algo( icl, algo_tx_id, receiver, amount, retry=retry+1 )
        else:
            return False
    print( f"algo_tx['transactions'] = {algo_tx['transactions']}" )
    print( "Leaving check_algo_tx" )
    return False

###############################################
###############################################

def check_tx_eth( w3, eth_tx_id, receiver, amount ):
    try:
        if not w3.isConnected():
            print( "Error in check_tx_eth: not connected to w3" )
            return False
    except Exception as e:
            print( "Error in check_tx_eth" )
            print( e )
            return False
    try:
        tx = w3.eth.get_transaction(eth_tx_id)
    except Exception as e:
        print( f"check_tx_eth failed" )
        print( f"eth_tx_id = {eth_tx_id}" )
        print( e )
        return False
    if not 'to' in tx.keys() or not 'value' in tx.keys():
        print( "Incorrect fields in Eth tx" )
        return False
    if tx['to'] == receiver and tx['value'] == amount:
        return True
    else:
        print( f"Eth TX: {tx['to']} =? {receiver}" )
        print( f"Eth TX: {tx['value']} =? {amount}" )
        return False

