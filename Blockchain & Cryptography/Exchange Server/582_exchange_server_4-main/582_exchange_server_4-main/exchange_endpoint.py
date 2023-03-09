from flask import Flask, request, g
from flask_restful import Resource, Api
from sqlalchemy import create_engine, and_
from flask import jsonify
import json
import eth_account
import algosdk
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import load_only
from datetime import datetime
import sys

from models import Base, Order, Log
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

app = Flask(__name__)

@app.before_request
def create_session():
    g.session = scoped_session(DBSession)

@app.teardown_appcontext
def shutdown_session(response_or_exc):
    sys.stdout.flush()
    g.session.commit()
    g.session.remove()

def create_order(sender_pk, receiver_pk, buy_currency, sell_currency, buy_amount, sell_amount, sig):
    order = Order()
    order.sender_pk = sender_pk
    order.receiver_pk = receiver_pk
    order.buy_currency = buy_currency
    order.sell_currency = sell_currency
    order.buy_amount = buy_amount
    order.sell_amount = sell_amount
    order.signature = sig
    return order
""" Suggested helper methods """


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


def process_order(order):
    order_dict = dict(order)
    del order_dict['pk']
    del order_dict['platform']
    if order_dict['buy_amount'] == 0:
        print('Error in process_order: buy_amount cannot be 0')
        log_message(order)
        return False
    else:
        if order_dict['sell_amount'] == 0:
            print('Error in process_order: sell_amount cannot be 0')
            log_message(payload)
            return False

        new_order = Order(**order_dict)
        g.session.add(new_order)
        g.session.commit()

        return fill_order(new_order)


def fill_order(order, txes=[]):
    if not is_valid(order):
        print('fill order received an invalid order')
        return txes
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

        # if order.sell_amount < eo.buy_amount:
        #     new_order = Order()
        #     new_order.buy_amount = eo.buy_amount - order.sell_amount
        #     new_order.sell_amount = (1 - float(order.sell_amount) / eo.buy_amount) * eo.sell_amount
        #     new_order.buy_currency = eo.buy_currency
        #     new_order.sell_currency = eo.sell_currency
        #     new_order.sender_pk = eo.sender_pk
        #     new_order.creator_id = order.id

        #     g.session.flush()

        #     # eo.child = new_order.id

        #     g.session.add(new_order)

        if eo.sell_amount < order.buy_amount:
            new_order = Order()
            new_order.buy_amount = order.buy_amount - eo.sell_amount
            new_order.buy_currency = order.buy_currency
            new_order.sell_currency = order.sell_currency
            new_order.sender_pk = order.sender_pk
            new_order.sell_amount = (1 - float(eo.sell_amount) / order.buy_amount) * order.sell_amount
            new_order.creator_id = order.id


            # order.child = new_order.id
            g.session.add(new_order)

            g.session.commit()

            return fill_order(new_order, txes=(txes + new_txes))

        else:
            g.session.commit()
            return txes + new_txes

def make_tx(platform, receiver, amount):
    if platform == 'Algorand':
        return make_tx_algo(receiver, amount)
    if platform == 'Ethereum':
        return make_tx_eth(receiver, amount)
    print(f"Error: make_tx received an invalid platform {platform}")


def make_tx_algo(receiver, amount):
    tx = {'sender':'exchange',
     'receiver':receiver,  'amount':amount,  'platform':'Algorand'}
    return tx


def make_tx_eth(receiver, amount):
    tx = {'sender':'exchange',
     'receiver':receiver,  'amount':amount,  'platform':'Ethereum'}
    return tx


def log_message(d):
    # Takes input dictionary d and writes it to the Log table
    # Hint: use json.dumps or str() to get it in a nice string form
    log = Log()
    log.payload = json.dumps(d)
    g.session.add(log)
    g.session.commit()

def verify_eth(payload, sig, sender_pk):
    msg = json.dumps(payload)
    # encode the payload
    eth_encoded_msg = eth_account.messages.encode_defunct(text=msg)
    if eth_account.Account.recover_message(eth_encoded_msg, signature=sig) == sender_pk:
        return True
    else:
        return False

def verify_algo(payload, sig, sender_pk):
    msg = json.dumps(payload)
    if algosdk.util.verify_bytes(msg.encode('utf-8'),sig,sender_pk):
        return True
    else:
        return False
""" End of helper methods """


@app.route('/trade', methods=['POST'])
def trade():
    print("In trade endpoint")
    if request.method == "POST":
        content = request.get_json(silent=True)
        print( f"content = {json.dumps(content)}" )
        columns = [ "sender_pk", "receiver_pk", "buy_currency", "sell_currency", "buy_amount", "sell_amount", "platform" ]
        fields = [ "sig", "payload" ]

        for field in fields:
            if not field in content.keys():
                print( f"{field} not received by Trade" )
                print( json.dumps(content) )
                log_message(content)
                return jsonify( False )

        for column in columns:
            if not column in content['payload'].keys():
                print( f"{column} not received by Trade" )
                print( json.dumps(content) )
                log_message(content)
                return jsonify( False )

        #Your code here
        #Note that you can access the database session using g.session
        sig = content['sig']
        payload = content['payload']
        sender_pk = content['payload']['sender_pk']
        receiver_pk = content['payload']['receiver_pk']
        buy_currency = content['payload']['buy_currency']
        sell_currency = content['payload']['sell_currency']
        buy_amount = content['payload']['buy_amount']
        sell_amount = content['payload']['sell_amount']
        platform = content['payload']['platform']

        # TODO: Check the signature
        if platform.lower() == 'ethereum':
            valid = verify_eth(payload, sig, sender_pk)
        if platform.lower() == 'algorand':
            valid = verify_algo(payload, sig, sender_pk)

        if valid == False:
            log_message(payload)
            return jsonify( False )

        # TODO: Add the order to the database
        # TODO: Fill the order order_filled = False
        order_filled = process_order(payload)

        # TODO: Be sure to return jsonify(True) or jsonify(False) depending on if the method was successful
        if order_filled == False: return jsonify ( False )

        return jsonify( True )

@app.route('/order_book')
def order_book():
    #Your code here
    #Note that you can access the database session using g.session
    query = g.session.query(Order)
    fields = ['buy_currency','sell_currency','buy_amount','sell_amount', 'signature', 'sender_pk', 'receiver_pk' ]
    result = { 'data': [{field:getattr(u, field) for field in fields} for u in query.all()]}

    return jsonify(result)

if __name__ == '__main__':
    app.run(port='5002')