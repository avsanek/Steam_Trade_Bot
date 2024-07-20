import time
import traceback
import io
import os

from typing import Callable
from dotenv import load_dotenv
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def start_steam(browser: WebDriver, two_factor_code: Callable[[str | None], str], USERNAME: str, PASSWORD: str,
                TWO_KEY: str) -> str:
    """Login steam and take cookie"""
    try:
        browser.get('https://steamcommunity.com/login/home/?goto=')
        load_dotenv()
        browser.find_element(By.CSS_SELECTOR, 'input[type="text"]._2GBWeup5cttgbTw8FM3tfx').send_keys(
            os.getenv(USERNAME))
        browser.find_element(By.CSS_SELECTOR, 'input[type="password"]._2GBWeup5cttgbTw8FM3tfx').send_keys(
            os.getenv(PASSWORD))
        browser.find_element(By.CSS_SELECTOR, 'button.DjSvCZoKKfoNSmarsEcTS').click()
        while True:
            steam_Code = two_factor_code(os.getenv(TWO_KEY))
            browser.find_element(By.CSS_SELECTOR, 'input[tabindex="0"]:nth-child(1)').send_keys(steam_Code)
            error_key = len(browser.find_elements(By.CSS_SELECTOR, 'div._1Mcy9wnDnt1Q72FijsNtHC'))
            if error_key > 0:  # If we get error with bad twofactor code.
                time.sleep(0.5)
                continue
            time.sleep(2)
            cookies = browser.get_cookies()
            return cookies[2]['value']
    except Exception:
        buffer = io.StringIO()
        traceback.print_exc(file=buffer)
        with open('errors.txt', 'a') as logi:
            logi.write(f"Error in start_steam: {buffer.getvalue()} \n")
        traceback.print_exc()


def start_trade(browser: WebDriver, windows: dict[str, str], tradeback_set: dict[str, str]) -> None:
    """Set the search settings of items on the parser site."""
    try:
        time.sleep(1)
        browser.get(
            'https://tradeback.io/ru/comparison#{%22app%22:%22all%22,%22services%22:[%22steamcommunity.com%22,'
            '%22bitskins.com%22],%22updated%22:[],%22categories%22:[[%22normal%22],[%22normal%22]],'
            '%22hold_time_range%22:[8,8],%22price%22:[[],[]],%22count%22:[[],[]],%22profit%22:[[],[]]}')
        browser.find_element(By.CSS_SELECTOR, 'input.btn_green_white_innerfade').click()
        time.sleep(7)
        browser.find_element(By.CSS_SELECTOR, 'label[for="first-service-orders"]').click()
        browser.find_element(By.CSS_SELECTOR, 'div.dropdown-select:nth-child(3) div.title').click()
        browser.find_element(By.CSS_SELECTOR, 'div.menu.indent li[value="3"]').click()
        browser.find_element(By.CSS_SELECTOR, 'div.dropdown-select:nth-child(4) div.title:nth-child(1)').click()
        browser.find_element(By.CSS_SELECTOR, 'label[for="filter-without-stickers"]').click()
        browser.find_element(By.CSS_SELECTOR, 'div.comparison-service:nth-child(2) div.title').click()
        browser.find_element(By.CSS_SELECTOR,
                             'div.comparison-service:nth-child(2) div.menu.show li[value="steamcommunity.com"]').click()
        browser.find_element(By.CSS_SELECTOR,
                             'div.range-filters.price-filters[data-column="first"] input[placeholder="От"]').send_keys(
            tradeback_set['ot_buy'])
        browser.find_element(By.CSS_SELECTOR, '#more-filters.comparison-filters-btn').click()
        browser.find_element(By.CSS_SELECTOR, 'input.comparison-sales-input.sales-filter[data-key="s"]').clear()
        browser.find_element(By.CSS_SELECTOR, 'input.comparison-sales-input.sales-filter[data-key="s"]').send_keys(
            tradeback_set['weak'])
        time.sleep(0.5)
        browser.find_element(By.CSS_SELECTOR, 'div[id="filters-modal"] a.iziModal-button.iziModal-button-close').click()
        time.sleep(0.5)
        browser.find_element(By.CSS_SELECTOR, 'div.dropdown-select:nth-child(6) div.title').click()
        browser.find_element(By.CSS_SELECTOR, 'label[for="auto-update-live"]').click()
        browser.find_element(By.CSS_SELECTOR,
                             'th.center:nth-child(12) div.range-filters.profit-filters input[placeholder="От"]').send_keys(
            tradeback_set['ot_prof'])
        browser.find_element(By.CSS_SELECTOR,
                             'th.center:nth-child(12) div.range-filters.profit-filters input[placeholder="До"]').send_keys(
            tradeback_set['do_prof'])
        browser.find_element(By.CSS_SELECTOR, 'div.column-profit.sort[data-column="first"]').click()
        time.sleep(4)  # Swipe down to the bottom of the page to get all the elements.
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        windows['tradeback'] = browser.current_window_handle
    except Exception:
        buffer = io.StringIO()
        traceback.print_exc(file=buffer)
        with open('errors.txt', 'a') as logi:
            logi.write(f"Error in start_trade: {buffer.getvalue()} \n")
        traceback.print_exc()


def swipe_game(browser: WebDriver) -> list[str]:
    """Sets the settings - pick CS_2 and the range of searching for specific things, get the found elements."""
    while True:
        try:
            try:
                browser.find_element(By.CSS_SELECTOR, 'div.dropdown-select:nth-child(3) div.title').click()
                browser.find_element(By.CSS_SELECTOR, 'div.menu.indent li[value="2"]').click()
                browser.refresh()
                time.sleep(4)
                for i in range(15):
                    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll down 15 times
                time.sleep(1)
            except Exception:  # If something goes wrong, we try again.
                browser.refresh()
                time.sleep(4)
                print("swipe_game browser.refresh() Error")
                continue
            try:  # Get all the things we need to analyze.
                elements = WebDriverWait(browser, 3).until(EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, 'td.field-link[data-link-key="steamcommunity"] a')))
            except Exception:
                return []
            elements = [ell.get_attribute("href") for ell in elements]
            return elements
        except Exception:
            buffer = io.StringIO()
            traceback.print_exc(file=buffer)
            with open('errors.txt', 'a') as logi:
                logi.write(f"Error in swipe_game: {buffer.getvalue()} \n")
            traceback.print_exc()


def new_swipe_game(browser: WebDriver, range_1: str, range_2: str, prof_1: str) -> list[str]:
    """Sets the settings - pick dota and the range of searching for specific things, get the found elements."""
    while True:
        try:
            try:
                browser.find_element(By.CSS_SELECTOR, 'div.dropdown-select:nth-child(3) div.title').click()
                browser.find_element(By.CSS_SELECTOR, 'div.menu.indent li[value="3"]').click()
                browser.find_element(By.CSS_SELECTOR,
                                     'div.range-filters.price-filters[data-column="first"] input[placeholder="От"]').clear()
                browser.find_element(By.CSS_SELECTOR,
                                     'div.range-filters.price-filters[data-column="first"] input[placeholder="От"]').send_keys(
                    range_1)
                browser.find_element(By.CSS_SELECTOR,
                                     'div.range-filters.price-filters[data-column="first"] input[placeholder="До"]').clear()
                browser.find_element(By.CSS_SELECTOR,
                                     'div.range-filters.price-filters[data-column="first"] input[placeholder="До"]').send_keys(
                    range_2)
                browser.find_element(By.CSS_SELECTOR,
                                     'th.center:nth-child(12) div.range-filters.profit-filters input[placeholder="От"]').clear()
                browser.find_element(By.CSS_SELECTOR,
                                     'th.center:nth-child(12) div.range-filters.profit-filters input[placeholder="От"]').send_keys(
                    prof_1)
                time.sleep(2)
                browser.refresh()
                time.sleep(4)
                for i in range(15):
                    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll down 15 times
                time.sleep(1)
            except Exception:  # If something goes wrong, we try again.
                traceback.print_exc()
                browser.refresh()
                time.sleep(4)
                print("new_swipe_game browser.refresh() Error")
                continue
            try:  # Get all the things we need to analyze.
                elements = WebDriverWait(browser, 3).until(EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, 'td.field-link[data-link-key="steamcommunity"] a')))
            except Exception:
                return []
            elements = [ell.get_attribute("href") for ell in elements]
            return elements
        except Exception:
            buffer = io.StringIO()
            traceback.print_exc(file=buffer)
            with open('errors.txt', 'a') as logi:
                logi.write(f"Error in new_swipe_game: {buffer.getvalue()} \n")
            traceback.print_exc()
