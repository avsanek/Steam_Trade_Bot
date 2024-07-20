# Variables and funk with headers for working with chan_buy.
import time
import json
from datetime import datetime, timedelta

"""variables are used in chan_buy_main.py"""
start_zero_date: datetime = datetime.now() - timedelta(hours=9)
start = time.time()  # To track the running time of the script
count_gray_items: int = 0  # Counting minor things
time_to_sleep: float = 1.2  # Adjusting the dilemma to avoid getting 429.

"""variables are used in start_set.py. Need to memorize the items that become weakly relevant, 
so that when the orders overflow - remove the not needed. And orders that were recently removed, check for relevance.
"""
secondary_items: list[list[int | str]] = []
gray_items: list[list[str]] = []
secondary_gray_items: list[list[str]] = []
delete_gray_items: list[list[str]] = []

"""This is a dict with item names and their id to work with api-steam."""
with open('output_dota.json', 'r', encoding='utf-8') as file:
    item_nameid_dota = json.load(file)
with open('output_cs_go.json', 'r', encoding='utf-8') as file:
    item_nameid_cs_go = json.load(file)


def take_headers(steamLoginSecure: str, sessionid: str, need_headers: str) -> dict[str, str]:
    """The function contains all headers used in “start_set.py” placed in dict.
     I decided to put them here to make the code more readable.
     """
    headers_dict = {"headers_orders": {
        "cookie": "sessionid=5543ee1656a70dde82251639; steamCountry=BY%257Cfbf2a70fd1aa3304f62f9eb491d1ba4d",
        "Accept": "text/javascript, text/html, application/xml, text/xml, */*",
        "Accept-Language": "en-US,en;q=1",
        "Connection": "keep-alive",
        "Cookie": f"ActListPageSize=100; sessionid={sessionid}; timezoneOffset=10800,0; Steam_Language=english; "
                  f"webTradeEligibility=%7B%22allowed%22%3A1%2C%22allowed_at_time%22%3A0%2C"
                  f"%22steamguard_required_days%22%3A15%2C%22new_device_cooldown_days%22%3A0%2C%22time_checked%22"
                  f"%3A1717831769%7D; strInventoryLastContext=570_2; "
                  f"steamCountry=BY%7Cfbf2a70fd1aa3304f62f9eb491d1ba4d; "
                  f"app_impressions=381210@2_100100_100101_100106; steamLoginSecure={steamLoginSecure}; "
                  f"tsTradeOffersLastRead=1714593189; browserid=3362581138443957511",
        "Referer": "https://steamcommunity.com/market/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/126.0.0.0 Safari/537.36",
        "X-KL-kfa-Ajax-Request": "Ajax_Request",
        "X-Prototype-Version": "1.7",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": "^\^Not_A",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "^\^Windows^^"
    },
        "headers_get_item": {
            "Accept": "*/*",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Cookie": f"ActListPageSize=30; buy_orders=false; undefined=false; sessionid={sessionid}; timezoneOffset"
                      f"=10800,0; browserid=2934724684930533469; steamCurrencyId=5; Steam_Language=english; "
                      f"webTradeEligibility=%7B%22allowed%22%3A1%2C%22allowed_at_time%22%3A0%2C"
                      f"%22steamguard_required_days%22%3A15%2C%22new_device_cooldown_days%22%3A0%2C%22time_checked%22"
                      f"%3A1708012020%7D; steamCountry=BY%7C069a6323cb9105cab301fa93bf30bc11; "
                      f"recentlyVisitedAppHubs=730%2C1568590%2C570; "
                      f"app_impressions=753@2_100100_100101_100106|730@2_9_100006_100202|269670"
                      f"@2_100300_100500__100503|377160@2_100300_100500__100506|570@2_100300_100500__100509|2532550"
                      f"@2_100300_100500__100503|1850570@2_100300_100500__100503|730@2_100100_100101_100106|570"
                      f"@2_9_100000_|570@2_9_100000_; strInventoryLastContext=730_2; steamLoginSecure="
                      f"{steamLoginSecure}; tsTradeOffersLastRead=1683694588",
            "Origin": "https://steamcommunity.com",
            "Referer": "https://steamcommunity.com/market/listings/730/M4A4%20%7C%20Etch%20Lord%20%28Battle-Scarred%29",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/122.0.0.0 Safari/537.36",
            "X-KL-kfa-Ajax-Request": "Ajax_Request",
            "sec-ch-ua": "^\^Not_A",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "^\^Windows^^"
        },
        "headers_remove_item": {
            "Accept": "text/javascript, text/html, application/xml, text/xml, */*",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Cookie": f"ActListPageSize=30; buy_orders=false; undefined=false; sessionid={sessionid}; timezoneOffset"
                      f"=10800,0; browserid=2934724684930533469; steamCurrencyId=5; Steam_Language=english; "
                      f"webTradeEligibility=%7B%22allowed%22%3A1%2C%22allowed_at_time%22%3A0%2C"
                      f"%22steamguard_required_days%22%3A15%2C%22new_device_cooldown_days%22%3A0%2C%22time_checked%22"
                      f"%3A1708012020%7D; steamCountry=BY%7C069a6323cb9105cab301fa93bf30bc11; "
                      f"recentlyVisitedAppHubs=730%2C1568590%2C570; "
                      f"app_impressions=753@2_100100_100101_100106|730@2_9_100006_100202|269670"
                      f"@2_100300_100500__100503|377160@2_100300_100500__100506|570@2_100300_100500__100509|2532550"
                      f"@2_100300_100500__100503|1850570@2_100300_100500__100503|730@2_100100_100101_100106|570"
                      f"@2_9_100000_|570@2_9_100000_; strInventoryLastContext=730_2; steamLoginSecure="
                      f"{steamLoginSecure}",
            "Origin": "https://steamcommunity.com",
            "Referer": "https://steamcommunity.com/market/listings/730/M4A4%20%7C%20Etch%20Lord%20%28Battle-Scarred%29",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/122.0.0.0 Safari/537.36",
            "X-KL-kfa-Ajax-Request": "Ajax_Request",
            "X-Prototype-Version": "1.7",
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua": "^\^Not_A",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "^\^Windows^^"
        },
        "headers_item": {
            "cookie": "steamCountry=BY%257C37617d356840b5e6028fa9489d09881a; Steam_Language=english",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=1",
            "Connection": "keep-alive",
            "Cookie": f"ActListPageSize=30; buy_orders=false; sessionid={sessionid}; timezoneOffset=10800,0; "
                      f"browserid=2934724684930533469; steamCurrencyId=5; recentlyVisitedAppHubs=730; "
                      f"webTradeEligibility=%7B%22allowed%22%3A1%2C%22allowed_at_time%22%3A0%2C"
                      f"%22steamguard_required_days%22%3A15%2C%22new_device_cooldown_days%22%3A0%2C%22time_checked%22"
                      f"%3A1706258439%7D; app_impressions=753@2_100100_100101_100106|730@2_9_100006_100202|269670"
                      f"@2_100300_100500__100503|377160@2_100300_100500__100506|570@2_100300_100500__100509|2532550"
                      f"@2_100300_100500__100503|1850570@2_100300_100500__100503; Steam_Language=english; "
                      f"strInventoryLastContext=570_2; steamCountry=BY%7C99c08b4ef12a3151750bffe797e12e19; "
                      f"steamLoginSecure={steamLoginSecure}",
            "If-Modified-Since": "Thu, 08 Feb 2024 17:11:20 GMT",
            "Referer": "https://steamcommunity.com/market/listings/570/Scales%20of%20Incandescent%20Liturgy",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/121.0.0.0 Safari/537.36",
            "X-KL-kfa-Ajax-Request": "Ajax_Request",
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua": "^\^Not_A",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "^\^Windows^^"
        },
        "headers_myhistory": {
            "cookie": "steamCountry=BY%257C37617d356840b5e6028fa9489d09881a; Steam_Language=english",
            "Accept": "text/javascript, text/html, application/xml, text/xml, */*",
            "Accept-Language": "en-US,en;q=1",
            "Connection": "keep-alive",
            "Cookie": f"ActListPageSize=10; enableSIH=true; sessionid={sessionid}; timezoneOffset=10800,0; "
                      f"browserid=2944855789164494751; "
                      f"webTradeEligibility=%7B%22allowed%22%3A1%2C%22allowed_at_time%22%3A0%2C"
                      f"%22steamguard_required_days%22%3A15%2C%22new_device_cooldown_days%22%3A0%2C%22time_checked%22"
                      f"%3A1703081493%7D; steamCurrencyId=5; strInventoryLastContext=730_2; "
                      f"recentlyVisitedAppHubs=1966720%2C730; "
                      f"app_impressions=1966720@2_9_100000_|730@2_9_100006_100202|730@2_9_100006_100202|730"
                      f"@2_100100_100101_100106|1966720@2_9_100006_100202|730@2_9_100006_100202|730@2_9_100006_100202"
                      f"; steamCountry=BY%7C9e868d2c50e6f579dd7e8f980dd99e2e; steamLoginSecure={steamLoginSecure}",
            "Referer": "https://steamcommunity.com/market/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "X-KL-kfa-Ajax-Request": "Ajax_Request",
            "X-Prototype-Version": "1.7",
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua": "^\^Not_A",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "^\^Windows^^"
        }
    }

    return headers_dict[need_headers]
