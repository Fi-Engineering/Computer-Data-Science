from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random
import progressbar

def make_order(platform):
    platforms = ["Algorand", "Ethereum"]
    assert platform in platforms
    other_platform = platforms[1-platforms.index(platform)]
    order = {}
    order['platform'] = platform
    order['buy_currency'] = other_platform
    order['sell_currency'] = platform
    order['buy_amount'] = random.randint(1,10)
    order['sell_amount'] = random.randint(1,10)
    order['pk'] = hex(random.randint(0,2**256))[2:] 
    return order

try:
    from order_book import process_order
except ImportError:
    print( "Could not import 'process_order' from 'order_book.py'" )

try:
    from models import Base, User, Order
except ImportError:
    print( "Could not import 'Base,User,Order' from 'models.py'" )

try:
    engine = create_engine('sqlite:///orders.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
except Exception as e:
    print( "Could not create Session" )
    print( e )

try:
    session.query(Order).delete()
    session.query(User).delete()
    session.commit()
except Exception as e:
    print( "Could not clear tables" )
    print( e )

def validate():
    order_list = [] 
    num_orders=100
    print( f"Making {num_orders} transactions" )
    bar = progressbar.ProgressBar(max_value=num_orders, widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    for i in range(num_orders):
        bar.update(i+1)
        platforms = ["Algorand", "Ethereum"]
        order_dict = make_order( platforms[random.randint(0,1)] )
        order_list.append(order_dict)
        process_order(order_dict)
    bar.finish()

    for order in order_list:
        q = session.query(Order).filter(Order.buy_currency==order['buy_currency'])
        q = q.filter(Order.sell_currency==order['sell_currency'])
        q = q.filter(Order.sell_amount==order['sell_amount'])
        q = q.filter(Order.buy_amount==order['buy_amount'])
        q = q.filter(Order.user.has(platform=order['platform']))
        q = q.filter(Order.user.has(pk=order['pk']))
        q = q.first()
        if not q:
            print( "Error: order was not properly inserted" )

    print( f"Filled {session.query(Order).filter(Order.filled != None).count()} orders" )

    orders = session.query(Order).filter(Order.filled != None )
    for order in orders:
        if order.counterparty is None:
            print( "Error: filled order with no counterparty!" )
            print( f"Order.id = {order.id}" )
            continue
        if len(order.counterparty) > 1:
            print( "Error: orders should have at most 1 counterparty" )
            print( f"Order.id = {order.id}" )
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
        if maker.sell_currency != taker.buy_currency:
            print( "Error: maker.sell_currency != taker.buy_currency!" )
            print( f"maker.id = {maker.id}" )
            print( f"taker.id = {taker.id}" )
        if maker.sell_amount == 0:
            print( "Error: sell amount should never be 0" )
            print( f"Order.id = {maker.id}" )
            continue
        if taker.buy_amount == 0:
            print( "Error: buy amount should never be 0" )
            print( f"Order.id = {taker.id}" )
            continue
        if maker.buy_amount/maker.sell_amount > taker.sell_amount/taker.buy_amount:
            print( "Error: the exchange is losing money on this trade" )
            print( f"maker.id = {maker.id}" )
            print( f"taker.id = {taker.id}" )
        if taker.buy_amount > maker.sell_amount:
            if not taker.child:
                print( "Error: partially filled order should have a child" )

    orders = session.query(Order).filter(Order.creator_id != None)
    for order in orders:
        if order.creator.user_id != order.user_id:
            print( "Error: order and its creator should have the same user_id" )
        if order.creator.buy_currency != order.buy_currency:
            print( "Error: order and its creator should have the same buy_currency" )
        if order.creator.sell_currency != order.sell_currency:
            print( "Error: order and its creator should have the same sell_currency" )
        if order.creator.timestamp > order.timestamp:
            print( "Error: order created befor its creator" )
        if order.creator.buy_amount == 0:
            print( "Error: buy amount should never be 0" )
            print( f"Order.id = {order.creator.id}" )
            continue
        if order.creator.sell_amount == 0:
            print( "Error: sell amount should never be 0" )
            print( f"Order.id = {order.creator.id}" )
            continue
        if order.buy_amount/order.creator.buy_amount > order.sell_amount/order.creator.sell_amount + .01: #Extra .01 is because of rounding errors
            print( "Error: derived order has worse implied exchange rate" )
            print( f"{order.buy_amount:.2f}/{order.creator.buy_amount:.2f} > {order.sell_amount:.2f}/{order.creator.sell_amount:.2f}" )
            print( f"{order.buy_amount/order.creator.buy_amount:.2f} > {order.sell_amount/order.creator.sell_amount:.2f}" )
            print( f"Order.id = {order.id}" )
            print( f"Creator.id = {order.creator.id}" )

    eth_in = 0
    eth_out = 0
    algo_in = 0
    algo_out = 0

    #For all filled orders, the exchange takes in the "sell_amount" minus the "sell_amount" of its child, and pays out the "buy_amount" minus the buy_amount of its child
    orders = session.query(Order).filter(Order.filled != "").all()
    for order in orders:
        if order.sell_currency == "Algorand":
            algo_in += order.sell_amount 
            eth_out += order.counterparty[0].buy_amount
            if order.counterparty[0].child:
                eth_out -= order.counterparty[0].child[0].buy_amount
            if order.child:
                algo_in -= order.child[0].sell_amount
        if order.sell_currency == "Ethereum":
            eth_in += order.sell_amount
            algo_out += order.counterparty[0].buy_amount 
            if order.counterparty[0].child:
                algo_out -= order.counterparty[0].child[0].buy_amount
            if order.child:
                eth_in -= order.child[0].sell_amount

    print( f"Net profit (ETH) = {eth_in-eth_out:.2f}" )
    print( f"Net profit (ALGO) = {algo_in-algo_out:.2f}" )

    return (eth_in-eth_out),(algo_in-algo_out)

