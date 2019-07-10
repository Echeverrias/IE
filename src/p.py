import selenium

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.proxy import Proxy, ProxyType

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from time import sleep
import random

driver = webdriver.Chrome('chromedriver')
driver.get('https://free-proxy-list.net/anonymous-proxy.html')
driver.execute_script("window.scrollBy(0, %i);"%random.randint(1,150))