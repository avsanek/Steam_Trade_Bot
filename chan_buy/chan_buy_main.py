import time

from typing import Optional
from datetime import datetime, timedelta

from start_set import take_orders, take_item_nameid, calculate_relevance, check_sell_or_buy_items, check_gray_items, \
    take_steamLoginSecure
from config_chan import start_zero_date, start, count_gray_items, time_to_sleep

while __name__ == "__main__":
    """The main task is to keep the orders up to date: either update the price or remove them altogether. 
    It also keeps orders that are weakly relevant, which can give profit, but in case of a large number of orders, 
    it will cancel them. And also memorize recently canceled orders to check them in the future.
    And most importantly, it keeps track of the orders that worked and puts them out again!
    """
    # Updates cookies every 8 hours
    if start_zero_date + timedelta(hours=8) < datetime.now():
        start_zero_date = datetime.now()
        steamLoginSecure, sessionid = take_steamLoginSecure()
    """Gets the list of current orders, searches through them: 
    gets item_nameid for access to api-price and checks the order itself.
    """
    items_orders: list[list[str | float]] = take_orders(steamLoginSecure, sessionid)
    for item in items_orders:
        item_name, item_game, item_price, item_id = item
        item_nameid: Optional[str] = take_item_nameid(item_name, item_game)
        if item_nameid is None:
            continue
        calculate_relevance_: bool = calculate_relevance(steamLoginSecure, sessionid, item_nameid, item_price,
                                                         item_game, item_name, item_id)
        print(f'Working time: {(time.time() - start):.03f}s, item_name: {item_name}, Status: {calculate_relevance_}')
        time.sleep(time_to_sleep)  # Dillay is needed to avoid getting micro-banned 429.

    # Checks what items have been bought and sold to place an order on them.
    check_sell_or_buy_items_: bool = check_sell_or_buy_items(steamLoginSecure, sessionid, start, time_to_sleep)
    # Here we check canceled orders for relevance once in a while.
    count_gray_items += 1
    if count_gray_items == 2:
        check_gray_items_: bool = check_gray_items(steamLoginSecure, sessionid, start, time_to_sleep)
        count_gray_items = 0
