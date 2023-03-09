from flask import Flask, request, g
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from flask import jsonify
from web3 import Web3
import json
import eth_account
import algosdk
from algosdk import mnemonic
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import load_only
from datetime import datetime
import math
import sys
import traceback

# TODO: make sure you implement connect_to_algo, send_tokens_algo, and send_tokens_eth
from send_tokens import connect_to_algo, connect_to_eth, send_tokens_algo, send_tokens_eth

from models import Base, Order, TX
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

app = Flask(__name__)

""" Pre-defined methods (do not need to change) """

@app.before_request
def create_session():
    g.session = scoped_session(DBSession)

@app.teardown_appcontext
def shutdown_session(response_or_exc):
    sys.stdout.flush()
    g.session.commit()
    g.session.remove()

def connect_to_blockchains():
    try:
        # If g.acl has not been defined yet, then trying to query it fails
        acl_flag = False
        g.acl
    except AttributeError as ae:
        acl_flag = True

    try:
        if acl_flag or not g.acl.status():
            # Define Algorand client for the application
            g.acl = connect_to_algo()
    except Exception as e:
        print("Trying to connect to algorand client again")
        print(traceback.format_exc())
        g.acl = connect_to_algo()

    try:
        icl_flag = False
        g.icl
    except AttributeError as ae:
        icl_flag = True

    try:
        if icl_flag or not g.icl.health():
            # Define the index client
            g.icl = connect_to_algo(connection_type='indexer')
    except Exception as e:
        print("Trying to connect to algorand indexer client again")
        print(traceback.format_exc())
        g.icl = connect_to_algo(connection_type='indexer')


    try:
        w3_flag = False
        g.w3
    except AttributeError as ae:
        w3_flag = True

    try:
        if w3_flag or not g.w3.isConnected():
            g.w3 = connect_to_eth()
    except Exception as e:
        print("Trying to connect to web3 again")
        print(traceback.format_exc())
        g.w3 = connect_to_eth()

""" End of pre-defined methods """

""" Helper Methods (skeleton code for you to implement) """

def log_message(message_dict):
    msg = json.dumps(message_dict)
    log = Log()
    log.payload = msg
    g.session.add(log)
    g.session.commit()

    return

def get_algo_keys():
    try:
        private_key, account_address = algosdk.account.generate_account()
        algo_mnemonic = mnemonic.from_private_key(private_key)
        algo_sk = mnemonic.to_private_key(algo_mnemonic)
        algo_pk = mnemonic.to_public_key(algo_mnemonic)
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        print(e)

    return algo_sk, algo_pk

def get_eth_keys(filename = "eth_mnemonic.txt"):
    w3 = Web3()
    w3.eth.account.enable_unaudited_hdwallet_features()
    acct,mnemonic_secret = w3.eth.account.create_with_mnemonic()

    acct = w3.eth.account.from_mnemonic(mnemonic_secret)
    # the ethereum public/private keys
    eth_pk = acct._address
    eth_sk = acct._private_key

    return eth_sk, eth_pk

def execute_txes(txes):
    if txes is None:
        return True
    if len(txes) == 0:
        return True
    print( f"Trying to execute {len(txes)} transactions" )
    print( f"IDs = {[tx['order_id'] for tx in txes]}" )
    eth_sk, eth_pk = get_eth_keys()
    algo_sk, algo_pk = get_algo_keys()

    if not all( tx['platform'] in ["Algorand","Ethereum"] for tx in txes ):
        print( "Error: execute_txes got an invalid platform!" )
        print( tx['platform'] for tx in txes )

    algo_txes = [tx for tx in txes if tx['platform'] == "Algorand" ]
    eth_txes = [tx for tx in txes if tx['platform'] == "Ethereum" ]

    # TODO:
    #       1. Send tokens on the Algorand and eth testnets, appropriately
    #          We've provided the send_tokens_algo and send_tokens_eth skeleton methods in send_tokens.py
    #       2. Add all transactions to the TX table

    pass

''' START: Order creation and validation methods '''
def is_valid(order):
    if order.buy_amount == 0:
        print('Error: buy_amount cannot be 0')
        return False
    else:
        if order.sell_amount == 0:
            print('Error: sell_amount cannot be 0')
            return False
        else:
            if order.buy_amount < 0:
                print('Error: buy_amount cannot be negative')
                return False
            if order.sell_amount < 0:
                print('Error: sell_amount cannot be negative')
                return False
        return True

def create_order(content):
    order = Order()
    order.sender_pk = content['sender_pk']
    order.receiver_pk = content['receiver_pk']
    order.buy_currency = content['buy_currency']
    order.sell_currency = content['sell_currency']
    order.buy_amount = content['buy_amount']
    order.sell_amount = content['sell_amount']
    order.tx_id = content['tx_id']
    order.signature = sig
''' END: Order creation and validation methods '''


''' START: Signature validation methods '''
# method to validate eth signature
def verify_eth(payload, sig, sender_pk):
    msg = json.dumps(payload)
    # encode the payload
    eth_encoded_msg = eth_account.messages.encode_defunct(text=msg)
    if eth_account.Account.recover_message(eth_encoded_msg, signature=sig) == sender_pk:
        return True
    else:
        return False


# method to validate algo sig
def verify_algo(payload, sig, sender_pk):
    msg = json.dumps(payload)
    if algosdk.util.verify_bytes(msg.encode('utf-8'),sig,sender_pk):
        return True
    else:
        return False
''' END: Signature validation methods '''

''' START: Backing transaction validation methods '''
# method to check the backing transaction of an ETH transaction
def check_eth_backing_tx(tx_id):
    try:
        tx = w3.eth.get_transaction(tx_id)
        print("tx['value']", tx['value'])
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        print(e)
    return tx['value']

def check_algo_backing_tx(tx_id, amt):
    tx = algosdk.search_transactions(txid=tx_id, min_amount=int(amt), max_amount=int(amt))

    if tx != None:
        return True
    else:
        return False

''' END: Backing transaction validation methods '''

''' START: fill order methods '''
def fill_order(order, txes=[]):
    # Match orders (same as Exchange Server II)
    # Validate the order has a payment to back it (make sure the counterparty also made a payment)
    # Make sure that you end up executing all resulting transactions!
    eo = g.session.query(Order)
    eo = eo.filter(Order.filled == None)
    eo = eo.filter(Order.buy_currency == order.sell_currency).filter(Order.sell_currency == order.buy_currency)
    eo = eo.filter(Order.sell_amount / Order.buy_amount >= order.buy_amount / order.sell_amount)
    eo = eo.order_by(Order.buy_amount / Order.sell_amount).first()

    if eo is not None:
        eo.filled = datetime.now()
        order.filled = datetime.now()
        order.counterparty_id = eo.id
        eo.counterparty_id = order.id
        new_txes = []
        new_txes.append(make_tx(eo.buy_currency, eo.receiver_pk, min(order.sell_amount, eo.buy_amount)))
        new_txes.append(make_tx(order.buy_currency, order.sender_pk, min(order.buy_amount, eo.sell_amount)))

        if order.sell_amount < eo.buy_amount:
            new_order = Order()
            new_order.buy_amount = eo.buy_amount - order.sell_amount
            new_order.sell_amount = (1 - float(order.sell_amount) / eo.buy_amount) * eo.sell_amount
            new_order.buy_currency = eo.buy_currency
            new_order.sell_currency = eo.sell_currency
            new_order.sender_pk = eo.sender_pk
            new_order.creator_id = order.id
            g.session.flush()
            eo.child = new_order.id
            g.session.add(new_order)

        if eo.sell_amount < order.buy_amount:
            new_order = Order()
            new_order.buy_amount = order.buy_amount - eo.sell_amount
            new_order.buy_currency = order.buy_currency
            new_order.sell_currency = order.sell_currency
            new_order.sender_pk = order.sender_pk
            new_order.sell_amount = (1 - float(eo.sell_amount) / order.buy_amount) * order.sell_amount
            new_order.creator_id = order.id

            order.child = new_order.id
            g.session.add(new_order)

            g.session.commit()

            return fill_order(new_order, txes=(txes + new_txes))
        else:
            g.session.commit()
            return txes + new_txes
''' END: fill order methods '''

""" End of Helper methods"""
@app.route('/address', methods=['POST'])
def address():
    print( f"In /address", file=sys.stderr)
    if request.method == "POST":
        content = request.get_json(silent=True)
        if 'platform' not in content.keys():
            print( f"Error: no platform provided" )
            return jsonify( "Error: no platform provided" )
        if not content['platform'] in ["Ethereum", "Algorand"]:
            print( f"Error: {content['platform']} is an invalid platform" )
            return jsonify( f"Error: invalid platform provided: {content['platform']}"  )

        if content['platform'] == "Ethereum":
            eth_sk, eth_pk = get_eth_keys()
            return jsonify( eth_pk )
        if content['platform'] == "Algorand":
            algo_sk, algo_pk = get_algo_keys()
            return jsonify( algo_pk )

@app.route('/trade', methods=['POST'])
def trade():
    print( "In trade", file=sys.stderr )
    connect_to_blockchains()
    get_keys()
    if request.method == "POST":
        content = request.get_json(silent=True)
        columns = [ "buy_currency", "sell_currency", "buy_amount", "sell_amount", "platform", "tx_id", "receiver_pk"]
        fields = [ "sig", "payload" ]
        error = False
        for field in fields:
            if not field in content.keys():
                print( f"{field} not received by Trade" )
                error = True
        if error:
            print( json.dumps(content) )
            return jsonify( False )

        error = False
        for column in columns:
            if not column in content['payload'].keys():
                print( f"{column} not received by Trade" )
                error = True
        if error:
            print( json.dumps(content) )
            return jsonify( False )
        # Your code here
        ''' get the fields from content '''
        sig = content['sig']
        payload = content['payload']
        sender_pk = content['payload']['sender_pk']
        receiver_pk = content['payload']['receiver_pk']
        buy_currency = content['payload']['buy_currency']
        sell_currency = content['payload']['sell_currency']
        buy_amount = content['payload']['buy_amount']
        sell_amount = content['payload']['sell_amount']
        tx_id = content['payload']['tx_id']
        platform = content['payload']['platform']
        ''' end getting fields from content '''

        # 1. Check the signature
        if platform.lower() == 'ethereum':
            valid = verify_eth(payload, sig, sender_pk)
        if platform.lower() == 'algorand':
            valid = verify_algo(payload, sig, sender_pk)

        # if signature was invalid, add create Log record and add to Log table
        if valid == False:
            log_message(payload)
            return jsonify(False)

        # 2. Add the order to the table
        # create an Order obj of the content
        current_order = create_order(content)
        # check if the order is valid
        valid_order = is_valid(current_order)
        if not valid_order: return jsonify (False)
        # add the order to the table
        g.session.add(current_order)
        g.session.commit()

        # 3a. Check if the order is backed by a transaction equal to the sell_amount (this is new)
        tx_sell_amt_matches_order = None
        if sell_currency.lower() == 'ethereum':
            tx_sell_amt = check_eth_backing_tx(tx_id)
            tx_sell_amt_matches_order = tx_sell_amt == int(sell_amount)
        if sell_currency.lower() == 'algorand':
            tx_sell_amt_matches_order = check_algo_backing_tx(tx_id, int(sell_amount))

        if tx_sell_amt != int(sell_amount): return jsonify( False )

        # 3b. Fill the order (as in Exchange Server II) if the order is valid
        fill_order(new_order)

        # 4. Execute the transactions


        # If all goes well, return jsonify(True). else return jsonify(False)
        return jsonify(True)

@app.route('/order_book')
def order_book():
    fields = [ "buy_currency", "sell_currency", "buy_amount", "sell_amount", "signature", "tx_id", "receiver_pk" ]
    query = g.session.query(Order)   # Same as before
    result = { 'data': [{field:getattr(u, field) for field in fields} for u in query.all()]}

    return jsonify(result)

if __name__ == '__main__':
    app.run(port='5002')
