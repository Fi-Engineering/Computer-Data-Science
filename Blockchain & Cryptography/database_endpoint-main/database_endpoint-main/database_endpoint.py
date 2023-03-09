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

# starter code
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

"""
-------- Helper methods (feel free to add your own!) -------
"""
def log_message(d):
    log = Log()
    log.d = payload
    return log

"""
---------------- Endpoints ----------------
"""
# starter code start  
@app.route('/trade', methods=['POST'])
def trade():
    if request.method == "POST":
        content = request.get_json(silent=True)
        print( f"content = {json.dumps(content)}" )
        columns = [ "sender_pk", "receiver_pk", "buy_currency", "sell_currency", "buy_amount", "sell_amount", "platform" ]
        fields = [ "sig", "payload" ]
        error = False
        for field in fields:
            if not field in content.keys():
                print( f"{field} not received by Trade" )
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
        #starter code end    
        #Your code here. Note that you can access the database session using g.session
       
        sig = content['sig']
        payload = content['payload']
        buy_amount = content['payload']['buy_amount']
        sell_amount = content['payload']['sell_amount']
        buy_currency = content['payload']['buy_currency']
        sell_currency = content['payload']['sell_currency']
        sender_pk = content['payload']['sender_pk']
        receiver_pk = content['payload']['receiver_pk']
       
        platform = content['payload']['platform']
        
        if platform.lower() == 'algorand':
            valid = algorand(payload, sig, sender_pk)
        if platform.lower() == 'ethereum':
            valid = ethereum(payload, sig, sender_pk)
            
        if valid == False:
            invalid = log_message(content)
            g.session.add(invalid)
            g.session.commit()
            g.session.close()
            
        if valid == True:
            valid = new_order(sender_pk, receiver_pk, buy_currency, sell_currency, buy_amount, sell_amount, sig)
            g.session.add(valid)
            g.session.commit()
            g.session.close()
                  
        return jsonify(True)



def algorand(payload, sig, sender_pk):
    algo_message = json.dumps(payload)
    if algosdk.util.verify_bytes(algo_message.encode('utf-8'),sig,sender_pk):
        return True
   

def ethereum(payload, sig, sender_pk):
    eth_message = json.dumps(payload)
    eth_encoded_message = eth_account.messages.encode_defunct(text=eth_message)
    if eth_account.Account.recover_message(eth_encoded_message,signature=sig) == sender_pk:
        return True
   

def new_order( sender_pk, receiver_pk, buy_currency, sell_currency, buy_amount, sell_amount, sig):
    order = Order()
    order.sender_pk = sender_pk
    order.receiver_pk = receiver_pk
    order.buy_currency = buy_currency
    order.sell_currency = sell_currency
    order.buy_amount = buy_amount
    order.sell_amount = sell_amount
    order.signature = sig
    return order

@app.route('/order_book')
def order_book():
    #Your code here. Note that you can access the database session using g.session
    query = g.session.query(Order)
    dictionary = [ "sender_pk", "receiver_pk", "buy_currency", "sell_currency", "buy_amount", "sell_amount", "signature" ]
    end = { 'data': [{field:getattr(i, field) for field in dictionary} for i in query.all()] }
    return jsonify(end)

if __name__ == '__main__':
    app.run(port='5002')
