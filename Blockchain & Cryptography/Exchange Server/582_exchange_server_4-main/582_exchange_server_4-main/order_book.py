# uncompyle6 version 3.7.4
# Python bytecode 3.6 (3379)
# Decompiled from: Python 3.8.5 (default, Sep  4 2020, 02:22:02) 
# [Clang 10.0.0 ]
# Embedded file name: /home/codio/workspace/order_book.py
# Compiled at: 2020-12-16 20:18:46
# Size of source mod 2**32: 4254 bytes
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from models import Base, User, Order
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

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
        if order.creator_id is not None:
            pass
        return True


def process_order(order):
    order_dict = dict(order)
    order_dict['user_id'] = get_user_id(order)
    del order_dict['pk']
    del order_dict['platform']
    if order_dict['buy_amount'] == 0:
        print('Error in process_order: buy_amount cannot be 0')
        return []
    else:
        if order_dict['sell_amount'] == 0:
            print('Error in process_order: sell_amount cannot be 0')
            return []
        new_order = Order(**order_dict)
        session.add(new_order)
        session.commit()
        return fill_order(new_order)


def fill_order(order, txes=[]):
    if not is_valid(order):
        print('fill order received an invalid order')
        return txes
    eo = session.query(Order)
    eo = eo.filter(Order.filled == None)
    eo = eo.filter(Order.buy_currency == order.sell_currency).filter(Order.sell_currency == order.buy_currency)
    eo = eo.filter(Order.sell_amount / Order.buy_amount >= order.buy_amount / order.sell_amount)
    eo = eo.order_by(Order.buy_amount / Order.sell_amount).first()
    if eo is not None:
        eo.filled = datetime.now()
        order.filled = datetime.now()
        fields = ['user_id', 'buy_currency', 'sell_currency', 'buy_amount', 'sell_amount']
        order.counterparty_id = eo.id
        eo.counterparty_id = order.id
        new_txes = []
        new_txes.append(make_tx(eo.buy_currency, eo.user.pk, min(order.sell_amount, eo.buy_amount)))
        new_txes.append(make_tx(order.buy_currency, order.user.pk, min(order.buy_amount, eo.sell_amount)))
        if order.sell_amount < eo.buy_amount:
            new_order = Order(**)
            new_order.buy_amount -= order.sell_amount
            new_order.sell_amount = (1 - float(order.sell_amount) / eo.buy_amount) * eo.sell_amount
            new_order.creator_id = eo.id
            session.add(new_order)
        if eo.sell_amount < order.buy_amount:
            new_order = Order(**)
            new_order.buy_amount -= eo.sell_amount
            new_order.sell_amount = (1 - float(eo.sell_amount) / order.buy_amount) * order.sell_amount
            new_order.creator_id = order.id
            session.add(new_order)
            session.commit()
            return fill_order(new_order, txes=(txes + new_txes))
        else:
            session.commit()
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


def get_user_id(order):
    assert 'pk' in order.keys()
    user = session.query(User).filter(User.pk == str(order['pk'])).first()
    if user is None:
        user = User(pk=(order['pk']), platform=(order['platform']))
        session.add(user)
        session.commit()
    return user.id
# okay decompiling order_book.cpython-36.pyc
