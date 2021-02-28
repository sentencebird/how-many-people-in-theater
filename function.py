import requests
from bs4 import BeautifulSoup
import json
import time
import datetime
import dateutil
import matplotlib.pyplot as plt
import random

from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

def date_list(n_dates=6):
    n_dates = 6
    today = datetime.date.today()
    return [(today + datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(n_dates)]

def get_soup(url, useragents=[]):
    if len(useragents) != 0:
        response = requests.get(url, headers={'user-agent': random.choice(useragents)})
    else:
        response = requests.get(url)
    response.encoding = response.apparent_encoding
    html = response.text
    return BeautifulSoup(html, 'html.parser')

def get_driver(url, useragents=[]):
    options = Options()
    options.add_argument('--headless')
    options.add_argument("--disable-dev-shm-usage")
    if len(useragents) != 0:
        options.add_argument(f'--user-agent={random.choice(useragents)}')
    driver = webdriver.Chrome('chromedriver', chrome_options=options)
    driver.set_window_size(1920, 1080)
    driver.get(url) 
    return driver

def click_date_button(driver, date):
    for tag in driver.find_elements_by_class_name('calendar-item'):
        if tag.get_attribute('data-date') == date:
            tag.click()
            break