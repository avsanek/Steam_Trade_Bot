import requests
import traceback
import time
import io

from datetime import datetime, timedelta
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver


def buy_in_hour(cookies: str, name: str, game_id: str, buy_in_Hour: float) -> list[float]:
    """Does a statistical analysis of the thing, loads Api-item how many times this thing was bought in a day,
    if the purchases were not even, we don't buy this thing.
    """
    while True:
        try:
            count = 0
            coookies = {'steamLoginSecure': cookies}
            link = f"https://steamcommunity.com/market/pricehistory/?country=DE&currency=3&appid={game_id}&" \
                   f"market_hash_name={name}"
            site = requests.get(link, cookies=coookies).json()
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
            print(procent_items)
            if any(i > buy_in_Hour for i in procent_items):
                return False
            else:
                return procent_items
        except Exception:
            count += 1
            buffer = io.StringIO()
            traceback.print_exc(file=buffer)
            with open('errors.txt', 'a') as logi:
                logi.write(f'Error in buy_in_hour: {buffer.getvalue()} \n')
            traceback.print_exc()
            if count > 3:
                return False


def error_max(browser: WebDriver, windows: dict[str, str]) -> None:
    """Buy orders have a certain limit, if it is reached, this function will cancel the first 10 orders placed."""
    try:
        browser.execute_script("window.open('')")
        windows['error_max'] = browser.window_handles[-1]
        browser.switch_to.window(windows['error_max'])
        browser.get('https://steamcommunity.com/market/')
        full_orders = browser.find_elements(By.CSS_SELECTOR,
                                            'div.my_listing_section.market_content_block.market_home_listing_table'
                                            ':nth-child(n+4) span.item_market_action_button_contents')
        count_orders = 0
        for order in full_orders:
            order.click()
            count_orders += 1
            if count_orders == 10:
                break
        browser.close()
        del windows['error_max']
        browser.switch_to.window(windows['steam_auto'])
        print('error_max_srabotal')
        with open('errors.txt', 'a') as logi:
            logi.write('Error max srabotal \n')
    except Exception:
        buffer = io.StringIO()
        traceback.print_exc(file=buffer)
        with open('errors.txt', 'a') as logi:
            logi.write(f'Error in error_max: {buffer.getvalue()} \n')
        traceback.print_exc()


def not_spisoc(browser: WebDriver, cookies: str, item: str, buy_in_Hour: float, game_prof: float, status: str,
               min_prof: float) -> list[float]:
    """The function checks how much the thing is profitable, if the thing is profitable,
    we calculate the amount for which the thing will be bought.
    """
    while True:
        try:
            order = browser.find_element(By.CSS_SELECTOR,
                                         '#market_commodity_buyrequests '
                                         'span.market_commodity_orders_header_promote:nth-child(2)').text
            order = float(order.replace(",", ".").replace(" pуб.", ""))
            print(order, 'order')
            sell = browser.find_element(By.CSS_SELECTOR,
                                        '#market_commodity_forsale_table table.market_commodity_orders_table '
                                        'tr:nth-child(2) td[align="right"]:nth-child(1)').text
            sell = float(sell.replace(",", ".").replace(" pуб.", ""))
            print(sell, 'sell')
            sell_wik = round(sell / 1.15, 2)
            print(sell_wik, 'sell_wik')
            profit = round(sell_wik - order, 2)
            procent = profit
            print(profit, 'profit')
            if status == 'procent':
                procent = round(profit / (order / 100), 2)
                print(procent, 'procent')
            if procent >= game_prof:
                print(f'сработал профит в {game_prof}')
                parts = item.split('/')
                procent_items = buy_in_hour(cookies, parts[-1], parts[-2], buy_in_Hour)
                if procent_items:  # Checking the thing by static analysis.
                    browser.find_element(By.CSS_SELECTOR,
                                         '#market_commodity_order_spread div:nth-child(2) div '
                                         'div.market_commodity_orders_header a span').click()
                    browser.find_element(By.CSS_SELECTOR, '#market_buy_commodity_input_price').clear()
                    min_a = profit
                    coef_min = min_a // min_prof
                    if coef_min < 1:
                        plus_order = 0.05
                    elif coef_min <= 11:
                        plus_order = 0.1 * coef_min
                    else:
                        plus_order = 0.1 * 11
                    print(f'min_prof {min_a}, coef_min {coef_min} plus_order {plus_order}')
                    browser.find_element(By.CSS_SELECTOR, '#market_buy_commodity_input_price').send_keys(
                        order + round(plus_order, 2))
                    browser.find_element(By.CSS_SELECTOR, '#market_buyorder_dialog_accept_ssa').click()
                    browser.find_element(By.CSS_SELECTOR, '#market_buyorder_dialog_purchase').click()
                    return [order, sell_wik, profit, procent, procent_items]
            break
        except (ValueError, NoSuchElementException):
            print('not_spisoc обновляем')
            time.sleep(5)
            browser.refresh()
        except Exception:
            buffer = io.StringIO()
            traceback.print_exc(file=buffer)
            with open('errors.txt', 'a') as logi:
                logi.write(f"Error in not_spisoc: {buffer.getvalue()} , {item.split('/')[-1]} \n")
            traceback.print_exc()


def spisoc(browser: WebDriver, cookies: str, item: str, buy_in_Hour: float, game_prof: float, status: str,
           min_prof: float) -> list[float]:
    """The function checks how much the thing is profitable, loads a page with 10 things, evaluates them,
    if the thing is profitable, we calculate the amount for which the thing will be bought.
    """
    while True:
        try:
            order = browser.find_element(By.CSS_SELECTOR,
                                         '#market_commodity_buyrequests '
                                         'span.market_commodity_orders_header_promote:nth-child(2)').text
            order = float(order.replace(",", ".").replace(" pуб.", ""))
            print(order, 'order')
            sell_wik = browser.find_elements(By.CSS_SELECTOR,
                                             'span.market_listing_price.market_listing_price_without_fee')
            sell_wik = [browser.execute_script('return arguments[0].textContent;', sell) for sell in sell_wik]
            sell_wik = [float(sell.strip().replace(',', '.').split()[0]) for sell in sell_wik]
            print(sell_wik, 'sell_wik')
            profit = [round(i - order, 2) for i in sell_wik]
            procent = profit
            print(profit, 'profit')
            if status == 'procent':
                procent = [round(i / (order / 100), 2) for i in profit]
                print(procent, 'procent')
            if all(i >= game_prof for i in procent):
                print(f'сработал профит в {game_prof}')
                parts = item.split('/')
                procent_items = buy_in_hour(cookies, parts[-1], parts[-2], buy_in_Hour)
                if procent_items:  # Checking the thing by static analysis.
                    browser.find_element(By.CSS_SELECTOR,
                                         'a.btn_green_white_innerfade.btn_medium.market_noncommodity_buyorder_button '
                                         'span').click()
                    browser.find_element(By.CSS_SELECTOR, '#market_buy_commodity_input_price').clear()
                    min_a = min(profit)
                    coef_min = min_a // min_prof
                    if coef_min < 1:
                        plus_order = 0.05
                    elif coef_min <= 11:
                        plus_order = 0.1 * coef_min
                    else:
                        plus_order = 0.1 * 11
                    print(f'min_prof {min_a}, coef_min {coef_min} plus_order {plus_order}')
                    browser.find_element(By.CSS_SELECTOR, '#market_buy_commodity_input_price').send_keys(
                        order + round(plus_order, 2))
                    browser.find_element(By.CSS_SELECTOR, '#market_buyorder_dialog_accept_ssa').click()
                    browser.find_element(By.CSS_SELECTOR, '#market_buyorder_dialog_purchase').click()
                    return [order, sell_wik, profit, procent, procent_items]
            break
        except (ValueError, NoSuchElementException):
            print('spisoc обновляем')
            time.sleep(5)
            browser.refresh()
        except Exception:
            buffer = io.StringIO()
            traceback.print_exc(file=buffer)
            with open('errors.txt', 'a') as logi:
                logi.write(f"Error in spisoc: {buffer.getvalue()} , {item.split('/')[-1]} \n")
            traceback.print_exc()


def main(browser: WebDriver, windows: dict[str, str], elements: list[str], cookies: str, buy_in_Hour: float,
         game_prof: float, status: str, min_prof: float) -> None:
    """The main function of determining the advantageous item. Goes through all the stuff he's gotten.
    Checks 2 errors: 1) Standard page load error 2) error 429.
    Steam things have two different html-design, and by specific type checks the thing.
    """
    try:
        browser.execute_script("window.open('')")
        windows['steam_auto'] = browser.window_handles[-1]
        browser.switch_to.window(windows['steam_auto'])

        for item in elements:
            while True:
                browser.get(item)
                error_def = len(
                    browser.find_elements(By.CSS_SELECTOR, '#searchResultsTable div.market_listing_table_message'))
                if error_def > 0:  # Checking default bad page error.
                    continue
                error_time = len(browser.find_elements(By.CSS_SELECTOR, 'div.error_ctn'))
                if error_time > 0:  # Checking 429 error.
                    with open('errors.txt', 'a') as logi:
                        logi.write('Error time srabotal \n')
                    time.sleep(60)
                    continue

                #  First type of html-design.
                spisok = len(browser.find_elements(By.CSS_SELECTOR,
                                                   'span.market_listing_price.market_listing_price_without_fee'))
                if spisok > 0:
                    order_have = len(browser.find_elements(By.CSS_SELECTOR,
                                                           'div[class="my_listing_section market_content_block '
                                                           'market_home_listing_table"] '
                                                           'div.market_listing_row.market_recent_listing_row'))
                    if order_have:  # If the order is available now, skip this item.
                        break
                    details_item = spisoc(browser, cookies, item, buy_in_Hour, game_prof, status, min_prof)
                    if details_item:
                        time.sleep(0.5)
                        error_max_orders = browser.find_element(By.CSS_SELECTOR,
                                                                'span#market_buyorder_dialog_error_text').text
                        if len(error_max_orders) > 300:  # Checking for a error max orders.
                            error_max(browser, windows)
                            continue
                        with open('logi.txt', 'a') as logi:
                            logi.write(
                                f"order {details_item[0]} sell_wik {details_item[1]} profit {details_item[2]} "
                                f"procent_prof {details_item[3]} min_pt_prof {min(details_item[3])} "
                                f"procent_items {details_item[4]} max_item {max(details_item[4])} "
                                f"time_buy {datetime.now()} link {item}  \n")
                    break

                # Second type of html-design.
                not_spisok = len(browser.find_elements(By.CSS_SELECTOR, '#market_commodity_forsale_table'))
                if not_spisok > 0:
                    order_have = len(browser.find_elements(By.CSS_SELECTOR,
                                                           'div[class="my_listing_section market_content_block '
                                                           'market_home_listing_table"] '
                                                           'div.market_listing_row.market_recent_listing_row'))
                    if order_have:  # If the order is available now, skip this item.
                        break
                    details_item = not_spisoc(browser, cookies, item, buy_in_Hour, game_prof, status, min_prof)
                    if details_item:
                        time.sleep(0.5)
                        error_max_orders = browser.find_element(By.CSS_SELECTOR,
                                                                'span#market_buyorder_dialog_error_text').text
                        if len(error_max_orders) > 300:  # Checking for a error max orders.
                            error_max(browser, windows)
                            continue
                        with open('logi.txt', 'a') as logi:
                            logi.write(
                                f"order {details_item[0]} sell_wik {details_item[1]} profit {details_item[2]} "
                                f"procent_prof {details_item[3]} procent_items {details_item[4]} "
                                f"max_item {max(details_item[4])} time_buy {datetime.now()} link {item}  \n")
                    break

        browser.close()
        del windows['steam_auto']
        browser.switch_to.window(windows['tradeback'])

    except KeyboardInterrupt:
        print('Stopped by the user')
    except Exception:
        buffer = io.StringIO()
        traceback.print_exc(file=buffer)
        with open('errors.txt', 'a') as logi:
            logi.write(f'Error in main: {buffer.getvalue()} \n')
        traceback.print_exc()
