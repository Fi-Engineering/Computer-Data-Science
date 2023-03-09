from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
from models import Base, Order
from datetime import datetime

# from starter code
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def process_order(order): #from starter code
    order_init = create_order(order)
    commit_order(order_init)
    match_order(order_init)
   
'''
Insert the order into the database
– Insert the order into the “order” table. Make sure you set the following fields:
“buy_currency”
“sell_currency”
“buy_amount”
“sell_amount”
“sender_pk”
“receiver_pk”
'''
   
def create_order(order_dictionary):
    order_dict = Order()
    order_dict.buy_currency = order_dictionary['buy_currency'] #buy_currency
    order_dict.sell_currency = order_dictionary['sell_currency'] #sell_currency
    order_dict.buy_amount = order_dictionary['buy_amount'] #buy_amount
    order_dict.sell_amount = order_dictionary['sell_amount'] #sell_amount
    order_dict.sender_pk = order_dictionary['sender_pk'] #sender_pk
    order_dict.receiver_pk = order_dictionary['receiver_pk'] #receiver_pk
   
    return order_dict

def commit_order(order_init):
    session.add(order_init)
    session.commit()


'''
Check if there are any existing orders that match. Given new_order and existing order, to match all of the following requirements must be fulfilled:
existing_order.filled must be None
existing_order.buy_currency == order.sell_currency
existing_order.sell_currency == order.buy_currency
The implied exchange rate of the new order must be at least that of the existing order (existing_order.sell_amount / existing_order.buy_amount
>= order.buy_amount/order.sell_amount)
The buy / sell amounts need not match exactly
Each order should match at most one other
'''

def match_order(order_object):
    buy = order_object.buy_currency
    sell = order_object.sell_currency
    exchange_rate = order_object.buy_amount / order_object.sell_amount
    query = session.query(Order).filter(Order.buy_currency == sell, Order.sell_currency == buy, and_(Order.filled.is_(None),(Order.sell_amount / Order.buy_amount) >= exchange_rate)).first()
    update_orders(order_object, query)



'''
If a match is found between order and existing_order:
– Add a record to the Matches table including the ids of the two matching orders. The “maker” is the existing order, the “taker” is the new order
– Set the filled field to be the current timestamp on both orders
– Set counterparty_id to be the id of the other order
– If one of the orders is not completely filled (i.e. the counterparty’s sell_amount is less than buy_amount):
Create a new order for remaining balance
The new order should have the created_by field set to the id of its parent order
The new order should have the same pk and platform as its parent order
The sell_amount of the new order can be any value such that the implied exchange rate of the new order is at least that of the old order
You can then try to fill the new order
'''


'''
Each order matches at most one other (to match one order against multiple others create derivative orders, and set the “created_by” field as described above)
Any derived orders must have an implied exchange rate that is at least the original exchange rate, i.e.,
buy_amount/sell_amount on the new order must be at least the buy_amount/sell_amount on the order that created it

'''

def update_orders(current_order, existing_order):
    current_order.counterparty_id= existing_order.id
    existing_order.counterparty_id= current_order.id
    existing_order.filled = datetime.now()
    current_order.filled = datetime.now()
   

    buy_amount = current_order.buy_amount
    sell_amount = existing_order.sell_amount

    if sell_amount < buy_amount: # check other way around
        #new_buy_amount = buy_amount - sell_amount
        new_sell_amount = current_order.sell_amount - existing_order.buy_amount
        new_buy_amount = existing_order.buy_amount - current_order.sell_amount
        #new_buy_amount = current_order.buy_amount - existing_order.sell_amount
        #new_sell_amount = new_buy_amount
   
       
        # check derivatives
        der_order = Order()
        der_order.buy_amount = new_buy_amount
        der_order.sell_amount = new_sell_amount
        der_order.creator_id = current_order.id
        #der_order.creator_id = existing_order.id
        der_order.sell_currency = current_order.sell_currency
        der_order.buy_currency = current_order.buy_currency
        der_order.sender_pk = current_order.sender_pk
        der_order.receiver_pk = current_order.receiver_pk
        #existing_order.child = der_order.id
        session.add(der_order)
        session.commit()
        session.close()
       
        get_order = session.query(Order).filter(Order.creator.id == current_order.id)
        current_order.child = get_order.id #set child field on parent order
        #existing_order.child = get_order.id #set child field on parent order
        session.commit()
        match_order(der_order)
        session.close()    
   
    if sell_amount > buy_amount:
        #new_buy_amount = sell_amount - buy_amount
        #new_sell_amount = current_order.sell_amount - existing_order.buy_amount
        new_buy_amount = exisitng_order.buy_amount - current_order.sell_amount
        new_sell_amount = current_order.sell_amount - existing_order.buy_amount
         # check derivatives
        der_order = Order()
        der_order.buy_amount = new_buy_amount
        der_order.sell_amount = new_sell_amount
        der_order.creator_id = current_order.id
        #der_order.creator_id = existing_order.id
        der_order.sell_currency = current_order.sell_currency
        der_order.buy_currency = current_order.buy_currency
        der_order.sender_pk = current_order.sender_pk
        der_order.receiver_pk = current_order.receiver_pk

        session.add(der_order)
        session.commit()
        session.close()
       
        get_order = session.query(Order).filter(Order.creator.id == current_order.id)
        current_order.child = get_order.id
        session.commit()
        match_order(der_order)
        session.close()   

