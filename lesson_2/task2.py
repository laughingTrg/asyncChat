import json
from datetime import datetime


JSON_FILE_NAME = "orders.json"


def write_order_to_json(
        item: str = None,
        quantity: int = None,
        price: float = None,
        buyer: str = None,
        date: str = str(datetime.now())) -> None:

    if all([item,
            quantity,
            price,
            buyer,
            date]):

        order = {
            'item': item,
            'quantity': quantity,
            'price': price,
            'buyer': buyer,
            'date': date
        }

        with open(JSON_FILE_NAME, 'r') as f_o:
            orders = json.load(f_o)

        with open(JSON_FILE_NAME, 'w') as f_o:
            orders['orders'].append(order)
            json.dump(orders, f_o, sort_keys=True, indent=4)


    return


write_order_to_json(item='Носки', quantity=1, price=10.0, buyer='Петр')
