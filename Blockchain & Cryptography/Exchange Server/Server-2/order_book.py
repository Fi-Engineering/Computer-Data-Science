from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from sqlalchemy import and_

from datetime import datetime

from models import Base, Order

engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def process_order(order):
    # create an order object from order arg (dict)
    order_obj = create_order_obj(order)

    # add the order object to the db
    add_order_to_book(order_obj)

    # print count of items in db
    find_matching_order(order_obj)


# add the order to the db and commit the add
def add_order_to_book(order_obj):
    session.add(order_obj)
    session.commit()
    # print(type(order))


# method to convert the order from a dict format to an Order object
def create_order_obj(order_dict):
    order_obj = Order()
    order_obj.sender_pk = order_dict['sender_pk']
    order_obj.receiver_pk = order_dict['receiver_pk']
    order_obj.buy_amount = order_dict['buy_amount']
    order_obj.sell_amount = order_dict['sell_amount']
    order_obj.buy_currency = order_dict['buy_currency']
    order_obj.sell_currency = order_dict['sell_currency']

    return order_obj


def find_matching_order(order_obj):
    # get the sell currency amount from the order obj
    order_sell_currency = order_obj.sell_currency
    order_buy_currency = order_obj.buy_currency
    order_exchange_rate = order_obj.buy_amount / order_obj.sell_amount

    # query the database and match an unfilled order's buy currently with the sell currency of the current order
    q = session.query(Order).filter(and_(Order.filled.is_(None), Order.buy_currency == order_sell_currency,
                                         Order.sell_currency == order_buy_currency,
                                         (Order.sell_amount / Order.buy_amount) >= order_exchange_rate)).first()
    if q.id == None: return

    update_matched_orders(order_obj, q)


def update_matched_orders(current_order_obj, existing_order_obj):
    # update the the filled field for both objects to be the current timestamp
    current_order_obj.filled = datetime.now()
    existing_order_obj.filled = datetime.now()

    # set counterparty_id for both orders
    current_order_obj.counterparty_id = existing_order_obj.id
    existing_order_obj.counterparty_id = current_order_obj.id

    # check if current order buy amount > counterparty sell amount
    current_order_buy_amount = current_order_obj.buy_amount
    existing_order_sell_amount = existing_order_obj.sell_amount

    if current_order_buy_amount > existing_order_sell_amount:
        # create derivative order object
        derivative_order = Order()

        # get the buy/sell amount differences
        diff_buy_amt = current_order_buy_amount - existing_order_sell_amount
        diff_sell_amt = current_order_obj.sell_amount - existing_order_obj.buy_amount

        # update object fields of the derivative order
        derivative_order.creator_id = current_order_obj.id
        derivative_order.buy_currency = current_order_obj.buy_currency
        derivative_order.sell_currency = current_order_obj.sell_currency
        derivative_order.sell_amount = diff_sell_amt
        derivative_order.buy_amount = diff_buy_amt
        derivative_order.receiver_pk = current_order_obj.receiver_pk
        derivative_order.sender_pk = current_order_obj.sender_pk

        # add derivative order to the db and commit changes
        session.add(derivative_order)
        session.commit()

        # get the id of the newly created derivative order
        get_recently_committed_order = session.query(Order).filter(Order.creator_id == current_order_obj.id)

        current_order_obj.child = get_recently_committed_order.id
        session.commit()

        # try and find a matching order for the derivative order
        find_matching_order(derivative_order)


def print_db():
    for instance in session.query(Order).order_by(Order.receiver_pk):
        print("receiver_pk: ", instance.receiver_pk)
        print("buy_currency: ", instance.buy_currency)
        print("filled: ", instance.filled)
