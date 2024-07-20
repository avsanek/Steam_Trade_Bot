from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from steam_totp import generate_twofactor_code_for_time as two_factor_code

from start_set import start_steam, start_trade, swipe_game, new_swipe_game
from func_buy import main
from config_auto import tradeback_set, game_set, spisoc_range_prof, windows

if __name__ == "__main__":
    """The main task is to log in to steam and steam parser. 
    After that we go through the received things checking their profitability thanks to static analysis.
    """
    options = Options()
    # options.add_argument('--headless')
    browser = webdriver.Chrome(options=options)
    browser.implicitly_wait(1)

    cookies: str = start_steam(browser, two_factor_code, "USERNAME_1", "PASSWORD_1", "two_key_1")
    start_trade(browser, windows, tradeback_set)

    while True:
        for range_prof in spisoc_range_prof:
            elements: list[str] = new_swipe_game(browser, range_prof[0], range_prof[1], range_prof[2])
            print(len(elements), range_prof, 'dota_check')
            main(browser, windows, elements, cookies, game_set['buy_in_Hour'], range_prof[3], range_prof[5], 0.85)
            elements: list[str] = swipe_game(browser)
            print(len(elements), range_prof, 'cs_check')
            main(browser, windows, elements, cookies, game_set['buy_in_Hour'], range_prof[4], range_prof[5], 1.25)
