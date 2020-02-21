from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import os
import random


CHROME_DRIVER_PATH = './chromedriver'

class ChromeBrowser:

    proxies = []
    user_agents = []

    @classmethod
    def _set_user_agents(cls):
        cls.user_agents = [
            'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html) ',
            "DuckDuckBot/1.0; (+http://duckduckgo.com/duckduckbot.html)",
        ]

    @classmethod
    def get_user_agent(cls):
        if not cls.user_agents:
            cls._set_user_agents()
        return random.choice(cls.user_agents)

    @classmethod
    def _set_proxies(cls):
        # '151.253.158.19:8080',
        # '178.46.160.64:54508',
        cls.proxies = [
            "182.253.175.141:8080",
        ]

    @classmethod
    def get_proxy(cls):

        if not cls.proxies:
            cls._set_proxies()
        return random.choice(cls.proxies)

    @classmethod
    def __get_chrome_options(cls, config={'proxy':None, 'user_agent':None}):
        chrome_options = webdriver.ChromeOptions()
        #chrome_options.add_argument("headless")
        #chrome_options.add_argument("incognito")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-infobars")
        prefs = {'profile.managed_default_content_settings.images': 2} # selenium will not load the images
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--start-maximized")
        if config['user_agent']:
            print('USER AGENT: %s' % config['user_agent'])
            chrome_options.add_argument("user-agent=" + config['user_agent'])
        if config['proxy']:
            chrome_options.add_argument('--proxy-server=%s' % config['proxy'])
        return chrome_options



    @classmethod
    def get_driver(cls, proxy=None, user_agent=None):
        print('set_chrome_Browser') ##
        print(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))##
        options = {'proxy': proxy, 'user_agent': user_agent}
        chrome_options = cls.__get_chrome_options(options)
        driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=chrome_options)
        return driver
