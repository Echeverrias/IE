# -*- coding: utf-8 -*-

# Scrapy settings for ie project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import sys, os


## DJANGO INTEGRATION  ###########################################################
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(os.path.dirname(os.path.abspath('.')))
os.environ['DJANGO_SETTINGS_MODULE'] = 'ie_django.settings'

# This is required only if Django Version > 1.8
import django
django.setup()
################################################################################

BOT_NAME = 'afidor'#'earth616' #'ie'

SPIDER_MODULES = ['ie_scrapy.spiders']
NEWSPIDER_MODULE = 'ie_scrapy.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'ie (+http://www.yourdomain.com)'
#http://useragentstring.com/pages/useragentstring.php?name=Googlebot
#USER_AGENT = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
#USER_AGENT = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36";
#USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36"
# Obey robots.txt rules
ROBOTSTXT_OBEY = True


# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 8#16 #32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 4

DOWNLOAD_TIMEOUT = 20

# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en,es-ES;q=0.9,es;q=0.8'
}
# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
"""
SPIDER_MIDDLEWARES = {
   'ie_scrapy.middlewares.IeSpiderMiddleware': 443,
}
"""

"""
#scrapy-proxy-pool
PROXY_POOL_ENABLED = True

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html



"""
#scrapy-rotating-proxies #'92.222.77.101:4444'
 #ChromeBrowser.get_proxy()

ROTATING_PROXY_LIST = [

'51.158.186.242:8811', '144.217.101.242:3129'
]


"""
RANDOM_UA_PER_PROXY = True
DOWNLOADER_MIDDLEWARES = {
 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware':None,
   'rotating_proxies.middlewares.RotatingProxyMiddleware': 310,
    'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 420,
}

"""
RANDOM_UA_PER_PROXY = True
PROXY_POOL_ENABLED = True
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429, 400, 403] # added 400 to default codes
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware':None,
    'ie_scrapy.middlewares.CheckDownloaderMiddleware': 200,
    'scrapy_proxy_pool.middlewares.ProxyPoolMiddleware': 300,
    'scrapy_proxy_pool.middlewares.BanDetectionMiddleware': 320,
    'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 420,
    'ie_scrapy.middlewares.PUADownloaderMiddleware': 550,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 600,
    'ie_scrapy.middlewares.ERDownloaderMiddleware': 650,

}
#'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 560,



#'ie_scrapy.middlewares.IeDownloaderMiddleware': 743



# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html



ITEM_PIPELINES = {
   'ie_scrapy.pipelines.CleaningPipeline': 500,
   'ie_scrapy.pipelines.StoragePipeline': 550,
}



#
#'ie.pipelines.SqlitePipeline': 400,
# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

