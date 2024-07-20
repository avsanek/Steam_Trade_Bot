import time
import json

from typing import Union, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup, Tag

from func_sell import response_myhistory, take_assetid, take_item_nameid, calculate_price, sell_item, login_steam, \
    add_to_the_intermediate_base, update_base, save_steamLoginSecure, calculate_profit
from config_sell import start_zero_date, purchased_items, sold_items

while __name__ == "__main__":
    """The main point is to put purchased items on steam_market. But it also saves the amount of money 
    earned from each item, saves how much each CS_2 or Dota game has earned in total. 
    And stores in the database the current items for sale with their purchase price.
    """
	
    # Updates cookies every 12 hours and scans trade history
    if start_zero_date + timedelta(hours=12) < datetime.now():
        start_zero_date: datetime = datetime.now()
        steamLoginSecure_session: tuple[str, str] = login_steam('USERNAME_1', 'PASSWORD_1', 'two_key_1')
        steamLoginSecure, sessionid = steamLoginSecure_session
        save_steamLoginSecure(steamLoginSecure_session)
    response: dict[str: dict] = response_myhistory(steamLoginSecure, sessionid)
	
    """Here main objective it's check to changes trade history 
    and after we look this was a buy or sold item.
    """
    with open('main_base.json', 'r', encoding='utf-8') as file:
        our_total_count: dict[str, Union[int, dict, float]] = json.load(file)
        if our_total_count['total_count'] == "New_base":  # checking have whether new base
            update_base(our_total_count, response['total_count'], 'New')
            continue
        count_items_for_check: int = response['total_count'] - our_total_count['total_count']
        print('item for checking', count_items_for_check)
    # If there are changes in trade history, update our database.
    if count_items_for_check:
        if count_items_for_check < 500:
            update_base(our_total_count, response['total_count'], 'Old')
        elif count_items_for_check > 500:  # If there are too many changes (>500), clear the database.
            update_base(our_total_count, response['total_count'], 'New')
            time.sleep(15)
            continue
    else:
        time.sleep(15)
        continue  # If we don't have more a new transactions look again.

    """Depending on how many changes we've had in trade history, that's how many lines we'll check for buy and sell. 
    Adds bought and sold items to the intermediate databas
    """
    soup: BeautifulSoup = BeautifulSoup(response['results_html'], 'lxml')
    for row in soup.find_all('div', class_='market_recent_listing_row')[:count_items_for_check]:
        text_buy_or_sell_item: Tag = row.find('div', class_='market_listing_gainorloss').text.strip()
        if text_buy_or_sell_item in ['+', '-']:
            if text_buy_or_sell_item == '+':
                add_to_the_intermediate_base(row, purchased_items, response["assets"])
            else:
                add_to_the_intermediate_base(row, sold_items, response["assets"])

    if sold_items:  # Remove the sold items and calculate the profit.
        calculate_profit(sold_items, our_total_count)

    """Put the purchased item for sale, for this we need: 
    1) get assetid item from inventory for selling to market
    2) get item_nameid of item to calculate the price for selling
    3) calculate the price for selling
    4) put item to steam market place
    If all is successful, put the item into the database.
    """
    for item in purchased_items:
        item_name, item_price, item_game = item
        assetid: Optional[tuple[int, str]] = take_assetid(item_name, steamLoginSecure, sessionid, item_game)
        if assetid is None:
            continue
        assetid, market_hash_name = assetid
        item_nameid: str = take_item_nameid(market_hash_name, item_game)
        price_to_sell: Optional[str] = calculate_price(steamLoginSecure, sessionid, item_nameid, item_price, item_name)
        if price_to_sell is None:
            continue
        status_sell_item: Optional[bool] = sell_item(steamLoginSecure, sessionid, item_game, assetid, price_to_sell)
        if status_sell_item is True:
            if item_name not in our_total_count["assets"]:
                our_total_count["assets"].update({market_hash_name: [item_price]})
            else:
                our_total_count["assets"][market_hash_name].append(item_price)
            update_base(our_total_count)
            print(f'sell item {market_hash_name} for {price_to_sell}')
