import requests
import time
import io
import os
import traceback
import json

from bs4 import Tag
from dotenv import load_dotenv
from typing import Optional, Union
import steam.webauth as wa
from steam.webauth import WebAuthException
from steam_totp import generate_twofactor_code_for_time

from config_sell import take_headers, item_nameid_dota, item_nameid_cs_go


def login_steam(USERNAME: str, PASSWORD: str, two_key: str) -> tuple[str, str]:
    """Logs on to Steam and gets a cookie."""
    while True:
        try:
            load_dotenv()
            auth = wa.WebAuth(os.getenv(USERNAME), os.getenv(PASSWORD))
            steam_Code = generate_twofactor_code_for_time(shared_secret=os.getenv(two_key))
            session = auth.login(code=steam_Code)
            steamLoginSecure = session.cookies.__dict__['_cookies']["store.steampowered.com"]["/"][
                "steamLoginSecure"].value
            sessionid = session.cookies.__dict__['_cookies']["store.steampowered.com"]["/"]["sessionid"].value
            return steamLoginSecure, sessionid
        except WebAuthException:
            buffer = io.StringIO()
            traceback.print_exc(file=buffer)
            with open('errors.txt', 'a') as logi:
                logi.write(f'WebAuthException in login_steam: {buffer.getvalue()} \n')
            traceback.print_exc()
            time.sleep(30)
        except Exception:
            buffer = io.StringIO()
            traceback.print_exc(file=buffer)
            with open('errors.txt', 'a') as logi:
                logi.write(f'Error in login_steam: {buffer.getvalue()} \n')
            traceback.print_exc()
            time.sleep(30)


def save_steamLoginSecure(steamLogin_session: tuple[str, str]) -> None:
    """Save steam cookies."""
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)
    file_path = os.path.join(parent_dir, 'steam_login.json')
    with open(file_path, 'w') as file:
        json.dump(steamLogin_session, file)
    print(f'Save steamLogin success{steamLogin_session}')


def get_hash_item_name(item_name: str, item_game_name: str, response: dict[str: dict]) -> str:
    """We get a name with a hash name, because the inventory gives a name without a hash name."""
    for id_item in response[item_game_name]['2'].values():
        if id_item['status'] == 4 and id_item['name'] == item_name:
            return id_item["market_hash_name"]


def add_to_the_intermediate_base(row: Tag, current_base: list[str], response: dict[str: dict]) -> None:
    """Add to the intermediate data_base purchased or sold item."""
    item_name = row.find('span', class_='market_listing_item_name').text.strip()
    item_game_name = row.find('span', class_='market_listing_game_name').text.strip()
    item_name_hash = get_hash_item_name(item_name, game_id(item_game_name), response)
    item_price = row.find('span', class_='market_listing_price').text.strip()
    item_price = float(item_price.replace(",", ".").replace(" pуб.", ""))
    item_info = [item_name_hash, item_price, item_game_name]
    print(item_info[0], item_info[1])
    current_base.append(item_info)


def update_base(our_total_count: dict[str, Union[int, dict, float]], total_count: Optional[int] = None,
                status: Optional[str] = None) -> None:
    """Updates the database by changing the number of transactions or updating the entire database."""
    if status == 'Old':
        our_total_count['total_count'] = total_count
    elif status == 'New':
        our_total_count['total_count'] = total_count
        our_total_count['assets'] = {}
        our_total_count['make_money'] = 0
    with open('main_base.json', 'w', encoding='utf-8') as file:
        json.dump(our_total_count, file, ensure_ascii=False)


def game_id(game_name: str) -> str:
    """Get game_id of the game."""
    if game_name == 'Dota 2':
        return '570'
    elif game_name == 'Counter-Strike 2':
        return '730'


def response_myhistory(steamLoginSecure: str, sessionid: str) -> dict[str: dict]:
    """Get json myhistory trade."""
    url_myhistory = "https://steamcommunity.com/market/myhistory"
    querystring_myhistory = {"count": "500"}
    headers_myhistory = take_headers(steamLoginSecure, sessionid, "headers_myhistory")
    while True:
        try:
            response = requests.request("GET", url_myhistory, headers=headers_myhistory, params=querystring_myhistory)
            response = response.json()
            if response['assets'] == []:
                time.sleep(61)
                continue
            return response
        except (ConnectionResetError, requests.exceptions.ConnectionError):
            print('ConnectionResetError def error')
            time.sleep(10)
        except Exception:
            buffer = io.StringIO()
            traceback.print_exc(file=buffer)
            with open('errors.txt', 'a') as logi:
                logi.write(f"Error in response_myhistory: {buffer.getvalue()}\n")
            traceback.print_exc()
            time.sleep(30)


def take_assetid(item: str, steamLoginSecure: str, sessionid: str, game_name: str) -> Optional[tuple[int, str]]:
    """Get assetid item from inventory for selling to market."""
    url_inventory = f"https://steamcommunity.com/inventory/76561198091105943/{game_id(game_name)}/2"
    querystring_inventory = {"count": "2000", "market": "1"}
    headers_inventory = take_headers(steamLoginSecure, sessionid, "headers_inventory")
    try:
        while True:
            response = requests.request("GET", url_inventory, headers=headers_inventory, params=querystring_inventory)
            if response.status_code == 500:
                time.sleep(2)
                continue
            response = response.json()
            for info_inventory_item in response["descriptions"]:
                if "market_hash_name" in info_inventory_item:
                    if info_inventory_item["market_hash_name"] == item:
                        index_inventory_item = response["descriptions"].index(info_inventory_item)
                        print(f'assetid {response["assets"][index_inventory_item]["assetid"]}')
                        return response["assets"][index_inventory_item]["assetid"], info_inventory_item[
                            "market_hash_name"]
            return None
    except Exception:
        buffer = io.StringIO()
        traceback.print_exc(file=buffer)
        with open('errors.txt', 'a') as logi:
            logi.write(f"Error in take_assetid: {buffer.getvalue()}\n")
        traceback.print_exc()


def take_item_nameid(item_name: str, game_name: str) -> str:
    """Get item_nameid of item for calculate the price for selling."""
    try:
        if game_name == 'Dota 2':
            print(f'item_nameid {item_nameid_dota[item_name]}')
            return item_nameid_dota[item_name]
        elif game_name == 'Counter-Strike 2':
            print(f'item_nameid {item_nameid_cs_go[item_name]}')
            return item_nameid_cs_go[item_name]
    except Exception:
        buffer = io.StringIO()
        traceback.print_exc(file=buffer)
        with open('errors.txt', 'a') as logi:
            logi.write(f"Error in take_item_nameid: {buffer.getvalue()}\n")
        traceback.print_exc()


def change_price(item_price: float) -> str:
    """Api_steam after point of price always to do 2 number and we need to do samething."""
    price_for_sell = item_price - 0.01  # for example 7.1 need to do 7.10
    price_for_sell = round(price_for_sell, 2)
    price_for_sell = str(price_for_sell).split('.')
    if len(price_for_sell[-1]) == 1:
        price_for_sell[-1] = price_for_sell[-1] + '0'
    price_for_sell = ''.join(price_for_sell)
    return price_for_sell


def calculate_profit(sold_items: list[str], our_total_count: dict[str, list[str]]) -> None:
    """Deletes sold items from the database, calculates the profit total and game-specific and updates the database."""
    for item in sold_items:
        item_name, item_price, item_game = item
        if item_name in our_total_count["assets"]:
            if len(our_total_count["assets"][item_name]) == 1:
                our_total_count["make_money"] = our_total_count["make_money"] + item_price - \
                                                our_total_count["assets"][item_name][0]
                if item_game == 'Dota 2':
                    our_total_count["Dota 2"] = our_total_count["Dota 2"] + item_price - \
                                                our_total_count["assets"][item_name][0]
                elif item_game == 'Counter-Strike 2':
                    our_total_count["Counter-Strike 2"] = our_total_count["Counter-Strike 2"] + item_price - \
                                                          our_total_count["assets"][item_name][0]
                our_total_count["assets"].pop(item_name, None)
            else:
                our_total_count["make_money"] = our_total_count["make_money"] + item_price - max(
                    our_total_count["assets"][item_name])
                if item_game == 'Dota 2':
                    our_total_count["Dota 2"] = our_total_count["Dota 2"] + item_price - max(
                        our_total_count["assets"][item_name])
                elif item_game == 'Counter-Strike 2':
                    our_total_count["Counter-Strike 2"] = our_total_count["Counter-Strike 2"] + item_price - max(
                        our_total_count["assets"][item_name])
                index_max_item = our_total_count["assets"][item_name].index(max(our_total_count["assets"][item_name]))
                our_total_count["assets"][item_name].pop(index_max_item)
    update_base(our_total_count)


def calculate_price(steamLoginSecure: str, sessionid: str, item_nameid: str, price_item: float, item_name: str) \
        -> Optional[str]:
    """Calculate price for selling."""
    # Don't pay attention to the design, there was a lot of fine work here,
    # It was important for me to make it work correctly, because it's working with money.
    url_item = "https://steamcommunity.com/market/itemordershistogram"
    querystring_item = {"country": "RU", "language": "english", "currency": "5", "item_nameid": item_nameid,
                        "two_factor": "0"}
    headers_item = take_headers(steamLoginSecure, sessionid, "headers_item")
    try:
        while True:
            response = requests.request("GET", url_item, headers=headers_item, params=querystring_item)
            response = response.json()
            if response["success"] == 16:  # bad response
                continue
            last_count = 0
            sell_order_graph = response['sell_order_graph']
            for item_prices in sell_order_graph:
                count_current_prices = item_prices[1] - last_count
                last_count = item_prices[1]
                price_without_taxe = round(item_prices[0] / 1.15, 2)
                profit = round(price_without_taxe - price_item, 2)
                print(count_current_prices, item_prices[0], round(item_prices[0] / 1.15, 2), round(profit, 2))
                if profit > 0:
                    if profit >= 0.5:
                        if count_current_prices >= 3:
                            print(item_prices, f'item_name: {item_name}')
                            print(
                                f'counts: {count_current_prices}, price {item_prices[0]}, price_without_taxe '
                                f'{price_without_taxe}, price_item {price_item}, profit {profit} > 0.5 if '
                                f'count_current_prices >= 3: first')
                            return change_price(price_without_taxe)
                        elif count_current_prices == 2:
                            need_index = sell_order_graph.index(item_prices) + 1
                            second_price_without_taxe = round(sell_order_graph[need_index][0] / 1.15, 2)
                            second_profit = round(second_price_without_taxe - price_item, 2)
                            if profit * 3.24 <= second_profit:
                                print(item_prices, sell_order_graph[need_index], f'item_name: {item_name}')
                                return change_price(second_price_without_taxe)
                            else:
                                print(item_prices, sell_order_graph[need_index], f'item_name: {item_name}')
                                return change_price(price_without_taxe)
                        elif count_current_prices == 1:
                            need_index = sell_order_graph.index(item_prices) + 1
                            second_count = sell_order_graph[need_index][1] - last_count
                            if second_count >= 2:
                                second_price_without_taxe = round(sell_order_graph[need_index][0] / 1.15, 2)
                                second_profit = round(second_price_without_taxe - price_item, 2)
                                if profit * 1.8 <= second_profit:
                                    print(item_prices, sell_order_graph[need_index], f'item_name: {item_name}')
                                    return change_price(second_price_without_taxe)
                                else:
                                    print(item_prices, sell_order_graph[need_index], f'item_name: {item_name}')
                                    return change_price(price_without_taxe)
                            elif second_count == 1:
                                second_price_without_taxe = round(sell_order_graph[need_index][0] / 1.15, 2)
                                second_profit = round(second_price_without_taxe - price_item, 2)
                                if profit * 1.8 <= second_profit:
                                    third_price_without_taxe = round(sell_order_graph[need_index + 1][0] / 1.15, 2)
                                    profit_third = round(third_price_without_taxe - price_item, 2)
                                    if second_profit * 1.8 <= profit_third:
                                        print(item_prices, sell_order_graph[need_index],
                                              sell_order_graph[need_index + 1], f'item_name: {item_name}')
                                        return change_price(third_price_without_taxe)
                                    else:
                                        print(item_prices, sell_order_graph[need_index],
                                              sell_order_graph[need_index + 1], f'item_name: {item_name}')
                                        return change_price(second_price_without_taxe)
                                else:
                                    third_price_without_taxe = round(sell_order_graph[need_index + 1][0] / 1.15, 2)
                                    profit_third = round(third_price_without_taxe - price_item, 2)
                                    if profit * 3.24 <= profit_third:
                                        print(item_prices, sell_order_graph[need_index],
                                              sell_order_graph[need_index + 1], f'item_name: {item_name}')
                                        return change_price(third_price_without_taxe)
                                    else:
                                        print(item_prices, sell_order_graph[need_index],
                                              sell_order_graph[need_index + 1], f'item_name: {item_name}')
                                        return change_price(price_without_taxe)
                    elif profit < 0.5:
                        if count_current_prices >= 3:
                            print(item_prices, f'item_name: {item_name}')
                            return change_price(price_without_taxe)
                        elif count_current_prices == 2:
                            need_index = sell_order_graph.index(item_prices) + 1
                            second_price_without_taxe = round(sell_order_graph[need_index][0] / 1.15, 2)
                            second_profit = round(second_price_without_taxe - price_item, 2)
                            if second_profit >= 0.9:
                                print(item_prices, sell_order_graph[need_index], f'item_name: {item_name}')
                                return change_price(second_price_without_taxe)
                            else:
                                print(item_prices, sell_order_graph[need_index], f'item_name: {item_name}')
                                return change_price(price_without_taxe)
                        elif count_current_prices == 1:
                            need_index = sell_order_graph.index(item_prices) + 1
                            second_count = sell_order_graph[need_index][1] - last_count
                            if second_count >= 2:
                                second_price_without_taxe = round(sell_order_graph[need_index][0] / 1.15, 2)
                                second_profit = round(second_price_without_taxe - price_item, 2)
                                if second_profit >= 0.5:
                                    print(item_prices, sell_order_graph[need_index], f'item_name: {item_name}')
                                    return change_price(second_price_without_taxe)
                                else:
                                    print(item_prices, sell_order_graph[need_index], f'item_name: {item_name}')
                                    return change_price(price_without_taxe)
                            elif second_count == 1:
                                second_price_without_taxe = round(sell_order_graph[need_index][0] / 1.15, 2)
                                second_profit = round(second_price_without_taxe - price_item, 2)
                                if second_profit >= 0.5:
                                    third_price_without_taxe = round(sell_order_graph[need_index + 1][0] / 1.15, 2)
                                    profit_third = round(third_price_without_taxe - price_item, 2)
                                    if second_profit * 1.8 <= profit_third:
                                        print(item_prices, sell_order_graph[need_index],
                                              sell_order_graph[need_index + 1], f'item_name: {item_name}')
                                        return change_price(third_price_without_taxe)
                                    else:
                                        print(item_prices, sell_order_graph[need_index],
                                              sell_order_graph[need_index + 1], f'item_name: {item_name}')
                                        return change_price(second_price_without_taxe)
                                else:
                                    third_price_without_taxe = round(sell_order_graph[need_index + 1][0] / 1.15, 2)
                                    profit_third = round(third_price_without_taxe - price_item, 2)
                                    if profit_third >= 0.9:
                                        print(item_prices, sell_order_graph[need_index],
                                              sell_order_graph[need_index + 1], f'item_name: {item_name}')
                                        return change_price(third_price_without_taxe)
                                    else:
                                        print(item_prices, sell_order_graph[need_index],
                                              sell_order_graph[need_index + 1], f'item_name: {item_name}')
                                        return change_price(price_without_taxe)
    except Exception:
        buffer = io.StringIO()
        traceback.print_exc(file=buffer)
        with open('errors.txt', 'a') as logi:
            logi.write(f"Error in calculate_price: {buffer.getvalue()}\n")
        traceback.print_exc()


def sell_item(steamLoginSecure: str, sessionid: str, game_name: str, assetid: int, price_to_sell: str) \
        -> Optional[bool]:
    """Put item to steam market place."""
    url_sell = "https://steamcommunity.com/market/sellitem"
    payload_sell = f"sessionid={sessionid}&appid={game_id(game_name)}&contextid=2&assetid={assetid}&amount=1&" \
                   f"price={price_to_sell}"
    headers_sell = take_headers(steamLoginSecure, sessionid, "headers_sell")
    count = 0
    while True:
        try:
            response = requests.request("POST", url_sell, data=payload_sell, headers=headers_sell)
            response_status = response.json()["success"]
            if response_status is True:
                return response_status
            else:
                with open('errors.txt', 'a') as logi:
                    logi.write(f"f'response {response.status_code}, response_status{response.text}\n")
                count += 1  # Steam can give random errors.
                if count == 2:
                    break
                time.sleep(10)
                continue
        except Exception:
            buffer = io.StringIO()
            traceback.print_exc(file=buffer)
            with open('errors.txt', 'a') as logi:
                logi.write(f"Error in sell_item: {buffer.getvalue()} responst_status {response.status_code}\n")
            traceback.print_exc()
            return None
