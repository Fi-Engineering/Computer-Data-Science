from flask import Flask, request, g
from flask_restful import Resource, Api
from sqlalchemy import create_engine
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


""" helper methods """
def is_valid(order):
    if order.buy_amount <= 0 or order.sell_amount <= 0:
        return False
    return True


def check_sig(payload,sig):
    valid = False
    platform = payload['platform']
    sender_pk = payload['sender_pk']
    if platform.lower() == 'ethereum':
        valid = verify_eth(payload, sig, sender_pk)
    elif platform.lower() == 'algorand':
        valid = verify_algo(payload, sig, sender_pk)
    return valid


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


def fill_order(order, txes=[]):
    if is_valid(order) == False:
        log_message(order)
        return txes

    order_query = g.session.query(Order)
    order_query = order_query.filter(Order.filled == None)
    order_query = order_query.filter(Order.buy_currency == order.sell_currency).filter(Order.sell_currency == order.buy_currency)
    order_query = order_query.filter(Order.sell_amount / Order.buy_amount >= order.buy_amount / order.sell_amount)
    order_query = order_query.order_by(Order.buy_amount / Order.sell_amount).first()

    if order_query is not None:
        order_query.filled = datetime.now()
        order.filled = datetime.now()
        fields = ['buy_currency', 'sell_currency', 'buy_amount', 'sell_amount']
        order.counterparty_id = order_query.id
        order_query.counterparty_id = order.id
        new_txes = []
        new_txes.append(make_tx(order_query.buy_currency, min(order.sell_amount, order_query.buy_amount)))
        new_txes.append(make_tx(order.buy_currency, min(order.buy_amount, order_query.sell_amount)))

        if order.sell_amount < order_query.buy_amount:
            new_order = Order()
            new_order.buy_amount -= order.sell_amount
            new_order.sell_amount = (1 - float(order.sell_amount) / order_query.buy_amount) * order_query.sell_amount
            new_order.creator_id = order_query.id
            g.session.add(new_order)
        if order_query.sell_amount < order.buy_amount:
            new_order = Order()
            new_order.buy_amount -= order_query.sell_amount
            new_order.sell_amount = (1 - float(order_query.sell_amount) / order.buy_amount) * order.sell_amount
            new_order.creator_id = order.id
            g.session.add(new_order)
            g.session.commit()
            return fill_order(new_order, txes=(txes + new_txes))
        else:
            g.session.commit()
            return txes + new_txes


def make_tx(platform, amount):
    if platform.lower() == 'algorand':
        return make_tx_algo(amount)
    if platform.lower() == 'ethereum':
        return make_tx_eth(amount)


def make_tx_algo(platform, amount):
    tx = {'sender':'exchange',  'amount':amount,  'platform':'Algorand'}
    return tx


def make_tx_eth(platfrom, amount):
    tx = {'sender':'exchange','amount':amount, 'platform':'Ethereum'}
    return tx

# method to create an order object using the JSON content
def create_order(content):
    new_order = Order()
    new_order.signature = content['sig']
    new_order.payload = content['payload']
    new_order.sender_pk = content['payload']['sender_pk']
    new_order.receiver_pk = content['payload']['receiver_pk']
    new_order.buy_currency = content['payload']['buy_currency']
    new_order.sell_currency = content['payload']['sell_currency']
    new_order.buy_amount = content['payload']['buy_amount']
    new_order.sell_amount = content['payload']['sell_amount']
    new_order.platform = content['payload']['platform']

    return new_order

def log_message(d):
    # Takes input dictionary d and writes it to the Log table
    # Hint: use json.dumps or str() to get it in a nice string form
    log = Log()
    log.payload = json.dumps(d)
    g.session.add(log)
    g.session.commit()


def process_order(order):
    order_dict = dict(order)
    order_dict['signature'] = order_dict.pop('sig')
    if order_dict['payload']['buy_amount'] == 0:
        print('Error in process_order: buy_amount cannot be 0')
        return []
    else:
        if order_dict['payload']['sell_amount'] == 0:
            print('Error in process_order: sell_amount cannot be 0')
            return []
        new_order = create_order(order)
        g.session.add(new_order)
        g.session.commit()
        return fill_order(new_order)

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
        payload = content['payload']
        sig = content['sig']
        # TODO: Check the signature
        valid_signature = check_sig(payload, sig)

        # TODO: Add the order to the database
        if valid_signature == False:
            log_message(payload)
            return jsonify ( False )
        else:
            process_order(content)
            current_order = create_order(content)

        # TODO: Fill the order
        order_filled = fill_order(current_order)
        print("order_filled: ", order_filled)
        # TODO: Be sure to return jsonify(True) or jsonify(False) depending on if the method was successful
        return jsonify(True)

@app.route('/order_book')
def order_book():
   #Your code here
    #Note that you can access the database session using g.session
    query = g.session.query(Order)
    fields = ['buy_currency','sell_currency','buy_amount','sell_amount', 'signature', 'sender_pk', 'receiver_pk', ]

    result = [{field:getattr(u,field)for field in fields} for u in query.all()]

    return jsonify(result)

if __name__ == '__main__':
    app.run(port='5002')