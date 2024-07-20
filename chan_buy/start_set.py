import requests
import time
import io
import os
import traceback
import json
import re

from typing import Optional, Union
from datetime import datetime, timedelta
from bs4 import BeautifulSoup, Tag

from config_chan import take_headers, secondary_items, gray_items, secondary_gray_items, delete_gray_items, \
    item_nameid_dota, item_nameid_cs_go


def take_steamLoginSecure() -> tuple[str, str]:
    """Take steam cookies."""
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)
    file_path = os.path.join(parent_dir, 'steam_login.json')
    with open(file_path, 'r') as file:
        steamLoginSecure, sessionid = json.load(file)
    print('refresh steamLoginSecure')
    return steamLoginSecure, sessionid


def take_orders(steamLoginSecure: str, sessionid: str) -> list[list[str | float]]:
    """Get a complete list of orders, creates a list with the name of the item_name, game_name, price_name, order_id."""
    while True:
        start = 0
        items_orders = []
        try:
            url_orders = "https://steamcommunity.com/market/mylistings"
            querystring_orders = {"start": start, "count": "100"}
            headers_orders = take_headers(steamLoginSecure, sessionid, 'headers_orders')
            response = requests.request("GET", url_orders, headers=headers_orders, params=querystring_orders)
            if response.status_code != 200:
                print(f'response.status_code != 200 time.sleep(10) {response.status_code}')
                time.sleep(10)
                continue
            response_json = response.json()
            soup = BeautifulSoup(response_json['results_html'], 'lxml')
            items_orders_dirty = soup.find_all('div',
                                               class_='my_listing_section market_content_block market_home_listing_table')
            # Sometimes show block "My listings awaiting confirmation" and need pick another block with orders.
            for take_need_block in items_orders_dirty:
                block_name = take_need_block.find('span', class_='my_market_header_active').text.strip()
                if block_name == "My buy orders":
                    items_orders_dirty = take_need_block
            classes = ['market_listing_row', 'market_recent_listing_row']
            items_orders_dirty = items_orders_dirty.find_all('div', class_=classes)  # Receive every order.
            for item in items_orders_dirty:  # Clear every order and take need info.
                item_id = item.get('id').strip().replace("mybuyorder_", "")  # item_id is needed to delete an item.
                item_name = item.find(class_='market_listing_item_name_link').text.strip()
                if 'Unknown item:' in item_name:
                    item_name = item_name.replace("Unknown item: ", '')
                item_game = item.find(class_='market_listing_game_name').text.strip()
                item_price = item.find(class_='market_listing_price').contents[-1].text.strip()
                item_price = float(item_price.replace(",", ".").replace(" pуб.", ""))
                items_orders.append([item_name, item_game, item_price, item_id])
            return items_orders
        except (ValueError, requests.exceptions.ConnectionError):
            print('ValueError take_orders')
            time.sleep(10)
        except Exception:
            buffer = io.StringIO()
            traceback.print_exc(file=buffer)
            with open('errors.txt', 'a') as logi:
                logi.write(f"Error in take_orders, status_code {response}: {buffer.getvalue()}\n")
            traceback.print_exc()


def get_item(steamLoginSecure: str, sessionid: str, item_name: str, price_total: float, appid: int) -> bool:
    """Do a new order with a new price."""
    global secondary_items
    while True:
        try:
            url_get_item = "https://steamcommunity.com/market/createbuyorder"
            payload_get_item = f"sessionid={sessionid}&currency=5&appid={appid}&market_hash_name={item_name}&" \
                               f"price_total={price_total}&quantity=1&=billing_state%3D&save_my_address=0"
            headers_get_item = take_headers(steamLoginSecure, sessionid, 'headers_get_item')

            response = requests.request("POST", url_get_item, data=payload_get_item.encode('utf-8'),
                                        headers=headers_get_item)
            if response.status_code != 200:
                print(f"get_item != 200 {response.status_code} {item_name}")
                time.sleep(5)
                continue
            response_json = response.json()
            if response.status_code == 200 and response_json["success"] == 1:
                return response_json["success"]
            # If we have orders more than we can afford, we remove secondary_items.
            elif response.status_code == 200 and response_json["success"] == 25:
                if secondary_items == []:
                    return True
                secondary_items_to_remove = secondary_items[:10]
                secondary_items = secondary_items[10:]
                for item_to_remove in secondary_items_to_remove:
                    status_remove = remove_item(steamLoginSecure, sessionid, item_to_remove[0], item_to_remove[1])
                    print(f'пошло удаление {status_remove}')
            # We already have an active buy order for this item.
            elif response.status_code == 200 and response_json["success"] == 29:
                return True
            elif response.status_code == 200 and response_json["success"] in [16, 40]:
                time.sleep(5)
                print(f"Error in get_item {item_name}: {response_json}, response.status_code {response.status_code}\n")
                continue
            else:
                with open('errors.txt', 'a') as logi:
                    logi.write(
                        f"Error in get_item {item_name}: {response_json}, response.status_code {response.status_code}\n")
        except Exception:
            buffer = io.StringIO()
            traceback.print_exc(file=buffer)
            with open('errors.txt', 'a') as logi:
                logi.write(
                    f"Error in get_item: {buffer.getvalue()}, response.status_code {response.status_code}\n")
            traceback.print_exc()


def remove_item(steamLoginSecure: str, sessionid: str, buy_orderid: str, item_name: str) -> bool:
    """Delete an out-of-date order."""
    while True:
        try:
            url_remove_item = "https://steamcommunity.com/market/cancelbuyorder"
            payload_remove_item = f"sessionid={sessionid}&buy_orderid={buy_orderid}"
            headers_remove_item = take_headers(steamLoginSecure, sessionid, 'headers_remove_item')

            response = requests.request("POST", url_remove_item, data=payload_remove_item, headers=headers_remove_item)
            if response.status_code != 200:
                print(f"remove_item != 200 {response.status_code} {item_name}")
                time.sleep(5)
                continue
            response_json = response.json()
            if response.status_code == 200 and response_json["success"] == 1:
                return response_json["success"]
            elif response_json["success"] in [29, 79]:
                return True
            elif response_json["success"] in [16, 10]:  # Batched request timeout.
                print(response_json)
                continue
            else:
                with open('errors.txt', 'a') as logi:
                    logi.write(
                        f"Error in remove_item {item_name}: {response_json}, response.status_code {response.status_code}\n")
        except Exception:
            buffer = io.StringIO()
            traceback.print_exc(file=buffer)
            with open('errors.txt', 'a') as logi:
                logi.write(
                    f"Error in remove_item: {buffer.getvalue()}, response.status_code {response.status_code}\n")
            traceback.print_exc()


def take_item_nameid(item_name: str, game_name: str) -> Optional[str]:
    """Get item_nameid of item for checking price relevance."""
    while True:
        try:
            print(f'Check item{item_name}, {game_name}')
            if game_name == 'Dota 2':
                return item_nameid_dota[item_name]
            elif game_name == 'Counter-Strike 2':
                return item_nameid_cs_go[item_name]
        except KeyError:
            print(f"Error in take_item_nameid item {item_name, game_name} - continue")
            with open('errors.txt', 'a') as logi:
                logi.write(f"Error in take_item_nameid item {item_name, game_name} - continue \n")
            return None
        except Exception:
            buffer = io.StringIO()
            traceback.print_exc(file=buffer)
            with open('errors.txt', 'a') as logi:
                logi.write(f"Error in take_item_nameid: {buffer.getvalue()}\n")
            traceback.print_exc()
            return None


def buy_in_hour(cookies: str, name: str, game_id: int) -> Optional[Union[bool, int]]:
    """Does a statistical analysis of the thing, loads Api-item how many times this thing was bought in a day,
        if the purchases were not even, we don't buy this thing.
        """
    while True:
        try:
            coookies = {'steamLoginSecure': cookies}
            link = f"https://steamcommunity.com/market/pricehistory/?country=DE&currency=3&appid={game_id}&" \
                   f"market_hash_name={name}"
            response = requests.get(link, cookies=coookies)
            if response.status_code == 500:
                return False
            elif response.status_code != 200:
                continue
            site = response.json()
            if site == []:
                continue
            data_1 = site['prices'][-25:]
            now = datetime.now()
            interval = now - timedelta(hours=27)
            interval = interval.replace(minute=0, second=0, microsecond=0)
            for i in data_1:
                if interval >= datetime.strptime(i[0][0:14], '%b %d %Y %H'):
                    index = data_1.index(i)
                else:
                    break

            data = data_1[index + 1:]
            all_item = sum([int(i[2]) for i in data])
            solo_items = [int(i[2]) for i in data]
            procent_items = [round(i / (all_item / 100), 2) for i in solo_items]
            if any(i > 20 for i in procent_items):
                return False
            return all_item
        except Exception:
            buffer = io.StringIO()
            traceback.print_exc(file=buffer)
            with open('errors.txt', 'a') as logi:
                logi.write(f"Error in buy_in_hour: {buffer.getvalue()} , response {response}\n")
            return None


def game_id(game_name: str) -> int:
    """Get game_id of the game."""
    if game_name == 'Dota 2':
        return 570
    elif game_name == 'Counter-Strike 2':
        return 730


def coef_game(game_name: str, price_item: float) -> list[float | str]:
    """Settings for the range of analyzing the item for each item: 1) From how many cents the item costs
    2) From how many percent not to remove the order 3) From how many percent to move the order
    4) From how many rubles profit we are satisfied with 5) status for analyzing the item."""
    if game_name == 'Dota 2':
        spisoc_range_Dota = [[50, 1.4, 1.7, 0.85, 'procent'],
                             [40, 0.5, 0.6, 0.85, 'numbers'],
                             [30, 0.4, 0.5, 0.85, 'numbers'],
                             [0, 0.3, 0.4, 0.85, 'numbers']]
        for coef_range in spisoc_range_Dota:
            if coef_range[0] <= price_item:
                return coef_range[1:]
    elif game_name == 'Counter-Strike 2':
        spisoc_range_Cs = [[50, 2.2, 2.5, 1.25, 'procent'],
                           [40, 0.8, 0.9, 1.25, 'numbers'],
                           [30, 0.65, 0.75, 1.25, 'numbers'],
                           [0, 0.5, 0.6, 1.25, 'numbers']]
        for coef_range in spisoc_range_Cs:
            if coef_range[0] <= price_item:
                return coef_range[1:]


def change_price(item_price: float) -> str:
    """Api_steam after point of price always to do 2 number and we need to do samething."""
    price_for_sell = str(item_price).split('.')
    if len(price_for_sell[-1]) == 1:
        price_for_sell[-1] = price_for_sell[-1] + '0'
    price_for_sell = ''.join(price_for_sell)
    return price_for_sell


def new_order(current_order_item: float, profit: float, min_prof: float) -> float:
    """Calculates the premium price for placing a new order."""
    dop_price = profit // min_prof
    if dop_price < 1:
        dop_price = 0.05
    elif dop_price <= 11:
        dop_price = 0.1 * dop_price
    else:
        dop_price = 0.1 * 11
    new_order_ = round(current_order_item + dop_price, 2)
    return new_order_


def coef_day_and_sell_items(response_json: dict[str, Union[str, int]], steamLoginSecure: str, item_name: str,
                            game_name: str) -> Union[float, bool]:
    """My custom analysis of the thing.
    Divide the number of available items on the market by the number of items sold in a day.
    """
    try:
        all_sell_items_dirty = re.search(r'>(\d+)<', response_json['sell_order_summary'])
        all_sell_items = int(all_sell_items_dirty.group(1))
        per_day = buy_in_hour(steamLoginSecure, item_name, game_id(game_name))
        if per_day is False:
            return False
        coef_day_and_sell_items = round(all_sell_items / per_day, 2)
        return coef_day_and_sell_items
    except Exception:
        buffer = io.StringIO()
        traceback.print_exc(file=buffer)
        with open('errors.txt', 'a') as logi:
            logi.write(f"Error in coef_day_and_sell_items - return 1.5: {buffer.getvalue()}\n")
        return 1.5


def relevance_of_item(response_json: dict[str, Union[str, int]], price_item: float, min_coef: float,
                      steamLoginSecure: str, sessionid: str, buy_orderid: str, item_name: str, game_name: str,
                      status_coef: str, Status: Optional[str] = None) -> bool:
    """If the order with the price becomes not more profitable than the 3rd thing to sell,
    then remove the order, otherwise leave it.
    """
    for sell_order in response_json['sell_order_graph']:
        if sell_order[1] >= 3:
            price_without_taxe = round(sell_order[0] / 1.15, 2)
            profit = round(price_without_taxe - price_item, 2)
            coef_profit = profit
            if status_coef == 'procent':
                coef_profit = round(profit / (price_item / 100), 2)
            if coef_profit < min_coef:  # If current profit less "min_coef" - clearing the order.
                print(f'Убираем coef_profit {coef_profit} < {min_coef} ')
                gray_items.append([item_name, game_name])
                return remove_item(steamLoginSecure, sessionid, buy_orderid, item_name)
            else:
                print(f'Оставляем coef_profit {coef_profit} > {min_coef} ')
                if Status == 'base_off':  # Add to base not relevant of items to when need kick them.
                    print('В базу на отмену')
                    if [buy_orderid, item_name] not in secondary_items:
                        secondary_items.append([buy_orderid, item_name])
                return True


def rearranging_the_item(response_json: dict[str, Union[str, int]], current_order_item: float, max_coef: float,
                         price_item: float, min_coef: float, steamLoginSecure: str, sessionid: str, buy_orderid: str,
                         item_name: str, min_prof: float, game_name: str, status_coef: str, check_till: int) -> bool:
    """The function checks goods for profitability.
    Rearranges the order if the order is profitable: deletes the old one and puts up a new one.
    """
    for sell_order in response_json['sell_order_graph']:
        price_without_taxe = round(sell_order[0] / 1.15, 2)
        profit = round(price_without_taxe - current_order_item, 2)
        coef_profit = profit
        if status_coef == 'procent':
            coef_profit = round(profit / (current_order_item / 100), 2)
        if coef_profit >= max_coef:
            print(f'Переставляем {coef_profit} >= {max_coef}')
            # If we found a good item with good profit we remove old order.
            remove_item_status = remove_item(steamLoginSecure, sessionid, buy_orderid, item_name)
            if remove_item_status == 1:
                new_order_ = new_order(current_order_item, profit, min_prof)
                change_price_ = change_price(new_order_)
                return get_item(steamLoginSecure, sessionid, item_name, change_price_, game_id(game_name))
            break
        # If haven't profit - check profit with old price.
        if sell_order[1] >= check_till:
            print(f'Нету {max_coef} %')
            return relevance_of_item(response_json, price_item, min_coef, steamLoginSecure, sessionid, buy_orderid,
                                     item_name, game_name, status_coef, Status='base_off')


def calculate_relevance(steamLoginSecure: str, sessionid: str, item_nameid: str, price_item: float, game_name: str,
                        item_name: str, buy_orderid: str) -> bool:
    """Checks the order for relevance, looks at the statistical analysis of the thing,
    checks if our order is not overbought by more than 0.04 rubles and
    chooses an algorithm for evaluating the order based on its purchase demand.
    """
    url_item = "https://steamcommunity.com/market/itemordershistogram"
    querystring_item = {"country": "RU", "language": "english", "currency": "5", "item_nameid": item_nameid,
                        "two_factor": "0"}
    headers_item = take_headers(steamLoginSecure, sessionid, 'headers_item')
    while True:
        try:
            response = requests.request("GET", url_item, headers=headers_item, params=querystring_item)
            response_json = response.json()
            if response_json["success"] in [16, 10]:  # Bad response
                continue
            current_order_item = response_json['buy_order_graph'][0][0]  # First sell_order of item.
            min_coef, max_coef, min_prof, status_coef = coef_game(game_name, current_order_item)
            my_order = round(price_item + 0.04, 2)
            coef_day_and_sell_items_ = coef_day_and_sell_items(response_json, steamLoginSecure, item_name, game_name)
            if coef_day_and_sell_items_ is False:
                print("coef_day_and_sell_items_ > 35 remove_item")
                return remove_item(steamLoginSecure, sessionid, buy_orderid, item_name)

            if my_order < current_order_item:
                if coef_day_and_sell_items_ <= 1.2:  # If coef less 1.2 then we use a less strict algorithm.
                    print('Меньше 1.2 кф', coef_day_and_sell_items_)
                    return rearranging_the_item(response_json, current_order_item, max_coef, price_item, min_coef,
                                                steamLoginSecure, sessionid, buy_orderid, item_name, min_prof,
                                                game_name, status_coef, check_till=3)
                else:
                    print('Больше 1.2 кф', coef_day_and_sell_items_)
                    return rearranging_the_item(response_json, current_order_item, max_coef, price_item, min_coef,
                                                steamLoginSecure, sessionid, buy_orderid, item_name, min_prof,
                                                game_name, status_coef, check_till=1)
            else:
                return relevance_of_item(response_json, price_item, min_coef, steamLoginSecure, sessionid, buy_orderid,
                                         item_name, game_name, status_coef)

        except (ConnectionResetError, requests.exceptions.ConnectionError, TimeoutError):
            print('ConnectionResetError def error we good processed')
            time.sleep(10)
        except Exception:
            buffer = io.StringIO()
            traceback.print_exc(file=buffer)
            with open('errors.txt', 'a') as logi:
                logi.write(
                    f"Error in calculate_relevance: {buffer.getvalue()}, response.status_code {response.status_code} "
                    f"response {response.text}\n")
            traceback.print_exc()
            return None


def response_myhistory(steamLoginSecure: str, sessionid: str) -> dict[str: dict]:
    """Get json myhistory trade."""
    url_myhistory = "https://steamcommunity.com/market/myhistory"
    querystring_myhistory = {"count": "500"}
    headers_myhistory = take_headers(steamLoginSecure, sessionid, 'headers_myhistory')
    while True:
        try:
            response = requests.request("GET", url_myhistory, headers=headers_myhistory, params=querystring_myhistory)
            response = response.json()
            if response['assets'] == []:
                print('response_myhistory durit')
                time.sleep(5)
                continue
            return response
        except (ConnectionResetError, ConnectionError, requests.exceptions.JSONDecodeError,
                requests.exceptions.ConnectionError):
            print('ConnectionResetError def error')
            buffer = io.StringIO()
            traceback.print_exc(file=buffer)
            with open('errors.txt', 'a') as logi:
                logi.write(f"ConnectionResetError def error in response_myhistory: {buffer.getvalue()}\n")
            time.sleep(30)
        except Exception:
            buffer = io.StringIO()
            traceback.print_exc(file=buffer)
            with open('errors.txt', 'a') as logi:
                logi.write(f"Error in response_myhistory: {buffer.getvalue()}\n")
            traceback.print_exc()
            time.sleep(30)


def relevance_of_gray(response_json: dict[str, Union[str, int]], current_order_item: float, min_coef: float,
                      item_name: str, game_name: str, status_coef: str, Status_remove: Optional[str] = None,
                      Status: Optional[str] = None) -> bool:
    """Checks an order that was recently removed,
    leaves it to be checked if its price is not lower than the 7th thing on the list, otherwise removes it.
    """
    for sell_order in response_json['sell_order_graph']:
        if sell_order[1] >= 7:
            price_without_taxe = round(sell_order[0] / 1.15, 2)
            profit = price_without_taxe - current_order_item
            coef_profit = profit
            if status_coef == 'procent':
                coef_profit = round(profit / (current_order_item / 100), 2)
            if coef_profit < min_coef:
                print(f'Убираем coef_profit {coef_profit} < {min_coef} ')
                if Status_remove == "do it":  # We memorize gray item which need to delete.
                    delete_gray_items.append([item_name, game_name])
                return True
            else:
                print(f'Оставляем coef_profit {coef_profit} > {min_coef} ')
                if Status == 'base_off':  # Add to base of gray items with min_profit (we check them after).
                    secondary_gray_items.append([item_name, game_name])
                return True


def rearranging_the_gray(response_json: dict[str, Union[str, int]], current_order_item: float, max_coef: float,
                         min_coef: float, steamLoginSecure: str, sessionid: str, item_name: str, min_prof: float,
                         game_name: str, Status_remove: str, Status: str, status_coef: str, check_till: int) -> bool:
    """The function checks the recently deleted gray item for profitability, if so, we place an order."""
    for sell_order in response_json['sell_order_graph']:
        price_without_taxe = round(sell_order[0] / 1.15, 2)
        profit = round(price_without_taxe - current_order_item, 2)
        coef_profit = profit
        if status_coef == 'procent':
            coef_profit = round(profit / (current_order_item / 100), 2)
        # If have profit -  get order.
        if coef_profit >= max_coef:
            print(f'Переставляем {coef_profit} >= {max_coef}')
            new_order_ = new_order(current_order_item, profit, min_prof)
            change_price_ = change_price(new_order_)
            if Status_remove == "do it":  # We memorize gray item which need to delete.
                delete_gray_items.append([item_name, game_name])
            return get_item(steamLoginSecure, sessionid, item_name, change_price_, game_id(game_name))
        # If haven't profit - check profit for min profit to stay it's item.
        if sell_order[1] >= check_till:
            print(f'Нету {max_coef} %')
            return relevance_of_gray(response_json, current_order_item, min_coef, item_name, game_name, status_coef,
                                     Status_remove, Status)


def calculate_relevance_gray(steamLoginSecure: str, sessionid: str, item_nameid: str, game_name: str, item_name: str,
                             Status_remove: Optional[str] = None, Status: Optional[str] = None) -> Optional[bool]:
    """Checks the order for relevance, looks at the statistical analysis of the thing and
    chooses an algorithm for evaluating the order based on its purchase demand.
    """
    url_item = "https://steamcommunity.com/market/itemordershistogram"
    querystring_item = {"country": "RU", "language": "english", "currency": "5", "item_nameid": item_nameid,
                        "two_factor": "0"}
    headers_item = take_headers(steamLoginSecure, sessionid, 'headers_item')
    while True:
        try:
            response = requests.request("GET", url_item, headers=headers_item, params=querystring_item)
            response_json = response.json()
            if response_json["success"] == 16:  # Bad response.
                continue
            current_order_item = response_json['buy_order_graph'][0][0]  # First sell_order of item.
            min_coef, max_coef, min_prof, status_coef = coef_game(game_name, current_order_item)
            print(item_name, game_name, current_order_item)
            coef_day_and_sell_items_ = coef_day_and_sell_items(response_json, steamLoginSecure, item_name, game_name)
            if coef_day_and_sell_items_ is False and Status_remove == 'do it':
                delete_gray_items.append([item_name, game_name])
                return True
            elif not coef_day_and_sell_items_ and Status_remove == 'base_off':
                return True
            # If coef less 1.2 then we use a less strict algorithm.
            if coef_day_and_sell_items_ <= 1.2:
                print('Меньше 1.2 кф', coef_day_and_sell_items_)
                return rearranging_the_gray(response_json, current_order_item, max_coef, min_coef, steamLoginSecure,
                                            sessionid, item_name, min_prof, game_name, Status_remove, Status,
                                            status_coef, check_till=3)
            else:
                print('Больше 1.2 кф', coef_day_and_sell_items_)
                return rearranging_the_gray(response_json, current_order_item, max_coef, min_coef, steamLoginSecure,
                                            sessionid, item_name, min_prof, game_name, Status_remove, Status,
                                            status_coef, check_till=1)

        except (ConnectionResetError, TimeoutError, requests.exceptions.ConnectionError):
            buffer = io.StringIO()
            traceback.print_exc(file=buffer)
            with open('errors.txt', 'a') as logi:
                logi.write(
                    f"Error in calculate_relevance_gray - we good processed: {buffer.getvalue()}, "
                    f"response.status_code {response.status_code}\n")
            traceback.print_exc()
            print('we good processed')
            time.sleep(10)
        except Exception:
            buffer = io.StringIO()
            traceback.print_exc(file=buffer)
            with open('errors.txt', 'a') as logi:
                logi.write(
                    f"Error in calculate_relevance_gray: {buffer.getvalue()}, response.status_code {response.status_code}\n")
            traceback.print_exc()
            return None


def hash_items(purchased_sold_items: list[str], response: dict[str: dict], game_name: str) -> list[str]:
    """We get a name with a hash name, because the inventory gives a name without a hash name."""
    count = 0
    max_count = len(purchased_sold_items) - 1
    hash_items_ = []
    for item_history_info in response['assets'][str(game_id(game_name))]['2'].values():
        if item_history_info['status'] == 4 and item_history_info['name'] == purchased_sold_items[count]:
            hash_items_.append(item_history_info['market_hash_name'])
            count += 1
            if max_count < count:
                break
    return hash_items_


def update_base(our_total_count, total_count=None) -> None:
    """Updates the database by changing the number of transactions."""
    our_total_count['total_count'] = total_count
    with open('main_base.json', 'w', encoding='utf-8') as file:
        json.dump(our_total_count, file, ensure_ascii=False)


def check_gray_items(steamLoginSecure: str, sessionid: str, start: float, time_to_sleep: float) -> bool:
    """Check recently deleted orders for profit: either place the order, leave it or remove it from the selection."""
    global delete_gray_items, secondary_gray_items
    print(gray_items, 'gray_items')
    for gray_item in gray_items:
        calculate_relevance_gray(steamLoginSecure, sessionid, take_item_nameid(gray_item[0], gray_item[1]),
                                 gray_item[1], gray_item[0], Status_remove='do it')
        print(f'Time gray_items: {(time.time() - start):.03f}s')
        time.sleep(time_to_sleep)

    for delete_item in delete_gray_items:  # Delete used gray items.
        gray_items.pop(gray_items.index(delete_item))
    delete_gray_items = []

    for secondary_gray_item in secondary_gray_items:
        gray_items.append(secondary_gray_item)
    secondary_gray_items = []

    return True


def check_sell_or_buy_items(steamLoginSecure: str, sessionid: str, start: float, time_to_sleep: float) -> bool:
    """Checks recently bought and sold items for benefits and places an order."""
    response = response_myhistory(steamLoginSecure, sessionid)
    with open('main_base.json', 'r', encoding='utf-8') as file:
        our_total_count = json.load(file)
        count_items_for_check = response['total_count'] - our_total_count['total_count']
        if count_items_for_check:
            if count_items_for_check < 500:
                update_base(our_total_count, response['total_count'])
            elif count_items_for_check > 500:  # If there are too many changes (>500), clear the database.
                update_base(our_total_count, response['total_count'])
                return True
        else:
            return True

    """Depending on how many changes we've had in trade history, that's how many lines we'll check for buy and sell. 
    Adds bought and sold items to the intermediate databas
    """
    soup: Tag = BeautifulSoup(response['results_html'], 'lxml')
    purchased_sold_dota: list[str] = []
    purchased_sold_cs: list[str] = []
    for row in soup.find_all('div', class_='market_recent_listing_row')[:count_items_for_check]:
        text_buy_or_sell_item = row.find('div', class_='market_listing_gainorloss').text.strip()
        if text_buy_or_sell_item in ['+', '-']:
            item_name = row.find('span', class_='market_listing_item_name').text.strip()
            item_game_name = row.find('span', class_='market_listing_game_name').text.strip()
            if item_game_name == 'Dota 2':
                purchased_sold_dota.append(item_name)
            elif item_game_name == 'Counter-Strike 2':
                purchased_sold_cs.append(item_name)

    hash_dota_items, hash_cs_items = [], []
    count_for_game = 0
    # Api_history have 2 different column about that need work apart with dota and cs items.
    for purchased_sold_items in (purchased_sold_dota, purchased_sold_cs):
        count_for_game += 1
        if purchased_sold_items:
            if count_for_game == 1:
                hash_dota_items = hash_items(purchased_sold_items, response, 'Dota 2')
            elif count_for_game == 2:
                hash_cs_items = hash_items(purchased_sold_items, response, 'Counter-Strike 2')

    hash_dota_items, hash_cs_items = list(set(hash_dota_items)), list(set(hash_cs_items))  # Delete same items.
    hash_dota_items = [[item, 'Dota 2'] for item in hash_dota_items]  # Add to item him game_name.
    hash_cs_items = [[item, 'Counter-Strike 2'] for item in hash_cs_items]
    print(hash_dota_items, hash_cs_items, 'hash_dota_cs_items')
    # This is where cleared bought and sold items are tested for profit.
    for hash_gray_items in (hash_dota_items, hash_cs_items):
        for hash_gray_item in hash_gray_items:
            calculate_relevance_gray(steamLoginSecure, sessionid,
                                     take_item_nameid(hash_gray_item[0], hash_gray_item[1]), hash_gray_item[1],
                                     hash_gray_item[0], Status='base_off')
            print(f'Time hash_dota_cs_items: {(time.time() - start):.03f}s')
            time.sleep(time_to_sleep)
    return True
