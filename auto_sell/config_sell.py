# Variables and funk with headers for working with auto_sell.
import json
from datetime import datetime, timedelta

start_zero_date: datetime = datetime.now() - timedelta(hours=14)
purchased_items: list[str] = []
sold_items: list[str] = []

"""This is a dict with item names and their id to work with api-steam."""
with open('output_dota.json', 'r', encoding='utf-8') as file:
    item_nameid_dota: dict[str, str] = json.load(file)
with open('output_cs_go.json', 'r', encoding='utf-8') as file:
    item_nameid_cs_go: dict[str, str] = json.load(file)


def take_headers(steamLoginSecure: str, sessionid: str, need_headers: str) -> dict[str, str]:
    """The function contains all headers used in “func_sell.py” placed in dict.
     I decided to put them here to make the code more readable.
     """
    headers_dict = {"headers_myhistory": {
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
                  f"@2_100100_100101_100106|1966720@2_9_100006_100202|730@2_9_100006_100202|730@2_9_100006_100202; "
                  f"steamCountry=BY%7C9e868d2c50e6f579dd7e8f980dd99e2e; steamLoginSecure={steamLoginSecure}",
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
    },
        "headers_inventory": {
            "cookie": "steamCountry=BY%257C37617d356840b5e6028fa9489d09881a; Steam_Language=english",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=1",
            "Connection": "keep-alive",
            "Cookie": f"sessionid={sessionid}; timezoneOffset=10800,0; browserid=2934724684930533469; "
                      f"steamCurrencyId=5; recentlyVisitedAppHubs=730; "
                      f"webTradeEligibility=%7B%22allowed%22%3A1%2C%22allowed_at_time%22%3A0%2C"
                      f"%22steamguard_required_days%22%3A15%2C%22new_device_cooldown_days%22%3A0%2C%22time_checked%22"
                      f"%3A1706258439%7D; app_impressions=753@2_100100_100101_100106|730@2_9_100006_100202|269670"
                      f"@2_100300_100500__100503|377160@2_100300_100500__100506|570@2_100300_100500__100509|2532550"
                      f"@2_100300_100500__100503|1850570@2_100300_100500__100503; "
                      f"steamCountry=BY%7Ce146c3f7b82949c797ae81013bc373ed; steamLoginSecure={steamLoginSecure}; "
                      f"Steam_Language=english; strInventoryLastContext=570_2",
            "Referer": "https://steamcommunity.com/id/130840215/inventory?modal=1&market=1",
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
        "headers_sell": {
            "cookie": "steamCountry=BY%257C37617d356840b5e6028fa9489d09881a; Steam_Language=english",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=1",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Cookie": f"ActListPageSize=30; sell_listings=false; sessionid={sessionid}; timezoneOffset=10800,0; "
                      f"browserid=2934724684930533469; steamCurrencyId=5; recentlyVisitedAppHubs=730; "
                      f"webTradeEligibility=%7B%22allowed%22%3A1%2C%22allowed_at_time%22%3A0%2C"
                      f"%22steamguard_required_days%22%3A15%2C%22new_device_cooldown_days%22%3A0%2C%22time_checked%22"
                      f"%3A1706258439%7D; Steam_Language=english; "
                      f"app_impressions=753@2_100100_100101_100106|730@2_9_100006_100202|269670"
                      f"@2_100300_100500__100503|377160@2_100300_100500__100506|570@2_100300_100500__100509|2532550"
                      f"@2_100300_100500__100503|1850570@2_100300_100500__100503|730@2_100100_100101_100106; "
                      f"steamCountry=BY%7C24e8cef0183178cdd21288000454bb5b; steamLoginSecure={steamLoginSecure}; "
                      f"strInventoryLastContext=730_2",
            "Origin": "https://steamcommunity.com",
            "Referer": "https://steamcommunity.com/profiles/76561198091105943/inventory",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/121.0.0.0 Safari/537.36",
            "X-KL-kfa-Ajax-Request": "Ajax_Request",
            "sec-ch-ua": "^\^Not_A",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "^\^Windows^^"
        }
    }

    return headers_dict[need_headers]
