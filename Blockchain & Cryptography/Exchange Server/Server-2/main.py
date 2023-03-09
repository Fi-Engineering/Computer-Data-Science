import order_book
# import test_orders

import random
import models
import validate


def main():
    # order = test_orders.make_order("Algorand")
    # order_book.process_order(order)

    # order = make_order("Ethereum")
    # order_book.process_order(order)
    validate.validate()


# def make_order(platform):
#     platforms = ["Algorand", "Ethereum"]
#     assert platform in platforms
#     other_platform = platforms[1 - platforms.index(platform)]
#     order = {}
#     order['buy_currency'] = other_platform
#     order['sell_currency'] = platform
#     order['buy_amount'] = random.randint(1, 10)
#     order['sell_amount'] = random.randint(1, 10)
#     order['sender_pk'] = hex(random.randint(0, 2 ** 256))[2:]
#     order['receiver_pk'] = hex(random.randint(0, 2 ** 256))[2:]
#     return order

main()
