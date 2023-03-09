from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random
import progressbar


def make_order(platform):
    platforms = ["Algorand", "Ethereum"]
    assert platform in platforms
    other_platform = platforms[1 - platforms.index(platform)]
    order = {}
    order['buy_currency'] = other_platform
    order['sell_currency'] = platform
    order['buy_amount'] = random.randint(1, 10)
    order['sell_amount'] = random.randint(1, 10)
    order['sender_pk'] = hex(random.randint(0, 2 ** 256))[2:]
    order['receiver_pk'] = hex(random.randint(0, 2 ** 256))[2:]
    return order


try:
    from order_book import process_order
except ImportError:
    print("Could not import 'process_order' from 'order_book.py'")

try:
    from models import Base, Order
except ImportError:
    print("Could not import 'Base,Order' from 'models.py'")

try:
    engine = create_engine('sqlite:///orders.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
except Exception as e:
    print("Could not create Session")
    print(e)

try:
    session.query(Order).delete()
    session.commit()
except Exception as e:
    print("Could not clear tables")
    print(e)


def validate():
    order_list = []
    num_failed = 0
    num_orders = 100
    print(f"Making {num_orders} transactions")
    bar = progressbar.ProgressBar(max_value=num_orders,
                                  widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    for i in range(num_orders):
        bar.update(i + 1)
        platforms = ["Algorand", "Ethereum"]
        order_dict = make_order(platforms[random.randint(0, 1)])
        order_list.append(order_dict)
        try:
            process_order(order_dict)
        except Exception as e:
            num_failed += 1
            continue
    bar.finish()

    for order in order_list:
        try:
            q = session.query(Order).filter(Order.buy_currency == order['buy_currency'])
            q = q.filter(Order.sell_currency == order['sell_currency'])
            q = q.filter(Order.sell_amount == order['sell_amount'])
            q = q.filter(Order.buy_amount == order['buy_amount'])
            q = q.filter(Order.sender_pk == order['sender_pk'])
            q = q.first()
            if not q:
                print("Error: submitted order was not found in the database")
                print(f"order['buy_currency'] = {order['buy_currency']}")
                print(f"order['sell_currency'] = {order['sell_currency']}")
                print(f"order['buy_amount'] = {order['buy_amount']}")
                print(f"order['sender_pk'] = {order['sender_pk']}")
        except Exception as e:
            continue

    print(f"Filled {session.query(Order).filter(Order.filled != None).count()} orders")

    num_tests = session.query(Order).filter(Order.filled != None).count()
    num_passed = 0

    # Adding points for fulfilling sufficient # of orders
    if num_tests > 10:
        num_passed += 5
    num_tests += 5

    orders = session.query(Order).filter(Order.filled != None)
    for order in orders:
        correct = True

        if order.counterparty is None:
            print("Error: filled order with no counterparty!")
            print(f"Order.id = {order.id}")
            continue
        else:
            print(f"Order.id = {order.id} has counterparty (Good)")
        if len(order.counterparty) > 1:
            print("Error: orders should have at most 1 counterparty")
            print(f"Order.id = {order.id} has {len(order.counterparty)} counterparties")
            continue
        else:
            print(f"Order.id = {order.id} has at most 1 counterparty (Good)")
        if order.timestamp < order.counterparty[0].timestamp:
            maker = order
            taker = order.counterparty[0]
        else:
            maker = order.counterparty[0]
            taker = order
        if maker.buy_currency != taker.sell_currency:
            print("Error: maker.buy_currency != taker.sell_currency!")
            print(f"maker.id = {maker.id}")
            print(f"taker.id = {taker.id}")
            correct = False
        else:
            print(f"maker.id = {maker.id} buy currency matches taker.id ={taker.id} sell currency (Good)")
        if maker.sell_currency != taker.buy_currency:
            print("Error: maker.sell_currency != taker.buy_currency!")
            print(f"maker.id = {maker.id}")
            print(f"taker.id = {taker.id}")
            correct = False
        else:
            print(f"maker.id = {maker.id} sell currency matches taker.id ={taker.id} buy currency (Good)")
        if maker.sell_amount == 0:
            print("Error: sell amount should never be 0")
            print(f"Order.id = {maker.id}")
            continue
        else:
            print(f"Sell amount for order.id = {maker.id} is non-zero (Good)")
        if taker.buy_amount == 0:
            print("Error: buy amount should never be 0")
            print(f"Order.id = {taker.id}")
            continue
        else:
            print(f"Sell amount for order.id = {taker.id} is non-zero (Good)")
        if maker.buy_amount / maker.sell_amount > taker.sell_amount / taker.buy_amount:
            print("Error: the exchange is losing money on this trade (bad implied exchange rate)")
            print(f"maker.id = {maker.id}")
            print(f"taker.id = {taker.id}")
            correct = False
        else:
            print(f"The exchange does not lose money on this trade (Good implied exchange rate)")
        if taker.buy_amount > maker.sell_amount:
            if not taker.child:
                print("Error: partially filled order should have a child")
                correct = False
            else:
                print("Partially filled order has a child (good)")
        if correct:
            num_passed += 1

    print("Assessing derivative orders (where order.creator_id exists)")
    orders = session.query(Order).filter(Order.creator_id != None)

    num_tests += session.query(Order).filter(Order.creator_id != None).count()

    for order in orders:
        correct = True
        if order.creator.sender_pk != order.sender_pk:
            print("Error: order and its creator should have the same sender_pk")
            correct = False
        else:
            print('Good: order and creator share same sender_pk')
        if order.creator.buy_currency != order.buy_currency:
            print("Error: order and its creator should have the same buy_currency")
            correct = False
        else:
            print("Good: order and its creator have the same buy_currency")
        if order.creator.sell_currency != order.sell_currency:
            print("Error: order and its creator should have the same sell_currency")
            correct = False
        else:
            print("Good: order and its creator have the same sell_currency")
        if order.creator.timestamp > order.timestamp:
            print("Error: order created before its creator")
            correct = False
        else:
            print("Good: order was created before its creator")
        if order.creator.buy_amount == 0:
            print("Error: buy amount should never be 0")
            print(f"Order.id = {order.creator.id}")
            continue
        else:
            print(f"Order.id = {order.creator.id}")
            print("Good: non-zero buy_amount")
        if order.creator.sell_amount == 0:
            print("Error: sell amount should never be 0")
            print(f"Order.id = {order.creator.id}")
            continue
        else:
            print("Good: non-zero sell_amount")
            print(f"Order.id = {order.creator.id}")
        if order.buy_amount / order.creator.buy_amount > order.sell_amount / order.creator.sell_amount + .01:  # Extra .01 is because of rounding errors
            print("Error: derived order has worse implied exchange rate")
            print(
                "Ensure that order.buy_amount/order.creator.buy_amount <= order.sell_amount/order.creator.sell_amount")
            print(
                f"{order.buy_amount:.2f}/{order.creator.buy_amount:.2f} > {order.sell_amount:.2f}/{order.creator.sell_amount:.2f}")
            print(
                f"{order.buy_amount / order.creator.buy_amount:.2f} > {order.sell_amount / order.creator.sell_amount:.2f}")
            print(f"Order.id = {order.id}")
            print(f"Creator.id = {order.creator.id}")
            correct = False
        else:
            print("Good: derived order has valid implied exchange rate")
            print(
                "Ensure that order.buy_amount/order.creator.buy_amount <= order.sell_amount/order.creator.sell_amount")
            print(
                f"{order.buy_amount:.2f}/{order.creator.buy_amount:.2f} <= {order.sell_amount:.2f}/{order.creator.sell_amount:.2f}")
            print(f"Order.id = {order.id}")
            print(f"Creator.id = {order.creator.id}")
        if correct:
            num_passed += 1

    print(f'\n-------\nYou passed {num_passed} tests out of {num_tests}\nScore={(num_passed / num_tests) * 100}')
    print("(note that the number of tests changes based on how many orders you fill)")

    eth_in = 0
    eth_out = 0
    algo_in = 0
    algo_out = 0

    # For all filled orders, the exchange takes in the "sell_amount" minus the "sell_amount" of its child,
    # and pays out the "buy_amount" minus the buy_amount of its child
    try:
        orders = session.query(Order).filter(Order.filled != "").all()
    except Exception as e:
        orders = []
    for order in orders:
        if order.sell_currency == "Algorand":
            algo_in += order.sell_amount
            algo_out += order.counterparty[0].buy_amount
            if order.counterparty[0].child:
                algo_out -= order.counterparty[0].child[0].buy_amount
            if order.child:
                algo_in -= order.child[0].sell_amount
        if order.sell_currency == "Ethereum":
            eth_in += order.sell_amount
            eth_out += order.counterparty[0].buy_amount
            if order.counterparty[0].child:
                eth_out -= order.counterparty[0].child[0].buy_amount
            if order.child:
                eth_in -= order.child[0].sell_amount

    print(f"Net profit (ETH) = {eth_in - eth_out:.2f}")
    print(f"Net profit (ALGO) = {algo_in - algo_out:.2f}")

    return (eth_in - eth_out), (algo_in - algo_out)
