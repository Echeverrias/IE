from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import os
import random


class ChromeBrowser:

    @classmethod
    def get_user_agent(cls):
        user_agents = ['Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html) ',
                       "DuckDuckBot/1.0; (+http://duckduckgo.com/duckduckbot.html)"]
        return random.choice(user_agents)

    @classmethod
    def get_proxy(cls):
        proxies = [
            '151.253.158.19:8080',
        ]
        return random.choice(proxies)

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
        driver = webdriver.Chrome('./chromedriver', options=chrome_options)
        return driver

    """
        def __get_chrome_browser(self, request=None):
            print('set_chrome_Browser') ##
            print(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))##
            options = {'proxy': None, 'user_agent': None}
            if request:
                try:
                    options['user_agent'] = str(request.headers['User-Agent'])
                except Exception as e:
                    print(e)
                    user_agents = cls._get_a_random_user_agent()
                try:
                    options['proxy'] = request.meta['proxy']
                    #options['proxy'] = '153.232.171.254:8080'
                except Exception as e:
                    print(e)
            chrome_options = self.__get_chrome_options(options)
            driver = webdriver.Chrome('./chromedriver', options=chrome_options)
            return driver
        """