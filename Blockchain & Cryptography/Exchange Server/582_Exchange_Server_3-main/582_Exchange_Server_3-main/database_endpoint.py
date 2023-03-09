from flask import Flask, request, g
from flask_restful import Resource, Api
from sqlalchemy import create_engine, select, MetaData, Table
from flask import jsonify
import json
import eth_account
import algosdk
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import load_only

from models import Base, Order, Log
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

app = Flask(__name__)

#These decorators allow you to use g.session to access the database inside the request code
@app.before_request
def create_session():
    g.session = scoped_session(DBSession) #g is an "application global" https://flask.palletsprojects.com/en/1.1.x/api/#application-globals

@app.teardown_appcontext
def shutdown_session(response_or_exc):
    g.session.commit()
    g.session.remove()

@app.route('/trade', methods=['POST'])
def trade():
    if request.method == "POST":
        content = request.get_json(silent=True)
        print( f"content = {json.dumps(content)}" )
        columns = [ "sender_pk", "receiver_pk", "buy_currency", "sell_currency", "buy_amount", "sell_amount" ]
        fields = [ "sig", "payload" ]
        error = False
        for field in fields:
            if not field in content.keys():
                print( f"{field} not received by Trade" )
                error = True
        if error:
            print( json.dumps(content) )
            log_message(content)
            return jsonify( False )

        error = False
        for column in columns:
            if not column in content['payload'].keys():
                print( f"{column} not received by Trade" )
                error = True
        if error:
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

        valid = None

        if platform.lower() == 'ethereum':
            valid = verify_eth(payload, sig, sender_pk)
        elif platform.lower() == 'algorand':
            valid = verify_algo(payload, sig, sender_pk)

        if valid == True:
            valid_order = create_order(sender_pk, receiver_pk, buy_currency, sell_currency, buy_amount, sell_amount, sig)
            g.session.add(valid_order)
            g.session.commit()
        else:
            invalid_order = create_log(content)
            g.session.add(invalid_order)
            g.session.commit()


def verify_eth(payload, sig, sender_pk):
    msg = json.dumps(payload)
    # encode the payload
    eth_encoded_msg = eth_account.messages.encode_defunct(text=msg)
    # sign the payload using sender_pk
    # eth_sig_obj = eth_account.Account.sign_message(eth_encoded_msg, sender_pk)
    # verify signed payload matches the signature
    # test = payload['pk']
    if eth_account.Account.recover_message(eth_encoded_msg,signature=sig) == sender_pk:
        return True
    else:
        return False

def verify_algo(payload, sig, sender_pk):

    msg = json.dumps(payload)
    # encode the payload
    # payload_encode = payload.encode('utf-8')
    # verify signed payload matches sig
    if algosdk.util.verify_bytes(msg.encode('utf-8'),sig,sender_pk):
        return True
    else:
        return False

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

def create_log(payload):
    log = Log()
    log.payload = payload
    return log

@app.route('/order_book')
def order_book():
    #Your code here
    #Note that you can access the database session using g.session
    query = g.session.query(Order)

    fields = [ "sender_pk", "receiver_pk", "buy_currency", "sell_currency", "buy_amount", "sell_amount", "signature" ]

    result = { 'data': [{field:getattr(u, field) for field in fields} for u in query.all()] }

    return jsonify(result)


if __name__ == '__main__':
    app.run(port='5002')
