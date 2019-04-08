# -*- coding: utf-8 -*-

BOT_NAME = 'spa_housing_crawler'
SPIDER_MODULES = ['spa_housing_crawler.spiders']
NEWSPIDER_MODULE = 'spa_housing_crawler.spiders'
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"

# -*- Concurent requests & Delay
ROBOTSTXT_OBEY = False
CONCURRENT_REQUESTS = 1
DOWNLOAD_DELAY = 1
CONCURRENT_REQUESTS_PER_DOMAIN = 1
CONCURRENT_REQUESTS_PER_IP = 1

# -*-  -*- -*- -*- -*- -*- -*-

DOWNLOADER_MIDDLEWARES = {
  #  'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    'spa_housing_crawler.middlewares.SleepRetryMiddleware': 100,

    #  ---------> USER-AGENTS
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
    'random_useragent.RandomUserAgentMiddleware': 400,

    #'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,

    #  ---------> PROXIES
    #'scrapy_proxies.RandomProxy': 100,
    #'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,

    #'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
}

# ------  Scrapy random user-agent
USER_AGENT_LIST = "./spa_housing_crawler/useragents.txt"

# ------  Scrapy fake user-agent
RANDOM_UA_PER_PROXY = True

# ------  Retry many times since proxies often fail
RETRY_TIMES = 0
RETRY_HTTP_CODES = [500, 503, 504, 400, 403, 404, 408]

# ------  Scrapy rotating proxies
ROTATING_PROXY_LIST_PATH = "./spa_housing_crawler/proxies.txt"

# ------  Scrapy proxies
PROXY_LIST = "./spa_housing_crawler/proxies.txt"
PROXY_MODE = 0